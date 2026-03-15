"""
Scheme Explainability Service for SamvaadAI.

Generates deterministic explanations for why users qualify for government schemes.
Analyzes scheme eligibility rules against user profile to create human-readable explanations.

Architectural Guarantees:
- Deterministic explanation generation (no LLMs)
- Performance under 5ms per scheme
- O(N) complexity relative to rule count
- Safe profile rule matching
- Multilingual support (English, Hindi, Marathi)
"""

import time
from typing import Dict, Any, List, Optional
from core.logging_config import logger


class SchemeExplainabilityService:
    """
    Service for generating explanations of scheme eligibility.
    
    Analyzes scheme eligibility criteria against user profile and generates
    human-readable bullet points explaining why the user qualifies.
    """
    
    def __init__(self):
        """Initialize the explainability service."""
        self._field_explanations = self._build_field_explanation_templates()
        logger.info("SchemeExplainabilityService initialized")
    
    def _build_field_explanation_templates(self) -> Dict[str, Dict[str, str]]:
        """
        Build templates for explaining field matches in multiple languages.
        
        Returns:
            Dict mapping field names to language-specific explanation templates
        """
        return {
            "occupation": {
                "en": "You work as a {value}",
                "hi": "आप {value} के रूप में काम करते हैं",
                "mr": "तुम्ही {value} म्हणून काम करता"
            },
            "farmer_status": {
                "en": "You are classified as a {value} farmer",
                "hi": "आप {value} किसान के रूप में वर्गीकृत हैं",
                "mr": "तुम्ही {value} शेतकरी म्हणून वर्गीकृत आहात"
            },
            "state": {
                "en": "You live in {value}",
                "hi": "आप {value} में रहते हैं", 
                "mr": "तुम्ही {value} मध्ये राहता"
            },
            "income_range": {
                "en": "Your income falls within the {value} range",
                "hi": "आपकी आय {value} सीमा के भीतर है",
                "mr": "तुमचे उत्पन्न {value} श्रेणीत येते"
            },
            "age_group": {
                "en": "You belong to the {value} age group",
                "hi": "आप {value} आयु वर्ग से संबंधित हैं",
                "mr": "तुम्ही {value} वयोगटातील आहात"
            },
            "gender": {
                "en": "You are {value}",
                "hi": "आप {value} हैं",
                "mr": "तुम्ही {value} आहात"
            },
            "caste_category": {
                "en": "You belong to the {value} category",
                "hi": "आप {value} श्रेणी से संबंधित हैं",
                "mr": "तुम्ही {value} श्रेणीतील आहात"
            },
            "student_status": {
                "en": "You are currently a {value} student",
                "hi": "आप वर्तमान में {value} छात्र हैं",
                "mr": "तुम्ही सध्या {value} विद्यार्थी आहात"
            },
            "disability_status": {
                "en": "Your disability status: {value}",
                "hi": "आपकी विकलांगता स्थिति: {value}",
                "mr": "तुमची अपंगत्व स्थिती: {value}"
            },
            "education_level": {
                "en": "Your education level is {value}",
                "hi": "आपका शिक्षा स्तर {value} है",
                "mr": "तुमची शिक्षण पातळी {value} आहे"
            },
            "land_ownership": {
                "en": "Land ownership status: {value}",
                "hi": "भूमि स्वामित्व स्थिति: {value}",
                "mr": "जमीन मालकी स्थिती: {value}"
            },
            "bank_account": {
                "en": "You have a bank account" if True else "You don't have a bank account",
                "hi": "आपका बैंक खाता है" if True else "आपका बैंक खाता नहीं है",
                "mr": "तुमचे बँक खाते आहे" if True else "तुमचे बँक खाते नाही"
            },
            "bpl_status": {
                "en": "You have a BPL card" if True else "You don't have a BPL card",
                "hi": "आपके पास बीपीएल कार्ड है" if True else "आपके पास बीपीएल कार्ड नहीं है",
                "mr": "तुमच्याकडे बीपीएल कार्ड आहे" if True else "तुमच्याकडे बीपीएल कार्ड नाही"
            },
            "urban_rural": {
                "en": "You live in an {value} area",
                "hi": "आप {value} क्षेत्र में रहते हैं",
                "mr": "तुम्ही {value} भागात राहता"
            },
            "family_size": {
                "en": "Your family has {value} members",
                "hi": "आपके परिवार में {value} सदस्य हैं",
                "mr": "तुमच्या कुटुंबात {value} सदस्य आहेत"
            }
        }
    
    def generate_explanation(
        self,
        profile: Dict[str, Any],
        scheme: Dict[str, Any],
        language: str = "en"
    ) -> List[str]:
        """
        Generate explanation points for why a user qualifies for a scheme.
        
        Args:
            profile: User profile dictionary
            scheme: Scheme dictionary with eligibility criteria
            language: Language code (en, hi, mr)
            
        Returns:
            List of explanation bullet points
        """
        start_time = time.time()
        
        try:
            scheme_id = scheme.get("scheme_id", "")
            criteria = scheme.get("eligibility_criteria", [])
            
            if not criteria:
                logger.warning(f"No eligibility criteria for scheme {scheme_id}")
                return []
            
            explanation_points = []
            rules_matched = 0
            rules_checked = len(criteria)
            
            for rule in criteria:
                field = rule.get("field", "")
                operator = rule.get("operator", "")
                expected = rule.get("value")
                rule_explanation = rule.get("explanation", "")
                
                # Get actual value from profile
                actual_value = profile.get(field)
                
                # Check if rule matches
                if self._rule_matches(actual_value, operator, expected):
                    rules_matched += 1
                    
                    # Generate explanation point
                    explanation = self._generate_explanation_point(
                        field, actual_value, operator, expected, rule_explanation, language
                    )
                    
                    if explanation:
                        explanation_points.append(explanation)
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Log metrics
            logger.info(
                f"Explanation generated for scheme {scheme_id}",
                extra={
                    "scheme_id": scheme_id,
                    "rules_matched": rules_matched,
                    "rules_checked": rules_checked,
                    "execution_time_ms": round(execution_time_ms, 2),
                    "explanation_points": len(explanation_points)
                }
            )
            
            return explanation_points
            
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Explanation generation failed for scheme {scheme.get('scheme_id', '')}",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "execution_time_ms": round(execution_time_ms, 2)
                },
                exc_info=True
            )
            return []
    
    def _rule_matches(self, actual: Any, operator: str, expected: Any) -> bool:
        """
        Check if a profile value matches a scheme rule.
        
        Uses the same logic as the eligibility engine's RuleParser.
        
        Args:
            actual: Actual value from user profile
            operator: Comparison operator
            expected: Expected value from scheme rule
            
        Returns:
            True if rule matches, False otherwise
        """
        if actual is None:
            return False
        
        if operator == "equals":
            return str(actual).lower() == str(expected).lower()
        
        if operator == "not_equals":
            return str(actual).lower() != str(expected).lower()
        
        if operator == "greater_than":
            return self._to_float(actual) > self._to_float(expected)
        
        if operator == "less_than":
            return self._to_float(actual) < self._to_float(expected)
        
        if operator == "greater_than_or_equals":
            return self._to_float(actual) >= self._to_float(expected)
        
        if operator == "less_than_or_equals":
            return self._to_float(actual) <= self._to_float(expected)
        
        if operator == "between":
            if isinstance(expected, list) and len(expected) == 2:
                val = self._to_float(actual)
                return self._to_float(expected[0]) <= val <= self._to_float(expected[1])
            return False
        
        if operator == "in":
            if isinstance(expected, list):
                return str(actual).lower() in [str(v).lower() for v in expected]
            return str(actual).lower() == str(expected).lower()
        
        if operator == "not_in":
            if isinstance(expected, list):
                return str(actual).lower() not in [str(v).lower() for v in expected]
            return str(actual).lower() != str(expected).lower()
        
        if operator == "contains":
            return str(expected).lower() in str(actual).lower()
        
        return False
    
    def _to_float(self, value: Any) -> float:
        """Convert value to float for numeric comparisons."""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = value.replace(",", "").replace("₹", "").replace("Rs", "").strip()
            try:
                return float(cleaned)
            except ValueError:
                return 0.0
        return 0.0
    
    def _generate_explanation_point(
        self,
        field: str,
        actual_value: Any,
        operator: str,
        expected: Any,
        rule_explanation: str,
        language: str
    ) -> Optional[str]:
        """
        Generate a human-readable explanation point for a matched rule.
        
        Args:
            field: Profile field name
            actual_value: Actual value from profile
            operator: Comparison operator
            expected: Expected value from rule
            rule_explanation: Rule explanation from scheme
            language: Language code
            
        Returns:
            Formatted explanation string or None
        """
        # Use rule explanation if available and detailed
        if rule_explanation and len(rule_explanation) > 10:
            return f"✔ {rule_explanation}"
        
        # Generate explanation from field templates
        if field in self._field_explanations:
            template = self._field_explanations[field].get(language, 
                                                         self._field_explanations[field]["en"])
            
            # Handle boolean fields specially
            if field in ["bank_account", "bpl_status"]:
                if actual_value:
                    if language == "hi":
                        return f"✔ आपके पास {self._get_field_name_hindi(field)} है"
                    elif language == "mr":
                        return f"✔ तुमच्याकडे {self._get_field_name_marathi(field)} आहे"
                    else:
                        return f"✔ You have a {field.replace('_', ' ')}"
                else:
                    return None  # Don't explain negative conditions
            
            # Format template with actual value
            try:
                formatted = template.format(value=actual_value)
                return f"✔ {formatted}"
            except (KeyError, ValueError):
                pass
        
        # Fallback to generic explanation
        if language == "hi":
            return f"✔ आपका {field}: {actual_value}"
        elif language == "mr":
            return f"✔ तुमचा {field}: {actual_value}"
        else:
            return f"✔ Your {field.replace('_', ' ')}: {actual_value}"
    
    def _get_field_name_hindi(self, field: str) -> str:
        """Get Hindi field names for boolean fields."""
        field_names = {
            "bank_account": "बैंक खाता",
            "bpl_status": "बीपीएल कार्ड"
        }
        return field_names.get(field, field)
    
    def _get_field_name_marathi(self, field: str) -> str:
        """Get Marathi field names for boolean fields."""
        field_names = {
            "bank_account": "बँक खाते",
            "bpl_status": "बीपीएल कार्ड"
        }
        return field_names.get(field, field)


# Global service instance
explainability_service = SchemeExplainabilityService()