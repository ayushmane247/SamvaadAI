"""
Deterministic Profile Extractor for SamvaadAI.

Regex-based profile extraction that works WITHOUT any LLM.
Used as fallback when Bedrock is unavailable (AccessDeniedException,
INVALID_PAYMENT_INSTRUMENT, etc.).

Supports: English, Hindi, Marathi.

Architectural guarantees:
- Zero network calls
- Deterministic (same input → same output)
- Sub-millisecond latency
- No side effects
"""

import re
from typing import Dict, Any, Optional, List


# ── State dictionaries ────────────────────────────────────────────

INDIAN_STATES = {
    # English
    "andhra pradesh", "arunachal pradesh", "assam", "bihar",
    "chhattisgarh", "goa", "gujarat", "haryana", "himachal pradesh",
    "jharkhand", "karnataka", "kerala", "madhya pradesh", "maharashtra",
    "manipur", "meghalaya", "mizoram", "nagaland", "odisha", "punjab",
    "rajasthan", "sikkim", "tamil nadu", "telangana", "tripura",
    "uttar pradesh", "uttarakhand", "west bengal",
    # Union Territories
    "delhi", "chandigarh", "puducherry", "jammu and kashmir",
    "ladakh", "andaman and nicobar", "lakshadweep",
    "dadra and nagar haveli and daman and diu",
    # Hindi / Marathi common names
    "महाराष्ट्र", "दिल्ली", "बिहार", "उत्तर प्रदेश", "राजस्थान",
    "गुजरात", "कर्नाटक", "तमिलनाडु", "केरल", "पंजाब",
    "हरियाणा", "मध्य प्रदेश", "छत्तीसगढ़", "झारखंड", "उत्तराखंड",
    "गोवा", "असम", "पश्चिम बंगाल", "ओडिशा", "तेलंगाना",
    "आंध्र प्रदेश",
}

# Map Hindi/Marathi state names to English
STATE_TRANSLATIONS = {
    "महाराष्ट्र": "Maharashtra", "दिल्ली": "Delhi", "बिहार": "Bihar",
    "उत्तर प्रदेश": "Uttar Pradesh", "राजस्थान": "Rajasthan",
    "गुजरात": "Gujarat", "कर्नाटक": "Karnataka", "तमिलनाडु": "Tamil Nadu",
    "केरल": "Kerala", "पंजाब": "Punjab", "हरियाणा": "Haryana",
    "मध्य प्रदेश": "Madhya Pradesh", "छत्तीसगढ़": "Chhattisgarh",
    "झारखंड": "Jharkhand", "उत्तराखंड": "Uttarakhand", "गोवा": "Goa",
    "असम": "Assam", "पश्चिम बंगाल": "West Bengal", "ओडिशा": "Odisha",
    "तेलंगाना": "Telangana", "आंध्र प्रदेश": "Andhra Pradesh",
}

# ── Occupation keywords ──────────────────────────────────────────

FARMER_KEYWORDS = {
    "farmer", "farming", "agriculture", "kisan", "kisaan",
    "किसान", "खेती", "शेतकरी", "शेती",
}

STUDENT_KEYWORDS = {
    "student", "studying", "college", "university", "school",
    "विद्यार्थी", "छात्र", "पढ़ाई", "विद्यार्थ्यांना",
}

OCCUPATION_KEYWORDS = {
    "doctor": {"doctor", "physician", "डॉक्टर"},
    "teacher": {"teacher", "शिक्षक", "शिक्षिका", "अध्यापक"},
    "engineer": {"engineer", "इंजीनियर"},
    "labourer": {"labourer", "laborer", "labour", "labor", "मजदूर", "कामगार"},
    "shopkeeper": {"shopkeeper", "shop owner", "दुकानदार"},
    "business": {"business", "businessman", "businesswoman", "entrepreneur", "व्यापारी", "व्यवसायी"},
    "unemployed": {"unemployed", "jobless", "बेरोजगार"},
    "retired": {"retired", "सेवानिवृत्त"},
    "housewife": {"housewife", "homemaker", "गृहिणी"},
    "self-employed": {"self-employed", "self employed", "स्वरोजगार"},
}

# ── Gender keywords ───────────────────────────────────────────────

