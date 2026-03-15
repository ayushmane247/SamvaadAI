"""
Unit tests for Scheme Ranking Service.

Tests benefit amount extraction, score calculation, and scheme ranking
with various input formats and edge cases.
"""

import unittest
import time
from unittest.mock import patch, MagicMock

from services.scheme_ranking_service import SchemeRankingService


class TestSchemeRankingService(unittest.TestCase):
    """Test cases for SchemeRankingService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = SchemeRankingService()
        
        # Sample schemes for testing
        self.sample_schemes = [
            {
                "scheme_id": "high_value_scheme",
                "scheme_name": "High Value Scheme",
                "benefit_summary": "Financial assistance of ₹50,000 per year",
                "priority": 5,
                "direct_benefit_transfer": True
            },
            {
                "scheme_id": "medium_value_scheme", 
                "scheme_name": "Medium Value Scheme",
                "benefit_summary": "Support of Rs. 25,000 annually",
                "priority": 3,
                "direct_benefit_transfer": False
            },
            {
                "scheme_id": "low_value_scheme",
                "scheme_name": "Low Value Scheme", 
                "benefit_summary": "Assistance up to ₹10,000",
                "priority": 1,
                "direct_benefit_transfer": True
            },
            {
                "scheme_id": "no_amount_scheme",
                "scheme_name": "No Amount Scheme",
                "benefit_summary": "Various benefits and support",
                "priority": 2,
                "direct_benefit_transfer": False
            }
        ]
    
    def test_extract_benefit_amount_rupee_symbol(self):
        """Test benefit amount extraction with ₹ symbol."""
        scheme = {"benefit_summary": "Financial assistance of ₹50,000 per year"}
        amount = self.service.extract_benefit_amount(scheme)
        self.assertEqual(amount, 50000.0)
    
    def test_extract_benefit_amount_rs_prefix(self):
        """Test benefit amount extraction with Rs. prefix."""
        scheme = {"benefit_summary": "Support of Rs. 25,000 annually"}
        amount = self.service.extract_benefit_amount(scheme)
        self.assertEqual(amount, 25000.0)
    
    def test_extract_benefit_amount_lakh_format(self):
        """Test benefit amount extraction with lakh format."""
        scheme = {"benefit_summary": "Up to ₹2.5 lakh assistance"}
        amount = self.service.extract_benefit_amount(scheme)
        self.assertEqual(amount, 250000.0)
    
    def test_extract_benefit_amount_crore_format(self):
        """Test benefit amount extraction with crore format."""
        scheme = {"benefit_summary": "Project funding of ₹1.2 crore"}
        amount = self.service.extract_benefit_amount(scheme)
        self.assertEqual(amount, 12000000.0)
    
    def test_extract_benefit_amount_no_amount(self):
        """Test benefit amount extraction when no amount present."""
        scheme = {"benefit_summary": "Various benefits and support"}
        amount = self.service.extract_benefit_amount(scheme)
        self.assertEqual(amount, 0.0)
    
    def test_extract_benefit_amount_missing_field(self):
        """Test benefit amount extraction with missing benefit_summary."""
        scheme = {"scheme_id": "test_scheme"}
        amount = self.service.extract_benefit_amount(scheme)
        self.assertEqual(amount, 0.0)
    
    def test_extract_benefit_amount_invalid_field(self):
        """Test benefit amount extraction with invalid field type."""
        scheme = {"benefit_summary": 12345}  # Not a string
        amount = self.service.extract_benefit_amount(scheme)
        self.assertEqual(amount, 0.0)
    
    def test_calculate_score_all_components(self):
        """Test score calculation with all components present."""
        scheme = {
            "benefit_summary": "₹50,000 assistance",
            "priority": 5,
            "direct_benefit_transfer": True
        }
        score = self.service.calculate_score(scheme)
        # Expected: (50000 * 0.5) + (5 * 10) + 10 = 25000 + 50 + 10 = 25060
        self.assertEqual(score, 25060.0)
    
    def test_calculate_score_no_priority(self):
        """Test score calculation without priority field."""
        scheme = {
            "benefit_summary": "₹30,000 assistance",
            "direct_benefit_transfer": True
        }
        score = self.service.calculate_score(scheme)
        # Expected: (30000 * 0.5) + (0 * 10) + 10 = 15000 + 0 + 10 = 15010
        self.assertEqual(score, 15010.0)
    
    def test_calculate_score_no_direct_transfer(self):
        """Test score calculation without direct benefit transfer."""
        scheme = {
            "benefit_summary": "₹20,000 assistance",
            "priority": 3,
            "direct_benefit_transfer": False
        }
        score = self.service.calculate_score(scheme)
        # Expected: (20000 * 0.5) + (3 * 10) + 0 = 10000 + 30 + 0 = 10030
        self.assertEqual(score, 10030.0)
    
    def test_calculate_score_string_boolean(self):
        """Test score calculation with string boolean values."""
        scheme = {
            "benefit_summary": "₹15,000 assistance",
            "priority": 2,
            "direct_benefit_transfer": "true"
        }
        score = self.service.calculate_score(scheme)
        # Expected: (15000 * 0.5) + (2 * 10) + 10 = 7500 + 20 + 10 = 7530
        self.assertEqual(score, 7530.0)
    
    def test_calculate_score_minimal_scheme(self):
        """Test score calculation with minimal scheme data."""
        scheme = {"scheme_id": "minimal_scheme"}
        score = self.service.calculate_score(scheme)
        # Expected: (0 * 0.5) + (0 * 10) + 0 = 0
        self.assertEqual(score, 0.0)
    
    def test_rank_schemes_correct_order(self):
        """Test that schemes are ranked in correct descending order."""
        ranked = self.service.rank_schemes(self.sample_schemes)
        
        # Verify all schemes are present
        self.assertEqual(len(ranked), 4)
        
        # Verify rank_score field is added
        for scheme in ranked:
            self.assertIn("rank_score", scheme)
        
        # Verify descending order
        scores = [scheme["rank_score"] for scheme in ranked]
        self.assertEqual(scores, sorted(scores, reverse=True))
        
        # Verify highest scoring scheme is first
        self.assertEqual(ranked[0]["scheme_id"], "high_value_scheme")
    
    def test_rank_schemes_empty_list(self):
        """Test ranking with empty scheme list."""
        ranked = self.service.rank_schemes([])
        self.assertEqual(ranked, [])
    
    def test_rank_schemes_single_scheme(self):
        """Test ranking with single scheme."""
        single_scheme = [self.sample_schemes[0]]
        ranked = self.service.rank_schemes(single_scheme)
        
        self.assertEqual(len(ranked), 1)
        self.assertIn("rank_score", ranked[0])
        self.assertEqual(ranked[0]["scheme_id"], "high_value_scheme")
    
    def test_rank_schemes_preserves_original(self):
        """Test that ranking doesn't modify original scheme objects."""
        original_schemes = [scheme.copy() for scheme in self.sample_schemes]
        ranked = self.service.rank_schemes(self.sample_schemes)
        
        # Original schemes should not have rank_score field
        for i, scheme in enumerate(self.sample_schemes):
            self.assertNotIn("rank_score", scheme)
            # Other fields should be unchanged
            for key in original_schemes[i]:
                self.assertEqual(scheme[key], original_schemes[i][key])
    
    def test_performance_constraint_single_scheme(self):
        """Test that single scheme processing meets <1ms constraint."""
        scheme = self.sample_schemes[0]
        
        start_time = time.perf_counter()
        self.service.calculate_score(scheme)
        execution_time = (time.perf_counter() - start_time) * 1000
        
        # Should be well under 1ms for single scheme
        self.assertLess(execution_time, 1.0)
    
    def test_performance_constraint_batch_ranking(self):
        """Test that batch ranking meets <5ms constraint."""
        # Create larger dataset (simulate 200 schemes)
        large_dataset = []
        for i in range(200):
            scheme = {
                "scheme_id": f"scheme_{i}",
                "benefit_summary": f"₹{(i+1)*1000} assistance",
                "priority": i % 10,
                "direct_benefit_transfer": i % 2 == 0
            }
            large_dataset.append(scheme)
        
        start_time = time.perf_counter()
        ranked = self.service.rank_schemes(large_dataset)
        execution_time = (time.perf_counter() - start_time) * 1000
        
        # Should be under 5ms for 200 schemes
        self.assertLess(execution_time, 5.0)
        self.assertEqual(len(ranked), 200)
    
    def test_get_ranking_metadata_complete(self):
        """Test ranking metadata generation with complete data."""
        ranked = self.service.rank_schemes(self.sample_schemes)
        metadata = self.service.get_ranking_metadata(ranked)
        
        self.assertEqual(metadata["total_schemes"], 4)
        self.assertIn("score_statistics", metadata)
        self.assertIn("benefit_statistics", metadata)
        self.assertIn("priority_distribution", metadata)
        self.assertIn("direct_transfer_count", metadata)
        
        # Check statistics structure
        self.assertIn("min", metadata["score_statistics"])
        self.assertIn("max", metadata["score_statistics"])
        self.assertIn("avg", metadata["score_statistics"])
    
    def test_get_ranking_metadata_empty(self):
        """Test ranking metadata generation with empty list."""
        metadata = self.service.get_ranking_metadata([])
        
        self.assertEqual(metadata["total_schemes"], 0)
        self.assertEqual(metadata["score_statistics"], {})
        self.assertEqual(metadata["benefit_statistics"], {})
        self.assertEqual(metadata["priority_distribution"], {})
        self.assertEqual(metadata["direct_transfer_count"], 0)
    
    @patch('services.scheme_ranking_service.logger')
    def test_error_handling_extract_benefit(self, mock_logger):
        """Test error handling in benefit amount extraction."""
        # Test with None scheme
        amount = self.service.extract_benefit_amount(None)
        self.assertEqual(amount, 0.0)
        
        # Test with malformed scheme
        amount = self.service.extract_benefit_amount("not_a_dict")
        self.assertEqual(amount, 0.0)
    
    @patch('services.scheme_ranking_service.logger')
    def test_error_handling_calculate_score(self, mock_logger):
        """Test error handling in score calculation."""
        # Test with None scheme
        score = self.service.calculate_score(None)
        self.assertEqual(score, 0.0)
        
        # Test with invalid priority type
        scheme = {
            "benefit_summary": "₹10,000",
            "priority": "invalid",
            "direct_benefit_transfer": True
        }
        score = self.service.calculate_score(scheme)
        # Should handle gracefully and use 0 for priority
        self.assertEqual(score, 5010.0)  # (10000 * 0.5) + 0 + 10
    
    @patch('services.scheme_ranking_service.logger')
    def test_error_handling_rank_schemes(self, mock_logger):
        """Test error handling in scheme ranking."""
        # Mock an exception during processing
        with patch.object(self.service, 'calculate_score', side_effect=Exception("Test error")):
            ranked = self.service.rank_schemes(self.sample_schemes)
            # Should return original schemes on error
            self.assertEqual(len(ranked), 4)
            # Should not have rank_score field due to error
            for scheme in ranked:
                self.assertNotIn("rank_score", scheme)


if __name__ == '__main__':
    unittest.main()