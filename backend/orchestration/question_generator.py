"""
Question Generator for SamvaadAI.

Generates structured questions with quick-select options for missing profile fields.
Supports multilingual questions and voice-optimized option labels.

Design principles:
- One question at a time (avoid overwhelming users)
- Priority-based ordering (high-impact fields first)
- Voice-friendly options (short, speakable labels)
- Progressive disclosure (skip irrelevant questions)
"""

from typing import Dict, Any, List, Optional


class QuestionGenerator:
    """Generate structured questions for profile data collection."""

    # Priority order for asking questions (high impact → low impact)
    QUESTION_PRIORITY = [
        "state",           # Determines scheme availability
        "occupation",      # Major eligibility factor
        "age_group",       # Many schemes are age-gated
        "income_range",    # Economic eligibility
        "gender",          # Gender-specific schemes
        "caste_category",  # Reservation-based schemes
        "farmer_status",   # Agricultural schemes
        "student_status",  # Education schemes
        "disability_status",  # Disability schemes
    ]

    # Question templates with multilingual support
    QUESTION_TEMPLATES = {
        "state": {
            "type": "dropdown",
            "text": {
                "en": "Which state are you from?",
                "hi": "आप किस राज्य से हैं?",
                "mr": "तुम्ही कोणत्या राज्यातून आहात?",
            },
            "options": [
                {"label": {"en": "Maharashtra", "hi": "महाराष्ट्र", "mr": "महाराष्ट्र"}, "value": "Maharashtra"},
                {"label": {"en": "Delhi", "hi": "दिल्ली", "mr": "दिल्ली"}, "value": "Delhi"},
                {"label": {"en": "Karnataka", "hi": "कर्नाटक", "mr": "कर्नाटक"}, "value": "Karnataka"},
                {"label": {"en": "Tamil Nadu", "hi": "तमिलनाडु", "mr": "तामिळनाडू"}, "value": "Tamil Nadu"},
                {"label": {"en": "Gujarat", "hi": "गुजरात", "mr": "गुजरात"}, "value": "Gujarat"},
                {"label": {"en": "Uttar Pradesh", "hi": "उत्तर प्रदेश", "mr": "उत्तर प्रदेश"}, "value": "Uttar Pradesh"},
                {"label": {"en": "Other", "hi": "अन्य", "mr": "इतर"}, "value": "other"},
            ],
            "allow_text_input": True,
        },
        "occupation": {
            "type": "chips",
            "text": {
                "en": "What is your occupation?",
                "hi": "आपका पेशा क्या है?",
                "mr": "तुमचा व्यवसाय काय आहे?",
            },
            "options": [
                {"label": {"en": "Farmer", "hi": "किसान", "mr": "शेतकरी"}, "value": "farmer"},
                {"label": {"en": "Student", "hi": "छात्र", "mr": "विद्यार्थी"}, "value": "student"},
                {"label": {"en": "Business", "hi": "व्यापारी", "mr": "व्यवसायी"}, "value": "business"},
                {"label": {"en": "Labour", "hi": "मजदूर", "mr": "कामगार"}, "value": "labourer"},
                {"label": {"en": "Unemployed", "hi": "बेरोजगार", "mr": "बेरोजगार"}, "value": "unemployed"},
                {"label": {"en": "Other", "hi": "अन्य", "mr": "इतर"}, "value": "other"},
            ],
            "allow_text_input": True,
        },
        "age_group": {
            "type": "chips",
            "text": {
                "en": "What is your age group?",
                "hi": "आपकी आयु वर्ग क्या है?",
                "mr": "तुमचा वयोगट काय आहे?",
            },
            "options": [
                {"label": {"en": "18-25 years", "hi": "18-25 वर्ष", "mr": "18-25 वर्षे"}, "value": "18-25"},
                {"label": {"en": "26-35 years", "hi": "26-35 वर्ष", "mr": "26-35 वर्षे"}, "value": "26-35"},
                {"label": {"en": "36-45 years", "hi": "36-45 वर्ष", "mr": "36-45 वर्षे"}, "value": "36-45"},
                {"label": {"en": "46-60 years", "hi": "46-60 वर्ष", "mr": "46-60 वर्षे"}, "value": "46-60"},
                {"label": {"en": "Above 60", "hi": "60 से अधिक", "mr": "60 पेक्षा जास्त"}, "value": "60+"},
            ],
            "allow_text_input": True,
        },
        "income_range": {
            "type": "chips",
            "text": {
                "en": "What is your annual income range?",
                "hi": "आपकी वार्षिक आय सीमा क्या है?",
                "mr": "तुमची वार्षिक उत्पन्न श्रेणी काय आहे?",
            },
            "options": [
                {"label": {"en": "Below ₹1 lakh", "hi": "₹1 लाख से कम", "mr": "₹1 लाखापेक्षा कमी"}, "value": "below_1l"},
                {"label": {"en": "₹1-2.5 lakh", "hi": "₹1-2.5 लाख", "mr": "₹1-2.5 लाख"}, "value": "1l_to_2.5l"},
                {"label": {"en": "₹2.5-5 lakh", "hi": "₹2.5-5 लाख", "mr": "₹2.5-5 लाख"}, "value": "2.5l_to_5l"},
                {"label": {"en": "₹5-10 lakh", "hi": "₹5-10 लाख", "mr": "₹5-10 लाख"}, "value": "5l_to_10l"},
                {"label": {"en": "Above ₹10 lakh", "hi": "₹10 लाख से अधिक", "mr": "₹10 लाखापेक्षा जास्त"}, "value": "above_10l"},
            ],
            "allow_text_input": True,
        },
        "gender": {
            "type": "chips",
            "text": {
                "en": "What is your gender?",
                "hi": "आपका लिंग क्या है?",
                "mr": "तुमचे लिंग काय आहे?",
            },
            "options": [
                {"label": {"en": "Male", "hi": "पुरुष", "mr": "पुरुष"}, "value": "male"},
                {"label": {"en": "Female", "hi": "महिला", "mr": "महिला"}, "value": "female"},
                {"label": {"en": "Prefer not to say", "hi": "नहीं बताना चाहते", "mr": "सांगू इच्छित नाही"}, "value": "other"},
            ],
            "allow_text_input": False,
        },
        "caste_category": {
            "type": "chips",
            "text": {
                "en": "What is your caste category?",
                "hi": "आपकी जाति श्रेणी क्या है?",
                "mr": "तुमची जात श्रेणी काय आहे?",
            },
            "options": [
                {"label": {"en": "General", "hi": "सामान्य", "mr": "सामान्य"}, "value": "general"},
                {"label": {"en": "OBC", "hi": "ओबीसी", "mr": "ओबीसी"}, "value": "obc"},
                {"label": {"en": "SC", "hi": "एससी", "mr": "एससी"}, "value": "sc"},
                {"label": {"en": "ST", "hi": "एसटी", "mr": "एसटी"}, "value": "st"},
                {"label": {"en": "EWS", "hi": "ईडब्ल्यूएस", "mr": "ईडब्ल्यूएस"}, "value": "ews"},
            ],
            "allow_text_input": False,
        },
        "farmer_status": {
            "type": "binary",
            "text": {
                "en": "Are you a farmer?",
                "hi": "क्या आप किसान हैं?",
                "mr": "तुम्ही शेतकरी आहात का?",
            },
            "options": [
                {"label": {"en": "Yes", "hi": "हाँ", "mr": "होय"}, "value": True},
                {"label": {"en": "No", "hi": "नहीं", "mr": "नाही"}, "value": False},
            ],
            "allow_text_input": False,
        },
        "student_status": {
            "type": "binary",
            "text": {
                "en": "Are you a student?",
                "hi": "क्या आप छात्र हैं?",
                "mr": "तुम्ही विद्यार्थी आहात का?",
            },
            "options": [
                {"label": {"en": "Yes", "hi": "हाँ", "mr": "होय"}, "value": True},
                {"label": {"en": "No", "hi": "नहीं", "mr": "नाही"}, "value": False},
            ],
            "allow_text_input": False,
        },
        "disability_status": {
            "type": "binary",
            "text": {
                "en": "Do you have any disability?",
                "hi": "क्या आपको कोई विकलांगता है?",
                "mr": "तुम्हाला काही अपंगत्व आहे का?",
            },
            "options": [
                {"label": {"en": "Yes", "hi": "हाँ", "mr": "होय"}, "value": True},
                {"label": {"en": "No", "hi": "नहीं", "mr": "नाही"}, "value": False},
            ],
            "allow_text_input": False,
        },
    }

    def get_next_question(
        self,
        missing_fields: List[str],
        profile: Dict[str, Any],
        language: str = "en",
    ) -> Optional[Dict[str, Any]]:
        """
        Get the next highest-priority question to ask.

        Args:
            missing_fields: List of fields not yet collected.
            profile: Current user profile (for smart skipping).
            language: Language code (en, hi, mr).

        Returns:
            Structured question dict or None if no questions needed.
        """
        # Smart skipping logic
        filtered_fields = self._filter_relevant_fields(missing_fields, profile)

        # Get highest priority field
        for field in self.QUESTION_PRIORITY:
            if field in filtered_fields:
                return self._build_question(field, language)

        return None

    def _filter_relevant_fields(
        self,
        missing_fields: List[str],
        profile: Dict[str, Any],
    ) -> List[str]:
        """
        Filter out irrelevant questions based on user profile.

        Enhanced smart skipping rules:
        - If occupation is "farmer", skip farmer_status
        - If occupation is "student", skip student_status
        - If age > 30, skip student_status
        - If occupation is known and not student, skip student_status
        - If income > 5L, likely general category, deprioritize caste_category
        - If occupation not agriculture-related, deprioritize farmer_status
        - If no disability mentioned in conversation, deprioritize disability_status
        """
        filtered = list(missing_fields)

        # Skip farmer_status if occupation is already "farmer"
        if profile.get("occupation") == "farmer" and "farmer_status" in filtered:
            filtered.remove("farmer_status")

        # Skip student_status if occupation is already "student"
        if profile.get("occupation") == "student" and "student_status" in filtered:
            filtered.remove("student_status")

        # Skip student_status if age > 30
        age_group = profile.get("age_group", "")
        if age_group in ["36-45", "46-60", "60+"] and "student_status" in filtered:
            filtered.remove("student_status")

        # Skip student_status if occupation is known and not student
        occupation = profile.get("occupation")
        if (
            occupation
            and occupation != "student"
            and "student_status" in filtered
        ):
            filtered.remove("student_status")
        
        # Deprioritize farmer_status if occupation is not agriculture-related
        if occupation and occupation not in ["farmer", "labourer", "unemployed"]:
            if "farmer_status" in filtered:
                # Move to end of list (lowest priority)
                filtered.remove("farmer_status")
                filtered.append("farmer_status")
        
        # Deprioritize caste_category if income is high (likely general category)
        income_range = profile.get("income_range", "")
        if income_range in ["5l_to_10l", "above_10l"] and "caste_category" in filtered:
            # Move to end of list
            filtered.remove("caste_category")
            filtered.append("caste_category")
        
        # Deprioritize disability_status (ask only if relevant)
        if "disability_status" in filtered:
            # Move to end of list - ask last
            filtered.remove("disability_status")
            filtered.append("disability_status")

        return filtered

    def _build_question(self, field: str, language: str) -> Dict[str, Any]:
        """
        Build a structured question object for a field.

        Args:
            field: Profile field name.
            language: Language code.

        Returns:
            Question dict with text, options, type, skip option, etc.
        """
        template = self.QUESTION_TEMPLATES.get(field)
        if not template:
            return None

        # Build question with skip option
        question = {
            "field": field,
            "type": template["type"],
            "text": template["text"].get(language, template["text"]["en"]),
            "options": [
                {
                    "label": opt["label"].get(language, opt["label"]["en"]),
                    "value": opt["value"],
                }
                for opt in template["options"]
            ],
            "allow_text_input": template.get("allow_text_input", False),
            "allow_skip": True,  # All questions can be skipped
            "skip_label": self._get_skip_label(language),
            "voice_prompt": self._build_voice_prompt(template, language),
        }
        
        return question
    
    def _get_skip_label(self, language: str) -> str:
        """Get localized skip button label."""
        skip_labels = {
            "en": "Skip",
            "hi": "छोड़ें",
            "mr": "वगळा",
        }
        return skip_labels.get(language, "Skip")

    def _build_voice_prompt(self, template: Dict, language: str) -> str:
        """
        Build a voice-friendly prompt with option hints.

        Example: "What is your age group? You can say 18 to 25, 26 to 35, and so on."
        """
        text = template["text"].get(language, template["text"]["en"])
        options = template["options"]

        if template["type"] == "binary":
            # For yes/no questions
            yes_label = options[0]["label"].get(language, "Yes")
            no_label = options[1]["label"].get(language, "No")
            return f"{text} You can say {yes_label} or {no_label}."

        # For multi-option questions, list first 3 options
        option_hints = [
            opt["label"].get(language, opt["label"]["en"])
            for opt in options[:3]
        ]
        hints_text = ", ".join(option_hints)

        if language == "hi":
            return f"{text} आप कह सकते हैं {hints_text}, और इसी तरह।"
        elif language == "mr":
            return f"{text} तुम्ही म्हणू शकता {hints_text}, आणि असेच."
        else:
            return f"{text} You can say {hints_text}, and so on."
