# SamvaadAI: 4-Day Hackathon Execution Charter

## 1. Project Execution Charter

### Execution Philosophy

**Deterministic-first principle**: AI for language only. Rule engine for eligibility. No LLM in decision logic.

**Integration by Day 3 mandate**: All modules must integrate end-to-end by EOD Day 3. Day 4 is polish only.

**Zero scope expansion**: requirements.md and design.md are immutable architectural truth. No new features. No architecture changes.

### Architectural Constraints (Non-Negotiable)

From design.md:
- AI for language only
- Deterministic rule engine for eligibility
- No LLM in decision logic
- Stateless Lambda architecture
- DynamoDB session TTL = 1 hour
- S3 versioned scheme datasets
- last_verified_date visible in results

From requirements.md:
- API latency < 500ms (p95)
- Eligibility evaluation < 2 seconds
- Voice-to-text < 2 seconds
- Works on 50kbps
- No permanent PII storage
- 3 languages (Hindi, English, Marathi)
- 5-10 Maharashtra schemes only
- PWA only (no mobile app)

## 2. Responsibility Matrix

### Ratnadeep – Conversation + Amazon Bedrock Lead

**OWNS:**
- Intent extraction from user input
- Multilingual response generation (Hindi, English, Marathi)
- Explanation simplification
- Question rephrasing for clarity
- LLM prompt engineering
- Bedrock API integration
- LLM latency optimization

**DOES NOT OWN:**
- Eligibility decision logic
- Rule evaluation
- Scheme data structure
- API schema definition
- Session management
- Frontend integration

**API RESPONSIBILITIES:**
- Consumes: User input text from conversation handler
- Produces: Structured attributes (JSON) for rule engine
- Produces: Simplified explanations in target language

**DATA RESPONSIBILITIES:**
- No data storage
- No scheme data modification
- Stateless LLM calls only

**LATENCY RESPONSIBILITY:**
- LLM response time < 2 seconds
- Intent extraction < 500ms

**DEFINITION OF DONE:**
- Intent extraction returns structured JSON: `{age: int, occupation: str, income_band: str, location: {state: str}}`
- Explanation generation converts rule engine output to simple language
- Supports 3 languages (Hindi, English, Marathi)
- LLM never returns eligibility decisions
- Fallback to templates if LLM fails

---

### Pranit – Deterministic Rule Engine Lead

**OWNS:**
- Eligibility evaluation logic (pure Python)
- Rule definition schema
- Scheme criteria validation
- Deterministic output guarantee
- Explanation trace generation
- Rule engine performance

**DOES NOT OWN:**
- LLM integration
- User input parsing
- API routing
- Session state
- Frontend display logic
- Scheme data collection

**API RESPONSIBILITIES:**
- Consumes: Structured user profile (JSON) from conversation handler
- Produces: Eligibility result with explanation trace
- Produces: Partial eligibility guidance

**DATA RESPONSIBILITIES:**
- Reads scheme rules from S3
- No data modification
- No session state management

**LATENCY RESPONSIBILITY:**
- Eligibility evaluation < 2 seconds
- Rule validation < 100ms

**DEFINITION OF DONE:**
- Rule engine evaluates 5-10 schemes in < 2 seconds
- Same input produces same output (deterministic)
- Every result includes explanation trace
- Supports operators: equals, less_than, greater_than, between, in, not_in
- Outputs: eligible / partially_eligible / ineligible with reasons
- Zero LLM involvement in evaluation

---

### Pushkar – Frontend & Voice (React PWA) Lead

**OWNS:**
- React PWA implementation
- Voice input (Web Speech API)
- Text input fallback
- Language selection UI
- Result display with explanations
- Data freshness indicator display
- Low-bandwidth mode
- Frontend performance

**DOES NOT OWN:**
- API schema definition
- Backend logic
- Eligibility evaluation
- LLM integration
- Session management logic
- Scheme data structure

**API RESPONSIBILITIES:**
- Consumes: API schema defined by backend
- Calls: POST /session/start, POST /conversation/input, GET /conversation/results
- No assumptions about backend logic

**DATA RESPONSIBILITIES:**
- Local caching of question flows
- No PII storage beyond session
- Displays last_verified_date from API

**LATENCY RESPONSIBILITY:**
- Voice-to-text < 2 seconds
- UI render < 100ms
- Works on 50kbps

**DEFINITION OF DONE:**
- PWA supports voice and text input
- 3 languages (Hindi, English, Marathi) selectable
- Displays eligibility results with explanations
- Shows last_verified_date for every scheme
- Auto-fallback to text if voice fails
- Lighthouse score > 80
- Works on 50kbps (tested)

