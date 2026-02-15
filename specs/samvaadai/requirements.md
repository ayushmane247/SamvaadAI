# Requirements Document: SamvaadAI

## Problem Statement

### The Access Gap in India

Millions of eligible Indian citizens do not benefit from government schemes due to:

- **Language barriers**: Official portals are primarily in English/Hindi
- **Low digital literacy**: Complex navigation and technical terminology
- **Information fragmentation**: 1000+ schemes across central and state governments
- **Complex eligibility criteria**: Citizens don't know what they qualify for
- **Search-driven design**: Users must know scheme names beforehand

**This is an access problem, not an availability problem.**

### Why Users Fail to Access Schemes Today

Real-world barriers observed in field research:
- Users abandon forms after 2-3 fields due to language/terminology confusion
- 70%+ rely on intermediaries (agents, CSC operators) who charge fees
- Eligibility criteria are written in legal language, not user language
- No way to know "am I eligible?" before investing time in application
- Voice is the only accessible input method for low-literacy users

### SamvaadAI's Approach

A **voice-first eligibility discovery platform** that:
- Asks adaptive questions to understand user profile
- Evaluates eligibility using deterministic rules
- Explains results in simple, local language
- Guides users to official portals for application

**Core Principle:** Deterministic decisions. AI for language only.

## Voice-First as an Accessibility Requirement

Voice interaction is not a convenience feature. **It is an inclusion requirement.**

Required because:
- Target users have low typing literacy
- Regional language keyboards are a barrier for non-English speakers
- Assisted operators can process beneficiaries faster with voice
- Reduces cognitive load for elderly and low-literacy users

System automatically degrades to text in low-bandwidth environments, ensuring accessibility across connectivity conditions.

## Goals

### Citizen Outcomes
- Discover schemes based on eligibility, not search
- Understand benefits and requirements in simple language
- Reduce time to identify applicable schemes from hours to minutes
- Receive actionable guidance for partial eligibility

### System Outcomes
- **Voice-first**: Primary input for low-literacy users and assisted operators
- **Explainable eligibility**: Every decision traceable to build trust in public systems
- **Local language**: Enables independent access without intermediaries
- Maintain data freshness and source traceability
- Support low-bandwidth environments (50 kbps)
- Scale from district to national deployment

### Trust & Explainability
- Every eligibility decision includes a clear explanation
- Users see "why" they are eligible or not
- Data freshness indicators visible to users
- Zero hallucination in eligibility logic

## AWS AI Service Utilization

### Amazon Bedrock
Used for:
- Intent extraction from user input
- Multilingual response generation (Hindi, English, Marathi)
- Explanation simplification
- Question rephrasing for clarity

**Model Selection Rationale:**
- Low latency for conversational flow (< 2s response time)
- Managed scaling (no infrastructure overhead)
- Secure VPC integration
- Support for Anthropic Claude models

### Why Bedrock Instead of External LLM APIs
- **Data sovereignty**: Keeps citizen interaction data within AWS boundary
- **Security**: Simplifies IAM-based access control
- **Compliance**: Improves deployment compliance for public-sector use cases
- **Cost**: Predictable pricing with AWS credits
- **Integration**: Native integration with Lambda, API Gateway, CloudWatch

### Amazon Polly ( Phase 2)
- Text-to-speech for voice output
- Support for Indian English and Hindi voices
- Low-latency streaming

## Scheme Data Trust & Verification Model

Each scheme includes:
- `source_url`: Link to official government portal
- `last_verified_date`: Timestamp of last manual verification
- `verification_method`: Manual or automated
- `ttl_days`: Configurable freshness threshold

**TTL-Based Freshness Policy:**
- Data older than configured TTL is flagged in UI
- Users see: "Last verified: [date]" for every scheme
- Only official government portals used as source of truth

**Eligibility Rules Derived From:**
- Official scheme guidelines (PDF/web)
- Publicly available documentation
- Government circulars and notifications

