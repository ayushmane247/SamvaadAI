"""
Unit tests for CSC Center Service.

Tests center lookup, profile-based search, and performance constraints
with various input formats and edge cases.
"""

import unittest
import time
import json
import tempfile
import os
from unittest.mock import patch, mock_open, MagicMock

from services.csc_center_service import CSCCenterService


class TestCSCCenterService(unittest.TestCase):
    """Test cases for CSCCenterService."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample centers data for testing
        self.sample_centers_data = {
            "Maharashtra": {
                "Mumbai": [
                    {
                        "name": "CSC Center - Andheri East",
                        "address": "Shop No. 15, Andheri East, Mumbai - 400069",
                        "contact": "+91-9876543210",
                        "services": ["scheme_applications", "document_verification"]
                    },
                    {
                        "name": "CSC Center - Bandra West",
                        "address": "Office No. 23, Bandra West, Mumbai - 400050",
                        "contact": "+91-9876543211",
                        "services": ["scheme_applications", "banking_services"]
                    },
                    {
                        "name": "CSC Center - Borivali",
                        "address": "Ground Floor, Borivali West, Mumbai - 400092",
                        "contact": "+91-9876543212",
                        "services": ["scheme_applications", "insurance_services"]
                    },
                    {
                        "name": "CSC Center - Dadar",
                        "address": "Shop No. 8, Dadar East, Mumbai - 400014",
                        "contact": "+91-9876543213",
                        "services": ["scheme_applications", "pension_services"]
                    }
                ],
                "Pune": [
                    {
                        "name": "CSC Center - Shivajinagar",
                        "address": "Office No. 12, Shivajinagar, Pune - 411005",
                        "contact": "+91-9876543220",
                        "services": ["scheme_applications", "document_verification"]
                    },
                    {
                        "name": "CSC Center - Kothrud",
                        "address": "Shop No. 45, Kothrud, Pune - 411038",
                        "contact": "+91-9876543221",
                        "services": ["scheme_applications", "banking_services"]
                    }
                ]
            },
            "Karnataka": {
                "Bangalore": [
                    {
                        "name": "CSC Center - Koramangala",
                        "address": "Shop No. 42, Koramangala, Bangalore - 560034",
                        "contact": "+91-9876543300",
                        "services": ["scheme_applications", "digital_services"]
                    }
                ]
            }
        }
        
        # Create temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(self.sample_centers_data, self.temp_file)
        self.temp_file.close()
        
        # Initialize service with test data
        self.service = CSCCenterService(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_initialization_success(self):
        """Test successful service initialization."""
        self.assertEqual(len(self.service.centers_data), 2)  # Maharashtra, Karnataka
        self.assertIn("Maharashtra", self.service.centers_data)
        self.assertIn("Karnataka", self.service.centers_data)
    
    def test_initialization_file_not_found(self):
        """Test initialization with non-existent file."""
        service = CSCCenterService("non_existent_file.json")
        self.assertEqual(service.centers_data, {})
    
    def test_initialization_invalid_json(self):
        """Test initialization with invalid JSON file."""
        # Create file with invalid JSON
        invalid_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        invalid_file.write("{ invalid json content")
        invalid_file.close()
        
        try:
            service = CSCCenterService(invalid_file.name)
            self.assertEqual(service.centers_data, {})
        finally:
            os.unlink(invalid_file.name)
    
    def test_find_centers_valid_location(self):
        """Test finding centers with valid state and district."""
        centers = self.service.find_centers("Maharashtra", "Mumbai")
        
        # Should return top 3 centers (Mumbai has 4, so limited to 3)
        self.assertEqual(len(centers), 3)
        
        # Verify structure of returned centers
        for center in centers:
            self.assertIn("name", center)
            self.assertIn("address", center)
            self.assertIn("contact", center)
            self.assertIn("services", center)
        
        # Verify first center
        self.assertEqual(centers[0]["name"], "CSC Center - Andheri East")
    
    def test_find_centers_all_available(self):
        """Test finding centers when fewer than 3 available."""
        centers = self.service.find_centers("Maharashtra", "Pune")
        
        # Pune has only 2 centers, should return all
        self.assertEqual(len(centers), 2)
        self.assertEqual(centers[0]["name"], "CSC Center - Shivajinagar")
        self.assertEqual(centers[1]["name"], "CSC Center - Kothrud")
    
    def test_find_centers_invalid_state(self):
        """Test finding centers with invalid state."""
        centers = self.service.find_centers("InvalidState", "Mumbai")
        self.assertEqual(centers, [])
    
    def test_find_centers_invalid_district(self):
        """Test finding centers with invalid district."""
        centers = self.service.find_centers("Maharashtra", "InvalidDistrict")
        self.assertEqual(centers, [])
    
    def test_find_centers_empty_inputs(self):
        """Test finding centers with empty inputs."""
        # Empty state
        centers = self.service.find_centers("", "Mumbai")
        self.assertEqual(centers, [])
        
        # Empty district
        centers = self.service.find_centers("Maharashtra", "")
        self.assertEqual(centers, [])
        
        # Both empty
        centers = self.service.find_centers("", "")
        self.assertEqual(centers, [])
    
    def test_find_centers_none_inputs(self):
        """Test finding centers with None inputs."""
        centers = self.service.find_centers(None, "Mumbai")
        self.assertEqual(centers, [])
        
        centers = self.service.find_centers("Maharashtra", None)
        self.assertEqual(centers, [])
    
    def test_find_centers_case_insensitive(self):
        """Test that center lookup is case insensitive."""
        # Test different cases
        centers1 = self.service.find_centers("maharashtra", "mumbai")
        centers2 = self.service.find_centers("MAHARASHTRA", "MUMBAI")
        centers3 = self.service.find_centers("Maharashtra", "Mumbai")
        
        # All should return same results
        self.assertEqual(len(centers1), 3)
        self.assertEqual(len(centers2), 3)
        self.assertEqual(len(centers3), 3)
        self.assertEqual(centers1[0]["name"], centers2[0]["name"])
        self.assertEqual(centers2[0]["name"], centers3[0]["name"])
    
    def test_find_centers_by_profile_valid(self):
        """Test finding centers using profile data."""
        profile = {
            "state": "Maharashtra",
            "district": "Mumbai",
            "occupation": "farmer"
        }
        
        centers = self.service.find_centers_by_profile(profile)
        self.assertEqual(len(centers), 3)
        self.assertEqual(centers[0]["name"], "CSC Center - Andheri East")
    
    def test_find_centers_by_profile_missing_fields(self):
        """Test finding centers with missing profile fields."""
        # Missing district
        profile = {"state": "Maharashtra"}
        centers = self.service.find_centers_by_profile(profile)
        self.assertEqual(centers, [])
        
        # Missing state
        profile = {"district": "Mumbai"}
        centers = self.service.find_centers_by_profile(profile)
        self.assertEqual(centers, [])
        
        # Empty profile
        centers = self.service.find_centers_by_profile({})
        self.assertEqual(centers, [])
    
    def test_find_centers_by_profile_invalid_profile(self):
        """Test finding centers with invalid profile."""
        centers = self.service.find_centers_by_profile(None)
        self.assertEqual(centers, [])
    
    def test_get_available_locations(self):
        """Test getting available locations."""
        locations = self.service.get_available_locations()
        
        self.assertEqual(len(locations), 2)
        self.assertIn("Maharashtra", locations)
        self.assertIn("Karnataka", locations)
        
        # Check Maharashtra districts
        self.assertEqual(set(locations["Maharashtra"]), {"Mumbai", "Pune"})
        
        # Check Karnataka districts
        self.assertEqual(set(locations["Karnataka"]), {"Bangalore"})
    
    def test_get_center_count(self):
        """Test getting center count statistics."""
        stats = self.service.get_center_count()
        
        self.assertEqual(stats["total_states"], 2)
        self.assertEqual(stats["total_districts"], 3)  # Mumbai, Pune, Bangalore
        self.assertEqual(stats["total_centers"], 7)  # 4 + 2 + 1
        
        # Check per-state counts
        self.assertEqual(stats["centers_by_state"]["Maharashtra"], 6)  # 4 + 2
        self.assertEqual(stats["centers_by_state"]["Karnataka"], 1)
    
    def test_performance_constraint(self):
        """Test that center lookup meets <2ms constraint."""
        start_time = time.perf_counter()
        centers = self.service.find_centers("Maharashtra", "Mumbai")
        execution_time = (time.perf_counter() - start_time) * 1000
        
        # Should be well under 2ms
        self.assertLess(execution_time, 2.0)
        self.assertEqual(len(centers), 3)
    
    def test_performance_multiple_lookups(self):
        """Test performance with multiple consecutive lookups."""
        lookups = [
            ("Maharashtra", "Mumbai"),
            ("Maharashtra", "Pune"),
            ("Karnataka", "Bangalore"),
            ("InvalidState", "InvalidDistrict")
        ]
        
        start_time = time.perf_counter()
        for state, district in lookups:
            self.service.find_centers(state, district)
        execution_time = (time.perf_counter() - start_time) * 1000
        
        # All lookups should complete well under 2ms each
        avg_time_per_lookup = execution_time / len(lookups)
        self.assertLess(avg_time_per_lookup, 2.0)
    
    def test_reload_centers_data_success(self):
        """Test successful reload of centers data."""
        # Modify the file
        modified_data = {"TestState": {"TestDistrict": []}}
        with open(self.temp_file.name, 'w') as f:
            json.dump(modified_data, f)
        
        # Reload
        success = self.service.reload_centers_data()
        self.assertTrue(success)
        self.assertEqual(self.service.centers_data, modified_data)
    
    def test_reload_centers_data_failure(self):
        """Test reload failure with invalid file."""
        # Delete the file
        os.unlink(self.temp_file.name)
        
        # Try to reload
        success = self.service.reload_centers_data()
        self.assertFalse(success)
    
    @patch('services.csc_center_service.logger')
    def test_error_handling_find_centers(self, mock_logger):
        """Test error handling in find_centers method."""
        # Mock an exception in the method
        with patch.object(self.service, 'centers_data', side_effect=Exception("Test error")):
            centers = self.service.find_centers("Maharashtra", "Mumbai")
            self.assertEqual(centers, [])
    
    @patch('services.csc_center_service.logger')
    def test_error_handling_get_available_locations(self, mock_logger):
        """Test error handling in get_available_locations method."""
        # Mock an exception
        with patch.object(self.service, 'centers_data', side_effect=Exception("Test error")):
            locations = self.service.get_available_locations()
            self.assertEqual(locations, {})
    
    @patch('services.csc_center_service.logger')
    def test_error_handling_get_center_count(self, mock_logger):
        """Test error handling in get_center_count method."""
        # Mock an exception
        with patch.object(self.service, 'centers_data', side_effect=Exception("Test error")):
            stats = self.service.get_center_count()
            self.assertEqual(stats, {})
    
    def test_logging_behavior(self):
        """Test that appropriate logging occurs."""
        with patch('services.csc_center_service.logger') as mock_logger:
            # Test successful lookup
            self.service.find_centers("Maharashtra", "Mumbai")
            mock_logger.info.assert_called()
            
            # Test failed lookup
            self.service.find_centers("InvalidState", "InvalidDistrict")
            mock_logger.debug.assert_called()
    
    def test_thread_safety_simulation(self):
        """Test that service can handle concurrent-like access."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def lookup_centers():
            centers = self.service.find_centers("Maharashtra", "Mumbai")
            results.put(len(centers))
        
        # Simulate concurrent access
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=lookup_centers)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All should return same result
        while not results.empty():
            result = results.get()
            self.assertEqual(result, 3)


if __name__ == '__main__':
    unittest.main()