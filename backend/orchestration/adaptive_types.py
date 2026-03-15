"""
Data structures and constants for adaptive questioning feature.

This module contains dataclasses and constants used by the AdaptiveQuestioningEngine
to analyze scheme requirements and prioritize questions intelligently.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Set
import time


@dataclass
class MissingAttribute:
    """
    Represents a missing profile attribute with metadata for prioritization.
    
    Attributes:
        field: The profile field name (e.g., "education_level", "district")
        required_by_schemes: List of scheme_ids that require this attribute
        scheme_unlock_count: Number of schemes that could become eligible/partial
        partial_scheme_count: Number of partial schemes that need this field
        is_high_value: Whether required by high-value schemes
        priority_score: Calculated priority score for question selection
        logic_types: Dict mapping scheme_id to "AND" or "OR" logic
    """
    field: str
    required_by_schemes: List[str] = field(default_factory=list)
    scheme_unlock_count: int = 0
    partial_scheme_count: int = 0
    is_high_value: bool = False
    priority_score: float = 0.0
    logic_types: Dict[str, str] = field(default_factory=dict)
    
    def __repr__(self) -> str:
        return (
            f"MissingAttribute(field='{self.field}', "
            f"unlock={self.scheme_unlock_count}, "
            f"partial={self.partial_scheme_count}, "
            f"priority={self.priority_score:.2f})"
        )


@dataclass
class SchemeCriteria:
    """
    Cached representation of scheme eligibility criteria.
    
    Attributes:
        scheme_id: Unique identifier for the scheme
        scheme_name: Display name of the scheme
        required_fields: Set of all fields mentioned in eligibility criteria
        logic: "AND" or "OR" - how criteria are combined
        is_high_value: Whether scheme is high-value (based on benefit keywords)
        benefit_summary: Brief description of scheme benefits
        criteria_count: Number of eligibility criteria
    """
    scheme_id: str
    scheme_name: str
    required_fields: Set[str] = field(default_factory=set)
    logic: str = "AND"  # Default to AND
    is_high_value: bool = False
    benefit_summary: str = ""
    criteria_count: int = 0
    
    def __repr__(self) -> str:
        return (
            f"SchemeCriteria(id='{self.scheme_id}', "
            f"fields={len(self.required_fields)}, "
            f"logic='{self.logic}', "
            f"high_value={self.is_high_value})"
        )


@dataclass
class Conflict:
    """
    Represents a detected conflict in profile data.
    
    Attributes:
        field: The profile field with conflicting values
        old_value: Previously stored value
        new_value: Newly extracted value
        timestamp: When the conflict was detected (Unix timestamp)
        resolution: How the conflict was resolved
    """
    field: str
    old_value: Any
    new_value: Any
    timestamp: float = field(default_factory=time.time)
    resolution: str = "new_value_wins"  # Default resolution strategy
    
    def __repr__(self) -> str:
        return (
            f"Conflict(field='{self.field}', "
            f"{self.old_value} → {self.new_value}, "
            f"resolution='{self.resolution}')"
        )


# Skip keywords for multilingual skip intent detection
SKIP_KEYWORDS = {
    "en": [
        "skip", "next", "pass", "don't want to answer", 
        "prefer not to say", "don't know", "not sure",
        "skip this", "skip question", "next question"
    ],
    "hi": [
        "छोड़ें", "अगला", "नहीं बताना चाहते", "पास",
        "नहीं पता", "अगला सवाल", "छोड़ दें"
    ],
    "mr": [
        "वगळा", "पुढे", "सांगू इच्छित नाही", "पास",
        "माहित नाही", "पुढील प्रश्न", "वगळा हा"
    ],
}


# Critical fields that trigger conflict detection
CRITICAL_FIELDS = {
    "state", "occupation", "age_group", "income_range",
    "gender", "caste_category", "farmer_status"
}
