# SamvaadAI Backend - Engineering Architecture Review

**Review Date**: March 4, 2026  
**Reviewer**: Senior Backend Architect  
**System**: SamvaadAI - Government Scheme Eligibility Discovery Platform  
**Technology Stack**: Python, FastAPI, AWS Lambda, Amazon Bedrock (Claude), DynamoDB, S3  
**Review Scope**: Complete backend architecture, code quality, production readiness

---

## EXECUTIVE SUMMARY

**Overall Assessment**: ⚠️ **EARLY MVP WITH CRITICAL ARCHITECTURAL ISSUES**

**Production Readiness Score**: **4/10**

**Key Findings**:
- ✅ Strong foundation: Deterministic eligibility engine, LLM guardrails, structured logging
- ⚠️ Critical architectural flaws: Multiple API entry points, LLM client initialization anti-pattern
- ❌ Incomplete integration: Conversation manager not fully implemented
- ❌ Duplicate/unnecessary files: Multiple routers, standalone LLM service artifacts
- ⚠️ Security concerns: Incomplete input validation, missing rate limiting
- ⚠️ Scalability risks: LLM client per-request instantiation, no connection pooling

**Recommendation**: **DO NOT DEPLOY TO PRODUCTION** without addressing critical issues in Sections 5-7.

---

## SECTION 1 — CURRENT SYSTEM ARCHITECTURE

### 1.1 Layered Architecture Overview

The system follows a **4-layer architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                     API LAYER (FastAPI)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  routes.py   │  │conversation.py│  │   chat.py    │      │
│  │  (v1 API)    │  │  (duplicate)  │  │  (duplicate) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              ORCHESTRATION LAYER (Business Logic)            │
│  ┌──────────────────────────┐  ┌──────────────────────────┐│
│  │ conversation_manager.py  │  │ eligibility_service.py   ││
│  │ (LLM + Rule coordination)│  │ (Rule engine wrapper)    ││
│  └──────────────────────────┘  └──────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ llm_service  │  │eligibility_  │  │scheme_service│      │
│  │ (Bedrock)    │  │engine        │  │(S3 loader)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER (AWS)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  DynamoDB    │  │      S3      │  │   Bedrock    │      │
│  │  (Sessions)  │  │  (Schemes)   │  │   (Claude)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Component Responsibilities

#### API Layer (`backend/api/`)
**Purpose**: HTTP request handling, routing, validation
**Files**: `main.py`, `routes.py`, `conversation.py`, `chat.py`, `schemas.py`
**Responsibilities**:
- Request validation (Pydantic)
- Response formatting
- Error handling
- CORS configuration
- Lambda integration (Mangum)

**⚠️ ISSUE**: Three separate routers with overlapping functionality

#### Orchestration Layer (`backend/orchestration/`)
**Purpose**: Business logic coordination
**Files**: `conversation_manager.py`, `eligibility_service.py`
**Responsibilities**:
- LLM profile extraction coordination
- Eligibility evaluation orchestration
- Response generation coordination
- Latency tracking

**⚠️ ISSUE**: Incomplete conversation manager implementation

#### Service Layer
**LLM Service** (`backend/llm_service/`):
- Intent extraction (natural language → structured profile)
- Explanation generation (technical → simple language)
- Multilingual support (English, Hindi, Marathi)
- Safety guardrails (prevents LLM eligibility decisions)

**Eligibility Engine** (`backend/eligibility_engine/`):
- Deterministic rule evaluation
- 8 operators supported
- Explanation trace generation

**Scheme Service** (`backend/scheme_service/`):
- S3 scheme data loading
- Caching layer

**Session Service** (`backend/session_store/`):
- DynamoDB session management
- 1-hour TTL enforcement

#### Data Layer
- **DynamoDB**: Session state (TTL: 1 hour)
- **S3**: Scheme datasets (versioned)
- **Bedrock**: LLM API (Anthropic Claude)

### 1.3 Request Flow

**Current Flow** (Conversation API):
```
User Query
    ↓
POST /conversation
    ↓
conversation.py → ConversationManager
    ↓
ConversationManager.__init__() → LLMService() [NEW INSTANCE]
    ↓
LLMService.__init__() → BedrockClient() [NEW INSTANCE]
    ↓
extract_user_profile() → Bedrock API
    ↓
evaluate_profile() → Eligibility Engine
    ↓
generate_response() → Bedrock API
    ↓
Return response
```

**⚠️ CRITICAL ISSUE**: New LLM client created per request (see Section 5.1)

---