**Verification Process:**
1. Manual review of official scheme documents
2. Rule extraction and validation
3. JSON schema creation
4. Periodic re-verification (30-90 days)

This ensures users can trust the system's recommendations.

## Non-Goals (MVP Scope)

❌ **We do NOT:**
- Process or submit government applications
- Store sensitive personal data (Aadhaar, documents)
- Replace official government portals
- Provide legal, financial, or medical advice
- Guarantee real-time scheme accuracy
- Build mobile apps (PWA only for MVP)
- Implement community experience layer (Phase 2)
- Support offline mode (Phase 2)

## Target Users

### Primary: Low Digital Literacy Citizen
- **Profile**: Rural/semi-urban, limited English, basic smartphone
- **Needs**: Voice interaction, local language, simple explanations
- **Pain**: Cannot navigate complex government portals
- **Success**: Discovers 2-3 eligible schemes in under 5 minutes

### Secondary: Assisted Access Operator
- **Profile**: CSC operator, NGO worker, village volunteer
- **Needs**: Fast eligibility resolution for multiple beneficiaries
- **Pain**: Manual scheme matching is time-consuming
- **Success**: Helps 10+ citizens per day efficiently

## User Journeys

### Journey 1: Scheme Discovery (Primary Flow)

1. User opens PWA, selects language (Hindi/English/Marathi)
2. User speaks or types: "I am a farmer, what schemes can I get?"
3. System asks adaptive questions:
   - "What is your age?"
   - "What is your annual income?"
   - "Which state do you live in?"
4. System evaluates eligibility using rule engine
5. System presents results:
   - **Eligible**: PM-KISAN (₹6000/year for farmers)
   - **Partially Eligible**: MUDRA Loan (need bank account)
   - **Not Eligible**: Old Age Pension (age < 60)
6. User selects PM-KISAN
7. System shows:
   - Benefit summary
   - Document checklist
   - Official portal link
8. User clicks link → redirected to official portal

### Journey 2: Eligibility Explanation

1. User receives "Not Eligible" for a scheme
2. System explains: "You are not eligible because your age is below 60 years"
3. User asks: "What do I need to become eligible?"
4. System responds: "This scheme requires age 60+. You can apply after [date]"
5. User saves result for future reference

### Journey 3: Partial Eligibility Guidance

1. User is "Partially Eligible" for MUDRA Loan
2. System shows: "You need: Bank account"
3. System provides: "Visit any nationalized bank with Aadhaar and PAN"
4. User returns after opening account
5. System re-evaluates → now "Eligible"

## Functional Requirements

### FR-1: Voice and Text Input (P0)
- Accept voice input using Web Speech API
- Accept text input as fallback
- Support Hindi, English, Marathi (MVP)
- Convert voice to text within 2 seconds
- Auto-switch to text mode if voice fails

### FR-2: Adaptive Questioning (P0)
- Ask minimum questions to determine eligibility
- Select next question based on previous answers
- Allow users to skip questions
- Rephrase unclear questions using LLM
- Maintain conversation context in session

### FR-3: Deterministic Eligibility Evaluation (P0)
- Apply rule-based logic (NO LLM involvement)
- Evaluate against 5-10 schemes (Maharashtra, MVP)
- Return: eligible / partially eligible / not eligible
- Complete evaluation in < 2 seconds
- Rank eligible schemes by relevance

### FR-4: Explainable Results (P0)
- Provide clear explanation for every eligibility decision
- Show which attributes contributed to decision
- Explain missing criteria for partial eligibility
- Use simple language (no jargon)
- Present in user's selected language

### FR-5: Scheme Information Display (P0)
- Show benefit summary in simple language
- Display eligibility criteria
- Provide document checklist
- Include official portal link
- Show data last verified date

### FR-6: Session Management (P0)
- Create anonymous session on start
- Store session state in DynamoDB (TTL: 1 hour)
- Resume session if user returns
- Delete all user data after session expires
- No permanent storage of PII

