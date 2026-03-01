# Structured Logging Guide

## Overview

SamvaadAI uses structured JSON logging for machine-readable, searchable logs with zero PII leakage.

## Log Format

All logs are output as JSON with the following structure:

```json
{
  "timestamp": "2025-03-01T12:34:56.789Z",
  "level": "INFO",
  "logger": "samvaadai",
  "message": "Human-readable message",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "endpoint": "/v1/evaluate",
  "status_code": 200,
  "latency_ms": 45.23,
  "evaluation_count": 3,
  "error_type": "ValueError"
}
```

## Field Descriptions

| Field | Type | Description | Always Present |
|-------|------|-------------|----------------|
| `timestamp` | string | UTC timestamp in ISO 8601 format | Yes |
| `level` | string | Log level (DEBUG, INFO, WARNING, ERROR) | Yes |
| `logger` | string | Logger name (always "samvaadai") | Yes |
| `message` | string | Human-readable log message | Yes |
| `request_id` | string | Unique UUID for request tracking | Conditional |
| `endpoint` | string | API endpoint path | Conditional |
| `status_code` | integer | HTTP status code | Conditional |
| `latency_ms` | float | Request latency in milliseconds | Conditional |
| `evaluation_count` | integer | Number of schemes evaluated | Conditional |
| `error_type` | string | Exception class name | Conditional |
| `exception` | string | Stack trace (development only) | Conditional |

## Log Levels

### INFO
Normal operational events:
- Request completed successfully
- Session created
- Evaluation completed
- Schemes loaded

### WARNING
Potentially problematic situations:
- Latency threshold exceeded
- Returning stale cache
- Client errors (4xx)

### ERROR
Error events that might still allow the application to continue:
- Evaluation failed
- Scheme loading failed
- Server errors (5xx)

### DEBUG
Detailed information for debugging (development only):
- Cache hit/miss
- Detailed timing information
- Internal state changes

## Sample Log Outputs

### Successful Request
```json
{
  "timestamp": "2025-03-01T10:15:30.123Z",
  "level": "INFO",
  "logger": "samvaadai",
  "message": "Request completed",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "endpoint": "/v1/evaluate",
  "status_code": 200,
  "latency_ms": 42.56
}
```

### Evaluation with Latency Tracking
```json
{
  "timestamp": "2025-03-01T10:15:30.100Z",
  "level": "INFO",
  "logger": "samvaadai",
  "message": "Evaluation completed in 38.45ms for 3 schemes",
  "latency_ms": 38.45,
  "evaluation_count": 3
}
```

### Latency Warning
```json
{
  "timestamp": "2025-03-01T10:20:15.456Z",
  "level": "WARNING",
  "logger": "samvaadai",
  "message": "Evaluation latency 2150.34ms exceeds threshold 2000ms",
  "latency_ms": 2150.34
}
```

### Client Error (400)
```json
{
  "timestamp": "2025-03-01T10:25:45.789Z",
  "level": "WARNING",
  "logger": "samvaadai",
  "message": "Request error",
  "request_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "endpoint": "/v1/evaluate",
  "status_code": 400,
  "latency_ms": 5.12,
  "error_type": "HTTP_400"
}
```

### Server Error (500)
```json
{
  "timestamp": "2025-03-01T10:30:20.345Z",
  "level": "ERROR",
  "logger": "samvaadai",
  "message": "Evaluation failed: Scheme loading error",
  "request_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "error_type": "SchemeLoadError"
}
```

### Scheme Loading
```json
{
  "timestamp": "2025-03-01T10:00:00.000Z",
  "level": "INFO",
  "logger": "samvaadai",
  "message": "Loaded 3 schemes from source"
}
```

### Cache Fallback
```json
{
  "timestamp": "2025-03-01T10:35:10.567Z",
  "level": "WARNING",
  "logger": "samvaadai",
  "message": "Returning stale cache due to load failure"
}
```

## Querying Logs

### CloudWatch Insights Queries

**Find slow requests (> 500ms)**:
```
fields @timestamp, request_id, endpoint, latency_ms
| filter latency_ms > 500
| sort latency_ms desc
```

**Count requests by endpoint**:
```
fields endpoint
| stats count() by endpoint
```

**Find errors by type**:
```
fields @timestamp, error_type, message
| filter level = "ERROR"
| stats count() by error_type
```

**Track evaluation performance**:
```
fields @timestamp, evaluation_count, latency_ms
| filter evaluation_count > 0
| stats avg(latency_ms), max(latency_ms), min(latency_ms) by evaluation_count
```

**Find requests by ID**:
```
fields @timestamp, message, endpoint, status_code
| filter request_id = "your-request-id-here"
| sort @timestamp asc
```

## PII Protection

### What is NEVER logged:
- ❌ User profile data (age, income, occupation, etc.)
- ❌ Session attributes
- ❌ Personal identifiers
- ❌ Location details
- ❌ Any user input

### What IS logged:
- ✅ Request IDs (anonymous UUIDs)
- ✅ Endpoint paths
- ✅ Status codes
- ✅ Latency metrics
- ✅ Error types (no details)
- ✅ Aggregated counts

## Configuration

### Enable/Disable Structured Logging
```bash
# Enable (default)
export ENABLE_STRUCTURED_LOGGING=true

# Disable (simple format for development)
export ENABLE_STRUCTURED_LOGGING=false
```

### Enable/Disable Latency Tracking
```bash
# Enable (default)
export ENABLE_LATENCY_TRACKING=true

# Disable
export ENABLE_LATENCY_TRACKING=false
```

### Environment-Specific Behavior

**Development** (`APP_ENV=development`):
- Log level: DEBUG
- Simple format option available
- Stack traces included

**Production** (`APP_ENV=production`):
- Log level: INFO
- Structured JSON only
- No stack traces in logs

## Best Practices

1. **Always include request_id** when logging request-specific events
2. **Use appropriate log levels** (don't log INFO as ERROR)
3. **Never log PII** - use aggregated metrics only
4. **Include context** - add relevant fields for searchability
5. **Keep messages concise** - details go in structured fields
6. **Use consistent field names** - follow the schema above

## Integration with Monitoring

### CloudWatch
- Logs automatically sent to CloudWatch Logs
- Use CloudWatch Insights for querying
- Set up alarms on error rates and latency

### Future Integrations
- Elasticsearch/Kibana for advanced search
- Grafana for visualization
- Datadog/New Relic for APM

## Troubleshooting

### Request Tracking
1. Get request_id from response header `X-Request-ID`
2. Search logs for that request_id
3. View complete request lifecycle

### Performance Issues
1. Query logs for high latency_ms
2. Check evaluation_count correlation
3. Identify slow endpoints

### Error Investigation
1. Filter by level = "ERROR"
2. Group by error_type
3. Check request_id for context
4. Review timestamp patterns

## Example: Debugging a Slow Request

1. **Identify slow request**:
```
filter latency_ms > 500
| fields @timestamp, request_id, endpoint, latency_ms
```

2. **Get full request context**:
```
filter request_id = "found-request-id"
| fields @timestamp, message, latency_ms, evaluation_count
| sort @timestamp asc
```

3. **Check evaluation performance**:
```
filter evaluation_count > 0 and latency_ms > 2000
| stats count(), avg(latency_ms) by evaluation_count
```

4. **Investigate scheme loading**:
```
filter message like /scheme/
| fields @timestamp, message
```

## Compliance

- ✅ GDPR compliant (no PII)
- ✅ Data minimization principle
- ✅ Audit trail for requests
- ✅ Retention policy configurable
- ✅ No sensitive data exposure
