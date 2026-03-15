"""
Validation tests for adaptive questioning feature.
"""
import sys
sys.path.insert(0, 'backend')

from orchestration.conversation_manager import AdaptiveQuestioningEngine, ConversationManager
from orchestration.question_generator import QuestionGenerator
from orchestration.adaptive_types import MissingAttribute, SchemeCriteria, SKIP_KEYWORDS, Conflict, CRITICAL_FIELDS


def test_adaptive_engine_initialization():
    """Test AdaptiveQuestioningEngine initializes correctly."""
    question_gen = QuestionGenerator()
    engine = AdaptiveQuestioningEngine(question_gen)
    
    assert engine.question_gen is question_gen
    assert isinstance(engine._criteria_cache, dict)
    assert len(engine._criteria_cache) == 0
    print("✓ AdaptiveQuestioningEngine initializes correctly")


def test_parse_scheme_criteria():
    """Test scheme criteria parsing with validation."""
    question_gen = QuestionGenerator()
    engine = AdaptiveQuestioningEngine(question_gen)
    
    schemes = [
        {
            "scheme_id": "test_scheme_1",
            "scheme_name": "Test Scheme 1",
            "eligibility_criteria": [
                {"field": "occupation", "operator": "equals", "value": "farmer"},
                {"field": "state", "operator": "equals", "value": "Maharashtra"},
            ],
            "logic": "AND",
            "benefit_summary": "Get ₹10 lakh subsidy"
        },
        {
            "scheme_id": "test_scheme_2",
            "scheme_name": "Test Scheme 2",
            "eligibility_criteria": [
                {"field": "age_group", "operator": "in", "value": ["18-25", "26-35"]},
            ],
            "logic": "OR",
            "benefit_summary": "Education support"
        }
    ]
    
    criteria_map = engine.parse_scheme_criteria(schemes)
    
    assert len(criteria_map) == 2
    assert "test_scheme_1" in criteria_map
    assert "test_scheme_2" in criteria_map
    
    scheme1 = criteria_map["test_scheme_1"]
    assert scheme1.logic == "AND"
    assert "occupation" in scheme1.required_fields
    assert "state" in scheme1.required_fields
    assert scheme1.is_high_value  # Contains "lakh"
    
    scheme2 = criteria_map["test_scheme_2"]
    assert scheme2.logic == "OR"
    assert "age_group" in scheme2.required_fields
    assert not scheme2.is_high_value
    
    print("✓ Scheme criteria parsing works correctly")


def test_analyze_missing_attributes():
    """Test missing attribute identification."""
    question_gen = QuestionGenerator()
    engine = AdaptiveQuestioningEngine(question_gen)
    
    profile = {
        "occupation": "farmer",
        "state": "Maharashtra"
    }
    
    schemes = [
        {
            "scheme_id": "scheme1",
            "scheme_name": "Scheme 1",
            "eligibility_criteria": [
                {"field": "occupation", "operator": "equals", "value": "farmer"},
                {"field": "state", "operator": "equals", "value": "Maharashtra"},
                {"field": "income_range", "operator": "in", "value": ["below_1l", "1l_to_2.5l"]},
            ],
            "logic": "AND",
            "benefit_summary": "Farmer support"
        }
    ]
    
    missing_attrs = engine.analyze_missing_attributes(profile, schemes)
    
    assert len(missing_attrs) == 1
    assert missing_attrs[0].field == "income_range"
    assert "scheme1" in missing_attrs[0].required_by_schemes
    
    print("✓ Missing attribute identification works correctly")


def test_calculate_priority():
    """Test priority calculation."""
    question_gen = QuestionGenerator()
    engine = AdaptiveQuestioningEngine(question_gen)
    
    profile = {"occupation": "farmer"}
    
    schemes = [
        {
            "scheme_id": "scheme1",
            "scheme_name": "Scheme 1",
            "eligibility_criteria": [
                {"field": "occupation", "operator": "equals", "value": "farmer"},
                {"field": "state", "operator": "equals", "value": "Maharashtra"},
            ],
            "logic": "AND",
            "benefit_summary": "Get ₹5 lakh"
        }
    ]
    
    criteria_map = engine.parse_scheme_criteria(schemes)
    
    missing_attr = MissingAttribute(
        field="state",
        required_by_schemes=["scheme1"],
        logic_types={"scheme1": "AND"},
        is_high_value=criteria_map["scheme1"].is_high_value  # Get from parsed criteria
    )
    
    priority = engine.calculate_priority(missing_attr, profile, criteria_map)
    
    assert priority > 0
    assert missing_attr.scheme_unlock_count == 1  # Only missing state
    # High value boost should be applied
    assert priority >= 10 * 1.2  # Base 10 with 20% boost
    
    print("✓ Priority calculation works correctly")


