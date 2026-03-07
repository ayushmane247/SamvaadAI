// frontend/src/api/apiClient.js
// ─────────────────────────────────────────────────────────────────
// Production API client for SamvaadAI.
//
// Features:
//   • Base URL from VITE_API_URL
//   • 10s request timeout
//   • Retry with exponential backoff (max 3 attempts)
//   • AbortController support (prevents duplicate LLM calls)
//   • x-request-id propagation (frontend → backend)
//   • Structured error normalization
//   • Response normalization layer (schemes + documents)
//   • Query-level cache (Phase 6 — latency optimization)
//   • Request deduplication (Phase 7 — cost protection)
//   • Throttle guard (Phase 7 — cost protection)
// ─────────────────────────────────────────────────────────────────

const BASE_URL = import.meta.env.VITE_API_URL || "";
const TIMEOUT_MS = 10_000;
const MAX_RETRIES = 3;
const RETRY_BASE_MS = 500;
const CACHE_TTL_MS = 60_000; // 1 minute cache
const THROTTLE_MS = 2_000; // min 2s between requests

// ── UUID v4 generator (no dependency) ────────────────────────────
function uuidv4() {
  return "10000000-1000-4000-8000-100000000000".replace(/[018]/g, (c) =>
    (+c ^ (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (+c / 4)))).toString(16)
  );
}

// ── Error class ──────────────────────────────────────────────────

export class ApiError extends Error {
  constructor(status, detail, requestId = null) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
    this.requestId = requestId;
  }
}

// ── Internal helpers ─────────────────────────────────────────────

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

/**
 * Core fetch wrapper with timeout and single-attempt error handling.
 */
async function fetchWithTimeout(url, options = {}, signal) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);

  // Merge external signal (AbortController from caller) with timeout
  if (signal) {
    signal.addEventListener("abort", () => controller.abort());
  }

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    return response;
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * Parse and normalize error responses from the backend.
 */
async function parseError(response, requestId) {
  let detail = "Sorry, something went wrong. Please try again.";

  try {
    const body = await response.json();
    detail = body.detail || body.message || detail;
  } catch {
    // Response body is not JSON
  }

  return new ApiError(response.status, detail, requestId);
}

// ── Response Normalization ───────────────────────────────────────

/**
 * Normalize the backend ConversationResponse into a UI-friendly shape.
 *
 * Backend returns:
 *   { profile, eligibility: { eligible[], partially_eligible[], ineligible[] }, response, session_id }
 *
 * We normalize to:
 *   { profile, eligibleSchemes, partialSchemes, ineligibleSchemes, response, sessionId }
 */
function normalizeConversationResponse(data) {
  const eligibility = data.eligibility || {};

  return {
    profile: data.profile || {},
    eligibleSchemes: eligibility.eligible || [],
    partialSchemes: eligibility.partially_eligible || [],
    ineligibleSchemes: eligibility.ineligible || [],
    response: data.response || "",
    schemes: data.schemes || [],
    documents: data.documents || [],
    sessionId: data.session_id || null,
  };
}

// ── Query Cache (Phase 6) ────────────────────────────────────────

const _cache = new Map();

function getCached(key) {
  const entry = _cache.get(key);
  if (!entry) return null;
  if (Date.now() - entry.ts > CACHE_TTL_MS) {
    _cache.delete(key);
    return null;
  }
  console.debug("[SamvaadAI] cache hit");
  return entry.data;
}

function setCache(key, data) {
  // Keep cache bounded (max 20 entries)
  if (_cache.size >= 20) {
    const oldest = _cache.keys().next().value;
    _cache.delete(oldest);
  }
  _cache.set(key, { data, ts: Date.now() });
}

// ── Request Deduplication (Phase 7) ──────────────────────────────

const _pending = new Map();

// ── Throttle Guard (Phase 7) ─────────────────────────────────────

let _lastRequestTs = 0;

// ── Public API ───────────────────────────────────────────────────

