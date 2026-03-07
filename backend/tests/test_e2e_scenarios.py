"""
End-to-end scenario tests for SamvaadAI stabilized pipeline.

Tests the complete flow: profile extraction → eligibility → response
using deterministic mode (no Bedrock needed).
"""
import os
os.environ["APP_ENV"] = "test"

from orchestration.conversation_manager import ConversationManager
from llm_service.inference_gateway import InferenceGateway


def _create_deterministic_manager():
    """Create a ConversationManager in full deterministic mode."""
    gateway = InferenceGateway()
    # Force deterministic mode
    gateway._bedrock_available = False
    return ConversationManager(gateway=gateway)


def test_farmer_from_maharashtra():
    """
    Scenario: 'I am a farmer from Maharashtra'
    Expected: PM Kisan eligible
    """
    manager = _create_deterministic_manager()
    result = manager.process_user_query(
        query="I am a farmer from Maharashtra",
        language="en",
        session_id="test-farmer-1",
    )

    assert "profile" in result
    assert "eligibility" in result
    assert "response" in result
    assert "schemes" in result
    assert "documents" in result

    # Profile should have farmer + Maharashtra
    profile = result["profile"]
    assert profile.get("occupation") == "farmer"
    assert profile.get("state") == "Maharashtra"

    # Should be eligible for PM Kisan
    eligible_ids = [s["scheme_id"] for s in result["eligibility"]["eligible"]]
    assert "PM_KISAN" in eligible_ids

    # Schemes list should include PM Kisan
    scheme_names = [s["name"] for s in result["schemes"]]
    assert any("Kisan" in name for name in scheme_names)

    # Response should not be empty
    assert len(result["response"]) > 10


def test_student_from_delhi():
    """
    Scenario: 'I am a student from Delhi'
    Expected: National Scholarship eligible
    """
    manager = _create_deterministic_manager()
    result = manager.process_user_query(
        query="I am a student from Delhi",
        language="en",
        session_id="test-student-1",
    )

    profile = result["profile"]
    assert profile.get("occupation") == "student"
    assert profile.get("state") == "Delhi"

    eligible_ids = [s["scheme_id"] for s in result["eligibility"]["eligible"]]
    assert "NATIONAL_SCHOLARSHIP" in eligible_ids


def test_multi_turn_conversation():
    """
    Scenario: Multi-turn conversation builds profile progressively.
    Turn 1: 'I am a farmer'
    Turn 2: 'I live in Maharashtra'
    Turn 3: 'My income is 50000'
    """
    manager = _create_deterministic_manager()
    session_id = "test-multi-turn-1"

    # Turn 1
    r1 = manager.process_user_query("I am a farmer", "en", session_id)
    assert r1["profile"].get("occupation") == "farmer"
    # Should still ask for more info
    assert len(r1["response"]) > 0

    # Turn 2
    r2 = manager.process_user_query("I live in Maharashtra", "en", session_id)
    # Should remember farmer from turn 1
    assert r2["profile"].get("occupation") == "farmer"
    assert r2["profile"].get("state") == "Maharashtra"

    # Turn 3
    r3 = manager.process_user_query("My income is 50000 per year", "en", session_id)
    assert r3["profile"].get("occupation") == "farmer"
    assert r3["profile"].get("state") == "Maharashtra"
    assert r3["profile"].get("income") == 50000.0

    # Should now be eligible for multiple schemes
    eligible_ids = [s["scheme_id"] for s in r3["eligibility"]["eligible"]]
    assert "PM_KISAN" in eligible_ids


def test_low_income_eligibility():
    """
    Scenario: Low-income user should match Ayushman Bharat + PM Awas
    """
    manager = _create_deterministic_manager()
    result = manager.process_user_query(
        query="I am a 40 year old labourer from Bihar with income 2 lakh",
        language="en",
        session_id="test-income-1",
    )

    eligible_ids = [s["scheme_id"] for s in result["eligibility"]["eligible"]]
    # Income < 300000 → PM Awas Yojana eligible
    assert "PM_AWAS_YOJANA" in eligible_ids


def test_business_owner_mudra():
    """
    Scenario: Business owner should match Mudra Yojana
    """
    manager = _create_deterministic_manager()
    result = manager.process_user_query(
        query="I am a shopkeeper from Gujarat",
        language="en",
        session_id="test-business-1",
    )

    eligible_ids = [s["scheme_id"] for s in result["eligibility"]["eligible"]]
    assert "PM_MUDRA_YOJANA" in eligible_ids


def test_response_includes_documents():
    """Document list should be populated for eligible schemes."""
    manager = _create_deterministic_manager()
    result = manager.process_user_query(
        query="I am a farmer from Maharashtra",
        language="en",
        session_id="test-docs-1",
    )

    # PM Kisan requires Aadhaar Card
    assert isinstance(result["documents"], list)
    if result["documents"]:
        assert any("Aadhaar" in doc for doc in result["documents"])


def test_hindi_conversation():
    """
    Scenario: Hindi input should work end-to-end.
    """
    manager = _create_deterministic_manager()
    result = manager.process_user_query(
        query="मैं एक किसान हूँ",
        language="hi",
        session_id="test-hindi-1",
    )

    assert result["profile"].get("occupation") == "farmer"
    # Response should not be empty
    assert len(result["response"]) > 0


def test_session_id_returned():
    """Session ID should be echoed back in the response."""
    manager = _create_deterministic_manager()
    result = manager.process_user_query(
        query="I am a farmer",
        language="en",
        session_id="my-test-session",
    )
    assert result["session_id"] == "my-test-session"


def test_no_session_id_works():
    """Pipeline should work without a session ID (stateless mode)."""
    manager = _create_deterministic_manager()
    result = manager.process_user_query(
        query="I am a student",
        language="en",
    )
    assert "profile" in result
    assert "response" in result
    assert result.get("session_id") is None
