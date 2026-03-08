# 🔧 SamvaadAI Backend

**FastAPI-powered conversational AI backend for government scheme discovery**

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.134-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![AWS](https://img.shields.io/badge/AWS-Bedrock%20%7C%20S3%20%7C%20Lambda-FF9900?style=flat-square&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![Tests](https://img.shields.io/badge/Tests-82%20passing-success?style=flat-square)](./tests/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Core Components](#core-components)
- [Setup & Installation](#setup--installation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Configuration](#configuration)

---

## 🎯 Overview

The SamvaadAI backend is a production-grade FastAPI application that powers conversational AI for government scheme discovery. It implements a hybrid architecture combining deterministic rule-based logic with optional AI enhancement.

### Key Features

✅ **Hybrid Architecture**: Deterministic pipeline + optional AI enhancement  
✅ **Graceful Degradation**: Works perfectly even when AI services fail  
✅ **High Performance**: <500ms p95 latency, <100ms eligibility evaluation  
✅ **Production-Ready**: 82 tests passing, comprehensive error handling  
✅ **AWS Integration**: Bedrock, S3, DynamoDB, Lambda  
✅ **Security**: Rate limiting, input sanitization, CORS, request validation  

---

## 🏗️ Architecture

### System Layers

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                     │
│  • Request validation (Pydantic)                            │
│  • Rate limiting (100 req/min)                              │
│  • CORS configuration                                       │
│  • Global exception handling                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Orchestration Layer (ConversationManager)       │
│  • Pipeline coordination                                    │
│  • Session management                                       │
│  • History tracking                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Processing Layers                         │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ Profile Extractor│  │ Eligibility Engine│                │
│  │  (Deterministic) │  │  (Rule-Based)     │                │
│  └──────────────────┘  └──────────────────┘                │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ Template Generator│  │  LLM Service     │                │
│  │  (Multilingual)   │  │  (Optional AI)   │                │
│  └──────────────────┘  └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  • S3: Scheme data storage                                  │
│  • DynamoDB: Session persistence                            │
│  • Bedrock: AI inference (optional)                         │
└─────────────────────────────────────────────────────────────┘
```

### Conversation Pipeline

```python
User Query
    ↓
Profile Extraction (Deterministic Regex)
    ↓
Profile Memory Update (Session-Based)
    ↓
Eligibility Evaluation (Rule Engine)
    ↓
Template Response Generation (Multilingual)
    ↓
Optional AI Enhancement (Bedrock)
    ↓
Response + Scheme Cards
```

---

## 📁 Project Structure

```
backend/
├── api/                          # API layer
│   ├── main.py                   # FastAPI app initialization
│   ├── routes.py                 # API endpoints
│   └── schemas.py                # Pydantic models
│
├── orchestration/                # Orchestration layer
│   ├── conversation_manager.py   # Main pipeline coordinator
│   ├── eligibility_service.py    # Eligibility evaluation wrapper
│   └── profile_memory.py         # Session-based profile storage
│
├── llm_service/                  # AI layer
│   ├── bedrock_client.py         # Amazon Bedrock client
│   ├── inference_gateway.py      # LLM gateway with caching
│   ├── llm_service.py            # LLM service wrapper
│   ├── profile_extractor.py      # Deterministic profile extraction
│   └── fallback_templates.py     # Template responses
│
├── eligibility_engine/           # Logic layer
│   ├── engine.py                 # Eligibility evaluation engine
│   └── rule_parser.py            # Rule parsing and evaluation
│
├── scheme_service/               # Data layer
│   └── scheme_loader.py          # S3 scheme data loader
│
├── session_store/                # Persistence layer
│   ├── session_service.py        # DynamoDB session management
│   └── profile_memory.py         # Profile memory adapter
│
├── core/                         # Core utilities
│   ├── config.py                 # Configuration management
│   ├── logging_config.py         # Structured logging
│   └── middleware.py             # Custom middleware
│
└── tests/                        # Test suite
    ├── test_api.py               # API endpoint tests
    ├── test_engine.py            # Eligibility engine tests
    ├── test_profile_extractor.py # Profile extraction tests
    ├── test_integration.py       # Integration tests
    └── test_e2e_scenarios.py     # End-to-end tests
```

---

## 🔌 API Endpoints

### Public Endpoints

#### `POST /v1/conversation`
Process a conversational query through the full pipeline.

**Request:**
```json
{
  "query": "I am a farmer from Maharashtra",
  "language": "en",
  "session_id": "optional-uuid"
}
```

**Response:**
```json
{
  "profile": {
    "occupation": "farmer",
    "state": "Maharashtra"
  },
  "eligibility": {
    "eligible": [...],
    "partially_eligible": [...],
    "ineligible": [...]
  },
  "response": "You are eligible for PM Kisan Samman Nidhi...",
  "schemes": [...],
  "documents": [...],
  "session_id": "uuid"
}
```

#### `POST /v1/session/start`
Create a new conversation session.

**Response:**
```json
{
  "session_id": "uuid",
  "created_at": "2026-03-08T10:00:00Z",
  "expires_at": "2026-03-08T11:00:00Z"
}
```

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### Internal Endpoints

#### `POST /v1/evaluate`
Direct profile evaluation (testing only).

---

## 🧩 Core Components

### 1. ConversationManager
**File**: `orchestration/conversation_manager.py`

Orchestrates the complete conversation pipeline with dependency injection.

```python
manager = ConversationManager(
    gateway=InferenceGateway(),
    evaluate_fn=evaluate_profile,
    session_service=SessionService()
)

result = manager.process_user_query(
    query="I am a farmer",
    language="en",
    session_id="uuid"
)
```

### 2. Profile Extractor
**File**: `llm_service/profile_extractor.py`

Deterministic regex-based profile extraction (works without AI).

```python
extraction = extract_profile(
    text="I am a 35-year-old farmer from Maharashtra",
    language="en"
)
# Returns: {
#   "profile": {"occupation": "farmer", "state": "Maharashtra", "age": 35},
#   "missing_fields": ["income_range", "gender", ...]
# }
```

### 3. Eligibility Engine
**File**: `eligibility_engine/engine.py`

Pure deterministic rule-based eligibility evaluation.

```python
result = evaluate(profile, schemes)
# Returns: {
#   "eligible": [...],
#   "partially_eligible": [...],
#   "ineligible": [...]
# }
```

### 4. Bedrock Client
**File**: `llm_service/bedrock_client.py`

Singleton Amazon Bedrock client with retry and fallback.

```python
client = get_client()
response = client.invoke_model_with_response_stream(prompt)
```

### 5. Session Service
**File**: `session_store/session_service.py`

DynamoDB-backed session persistence with TTL.

```python
service = SessionService()
session = service.create_session()
service.update_session(session_id, updates)
```

---

## 🚀 Setup & Installation

### Prerequisites

- Python 3.13+
- AWS Account (for Bedrock, S3, DynamoDB)
- pip or poetry

### Installation Steps

#### 1. Clone and Navigate
```bash
git clone https://github.com/yourusername/samvaadai.git
cd samvaadai/backend
```

#### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` with your AWS credentials:
```env
APP_ENV=development
AWS_REGION=ap-south-1
S3_BUCKET_NAME=your-bucket-name
BEDROCK_ENABLED=true
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
DYNAMODB_TABLE_NAME=samvaadai-sessions
```

#### 5. Run Tests
```bash
pytest
```

#### 6. Start Development Server
```bash
uvicorn api.main:app --reload
```

Server will run on `http://localhost:8000`

#### 7. Access API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test Suite
```bash
pytest tests/test_api.py
pytest tests/test_engine.py
pytest tests/test_profile_extractor.py
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html
```

### Test Results
```
82 tests passing | 100% success rate | 5.89s execution time
```

### Test Categories

- **Unit Tests**: Core function testing
- **Integration Tests**: Component interaction testing
- **E2E Tests**: Full pipeline testing
- **Performance Tests**: Latency validation

---

## 🚢 Deployment

### AWS Lambda Deployment

#### 1. Package Application
```bash
pip install -r requirements.txt -t package/
cp -r api orchestration llm_service eligibility_engine scheme_service session_store core package/
cd package && zip -r ../deployment.zip . && cd ..
```

#### 2. Deploy to Lambda
```bash
aws lambda update-function-code \
  --function-name samvaadai-backend \
  --zip-file fileb://deployment.zip
```

#### 3. Configure Lambda
- **Runtime**: Python 3.13
- **Memory**: 512 MB
- **Timeout**: 30 seconds
- **Handler**: `api.main.handler`

### Environment Variables (Production)
```env
APP_ENV=production
AWS_REGION=ap-south-1
S3_BUCKET_NAME=samvaadai-schemes-prod
BEDROCK_ENABLED=true
DYNAMODB_TABLE_NAME=samvaadai-sessions-prod
ALLOWED_ORIGINS=https://main.d1ldcuarhn106p.amplifyapp.com
```

---

## ⚙️ Configuration

### Core Configuration
**File**: `core/config.py`

```python
class Config:
    # Environment
    APP_ENV = "development"  # development | production | test
    
    # AWS
    AWS_REGION = "ap-south-1"
    S3_BUCKET_NAME = "samvaadai-schemes-prod"
    DYNAMODB_TABLE_NAME = "samvaadai-sessions"
    
    # Bedrock
    BEDROCK_ENABLED = True
    BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
    BEDROCK_TIMEOUT_SECONDS = 3
    
    # Performance
    API_LATENCY_THRESHOLD_MS = 500
    SCHEME_CACHE_TTL_SECONDS = 300
    
    # Security
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW_SECONDS = 60
```

### Feature Flags

- `BEDROCK_ENABLED`: Enable/disable AI enhancement
- `SCHEME_CACHE_ENABLED`: Enable/disable scheme caching
- `ENABLE_STRUCTURED_LOGGING`: Enable JSON logging

---

## 📊 Performance Metrics

- **API Latency (p95)**: <500ms
- **Eligibility Evaluation**: <100ms
- **Profile Extraction**: <100ms
- **Template Generation**: <50ms
- **Cold Start**: <2 seconds

---

## 🔒 Security Features

- ✅ Input validation (Pydantic)
- ✅ Input sanitization (prompt injection defense)
- ✅ Rate limiting (100 req/min per IP)
- ✅ CORS configuration
- ✅ Request size limits (10KB max)
- ✅ No PII in logs
- ✅ Environment-based secrets

---

## 📚 Additional Resources

- [API Documentation](./docs/API.md)
- [Architecture Guide](./docs/ARCHITECTURE.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [Engineering Audit](../docs/SAMVAADAI_ENGINEERING_AUDIT_REPORT.md)

---

## 🤝 Contributing

See the main [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

---

<div align="center">

**Built with ❤️ using FastAPI and AWS**

</div>
