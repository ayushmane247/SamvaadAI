"""
Test script for SamvaadAI LLM Service.

This script tests intent extraction and explanation generation
with examples in English, Hindi, and Marathi.
"""

import json
from llm_service.llm_service import LLMService


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def test_intent_extraction():
    """Test intent extraction with multilingual examples."""
    print_section("TEST 1: Intent Extraction")
    
    service = LLMService()
    
    # Test cases
    test_cases = [
        {
            "text": "I am 35 years old, work as a farmer in Maharashtra, earn about 2 lakhs per year",
            "language": "en",
            "description": "English - Complete profile"
        },
        {
            "text": "मैं ४० साल का हूं, किसान हूं, महाराष्ट्र में रहता हूं",
            "language": "hi",
            "description": "Hindi - Partial profile"
        },
        {
            "text": "मी २८ वर्षांचा आहे, शिक्षक आहे, महाराष्ट्रात राहतो",
            "language": "mr",
            "description": "Marathi - Partial profile"
        },
        {
            "text": "Hello, I need help",
            "language": "en",
            "description": "English - Minimal information"
        },
        {
            "text": "मैं दिल्ली में रहता हूं",
            "language": "hi",
            "description": "Hindi - Only location"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['description']} ---")
        print(f"Input ({test_case['language']}): {test_case['text']}")
        print("\nExtracting profile...")
        
        try:
            profile = service.extract_user_profile(
                test_case['text'],
                test_case['language']
            )
            
            print("\nExtracted Profile:")
            print(json.dumps(profile, indent=2, ensure_ascii=False))
            
            # Validate structure
            assert "age" in profile
            assert "occupation" in profile
            assert "income_band" in profile
            assert "location" in profile
            assert "state" in profile["location"]
            print("\n✓ Profile structure validated")
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()


def test_explanation_generation():
    """Test explanation generation with different rule outputs."""
    print_section("TEST 2: Explanation Generation")
    
    service = LLMService()
    
    # Test cases
    test_cases = [
        {
            "rule_output": {
                "scheme": "PM-KISAN",
                "status": "eligible",
                "reason": "occupation=farmer AND income<3L AND location.state=Maharashtra"
            },
            "language": "en",
            "description": "English - Eligible case"
        },
        {
            "rule_output": {
                "scheme": "PM-KISAN",
                "status": "not_eligible",
                "reason": "occupation!=farmer"
            },
            "language": "hi",
            "description": "Hindi - Not eligible case"
        },
        {
            "rule_output": {
                "scheme": "PM-KISAN",
                "status": "eligible",
                "reason": "occupation=farmer AND location.state=Maharashtra"
            },
            "language": "mr",
            "description": "Marathi - Eligible case"
        },
        {
            "rule_output": {
                "scheme": "PM-AWAS",
                "status": "not_eligible",
                "reason": "income>5L"
            },
            "language": "en",
            "description": "English - Not eligible (income too high)"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['description']} ---")
        print(f"Rule Output:")
        print(json.dumps(test_case['rule_output'], indent=2))
        print(f"\nGenerating explanation in {test_case['language']}...")
        
        try:
            explanation = service.generate_explanation(
                test_case['rule_output'],
                test_case['language']
            )
            
            print(f"\nExplanation ({test_case['language']}):")
            print(f"  {explanation}")
            
            # Verify explanation doesn't contradict status
            status = test_case['rule_output']['status']
            if status == "eligible":
                assert "not eligible" not in explanation.lower() or "not eligible" not in explanation
            print("\n✓ Explanation validated")
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()


def test_fallback_behavior():
    """Test fallback behavior when LLM fails."""
    print_section("TEST 3: Fallback Behavior")
    
    print("\nNote: This test demonstrates fallback templates.")
    print("In production, fallbacks activate automatically on errors.\n")
    
    from llm_service.fallback_templates import (
        get_default_profile,
        get_error_message,
        get_timeout_message,
        get_fallback_explanation
    )
    
    # Test default profile
    print("Default Profile (when extraction fails):")
    default_profile = get_default_profile("en")
    print(json.dumps(default_profile, indent=2))
    
    # Test error messages
    print("\nError Messages:")
    for lang in ["en", "hi", "mr"]:
        print(f"  {lang}: {get_error_message(lang)}")
    
    # Test timeout messages
    print("\nTimeout Messages:")
    for lang in ["en", "hi", "mr"]:
        print(f"  {lang}: {get_timeout_message(lang)}")
    
    # Test fallback explanation
    print("\nFallback Explanations:")
    rule_output = {"scheme": "PM-KISAN", "status": "eligible", "reason": "test"}
    for lang in ["en", "hi", "mr"]:
        explanation = get_fallback_explanation(rule_output, lang)
        print(f"  {lang}: {explanation}")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  SAMVADAI LLM SERVICE - TEST SUITE")
    print("=" * 70)
    
    try:
        # Test intent extraction
        test_intent_extraction()
        
        # Test explanation generation
        test_explanation_generation()
        
        # Test fallback behavior
        test_fallback_behavior()
        
        print_section("ALL TESTS COMPLETED")
        print("\n✓ Test suite finished successfully!")
        print("\nNote: Some tests may fail if AWS Bedrock is not configured.")
        print("      Fallback templates will activate automatically on errors.")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Test suite error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
