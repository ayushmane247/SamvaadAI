# backend\api\routes.py
"""
API Routes for SamvaadAI.

Public API Surface:
- POST /v1/conversation       — Process conversational input
- POST /v1/session/start      — Create session
- GET  /v1/conversation/results — Get results (stub)
- GET  /health                 — Health check (in main.py)

Internal:
- POST /v1/evaluate            — Direct evaluation (testing only)

Architectural Rules:
- Zero business logic in routes
- All processing through ConversationManager
- Structured error responses
- No PII in error messages
"""

from fastapi import APIRouter, HTTPException, Request
from api.schemas import (
    SessionStartResponse,
    ConversationResultsResponse,
    ConversationRequest,
    ConversationResponse,
    EvaluateRequest,
    EvaluateResponse,
)
from orchestration.conversation_manager import ConversationManager
from orchestration.eligibility_service import evaluate_profile
from core.logging_config import logger
from datetime import datetime, timedelta, UTC
import uuid

router = APIRouter(prefix="/v1")

# =========================================
# Singleton ConversationManager
# Initialized once, reused across requests
# =========================================
_manager = ConversationManager()


# =========================================
# Primary Endpoint — Conversation
# =========================================

@router.post("/conversation", response_model=ConversationResponse)
def conversation(request_obj: Request, payload: ConversationRequest):
    """
    Process a conversational query through the full pipeline.

    Pipeline:
    1. LLM profile extraction
    2. Deterministic eligibility evaluation
    3. LLM response generation

    Args:
        request_obj: FastAPI request (for request_id).
        payload: ConversationRequest with query and optional language.

    Returns:
        ConversationResponse with profile, eligibility, and response.
    """
    request_id = getattr(request_obj.state, "request_id", "unknown")

    try:
        result = _manager.process_user_query(
            query=payload.query,
            language=payload.language or "en",
            session_id=payload.session_id,
        )

        logger.info(
            "Conversation endpoint success",
            extra={"request_id": request_id},
        )

        return result

    except Exception as e:
        logger.error(
            f"Conversation endpoint failed: {type(e).__name__}",
            extra={"request_id": request_id},
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Conversation processing failed. Please try again.",
        )


# =========================================
# Session Management
# =========================================

@router.post("/session/start", response_model=SessionStartResponse)
def start_session(request: Request):
    """Create new anonymous session."""
    now = datetime.now(UTC)
    session_id = str(uuid.uuid4())

    logger.info(f"Session created: {session_id}")

    return SessionStartResponse(
        session_id=session_id,
        created_at=now,
        expires_at=now + timedelta(hours=1),
    )


@router.get("/conversation/results", response_model=ConversationResultsResponse)
def get_results():
    """
    Get eligibility results for session (stub).

    Future: Retrieve from DynamoDB session store.
    """
    return ConversationResultsResponse(
        eligible=[],
        partially_eligible=[],
        ineligible=[],
    )


# =========================================
# Internal — Direct Evaluation (testing)
# =========================================

@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate_profile_route(request_obj: Request, payload: EvaluateRequest):
    """
    Internal endpoint for direct profile evaluation.

    ⚠️ NOT PUBLIC-FACING — for testing/internal use only.
    """
    if payload.profile is None:
        logger.warning("Evaluation request missing profile")
        raise HTTPException(status_code=400, detail="Profile is required")

    request_id = getattr(request_obj.state, "request_id", "unknown")

    try:
        result = evaluate_profile(payload.profile)

        logger.info(
            "Evaluation successful",
            extra={
                "request_id": request_id,
                "evaluation_count": (
                    len(result.get("eligible", []))
                    + len(result.get("partially_eligible", []))
                    + len(result.get("ineligible", []))
                ),
            },
        )

        return result

    except Exception as e:
        logger.error(
            f"Evaluation failed: {type(e).__name__}",
            extra={"request_id": request_id},
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Evaluation failed. Please try again.",
        )