# eligibility_engine\rule_parser.py

from typing import Any, Dict, List, Tuple, Optional


class RuleParser:
    @staticmethod
    def evaluate_condition(
        field: str,
        operator: str,
        expected_value: Any,
        profile: Optional[Dict[str, Any]]
    ) -> Tuple[bool, Dict]:
        actual_value = RuleParser._get_nested_value(profile, field)
        
        result = {
            "field": field,
            "operator": operator,
            "expected": expected_value,
            "actual": actual_value,
            "result": "pass" if RuleParser._match(actual_value, operator, expected_value) else "fail"
        }
        
        is_match = RuleParser._match(actual_value, operator, expected_value)
        return is_match, result
    
    @staticmethod
    def _get_nested_value(data: Dict, field: str) -> Any:
        keys = field.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value
    
    @staticmethod
    def _match(actual: Any, operator: str, expected: Any) -> bool:
        if actual is None:
            return False
        
        if operator == "equals":
            return str(actual).lower() == str(expected).lower()
        
        if operator == "not_equals":
            return str(actual).lower() != str(expected).lower()
        
        if operator == "greater_than":
            return RuleParser._to_float(actual) > RuleParser._to_float(expected)
        
        if operator == "less_than":
            return RuleParser._to_float(actual) < RuleParser._to_float(expected)
        
        if operator == "greater_than_or_equals":
            return RuleParser._to_float(actual) >= RuleParser._to_float(expected)
        
        if operator == "less_than_or_equals":
            return RuleParser._to_float(actual) <= RuleParser._to_float(expected)
        
        if operator == "between":
            if isinstance(expected, list) and len(expected) == 2:
                val = RuleParser._to_float(actual)
                return RuleParser._to_float(expected[0]) <= val <= RuleParser._to_float(expected[1])
            return False
        
        if operator == "in":
            if isinstance(expected, list):
                return str(actual).lower() in [str(v).lower() for v in expected]
            return str(actual).lower() == str(expected).lower()
        
        if operator == "not_in":
            if isinstance(expected, list):
                return str(actual).lower() not in [str(v).lower() for v in expected]
            return str(actual).lower() != str(expected).lower()
        
        if operator == "contains":
            return str(expected).lower() in str(actual).lower()
        
        return False
    
    @staticmethod
    def _to_float(value: Any) -> float:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = value.replace(",", "").replace("₹", "").replace("Rs", "").strip()
            try:
                return float(cleaned)
            except ValueError:
                return 0.0
        return 0.0
    
    @staticmethod
    def validate_operator(operator: str) -> bool:
        valid_operators = {
            "equals",
            "not_equals",
            "greater_than",
            "less_than",
            "greater_than_or_equals",
            "less_than_or_equals",
            "between",
            "in",
            "not_in",
            "contains"
        }
        return operator in valid_operators
