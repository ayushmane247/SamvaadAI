"""
Conversation orchestration layer for SamvaadAI.

Coordinates:
- Deterministic profile extraction (always first)
- ProfileMemory accumulation across turns
- Deterministic eligibility evaluation
- Template response generation
- Optional LLM enhancement (only when needed AND available)
- MAX_SESSION_MESSAGES guard to prevent memory/token explosion

Pipeline:
    User Input → Profile Extraction → Memory Update → Eligibility →
    Template Response → LLM Enhancement (conditional)

Architectural guarantees:
- Dependencies injected via constructor
- No instance creation of heavy objects
- Deterministic orchestration (same inputs → same outputs)
- No business logic or eligibility rules
- Session support via in-memory ProfileMemory
- LLM called only when template response is insufficient
"""

import time
from typing import Dict, Any, Callable, Optional, List

from llm_service.inference_gateway import InferenceGateway
from llm_service.profile_extractor import extract_profile
from orchestration.eligibility_service import evaluate_profile as _default_evaluate
from orchestration.profile_memory import ProfileMemory
from core.logging_config import logger
from core.config import config


# ── Guards ────────────────────────────────────────────────────────
MAX_SESSION_MESSAGES = 20  # Prevents token explosion + memory growth
LLM_ENHANCEMENT_THRESHOLD = 150  # Only call LLM if template < N chars


