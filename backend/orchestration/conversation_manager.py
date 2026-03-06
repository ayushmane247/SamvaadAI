"""
Conversation orchestration layer for SamvaadAI.

Coordinates:
- LLM profile extraction (single Bedrock call)
- Deterministic eligibility evaluation
- LLM response generation (only when results ready)
- Optional session persistence via DynamoDB

Architectural guarantees:
- Dependencies injected via constructor
- No instance creation of heavy objects
- Deterministic orchestration (same inputs → same outputs)
- No business logic or eligibility rules
- Session support is optional — stateless mode works without it
"""

import time
from typing import Dict, Any, Callable, Optional

from llm_service.llm_service import LLMService
from orchestration.eligibility_service import evaluate_profile as _default_evaluate
from core.logging_config import logger


class ConversationManager:
    """
    Orchestrates the conversation pipeline.

    Must be instantiated once (at app startup) and reused across requests.
    Dependencies are injected via constructor — never created per-request.
    """

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        evaluate_fn: Optional[Callable[[dict], dict]] = None,
        session_service=None,
    ):
        """
        Args:
            llm_service: LLMService instance (uses singleton Bedrock client).
            evaluate_fn: Eligibility evaluation function.
                         Defaults to orchestration.eligibility_service.evaluate_profile.
            session_service: Optional SessionService for persisting conversation state.
                             When None, the pipeline runs in stateless mode.
        """
        self.llm = llm_service or LLMService()
        self.evaluate = evaluate_fn or _default_evaluate
        self.session_service = session_service
        logger.info("ConversationManager initialized")

    def process_user_query(
        self,
        query: str,
        language: str = "en",
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Orchestrate processing of a user query end-to-end.

        Pipeline:
        1. Load session (if session_id provided)
        2. LLM extract user profile (Bedrock call #1)
        3. Merge with stored profile (if session exists)
        4. Deterministic eligibility evaluation (free)
        5. LLM generate response (Bedrock call #2 — only when results ready)
        6. Store conversation state (if session_id provided)

        Args:
            query: User's natural language query.
            language: Language code (en, hi, mr).
            session_id: Optional session ID for stateful conversations.

        Returns:
            Dict with profile, eligibility, response, and optional session_id.
        """
        start_time = time.time()

        try:
            logger.info("Processing user query")

            # Step 0 — Load existing session (optional)
            stored_profile = {}
            if session_id and self.session_service:
                session = self.session_service.get_session(session_id)
                if session:
                    stored_profile = session.get("structured_profile", {})
                    logger.info(
                        "Session loaded",
                        extra={"session_id": session_id},
                    )

            # Step 1 — Extract structured profile (Bedrock call)
            extracted = self.llm.extract_user_profile(query, language)

            # Step 2 — Merge: stored profile + newly extracted attributes
            # New extractions overwrite stored values (latest wins)
            profile = {**stored_profile, **extracted}

            # Step 3 — Deterministic eligibility evaluation (no LLM)
            eligibility = self.evaluate(profile)

            # Step 4 — Generate natural language response (Bedrock call)
            response = self.llm.generate_response(
                user_query=query,
                profile=profile,
                eligibility=eligibility,
                language=language,
            )

            # Step 5 — Store conversation state (optional)
            if session_id and self.session_service:
                self.session_service.update_session(
                    session_id=session_id,
                    updates={
                        "structured_profile": profile,
                        "evaluation_result": eligibility,
                        "conversation_state": {
                            "last_query": query,
                            "language": language,
                        },
                    },
                )
                logger.info(
                    "Session updated",
                    extra={"session_id": session_id},
                )

            latency = (time.time() - start_time) * 1000

            logger.info(
                "Conversation processed successfully",
                extra={"latency_ms": round(latency, 2)},
            )

            result = {
                "profile": profile,
                "eligibility": eligibility,
                "response": response,
            }

            if session_id:
                result["session_id"] = session_id

            return result

        except Exception as e:
            latency = (time.time() - start_time) * 1000

            logger.error(
                "Conversation processing failed",
                extra={
                    "latency_ms": round(latency, 2),
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )

            raise