def test_apply_relevance_filter():
    """Test relevance filtering."""
    question_gen = QuestionGenerator()
    engine = AdaptiveQuestioningEngine(question_gen)
    
    profile = {
        "occupation": "farmer",
        "age_group": "46-60"
    }
    
    missing_attrs = [
        MissingAttribute(field="farmer_status", priority_score=10.0),
        MissingAttribute(field="student_status", priority_score=10.0),
        MissingAttribute(field="state", priority_score=10.0),
    ]
    
    filtered = engine.apply_relevance_filter(missing_attrs, profile)
    
    # farmer_status should be filtered (occupation=farmer)
    # student_status should be filtered (age_group=46-60)
    # state should remain
    assert len(filtered) == 1
    assert filtered[0].field == "state"
    
    print("✓ Relevance filtering works correctly")


def test_skip_keywords_defined():
    """Test skip keywords are defined for all languages."""
    assert "en" in SKIP_KEYWORDS
    assert "hi" in SKIP_KEYWORDS
    assert "mr" in SKIP_KEYWORDS
    
    assert "skip" in SKIP_KEYWORDS["en"]
    assert "छोड़ें" in SKIP_KEYWORDS["hi"]
    assert "वगळा" in SKIP_KEYWORDS["mr"]
    
    print("✓ Skip keywords defined for all languages")


def test_missing_attribute_dataclass():
    """Test MissingAttribute dataclass."""
    attr = MissingAttribute(
        field="education_level",
        required_by_schemes=["scheme1", "scheme2"],
        scheme_unlock_count=2,
        priority_score=25.0
    )
    
    assert attr.field == "education_level"
    assert len(attr.required_by_schemes) == 2
    assert attr.scheme_unlock_count == 2
    assert attr.priority_score == 25.0
    
    print("✓ MissingAttribute dataclass works correctly")


def test_scheme_criteria_dataclass():
    """Test SchemeCriteria dataclass."""
    criteria = SchemeCriteria(
        scheme_id="test_scheme",
        scheme_name="Test Scheme",
        required_fields={"occupation", "state", "income_range"},
        logic="AND",
        is_high_value=True
    )
    
    assert criteria.scheme_id == "test_scheme"
    assert len(criteria.required_fields) == 3
    assert criteria.logic == "AND"
    assert criteria.is_high_value
    
    print("✓ SchemeCriteria dataclass works correctly")


def test_conflict_dataclass():
    """Test Conflict dataclass."""
    conflict = Conflict(
        field="occupation",
        old_value="farmer",
        new_value="student",
        resolution="new_value_wins"
    )
    
    assert conflict.field == "occupation"
    assert conflict.old_value == "farmer"
    assert conflict.new_value == "student"
    assert conflict.resolution == "new_value_wins"
    assert conflict.timestamp > 0
    
    print("✓ Conflict dataclass works correctly")


def test_detect_conflicts_no_conflicts():
    """Test conflict detection with no conflicts."""
    manager = ConversationManager()
    
    old_profile = {"occupation": "farmer", "state": "Maharashtra"}
    new_profile = {"income_range": "below_1l"}  # No overlapping fields
    
    conflicts = manager._detect_conflicts(old_profile, new_profile)
    
    assert len(conflicts) == 0
    print("✓ No conflicts detected when profiles don't overlap")


def test_detect_conflicts_single_conflict():
    """Test conflict detection with single conflict."""
    manager = ConversationManager()
    
    old_profile = {"occupation": "farmer", "state": "Maharashtra"}
    new_profile = {"occupation": "student"}  # Conflicts with occupation
    
    conflicts = manager._detect_conflicts(old_profile, new_profile)
    
    assert len(conflicts) == 1
    assert conflicts[0].field == "occupation"
    assert conflicts[0].old_value == "farmer"
    assert conflicts[0].new_value == "student"
    assert conflicts[0].resolution == "new_value_wins"
    
    print("✓ Single conflict detected correctly")


