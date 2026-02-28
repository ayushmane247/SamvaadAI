# Technical Design Document: SamvaadAI

## 1. System Intent

SamvaadAI is a **voice-first eligibility discovery platform** for government schemes.

**Hackathon implementation scope:**  
Maharashtra → 5-7 schemes → full eligibility journey (voice input → rule evaluation → explainable result)

**Core architectural principle:**  
**Deterministic decisions. AI for language only.**

This guarantees:
- ✅ Auditability
- ✅ Repeatable outputs
- ✅ Zero hallucination in eligibility
- ✅ Suitability for public service delivery

## 2. Architectural Style

**Serverless, stateless, explainable core**

Design goals:
- Fast hackathon deployment
- Low operational overhead
- Horizontal scalability
- Low bandwidth tolerance

## 3. High-Level Flow

```
Client (React PWA)
        │
        ▼
API Gateway (AWS)
        │
        ▼
Conversation Handler (FastAPI on Lambda)
        │
        ├── Attribute extraction
        ├── Dialogue state
        └── LLM interaction (language only)
                │
                ▼
Eligibility Engine (Deterministic Python)
                │
                ▼
Scheme Data Store (S3/DynamoDB)
```

**Note:** Speech layer is invoked only when voice mode is active.

## 4. Core Components

### 4.1 Client

**React PWA**

Capabilities:
- Voice and text input
- Local language UI
- Offline caching of question flows
- Low-bandwidth mode (text-only fallback)

**Technology:**
- React (Vite)
- Tailwind CSS
- Web Speech API (voice input)

### 4.2 API Layer

**Single entry point** (AWS API Gateway)

Responsibilities:
- Session lifecycle
- Request routing
- Rate limiting
- Auth (future)

**Stateless by design.**

### 4.3 Conversation Handler

**Owns the interaction loop.**

Functions:
- Maintain session state
- Extract structured attributes
- Detect missing fields
- Generate next question
- Call LLM for:
  - Intent detection
  - Multilingual response
  - Simplification

**Never performs eligibility logic.**

**Technology:**
- FastAPI (Python)
- Pydantic (contracts)
- Mangum (Lambda adapter)

### 4.4 Eligibility Engine (Deterministic Core)

**Pure Python rule evaluator.**

Properties:
- Same input → same output
- Fully explainable
- LLM-independent
- Traceable decision path

Outputs:
- Eligible schemes
- Partially eligible schemes with actionable guidance
- Ineligible schemes with rejection reasons

**This is the trust anchor of the system.**

### 4.5 Scheme Service

Provides:
- Scheme metadata
- Rule sets
- State-filtered retrieval

**Data freshness as trust infrastructure:**
- Schemes are versioned (S3 object versioning)
- `last_verified_date` visible to users on every result
- TTL triggers manual review pipeline (30-90 days)
- Required for public-sector trust, not just technical optimization

**No AI involvement.**

### 4.6 Data Layer

Stores:
- Scheme master data
- Eligibility rules
- Anonymous session state
- Analytics events

**No permanent storage of PII.**

**Technology:**
- DynamoDB (sessions)
- S3 (scheme datasets)
- PostgreSQL (optional for relational queries)

## 5. Conversation → Decision Flow

1. User speaks or types
2. Session created or resumed
3. Attributes extracted and merged into profile
4. Missing fields → adaptive follow-up
5. Profile sent to eligibility engine
6. Deterministic evaluation
7. LLM converts result into simple local-language explanation
8. Response returned

## 6. Eligibility Engine Design

### 6.1 Input: Structured User Profile

```json
{
  "age_range": "18-35",
  "gender": "female",
  "occupation": "farmer",
  "income_band": "0-250000",
  "education_level": "10th",
  "location": {
    "state": "Maharashtra",
    "district": "Kolhapur"
  },
  "social_category": "SC"
}
```

### 6.2 Rule Model

Each scheme:
- Criteria list
- Logical operator (AND / OR)

**Supported operators:**
- `equals` / `not_equals`
- `less_than` / `greater_than` / `between`
- `in` / `not_in`
- `contains`

**Example:**
```json
{
  "scheme_id": "PM_KISAN",
  "criteria": [
    { "field": "occupation", "operator": "equals", "value": "farmer" },
    { "field": "income_band", "operator": "less_than", "value": 250000 },
    { "field": "location.state", "operator": "in", "value": ["Maharashtra"] }
  ],
  "logic": "AND"
}
```

### 6.3 Output Contract

