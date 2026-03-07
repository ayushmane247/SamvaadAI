# SamvaadAI Backend Execution Roadmap

**Version**: 2.0  
**Last Updated**: March 3, 2026  
**Owner**: Backend Team (Ayush, Pranit, Ratnadeep)  
**Status**: Day 2 Complete + LLM Service Ready → Day 3 Integration Phase

---

## 📊 Executive Summary

### Current Production Readiness: 85%

**What's Built (Day 1-2 Complete + LLM Service)**:
- ✅ FastAPI backend with OpenAPI 3.1 documentation
- ✅ AWS Lambda deployment layer (Mangum adapter)
- ✅ Mock scheme loader (S3 integration ready)
- ✅ DynamoDB session service (TTL: 1 hour)
- ✅ Deterministic eligibility engine (17 passing tests)
- ✅ API Gateway integration ready
- ✅ Environment-based configuration
- ✅ CORS security hardening
- ✅ Dependency hygiene (boto3 added)
- ✅ **LLM Service Module (standalone, production-ready)**
- ✅ **Bedrock client with guardrails**
- ✅ **Intent extraction + Explanation generation**
- ✅ **Fallback templates (3 languages)**
- ✅ **30 passing tests (17 engine + 8 API + 11 integration)**

**What's Missing (Day 3-4 Remaining)**:
- ❌ LLM Service integration into main backend
- ❌ Conversation handler implementation
- ❌ S3 scheme loader (currently using mock data)
- ❌ DynamoDB session persistence (service exists, not integrated)
- ❌ CloudWatch structured logging dashboards
- ❌ CloudWatch metrics tracking
- ❌ X-Ray distributed tracing
- ❌ API Gateway rate limiting configuration
- ❌ IAM least-privilege hardening
- ❌ CI/CD pipeline
- ❌ Infrastructure as Code (CloudFormation/Terraform)

---

## 🎯 Mission-Critical Constraints

### Non-Negotiable Architectural Rules

From `requirements.md` and `design.md`:

1. **Deterministic-First Principle**: AI for language only, rule engine for eligibility
2. **No LLM in Decision Logic**: Zero hallucination in eligibility evaluation
3. **Stateless Lambda Architecture**: Horizontal scaling, no server state
4. **Session TTL = 1 Hour**: No permanent PII storage
5. **API Latency < 500ms (p95)**: Performance requirement
6. **Eligibility Evaluation < 2 seconds**: User experience requirement
7. **S3 Versioned Scheme Datasets**: Data freshness tracking
8. **last_verified_date Visible**: Trust signal for users

### Engineering Standards (PROJECT_ENGINEERING_RULEBOOK.md)

1. **No hardcoded values**: Use environment variables
2. **No print() in production**: Structured logging only
3. **snake_case for functions**: PascalCase for classes
4. **Validate all inputs**: Proper HTTP status codes
5. **No stack traces exposed**: Safe error responses
6. **Every PR references an issue**: Traceability
7. **No direct commits to main**: Feature branch workflow

---

## 📋 Status Audit: Completed vs. Remaining

### ✅ COMPLETED (Day 1-2 + LLM Service)

#### 1. API Layer (85% Complete)
| Component | Status | Owner | Notes |
|-----------|--------|-------|-------|
| FastAPI skeleton | ✅ Done | Ayush | Deployed on Lambda |
| OpenAPI 3.1 spec | ✅ Done | Ayush | Auto-documented at `/prod/openapi.json` |
| Health check endpoint | ✅ Done | Ayush | `GET /health` |
| Session start endpoint | ✅ Done | Ayush | `POST /v1/session/start` |
| Conversation input endpoint | ⚠️ Stub | Ayush | Needs LLM integration |
| Conversation results endpoint | ⚠️ Stub | Ayush | Needs session retrieval |
| Evaluate endpoint (internal) | ✅ Done | Ayush | `POST /v1/evaluate` |
| Request validation | ✅ Done | Ayush | Pydantic models |
| Error handling | ✅ Done | Ayush | Global exception handler |
| CORS configuration | ✅ Done | Ayush | Environment-based |

