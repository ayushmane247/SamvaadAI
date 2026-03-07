# eligibility_engine\engine.py

from typing import Any, Dict, List
from eligibility_engine.rule_parser import RuleParser


def evaluate(profile: dict, schemes: list[dict]) -> dict:
    """
    Pure deterministic evaluation.
    Same input always produces same output.
    No side effects.
    
    Args:
        profile: structured attributes from conversation layer
        schemes: list of scheme JSON objects (passed from S3 loader)
    
    Returns:
        dict with eligible, partially_eligible, ineligible lists
    """
    eligible = []
    partially_eligible = []
    ineligible = []
    
    for scheme in schemes:
        result = _evaluate_single_scheme(profile, scheme)
        
        if result["status"] == "eligible":
            eligible.append(result)
        elif result["status"] == "partially_eligible":
            partially_eligible.append(result)
        else:
            ineligible.append(result)
    
    eligible = sorted(eligible, key=lambda x: x["scheme_id"])
    partially_eligible = sorted(partially_eligible, key=lambda x: x["scheme_id"])
    ineligible = sorted(ineligible, key=lambda x: x["scheme_id"])
    
    return {
        "eligible": eligible,
        "partially_eligible": partially_eligible,
        "ineligible": ineligible
    }


def _evaluate_single_scheme(profile: dict, scheme: dict) -> dict:
    scheme_id = scheme.get("scheme_id", "")
    scheme_name = scheme.get("name", "")
    criteria = scheme.get("eligibility_criteria", [])
    logic = scheme.get("logic", "AND").upper()
    benefit = scheme.get("benefit_summary", "")
    source_url = scheme.get("source_url", "")
    last_verified = scheme.get("last_verified_date", "")
    required_documents = scheme.get("required_documents", [])
    
    if not criteria:
        return {
            "scheme_id": scheme_id,
            "scheme_name": scheme_name,
            "status": "ineligible",
            "reasons": ["No eligibility criteria defined"],
            "trace": [],
            "benefit": benefit,
            "source_url": source_url,
            "last_verified_date": last_verified,
            "required_documents": required_documents
        }
    
    trace = []
    passed_rules = []
    failed_rules = []
    
    for rule in criteria:
        field = rule.get("field", "")
        operator = rule.get("operator", "")
        expected = rule.get("value")
        explanation = rule.get("explanation", "")
        
        is_match, rule_result = RuleParser.evaluate_condition(
            field, operator, expected, profile
        )
        
        rule_result["explanation"] = explanation
        trace.append(rule_result)
        
        if is_match:
            passed_rules.append(explanation)
        else:
            failed_rules.append(explanation)
    
    total_rules = len(criteria)
    passed_count = len(passed_rules)
    
    is_and_logic = logic == "AND"
    
    if is_and_logic:
        is_eligible = passed_count == total_rules
        is_partial = passed_count > 0 and passed_count < total_rules
    else:
        is_eligible = passed_count > 0
        is_partial = False
    
    if is_eligible:
        return {
            "scheme_id": scheme_id,
            "scheme_name": scheme_name,
            "status": "eligible",
            "reasons": passed_rules,
            "trace": trace,
            "benefit": benefit,
            "source_url": source_url,
            "last_verified_date": last_verified,
            "required_documents": required_documents
        }
    elif is_partial:
        missing = [r.get("field", "") for r in trace if r.get("result") == "fail"]
        guidance = " and ".join(failed_rules) if failed_rules else "Complete missing requirements"
        return {
            "scheme_id": scheme_id,
            "scheme_name": scheme_name,
            "status": "partially_eligible",
            "reasons": passed_rules,
            "missing_fields": missing,
            "guidance": guidance,
            "trace": trace,
            "benefit": benefit,
            "source_url": source_url,
            "last_verified_date": last_verified,
            "required_documents": required_documents
        }
    else:
        return {
            "scheme_id": scheme_id,
            "scheme_name": scheme_name,
            "status": "ineligible",
            "reasons": failed_rules,
            "trace": trace,
            "benefit": benefit,
            "source_url": source_url,
            "last_verified_date": last_verified,
            "required_documents": required_documents
        }