---

### Ayush – AWS + FastAPI Backend + Infrastructure Lead

**OWNS:**
- API schema definition
- FastAPI implementation
- Session management (DynamoDB)
- Conversation handler logic
- API Gateway configuration
- Lambda deployment
- S3 scheme data storage
- CloudWatch monitoring
- End-to-end API latency

**DOES NOT OWN:**
- LLM prompt engineering
- Rule engine logic
- Frontend implementation
- Voice API integration

**API RESPONSIBILITIES:**
- Defines: API contract (OpenAPI spec)
- Implements: POST /session/start, POST /conversation/input, GET /conversation/results
- Orchestrates: LLM → Rule Engine → Response flow
- Guarantees: API latency < 500ms (p95)

**DATA RESPONSIBILITIES:**
- DynamoDB session management (TTL: 1 hour)
- S3 scheme data versioning
- No permanent PII storage
- CloudWatch analytics

**LATENCY RESPONSIBILITY:**
- API response time < 500ms (p95)
- Session creation < 100ms
- End-to-end flow < 3 seconds

**DEFINITION OF DONE:**
- FastAPI deployed on Lambda
- API Gateway configured with rate limiting
- DynamoDB session store with 1-hour TTL
- S3 scheme data with versioning enabled
- CloudWatch logs and metrics enabled
- API latency < 500ms (p95) validated
- OpenAPI spec published for frontend
- 5-10 Maharashtra schemes loaded in S3

## 3. 4-Day Execution Plan

### Day 1: API Contract Freeze + Module Skeletons

**Ayush (Backend + Infrastructure)**
- Tasks:
  - Define OpenAPI spec (POST /session/start, POST /conversation/input, GET /conversation/results)
  - Create FastAPI skeleton with Pydantic models
  - Deploy Lambda + API Gateway (hello world)
  - Configure DynamoDB table (session_id PK, TTL: 3600)
  - Create S3 bucket with versioning enabled
  - Set up CloudWatch logging
- Expected Output:
  - OpenAPI spec published (shared with Pushkar)
  - Lambda deployed and accessible via API Gateway URL
  - DynamoDB table created
  - S3 bucket created
- Dependencies: None
- Integration Checkpoint: API Gateway returns 200 OK
- Risk Flags: Lambda cold start latency, IAM permissions

**Pranit (Rule Engine)**
- Tasks:
  - Define rule schema (JSON format)
  - Implement rule evaluator (pure Python)
  - Create 5 sample schemes with rules (Maharashtra)
  - Write unit tests for rule evaluation
  - Validate deterministic output
- Expected Output:
  - Rule engine Python module (eligibility_engine.py)
  - 5 scheme JSON files with rules
  - Unit tests passing (same input → same output)
- Dependencies: None
- Integration Checkpoint: Rule engine callable as Python function
- Risk Flags: Rule complexity, operator edge cases

**Ratnadeep (LLM + Bedrock)**
- Tasks:
  - Set up Bedrock API access (Anthropic Claude)
  - Implement intent extraction (user input → structured JSON)
  - Implement explanation generation (rule output → simple language)
  - Create prompt templates for 3 languages (Hindi, English, Marathi)
  - Test LLM latency
- Expected Output:
  - Bedrock integration module (llm_service.py)
  - Intent extraction function
  - Explanation generation function
  - Prompt templates (Hindi, English, Marathi)
- Dependencies: None
- Integration Checkpoint: LLM returns structured JSON for sample inputs
- Risk Flags: Bedrock latency spikes, prompt engineering quality

**Pushkar (Frontend)**
- Tasks:
  - Create React PWA skeleton (Vite + Tailwind)
  - Implement language selection UI
  - Implement text input form
  - Implement Web Speech API integration
  - Create result display component (placeholder data)
- Expected Output:
  - React PWA running locally
  - Language selection working
  - Text input working
  - Voice input working (browser permission)
  - Result display component (mock data)
- Dependencies: OpenAPI spec from Ayush (EOD Day 1)
- Integration Checkpoint: PWA accessible in browser
- Risk Flags: Web Speech API browser compatibility

**EOD Day 1 Checkpoint:**
- API contract frozen (OpenAPI spec)
- All modules have working skeletons
- No integration yet (expected)

---

### Day 2: Independent Module Completion