```json
{
  "eligible_schemes": [
    {
      "scheme_id": "PM_KISAN",
      "eligibility_status": "eligible",
      "match_completeness": 1.0,
      "explanation": "You meet all criteria: farmer occupation, income below threshold"
    }
  ],
  "partially_eligible_schemes": [
    {
      "scheme_id": "MUDRA_LOAN",
      "eligibility_status": "partially_eligible",
      "missing_data": ["bank_account"],
      "user_guidance": "Open a bank account at any nationalized bank to become eligible"
    }
  ],
  "ineligible_schemes": [
    {
      "scheme_id": "PENSION_SCHEME",
      "eligibility_status": "ineligible",
      "rejection_reasons": ["age below 60 years"]
    }
  ]
}
```

**Every result includes an explanation trace.**

## 7. LLM Boundary (Hard Rule)

### LLM is used ONLY for:
✅ Intent detection  
✅ Language translation  
✅ Response generation  
✅ Question rephrasing  

### LLM is NEVER used for:
❌ Eligibility decisions  
❌ Rule evaluation  
❌ Scheme data generation  

## 8. Data Model

### Scheme
```
scheme_id (PK)
name
state
category
benefit_summary
eligibility_criteria_json
last_verified_date
```

### Rule
```
rule_id (PK)
scheme_id (FK)
field
operator
value
```

### Session (TTL-based)
```
session_id (PK)
collected_attributes (JSON)
language
created_at
ttl: 3600 seconds
```

### Analytics_Event
```
event_id (PK)
anonymized_session_id
event_type
metadata (JSON)
timestamp
```

**Privacy by design: session-scoped identity.**

## 9. API Surface

### Session
```
POST   /session/start
POST   /conversation/input
```

### Results
```
GET    /conversation/next-question
GET    /conversation/results
```

### Eligibility
```
POST   /eligibility/evaluate
```

### Schemes
```
GET    /schemes?state={state}&category={category}
GET    /schemes/{id}
```

## 10. Scalability Strategy

- **Stateless compute** → horizontal scaling
- **Cached scheme dataset** → reduced database load
- **Async analytics writes** → non-blocking
- **Voice as optional capability** → graceful degradation

Designed to scale from **district → national rollout**.

## 11. Security & Trust

- **Anonymous access** supported
- **Explicit consent** for saved profiles
- **TLS** for all transport
- **Role-based** scheme update access
- **Data minimization** enforced at API level

**Trust signals exposed to users:**
- "Why you are eligible"
- "Data last verified on [date]"

## 12. Observability

### System Metrics
- API latency
- LLM response time
- Eligibility execution time

### Product Metrics
- Schemes discovered per session
- Completion rate
- Question drop-off

### Trust Metrics
- % results with explanation
- Data freshness visibility

## 13. Low-Bandwidth Operation

- **Automatic voice → text fallback**
- **Cached question flow**
- **Reduced round trips**
- **Compressed responses**
- **Progressive enhancement**

## 14. Technology Stack

### Frontend
- **React** (Vite)
- **Tailwind CSS**
- **Web Speech API** (voice input)

### Backend
- **FastAPI** (Python)
- **Pydantic** (contracts)
- **Mangum** (Lambda adapter)

### Core Engine
- **Deterministic eligibility engine** (pure Python)

### Data
- **DynamoDB** — sessions
- **S3** — scheme datasets
- **PostgreSQL** (optional if relational queries required)

### AI Layer
- **Amazon Bedrock** (Anthropic Claude):
  - Intent extraction
  - Multilingual response generation

### Deployment (AWS-Native)
- **Frontend**: S3 + CloudFront (Amplify)
- **API**: API Gateway + Lambda (FastAPI)
- **Eligibility Engine**: Lambda (containerized stateless service)
- **Session Store**: DynamoDB (TTL: 1 hour)
- **Scheme Data**: S3 (versioned JSON)
- **Analytics**: CloudWatch Logs + S3
- **Speech**: Web Speech API (client-side)

## 15. Implementation Phases

### Phase 1: MVP (Hackathon)
- React PWA with text input
- FastAPI conversation handler
- Deterministic eligibility engine
- 5-10 sample schemes (Maharashtra)
- Basic LLM integration for Hindi/English

### Phase 2: Voice & Scale
- Web Speech API integration
- STT/TTS service (Bhashini API)
- Expand to 50+ schemes
- Multi-state support
- Analytics dashboard

### Phase 3: Production
- Authentication & user profiles
- Community experience layer
- Offline mode with sync
- Admin portal for scheme management
- Performance optimization