### FR-7: LLM Integration with Guardrails (P0)
- Use LLM ONLY for:
  - Intent detection
  - Multilingual response generation
  - Question rephrasing
  - Explanation simplification
- LLM NEVER used for:
  - Eligibility decisions
  - Rule evaluation
  - Scheme data generation
- Validate LLM outputs against safety guidelines
- Fallback to templates if LLM fails

### FR-8: Low-Bandwidth Optimization (P1)
- Function on 50 kbps connections
- Compress responses
- Cache scheme data locally
- Prioritize text over voice on slow connections
- Show connection quality indicator

### FR-9: Analytics (Privacy-Preserving) (P1)
- Track anonymized usage metrics
- Measure: schemes discovered, completion rate, drop-off
- No storage of PII beyond session
- Generate aggregated reports
- Export to CloudWatch/S3

### FR-10: Scheme Data Management (P1)
- Store schemes in S3 (JSON format)
- Support versioning and rollback
- Validate eligibility rules before activation
- Update data freshness timestamp
- Support bulk import/export

### FR-11: Official Portal Integration (P1)
- Provide direct links to official portals
- Track redirect rates
- Show fallback instructions if link unavailable
- Clearly indicate application happens externally

### FR-12: Error Handling (P1)
- Auto-switch to text if voice fails
- Request missing data if eligibility cannot be determined
- Preserve session state on network loss
- Show user-friendly error messages in local language
- Log errors for monitoring

### FR-13: Multi-User Support (Assisted Access) (P2)
- Support multiple concurrent sessions
- Maintain separate contexts per beneficiary
- Allow operators to print checklists
- Track assisted vs. direct usage separately

### FR-14: State/Regional Variation (P2)
- Filter schemes by state
- Apply state-specific eligibility rules
- Indicate regional availability
- Support modular expansion to new states

## Non-Functional Requirements

### NFR-1: Performance
- API response time: < 500ms (p95)
- Eligibility evaluation: < 2 seconds
- Voice-to-text latency: < 2 seconds
- Support 100 concurrent users (MVP)
- Scale to 1000+ concurrent users (AWS Lambda auto-scaling)

### NFR-2: Low-Bandwidth Support
- Function on 50 kbps connections
- Compressed JSON responses (< 10 KB)
- Progressive enhancement (text → voice)
- Cached question flows
- Minimal round trips

### NFR-3: Multilingual Capability
- Support 3 languages (MVP): Hindi, English, Marathi
- LLM-powered translation for responses
- Language switching mid-session
- Consistent terminology across languages

### NFR-4: Privacy by Design
- No PII storage beyond session (1 hour TTL)
- Anonymous session IDs
- Aggregated analytics only
- Explicit consent for any data retention
- GDPR/data minimization principles

### NFR-5: Explainability
- Every eligibility decision includes explanation
- Traceable decision path
- No black-box AI in eligibility logic
- Users can see "why" for every outcome

### NFR-6: Scalability (AWS Serverless)
- Stateless Lambda functions
- DynamoDB for sessions (auto-scaling)
- S3 for scheme data (versioned)
- API Gateway for routing
- CloudWatch for monitoring

### NFR-7: Reliability
- 99% uptime (AWS SLA)
- Graceful degradation (voice → text)
- Session state preservation on network loss
- Fallback templates if LLM fails
- Error logging and monitoring

### NFR-8: Security
- TLS for all API calls
- API Gateway rate limiting
- Input validation and sanitization
- No storage of sensitive documents
- Role-based access for scheme updates (future)

## AI Justification (Critical for Judging)

### Why AI is Required

**Problem:** Citizens speak in natural, unstructured language
- "I am a farmer with 2 acres, what can I get?" (English)
- "मुझे कौन सी योजना मिल सकती है?" (Hindi)
- ""मी २ एकर जमीन असलेला शेतकरी आहे, मला काय मिळेल?"" (Marathi)

