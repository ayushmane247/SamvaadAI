"""
Tests for Document Requirement Service.

Tests the deterministic document extraction from scheme metadata.
"""

import pytest
import time
from services.document_requirement_service import DocumentRequirementService


class TestDocumentRequirementService:
    """Test cases for document requirement service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = DocumentRequirementService()
    
    def test_get_required_documents_basic(self):
        """Test basic document extraction from a valid scheme."""
        scheme = {
            "scheme_id": "PM_KISAN",
            "name": "PM Kisan Samman Nidhi",
            "required_documents": [
                "Aadhaar Card",
                "Land ownership records",
                "Bank account details"
            ]
        }
        
        documents = self.service.get_required_documents(scheme)
        
        assert len(documents) == 3
        assert "Aadhaar Card" in documents
        assert "Land ownership records" in documents
        assert "Bank account details" in documents
    
    def test_get_required_documents_missing_field(self):
        """Test document extraction when required_documents field is missing."""
        scheme = {
            "scheme_id": "NO_DOCS_SCHEME",
            "name": "Scheme Without Documents"
        }
        
        documents = self.service.get_required_documents(scheme)
        
        assert documents == []
    
    def test_get_required_documents_empty_list(self):
        """Test document extraction when required_documents is an empty list."""
        scheme = {
            "scheme_id": "EMPTY_DOCS",
            "name": "Scheme With Empty Documents",
            "required_documents": []
        }
        
        documents = self.service.get_required_documents(scheme)
        
        assert documents == []
    
    def test_get_required_documents_invalid_type(self):
        """Test document extraction when required_documents is not a list."""
        scheme = {
            "scheme_id": "INVALID_DOCS",
            "name": "Scheme With Invalid Documents",
            "required_documents": "Not a list"
        }
        
        documents = self.service.get_required_documents(scheme)
        
        assert documents == []  # Should return empty list for invalid type
    
    def test_get_required_documents_malformed_scheme(self):
        """Test document extraction with malformed scheme data."""
        # Test with None
        documents = self.service.get_required_documents(None)
        assert documents == []
        
        # Test with empty dict
        documents = self.service.get_required_documents({})
        assert documents == []
    
    def test_get_documents_for_schemes_batch(self):
        """Test batch document extraction for multiple schemes."""
        schemes = [
            {
                "scheme_id": "SCHEME_1",
                "required_documents": ["Aadhaar Card", "Income Certificate"]
            },
            {
                "scheme_id": "SCHEME_2", 
                "required_documents": ["Bank Details", "Address Proof"]
            },
            {
                "scheme_id": "SCHEME_3"
                # Missing required_documents field
            }
        ]
        
        result = self.service.get_documents_for_schemes(schemes)
        
        assert len(result) == 3
        assert result["SCHEME_1"] == ["Aadhaar Card", "Income Certificate"]
        assert result["SCHEME_2"] == ["Bank Details", "Address Proof"]
        assert result["SCHEME_3"] == []
    
    def test_get_documents_for_schemes_empty_list(self):
        """Test batch processing with empty scheme list."""
        result = self.service.get_documents_for_schemes([])
        
        assert result == {}
    
    def test_get_documents_for_schemes_missing_scheme_id(self):
        """Test batch processing with schemes missing scheme_id."""
        schemes = [
            {
                "name": "Scheme Without ID",
                "required_documents": ["Document 1"]
            }
        ]
        
        result = self.service.get_documents_for_schemes(schemes)
        
        assert len(result) == 1
        assert "" in result  # Empty string key for missing scheme_id
        assert result[""] == ["Document 1"]
    
    def test_get_all_unique_documents(self):
        """Test aggregation of unique documents across schemes."""
        schemes = [
            {
                "scheme_id": "SCHEME_1",
                "required_documents": ["Aadhaar Card", "Income Certificate", "Bank Details"]
            },
            {
                "scheme_id": "SCHEME_2",
                "required_documents": ["Aadhaar Card", "Address Proof"]  # Aadhaar Card duplicated
            },
            {
                "scheme_id": "SCHEME_3",
                "required_documents": ["Bank Details", "Caste Certificate"]  # Bank Details duplicated
            }
        ]
        
        unique_documents = self.service.get_all_unique_documents(schemes)
        
        # Should be sorted and deduplicated
        expected = ["Aadhaar Card", "Address Proof", "Bank Details", "Caste Certificate", "Income Certificate"]
        assert unique_documents == expected
    
    def test_get_all_unique_documents_empty_schemes(self):
        """Test unique document aggregation with empty scheme list."""
        unique_documents = self.service.get_all_unique_documents([])
        
        assert unique_documents == []
    
    def test_performance_single_scheme(self):
        """Test that single scheme processing completes under 1ms."""
        scheme = {
            "scheme_id": "PERFORMANCE_TEST",
            "required_documents": [
                "Aadhaar Card", "Income Certificate", "Bank Details",
                "Address Proof", "Caste Certificate", "Age Proof"
            ]
        }
        
        start_time = time.perf_counter()
        documents = self.service.get_required_documents(scheme)
        execution_time_ms = (time.perf_counter() - start_time) * 1000
        
        assert execution_time_ms < 1.0  # Must complete under 1ms
        assert len(documents) == 6
    
    def test_performance_batch_processing(self):
        """Test batch processing performance with multiple schemes."""
        # Create 20 schemes to simulate realistic load
        schemes = []
        for i in range(20):
            schemes.append({
                "scheme_id": f"SCHEME_{i}",
                "required_documents": [
                    "Aadhaar Card",
                    "Income Certificate", 
                    f"Document_{i}_1",
                    f"Document_{i}_2"
                ]
            })
        
        start_time = time.perf_counter()
        result = self.service.get_documents_for_schemes(schemes)
        execution_time_ms = (time.perf_counter() - start_time) * 1000
        
        # Should process 20 schemes well under 20ms (1ms per scheme target)
        assert execution_time_ms < 20.0
        assert len(result) == 20
        
        # Verify all schemes processed correctly
        for i in range(20):
            scheme_id = f"SCHEME_{i}"
            assert scheme_id in result
            assert len(result[scheme_id]) == 4
    
    def test_real_scheme_structure(self):
        """Test with realistic scheme structure based on actual data."""
        scheme = {
            "scheme_id": "PM_KISAN_CENTRAL",
            "name": "PM Kisan Samman Nidhi",
            "state": "All India",
            "eligibility_criteria": [
                {
                    "field": "farmer_status",
                    "operator": "equals",
                    "value": True,
                    "explanation": "Must be a farmer"
                }
            ],
            "logic": "OR",
            "benefit_summary": "₹6,000 per year in 3 installments",
            "source_url": "https://pmkisan.gov.in",
            "last_verified_date": "2026-03-01",
            "required_documents": [
                "Aadhaar Card",
                "Land ownership records",
                "Bank account details"
            ],
            "application_process": "Apply online at pmkisan.gov.in",
            "notes": "Excludes institutional landholders"
        }
        
        documents = self.service.get_required_documents(scheme)
        
        assert len(documents) == 3
        assert "Aadhaar Card" in documents
        assert "Land ownership records" in documents
        assert "Bank account details" in documents
    
    def test_error_handling_robustness(self):
        """Test that service handles various error conditions gracefully."""
        # Test with malformed schemes that might cause exceptions
        test_cases = [
            None,
            {},
            {"scheme_id": None},
            {"required_documents": None},
            {"required_documents": 123},
            {"required_documents": {"not": "a list"}},
        ]
        
        for scheme in test_cases:
            try:
                documents = self.service.get_required_documents(scheme)
                assert isinstance(documents, list)  # Should always return a list
            except Exception as e:
                pytest.fail(f"Service should not raise exceptions, got: {e}")