"""
Test Bedrock invocation for complete profiles.

This test verifies that when a user provides a complete profile,
the Bedrock Nova model is invoked to generate AI-enhanced responses.
"""
import os
import pytest
from unittest.mock import Mock, patch

# Set test environment before imports
os.environ["APP_ENV"] = "test"

from orchestration.conversation_manager import ConversationManager
from llm_service.inference_gateway import InferenceGateway
from core.config import config


def _create_bedrock_enabled_manager():
    """Create a ConversationManager with Bedrock enabled."""
    gateway = InferenceGateway()
    # Force Bedrock to be available for testing
    gateway._bedrock_available = True
    return ConversationManager(gateway=gateway)


def test_bedrock_invoked_for_complete_profile():
    """
    Test that Bedrock Nova model generates responses for complete profiles.
    
    This test verifies the acceptance criteria:
    - Bedrock Nova model generates responses for complete profiles
    """
    # Ensure Bedrock is enabled in config
    original_bedrock_enabled = config.BEDROCK_ENABLED
    config.BEDROCK_ENABLED = True
    
    try:
        manager = _create_bedrock_enabled_manager()
        
        # Mock the template response to be short (under threshold)
        with patch.object(manager, '_build_template_response') as mock_template:
            mock_template.return_value = "You are eligible for PM-KISAN."  # Short template (under 300 chars)
            
            # Mock the Bedrock call to return a longer enhanced response
            with patch.object(manager.gateway, 'generate_explanation') as mock_bedrock:
                mock_bedrock.return_value = "Great news! As a 30-year-old farmer from Maharashtra with an annual income of ₹2 lakhs, you are eligible for several government schemes that can significantly benefit you. The PM-KISAN scheme provides ₹6,000 per year directly to your bank account in three installments. This scheme is specifically designed for farmers like you and requires minimal documentation. You can apply online through the official PM-KISAN portal with your Aadhaar card and bank details."
                
                # Mock profile memory to return no missing fields (complete profile)
                with patch.object(manager, '_get_memory') as mock_memory:
                    mock_memory_instance = Mock()
                    mock_memory_instance.update.return_value = {
                        "occupation": "farmer",
                        "state": "Maharashtra", 
                        "age": 30,
                        "income": 200000.0,
                        "age_group": "26-35",
                        "income_range": "1-2.5L",
                        "gender": "male",
                        "disability_status": "no",
                        "caste_category": "general",
                        "farmer_status": "yes",
                        "student_status": "no"
                    }
                    mock_memory_instance.get_profile.return_value = {
                        "occupation": "farmer",
                        "state": "Maharashtra", 
                        "age": 30,
                        "income": 200000.0,
                        "age_group": "26-35",
                        "income_range": "1-2.5L",
                        "gender": "male",
                        "disability_status": "no",
                        "caste_category": "general",
                        "farmer_status": "yes",
                        "student_status": "no"
                    }
                    mock_memory_instance.get_missing_fields.return_value = []  # No missing fields
                    mock_memory.return_value = mock_memory_instance
                    
                    # Provide a complete profile query
                    result = manager.process_user_query(
                        query="I am a 30 year old male farmer from Maharashtra with annual income of 2 lakh rupees",
                        language="en",
                        session_id="test-bedrock-complete-profile"
                    )
                    
                    # Verify that Bedrock was called (mock was invoked)
                    mock_bedrock.assert_called_once()
                    
                    # Verify that the response is AI-enhanced
                    assert result["llm_enhanced"] == True
                    
                    # Verify that llm_metadata is present
                    assert "llm_metadata" in result
                    llm_metadata = result["llm_metadata"]
                    assert llm_metadata["model"] == config.BEDROCK_MODEL_ID
                    assert llm_metadata["latency_ms"] >= 0
                    assert llm_metadata["template_length"] > 0
                    assert llm_metadata["enhanced_length"] > llm_metadata["template_length"]
                    assert llm_metadata["skip_reason"] is None
                    
                    # Verify the response is the enhanced version
                    assert "Great news!" in result["response"]
                    assert len(result["response"]) > 200  # Enhanced response should be longer
            
    finally:
        # Restore original config
        config.BEDROCK_ENABLED = original_bedrock_enabled


def test_bedrock_skipped_for_incomplete_profile():
    """
    Test that Bedrock is skipped when profile is incomplete (missing fields).
    """
    original_bedrock_enabled = config.BEDROCK_ENABLED
    config.BEDROCK_ENABLED = True
    
    try:
        manager = _create_bedrock_enabled_manager()
        
        with patch.object(manager.gateway, 'generate_explanation') as mock_bedrock:
            # Provide an incomplete profile query (missing age, income)
            result = manager.process_user_query(
                query="I am a farmer from Maharashtra",
                language="en",
                session_id="test-bedrock-incomplete-profile"
            )
            
            # Verify that Bedrock was NOT called due to missing fields
            mock_bedrock.assert_not_called()
            
            # Verify that the response is NOT AI-enhanced
            assert result["llm_enhanced"] == False
            
            # Verify that llm_metadata indicates skip reason
            assert "llm_metadata" in result
            assert result["llm_metadata"]["skip_reason"] == "profile_incomplete"
            
            # Verify that a structured question is returned for missing fields
            assert "question" in result
            assert result["question"] is not None
            
    finally:
        config.BEDROCK_ENABLED = original_bedrock_enabled


