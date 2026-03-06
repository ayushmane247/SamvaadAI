"""
Integration Test - Full SamvaadAI Pipeline Simulation.

Simulates complete flow without AWS credentials:
User Input -> Profile (simulated) -> Mock Rule Engine -> Explanation
"""

import json
import sys

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
from typing import Dict, Any

from llm_service.llm_service import LLMService
from llm_service.config import LANGUAGE_NAMES


def _evaluate_mock_rules(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Inline mock rule engine for integration testing."""
    occupation = str(profile.get("occupation", "")).lower()
    if occupation == "farmer":
        return {"scheme": "PM-KISAN", "status": "eligible", "reason": "occupation=farmer"}
    return {"scheme": "PM-KISAN", "status": "not_eligible", "reason": f"occupation={occupation}"}


def _normalize_rule_output(data: Any) -> Dict[str, Any]:
    """Inline normalize for integration testing."""
    if not isinstance(data, dict):
        return {"scheme": "Unknown", "status": "partially_eligible", "reason": "invalid"}
    return {
        "scheme": data.get("scheme", "Unknown"),
        "status": data.get("status", "partially_eligible"),
        "reason": data.get("reason", ""),
    }


def _print_stage(title: str, content: Any, is_json: bool = False) -> None:
    """Print a formatted pipeline stage."""
    print(f"\n  [{title}]")
    print("  " + "-" * 50)
    if is_json:
        print("  " + json.dumps(content, indent=2, ensure_ascii=False).replace("\n", "\n  "))
    else:
        for line in str(content).split("\n"):
            print(f"  {line}")
    print()


def run_demo_flow(
    user_input: str,
    language: str,
    simulated_profile: Dict[str, Any],
) -> None:
    """
    Run one full demo flow through the pipeline.

    Uses simulated_profile to bypass LLM when AWS is unavailable.
    In production, profile comes from extract_user_profile().
    """
    lang_name = LANGUAGE_NAMES.get(language, language)

    print("\n" + "=" * 60)
    print(f"  DEMO: {lang_name} User")
    print("=" * 60)

    _print_stage("1. USER INPUT", user_input)
    _print_stage("2. EXTRACTED PROFILE (simulated)", simulated_profile, is_json=True)

    # Inline mock rule evaluation (replaces deleted mock_rule_engine.py)
    rule_output = _evaluate_mock_rules(simulated_profile)
    normalized = _normalize_rule_output(rule_output)
    _print_stage("3. RULE ENGINE OUTPUT", normalized, is_json=True)

    service = LLMService()
    try:
        explanation = service.generate_explanation(normalized, language)
    except Exception:
        from llm_service.fallback_templates import get_fallback_explanation
        explanation = get_fallback_explanation(normalized, language)

    _print_stage("4. EXPLANATION", explanation)
    print("  " + "=" * 60)


def main() -> None:
    """Run 3 demo flows: English farmer, Hindi user, Marathi user."""
    print("\n" + "#" * 60)
    print("#  SAMVADAI - Full Pipeline Integration Simulation")
    print("#" * 60)

    # Demo 1: English farmer (eligible for PM-KISAN)
    run_demo_flow(
        user_input="I am 35 years old, work as a farmer in Maharashtra, earn about 2 lakhs per year",
        language="en",
        simulated_profile={
            "age": 35,
            "occupation": "farmer",
            "income_band": "2L",
            "location": {"state": "Maharashtra"},
        },
    )

    # Demo 2: Hindi user (teacher, partially eligible)
    run_demo_flow(
        user_input="मैं ४० साल का हूं, शिक्षक हूं, महाराष्ट्र में रहता हूं",
        language="hi",
        simulated_profile={
            "age": 40,
            "occupation": "teacher",
            "income_band": None,
            "location": {"state": "Maharashtra"},
        },
    )

    # Demo 3: Marathi user (software engineer, not eligible for PM-KISAN)
    run_demo_flow(
        user_input="मी २८ वर्षांचा आहे, सॉफ्टवेअर इंजिनियर आहे, महाराष्ट्रात राहतो",
        language="mr",
        simulated_profile={
            "age": 28,
            "occupation": "software engineer",
            "income_band": "8L",
            "location": {"state": "Maharashtra"},
        },
    )

    print("\n" + "#" * 60)
    print("#  Integration simulation complete")
    print("#" * 60 + "\n")


if __name__ == "__main__":
    main()