def test_detect_conflicts_multiple_conflicts():
    """Test conflict detection with multiple conflicts."""
    manager = ConversationManager()
    
    old_profile = {
        "occupation": "farmer",
        "state": "Maharashtra",
        "income_range": "below_1l"
    }
    new_profile = {
        "occupation": "student",
        "state": "Delhi",
        "age_group": "18-25"  # No conflict
    }
    
    conflicts = manager._detect_conflicts(old_profile, new_profile)
    
    assert len(conflicts) == 2
    conflict_fields = {c.field for c in conflicts}
    assert "occupation" in conflict_fields
    assert "state" in conflict_fields
    
    print("✓ Multiple conflicts detected correctly")


def test_detect_conflicts_critical_fields_only():
    """Test that only critical fields trigger conflict detection."""
    manager = ConversationManager()
    
    old_profile = {
        "occupation": "farmer",  # Critical field
        "education_level": "primary"  # Non-critical field
    }
    new_profile = {
        "occupation": "student",  # Should trigger conflict
        "education_level": "secondary"  # Should NOT trigger conflict
    }
    
    conflicts = manager._detect_conflicts(old_profile, new_profile)
    
    # Only occupation should be detected (it's in CRITICAL_FIELDS)
    assert len(conflicts) == 1
    assert conflicts[0].field == "occupation"
    
    print("✓ Only critical fields trigger conflict detection")


def test_build_conflict_clarification_english():
    """Test conflict clarification message in English."""
    manager = ConversationManager()
    
    conflicts = [
        Conflict(
            field="occupation",
            old_value="farmer",
            new_value="student",
            resolution="new_value_wins"
        )
    ]
    
    message = manager._build_conflict_clarification(conflicts, "en")
    
    assert "occupation" in message.lower()
    assert "farmer" in message
    assert "student" in message
    assert len(message) > 0
    
    print("✓ Conflict clarification in English works correctly")


def test_build_conflict_clarification_hindi():
    """Test conflict clarification message in Hindi."""
    manager = ConversationManager()
    
    conflicts = [
        Conflict(
            field="state",
            old_value="Maharashtra",
            new_value="Delhi",
            resolution="new_value_wins"
        )
    ]
    
    message = manager._build_conflict_clarification(conflicts, "hi")
    
    assert "राज्य" in message  # "state" in Hindi
    assert len(message) > 0
    
    print("✓ Conflict clarification in Hindi works correctly")


def test_build_conflict_clarification_marathi():
    """Test conflict clarification message in Marathi."""
    manager = ConversationManager()
    
    conflicts = [
        Conflict(
            field="income_range",
            old_value="below_1l",
            new_value="1l_to_2.5l",
            resolution="new_value_wins"
        )
    ]
    
    message = manager._build_conflict_clarification(conflicts, "mr")
    
    assert "उत्पन्न" in message  # "income" in Marathi
    assert len(message) > 0
    
    print("✓ Conflict clarification in Marathi works correctly")


def test_build_conflict_clarification_multiple_conflicts():
    """Test conflict clarification with multiple conflicts."""
    manager = ConversationManager()
    
    conflicts = [
        Conflict(field="occupation", old_value="farmer", new_value="student"),
        Conflict(field="state", old_value="Maharashtra", new_value="Delhi"),
    ]
    
    message = manager._build_conflict_clarification(conflicts, "en")
    
    # Should have a generic message for multiple conflicts
    assert len(message) > 0
    assert "updated" in message.lower() or "changed" in message.lower()
    
    print("✓ Multiple conflicts clarification works correctly")


def test_build_conflict_clarification_empty():
    """Test conflict clarification with no conflicts."""
    manager = ConversationManager()
    
    message = manager._build_conflict_clarification([], "en")
    
    assert message == ""
    
    print("✓ Empty conflict list returns empty message")


if __name__ == "__main__":
    print("Running adaptive questioning validation tests...\n")
    
    test_adaptive_engine_initialization()
    test_parse_scheme_criteria()
    test_analyze_missing_attributes()
    test_calculate_priority()
    test_apply_relevance_filter()
    test_skip_keywords_defined()
    test_missing_attribute_dataclass()
    test_scheme_criteria_dataclass()
    test_conflict_dataclass()
    test_detect_conflicts_no_conflicts()
    test_detect_conflicts_single_conflict()
    test_detect_conflicts_multiple_conflicts()
    test_detect_conflicts_critical_fields_only()
    test_build_conflict_clarification_english()
    test_build_conflict_clarification_hindi()
    test_build_conflict_clarification_marathi()
    test_build_conflict_clarification_multiple_conflicts()
    test_build_conflict_clarification_empty()
    
    print("\n✅ All adaptive questioning validation tests passed!")
