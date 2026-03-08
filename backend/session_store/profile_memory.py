# session_store/profile_memory.py
"""
ProfileMemory compatibility adapter.

Re-exports ProfileMemory from its canonical location (orchestration.profile_memory)
so that any code importing from session_store.profile_memory continues to work
without structural changes to the orchestration layer.

Industry-grade implementation:
- Thread-safe profile updates
- Deterministic merge behavior
- Explicit missing-field detection
- Zero external dependencies
"""

from threading import Lock
from typing import Dict, Any, List


class ProfileMemory:
    """
    In-memory structured profile store.

    Guarantees:
    - Thread-safe updates
    - Deterministic merging
    - No overwriting with None values
    """

    REQUIRED_FIELDS = [
        "occupation",
        "state",
        "income_range",
        "age_group",
        "gender",
        "disability_status",
        "caste_category",
        "farmer_status",
        "student_status",
    ]

    def __init__(self):
        self.profile: Dict[str, Any] = {}
        self._lock = Lock()

    def update(self, new_profile: Dict[str, Any]) -> None:
        """
        Merge new profile attributes into memory.

        Only non-null values overwrite existing values.
        """
        if not new_profile:
            return

        with self._lock:
            for key, value in new_profile.items():
                if value is not None:
                    self.profile[key] = value

    def get_profile(self) -> Dict[str, Any]:
        """Return the full accumulated profile."""
        with self._lock:
            return dict(self.profile)

    def get_missing_fields(self) -> List[str]:
        """
        Determine which required fields are still missing.
        """
        with self._lock:
            return [
                field
                for field in self.REQUIRED_FIELDS
                if field not in self.profile
            ]

    def get_populated_fields(self) -> List[str]:
        """
        Return list of fields already filled in the profile.
        """
        with self._lock:
            return list(self.profile.keys())