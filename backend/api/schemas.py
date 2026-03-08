# backend\api\schemas.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class SessionStartResponse(BaseModel):
    session_id: str
    created_at: datetime
    expires_at: datetime

class EligibilityResult(BaseModel):
    scheme_id: str
    eligibility_status: str
    explanation: str
    last_verified_date: str

class ConversationResultsResponse(BaseModel):
    eligible: List[EligibilityResult]
    partially_eligible: List[EligibilityResult]
    ineligible: List[EligibilityResult]


class EvaluateRequest(BaseModel):
    """Request model for eligibility evaluation endpoint"""
    profile: Optional[Dict[str, Any]]

class EvaluateResponse(BaseModel):
    """Response model for eligibility evaluation endpoint"""
    eligible: List[Dict[str, Any]]
    partially_eligible: List[Dict[str, Any]]
    ineligible: List[Dict[str, Any]]


# ---- Conversation Endpoint Schemas ----

class ConversationRequest(BaseModel):
    """Request model for POST /v1/conversation"""
    query: str = Field(..., min_length=1, max_length=2000)
    language: Optional[str] = Field("en", pattern=r"^(en|hi|mr)$")
    session_id: Optional[str] = Field(None, max_length=100)


class ConversationResponse(BaseModel):
    """Response model for POST /v1/conversation"""
    profile: Dict[str, Any]
    eligibility: Dict[str, Any]
    response: str
    schemes: List[Dict[str, Any]] = []
    documents: List[str] = []
    session_id: Optional[str] = None
    llm_enhanced: bool = False