"""
LLM Service Module for SamvaadAI.

This module provides intent extraction and explanation generation using
Amazon Bedrock (Anthropic Claude). It is completely stateless and includes
safety guardrails to prevent LLM from making eligibility decisions.
"""

import json
import logging
import re
import time
from typing import Dict, Optional, Any
from pathlib import Path

from llm_service.bedrock_client import BedrockClient, get_client
from llm_service.fallback_templates import (
    get_default_profile,
    get_error_message,
    get_timeout_message,
    get_fallback_explanation
)
from llm_service.config import SUPPORTED_LANGUAGES, LANGUAGE_NAMES

logger = logging.getLogger(__name__)

# Get prompts directory
PROMPTS_DIR = Path(__file__).parent / "prompts"
INTENT_PROMPT_PATH = PROMPTS_DIR / "intent_prompt.txt"
EXPLANATION_PROMPT_PATH = PROMPTS_DIR / "explanation_prompt.txt"


class LLMService:
    """
    Main LLM service for intent extraction and explanation generation.
    
    This service is stateless and handles all LLM interactions with
    proper error handling and fallback mechanisms.
    """
    
    def __init__(self, bedrock_client: Optional[BedrockClient] = None):
        """
        Initialize LLM service.

        Args:
            bedrock_client: Optional BedrockClient instance.
                            Uses module-level singleton if None.
        """
        self.client = bedrock_client or get_client()
        self._intent_prompt_template = self._load_prompt(INTENT_PROMPT_PATH)
        self._explanation_prompt_template = self._load_prompt(EXPLANATION_PROMPT_PATH)
    
    @staticmethod
    def _load_prompt(file_path: Path) -> str:
        """
        Load prompt template from file.
        
        Args:
            file_path: Path to prompt file
            
        Returns:
            Prompt template string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Prompt file not found: {file_path}")
            return ""
        except Exception as e:
            logger.error(f"Error loading prompt file {file_path}: {e}")
            return ""
    
    def _validate_json_output(self, text: str) -> bool:
        """
        Validate that output is valid JSON.
        
        Args:
            text: Text to validate
            
        Returns:
            True if valid JSON, False otherwise
        """
        try:
            json.loads(text)
            return True
        except json.JSONDecodeError:
            return False
    
    def _extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from LLM response, handling markdown code blocks.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed JSON dict or None if extraction fails
        """
        # Remove markdown code blocks if present
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            response = json_match.group(1)
        
        # Try to find JSON object in response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            response = json_match.group(0)
        
        try:
            parsed = json.loads(response.strip())
            return parsed
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from response: {e}")
            return None
    
    def _validate_profile_schema(self, profile: Dict[str, Any]) -> bool:
        """
        Validate that profile matches expected schema.
        
        Args:
            profile: Profile dict to validate
            
        Returns:
            True if valid schema, False otherwise
        """
        required_keys = ["age", "occupation", "income_band", "location"]
        if not all(key in profile for key in required_keys):
            return False
        
        if not isinstance(profile.get("location"), dict):
            return False
        
        if "state" not in profile["location"]:
            return False
        
        # Validate types
        if profile["age"] is not None and not isinstance(profile["age"], int):
            return False
        
        if profile["occupation"] is not None and not isinstance(profile["occupation"], str):
            return False
        
        if profile["income_band"] is not None and not isinstance(profile["income_band"], str):
            return False
        
        if profile["location"]["state"] is not None and not isinstance(profile["location"]["state"], str):
            return False
        
        return True
    
    def _check_eligibility_guardrail(self, text: str) -> bool:
        """
        Safety guardrail: Check if LLM tried to make eligibility decision.
        
        Args:
            text: Text to check
            
        Returns:
            True if safe (no eligibility decision), False if unsafe
        """
        # Keywords that indicate eligibility decision
        unsafe_patterns = [
            r'\b(eligible|not eligible|ineligible|qualify|disqualify)\b',
            r'\b(पात्र|अपात्र|योग्य|अयोग्य)\b',  # Hindi
            r'\b(पात्र|अपात्र|योग्य|अयोग्य)\b',  # Marathi (similar script)
        ]
        
        text_lower = text.lower()
        for pattern in unsafe_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"Guardrail triggered: Eligibility decision detected in text")
                return False
        
        return True
    
    def extract_user_profile(
        self,
        user_text: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Extract structured user profile from natural language text.
        
        This function uses LLM to extract age, occupation, income, and location
        from user input in English, Hindi, or Marathi.
        
        Args:
            user_text: User input text (any language)
            language: Language code (en, hi, mr) - used for fallback messages only
            
        Returns:
            Dict with structure:
            {
                "age": int | None,
                "occupation": str | None,
                "income_band": str | None,
                "location": {"state": str | None}
            }
        """
        if language not in SUPPORTED_LANGUAGES:
            logger.warning(f"Unsupported language {language}, defaulting to English")
            language = "en"
        
        # Prepare prompt
        prompt = self._intent_prompt_template.format(user_text=user_text)
        
        try:
            logger.info("[LLM] intent_extraction started")
            t0 = time.perf_counter()

            # Call Bedrock
            response = self.client.invoke_model(prompt)
            latency = time.perf_counter() - t0
            logger.info(f"[LLM_LATENCY] intent_extraction={latency:.2f}s")
            
            # Extract JSON from response
            profile = self._extract_json_from_response(response)
            
            if profile is None:
                logger.warning("[LLM] fallback activated: invalid JSON from intent extraction")
                return get_default_profile(language)
            
            # Validate schema
            if not self._validate_profile_schema(profile):
                logger.warning("[LLM] fallback activated: invalid profile schema")
                return get_default_profile(language)

            # Safety guardrail: Check for eligibility decisions
            if not self._check_eligibility_guardrail(response):
                logger.warning("[LLM] fallback activated: guardrail triggered (eligibility decision)")
                return get_default_profile(language)

            logger.info("[LLM] intent_extraction completed")
            return profile
            
        except TimeoutError:
            logger.error("[LLM] Bedrock failure: timeout during intent extraction")
            return get_default_profile(language)
        except Exception as e:
            logger.error(f"[LLM] Bedrock failure during intent extraction: {e}")
            return get_default_profile(language)
    
    def generate_explanation(
        self,
        rule_output: Dict[str, Any],
        language: str = "en"
    ) -> str:
        """
        Generate human-friendly explanation from rule engine output.
        
        This function converts technical rule engine results into simple,
        grade-6 reading level explanations in the requested language.
        
        IMPORTANT: This function NEVER modifies the eligibility decision.
        It only explains it.
        
        Args:
            rule_output: Rule engine output dict with keys:
                - scheme: str (scheme name)
                - status: str ("eligible" or "not_eligible")
                - reason: str (technical reason)
            language: Language code (en, hi, mr)
            
        Returns:
            Simple explanation string in requested language
        """
        if language not in SUPPORTED_LANGUAGES:
            logger.warning(f"Unsupported language {language}, defaulting to English")
            language = "en"
        
        # Validate rule_output structure
        if not isinstance(rule_output, dict):
            logger.error("Invalid rule_output: not a dict")
            return get_fallback_explanation({"status": "unknown"}, language)
        
        if "status" not in rule_output:
            logger.error("Invalid rule_output: missing 'status' key")
            return get_fallback_explanation({"status": "unknown"}, language)
        
        # Safety guardrail: Ensure we're not modifying status
        original_status = rule_output.get("status")
        
        # Prepare prompt
        language_name = LANGUAGE_NAMES.get(language, "English")
        rule_output_str = json.dumps(rule_output, indent=2)
        prompt = self._explanation_prompt_template.format(
            language=language_name,
            rule_output=rule_output_str
        )
        
        try:
            logger.info("[LLM] explanation_generation started")
            t0 = time.perf_counter()

            # Call Bedrock
            response = self.client.invoke_model(prompt)
            latency = time.perf_counter() - t0
            logger.info(f"[LLM_LATENCY] explanation_generation={latency:.2f}s")

            # Clean response
            explanation = response.strip()
            
            # Safety guardrail: Check if explanation changed the status
            # This is a simple check - in production, you might want more sophisticated validation
            if not self._check_eligibility_guardrail(explanation):
                logger.warning("[LLM] fallback activated: guardrail triggered (eligibility in explanation)")
                return get_fallback_explanation(rule_output, language)

            # Verify status wasn't changed (basic check)
            if original_status == "eligible" and "not eligible" in explanation.lower():
                logger.warning("[LLM] fallback activated: explanation contradicts status")
                return get_fallback_explanation(rule_output, language)

            logger.info("[LLM] explanation_generation completed")
            return explanation
            
        except TimeoutError:
            logger.error("[LLM] Bedrock failure: timeout during explanation generation")
            return get_timeout_message(language)
        except Exception as e:
            logger.error(f"[LLM] Bedrock failure during explanation generation: {e}")
            return get_fallback_explanation(rule_output, language)


    def generate_response(
        self,
        user_query: str,
        profile: Dict[str, Any],
        eligibility: Dict[str, Any],
        language: str = "en",
    ) -> str:
        """
        Generate a natural language response summarizing eligibility results.

        Uses template formatting for standard cases and LLM explanation
        only when complex results need simplification.

        This method NEVER modifies the eligibility decision.

        Args:
            user_query: Original user query.
            profile: Extracted user profile dict.
            eligibility: Eligibility evaluation result dict with keys:
                eligible, partially_eligible, ineligible.
            language: Language code (en, hi, mr).

        Returns:
            Human-readable response string.
        """
        if language not in SUPPORTED_LANGUAGES:
            language = "en"

        eligible = eligibility.get("eligible", [])
        partial = eligibility.get("partially_eligible", [])
        ineligible = eligibility.get("ineligible", [])

        # Build a combined rule_output for explanation
        summary_parts = []

        for scheme in eligible:
            summary_parts.append(
                f"- {scheme.get('scheme_name', scheme.get('scheme_id'))}: Eligible"
            )

        for scheme in partial:
            guidance = scheme.get("guidance", "")
            summary_parts.append(
                f"- {scheme.get('scheme_name', scheme.get('scheme_id'))}: "
                f"Partially eligible ({guidance})"
            )

        for scheme in ineligible:
            reasons = ", ".join(scheme.get("reasons", []))
            summary_parts.append(
                f"- {scheme.get('scheme_name', scheme.get('scheme_id'))}: "
                f"Not eligible ({reasons})"
            )

        if not summary_parts:
            return get_fallback_explanation({"status": "unknown"}, language)

        summary_text = "\n".join(summary_parts)

        # Use LLM to convert technical summary into simple language
        rule_output = {
            "summary": summary_text,
            "status": "eligible" if eligible else "partially_eligible" if partial else "not_eligible",
            "eligible_count": len(eligible),
            "partial_count": len(partial),
            "ineligible_count": len(ineligible),
        }

        try:
            language_name = LANGUAGE_NAMES.get(language, "English")
            prompt = self._explanation_prompt_template.format(
                language=language_name,
                rule_output=json.dumps(rule_output, indent=2)
            )

            logger.info("[LLM] response_generation started")
            t0 = time.perf_counter()

            response = self.client.invoke_model(prompt)
            latency = time.perf_counter() - t0
            logger.info(f"[LLM_LATENCY] response_generation={latency:.2f}s")

            explanation = response.strip()

            if not self._check_eligibility_guardrail(explanation):
                logger.warning("[LLM] guardrail triggered in response generation")
                return get_fallback_explanation(rule_output, language)

            return explanation

        except Exception as e:
            logger.error(f"[LLM] response generation failed: {e}")
            return get_fallback_explanation(rule_output, language)
