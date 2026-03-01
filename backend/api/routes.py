# backend\api\routes.py
"""
API Routes for SamvaadAI.

Public API Contract (from requirements.md):
- POST /v1/session/start
- POST /v1/conversation/input
- GET /v1/conversation/results

Internal Endpoint (not public-facing):
- POST /v1/evaluate (for testing/internal use only)

Architectural Rules:
- No business logic in routes
- All evaluation through orchestration layer
- Structured error responses
- No PII in error messages
"""

from fastapi import APIRouter, HTTPException, Request
from api.schemas import (
    SessionStartResponse,
    ConversationInputRequest,
    ConversationInputResponse,
    ConversationResultsResponse,
    EvaluateRequest,
    EvaluateResponse,
)
from orchestration.eligibility_service import evaluate_profile
from core.logging_config import logger
from datetime import datetime, timedelta, UTC
import uuid

router = APIRouter(prefix="/v1")


@router.post("/session/start", response_model=SessionStartResponse)
def start_session(request: Request):
    """
    Create new anonymous session.
    
    Returns:
        Session metadata with TTL
    """
    now = datetime.now(UTC)
    session_id = str(uuid.uuid4())
    
    logger.info(f"Session created: {session_id}")
    
    return SessionStartResponse(
        session_id=session_id,
        created_at=now,
        expires_at=now + timedelta(hours=1)
    )


@router.post("/conversation/input", response_model=ConversationInputResponse)
def conversation_input(request: ConversationInputRequest):
    """
    Process conversational input (stub for MVP).
    
    Future implementation:
    - Extract intent via LLM
    - Update session state
    - Generate next question
    - Trigger evaluation when complete
    """
    # TODO: Implement conversation handler
    return ConversationInputResponse(
        next_question="Stub question",
        collected_attributes={},
        is_complete=False
    )


@router.get("/conversation/results", response_model=ConversationResultsResponse)
def get_results():
    """
    Get eligibility results for session (stub for MVP).
    
    Future implementation:
    - Retrieve session from DynamoDB
    - Return cached evaluation results
    """
    # TODO: Implement results retrieval
    return ConversationResultsResponse(
        eligible=[],
        partially_eligible=[],
        ineligible=[]
    )


@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate_profile_route(request_obj: Request, payload: EvaluateRequest):
    """
    Internal endpoint for direct profile evaluation.
    
    ⚠️ NOT PUBLIC-FACING:
    This endpoint is for testing and internal use only.
    Public interaction must occur through conversational endpoints.
    
    Product identity: Conversational Eligibility Guidance System
    NOT: Eligibility-as-a-Service API
    
    Args:
        request_obj: FastAPI request object
        payload: Evaluation request with profile
        
    Returns:
        Eligibility results (eligible, partially_eligible, ineligible)
        
    Raises:
        HTTPException: 400 if profile invalid, 500 if evaluation fails
    """
    # Validation
    if payload.profile is None:
        logger.warning("Evaluation request missing profile")
        raise HTTPException(
            status_code=400,
            detail="Profile is required"
        )
    
    # Get request ID from middleware
    request_id = getattr(request_obj.state, "request_id", "unknown")
    
    try:
        # Orchestrate evaluation (no transformation)
        result = evaluate_profile(payload.profile)
        
        logger.info(
            f"Evaluation successful",
            extra={
                "request_id": request_id,
                "evaluation_count": (
                    len(result.get("eligible", [])) +
                    len(result.get("partially_eligible", [])) +
                    len(result.get("ineligible", []))
                )
            }
        )
        
        return result
    
    except Exception as e:
        logger.error(
            f"Evaluation failed: {str(e)}",
            extra={"request_id": request_id},
            exc_info=True
        )
        
        # Safe error response (no PII, no stack trace)
        raise HTTPException(
            status_code=500,
            detail="Evaluation failed. Please try again."
        )