class ConversationManager:
    """
    Orchestrates the conversation pipeline.

    Must be instantiated once (at app startup) and reused across requests.
    Dependencies are injected via constructor — never created per-request.
    """

    def __init__(
        self,
        gateway: Optional[InferenceGateway] = None,
        evaluate_fn: Optional[Callable[[dict], dict]] = None,
        session_service=None,
    ):
        """
        Args:
            gateway: InferenceGateway instance (wraps LLMService with caching).
            evaluate_fn: Eligibility evaluation function.
                         Defaults to orchestration.eligibility_service.evaluate_profile.
            session_service: Optional SessionService for persisting conversation state.
                             When None, the pipeline runs with in-memory sessions only.
        """
        self.gateway = gateway or InferenceGateway()
        self.evaluate = evaluate_fn or _default_evaluate
        self.session_service = session_service

        # In-memory session stores (session_id → ProfileMemory / history)
        self._memories: Dict[str, ProfileMemory] = {}
        self._histories: Dict[str, List[Dict[str, str]]] = {}

        logger.info("ConversationManager initialized")

    def _get_memory(self, session_id: Optional[str]) -> ProfileMemory:
        """Get or create ProfileMemory for a session."""
        if not session_id:
            return ProfileMemory()
        if session_id not in self._memories:
            self._memories[session_id] = ProfileMemory()
        return self._memories[session_id]

    def _get_history(self, session_id: Optional[str]) -> List[Dict[str, str]]:
        """Get or create conversation history for a session."""
        if not session_id:
            return []
        if session_id not in self._histories:
            self._histories[session_id] = []
        return self._histories[session_id]

    def _trim_history(self, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Trim history to MAX_SESSION_MESSAGES to prevent memory explosion."""
        if len(history) > MAX_SESSION_MESSAGES:
            history[:] = history[-MAX_SESSION_MESSAGES:]
        return history

    def process_user_query(
        self,
        query: str,
        language: str = "en",
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Orchestrate processing of a user query end-to-end.

        Optimized Pipeline:
        1. Deterministic profile extraction (always runs — free)
        2. ProfileMemory update (merge with session memory)
        3. Deterministic eligibility evaluation (free)
        4. Template response generation (free)
        5. Optional LLM enhancement (only if template < threshold AND Bedrock available)
        6. Store conversation history (with MAX_SESSION_MESSAGES guard)

        Args:
            query: User's natural language query.
            language: Language code (en, hi, mr).
            session_id: Optional session ID for stateful conversations.

        Returns:
            Dict with profile, eligibility, response, schemes, documents, and optional session_id.
        """
        start_time = time.time()

        try:
            logger.info("Processing user query")

            # ── Step 1 — Deterministic profile extraction (always runs) ──
            extraction = extract_profile(query, language)
            extracted_profile = extraction["profile"]

            logger.info(
                "Profile extracted",
                extra={
                    "field_count": len(extracted_profile),
                    "fields": list(extracted_profile.keys()),
                },
            )

            # ── Step 2 — ProfileMemory update ──
            memory = self._get_memory(session_id)
            memory.update(extracted_profile)
            profile = memory.get_profile()
            missing_fields = memory.get_missing_fields()

            # ── Step 3 — Deterministic eligibility evaluation (free) ──
            eligibility = self.evaluate(profile)

            logger.info(
                "Eligibility evaluated",
                extra={
                    "eligible_count": len(eligibility.get("eligible", [])),
                    "partial_count": len(eligibility.get("partially_eligible", [])),
                    "ineligible_count": len(eligibility.get("ineligible", [])),
                    "eligible_ids": [
                        s.get("scheme_id") for s in eligibility.get("eligible", [])
                    ],
                },
            )

            # ── Step 4 — Template response generation ──
            response = self._build_template_response(
                eligibility, missing_fields, language
            )

            # ── Step 5 — Conditional LLM enhancement ──
            # Only call LLM if:
            #   - BEDROCK_ENABLED flag is true
            #   - Template response is below threshold length
            #   - Bedrock is available
            #   - Profile has enough data to justify the cost
            if (
                config.BEDROCK_ENABLED
                and len(response) < LLM_ENHANCEMENT_THRESHOLD
                and self.gateway.bedrock_available
                and not missing_fields
            ):
                eligible = eligibility.get("eligible", [])
                partial = eligibility.get("partially_eligible", [])
                if eligible or partial:
                    try:
                        enhanced = self.gateway.generate_explanation(
                            eligibility=eligibility,
                            profile=profile,
                            query=query,
                            language=language,
                        )
                        if enhanced and len(enhanced) > len(response):
                            response = enhanced
                    except Exception as e:
                        logger.warning(
                            "Bedrock enhancement failed — using template response",
                            extra={"error": str(e), "error_type": type(e).__name__},
                        )
            elif not config.BEDROCK_ENABLED:
                logger.info("Bedrock skipped — BEDROCK_ENABLED=false, using template response")

            # ── Step 6 — History management with guard ──
            history = self._get_history(session_id)
            history.append({"role": "user", "content": query})
            history.append({"role": "assistant", "content": response})
            self._trim_history(history)

            # ── Step 7 — Persist to DynamoDB (optional) ──
            if session_id and self.session_service:
                try:
                    self.session_service.update_session(
                        session_id=session_id,
                        updates={
                            "structured_profile": profile,
                            "evaluation_result": eligibility,
                            "conversation_state": {
                                "last_query": query,
                                "language": language,
                                "missing_fields": missing_fields,
                            },
                        },
                    )
                    logger.info(
                        "Session updated",
                        extra={"session_id": session_id},
                    )
                except Exception as e:
                    logger.warning(f"Session persistence failed: {e}")

            latency = (time.time() - start_time) * 1000

            # ── Build scheme + document info for frontend ──
            schemes = self._build_scheme_list(eligibility)
            documents = self._build_document_list(eligibility)

            logger.info(
                "Conversation processed successfully",
                extra={
                    "latency_ms": round(latency, 2),
                    "mode": "deterministic" if not self.gateway.bedrock_available else "hybrid",
                    "profile_fields": len(profile),
                    "eligible_count": len(eligibility.get("eligible", [])),
                },
            )

            result = {
                "profile": profile,
                "eligibility": eligibility,
                "response": response,
                "schemes": schemes,
                "documents": documents,
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

    def _build_template_response(
        self,
        eligibility: Dict[str, Any],
        missing_fields: List[str],
        language: str,
    ) -> str:
        """Build a template response from eligibility results."""
        eligible = eligibility.get("eligible", [])
        partial = eligibility.get("partially_eligible", [])

        parts = []

        # If we still need more info
        if missing_fields:
            field_names = {
                "occupation": "occupation/पेशा",
                "state": "state/राज्य",
                "income_range": "income/आय",
                "age_group": "age/उम्र",
                "gender": "gender/लिंग",
                "disability_status": "disability status",
                "caste_category": "caste category/जाति",
                "farmer_status": "farmer status",
                "student_status": "student status",
            }

            if language == "hi":
                needed = [field_names.get(f, f) for f in missing_fields[:3]]
                parts.append(f"कृपया मुझे और बताएं: {', '.join(needed)}।")
            elif language == "mr":
                needed = [field_names.get(f, f) for f in missing_fields[:3]]
                parts.append(f"कृपया मला अधिक सांगा: {', '.join(needed)}.")
            else:
                needed = [f.replace("_", " ") for f in missing_fields[:3]]
                parts.append(f"Please tell me more about your: {', '.join(needed)}.")

        # Show eligible schemes
        if eligible:
            scheme_names = [s.get("scheme_name", s.get("scheme_id", "")) for s in eligible]
            if language == "hi":
                parts.append(f"आप इन योजनाओं के लिए पात्र हैं: {', '.join(scheme_names)}।")
            elif language == "mr":
                parts.append(f"तुम्ही या योजनांसाठी पात्र आहात: {', '.join(scheme_names)}.")
            else:
                parts.append(f"Based on your profile, you are eligible for: {', '.join(scheme_names)}.")

            for scheme in eligible:
                benefit = scheme.get("benefit", "")
                url = scheme.get("source_url", "")
                if benefit:
                    parts.append(f"  • {scheme.get('scheme_name', '')}: {benefit}")
                if url:
                    parts.append(f"    Apply: {url}")

        # Show partially eligible schemes
        if partial:
            scheme_names = [s.get("scheme_name", s.get("scheme_id", "")) for s in partial]
            if language == "hi":
                parts.append(f"अधिक जानकारी के साथ आप इनके लिए भी पात्र हो सकते हैं: {', '.join(scheme_names)}।")
            elif language == "mr":
                parts.append(f"अधिक माहितीसह तुम्ही यासाठी पात्र होऊ शकता: {', '.join(scheme_names)}.")
            else:
                parts.append(f"With more details, you may also qualify for: {', '.join(scheme_names)}.")

        if not parts:
            if language == "hi":
                return "नमस्ते! मुझे अपने बारे में बताएं — आपकी उम्र, पेशा, आय और राज्य — और मैं आपके लिए सरकारी योजनाएं खोजूंगा।"
            elif language == "mr":
                return "नमस्कार! मला तुमच्याबद्दल सांगा — तुमचे वय, व्यवसाय, उत्पन्न आणि राज्य — आणि मी तुम्हाला सरकारी योजना शोधून देतो."
            return "Hello! Tell me about yourself — your age, occupation, income, and state — and I'll find government schemes you may be eligible for."

        return "\n".join(parts)

    def _build_scheme_list(self, eligibility: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build a frontend-friendly list of scheme cards."""
        schemes = []
        for status_key, status_label in [
            ("eligible", "eligible"),
            ("partially_eligible", "partial"),
        ]:
            for scheme in eligibility.get(status_key, []):
                schemes.append({
                    "id": scheme.get("scheme_id", ""),
                    "name": scheme.get("scheme_name", ""),
                    "status": status_label,
                    "benefit": scheme.get("benefit", ""),
                    "url": scheme.get("source_url", ""),
                    "documents": scheme.get("required_documents", []),
                })
        return schemes

    def _build_document_list(self, eligibility: Dict[str, Any]) -> List[str]:
        """Build a deduplicated list of required documents across all eligible schemes."""
        docs = set()
        for key in ["eligible", "partially_eligible"]:
            for scheme in eligibility.get(key, []):
                for doc in scheme.get("required_documents", []):
                    docs.add(doc)
        return sorted(docs)