#### 2. AWS Integration (60% Complete)
| Component | Status | Owner | Notes |
|-----------|--------|-------|-------|
| Lambda deployment | ✅ Done | Ayush | Mangum adapter configured |
| API Gateway | ✅ Done | Ayush | Root path `/prod` |
| S3 bucket | ⚠️ Ready | Ayush | Using mock loader currently |
| S3 scheme loader | ⚠️ Mock | Ayush | Real S3 integration pending |
| DynamoDB table | ⚠️ Service Ready | Ayush | Not integrated yet |
| DynamoDB TTL | ⚠️ Service Ready | Ayush | 1 hour expiration configured |
| boto3 dependency | ✅ Done | Ayush | Added to requirements.txt |
| Environment config | ✅ Done | Ayush | `core/config.py` |
| Cold start optimization | ⚠️ Pending | Ayush | Scheme preload needed |

#### 3. Eligibility Engine (100% Complete)
| Component | Status | Owner | Notes |
|-----------|--------|-------|-------|
| Rule evaluator | ✅ Done | Pranit | Pure Python, deterministic |
| Rule parser | ✅ Done | Pranit | Supports 8 operators |
| Explanation trace | ✅ Done | Pranit | Every result explained |
| Partial eligibility | ✅ Done | Pranit | Missing data guidance |
| Unit tests | ✅ Done | Pranit | 17 tests passing |
| Performance validation | ✅ Done | Pranit | < 100ms for 10 schemes |
| Determinism guarantee | ✅ Done | Pranit | Same input → same output |

#### 4. LLM Service (100% Complete - Standalone)
| Component | Status | Owner | Notes |
|-----------|--------|-------|-------|
| Bedrock client | ✅ Done | Ratnadeep | With retry logic |
| Intent extraction | ✅ Done | Ratnadeep | Natural language → JSON |
| Explanation generation | ✅ Done | Ratnadeep | Technical → Simple language |
| Multilingual support | ✅ Done | Ratnadeep | English, Hindi, Marathi |
| Prompt templates | ✅ Done | Ratnadeep | Versioned in files |
| Fallback templates | ✅ Done | Ratnadeep | All 3 languages |
| LLM guardrails | ✅ Done | Ratnadeep | Prevents eligibility decisions |
| Safety validation | ✅ Done | Ratnadeep | JSON + schema validation |
| Unit tests | ✅ Done | Ratnadeep | Comprehensive coverage |
| Integration tests | ✅ Done | Ratnadeep | With mock rule engine |

#### 5. Scheme Data (50% Complete)
| Component | Status | Owner | Notes |
|-----------|--------|-------|-------|
| Scheme JSON schema | ✅ Done | Pranit | Validated structure |
| Maharashtra schemes | ✅ Done | Pranit | 5 schemes in `docs/` |
| Mock scheme loader | ✅ Done | Ayush | 3 test schemes |
| S3 upload | ❌ Pending | Ayush | Need to upload to S3 |
| Scheme loader (S3) | ⚠️ Ready | Ayush | Code exists, not integrated |
| Versioning | ⚠️ Ready | Ayush | S3 versioning enabled |
| last_verified_date | ✅ Done | Pranit | In all scheme JSONs |

#### 6. Testing (100% Complete)
| Component | Status | Owner | Notes |
|-----------|--------|-------|-------|
| Engine unit tests | ✅ Done | Pranit | 17 tests passing |
| API integration tests | ✅ Done | Ayush | 8 tests passing |
| Full flow tests | ✅ Done | Ayush | 11 tests passing |
| LLM service tests | ✅ Done | Ratnadeep | Standalone module |
| Total test count | ✅ Done | All | 30+ tests passing |

---

### ❌ REMAINING (Day 3-4)

