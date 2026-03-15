// frontend/src/store/useConversationStore.js
// ─────────────────────────────────────────────────────────────────
// Zustand store for SamvaadAI conversation state.
//
// Responsibilities:
//   • Manage chat messages (user + assistant)
//   • Persist session ID in localStorage (Phase 4)
//   • Auto-create session if missing (Phase 4)
//   • Debounce rapid sends (Phase 7 — cost protection)
//   • Processing state for UI indicators (Phase 6)
//   • AbortController to prevent duplicate LLM calls
//   • Voice-pipeline-safe (all state updates are synchronous)
//
// Session Storage Decision: localStorage
//   ✅ Simple — no backend cookie handling needed
//   ✅ Persists across tabs and browser restarts
//   ✅ No CORS complications
//   ✅ session_id is a UUID (not sensitive like an auth token)
//   ✅ Firebase handles real auth separately
//   ❌ Alternative: httpOnly cookies would require backend Set-Cookie
//      header, CORS preflight changes, and SameSite config — too
//      invasive for a non-sensitive session identifier.
// ─────────────────────────────────────────────────────────────────

import { create } from "zustand";
import { sendConversation, startSession } from "../api/apiClient";

const SESSION_KEY = "samvaad_session_id";
const DEBOUNCE_MS = 300;

// ── localStorage helpers ─────────────────────────────────────────

function loadSessionId() {
    try {
        return localStorage.getItem(SESSION_KEY) || null;
    } catch {
        return null;
    }
}

function saveSessionId(id) {
    try {
        if (id) localStorage.setItem(SESSION_KEY, id);
    } catch {
        // localStorage unavailable (private browsing, etc.)
    }
}

function clearSessionId() {
    try {
        localStorage.removeItem(SESSION_KEY);
    } catch {
        // noop
    }
}

// ── Debounce timer ───────────────────────────────────────────────

let _debounceTimer = null;

const useConversationStore = create((set, get) => ({
    // ── State ────────────────────────────────────────────────────────
    messages: [],
    sessionId: loadSessionId(),
    profile: {},
    eligibility: null,
    schemes: [],
    documents: [],
    currentQuestion: null,
    isLoading: false,
    error: null,

    // Internal: AbortController for the current in-flight request
    _controller: null,

    // ── Actions ──────────────────────────────────────────────────────

    /**
     * Send a user message to the backend and process the response.
     *
     * Automatically:
     *   • Debounces rapid calls (300ms)
     *   • Auto-creates session if none exists
     *   • Appends user message to chat
     *   • Cancels any in-flight request (AbortController)
     *   • Calls POST /v1/conversation
     *   • Appends assistant response to chat
     *   • Updates profile, eligibility, sessionId
     *   • Persists sessionId to localStorage
     *
     * @param {string} query - User's message text
     * @param {string} [language] - Language code (en, hi, mr)
     * @returns {Promise<Object|undefined>} The API result, or undefined on error
     */
    sendMessage: async (query, language = "en") => {
        // Clear any pending debounce
        if (_debounceTimer) {
            clearTimeout(_debounceTimer);
            _debounceTimer = null;
        }

        // Debounce: wait 300ms before actually sending
        await new Promise((resolve) => {
            _debounceTimer = setTimeout(resolve, DEBOUNCE_MS);
        });

        // Cancel any in-flight request
        const prev = get()._controller;
        if (prev) prev.abort();

        const controller = new AbortController();

        // Optimistic: append user message + set loading
        set((state) => ({
            messages: [...state.messages, { role: "user", content: query }],
            isLoading: true,
            error: null,
            _controller: controller,
        }));

        try {
            // Auto-create session if missing
            let sessionId = get().sessionId;
            if (!sessionId) {
                try {
                    const session = await startSession(controller.signal);
                    sessionId = session.sessionId;
                    saveSessionId(sessionId);
                    set({ sessionId });
                } catch {
                    // Session creation failed — proceed without session
                    // (stateless mode still works)
                    console.warn("[SamvaadAI] Session creation failed, continuing stateless");
                }
            }

            const result = await sendConversation({
                query,
                language,
                sessionId,
                signal: controller.signal,
            });

            // Only update if this controller is still active (not aborted)
            if (controller.signal.aborted) return;

            // Persist session from response
            const newSessionId = result.sessionId || sessionId;
            if (newSessionId) saveSessionId(newSessionId);

            set((state) => ({
                messages: [
                    ...state.messages,
                {
                    role: "assistant",
                    content: result.response || "I couldn't generate a response. Please try again.",
                },
            ],
                sessionId: newSessionId,
                profile: result.profile,
                eligibility: {
                    eligible: result.eligibleSchemes,
                    partiallyEligible: result.partialSchemes,
                    ineligible: result.ineligibleSchemes,
                },
                schemes: result.schemes || [],
                documents:
                result.documents?.length
                ? result.documents
                : (result.schemes || []).flatMap((s) => s.documents || []),
                currentQuestion: result.question || null,
                isLoading: false,
                error: null,
                _controller: null,
            }));

            return result;
        } catch (err) {
            // Ignore abort errors (user sent a new message)
            if (err.name === "ApiError" && err.status === 0) {
                set({ isLoading: false, _controller: null });
                return;
            }
            if (err.name === "AbortError") {
                set({ isLoading: false, _controller: null });
                return;
            }

            set({
                isLoading: false,
                error: err.detail || err.message || "Sorry, something went wrong. Please try again.",
                _controller: null,
            });
        }
    },

    /**
     * Reset conversation for a fresh session.
     */
    resetConversation: () => {
        const prev = get()._controller;
        if (prev) prev.abort();
        clearSessionId();

        set({
            messages: [],
            sessionId: null,
            profile: {},
            eligibility: null,
            schemes: [],
            documents: [],
            currentQuestion: null,
            isLoading: false,
            error: null,
            _controller: null,
        });
    },

    /**
     * Clear error state.
     */
    clearError: () => set({ error: null }),
}));

export default useConversationStore;
