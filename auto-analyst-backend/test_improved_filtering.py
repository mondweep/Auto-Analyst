#!/usr/bin/env python3
"""
Test suite for improved attribute filtering functionality
"""

import pytest
import os
import csv
import tempfile
from unittest.mock import patch

# Import the improved functions
import sys
sys.path.append('.')

from attribute_filtering_improved import (
    detect_attribute_query,
    filter_csv_by_attribute,
    count_attribute_values,
    find_dataset
)

class TestImprovedAttributeFiltering:
    """Test the improved attribute filtering functions"""
    
    @pytest.fixture
    def sample_csv_data(self):
        """Create sample CSV data for testing"""
        return [
            ["make", "model", "year", "color", "condition", "price"],
            ["Toyota", "Camry", "2022", "green", "excellent", "25000"],
            ["Honda", "Civic", "2021", "blue", "good", "22000"],
            ["Toyota", "Prius", "2022", "green", "excellent", "28000"],
            ["Ford", "Focus", "2020", "red", "fair", "18000"],
            ["Honda", "Accord", "2021", "green", "good", "26000"]
        ]
    
    @pytest.fixture
    def temp_csv_file(self, sample_csv_data):
        """Create temporary CSV file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            writer = csv.writer(f)
            writer.writerows(sample_csv_data)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        os.unlink(temp_path)
    
    def test_detect_color_variations(self):
        """Test various color query formats"""
        test_cases = [
            ("how many red cars", (True, "color", "red")),
            ("count of blue vehicles", (True, "color", "blue")),
            ("How many BLACK vehicles?", (True, "color", "black")),
            ("vehicles that are white", (True, "color", "white"))
        ]
        
        for query, expected in test_cases:
            result = detect_attribute_query(query)
            assert result == expected, f"Failed for query: {query}"
    
    def test_detect_make_variations(self):
        """Test various make query formats"""
        test_cases = [
            ("how many toyota vehicles", (True, "make", "toyota")),
            ("count of Honda cars", (True, "make", "honda")),
            ("BMW vehicles", (True, "make", "bmw"))
        ]
        
        for query, expected in test_cases:
            result = detect_attribute_query(query)
            assert result == expected, f"Failed for query: {query}"
    
    def test_filter_nonexistent_attribute_returns_none(self, temp_csv_file):
        """Should return None, None for nonexistent attributes"""
        result, header = filter_csv_by_attribute(temp_csv_file, "engine", "V6")
        assert result is None
        assert header is None
    
    def test_count_returns_dict(self, temp_csv_file):
        """Count function should return a dictionary with count info"""
        with patch('builtins.print'):
            result = count_attribute_values(temp_csv_file, "color", "green")
        
        assert result is not None
        assert isinstance(result, dict)
        assert 'count' in result
        assert result['count'] == 3  # Should find 3 green vehicles

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 