#### 1. LLM Integration (50% Complete) - BLOCKING
| Component | Status | Owner | Priority | Estimated Time |
|-----------|--------|-------|----------|----------------|
| Bedrock API setup | ✅ Done | Ratnadeep | P0 | - |
| Intent extraction | ✅ Done | Ratnadeep | P0 | - |
| Explanation generation | ✅ Done | Ratnadeep | P0 | - |
| Multilingual support | ✅ Done | Ratnadeep | P0 | - |
| Prompt templates | ✅ Done | Ratnadeep | P0 | - |
| Fallback templates | ✅ Done | Ratnadeep | P0 | - |
| LLM guardrails | ✅ Done | Ratnadeep | P0 | - |
| **Move to main backend** | ❌ Not Started | Ayush | P0 | 1 hour |
| **Merge configuration** | ❌ Not Started | Ayush | P0 | 30 min |
| **Integration testing** | ❌ Not Started | All | P0 | 1 hour |
| Latency optimization | ❌ Not Started | Ratnadeep | P1 | 2 hours |

**Total Estimated Time**: 4.5 hours (was 21 hours, saved 16.5 hours!)

#### 2. Conversation Handler (0% Complete) - BLOCKING
| Component | Status | Owner | Priority | Estimated Time |
|-----------|--------|-------|----------|----------------|
| Session state management | ❌ Not Started | Ayush | P0 | 2 hours |
| Attribute extraction | ❌ Not Started | Ayush | P0 | 2 hours |
| Question generation | ❌ Not Started | Ayush | P0 | 3 hours |
| LLM orchestration | ❌ Not Started | Ayush | P0 | 2 hours |
| Rule engine integration | ❌ Not Started | Ayush | P0 | 2 hours |
| Results caching | ❌ Not Started | Ayush | P1 | 2 hours |
| Error handling | ❌ Not Started | Ayush | P1 | 2 hours |

**Total Estimated Time**: 15 hours (was 19 hours, saved 4 hours!)

#### 3. Data Layer Integration (0% Complete) - BLOCKING
| Component | Status | Owner | Priority | Estimated Time |
|-----------|--------|-------|----------|----------------|
| S3 scheme loader integration | ❌ Not Started | Ayush | P0 | 2 hours |
| Upload schemes to S3 | ❌ Not Started | Ayush | P0 | 1 hour |
| DynamoDB session integration | ❌ Not Started | Ayush | P0 | 2 hours |
| Session TTL validation | ❌ Not Started | Ayush | P0 | 1 hour |

**Total Estimated Time**: 6 hours

#### 3. Observability (40% Complete)
| Component | Status | Owner | Priority | Estimated Time |
|-----------|--------|-------|----------|----------------|
| Structured logging | ✅ Done | Ayush | P0 | - |
| CloudWatch logs | ✅ Done | Ayush | P0 | - |
| CloudWatch dashboards | ❌ Not Started | Ayush | P1 | 3 hours |
| CloudWatch metrics | ❌ Not Started | Ayush | P1 | 3 hours |
| X-Ray tracing | ❌ Not Started | Ayush | P2 | 4 hours |
| Latency tracking | ✅ Done | Ayush | P0 | - |
| Error tracking | ✅ Done | Ayush | P0 | - |

**Total Estimated Time**: 10 hours (1.3 days)

#### 4. Security & Compliance (70% Complete)
| Component | Status | Owner | Priority | Estimated Time |
|-----------|--------|-------|----------|----------------|
| CORS hardening | ✅ Done | Ayush | P0 | - |
| Input validation | ✅ Done | Ayush | P0 | - |
| Rate limiting | ❌ Not Started | Ayush | P1 | 2 hours |
| IAM least-privilege | ❌ Not Started | Ayush | P1 | 3 hours |
| WAF configuration | ❌ Not Started | Ayush | P2 | 4 hours |
| Secrets management | ⚠️ Partial | Ayush | P1 | 2 hours |

**Total Estimated Time**: 11 hours (1.4 days)