**Without AI:**
- Users must fill rigid forms
- No natural language understanding
- No multilingual support
- No conversational guidance

**With AI (Amazon Bedrock):**
- Understands intent from natural speech
- Extracts structured attributes (age, occupation, income)
- Generates simple explanations in local languages
- Rephrases questions for clarity
- Maintains data sovereignty within AWS

### What Fails Without AI

1. **Intent Understanding**: Cannot parse "I am a farmer" → occupation = "farmer"
2. **Multilingual Interaction**: Cannot translate responses to Hindi/Marathi
3. **Explanation Generation**: Cannot simplify "income threshold < ₹2.5L" → "your income is below the limit"
4. **Conversational Flow**: Cannot rephrase unclear questions

### Why Deterministic Logic is Still Needed

**Eligibility decisions MUST be rule-based because:**

1. **Auditability**: Government decisions must be traceable
2. **Consistency**: Same input must always produce same output
3. **Trust**: Citizens need to trust the system
4. **Zero Hallucination**: LLMs can hallucinate eligibility criteria
5. **Legal Compliance**: Eligibility is a legal determination

**Example:**
```
User: "I am 25 years old"
LLM (wrong): "You might be eligible for old age pension"
Rule Engine (correct): "Not eligible - age requirement is 60+"
```

### Hybrid Architecture

```
User Input (natural language)
        ↓
Amazon Bedrock (intent extraction)
        ↓
Structured Profile {age: 25, occupation: "farmer"}
        ↓
Rule Engine (deterministic evaluation)
        ↓
Eligibility Result {eligible: ["PM-KISAN"], not_eligible: ["Pension"]}
        ↓
Amazon Bedrock (explanation generation)
        ↓
User Output (simple language)
```

**AI for language. Rules for decisions.**

## Success Metrics

### Product Metrics (User Impact)
- **Schemes discovered per session**: Target 2-3
- **Time to eligibility resolution**: Target < 5 minutes
- **Completion rate**: Target 70%+
- **Official portal redirects**: Target 40%+
- **User satisfaction**: Target 4/5 stars

### Technical Metrics (System Performance)
- **API latency (p95)**: < 500ms
- **Eligibility evaluation time**: < 2 seconds
- **Voice-to-text latency**: < 2 seconds
- **Concurrent users supported**: 100+ (MVP)
- **Uptime**: 99%+

### Trust Metrics (Explainability)
- **Results with explanation**: 100%
- **Data freshness visibility**: 100%
- **Eligibility accuracy**: 95%+ (validated against official criteria)
- **LLM guardrail compliance**: 100% (no eligibility decisions by LLM)

## Impact Measurement Model

### Time Saved Calculation

Time saved per session is estimated as:

```
time_saved = baseline_manual_time - system_completion_time
```

Where:
- **baseline_manual_time**: Average time to manually discover schemes
  - Estimated: 2-4 hours (based on user research)
  - Includes: portal navigation, scheme reading, eligibility checking
- **system_completion_time**: Actual session duration in SamvaadAI
  - Target: < 5 minutes

**Example:**
- Manual discovery: 3 hours
- SamvaadAI session: 4 minutes
- Time saved: 2 hours 56 minutes per user

### Aggregated Impact Metrics

Stored in anonymized form:
- Total sessions completed
- Average time saved per session
- Total schemes discovered
- Portal redirect rate (conversion to application)

**Projected Impact (1000 users/month):**
- Time saved: ~3000 hours/month
- Schemes discovered: ~2500 schemes/month
- Applications initiated: ~1000/month (40% conversion)

This quantifies the platform's value for stakeholders and funders.

## Risks & Assumptions

### Risks

1. **Scheme data becomes outdated**
   - Mitigation: TTL-based freshness tracking, manual verification

2. **LLM generates incorrect information**
   - Mitigation: Strict guardrails, template fallbacks, validation

3. **Low adoption due to trust concerns**
   - Mitigation: Explainability, data freshness indicators, official portal links