GENDER_KEYWORDS = {
    "male": {"male", "man", "boy", "पुरुष", "लड़का", "मुलगा"},
    "female": {"female", "woman", "girl", "lady", "महिला", "लड़की", "मुलगी", "स्त्री"},
}

# ── Caste keywords ────────────────────────────────────────────────

CASTE_KEYWORDS = {
    "general": {"general", "सामान्य"},
    "obc": {"obc", "other backward class", "अन्य पिछड़ा वर्ग", "ओबीसी"},
    "sc": {"sc", "scheduled caste", "अनुसूचित जाति", "एससी"},
    "st": {"st", "scheduled tribe", "अनुसूचित जनजाति", "एसटी"},
    "ews": {"ews", "economically weaker", "आर्थिक रूप से कमजोर"},
}

# ── Disability keywords ──────────────────────────────────────────

DISABILITY_KEYWORDS = {
    "disabled", "disability", "handicapped", "differently abled",
    "divyang", "विकलांग", "दिव्यांग", "अपंग",
}

# ── Land holding patterns ────────────────────────────────────────

LAND_HOLDING_PATTERNS = [
    # "I own 2 acres", "2 acre land", "2 hectares"
    r"(\d+\.?\d*)\s*(?:acres?|एकर)",
    r"(\d+\.?\d*)\s*(?:hectares?|हेक्टेयर|हेक्टर)",
    r"(?:own|have|possess)\s+(\d+\.?\d*)\s*(?:acres?|hectares?|bigha|बीघा)",
    r"(\d+\.?\d*)\s*(?:bigha|बीघा)",
]

# Conversion: 1 acre ≈ 0.405 hectares, 1 bigha ≈ 0.25 acres ≈ 0.1 hectares
_LAND_UNIT_TO_HECTARES = {
    "acre": 0.405,
    "acres": 0.405,
    "एकर": 0.405,
    "hectare": 1.0,
    "hectares": 1.0,
    "हेक्टेयर": 1.0,
    "हेक्टर": 1.0,
    "bigha": 0.1,
    "बीघा": 0.1,
}

# ── Bank account keywords ────────────────────────────────────────

BANK_ACCOUNT_YES = {
    "bank account", "have account", "savings account", "jan dhan",
    "बैंक खाता", "खाता है", "बँक खाते",
}
BANK_ACCOUNT_NO = {
    "no bank account", "don't have account", "no account",
    "बैंक खाता नहीं", "खाता नहीं",
}

# ── House ownership keywords ─────────────────────────────────────

NO_HOUSE_KEYWORDS = {
    "no house", "don't own house", "no pucca house", "homeless",
    "renting", "rented house", "tenant", "no home",
    "घर नहीं", "पक्का घर नहीं", "किराये पर",
}
OWNS_HOUSE_KEYWORDS = {
    "own house", "own home", "pucca house", "my house",
    "घर है", "अपना घर",
}