#### 5. DevOps & Infrastructure (0% Complete)
| Component | Status | Owner | Priority | Estimated Time |
|-----------|--------|-------|----------|----------------|
| CI/CD pipeline | ❌ Not Started | Ayush | P2 | 6 hours |
| CloudFormation/Terraform | ❌ Not Started | Ayush | P2 | 8 hours |
| Automated testing | ❌ Not Started | All | P2 | 4 hours |
| Deployment docs | ❌ Not Started | Ayush | P1 | 2 hours |

**Total Estimated Time**: 20 hours (2.5 days)

---

## 🗓️ Day 3-4 Execution Plan (UPDATED)

### Day 3: Full End-to-End Integration (CRITICAL)

**Goal**: Complete conversation flow working end-to-end

**Morning (4 hours)**:
1. **Ayush**: Integrate LLM service into main backend (1 hour)
   - Move llm_service module to backend root
   - Merge configuration files
   - Update imports
2. **Ayush**: Integrate S3 scheme loader (2 hours)
   - Replace mock loader with real S3 loader
   - Upload 5 Maharashtra schemes to S3
   - Test scheme loading
3. **Ayush**: Integrate DynamoDB session service (1 hour)
   - Connect session endpoints to DynamoDB
   - Test session creation and TTL
4. **Pranit**: Validate rule engine with real schemes (1 hour)
   - Test with uploaded S3 schemes
   - Fix any compatibility issues

**Afternoon (4 hours)**:
1. **Ayush**: Implement conversation handler (4 hours)
   - Session state management
   - Attribute extraction using LLM
   - Question generation logic
   - Rule engine integration
2. **Ratnadeep**: Test LLM service integration (2 hours)
   - Test intent extraction with conversation handler
   - Test explanation generation
   - Optimize prompts if needed
3. **Pranit**: Prepare demo scenarios (2 hours)
   - Create test profiles
   - Document expected results

**Evening (3 hours)**:
1. **All**: Integration testing (2 hours)
   - Test full conversation flow
   - Test all 3 languages
   - Test edge cases
2. **Ayush**: Fix integration bugs (1 hour)
3. **All**: Validate performance targets (30 min)
   - API latency < 500ms
   - Eligibility evaluation < 2 seconds

**EOD Day 3 Checkpoint**:
- [ ] Full conversation flow working
- [ ] LLM service integrated
- [ ] S3 scheme loader working
- [ ] DynamoDB sessions working
- [ ] Rule engine integrated
- [ ] API latency < 500ms validated
- [ ] No critical bugs

---

### Day 4: Polish & Production Readiness

**Goal**: System demo-ready, all performance targets met

**Morning (3 hours)**:
1. **Ayush**: Configure CloudWatch dashboards (2 hours)
2. **Ayush**: Set up API Gateway rate limiting (1 hour)
3. **Ratnadeep**: Refine prompts for demo (1 hour)
4. **Pranit**: Validate all schemes (1 hour)

**Afternoon (3 hours)**:
1. **Ayush**: IAM least-privilege review (2 hours)
2. **Ayush**: Document deployment process (1 hour)
3. **Ratnadeep**: Test edge cases (1 hour)
4. **Pranit**: Prepare demo script (1 hour)

**Evening (2 hours)**:
1. **All**: Final integration testing
2. **All**: Prepare demo presentation
3. **All**: Fix minor bugs

**EOD Day 4 Checkpoint**:
- [ ] System demo-ready
- [ ] All performance targets met
- [ ] Demo script prepared
- [ ] Documentation complete

---

## 📊 Work Distribution Table (UPDATED)

### Priority 0 (BLOCKING) - Must Complete Day 3