**Ayush (Backend + Infrastructure)**
- Tasks:
  - Implement POST /session/start (create DynamoDB session)
  - Implement POST /conversation/input (orchestrate LLM + Rule Engine)
  - Implement GET /conversation/results (return eligibility results)
  - Load 5-10 Maharashtra schemes into S3
  - Integrate Pranit's rule engine module
  - Integrate Ratnadeep's LLM module
  - Test end-to-end flow (mock frontend requests)
- Expected Output:
  - All 3 API endpoints functional
  - Session management working (DynamoDB TTL verified)
  - Scheme data in S3
  - End-to-end flow: input → LLM → rule engine → response
- Dependencies: Pranit's rule engine, Ratnadeep's LLM module
- Integration Checkpoint: Postman test returns eligibility result
- Risk Flags: Module integration bugs, Lambda timeout

**Pranit (Rule Engine)**
- Tasks:
  - Complete rule engine implementation (all operators)
  - Add explanation trace generation
  - Implement partial eligibility logic
  - Create 10 Maharashtra schemes with rules
  - Validate rule engine performance (< 2 seconds)
  - Package as importable Python module
- Expected Output:
  - Rule engine module ready for integration
  - 10 scheme JSON files
  - Performance validated (< 2 seconds for 10 schemes)
  - Explanation trace included in output
- Dependencies: None
- Integration Checkpoint: Ayush can import and call rule engine
- Risk Flags: Rule complexity causing latency

**Ratnadeep (LLM + Bedrock)**
- Tasks:
  - Refine intent extraction prompts
  - Refine explanation generation prompts
  - Implement multilingual support (Hindi, English, Marathi)
  - Add fallback templates if LLM fails
  - Optimize LLM latency (< 2 seconds)
  - Package as importable Python module
- Expected Output:
  - LLM module ready for integration
  - 3 languages supported
  - Fallback templates implemented
  - Latency < 2 seconds validated
- Dependencies: None
- Integration Checkpoint: Ayush can import and call LLM module
- Risk Flags: LLM hallucination, latency spikes

**Pushkar (Frontend)**
- Tasks:
  - Integrate with backend API (use OpenAPI spec)
  - Implement session creation flow
  - Implement conversation input flow
  - Implement result display with explanations
  - Display last_verified_date for schemes
  - Implement low-bandwidth mode (text-only fallback)
  - Test voice input on multiple browsers
- Expected Output:
  - Frontend connected to backend API
  - Full conversation flow working (text input)
  - Voice input working (Chrome, Edge)
  - Result display with explanations
  - last_verified_date visible
- Dependencies: Backend API endpoints (Ayush)
- Integration Checkpoint: Frontend can create session and get results
- Risk Flags: API integration bugs, CORS issues

**EOD Day 2 Checkpoint:**
- All modules independently functional
- Backend API returns eligibility results
- Frontend displays results (may have bugs)

---

### Day 3: Full End-to-End Integration

**Ayush (Backend + Infrastructure)**
- Tasks:
  - Fix integration bugs from Day 2
  - Validate API latency < 500ms (p95) using CloudWatch
  - Validate session TTL (1 hour)
  - Test with 10 concurrent users
  - Deploy to production Lambda
  - Configure API Gateway rate limiting
  - Document API endpoints
- Expected Output:
  - API latency < 500ms (p95) validated
  - Session TTL working
  - Production deployment complete
  - API documentation published
- Dependencies: Bug reports from Pushkar, Pranit, Ratnadeep
- Integration Checkpoint: End-to-end flow works without errors
- Risk Flags: Latency spikes, DynamoDB throttling

**Pranit (Rule Engine)**
- Tasks:
  - Fix rule engine bugs from integration testing
  - Validate deterministic output (same input → same output)
  - Validate eligibility evaluation < 2 seconds
  - Add logging for debugging
  - Test edge cases (missing fields, invalid input)
- Expected Output:
  - Rule engine bug-free
  - Deterministic output validated
  - Latency < 2 seconds validated
  - Edge cases handled
- Dependencies: Bug reports from Ayush
- Integration Checkpoint: Rule engine produces correct results for all test cases
- Risk Flags: Edge case bugs

**Ratnadeep (LLM + Bedrock)**
- Tasks:
  - Fix LLM integration bugs from Day 2
  - Validate LLM never returns eligibility decisions
  - Validate explanation quality (simple language)
  - Test multilingual support (Hindi, English, Marathi)
  - Optimize prompts for latency
  - Add LLM guardrails (no eligibility decisions)
- Expected Output:
  - LLM bug-free
  - Explanation quality validated
  - 3 languages working
  - LLM guardrails enforced
