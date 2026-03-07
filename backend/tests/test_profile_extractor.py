"""
Tests for deterministic profile extraction (no LLM).
"""
import os
os.environ["APP_ENV"] = "test"

from llm_service.profile_extractor import extract_profile


def test_farmer_from_maharashtra():
    """'I am a farmer from Maharashtra' should extract farmer + Maharashtra."""
    result = extract_profile("I am a farmer from Maharashtra")
    profile = result["profile"]
    assert profile["occupation"] == "farmer"
    assert profile["state"] == "Maharashtra"
    assert profile["farmer_status"] is True


def test_student_from_delhi():
    """'I am a student from Delhi' should extract student + Delhi."""
    result = extract_profile("I am a student from Delhi")
    profile = result["profile"]
    assert profile["occupation"] == "student"
    assert profile["state"] == "Delhi"
    assert profile["student_status"] is True


def test_age_extraction():
    """Should extract age from various patterns."""
    result = extract_profile("I am 30 years old")
    assert result["profile"]["age"] == 30
    assert result["profile"]["age_group"] == "26-35"


def test_income_extraction():
    """Should extract income from text."""
    result = extract_profile("My income is 50000 per year")
    assert result["profile"]["income"] == 50000.0
    assert result["profile"]["income_range"] == "below_1l"


def test_income_lakh_format():
    """Should handle lakh format."""
    result = extract_profile("My salary is 2.5 lakh per annum")
    assert result["profile"]["income"] == 250000.0
    assert result["profile"]["income_range"] == "1l_to_2.5l"


def test_gender_extraction():
    """Should extract gender."""
    result = extract_profile("I am a female farmer from Uttar Pradesh")
    assert result["profile"]["gender"] == "female"


def test_caste_extraction():
    """Should extract caste category."""
    result = extract_profile("I belong to OBC category")
    assert result["profile"]["caste_category"] == "obc"


def test_disability_extraction():
    """Should extract disability status."""
    result = extract_profile("I am a disabled person from Kerala")
    assert result["profile"]["disability_status"] is True


def test_hindi_input():
    """Should extract profile from Hindi text."""
    result = extract_profile("मैं एक किसान हूँ महाराष्ट्र से")
    profile = result["profile"]
    assert profile["occupation"] == "farmer"
    # State should be extracted from Hindi
    assert profile.get("state") == "Maharashtra"


def test_multiple_attributes():
    """Should extract multiple attributes from one sentence."""
    result = extract_profile(
        "I am a 25 year old male farmer from Maharashtra with income of 1.5 lakh"
    )
    profile = result["profile"]
    assert profile["occupation"] == "farmer"
    assert profile["age"] == 25
    assert profile["age_group"] == "18-25"
    assert profile["gender"] == "male"
    assert profile["state"] == "Maharashtra"
    assert profile["income"] == 150000.0


def test_missing_fields_reported():
    """Should report what fields are still missing."""
    result = extract_profile("I am a farmer")
    missing = result["missing_fields"]
    assert "state" in missing
    assert "income_range" in missing
    assert "age_group" in missing
    # occupation and farmer_status should NOT be missing
    assert "occupation" not in missing
    assert "farmer_status" not in missing


def test_empty_input():
    """Empty input should return all fields missing."""
    result = extract_profile("")
    assert len(result["missing_fields"]) == 9


def test_business_owner():
    """Should extract business occupation for Mudra scheme matching."""
    result = extract_profile("I am a self-employed shopkeeper from Gujarat")
    profile = result["profile"]
    # Should match shopkeeper or self-employed
    assert profile["occupation"] in ["shopkeeper", "self-employed"]
    assert profile["state"] == "Gujarat"