/**
 * Send a conversational query to the backend.
 *
 * Includes: cache, dedup, throttle, retry, timeout, abort.
 *
 * @param {Object} params
 * @param {string} params.query       - User's natural language message
 * @param {string} [params.language]  - Language code (en, hi, mr)
 * @param {string} [params.sessionId] - Session ID for multi-turn
 * @param {AbortSignal} [params.signal] - AbortController signal
 * @returns {Promise<Object>} Normalized conversation response
 */
export async function sendConversation({
  query,
  language = "en",
  sessionId = null,
  signal = null,
}) {
  // ── Throttle: enforce minimum gap between requests ──
  const now = Date.now();
  const gap = now - _lastRequestTs;
  if (gap < THROTTLE_MS) {
    const wait = THROTTLE_MS - gap;
    console.debug(`[SamvaadAI] throttled — waiting ${wait}ms`);
    await sleep(wait);
  }
  _lastRequestTs = Date.now();

  // ── Cache check ──
  const cacheKey = `${query}|${language}|${sessionId || ""}`;
  const cached = getCached(cacheKey);
  if (cached) return cached;

  // ── Dedup: if identical request is already in-flight, reuse it ──
  if (_pending.has(cacheKey)) {
    console.debug("[SamvaadAI] dedup — reusing pending request");
    return _pending.get(cacheKey);
  }

  // ── Build request ──
  const url = `${BASE_URL}/v1/conversation`;
  const requestId = uuidv4();
  const body = JSON.stringify({
    query,
    language,
    session_id: sessionId,
  });

  const request = (async () => {
    let lastError = null;

    for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
      try {
        const response = await fetchWithTimeout(
          url,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "x-request-id": requestId,
            },
            body,
          },
          signal,
        );

        // Capture request ID from backend
        const requestId = response.headers.get("x-request-id");
        if (requestId) {
          console.debug(`[SamvaadAI] request_id=${requestId}`);
        }

        if (!response.ok) {
          throw await parseError(response, requestId);
        }

        const data = await response.json();
        const result = normalizeConversationResponse(data);

        // Store in cache
        setCache(cacheKey, result);

        return result;
      } catch (err) {
        // Don't retry if the request was intentionally aborted
        if (err.name === "AbortError") {
          throw new ApiError(0, "Request cancelled", null);
        }

        // Don't retry client errors (4xx)
        if (
          err instanceof ApiError &&
          err.status >= 400 &&
          err.status < 500
        ) {
          throw err;
        }

        lastError = err;

        // Exponential backoff before next retry
        if (attempt < MAX_RETRIES - 1) {
          const delay = RETRY_BASE_MS * Math.pow(2, attempt);
          console.warn(
            `[SamvaadAI] Retry ${attempt + 1}/${MAX_RETRIES} after ${delay}ms`,
          );
          await sleep(delay);
        }
      }
    }

    // All retries exhausted
    throw lastError instanceof ApiError
      ? lastError
      : new ApiError(0, lastError?.message || "Network error", null);
  })();

  // Register pending request for dedup
  _pending.set(cacheKey, request);
  try {
    return await request;
  } finally {
    _pending.delete(cacheKey);
  }
}

/**
 * Start a new backend session.
 *
 * @param {AbortSignal} [signal]
 * @returns {Promise<{sessionId: string, createdAt: string, expiresAt: string}>}
 */
export async function startSession(signal = null) {
  const url = `${BASE_URL}/v1/session/start`;

  const response = await fetchWithTimeout(
    url,
    { method: "POST", headers: { "Content-Type": "application/json" } },
    signal,
  );

  const requestId = response.headers.get("x-request-id");
  if (requestId) {
    console.debug(`[SamvaadAI] session/start request_id=${requestId}`);
  }

  if (!response.ok) {
    throw await parseError(response, requestId);
  }

  const data = await response.json();
  return {
    sessionId: data.session_id,
    createdAt: data.created_at,
    expiresAt: data.expires_at,
  };
}

/**
 * Health check.
 *
 * @returns {Promise<boolean>}
 */
export async function checkHealth() {
  try {
    const response = await fetchWithTimeout(`${BASE_URL}/health`, {
      method: "GET",
    });
    return response.ok;
  } catch {
    return false;
  }
}