def test_bedrock_skipped_when_disabled():
    """
    Test that Bedrock is skipped when BEDROCK_ENABLED is False.
    """
    original_bedrock_enabled = config.BEDROCK_ENABLED
    config.BEDROCK_ENABLED = False
    
    try:
        manager = _create_bedrock_enabled_manager()
        
        with patch.object(manager.gateway, 'generate_explanation') as mock_bedrock:
            # Mock profile memory to return complete profile
            with patch.object(manager, '_get_memory') as mock_memory:
                mock_memory_instance = Mock()
                mock_memory_instance.update.return_value = {}
                mock_memory_instance.get_profile.return_value = {
                    "occupation": "farmer",
                    "state": "Maharashtra", 
                    "income_range": "1-2.5L",
                    "age_group": "26-35",
                    "gender": "male",
                    "disability_status": "none",
                    "caste_category": "general",
                    "farmer_status": "yes",
                    "student_status": "no"
                }
                mock_memory_instance.get_missing_fields.return_value = []  # Complete profile
                mock_memory_instance.is_complete = True
                mock_memory.return_value = mock_memory_instance
                
                # Mock profile extraction
                with patch('llm_service.profile_extractor.extract_profile') as mock_extract:
                    mock_extract.return_value = {"profile": {}}
                    
                    # Mock eligibility evaluation
                    with patch.object(manager, 'evaluate') as mock_eval:
                        mock_eval.return_value = {"eligible": [{"scheme_id": "PM_KISAN"}], "partially_eligible": [], "ineligible": []}
                        
                        # Provide a complete profile query
                        result = manager.process_user_query(
                            query="I am a 30 year old farmer from Maharashtra with annual income of 2 lakh rupees",
                            language="en",
                            session_id="test-bedrock-disabled"
                        )
                        
                        # Verify that Bedrock was NOT called due to being disabled
                        mock_bedrock.assert_not_called()
                        
                        # Verify that the response is NOT AI-enhanced
                        assert result["llm_enhanced"] == False
                        
                        # Verify that llm_metadata indicates skip reason
                        assert "llm_metadata" in result
                        assert result["llm_metadata"]["skip_reason"] == "bedrock_disabled"
            
    finally:
        config.BEDROCK_ENABLED = original_bedrock_enabled


def test_bedrock_threshold_configuration():
    """
    Test that the new threshold (300 characters) allows longer templates to be enhanced.
    """
    original_bedrock_enabled = config.BEDROCK_ENABLED
    original_threshold = config.LLM_ENHANCEMENT_THRESHOLD
    config.BEDROCK_ENABLED = True
    config.LLM_ENHANCEMENT_THRESHOLD = 300  # Ensure it's set to 300
    
    try:
        manager = _create_bedrock_enabled_manager()
        
        # Mock the template response to be around 250 characters (below 300 threshold)
        with patch.object(manager, '_build_template_response') as mock_template:
            mock_template.return_value = "Based on your profile, you are eligible for PM-KISAN (₹6000/year for farmers). You are also eligible for MUDRA Loan (up to ₹10 lakh for business). Apply online with Aadhaar card and bank details. Visit official portals for more information."
            
            # Mock profile memory to return no missing fields (complete profile)
            with patch.object(manager, '_get_memory') as mock_memory:
                mock_memory_instance = Mock()
                mock_memory_instance.update.return_value = {}  # No conflicts - return empty update
                mock_memory_instance.get_profile.return_value = {
                    "occupation": "farmer",
                    "state": "Maharashtra", 
                    "age": 30,
                    "income": 200000.0,
                    "age_group": "26-35",
                    "income_range": "1-2.5L",
                    "gender": "male",
                    "disability_status": "no",
                    "caste_category": "general",
                    "farmer_status": "yes",
                    "student_status": "no"
                }
                mock_memory_instance.get_missing_fields.return_value = []  # No missing fields
                mock_memory_instance.is_complete = True  # Explicitly set complete
                mock_memory.return_value = mock_memory_instance
                
                # Mock profile extraction to avoid conflicts
                with patch('llm_service.profile_extractor.extract_profile') as mock_extract:
                    mock_extract.return_value = {"profile": {}}  # Empty extraction to avoid conflicts
                
                with patch.object(manager.gateway, 'generate_explanation') as mock_bedrock:
                    # Mock a longer enhanced response
                    mock_bedrock.return_value = "This is a much longer AI-enhanced response that provides detailed explanations about the schemes and eligibility criteria in simple language that users can understand easily. The PM-KISAN scheme provides ₹6,000 per year directly to your bank account in three installments of ₹2,000 each. This scheme is specifically designed for farmers like you and requires minimal documentation. You can apply online through the official PM-KISAN portal with your Aadhaar card and bank details. Additionally, the MUDRA Loan scheme can provide up to ₹10 lakh for agricultural activities or small business ventures. Both schemes are excellent opportunities for farmers in Maharashtra to improve their financial situation and expand their agricultural operations."
                    
                    result = manager.process_user_query(
                        query="I am a 30 year old farmer from Maharashtra with annual income of 2 lakh rupees",
                        language="en",
                        session_id="test-threshold-300"
                    )
                    
                    # Verify that Bedrock was called (template < 300 chars)
                    mock_bedrock.assert_called_once()
                    
                    # Verify that the response is AI-enhanced
                    assert result["llm_enhanced"] == True
                    
    finally:
        config.BEDROCK_ENABLED = original_bedrock_enabled
        config.LLM_ENHANCEMENT_THRESHOLD = original_threshold


if __name__ == "__main__":
    # Run the tests
    test_bedrock_invoked_for_complete_profile()
    test_bedrock_skipped_for_incomplete_profile()
    test_bedrock_skipped_when_disabled()
    test_bedrock_threshold_configuration()
    print("All Bedrock invocation tests passed!")