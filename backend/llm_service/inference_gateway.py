"""
Inference Gateway for SamvaadAI.

Lightweight gateway layer between orchestration and LLM service.

Responsibilities:
- Central entry point for all LLM requests
- In-memory query result caching (reduces duplicate Bedrock calls)
- Bedrock availability detection → automatic deterministic fallback
- Future location for request batching, routing, and model switching

Architectural guarantees:
- No business logic
- No eligibility decisions
- Cache is per-process (Lambda-safe)
- Thread-safe for concurrent requests (GIL-protected dict)
- Always returns valid results (never crashes on Bedrock failure)
"""

import logging
from typing import Dict, Any, Optional

from llm_service.llm_service import LLMService
from llm_service.bedrock_client import BedrockUnavailableError, is_available
from llm_service.profile_extractor import extract_profile
from llm_service.fallback_templates import (
    get_error_message,
    get_missing_info_message,
    get_fallback_explanation,
)

logger = logging.getLogger(__name__)


class InferenceGateway:
    """
    Central gateway for LLM inference requests.

    Wraps LLMService with caching and automatic Bedrock fallback.
    When Bedrock is unavailable, routes to deterministic profile extraction.
    """

    def __init__(self, llm_service: Optional[LLMService] = None):
        """
        Args:
            llm_service: LLMService instance (uses singleton Bedrock client).
        """
        self.llm_service = llm_service or LLMService()
        self._cache: Dict[int, Dict[str, Any]] = {}
        self._cache_hits = 0
        self._cache_misses = 0
        self._bedrock_available = is_available()
        logger.info(
            f"InferenceGateway initialized (bedrock_available={self._bedrock_available})"
        )

    def process(self, query: str, language: str = "en") -> Dict[str, Any]:
        """
        Process a query through the LLM pipeline with caching and fallback.

        If Bedrock is available: use LLM for profile extraction + response.
        If Bedrock is unavailable: use deterministic regex extraction + templates.

        Args:
            query: User's natural language input.
            language: Language code (en, hi, mr).

        Returns:
            Dict with profile, assistant_response, and missing_fields.
        """
        cache_key = hash((query, language))

        if cache_key in self._cache:
            self._cache_hits += 1
            logger.info(
                "[InferenceGateway] cache hit",
                extra={"cache_hits": self._cache_hits},
            )
            return self._cache[cache_key]

        self._cache_misses += 1

        # Route based on Bedrock availability
        if not self._bedrock_available:
            result = self._deterministic_process(query, language)
        else:
            try:
                result = self.llm_service.process_query(query, language)
            except BedrockUnavailableError:
                logger.warning(
                    "[InferenceGateway] Bedrock unavailable — switching to deterministic mode"
                )
                self._bedrock_available = False
                result = self._deterministic_process(query, language)

        self._cache[cache_key] = result

        logger.info(
            "[InferenceGateway] cache miss — processed",
            extra={
                "cache_misses": self._cache_misses,
                "cache_size": len(self._cache),
                "mode": "deterministic" if not self._bedrock_available else "llm",
            },
        )

        return result

    def _deterministic_process(
        self, query: str, language: str
    ) -> Dict[str, Any]:
        """
        Process query using deterministic regex extraction + template responses.
        No LLM calls. Sub-millisecond latency.
        """
        extraction = extract_profile(query, language)
        profile = extraction["profile"]
        missing_fields = extraction["missing_fields"]

        # Generate template response
        if missing_fields:
            first_missing = missing_fields[0]
            response = get_missing_info_message(first_missing, language)
        else:
            response = get_missing_info_message("general", language)

        return {
            "profile": profile,
            "assistant_response": response,
            "missing_fields": missing_fields,
        }

    def generate_explanation(
        self,
        eligibility: Dict[str, Any],
        profile: Dict[str, Any],
        query: str,
        language: str = "en",
    ) -> str:
        """
        Generate a natural language explanation of eligibility results.

        When Bedrock is available: uses LLM for rich explanation.
        When Bedrock is unavailable: uses template fallback.

        Args:
            eligibility: Eligibility evaluation result dict.
            profile: User profile dict.
            query: Original user query.
            language: Language code.

        Returns:
            Human-readable explanation string.
        """
        if not self._bedrock_available:
            return self._template_explanation(eligibility, language)

        try:
            return self.llm_service.generate_response(
                user_query=query,
                profile=profile,
                eligibility=eligibility,
                language=language,
            )
        except BedrockUnavailableError:
            self._bedrock_available = False
            return self._template_explanation(eligibility, language)

    def _template_explanation(
        self, eligibility: Dict[str, Any], language: str
    ) -> str:
        """Build a template-based explanation from eligibility results."""
        eligible = eligibility.get("eligible", [])
        partial = eligibility.get("partially_eligible", [])

        parts = []

        if eligible:
            scheme_names = [s.get("scheme_name", s.get("scheme_id", "")) for s in eligible]
            if language == "hi":
                parts.append(f"आप इन योजनाओं के लिए पात्र हैं: {', '.join(scheme_names)}।")
            elif language == "mr":
                parts.append(f"तुम्ही या योजनांसाठी पात्र आहात: {', '.join(scheme_names)}.")
            else:
                parts.append(f"You are eligible for: {', '.join(scheme_names)}.")

            for scheme in eligible:
                benefit = scheme.get("benefit", "")
                if benefit:
                    parts.append(f"  • {scheme.get('scheme_name', '')}: {benefit}")

        if partial:
            scheme_names = [s.get("scheme_name", s.get("scheme_id", "")) for s in partial]
            if language == "hi":
                parts.append(f"आप आंशिक रूप से इन योजनाओं के लिए पात्र हो सकते हैं: {', '.join(scheme_names)}।")
            elif language == "mr":
                parts.append(f"तुम्ही या योजनांसाठी अंशतः पात्र असू शकता: {', '.join(scheme_names)}.")
            else:
                parts.append(f"You may partially qualify for: {', '.join(scheme_names)}.")

        if not parts:
            return get_fallback_explanation({"status": "unknown"}, language)

        return "\n".join(parts)

    @property
    def bedrock_available(self) -> bool:
        """Check if Bedrock is currently available for this gateway."""
        return self._bedrock_available

    def clear_cache(self) -> None:
        """Clear the inference cache."""
        self._cache.clear()
        logger.info("[InferenceGateway] cache cleared")

    @property
    def cache_stats(self) -> Dict[str, int]:
        """Return cache statistics."""
        return {
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "size": len(self._cache),
        }

