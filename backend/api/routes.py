# backend\api\routes.py
from fastapi import APIRouter
from api.schemas import (
    SessionStartResponse,
    ConversationInputRequest,
    ConversationInputResponse,
    ConversationResultsResponse,
)
from datetime import datetime, timedelta
import uuid

router = APIRouter(prefix="/v1")

@router.post("/session/start", response_model=SessionStartResponse)
def start_session():
    now = datetime.utcnow()
    return SessionStartResponse(
        session_id=str(uuid.uuid4()),
        created_at=now,
        expires_at=now + timedelta(hours=1)
    )

@router.post("/conversation/input", response_model=ConversationInputResponse)
def conversation_input(request: ConversationInputRequest):
    return ConversationInputResponse(
        next_question="Stub question",
        collected_attributes={},
        is_complete=False
    )

@router.get("/conversation/results", response_model=ConversationResultsResponse)
def get_results():
    return ConversationResultsResponse(
        eligible=[],
        partially_eligible=[],
        ineligible=[]
    )