- Dependencies: Bug reports from Ayush
- Integration Checkpoint: LLM produces correct explanations in all 3 languages
- Risk Flags: LLM hallucination, prompt quality

**Pushkar (Frontend)**
- Tasks:
  - Fix frontend bugs from Day 2
  - Test voice input on multiple devices
  - Validate voice-to-text < 2 seconds
  - Test low-bandwidth mode (50kbps simulation)
  - Run Lighthouse audit (target > 80)
  - Test on mobile browsers
  - Polish UI/UX
- Expected Output:
  - Frontend bug-free
  - Voice input working on all browsers
  - Low-bandwidth mode working
  - Lighthouse score > 80
  - Mobile-friendly
- Dependencies: Backend API stability (Ayush)
- Integration Checkpoint: Full eligibility flow works end-to-end
- Risk Flags: Voice API browser compatibility, low-bandwidth issues

**EOD Day 3 Checkpoint:**
- Full end-to-end eligibility loop working
- Voice input → LLM → rule engine → result display
- All performance targets met
- No critical bugs

---

### Day 4: Polish Only (No Core Feature Development)

**Ayush (Backend + Infrastructure)**
- Tasks:
  - Monitor CloudWatch metrics
  - Fix minor bugs
  - Optimize API latency if needed
  - Prepare demo script
  - Document deployment process
- Expected Output:
  - API stable and monitored
  - Demo script ready
  - Deployment documented
- Dependencies: None
- Integration Checkpoint: API ready for demo
- Risk Flags: Last-minute bugs

**Pranit (Rule Engine)**
- Tasks:
  - Fix minor bugs
  - Add more schemes if time permits (stay within 10)
  - Validate explanation quality
  - Prepare demo scenarios
- Expected Output:
  - Rule engine stable
  - Demo scenarios ready
- Dependencies: None
- Integration Checkpoint: Rule engine ready for demo
- Risk Flags: Last-minute bugs

**Ratnadeep (LLM + Bedrock)**
- Tasks:
  - Fix minor bugs
  - Refine prompts for demo
  - Test edge cases
  - Prepare demo script
- Expected Output:
  - LLM stable
  - Demo script ready
- Dependencies: None
- Integration Checkpoint: LLM ready for demo
- Risk Flags: Last-minute bugs

**Pushkar (Frontend)**
- Tasks:
  - Fix minor UI bugs
  - Polish UI/UX
  - Test demo flow
  - Prepare demo script
  - Deploy to production (Amplify)
- Expected Output:
  - Frontend polished
  - Demo script ready
  - Production deployment complete
- Dependencies: None
- Integration Checkpoint: Frontend ready for demo
- Risk Flags: Last-minute bugs

**EOD Day 4 Checkpoint:**
- System demo-ready
- All performance targets met
- Demo script prepared

## 4. Integration Timeline

### Day 1 EOD
- **FastAPI skeleton deployed**: Lambda + API Gateway accessible
- **OpenAPI spec published**: Shared with frontend
- **Rule engine callable**: Python function ready
- **LLM module callable**: Python function ready
- **Frontend skeleton running**: PWA accessible in browser

### Day 2 EOD
- **Backend integrated**: LLM + Rule Engine working together
- **Frontend connected**: API calls working
- **End-to-end flow**: Input → LLM → Rule Engine → Response (may have bugs)

### Day 3 EOD
- **Full integration**: Voice input → LLM → Rule Engine → Result display
- **Performance validated**: All latency targets met
- **Bug-free**: No critical bugs

### Day 4 EOD
- **Demo-ready**: System polished and stable

## 5. Risk Mitigation Plan

### Risk 1: Bedrock Latency Spikes
**Impact**: LLM response time > 2 seconds  
**Mitigation**:
- Use Anthropic Claude (fast model)
- Implement timeout (3 seconds)
- Fallback to templates if LLM fails
- Cache common responses
**Owner**: Ratnadeep

### Risk 2: Rule Engine Complexity Bugs
**Impact**: Incorrect eligibility results  
**Mitigation**:
- Write unit tests for all operators
- Validate deterministic output
- Test edge cases (missing fields, invalid input)
- Add logging for debugging
**Owner**: Pranit

### Risk 3: API Schema Mismatch
**Impact**: Frontend-backend integration failure  
**Mitigation**:
- Freeze API contract on Day 1
- Use OpenAPI spec for contract
- Backend publishes spec, frontend consumes
- No assumptions by frontend
**Owner**: Ayush

