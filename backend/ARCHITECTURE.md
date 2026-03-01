# SamvaadAI Backend Architecture

## System Overview

**Product Identity**: Conversational Eligibility Guidance System  
**Core Principle**: Deterministic decisions. AI for language only.

## Architectural Layers

```
┌─────────────────────────────────────────┐
│         API Layer (FastAPI)             │
│  - Request validation                   │
│  - Error handling                       │
│  - No business logic                    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Orchestration Layer                │
│  - Coordinate scheme loading            │
│  - Call deterministic engine            │
│  - Track latency                        │
│  - No transformation                    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   Eligibility Engine (Deterministic)    │
│  - Pure rule evaluation                 │
│  - No side effects                      │
│  - No LLM involvement                   │
│  - Traceable decisions                  │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        Scheme Loader                    │
│  - Load from S3 (future)                │
│  - In-memory caching                    │
│  - Deterministic ordering               │
└─────────────────────────────────────────┘
```

## Key Architectural Guarantees

### 1. Determinism
- Same input → same output (always)
- No reliance on dict ordering
- Explicit sorting by scheme_id
- No hidden state
- No side effects

### 2. Separation of Concerns
- API layer: Validation & routing only
- Orchestration: Coordination only
- Engine: Evaluation only
- No business logic in routes

### 3. Observability
- Structured JSON logging
- Request ID tracking
- Latency measurement
- No PII in logs

### 4. Resilience
- Graceful error handling
- Safe error responses
- No stack traces in production
- Stale cache fallback

## API Contract (Frozen)

### Public Endpoints (Conversational)
- `POST /v1/session/start` - Create session
- `POST /v1/conversation/input` - Process input
- `GET /v1/conversation/results` - Get results

### Internal Endpoint (Testing Only)
- `POST /v1/evaluate` - Direct evaluation

⚠️ `/evaluate` is NOT public-facing. Product identity is conversational-first.

## Performance Targets (from requirements.md)

- API latency: < 500ms (p95)
- Evaluation: < 2 seconds
- Session TTL: 1 hour
- No permanent PII storage

## Caching Strategy

### Scheme Caching
- **Location**: In-memory
- **TTL**: 5 minutes (configurable)
- **Cold start**: Load on first request
- **Invalidation**: TTL-based
- **Failure mode**: Return stale cache

### Future S3 Integration
1. Connect to S3 bucket
2. List objects with prefix "schemes/"
3. Download and parse JSON
4. Validate schema
5. Sort by scheme_id (determinism)
6. Cache in memory

## Failure Modes

### Scheme Loading Failure
- **Behavior**: Return stale cache if available
- **Logging**: Error logged with details
- **Response**: 500 if no cache available

### Evaluation Failure
- **Behavior**: Raise exception
- **Logging**: Error logged with request_id
- **Response**: 500 with safe message

### Malformed Scheme JSON
- **Behavior**: Skip invalid schemes
- **Logging**: Warning logged
- **Response**: Continue with valid schemes

## Configuration

All environment-dependent values in `core/config.py`:
- AWS region
- DynamoDB table name
- S3 bucket name
- Session TTL
- Cache TTL
- Feature toggles

## Logging

### Structured Format (JSON)
```json
{
  "timestamp": "2025-03-01T12:00:00Z",
  "level": "INFO",
  "logger": "samvaadai",
  "message": "Request completed",
  "request_id": "uuid",
  "endpoint": "/v1/evaluate",
  "status_code": 200,
  "latency_ms": 45.23,
  "evaluation_count": 3
}
```

### No PII Logging
- No user profiles
- No session data
- No personal attributes
- Only aggregated metrics

## Testing Strategy

### Unit Tests (17 tests)
- Engine operators
- Determinism
- Edge cases
- Performance

### Integration Tests (11 tests)
- Full flow
- Caching
- Error handling
- API endpoints

### Total: 30 tests (all passing)

## Deployment

- **Platform**: AWS Lambda
- **Framework**: FastAPI + Mangum
- **Gateway**: API Gateway
- **Monitoring**: CloudWatch
- **Logs**: Structured JSON

## Future Enhancements

1. S3 scheme loader integration
2. DynamoDB session management
3. LLM conversation handler
4. Advanced caching strategies
5. Performance optimization

## Non-Negotiable Constraints

From requirements.md and design.md:
- ✅ Deterministic engine
- ✅ No LLM in eligibility
- ✅ Stateless architecture
- ✅ Session TTL = 1 hour
- ✅ No permanent PII
- ✅ API latency < 500ms
- ✅ Evaluation < 2 seconds
