# Phase 14 — Final Engineering Report

## 1. Integration Readiness Summary

| Component | Status | Notes |
|---|---|---|
| Frontend ↔ Backend API | ✅ Integrated | `apiClient.js` handles retry, cache, dedup, throttle |
| Voice Pipeline | ✅ Integrated | STT (Web Speech API) + TTS per language locale |
| Eligibility Rendering | ✅ Integrated | `Results.jsx` + `SchemeDetail.jsx` — zero frontend logic |
| i18n (en/hi/mr) | ✅ Complete | All UI strings use `t()` with safe fallback chain |
| Security | ✅ Hardened | Rate limit + prompt injection + CORS + input validation |
| Middleware Stack | ✅ Ordered | RequestTracking → RateLimit → CORS |

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                    FRONTEND (React)                   │
│  ┌──────┐  ┌──────┐  ┌────────┐  ┌───────────────┐  │
│  │ Chat │  │Results│  │Scheme  │  │  useUIStore   │  │
│  │ .jsx │  │ .jsx  │  │Detail  │  │  (language)   │  │
│  └──┬───┘  └──┬───┘  └───┬────┘  └───────────────┘  │
│     │         │          │                            │
│  ┌──┴─────────┴──────────┴───────────────────────┐   │
│  │           apiClient.js                         │   │
│  │  (retry, cache, dedup, throttle, abort)         │   │
│  └────────────────────┬──────────────────────────┘   │
└───────────────────────┼──────────────────────────────┘
                        │ POST /v1/conversation
                        ▼
┌───────────────────────────────────────────────────────┐
│                 BACKEND (FastAPI + Lambda)              │
│                                                        │
│  ┌────────────────────────────────────────────────┐   │
│  │ Middleware Stack                                │   │
│  │  1. RequestTrackingMiddleware (request ID)      │   │
│  │  2. RateLimitMiddleware (100 req/min/IP)        │   │
│  │  3. CORSMiddleware                              │   │
│  └────────────────────┬───────────────────────────┘   │
│                       ▼                                │
│  ┌─────────── routes.py ──────────────────────────┐   │
│  │  sanitize_input() → ConversationManager         │   │
│  └────────────────────┬───────────────────────────┘   │
│                       ▼                                │
│  ┌──── ConversationManager (orchestration) ───────┐   │
│  │  1. InferenceGateway → Bedrock (profile + resp) │   │
│  │  2. EligibilityEngine → deterministic rules     │   │
│  │  3. InferenceGateway → explanation (if ready)   │   │
│  └────────────────────┬───────────────────────────┘   │
│                       ▼                                │
│  ┌────── Eligibility Engine ──────────────────────┐   │
│  │  RuleParser → deterministic evaluation          │   │
│  │  No side effects, sorted output                 │   │
│  └────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────┘
```

## 3. Critical Engineering Fixes Applied

| Fix | File | Impact |
|---|---|---|
| Hardcoded strings → `t()` | `Chat.jsx`, `Results.jsx`, `SchemeDetail.jsx` | i18n compliance |
| RateLimitMiddleware registered | `main.py` | DDoS protection active |
| Middleware ordering | `main.py` | Blocks abuse before CORS |
| `sanitize_input()` in route | `routes.py` | Prompt injection defense |
| Configurable rate limits | `config.py` | Production scalability |

## 4. Performance Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Bedrock cold start | High | Provisioned concurrency |
| LLM p95 latency > 3s | High | Cache + single-call optimization |
| In-memory rate store | Medium | Migrate to DynamoDB/Redis for multi-instance |
| Browser STT quality for mr-IN | Medium | Fallback to text input |

## 5. Cost Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Duplicate LLM calls | Low | Request dedup + AbortController |
| Cache miss storms | Medium | 60s TTL + bounded cache (20 entries) |
| Rapid user clicks | Low | 300ms debounce + 2s throttle |
| Long conversations | Medium | 2000-char query limit + max 1024 tokens |

## 6. Production Deployment Recommendations

1. **Enable provisioned concurrency** for Lambda (2 warm instances)
2. **Set `ALLOWED_ORIGINS`** to production domain only
3. **Migrate `_rate_store`** to DynamoDB for distributed rate limiting
4. **Monitor Bedrock latency** via CloudWatch custom metrics
5. **Enable WAF** on API Gateway for additional DDoS protection
6. **Set `APP_ENV=production`** to activate production CORS whitelist

---

## 7. Next Phase — Document Intelligence Pipeline Design

### Pipeline Architecture

```
Document Upload → OCR (Textract) → Layout Detection
→ Schema Detection → Field Extraction → JSON Output
```

### Extraction Rules

| Rule | Detail |
|---|---|
| Dates | ISO 8601 format (`YYYY-MM-DD`) |
| Currency | ISO currency codes (INR, USD) |
| Numerics | Strip commas, convert to number |
| Addresses | Return as full text |
| Missing fields | Return `null`, never fabricate |

### Output Schema (with Confidence Scores)

```json
{
  "document_type": "invoice",
  "fields": {
    "invoice_number": {
      "value": "INV-2039",
      "confidence": 0.94
    },
    "date": {
      "value": "2026-01-15",
      "confidence": 0.98
    },
    "supplier_name": {
      "value": "Tata Steel Ltd",
      "confidence": 0.91
    },
    "total_amount": {
      "value": 4580.50,
      "confidence": 0.91
    },
    "tax_amount": {
      "value": 824.49,
      "confidence": 0.87
    },
    "currency": {
      "value": "INR",
      "confidence": 0.99
    }
  },
  "validation": {
    "total_tax_check": true,
    "date_format_valid": true
  }
}
```

### Design Safeguards

| Safeguard | Implementation |
|---|---|
| OCR noise handling | Pre-process with deskew + denoise before Textract |
| Hallucination prevention | Confidence threshold (< 0.7 → return `null`) |
| Schema detection | Document classifier before extraction |
| Deterministic output | Template-based extraction, LLM only for ambiguous fields |