| Task ID | Task | Owner | Estimated Time | Dependencies | Status |
|---------|------|-------|----------------|--------------|--------|
| P0-1 | Integrate LLM service to main backend | Ayush | 1h | None | ❌ |
| P0-2 | Merge LLM configuration | Ayush | 0.5h | P0-1 | ❌ |
| P0-3 | Integrate S3 scheme loader | Ayush | 2h | None | ❌ |
| P0-4 | Upload schemes to S3 | Ayush | 1h | P0-3 | ❌ |
| P0-5 | Integrate DynamoDB session service | Ayush | 1h | None | ❌ |
| P0-6 | Test session TTL | Ayush | 0.5h | P0-5 | ❌ |
| P0-7 | Implement session state management | Ayush | 2h | P0-5 | ❌ |
| P0-8 | Implement attribute extraction | Ayush | 2h | P0-1, P0-7 | ❌ |
| P0-9 | Implement question generation | Ayush | 3h | P0-7, P0-8 | ❌ |
| P0-10 | Integrate LLM in conversation flow | Ayush | 2h | P0-1, P0-9 | ❌ |
| P0-11 | Integrate rule engine in conversation | Ayush | 2h | P0-10 | ❌ |
| P0-12 | End-to-end integration testing | All | 2h | P0-1 to P0-11 | ❌ |
| P0-13 | Validate API latency < 500ms | Ayush | 0.5h | P0-12 | ❌ |

**Total P0 Time**: ~19.5 hours (distributed across 3 people = ~6.5 hours per person)
**Time Saved**: 17 hours (was 36.5 hours)

### Priority 1 (HIGH) - Complete Day 4

| Task ID | Task | Owner | Estimated Time | Dependencies | Status |
|---------|------|-------|----------------|--------------|--------|
| P1-1 | Implement fallback templates | Ratnadeep | 2h | P0-2, P0-3 | ❌ |
| P1-2 | Optimize LLM latency | Ratnadeep | 2h | P0-13 | ❌ |
| P1-3 | Implement results caching | Ayush | 2h | P0-11 | ❌ |
| P1-4 | Add conversation error handling | Ayush | 2h | P0-11 | ❌ |
| P1-5 | Configure CloudWatch dashboards | Ayush | 3h | P0-13 | ❌ |
| P1-6 | Configure CloudWatch metrics | Ayush | 3h | P0-13 | ❌ |
| P1-7 | Set up API Gateway rate limiting | Ayush | 2h | None | ❌ |
| P1-8 | IAM least-privilege review | Ayush | 3h | None | ❌ |
| P1-9 | Secrets management (AWS Secrets Manager) | Ayush | 2h | None | ❌ |
| P1-10 | Document deployment process | Ayush | 2h | P0-13 | ❌ |

**Total P1 Time**: ~23 hours (distributed across 2 people = ~11.5 hours per person)

### Priority 2 (NICE TO HAVE) - Post-Hackathon

| Task ID | Task | Owner | Estimated Time | Status |
|---------|------|-------|----------------|--------|
| P2-1 | X-Ray distributed tracing | Ayush | 4h | ❌ |
| P2-2 | WAF configuration | Ayush | 4h | ❌ |
| P2-3 | CI/CD pipeline | Ayush | 6h | ❌ |
| P2-4 | Infrastructure as Code | Ayush | 8h | ❌ |
| P2-5 | Automated testing pipeline | All | 4h | ❌ |

**Total P2 Time**: ~26 hours (Post-hackathon)

---

## 🔗 Frontend Integration Mapping

### Backend Tasks → Frontend Requirements

| Frontend Requirement | Backend Task | Owner | Status | Notes |
|---------------------|--------------|-------|--------|-------|
| Session management | P0-7 | Ayush | ❌ | Frontend needs `session_id` |
| Language selection (en/hi/mr) | P0-4 | Ratnadeep | ❌ | LLM must support 3 languages |
| Conversation flow | P0-9, P0-10 | Ayush | ❌ | `next_question` generation |
| Eligibility results | P0-11 | Ayush | ❌ | `eligible/partial/ineligible` |
| Explanation display | P0-3 | Ratnadeep | ❌ | Simple language explanations |
| Data freshness indicator | ✅ Done | Pranit | ✅ | `last_verified_date` in schemes |
| Session expiry warning | P0-7 | Ayush | ❌ | `expires_at` in session response |
| Error handling | P1-4 | Ayush | ❌ | Safe error messages |
| Low-bandwidth support | ✅ Done | Ayush | ✅ | Compressed JSON responses |

---

## 🚨 Risk & Compliance