## SECTION 2 — CURRENT PROJECT STATUS

### 2.1 Project Maturity Classification

**Classification**: **EARLY MVP (Prototype → MVP Transition)**

**Reasoning**:
1. **Core functionality exists** but not fully integrated
2. **Production patterns present** (structured logging, error handling, guardrails)
3. **Critical gaps remain** (incomplete conversation flow, duplicate APIs)
4. **Testing infrastructure** exists (30+ tests) but incomplete coverage
5. **AWS integration** partially implemented (Lambda ready, DynamoDB/S3 not integrated)

### 2.2 What's Working Correctly

#### ✅ Eligibility Engine (100% Complete)
- **Status**: Production-ready
- **Evidence**: 17 passing unit tests, deterministic evaluation, < 100ms performance
- **Quality**: Excellent separation of concerns, pure functions, comprehensive testing

#### ✅ LLM Service Module (100% Complete - Standalone)
- **Status**: Production-ready as standalone module
- **Evidence**: Comprehensive tests, guardrails, fallback mechanisms
- **Quality**: Well-structured, proper error handling, safety-first design

#### ✅ Core Infrastructure
- **Structured logging**: JSON logs with request IDs
- **Configuration management**: Environment-based, centralized
- **Middleware**: Request tracking, CORS
- **Lambda integration**: Mangum adapter configured

#### ✅ API Foundation
- **FastAPI setup**: OpenAPI 3.1, Pydantic validation
- **Error handling**: Global exception handler, safe error responses
- **Health check**: Basic monitoring endpoint

### 2.3 What's Incomplete

#### ⚠️ Conversation Orchestration (50% Complete)
- **Issue**: `ConversationManager` exists but missing critical methods
- **Missing**: `generate_response()`, `handle_message()` methods not in LLMService
- **Impact**: Conversation API endpoints return errors

#### ⚠️ Data Layer Integration (30% Complete)
- **Issue**: DynamoDB session service exists but not integrated into API
- **Issue**: S3 scheme loader exists but using mock data
- **Impact**: Sessions not persisted, schemes not loaded from S3

#### ⚠️ API Consistency (40% Complete)
- **Issue**: Three separate routers (`routes.py`, `conversation.py`, `chat.py`)
- **Issue**: Overlapping functionality, inconsistent patterns
- **Impact**: Confusing API surface, maintenance burden

### 2.4 What's Fragile

#### 🔴 LLM Client Initialization Pattern
**Location**: `conversation_manager.py:__init__()`
```python
def __init__(self):
    self.llm = LLMService()  # Creates new Bedrock client per request
```
**Problem**: New AWS Bedrock client created for every API request
**Impact**: 
- Connection overhead on every request
- Potential rate limiting issues
- Increased latency (cold start per request)
- Resource exhaustion under load

#### 🔴 Multiple API Entry Points
**Locations**: `routes.py`, `conversation.py`, `chat.py`
**Problem**: Three different conversation endpoints with different patterns
**Impact**:
- Unclear which endpoint to use
- Duplicate code
- Inconsistent error handling
- Maintenance complexity

#### 🔴 Incomplete Error Boundaries
**Location**: `conversation_manager.py:process_user_query()`
**Problem**: Generic exception handling without specific error types
**Impact**:
- All errors treated the same
- No differentiation between retryable/non-retryable errors
- Poor user experience

#### 🔴 Missing Input Validation
**Location**: `conversation.py`, `chat.py`
**Problem**: No validation on user input length, content, or format
**Impact**:
- Potential for abuse (very long inputs)
- No protection against malicious content
- Uncontrolled LLM costs

---

## SECTION 3 — CODE QUALITY REVIEW

### 3.1 Code Smells Identified

#### 🟡 Duplicate Logic

**Location 1**: `llm_service/llm_service.py` (lines 280-295)
```python
# Convenience functions
def extract_user_profile(user_text: str, language: str = "en"):
    service = LLMService()  # Creates new instance
    return service.extract_user_profile(user_text, language)
```
**Issue**: Module-level convenience functions create new service instances
**Impact**: Defeats singleton pattern, creates unnecessary objects

**Location 2**: Multiple routers in `api/`
- `routes.py`: `/v1/conversation/input`
- `conversation.py`: `/conversation`
- `chat.py`: `/chat`
**Issue**: Three different ways to process conversation
**Impact**: Confusion, maintenance burden, inconsistent behavior

#### 🟡 Improper Object Initialization

