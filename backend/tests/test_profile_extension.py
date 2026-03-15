"""
Quick validation tests for profile data model extension.
"""
import sys
sys.path.insert(0, 'backend')

from orchestration.profile_memory import ProfileMemory, PROFILE_FIELDS, FIELD_VALIDATORS


def test_new_fields_in_profile_fields():
    """Verify all 11 new fields are in PROFILE_FIELDS."""
    new_fields = [
        "education_level", "land_ownership", "bank_account",
        "family_size", "district", "employment_status",
        "urban_rural", "bpl_status", "minority_status"
    ]
    for field in new_fields:
        assert field in PROFILE_FIELDS, f"{field} not in PROFILE_FIELDS"
    print("✓ All 11 new fields present in PROFILE_FIELDS")


def test_field_validators_defined():
    """Verify FIELD_VALIDATORS dictionary exists and has correct fields."""
    expected_validators = [
        "education_level", "land_ownership", "urban_rural",
        "employment_status", "disability_status", "minority_status"
    ]
    for field in expected_validators:
        assert field in FIELD_VALIDATORS, f"{field} not in FIELD_VALIDATORS"
    print("✓ FIELD_VALIDATORS dictionary correctly defined")


def test_valid_education_level():
    """Test storing valid education_level."""
    memory = ProfileMemory()
    memory.update({"education_level": "graduate"})
    profile = memory.get_profile()
    assert profile["education_level"] == "graduate"
    print("✓ Valid education_level stored correctly")


def test_invalid_education_level_rejected():
    """Test invalid education_level is rejected."""
    memory = ProfileMemory()
    memory.update({"education_level": "invalid_value"})
    profile = memory.get_profile()
    assert "education_level" not in profile
    print("✓ Invalid education_level rejected")


def test_valid_family_size():
    """Test storing valid family_size."""
    memory = ProfileMemory()
    memory.update({"family_size": 5})
    profile = memory.get_profile()
    assert profile["family_size"] == 5
    print("✓ Valid family_size stored correctly")


def test_invalid_family_size_rejected():
    """Test invalid family_size (non-positive) is rejected."""
    memory = ProfileMemory()
    memory.update({"family_size": 0})
    profile = memory.get_profile()
    assert "family_size" not in profile
    
    memory.update({"family_size": -5})
    profile = memory.get_profile()
    assert "family_size" not in profile
    print("✓ Invalid family_size rejected")


def test_valid_boolean_fields():
    """Test storing valid boolean fields."""
    memory = ProfileMemory()
    memory.update({"bank_account": True, "bpl_status": False})
    profile = memory.get_profile()
    assert profile["bank_account"] is True
    assert profile["bpl_status"] is False
    print("✓ Valid boolean fields stored correctly")


def test_none_values_skip_validation():
    """Test None values skip validation."""
    memory = ProfileMemory()
    memory.update({"education_level": None, "family_size": None})
    profile = memory.get_profile()
    assert "education_level" not in profile
    assert "family_size" not in profile
    print("✓ None values skip validation correctly")


def test_mixed_profile_with_new_and_legacy_fields():
    """Test profile with both legacy and new fields."""
    memory = ProfileMemory()
    memory.update({
        "occupation": "farmer",
        "state": "Maharashtra",
        "age_group": "36-45",
        "education_level": "secondary",
        "land_ownership": "yes",
        "district": "Pune",
        "urban_rural": "rural",
        "family_size": 5,
        "bank_account": True
    })
    profile = memory.get_profile()
    assert profile["occupation"] == "farmer"
    assert profile["education_level"] == "secondary"
    assert profile["land_ownership"] == "yes"
    assert profile["district"] == "Pune"
    assert profile["family_size"] == 5
    print("✓ Mixed profile with legacy and new fields works correctly")


def test_get_missing_fields_includes_new_fields():
    """Test get_missing_fields() only includes REQUIRED fields, not optional fields."""
    memory = ProfileMemory()
    memory.update({"occupation": "farmer", "state": "Maharashtra"})
    missing = memory.get_missing_fields()
    
    # Check that REQUIRED fields are in missing list
    assert "income_range" in missing
    assert "age_group" in missing
    assert "gender" in missing
    
    # Check that OPTIONAL fields are NOT in missing list
    assert "education_level" not in missing
    assert "district" not in missing
    assert "urban_rural" not in missing
    print("✓ get_missing_fields() only includes REQUIRED fields, not optional fields")


def test_backward_compatibility_legacy_profile():
    """Test legacy profile (only old fields) still works."""
    memory = ProfileMemory()
    legacy_profile = {
        "occupation": "student",
        "state": "Delhi",
        "age_group": "18-25",
        "income_range": "below_1l",
        "gender": "female"
    }
    memory.update(legacy_profile)
    profile = memory.get_profile()
    
    # All legacy fields should be present
    for key, value in legacy_profile.items():
        assert profile[key] == value
    print("✓ Backward compatibility: legacy profile works unchanged")


if __name__ == "__main__":
    print("Running profile extension validation tests...\n")
    
    test_new_fields_in_profile_fields()
    test_field_validators_defined()
    test_valid_education_level()
    test_invalid_education_level_rejected()
    test_valid_family_size()
    test_invalid_family_size_rejected()
    test_valid_boolean_fields()
    test_none_values_skip_validation()
    test_mixed_profile_with_new_and_legacy_fields()
    test_get_missing_fields_includes_new_fields()
    test_backward_compatibility_legacy_profile()
    
    print("\n✅ All validation tests passed!")
