"""
Profile Memory for SamvaadAI.

In-memory per-session profile accumulation across conversation turns.
Each session maintains a profile that grows as the user provides more information.

Architectural guarantees:
- Session-lifetime only (no persistence, no DB calls)
- Thread-safe (GIL-protected dict operations)
- Deterministic merge logic (non-None values overwrite)
- No business logic or eligibility decisions
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


# Required fields for profile completion (9 fields)
REQUIRED_FIELDS = [
    "occupation",
    "state", 
    "income_range",
    "age_group",
    "gender",
    "disability_status",
    "caste_category",
    "farmer_status",
    "student_status"
]

# Optional fields for extended profiling
OPTIONAL_FIELDS = [
    "education_level",
    "land_ownership", 
    "land_holding",       # numeric hectares (derived: farmer_category)
    "bank_account",
    "house_ownership",    # "no_pucca_house" | "owns_house"
    "family_size",
    "district",
    "employment_status",
    "urban_rural",
    "bpl_status",
    "minority_status"
]

# Legacy fields used by eligibility engine
LEGACY_FIELDS = [
    "age",
    "income"
]

# All trackable profile fields
PROFILE_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS + LEGACY_FIELDS


# Validation rules for new optional fields
FIELD_VALIDATORS = {
    "education_level": ["primary", "secondary", "higher_secondary", "graduate", "postgraduate", "none"],
    "land_ownership": ["yes", "no", "leased"],
    "urban_rural": ["urban", "rural"],
    "employment_status": ["employed", "self_employed", "unemployed", "student", "retired"],
    "disability_status": ["none", "physical", "visual", "hearing", "multiple"],
    "minority_status": ["none", "religious_minority", "linguistic_minority"],
}


class ProfileMemory:
    """
    In-memory profile accumulator for a single session.

    Stores extracted profile attributes across multiple conversation turns.
    Non-None values from new extractions overwrite stored values.
    
    Enhanced with:
    - Skip tracking (fields user explicitly skipped)
    - Conflict detection (when user provides contradictory data)
    """

    # Class constants for testing
    REQUIRED_FIELDS = REQUIRED_FIELDS

    def __init__(self):
        self._profile: Dict[str, Any] = {}
        self._skipped_fields: set = set()  # Fields user chose to skip
        self._field_history: Dict[str, List[Any]] = {}  # Track value changes

    def _validate_field(self, field: str, value: Any) -> bool:
        """
        Validate a profile field value against validation rules.
        
        Returns True immediately if value is None or empty string (skip validation).
        For fields with validation rules, checks if value is in allowed set.
        For family_size, validates positive integer.
        For boolean fields (bank_account, bpl_status), validates boolean type.
        
        Args:
            field: The field name to validate
            value: The value to validate
            
        Returns:
            True if validation passes or should be skipped, False if validation fails
        """
        # Skip validation for None or empty string
        if value is None or value == "":
            return True
        
        # disability_status accepts both booleans and string values
        if field == "disability_status":
            if isinstance(value, bool):
                return True
            # fall through to enum check for string values like "physical", "none", etc.
        
        # Validate fields with enum constraints
        if field in FIELD_VALIDATORS:
            if value not in FIELD_VALIDATORS[field]:
                logger.warning(
                    f"Validation failed for {field}='{value}'. "
                    f"Expected one of {FIELD_VALIDATORS[field]}"
                )
                return False
        
        # Validate family_size as positive integer
        if field == "family_size":
            if not isinstance(value, int) or value <= 0:
                logger.warning(
                    f"Validation failed for {field}={value}. "
                    f"Expected positive integer"
                )
                return False
        
        # Validate boolean fields
        if field in ["bank_account", "bpl_status"]:
            if not isinstance(value, bool):
                logger.warning(
                    f"Validation failed for {field}={value}. "
                    f"Expected boolean"
                )
                return False
        
        return True

    def update(self, extracted: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge newly extracted profile attributes into stored profile.

        Only non-None values are merged (new values overwrite old ones).
        Tracks value changes for conflict detection.
        Validates new optional fields before merging.

        Args:
            extracted: Dict of newly extracted profile attributes.

        Returns:
            The complete merged profile.
        """
        for key, value in extracted.items():
            if value is not None:
                # Validate new optional fields before merging
                if not self._validate_field(key, value):
                    logger.warning(f"Skipping invalid value for {key}")
                    continue
                
                # Track value history for conflict detection
                if key in self._profile and self._profile[key] != value:
                    if key not in self._field_history:
                        self._field_history[key] = [self._profile[key]]
                    self._field_history[key].append(value)
                    logger.warning(
                        f"Profile conflict detected for {key}: {self._profile[key]} → {value}"
                    )
                
                self._profile[key] = value

        logger.debug(
            f"Profile updated: {len(self._profile)} fields populated",
            extra={"profile_keys": list(self._profile.keys())},
        )
        return self.get_profile()

    def get_profile(self) -> Dict[str, Any]:
        """
        Return the current profile as a dict.

        Returns:
            Copy of the stored profile.
        """
        return dict(self._profile)

    def get_missing_fields(self) -> List[str]:
        """
        Return list of REQUIRED profile fields that are still not populated.

        Only checks the core required fields (9 fields).
        Excludes fields that user explicitly skipped.
        """
        return [
            f for f in REQUIRED_FIELDS 
            if f not in self._profile and f not in self._skipped_fields
        ]

    def get_populated_fields(self) -> List[str]:
        """Return list of fields that have been populated."""
        return list(self._profile.keys())

    def reset(self) -> None:
        """Clear all stored profile attributes."""
        self._profile.clear()
        self._skipped_fields.clear()
        self._field_history.clear()
        logger.debug("Profile memory reset")

    @property
    def is_complete(self) -> bool:
        """Check if all REQUIRED profile fields are populated."""
        return len(self.get_missing_fields()) == 0
    
    def mark_field_skipped(self, field: str) -> None:
        """
        Mark a field as explicitly skipped by the user.
        
        Skipped fields won't appear in missing_fields list.
        """
        self._skipped_fields.add(field)
        logger.info(f"Field marked as skipped: {field}")
    
    def get_skipped_fields(self) -> List[str]:
        """Return list of fields user chose to skip."""
        return list(self._skipped_fields)
    
    def get_conflicts(self) -> Dict[str, List[Any]]:
        """
        Return fields with conflicting values.
        
        Returns:
            Dict mapping field names to list of conflicting values.
        """
        return {k: v for k, v in self._field_history.items() if len(v) > 1}
    
    def has_conflicts(self) -> bool:
        """Check if there are any conflicting field values."""
        return len(self.get_conflicts()) > 0

    def __repr__(self) -> str:
        populated = len(self.get_populated_fields())
        missing = len(self.get_missing_fields())
        return f"ProfileMemory(populated={populated}, missing={missing})"