def extract_profile(text: str, language: str = "en") -> Dict[str, Any]:
    """
    Extract a structured profile from natural language text using pattern matching.

    Args:
        text: User's natural language input.
        language: Language code (en, hi, mr).

    Returns:
        Dict with profile fields and missing_fields list.
    """
    text_lower = text.lower().strip()

    # Check for structured input from QuickSelectChips (format: "field_name: value")
    structured_match = re.match(r"^(\w+):\s*(.+)$", text)
    if structured_match:
        field_name = structured_match.group(1)
        field_value = structured_match.group(2).strip()
        
        # Map field names to profile values
        profile = {}
        if field_name == "state":
            profile["state"] = field_value
        elif field_name == "occupation":
            profile["occupation"] = field_value
            if field_value == "farmer":
                profile["farmer_status"] = True
            elif field_value == "student":
                profile["student_status"] = True
        elif field_name == "age_group":
            profile["age_group"] = field_value
            # Also extract numeric age if possible
            age_match = re.search(r"(\d+)", field_value)
            if age_match:
                profile["age"] = int(age_match.group(1))
        elif field_name == "income_range":
            profile["income_range"] = field_value
        elif field_name == "gender":
            profile["gender"] = field_value
        elif field_name == "caste_category":
            profile["caste_category"] = field_value
        elif field_name == "farmer_status":
            profile["farmer_status"] = field_value.lower() in ["true", "yes", "हाँ", "होय"]
        elif field_name == "student_status":
            profile["student_status"] = field_value.lower() in ["true", "yes", "हाँ", "होय"]
        elif field_name == "disability_status":
            profile["disability_status"] = field_value.lower() in ["true", "yes", "हाँ", "होय"]
        
        # Determine missing fields
        all_fields = [
            "occupation", "state", "income_range", "age_group",
            "gender", "disability_status", "caste_category",
            "farmer_status", "student_status",
        ]
        missing_fields = [f for f in all_fields if f not in profile]
        
        return {
            "profile": profile,
            "missing_fields": missing_fields,
        }

    profile: Dict[str, Any] = {
        "occupation": _extract_occupation(text_lower, text),
        "state": _extract_state(text_lower, text),
        "income_range": _extract_income(text_lower, text),
        "age_group": _extract_age(text_lower, text),
        "gender": _extract_gender(text_lower),
        "disability_status": _extract_disability(text_lower),
        "caste_category": _extract_caste(text_lower),
        "farmer_status": _is_farmer(text_lower),
        "student_status": _is_student(text_lower),
        "land_holding": _extract_land_holding(text_lower),
        "bank_account": _extract_bank_account(text_lower),
        "house_ownership": _extract_house_ownership(text_lower),
    }

    # Also set legacy fields used by eligibility engine
    age_num = _extract_age_number(text_lower, text)
    if age_num is not None:
        profile["age"] = age_num
    income_num = _extract_income_number(text_lower, text)
    if income_num is not None:
        profile["income"] = income_num
    if profile["occupation"]:
        pass  # occupation already set
    elif profile["farmer_status"]:
        profile["occupation"] = "farmer"
    elif profile["student_status"]:
        profile["occupation"] = "student"

    # Remove None values to allow clean merging
    clean_profile = {k: v for k, v in profile.items() if v is not None}

    # Determine missing fields
    all_fields = [
        "occupation", "state", "income_range", "age_group",
        "gender", "disability_status", "caste_category",
        "farmer_status", "student_status",
    ]
    missing_fields = [f for f in all_fields if f not in clean_profile]

    return {
        "profile": clean_profile,
        "missing_fields": missing_fields,
    }