**Location**: `conversation_manager.py:__init__()`
```python
class ConversationManager:
    def __init__(self):
        self.llm = LLMService()  # Anti-pattern
```
**Issue**: Heavy object (Bedrock client) created in constructor
**Better Pattern**: Dependency injection or lazy initialization
```python
class ConversationManager:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service  # Inject dependency
```

#### 🟡 Inefficient Resource Creation

**Location**: `bedrock_client.py:__init__()`
**Issue**: boto3 client created synchronously in constructor
**Impact**: Blocks request thread during AWS SDK initialization
**Better Pattern**: Async initialization or connection pooling

#### 🟡 Inconsistent Naming

**Examples**:
- `conversation_manager.py`: `process_user_query()`
- `chat.py`: `handle_message()`
- `routes.py`: `conversation_input()`

**Issue**: Three different names for same concept
**Impact**: Cognitive load, unclear API contract

#### 🟡 Dead Code

**Location**: `llm_service/` standalone artifacts
- `demo_run.py`: Demo script
- `demo_output.txt`: Demo output
- `mock_rule_engine.py`: Mock for testing
- `integration_test.py`: Standalone tests
- `test_llm.py`: Standalone tests
- `guardrail_tests.py`: Standalone tests

**Issue**: Standalone module artifacts not integrated into main backend
**Impact**: Confusion, maintenance burden, deployment bloat

#### 🟡 Improper Dependency Management

**Location**: `llm_service/requirements.txt` + `backend/requirements.txt`
**Issue**: Two separate requirements files
**Impact**: Dependency conflicts, unclear which is authoritative

#### 🟡 Tight Coupling

**Location**: `conversation_manager.py`
```python
from llm_service.llm_service import LLMService
from orchestration.eligibility_service import evaluate_profile
```
**Issue**: Direct imports create tight coupling
**Better Pattern**: Dependency injection with interfaces

### 3.2 Structural Mistakes

#### 🔴 Missing Abstraction Layer

**Issue**: No interface/protocol definitions for services
**Impact**: 
- Hard to test (no mocking)
- Hard to swap implementations
- Tight coupling between layers

**Recommendation**: Add protocols
```python
from typing import Protocol

class LLMServiceProtocol(Protocol):
    def extract_user_profile(self, text: str, lang: str) -> dict: ...
    def generate_explanation(self, result: dict, lang: str) -> str: ...
```

#### 🔴 Inconsistent Error Handling

**Pattern 1** (eligibility_service.py):
```python
except Exception as e:
    logger.error(f"Evaluation failed: {str(e)}", exc_info=True)
    raise  # Re-raises exception
```

**Pattern 2** (conversation_manager.py):
```python
except Exception as e:
    logger.error("...", exc_info=True)
    raise  # Re-raises exception
```

**Pattern 3** (routes.py):
```python
except Exception as e:
    logger.error("...", exc_info=True)
    raise HTTPException(status_code=500, detail="...")  # Converts to HTTP error
```

**Issue**: Inconsistent error propagation strategy
**Impact**: Unclear error handling contract

#### 🔴 Missing Validation Layer

**Issue**: No centralized input validation
**Locations**: 
- `conversation.py`: No validation on `query` field
- `chat.py`: No validation on `message` field
- `routes.py`: Basic Pydantic validation only

**Missing Validations**:
- Input length limits
- Content sanitization
- Rate limiting per user
- Malicious content detection

### 3.3 Violations of Best Practices

#### ❌ Logging Configuration in Module

**Location**: `llm_service/llm_service.py:15-18`
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```
**Violation**: Module configures global logging
**Impact**: Conflicts with application logging configuration
**Fix**: Remove `basicConfig`, use application logger

#### ❌ Hardcoded Paths

**Location**: `llm_service/llm_service.py:23-25`
```python
PROMPTS_DIR = Path(__file__).parent / "prompts"
INTENT_PROMPT_PATH = PROMPTS_DIR / "intent_prompt.txt"
```
**Issue**: Relative paths may break in Lambda deployment
**Fix**: Use configuration-based paths

#### ❌ Missing Type Hints

**Location**: `chat.py:handle_message()`
**Issue**: Method not defined in `ConversationManager` but called
**Impact**: Runtime errors, no IDE support

#### ❌ Synchronous I/O in Async Context

**Location**: `conversation.py:process_conversation()`
```python
@router.post("/conversation")
async def process_conversation(request: ConversationRequest):
    manager = ConversationManager()  # Sync initialization
    result = manager.process_user_query(request.query)  # Sync call
```
**Issue**: Async endpoint with synchronous operations
**Impact**: Blocks event loop, poor concurrency

---

