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


# All trackable profile fields
PROFILE_FIELDS = [
    "occupation",
    "state",
    "income_range",
    "age_group",
    "gender",
    "disability_status",
    "caste_category",
    "farmer_status",
    "student_status",
    # Legacy fields used by eligibility engine
    "age",
    "income",
]


class ProfileMemory:
    """
    In-memory profile accumulator for a single session.

    Stores extracted profile attributes across multiple conversation turns.
    Non-None values from new extractions overwrite stored values.
    """

    def __init__(self):
        self._profile: Dict[str, Any] = {}

    def update(self, extracted: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge newly extracted profile attributes into stored profile.

        Only non-None values are merged (new values overwrite old ones).

        Args:
            extracted: Dict of newly extracted profile attributes.

        Returns:
            The complete merged profile.
        """
        for key, value in extracted.items():
            if value is not None:
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
        Return list of profile fields that are still not populated.

        Only checks the core profile fields (not legacy numeric fields).
        """
        core_fields = [
            "occupation", "state", "income_range", "age_group",
            "gender", "disability_status", "caste_category",
            "farmer_status", "student_status",
        ]
        return [f for f in core_fields if f not in self._profile]

    def get_populated_fields(self) -> List[str]:
        """Return list of fields that have been populated."""
        return list(self._profile.keys())

    def reset(self) -> None:
        """Clear all stored profile attributes."""
        self._profile.clear()
        logger.debug("Profile memory reset")

    @property
    def is_complete(self) -> bool:
        """Check if all core profile fields are populated."""
        return len(self.get_missing_fields()) == 0

    def __repr__(self) -> str:
        populated = len(self.get_populated_fields())
        missing = len(self.get_missing_fields())
        return f"ProfileMemory(populated={populated}, missing={missing})"
