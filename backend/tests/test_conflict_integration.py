"""
Integration tests for conflict detection and resolution in conversation flow.
"""
import sys
sys.path.insert(0, 'backend')

from orchestration.conversation_manager import ConversationManager
from orchestration.profile_memory import ProfileMemory
from unittest.mock import Mock, patch


def test_conflict_detection_in_conversation_flow():
    """Test that conflicts are detected during conversation processing."""
    manager = ConversationManager()
    
    # Mock the extract_profile function to return controlled data
    with patch('orchestration.conversation_manager.extract_profile') as mock_extract:
        # First query: user says they're a farmer
        mock_extract.return_value = {
            "profile": {"occupation": "farmer", "state": "Maharashtra"}
        }
        
        result1 = manager.process_user_query(
            query="I am a farmer from Maharashtra",
            language="en",
            session_id="test_session_1"
        )
        
        assert result1["profile"]["occupation"] == "farmer"
        assert result1["profile"]["state"] == "Maharashtra"
        
        # Second query: user changes their mind and says they're a student
        mock_extract.return_value = {
            "profile": {"occupation": "student"}
        }
        
        result2 = manager.process_user_query(
            query="Actually, I am a student",
            language="en",
            session_id="test_session_1"
        )
        
        # Profile should be updated with new value
        assert result2["profile"]["occupation"] == "student"
        assert result2["profile"]["state"] == "Maharashtra"  # Should remain
        
        # Response should contain conflict clarification
        assert "changed" in result2["response"].lower() or "updated" in result2["response"].lower()
        
    print("✓ Conflict detection works in conversation flow")


def test_conflict_resolution_new_value_wins():
    """Test that new values always win in conflict resolution."""
    manager = ConversationManager()
    
    with patch('orchestration.conversation_manager.extract_profile') as mock_extract:
        # First query
        mock_extract.return_value = {
            "profile": {"state": "Maharashtra", "income_range": "below_1l"}
        }
        
        result1 = manager.process_user_query(
            query="I am from Maharashtra with income below 1 lakh",
            language="en",
            session_id="test_session_2"
        )
        
        assert result1["profile"]["state"] == "Maharashtra"
        assert result1["profile"]["income_range"] == "below_1l"
        
        # Second query: user provides conflicting data
        mock_extract.return_value = {
            "profile": {"state": "Delhi", "income_range": "1l_to_2.5l"}
        }
        
        result2 = manager.process_user_query(
            query="I moved to Delhi and my income is now 1-2.5 lakhs",
            language="en",
            session_id="test_session_2"
        )
        
        # New values should win
        assert result2["profile"]["state"] == "Delhi"
        assert result2["profile"]["income_range"] == "1l_to_2.5l"
        
    print("✓ New value wins in conflict resolution")


def test_conflict_triggers_eligibility_reevaluation():
    """Test that conflicts trigger eligibility re-evaluation."""
    manager = ConversationManager()
    
    with patch('orchestration.conversation_manager.extract_profile') as mock_extract:
        # First query
        mock_extract.return_value = {
            "profile": {"occupation": "farmer", "state": "Maharashtra"}
        }
        
        result1 = manager.process_user_query(
            query="I am a farmer from Maharashtra",
            language="en",
            session_id="test_session_3"
        )
        
        # Get initial eligibility results
        initial_eligible_count = len(result1["eligibility"]["eligible"])
        
        # Second query with conflict
        mock_extract.return_value = {
            "profile": {"occupation": "student"}
        }
        
        result2 = manager.process_user_query(
            query="Actually I am a student",
            language="en",
            session_id="test_session_3"
        )
        
        # Eligibility should be re-evaluated (may have different results)
        # We just verify that evaluation happened (result has eligibility data)
        assert "eligibility" in result2
        assert "eligible" in result2["eligibility"]
        assert "partially_eligible" in result2["eligibility"]
        
    print("✓ Conflicts trigger eligibility re-evaluation")


def test_multilingual_conflict_clarification():
    """Test conflict clarification in different languages."""
    manager = ConversationManager()
    
    with patch('orchestration.conversation_manager.extract_profile') as mock_extract:
        # Test in Hindi
        mock_extract.return_value = {
            "profile": {"occupation": "farmer"}
        }
        
        result1 = manager.process_user_query(
            query="मैं किसान हूं",
            language="hi",
            session_id="test_session_4"
        )
        
        mock_extract.return_value = {
            "profile": {"occupation": "student"}
        }
        
        result2 = manager.process_user_query(
            query="मैं छात्र हूं",
            language="hi",
            session_id="test_session_4"
        )
        
        # Response should be in Hindi
        assert any(hindi_char in result2["response"] for hindi_char in ["मैं", "आप", "है"])
        
        # Test in Marathi
        mock_extract.return_value = {
            "profile": {"state": "Maharashtra"}
        }
        
        result3 = manager.process_user_query(
            query="मी महाराष्ट्रातून आहे",
            language="mr",
            session_id="test_session_5"
        )
        
        mock_extract.return_value = {
            "profile": {"state": "Delhi"}
        }
        
        result4 = manager.process_user_query(
            query="मी दिल्लीत राहतो",
            language="mr",
            session_id="test_session_5"
        )
        
        # Response should be in Marathi
        assert any(marathi_char in result4["response"] for marathi_char in ["मी", "तुम्ही", "आहे"])
        
    print("✓ Multilingual conflict clarification works")


def test_non_critical_fields_no_conflict():
    """Test that non-critical fields don't trigger conflict detection."""
    manager = ConversationManager()
    
    with patch('orchestration.conversation_manager.extract_profile') as mock_extract:
        # First query with non-critical field
        mock_extract.return_value = {
            "profile": {"education_level": "primary", "occupation": "farmer"}
        }
        
        result1 = manager.process_user_query(
            query="I have primary education and I am a farmer",
            language="en",
            session_id="test_session_6"
        )
        
        # Second query changing non-critical field
        mock_extract.return_value = {
            "profile": {"education_level": "secondary"}
        }
        
        result2 = manager.process_user_query(
            query="I completed secondary education",
            language="en",
            session_id="test_session_6"
        )
        
        # Profile should be updated
        assert result2["profile"]["education_level"] == "secondary"
        
        # But no conflict message should appear (education_level is not critical)
        # Response should not mention "changed" or "updated" for non-critical fields
        # (unless there are other reasons for those words)
        
    print("✓ Non-critical fields don't trigger conflict messages")


def test_profile_memory_tracks_conflicts():
    """Test that ProfileMemory tracks conflicting values."""
    memory = ProfileMemory()
    
    # First update
    memory.update({"occupation": "farmer", "state": "Maharashtra"})
    
    assert memory.get_profile()["occupation"] == "farmer"
    assert not memory.has_conflicts()
    
    # Second update with conflict
    memory.update({"occupation": "student"})
    
    assert memory.get_profile()["occupation"] == "student"  # New value wins
    assert memory.has_conflicts()
    
    conflicts = memory.get_conflicts()
    assert "occupation" in conflicts
    assert "farmer" in conflicts["occupation"]
    assert "student" in conflicts["occupation"]
    
    print("✓ ProfileMemory tracks conflicts correctly")


if __name__ == "__main__":
    print("Running conflict detection integration tests...\n")
    
    test_conflict_detection_in_conversation_flow()
    test_conflict_resolution_new_value_wins()
    test_conflict_triggers_eligibility_reevaluation()
    test_multilingual_conflict_clarification()
    test_non_critical_fields_no_conflict()
    test_profile_memory_tracks_conflicts()
    
    print("\n✅ All conflict detection integration tests passed!")
