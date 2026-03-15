"""
Tests for ProfileMemory — session-scoped profile accumulation.
"""
import os
os.environ["APP_ENV"] = "test"

from orchestration.profile_memory import ProfileMemory


def test_empty_initial_profile():
    """New ProfileMemory should have empty profile."""
    mem = ProfileMemory()
    assert mem.get_profile() == {}
    assert len(mem.get_missing_fields()) == len(mem.REQUIRED_FIELDS)  # All core fields missing


def test_update_single_field():
    """Updating a single field should store it."""
    mem = ProfileMemory()
    mem.update({"occupation": "farmer"})
    profile = mem.get_profile()
    assert profile["occupation"] == "farmer"
    assert "occupation" not in mem.get_missing_fields()


def test_update_multiple_fields():
    """Updating multiple fields at once."""
    mem = ProfileMemory()
    mem.update({"occupation": "farmer", "state": "Maharashtra", "age": 30})
    profile = mem.get_profile()
    assert profile["occupation"] == "farmer"
    assert profile["state"] == "Maharashtra"
    assert profile["age"] == 30


def test_multi_turn_accumulation():
    """Profile should accumulate across multiple updates."""
    mem = ProfileMemory()

    # Turn 1: "I am a farmer"
    mem.update({"occupation": "farmer", "farmer_status": True})

    # Turn 2: "from Maharashtra"
    mem.update({"state": "Maharashtra"})

    # Turn 3: "I am 30 years old"
    mem.update({"age_group": "26-35", "age": 30})

    profile = mem.get_profile()
    assert profile["occupation"] == "farmer"
    assert profile["state"] == "Maharashtra"
    assert profile["age_group"] == "26-35"
    assert profile["farmer_status"] is True


def test_update_overwrites_non_none():
    """Non-None values should overwrite old values."""
    mem = ProfileMemory()
    mem.update({"occupation": "student"})
    assert mem.get_profile()["occupation"] == "student"

    mem.update({"occupation": "farmer"})
    assert mem.get_profile()["occupation"] == "farmer"


def test_none_values_do_not_overwrite():
    """None values should NOT overwrite existing values."""
    mem = ProfileMemory()
    mem.update({"occupation": "farmer"})
    mem.update({"occupation": None, "state": "Maharashtra"})

    profile = mem.get_profile()
    assert profile["occupation"] == "farmer"
    assert profile["state"] == "Maharashtra"


def test_get_missing_fields():
    """Missing fields should decrease as profile fills."""
    mem = ProfileMemory()
    assert len(mem.get_missing_fields()) == 9

    mem.update({"occupation": "farmer"})
    missing = mem.get_missing_fields()
    assert "occupation" not in missing
    assert len(missing) == 8


def test_is_complete():
    """is_complete should be True when all core fields populated."""
    mem = ProfileMemory()
    assert not mem.is_complete

    mem.update({
        "occupation": "farmer",
        "state": "Maharashtra",
        "income_range": "below_1l",
        "age_group": "26-35",
        "gender": "male",
        "disability_status":"none",
        "caste_category": "general",
        "farmer_status": "yes",
        "student_status": False,
    })
    assert mem.is_complete


def test_reset():
    """Reset should clear all stored data."""
    mem = ProfileMemory()
    mem.update({"occupation": "farmer", "state": "Maharashtra"})
    assert len(mem.get_profile()) > 0

    mem.reset()
    assert mem.get_profile() == {}
    assert len(mem.get_missing_fields()) == 9