### Risk 4: DynamoDB TTL Misconfiguration
**Impact**: Sessions not expiring, PII stored permanently  
**Mitigation**:
- Set TTL attribute on table creation
- Validate TTL working on Day 2
- Test session expiration (1 hour)
- Monitor DynamoDB metrics
**Owner**: Ayush

### Risk 5: Voice API Browser Compatibility
**Impact**: Voice input not working on some browsers  
**Mitigation**:
- Test on Chrome, Edge, Safari, Firefox
- Auto-fallback to text if voice fails
- Show clear error message
- Document browser requirements
**Owner**: Pushkar

### Risk 6: Scheme Data Inconsistencies
**Impact**: Incorrect eligibility rules  
**Mitigation**:
- Validate scheme JSON schema
- Manual review of rules
- Test with known examples
- Document data sources
**Owner**: Pranit

### Risk 7: Lambda Cold Start Latency
**Impact**: API latency > 500ms  
**Mitigation**:
- Use provisioned concurrency (if needed)
- Optimize Lambda package size
- Monitor CloudWatch metrics
- Test with concurrent users
**Owner**: Ayush

### Risk 8: LLM Hallucination in Eligibility
**Impact**: LLM returns incorrect eligibility decisions  
**Mitigation**:
- Strict guardrails: LLM never evaluates eligibility
- Validate LLM output format
- Fallback to templates if LLM fails
- Test with edge cases
**Owner**: Ratnadeep

### Risk 9: Low-Bandwidth Mode Failure
**Impact**: System unusable on 50kbps  
**Mitigation**:
- Compress JSON responses (< 10 KB)
- Auto-fallback to text mode
- Cache question flows locally
- Test with network throttling
**Owner**: Pushkar

### Risk 10: Integration Delays
**Impact**: Day 3 integration fails  
**Mitigation**:
- Freeze API contract on Day 1
- Daily integration checkpoints
- No scope expansion
- Focus on MVP only
**Owner**: All

## 6. Performance Validation Checklist

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

### Voice-to-Text (< 2 seconds)
- [ ] Measure Web Speech API latency
- [ ] Test on multiple browsers
- [ ] Validate < 2 seconds
- [ ] Document browser requirements
**Owner**: Pushkar

### Low-Bandwidth (50kbps)
- [ ] Simulate 50kbps using Chrome DevTools
- [ ] Test full eligibility flow
- [ ] Validate text-only fallback works
- [ ] Measure response size (< 10 KB)
**Owner**: Pushkar

### Lighthouse Audit
- [ ] Run Lighthouse on PWA
- [ ] Validate score > 80
- [ ] Fix performance issues
- [ ] Document results
**Owner**: Pushkar

### Explanation Presence (100%)
- [ ] Test 10 eligibility scenarios
- [ ] Validate explanation present in all results
- [ ] Validate explanation quality (simple language)
- [ ] Test in all 3 languages
**Owner**: Ratnadeep

### LLM Guardrails (100%)
- [ ] Test 10 eligibility scenarios
- [ ] Validate LLM never returns eligibility decision
- [ ] Validate rule engine always makes decision
- [ ] Test edge cases
**Owner**: Ratnadeep

### Data Freshness Visibility (100%)
- [ ] Validate last_verified_date present in all scheme results
- [ ] Validate date displayed in frontend
- [ ] Test with multiple schemes
- [ ] Document data sources
**Owner**: Ayush + Pushkar

## 7. Definition of Hackathon-Ready System

### Deterministic Output
- Same user input produces same eligibility result
- Rule engine is LLM-independent
- Explanation trace included in all results

### 5 Schemes Functional
- 5-10 Maharashtra schemes loaded in S3
- All schemes have valid eligibility rules
- All schemes tested with sample inputs

### Multilingual Flow Working
- 3 languages supported (Hindi, English, Marathi)
- Language selection working in frontend
- LLM generates responses in selected language

### Explanation Visible
- Every eligibility result includes explanation
- Explanation in simple language (no jargon)
- Explanation visible in frontend

### Data Freshness Visible
- last_verified_date present in all scheme results
- Date displayed in frontend result screen
- Users can see when data was last verified

### No Architecture Violations
- LLM never makes eligibility decisions
- Rule engine is deterministic
- Session TTL = 1 hour (no permanent PII storage)
- API latency < 500ms (p95)
- Eligibility evaluation < 2 seconds
- Voice-to-text < 2 seconds
- Works on 50kbps

### Demo Flow
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

**Demo duration**: < 5 minutes  
**Demo success criteria**: Full eligibility flow works without errors