### Critical Risks (from EXECUTION_CHARTER.md)

#### Risk 1: Bedrock Latency Spikes
**Impact**: LLM response time > 2 seconds  
**Probability**: Medium  
**Mitigation**:
- Use Anthropic Claude (fast model)
- Implement 3-second timeout
- Fallback to templates if LLM fails
- Cache common responses
**Owner**: Ratnadeep  
**Compliance Rule**: NFR-1 (Performance < 2s)

#### Risk 2: Integration Delays
**Impact**: Day 3 integration fails  
**Probability**: High  
**Mitigation**:
- Daily integration checkpoints
- No scope expansion
- Focus on MVP only
- Parallel development where possible
**Owner**: All  
**Compliance Rule**: EXECUTION_CHARTER (Integration by Day 3)

#### Risk 3: Lambda Cold Start Latency
**Impact**: API latency > 500ms  
**Probability**: Medium  
**Mitigation**:
- Scheme preload optimization (✅ Done)
- Monitor CloudWatch metrics
- Use provisioned concurrency if needed
**Owner**: Ayush  
**Compliance Rule**: NFR-1 (API latency < 500ms p95)

#### Risk 4: LLM Hallucination in Eligibility
**Impact**: LLM returns incorrect eligibility decisions  
**Probability**: Low (with guardrails)  
**Mitigation**:
- Strict guardrails: LLM never evaluates eligibility
- Validate LLM output format
- Fallback to templates if LLM fails
- Test with edge cases
**Owner**: Ratnadeep  
**Compliance Rule**: Design.md (LLM for language only)

#### Risk 5: DynamoDB TTL Misconfiguration
**Impact**: Sessions not expiring, PII stored permanently  
**Probability**: Low (already configured)  
**Mitigation**:
- TTL attribute set (✅ Done)
- Validate TTL working on Day 3
- Test session expiration (1 hour)
**Owner**: Ayush  
**Compliance Rule**: Requirements.md (No permanent PII)

---

### Engineering Rulebook Compliance

#### Must-Follow Rules (PROJECT_ENGINEERING_RULEBOOK.md)

| Rule | Compliance Status | Notes |
|------|-------------------|-------|
| No hardcoded API URLs | ✅ Compliant | Using environment variables |
| No hardcoded API keys | ✅ Compliant | Environment-based config |
| No print() in production | ✅ Compliant | Structured logging only |
| snake_case for functions | ✅ Compliant | Code review enforced |
| PascalCase for classes | ✅ Compliant | Code review enforced |
| Validate all inputs | ✅ Compliant | Pydantic models |
| Proper HTTP status codes | ✅ Compliant | FastAPI standards |
| No stack traces exposed | ✅ Compliant | Global exception handler |
| Every PR references issue | ⚠️ Partial | Need to enforce |
| No direct commits to main | ✅ Compliant | Branch protection |
| Feature branch workflow | ✅ Compliant | Git workflow enforced |
| Structured logging | ✅ Compliant | JSON logs to CloudWatch |
| No unused imports | ✅ Compliant | Linting enforced |
| Files < 300 lines | ✅ Compliant | Code review enforced |

---

## 📈 Success Criteria (Definition of Done)

### Day 3 EOD Checklist

- [ ] **LLM Integration Complete**
  - [ ] Bedrock API accessible
  - [ ] Intent extraction working
  - [ ] Explanation generation working
  - [ ] 3 languages supported (en, hi, mr)
  - [ ] LLM guardrails enforced
  - [ ] Fallback templates implemented

- [ ] **Conversation Handler Complete**
  - [ ] Session state management working
  - [ ] Attribute extraction working
  - [ ] Question generation working
  - [ ] LLM orchestration working
  - [ ] Rule engine integrated

- [ ] **End-to-End Flow Working**
  - [ ] User input → LLM → Rule Engine → Response
  - [ ] No critical bugs
  - [ ] API latency < 500ms (p95)
  - [ ] Eligibility evaluation < 2 seconds

