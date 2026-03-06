"""
Fallback Templates Module.

Provides template responses when LLM service fails or times out.
These templates ensure the system remains functional even when
Bedrock is unavailable.
"""

from typing import Dict, Optional
from llm_service.config import SUPPORTED_LANGUAGES, LANGUAGE_NAMES


# Template responses for missing information
MISSING_INFO_TEMPLATES: Dict[str, Dict[str, str]] = {
    "en": {
        "age": "Could you please tell me your age?",
        "occupation": "What is your occupation?",
        "income": "What is your approximate annual income?",
        "location": "Which state do you live in?",
        "general": "I need a bit more information to help you better. Could you provide your age, occupation, income, and location?"
    },
    "hi": {
        "age": "कृपया अपनी उम्र बताएं?",
        "occupation": "आपका व्यवसाय क्या है?",
        "income": "आपकी लगभग वार्षिक आय क्या है?",
        "location": "आप किस राज्य में रहते हैं?",
        "general": "मुझे आपकी बेहतर मदद करने के लिए थोड़ी और जानकारी चाहिए। कृपया अपनी उम्र, व्यवसाय, आय और स्थान बताएं।"
    },
    "mr": {
        "age": "कृपया तुमचे वय सांगा?",
        "occupation": "तुमचे व्यवसाय काय आहे?",
        "income": "तुमचे अंदाजे वार्षिक उत्पन्न किती आहे?",
        "location": "तुम्ही कोणत्या राज्यात राहता?",
        "general": "मला तुम्हाला चांगल्या प्रकारे मदत करण्यासाठी थोडी अधिक माहिती हवी आहे. कृपया तुमचे वय, व्यवसाय, उत्पन्न आणि स्थान सांगा."
    }
}

# Error response templates
ERROR_TEMPLATES: Dict[str, str] = {
    "en": "I'm having trouble processing your request right now. Please try again in a moment.",
    "hi": "मुझे अभी आपके अनुरोध को संसाधित करने में कठिनाई हो रही है। कृपया कुछ समय बाद पुनः प्रयास करें।",
    "mr": "मला आत्ता तुमची विनंती प्रक्रिया करण्यात अडचण येत आहे. कृपया थोड्या वेळाने पुन्हा प्रयत्न करा."
}

# Timeout response templates
TIMEOUT_TEMPLATES: Dict[str, str] = {
    "en": "The request is taking longer than expected. Please try again.",
    "hi": "अनुरोध अपेक्षा से अधिक समय ले रहा है। कृपया पुनः प्रयास करें।",
    "mr": "विनंती अपेक्षेपेक्षा जास्त वेळ घेते आहे. कृपया पुन्हा प्रयत्न करा."
}

# Default profile extraction template (when LLM fails)
DEFAULT_PROFILE_TEMPLATE: Dict[str, Dict[str, Optional[str]]] = {
    "en": {
        "age": None,
        "occupation": None,
        "income_band": None,
        "location": {"state": None}
    },
    "hi": {
        "age": None,
        "occupation": None,
        "income_band": None,
        "location": {"state": None}
    },
    "mr": {
        "age": None,
        "occupation": None,
        "income_band": None,
        "location": {"state": None}
    }
}

# Explanation templates (fallback when LLM fails)
EXPLANATION_TEMPLATES: Dict[str, Dict[str, str]] = {
    "en": {
        "eligible": "Based on the information provided, you appear to be eligible for this scheme.",
        "not_eligible": "Based on the information provided, you do not appear to be eligible for this scheme.",
        "partially_eligible": "You may qualify for some schemes. Please provide more details for a complete assessment.",
        "unknown": "I need more information to determine your eligibility."
    },
    "hi": {
        "eligible": "प्रदान की गई जानकारी के आधार पर, आप इस योजना के लिए पात्र प्रतीत होते हैं।",
        "not_eligible": "प्रदान की गई जानकारी के आधार पर, आप इस योजना के लिए पात्र नहीं प्रतीत होते हैं।",
        "partially_eligible": "आप कुछ योजनाओं के लिए पात्र हो सकते हैं। पूर्ण मूल्यांकन के लिए अधिक जानकारी दें।",
        "unknown": "आपकी पात्रता निर्धारित करने के लिए मुझे अधिक जानकारी चाहिए।"
    },
    "mr": {
        "eligible": "दिलेल्या माहितीच्या आधारे, तुम्ही या योजनेसाठी पात्र वाटत आहात.",
        "not_eligible": "दिलेल्या माहितीच्या आधारे, तुम्ही या योजनेसाठी पात्र नाही वाटत आहात.",
        "partially_eligible": "तुम्ही काही योजनांसाठी पात्र असू शकता. संपूर्ण मूल्यांकनासाठी अधिक माहिती द्या.",
        "unknown": "तुमची पात्रता निर्धारित करण्यासाठी मला अधिक माहिती हवी आहे."
    }
}


def get_missing_info_message(field: str, language: str = "en") -> str:
    """
    Get a message asking for missing information.
    
    Args:
        field: The missing field name (age, occupation, income, location)
        language: Language code (en, hi, mr)
        
    Returns:
        Template message in requested language
    """
    lang = language if language in SUPPORTED_LANGUAGES else "en"
    return MISSING_INFO_TEMPLATES[lang].get(field, MISSING_INFO_TEMPLATES[lang]["general"])


def get_error_message(language: str = "en") -> str:
    """
    Get error message template.
    
    Args:
        language: Language code (en, hi, mr)
        
    Returns:
        Error message in requested language
    """
    lang = language if language in SUPPORTED_LANGUAGES else "en"
    return ERROR_TEMPLATES[lang]


def get_timeout_message(language: str = "en") -> str:
    """
    Get timeout message template.
    
    Args:
        language: Language code (en, hi, mr)
        
    Returns:
        Timeout message in requested language
    """
    lang = language if language in SUPPORTED_LANGUAGES else "en"
    return TIMEOUT_TEMPLATES[lang]


def get_default_profile(language: str = "en") -> Dict[str, Optional[str]]:
    """
    Get default empty profile structure.
    
    Args:
        language: Language code (unused but kept for consistency)
        
    Returns:
        Default profile with all fields as None
    """
    return {
        "age": None,
        "occupation": None,
        "income_band": None,
        "location": {"state": None}
    }


def get_fallback_explanation(rule_output: Dict, language: str = "en") -> str:
    """
    Get fallback explanation when LLM fails.
    
    Args:
        rule_output: Rule engine output dict with 'status' key
        language: Language code (en, hi, mr)
        
    Returns:
        Simple explanation in requested language
    """
    lang = language if language in SUPPORTED_LANGUAGES else "en"
    status = rule_output.get("status", "unknown")
    
    if status == "eligible":
        return EXPLANATION_TEMPLATES[lang]["eligible"]
    elif status == "not_eligible":
        return EXPLANATION_TEMPLATES[lang]["not_eligible"]
    elif status == "partially_eligible":
        return EXPLANATION_TEMPLATES[lang]["partially_eligible"]
    else:
        return EXPLANATION_TEMPLATES[lang]["unknown"]
