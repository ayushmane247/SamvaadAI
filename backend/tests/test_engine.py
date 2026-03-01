# tests\test_engine.py

from eligibility_engine.engine import evaluate

def test_equals_operator():
    scheme = {
        "scheme_id": "TEST_1",
        "name": "Test Scheme",
        "eligibility_criteria": [
            {"field": "occupation", "operator": "equals", "value": "farmer", "explanation": "Must be farmer"}
        ],
        "logic": "AND"
    }
    profile = {"occupation": "farmer"}
    result = evaluate(profile, [scheme])
    assert len(result["eligible"]) == 1
    assert result["eligible"][0]["scheme_id"] == "TEST_1"


def test_not_equals_operator():
    scheme = {
        "scheme_id": "TEST_2",
        "name": "Test Scheme",
        "eligibility_criteria": [
            {"field": "occupation", "operator": "not_equals", "value": "student", "explanation": "Must not be student"}
        ],
        "logic": "AND"
    }
    profile = {"occupation": "farmer"}
    result = evaluate(profile, [scheme])
    assert len(result["eligible"]) == 1


def test_greater_than_operator():
    scheme = {
        "scheme_id": "TEST_3",
        "name": "Test Scheme",
        "eligibility_criteria": [
            {"field": "age", "operator": "greater_than", "value": 18, "explanation": "Must be adult"}
        ],
        "logic": "AND"
    }
    profile = {"age": 25}
    result = evaluate(profile, [scheme])
    assert len(result["eligible"]) == 1


def test_less_than_operator():
    scheme = {
        "scheme_id": "TEST_4",
        "name": "Test Scheme",
        "eligibility_criteria": [
            {"field": "age", "operator": "less_than", "value": 60, "explanation": "Must be below 60"}
        ],
        "logic": "AND"
    }
    profile = {"age": 25}
    result = evaluate(profile, [scheme])
    assert len(result["eligible"]) == 1


def test_between_operator():
    scheme = {
        "scheme_id": "TEST_5",
        "name": "Test Scheme",
        "eligibility_criteria": [
            {"field": "age", "operator": "between", "value": [18, 60], "explanation": "Age between 18 and 60"}
        ],
        "logic": "AND"
    }
    profile = {"age": 25}
    result = evaluate(profile, [scheme])
    assert len(result["eligible"]) == 1


def test_in_operator():
    scheme = {
        "scheme_id": "TEST_6",
        "name": "Test Scheme",
        "eligibility_criteria": [
            {"field": "state", "operator": "in", "value": ["Maharashtra", "Karnataka"], "explanation": "Must be in Maharashtra or Karnataka"}
        ],
        "logic": "AND"
    }
    profile = {"state": "Maharashtra"}
    result = evaluate(profile, [scheme])
    assert len(result["eligible"]) == 1


def test_not_in_operator():
    scheme = {
        "scheme_id": "TEST_7",
        "name": "Test Scheme",
        "eligibility_criteria": [
            {"field": "occupation", "operator": "not_in", "value": ["student", "unemployed"], "explanation": "Must have occupation"}
        ],
        "logic": "AND"
    }
    profile = {"occupation": "farmer"}
    result = evaluate(profile, [scheme])
    assert len(result["eligible"]) == 1


def test_contains_operator():
    scheme = {
        "scheme_id": "TEST_8",
        "name": "Test Scheme",
        "eligibility_criteria": [
            {"field": "name", "operator": "contains", "value": "Kumar", "explanation": "Name must contain Kumar"}
        ],
        "logic": "AND"
    }
    profile = {"name": "Rajesh Kumar"}
    result = evaluate(profile, [scheme])
    assert len(result["eligible"]) == 1


def test_deterministic_repeatability():
    scheme = {
        "scheme_id": "TEST_DET",
        "name": "Test Scheme",
        "eligibility_criteria": [
            {"field": "age", "operator": "greater_than", "value": 18, "explanation": "Must be adult"}
        ],
        "logic": "AND"
    }
    profile = {"age": 25}
    
    result1 = evaluate(profile, [scheme])
    result2 = evaluate(profile, [scheme])
    result3 = evaluate(profile, [scheme])
    
    assert result1 == result2 == result3


def test_edge_case_missing_field():
    scheme = {
        "scheme_id": "TEST_EDGE_1",
        "name": "Test Scheme",
        "eligibility_criteria": [
            {"field": "age", "operator": "greater_than", "value": 18, "explanation": "Must be adult"}
        ],
        "logic": "AND"
    }
    profile = {}
    result = evaluate(profile, [scheme])
    assert len(result["ineligible"]) == 1
    assert result["ineligible"][0]["trace"][0]["result"] == "fail"


def test_edge_case_null_value():
    scheme = {
        "scheme_id": "TEST_EDGE_2",
        "name": "Test Scheme",
        "eligibility_criteria": [
            {"field": "age", "operator": "greater_than", "value": 18, "explanation": "Must be adult"}
        ],
        "logic": "AND"
    }
    profile = {"age": None}
    result = evaluate(profile, [scheme])
    assert len(result["ineligible"]) == 1


def test_edge_case_wrong_type():
    scheme = {
        "scheme_id": "TEST_EDGE_3",
        "name": "Test Scheme",
        "eligibility_criteria": [
            {"field": "age", "operator": "greater_than", "value": 18, "explanation": "Must be adult"}
        ],
        "logic": "AND"
    }
    profile = {"age": "twenty five"}
    result = evaluate(profile, [scheme])
    assert len(result["ineligible"]) == 1