- [ ] **Frontend Integration Ready**
  - [ ] All API endpoints functional
  - [ ] OpenAPI spec updated
  - [ ] CORS configured
  - [ ] Error handling working

### Day 4 EOD Checklist

- [ ] **Observability Complete**
  - [ ] CloudWatch dashboards configured
  - [ ] CloudWatch metrics tracking
  - [ ] Latency monitoring working
  - [ ] Error tracking working

- [ ] **Security Hardened**
  - [ ] API Gateway rate limiting configured
  - [ ] IAM least-privilege reviewed
  - [ ] Secrets management configured

- [ ] **Documentation Complete**
  - [ ] Deployment process documented
  - [ ] API endpoints documented
  - [ ] Demo script prepared

- [ ] **Demo-Ready**
  - [ ] Full eligibility flow works
  - [ ] All performance targets met
  - [ ] No critical bugs
  - [ ] System stable

---

## 🎯 Performance Validation Checklist

### API Latency (< 500ms p95)
- [ ] Measure API latency via CloudWatch
- [ ] Test with 10 concurrent users
- [ ] Validate p95 < 500ms
- [ ] Identify bottlenecks if latency > 500ms
**Owner**: Ayush

### Eligibility Evaluation (< 2 seconds)
- [ ] Measure rule engine execution time
- [ ] Test with 10 schemes
- [ ] Validate < 2 seconds
- [ ] Optimize if needed
**Owner**: Pranit

### LLM Response Time (< 2 seconds)
- [ ] Measure Bedrock API latency
- [ ] Test intent extraction
- [ ] Test explanation generation
- [ ] Optimize prompts if needed
**Owner**: Ratnadeep

### Session Management
- [ ] Validate session creation < 100ms
- [ ] Validate session TTL = 1 hour
- [ ] Test session expiration
- [ ] Monitor DynamoDB metrics
**Owner**: Ayush

### Data Freshness Visibility (100%)
- [ ] Validate last_verified_date in all schemes
- [ ] Test with multiple schemes
- [ ] Verify frontend display
- [ ] Document data sources
**Owner**: Ayush + Pranit

### LLM Guardrails (100%)
- [ ] Test 10 eligibility scenarios
- [ ] Validate LLM never returns eligibility decision
- [ ] Validate rule engine always makes decision
- [ ] Test edge cases
**Owner**: Ratnadeep

---

## 📞 Team Coordination

### Daily Standup (15 minutes)

**Time**: 9:00 AM  
**Format**: Async or Sync

**Questions**:
1. What did you complete yesterday?
2. What are you working on today?
3. Any blockers?

### Integration Checkpoints

**Day 3 Morning (11:00 AM)**:
- Ratnadeep: Bedrock API setup complete?
- Ayush: Session management complete?
- Pranit: Any rule engine bugs?

**Day 3 Afternoon (3:00 PM)**:
- Ratnadeep: LLM integration ready?
- Ayush: Conversation handler ready?
- All: Ready for integration testing?

**Day 3 Evening (6:00 PM)**:
- All: Integration testing results
- All: Critical bugs identified?
- All: Ready for Day 4 polish?

### Communication Channels

**Slack/Discord**:
- `#backend-dev`: General backend discussion
- `#integration`: Cross-team integration issues
- `#blockers`: Urgent blockers only

**GitHub**:
- Issues: Track all tasks
- PRs: Code review required
- Projects: Kanban board

---

## 🔥 Critical Path Analysis

### Longest Dependency Chain (Day 3)

```
Bedrock API Setup (2h)
    ↓
Intent Extraction (4h)
    ↓
LLM Orchestration (3h)
    ↓
Conversation Handler (4h)
    ↓
Rule Engine Integration (2h)
    ↓
Integration Testing (3h)
────────────────────────
Total: 18 hours
```

**Critical**: Ratnadeep's Bedrock setup blocks everything else.  
**Mitigation**: Start Bedrock setup first thing Day 3 morning.

### Parallel Work Opportunities

**While Ratnadeep sets up Bedrock (2h)**:
- Ayush: Implement session state management (3h)
- Pranit: Fix rule engine bugs (1.5h)
- Ayush: Upload schemes to S3 (0.5h)