def _extract_age_number(text_lower: str, text: str) -> Optional[int]:
    """Extract numeric age from text."""
    patterns = [
        r"(?:i am|i'm|age is|aged?|my age is|am)\s*(\d{1,3})",
        r"(\d{1,3})\s*(?:years?\s*old|yrs?\s*old|साल|वर्ष)",
        r"(?:उम्र|वय)\s*(\d{1,3})",
        r"(\d{1,3})\s*(?:उम्र|वय)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            age = int(match.group(1))
            if 1 <= age <= 120:
                return age
    return None


def _extract_age(text_lower: str, text: str) -> Optional[str]:
    """Extract age group from text."""
    age = _extract_age_number(text_lower, text)
    if age is None:
        return None
    if age < 18:
        return "minor"
    elif age <= 25:
        return "18-25"
    elif age <= 35:
        return "26-35"
    elif age <= 45:
        return "36-45"
    elif age <= 60:
        return "46-60"
    else:
        return "60+"


def _extract_occupation(text_lower: str, text: str) -> Optional[str]:
    """Extract occupation from text."""
    # Check farmer first
    for kw in FARMER_KEYWORDS:
        if kw in text_lower:
            return "farmer"

    # Check student
    for kw in STUDENT_KEYWORDS:
        if kw in text_lower:
            return "student"

    # Check other occupations
    for occupation, keywords in OCCUPATION_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return occupation

    return None


def _extract_state(text_lower: str, text: str) -> Optional[str]:
    """Extract Indian state from text."""
    # Check Hindi/Marathi state names first (original case)
    for hindi_name, eng_name in STATE_TRANSLATIONS.items():
        if hindi_name in text:
            return eng_name

    # Check English state names (case-insensitive)
    # Sort by length descending to match longer names first
    sorted_states = sorted(
        [s for s in INDIAN_STATES if s.isascii()],
        key=len,
        reverse=True,
    )
    for state in sorted_states:
        if state in text_lower:
            return state.title()

    # Pattern: "from <state>"
    from_pattern = re.search(r"from\s+([a-z][a-z\s]+)", text_lower)
    if from_pattern:
        candidate = from_pattern.group(1).strip()
        for state in sorted_states:
            if state.startswith(candidate) or candidate.startswith(state):
                return state.title()

    return None


def _extract_income_number(text_lower: str, text: str) -> Optional[float]:
    """Extract numeric income value."""
    patterns = [
        # "50000", "50,000", "₹50000"
        r"(?:income|salary|earning|₹|rs\.?|inr)\s*[:\s]*(\d[\d,]*)",
        r"(\d[\d,]*)\s*(?:per\s*(?:month|year|annum)|monthly|annually|yearly|rupees|₹)",
        # "5 lakh", "2.5 lakh"
        r"(\d+\.?\d*)\s*(?:lakh|lac|लाख)",
        # Hindi/Marathi patterns
        r"(?:आय|उत्पन्न|कमाई)\s*(\d[\d,]*)",
    ]

    for i, pattern in enumerate(patterns):
        match = re.search(pattern, text_lower)
        if match:
            value_str = match.group(1).replace(",", "")
            try:
                value = float(value_str)
                # If lakh pattern
                if i == 2:
                    value *= 100000
                return value
            except ValueError:
                continue
    return None


def _extract_income(text_lower: str, text: str) -> Optional[str]:
    """Extract income range from text."""
    income = _extract_income_number(text_lower, text)
    if income is None:
        # Check for qualitative descriptions
        low_income_kw = {"poor", "low income", "below poverty", "bpl", "गरीब", "गरीबी"}
        for kw in low_income_kw:
            if kw in text_lower:
                return "below_1l"
        return None

    if income < 100000:
        return "below_1l"
    elif income < 250000:
        return "1l_to_2.5l"
    elif income < 500000:
        return "2.5l_to_5l"
    elif income < 1000000:
        return "5l_to_10l"
    else:
        return "above_10l"


def _extract_gender(text_lower: str) -> Optional[str]:
    """Extract gender from text using word boundaries."""
    # Check female FIRST (longer match) to avoid 'male' matching within 'female'
    for kw in GENDER_KEYWORDS["female"]:
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
            return "female"
    for kw in GENDER_KEYWORDS["male"]:
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
            return "male"
    return None


def _extract_disability(text_lower: str) -> Optional[bool]:
    """Extract disability status from text."""
    for kw in DISABILITY_KEYWORDS:
        if kw in text_lower:
            return True
    return None


def _extract_caste(text_lower: str) -> Optional[str]:
    """Extract caste category from text."""
    for category, keywords in CASTE_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return category
    return None


def _is_farmer(text_lower: str) -> Optional[bool]:
    """Check if user is a farmer."""
    for kw in FARMER_KEYWORDS:
        if kw in text_lower:
            return True
    return None


def _is_student(text_lower: str) -> Optional[bool]:
    """Check if user is a student."""
    for kw in STUDENT_KEYWORDS:
        if kw in text_lower:
            return True
    return None


def _extract_land_holding(text_lower: str) -> Optional[float]:
    """
    Extract land holding in hectares from text.
    Converts acres and bigha to hectares.
    """
    for pattern in LAND_HOLDING_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            try:
                value = float(match.group(1))
                # Determine unit from matched text
                matched_text = match.group(0).lower()
                for unit, factor in _LAND_UNIT_TO_HECTARES.items():
                    if unit in matched_text:
                        return round(value * factor, 3)
                # Default: assume acres if no unit matched
                return round(value * 0.405, 3)
            except (ValueError, IndexError):
                continue
    return None


def _extract_bank_account(text_lower: str) -> Optional[bool]:
    """Extract bank account status from text."""
    for kw in BANK_ACCOUNT_NO:
        if kw in text_lower:
            return False
    for kw in BANK_ACCOUNT_YES:
        if kw in text_lower:
            return True
    return None


def _extract_house_ownership(text_lower: str) -> Optional[str]:
    """Extract house ownership status from text."""
    for kw in NO_HOUSE_KEYWORDS:
        if kw in text_lower:
            return "no_pucca_house"
    for kw in OWNS_HOUSE_KEYWORDS:
        if kw in text_lower:
            return "owns_house"
    return None