4. **Voice recognition fails in noisy environments**
   - Mitigation: Auto-fallback to text mode

5. **State-specific eligibility variations**
   - Mitigation: Modular rule sets, start with single state (Maharashtra)

### Assumptions

1. Users have access to basic smartphone or assisted access point
2. Official scheme information is publicly available
3. Initial deployment targets Maharashtra (5-10 schemes)
4. Users trust system if explanations are clear
5. AWS services are available and reliable
6. LLM API (OpenAI/Anthropic) is accessible

## Initial Deployment Context

### Target Deployment Partners

**Primary:**
- **Common Service Centers (CSC)**: 4+ lakh centers across India
- **NGOs**: Organizations working in rural skilling and financial inclusion

**Why These Partners:**
- Assisted access model reduces trust barrier for first-time users
- High daily beneficiary throughput (10-50 citizens/day per center)
- No need for individual user acquisition in early stage
- Existing infrastructure and trained operators
- Government-backed credibility

### Pilot Deployment (MVP)

**Geography:** Maharashtra (1-2 districts)  
**Duration:** 3 months  
**Target:** 500-1000 users  
**Schemes:** 5-10 state and central schemes  

**Success Criteria:**
- 70%+ completion rate
- 40%+ portal redirect rate
- 4/5 user satisfaction
- < 5 min average session time

## MVP Scope (Hackathon)

### Live Demo Scope

**Demo will include:**
- Maharashtra state (single geography)
- 5-7 schemes (PM-KISAN, MUDRA, Pension, etc.)
- 1 complete eligibility flow (farmer persona)
- Multilingual voice interaction (Hindi/English/Marathi)
- Explainable result screen with data freshness indicator

**NOT being built for hackathon:**
- Multi-state support
- Authentication/user profiles
- Admin portal for scheme management
- Offline mode
- Mobile apps (PWA only)

### In Scope
✅ React PWA (text + voice input)  
✅ FastAPI backend on AWS Lambda  
✅ Deterministic eligibility engine  
✅ 5-10 schemes (Maharashtra)  
✅ 3 languages (Hindi, English, Marathi)  
✅ Amazon Bedrock integration (Anthropic Claude)  
✅ Session management (DynamoDB)  
✅ Scheme data storage (S3)  
✅ Basic analytics (CloudWatch)  
✅ Explainable results  
✅ Data trust & verification model  

### Out of Scope (Phase 2)
❌ Mobile apps (iOS/Android)  
❌ Offline mode  
❌ Community experience layer  
❌ Authentication & user profiles  
❌ Admin portal  
❌ Multi-state support  
❌ Advanced analytics dashboard  
❌ Document upload  

## Technology Stack

### Frontend
- React (Vite)
- Tailwind CSS
- Web Speech API
- Deployed on AWS Amplify

### Backend
- FastAPI (Python)
- Pydantic (validation)
- Mangum (Lambda adapter)
- Deployed on AWS Lambda

### Data
- DynamoDB (sessions, TTL: 1 hour)
- S3 (scheme datasets, versioned)

### AI
- **Amazon Bedrock** (Anthropic Claude)
  - Intent extraction
  - Multilingual response generation
  - Used ONLY for NLU/NLG, NOT eligibility
- **Amazon Polly** (Phase 2)
  - Text-to-speech for voice output

### Infrastructure
- AWS API Gateway
- AWS Lambda (auto-scaling)
- AWS CloudWatch (monitoring)
- AWS Amplify (frontend hosting)

## Glossary

- **Session**: Single user interaction (1 hour TTL)
- **Scheme**: Government program or opportunity
- **Rule Engine**: Deterministic eligibility evaluator
- **LLM**: Large Language Model (for language only)
- **CSC**: Common Service Center (assisted access point)
- **TTL**: Time-to-live (data expiration)
- **PII**: Personally Identifiable Information
- **NFR**: Non-Functional Requirement
- **FR**: Functional Requirement