**While Ratnadeep implements LLM (8h)**:
- Ayush: Implement conversation handler (7h)
- Pranit: Validate deterministic output (2h)

---

## 📚 Reference Documents

1. **EXECUTION_CHARTER.md**: 4-day execution plan, responsibility matrix
2. **PROJECT_ENGINEERING_RULEBOOK.md**: Coding standards, git workflow
3. **design.md**: System architecture, component design
4. **requirements.md**: Functional/non-functional requirements
5. **FRONTEND_INTEGRATION_PLAN.md**: Frontend API requirements
6. **ARCHITECTURE.md**: Backend architecture details

---

## 🎬 Demo Flow (Must Work End-to-End)

1. User opens PWA
2. User selects language (Hindi/English/Marathi)
3. User speaks or types: "I am a farmer, what schemes can I get?"
4. System asks: "What is your age?"
5. User responds: "35"
6. System asks: "What is your annual income?"
7. User responds: "2 lakh"
8. System evaluates eligibility
9. System shows results:
   - Eligible: PM-KISAN (explanation visible)
   - Partially Eligible: MUDRA Loan (missing: bank account)
   - Not Eligible: Old Age Pension (age < 60)
10. User sees last_verified_date for each scheme
11. User clicks PM-KISAN → redirected to official portal

**Demo Duration**: < 5 minutes  
**Demo Success Criteria**: Full eligibility flow works without errors

---

## ✅ Final Checklist (Day 4 EOD)

### System Readiness
- [ ] Full conversation flow working
- [ ] LLM service integrated into main backend
- [ ] S3 scheme loader working
- [ ] DynamoDB sessions working
- [ ] Rule engine integrated
- [ ] API latency < 500ms validated
- [ ] Eligibility evaluation < 100ms validated
- [ ] Session management working with TTL
- [ ] Data freshness visible
- [ ] Explanations present in all results
- [ ] 3 languages supported (en, hi, mr)
- [ ] LLM guardrails enforced

### Production Readiness
- [ ] CloudWatch dashboards configured
- [ ] CloudWatch metrics tracking
- [ ] API Gateway rate limiting configured
- [ ] IAM least-privilege reviewed
- [ ] Secrets management configured
- [ ] Deployment process documented
- [ ] Demo script prepared

### Demo Readiness
- [ ] Demo flow tested
- [ ] No critical bugs
- [ ] System stable
- [ ] All performance targets met
- [ ] 30+ tests passing

---

**Status**: Ready for Day 3 execution with significant time savings  
**Next Action**: Ayush integrates LLM service (Day 3 Morning, 9:00 AM)  
**Blocker**: None (LLM service is production-ready)  
**Time Saved**: 17 hours (47% reduction in Day 3 work)

---

## 🎉 Key Achievements

### What's Already Built
1. **Complete LLM Service** (standalone, production-ready)
   - Bedrock integration with guardrails
   - Intent extraction + explanation generation
   - Multilingual support (3 languages)
   - Fallback templates
   - Comprehensive tests

2. **Deterministic Eligibility Engine** (100% complete)
   - 8 operators supported
   - 17 passing unit tests
   - < 100ms performance
   - Full explanation traces

3. **API Layer** (85% complete)
   - FastAPI with OpenAPI 3.1
   - Lambda deployment ready
   - 8 API integration tests passing
   - Request validation and error handling

4. **Testing Infrastructure** (100% complete)
   - 30+ tests passing
   - Unit + integration + API tests
   - Performance benchmarks
   - Determinism validation

### What Needs Integration (Day 3)
1. Move LLM service to main backend (1 hour)
2. Integrate S3 scheme loader (2 hours)
3. Integrate DynamoDB sessions (1 hour)
4. Build conversation handler (7 hours)
5. End-to-end testing (2 hours)

**Total**: ~13 hours (vs original 36.5 hours)

---

*This roadmap reflects the actual current state. Update as tasks complete.*
