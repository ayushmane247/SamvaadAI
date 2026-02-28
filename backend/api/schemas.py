# backend\api\schemas.py

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from typing import Literal

class SessionStartResponse(BaseModel):
    session_id: str
    created_at: datetime
    expires_at: datetime

class ConversationInputRequest(BaseModel):
    session_id: str
    user_input: str
    language: Literal["en", "hi", "mr"]

class ConversationInputResponse(BaseModel):
    next_question: Optional[str]
    collected_attributes: Dict[str, Any]
    is_complete: bool

class EligibilityResult(BaseModel):
    scheme_id: str
    eligibility_status: str
    explanation: str
    last_verified_date: str

class ConversationResultsResponse(BaseModel):
    eligible: List[EligibilityResult]
    partially_eligible: List[EligibilityResult]
    ineligible: List[EligibilityResult]