def test_partially_eligible_logic():
    scheme = {
        "scheme_id": "TEST_PARTIAL",
        "name": "Test Scheme",
        "eligibility_criteria": [
            {"field": "occupation", "operator": "equals", "value": "farmer", "explanation": "Must be farmer"},
            {"field": "has_land", "operator": "equals", "value": True, "explanation": "Must have land"}
        ],
        "logic": "AND"
    }
    profile = {"occupation": "farmer", "has_land": False}
    result = evaluate(profile, [scheme])
    assert len(result["partially_eligible"]) == 1
    assert result["partially_eligible"][0]["status"] == "partially_eligible"


def test_trace_included():
    scheme = {
        "scheme_id": "TEST_TRACE",
        "name": "Test Scheme",
        "eligibility_criteria": [
            {"field": "age", "operator": "greater_than", "value": 18, "explanation": "Must be adult"}
        ],
        "logic": "AND"
    }
    profile = {"age": 25}
    result = evaluate(profile, [scheme])
    
    assert "trace" in result["eligible"][0]
    assert len(result["eligible"][0]["trace"]) == 1
    assert result["eligible"][0]["trace"][0]["field"] == "age"
    assert result["eligible"][0]["trace"][0]["result"] == "pass"


def test_multiple_schemes():
    schemes = [
        {
            "scheme_id": "SCHEME_A",
            "name": "Scheme A",
            "eligibility_criteria": [
                {"field": "occupation", "operator": "equals", "value": "farmer", "explanation": "Must be farmer"}
            ],
            "logic": "AND",
            "benefit_summary": "Test benefit",
            "source_url": "https://test.com",
            "last_verified_date": "2025-02-15"
        },
        {
            "scheme_id": "SCHEME_B",
            "name": "Scheme B",
            "eligibility_criteria": [
                {"field": "occupation", "operator": "equals", "value": "teacher", "explanation": "Must be teacher"}
            ],
            "logic": "AND",
            "benefit_summary": "Test benefit",
            "source_url": "https://test.com",
            "last_verified_date": "2025-02-15"
        }
    ]
    profile = {"occupation": "farmer"}
    result = evaluate(profile, schemes)
    
    assert len(result["eligible"]) == 1
    assert result["eligible"][0]["scheme_id"] == "SCHEME_A"
    assert len(result["ineligible"]) == 1
    assert result["ineligible"][0]["scheme_id"] == "SCHEME_B"


def test_output_sorted():
    schemes = [
        {"scheme_id": "SCHEME_C", "name": "C", "eligibility_criteria": [{"field": "x", "operator": "equals", "value": 1, "exp": "x"}], "logic": "AND"},
        {"scheme_id": "SCHEME_A", "name": "A", "eligibility_criteria": [{"field": "x", "operator": "equals", "value": 1, "exp": "x"}], "logic": "AND"},
        {"scheme_id": "SCHEME_B", "name": "B", "eligibility_criteria": [{"field": "x", "operator": "equals", "value": 1, "exp": "x"}], "logic": "AND"}
    ]
    profile = {"x": 1}
    result = evaluate(profile, schemes)
    
    assert result["eligible"][0]["scheme_id"] == "SCHEME_A"
    assert result["eligible"][1]["scheme_id"] == "SCHEME_B"
    assert result["eligible"][2]["scheme_id"] == "SCHEME_C"


def test_performance():
    import time
    schemes = [
        {
            "scheme_id": f"SCHEME_{i}",
            "name": f"Scheme {i}",
            "eligibility_criteria": [
                {"field": "age", "operator": "greater_than", "value": 18, "explanation": "Test"},
                {"field": "income", "operator": "less_than", "value": 100000, "explanation": "Test"}
            ],
            "logic": "AND",
            "benefit_summary": "Test",
            "source_url": "https://test.com",
            "last_verified_date": "2025-02-15"
        }
        for i in range(10)
    ]
    profile = {"age": 25, "income": 50000}
    
    start = time.time()
    for _ in range(100):
        evaluate(profile, schemes)
    elapsed = (time.time() - start) / 100 * 1000
    
    assert elapsed < 100, f"Evaluation took {elapsed}ms, should be < 100ms"


def run_all_tests():
    tests = [
        ("Equals Operator", test_equals_operator),
        ("Not Equals Operator", test_not_equals_operator),
        ("Greater Than Operator", test_greater_than_operator),
        ("Less Than Operator", test_less_than_operator),
        ("Between Operator", test_between_operator),
        ("In Operator", test_in_operator),
        ("Not In Operator", test_not_in_operator),
        ("Contains Operator", test_contains_operator),
        ("Deterministic Repeatability", test_deterministic_repeatability),
        ("Edge Case: Missing Field", test_edge_case_missing_field),
        ("Edge Case: Null Value", test_edge_case_null_value),
        ("Edge Case: Wrong Type", test_edge_case_wrong_type),
        ("Partially Eligible Logic", test_partially_eligible_logic),
        ("Trace Included", test_trace_included),
        ("Multiple Schemes", test_multiple_schemes),
        ("Output Sorted", test_output_sorted),
        ("Performance", test_performance),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"✓ {name}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {name}: Unexpected error - {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*50}")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
