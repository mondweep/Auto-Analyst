#!/usr/bin/env python3
"""
Production-Ready Attribute Filtering Module

This module provides comprehensive attribute-based query detection and filtering
capabilities for vehicle datasets. It follows TDD principles and includes:

- Query pattern detection for colors, makes, years, and conditions
- CSV-based filtering with robust error handling
- Statistical analysis and reporting
- Type hints and comprehensive documentation

Author: Auto-Analyst TDD Implementation
Version: 1.0.0
"""

import os
import csv
import re
import logging
from typing import Tuple, List, Dict, Optional, Union, Any
from pathlib import Path
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QueryResult:
    """Data class for query result information"""
    count: int
    total: int
    percentage: float
    attribute: str
    value: str
    matched_rows: List[Dict[str, Any]]
    
    def __str__(self) -> str:
        return f"Found {self.count} {self.value} {self.attribute}s ({self.percentage:.1f}% of {self.total} total)"

@dataclass
class AttributeQuery:
    """Data class for parsed attribute queries"""
    is_attribute_query: bool
    attribute_name: Optional[str] = None
    attribute_value: Optional[str] = None

class AttributePatterns:
    """Centralized patterns and constants for attribute detection"""
    
    COLORS = {
        "green", "red", "blue", "black", "white", "silver", "gray", "grey",
        "yellow", "orange", "purple", "pink", "brown", "beige", "gold", "maroon",
        "navy", "teal", "olive", "lime", "cyan", "magenta"
    }
    
    MAKES = {
        "toyota", "honda", "ford", "bmw", "mercedes", "audi", "tesla",
        "hyundai", "kia", "nissan", "chevrolet", "lexus", "acura", "infiniti",
        "volkswagen", "subaru", "mazda", "volvo", "jaguar", "porsche",
        "land rover", "mini", "fiat", "alfa romeo", "maserati", "ferrari"
    }
    
    CONDITIONS = {"excellent", "good", "fair", "poor", "new", "used", "certified"}
    
    COLOR_PATTERNS = [
        r"how many (\w+) (?:vehicles|cars)",
        r"count (?:of|the) (\w+) (?:vehicles|cars)",
        r"(?:vehicles|cars) that are (\w+)",
        r"(\w+) (?:vehicles|cars)",
        r"(\w+) colored (?:vehicles|cars)"
    ]
    
    MAKE_PATTERNS = [
        r"how many (\w+) (?:vehicles|cars)",
        r"count (?:of|the) (\w+)(?: vehicles| cars|$)",
        r"(\w+) (?:vehicles|cars)",
        r"(\w+)(?:\s|$)"
    ]
    
    YEAR_PATTERNS = [
        r"(?:from|in|made in|year) (\d{4})",
        r"vehicles (?:from|in) (\d{4})",
        r"(\d{4}) (?:vehicles|cars)"
    ]
    
    CONDITION_PATTERNS = [
        r"(\w+) condition",
        r"condition (?:is )?(\w+)",
        r"(\w+) quality"
    ]

class AttributeQueryDetector:
    """Handles detection and parsing of attribute-based queries"""
    
    def __init__(self):
        self.patterns = AttributePatterns()
    
    def detect(self, query: str) -> AttributeQuery:
        """
        Detect if a query is asking about a specific attribute
        
        Args:
            query (str): The user query
            
        Returns:
            AttributeQuery: Parsed query information
        """
        if not query or not isinstance(query, str):
            return AttributeQuery(False)
        
        query_lower = query.lower().strip()
        
        # Try color detection
        color_result = self._detect_color(query_lower)
        if color_result.is_attribute_query:
            return color_result
        
        # Try make detection
        make_result = self._detect_make(query_lower)
        if make_result.is_attribute_query:
            return make_result
        
        # Try year detection
        year_result = self._detect_year(query_lower)
        if year_result.is_attribute_query:
            return year_result
        
        # Try condition detection
        condition_result = self._detect_condition(query_lower)
        if condition_result.is_attribute_query:
            return condition_result
        
        # Try general attribute pattern
        general_result = self._detect_general_attribute(query_lower)
        if general_result.is_attribute_query:
            return general_result
        
        return AttributeQuery(False)
    
    def _detect_color(self, query: str) -> AttributeQuery:
        """Detect color-based queries"""
        for pattern in self.patterns.COLOR_PATTERNS:
            match = re.search(pattern, query)
            if match:
                potential_color = match.group(1)
                if potential_color in self.patterns.COLORS:
                    return AttributeQuery(True, "color", potential_color)
        return AttributeQuery(False)
    
    def _detect_make(self, query: str) -> AttributeQuery:
        """Detect make-based queries"""
        for pattern in self.patterns.MAKE_PATTERNS:
            match = re.search(pattern, query)
            if match:
                potential_make = match.group(1)
                if potential_make in self.patterns.MAKES:
                    return AttributeQuery(True, "make", potential_make)
        return AttributeQuery(False)
    
    def _detect_year(self, query: str) -> AttributeQuery:
        """Detect year-based queries"""
        for pattern in self.patterns.YEAR_PATTERNS:
            match = re.search(pattern, query)
            if match:
                year = match.group(1)
                # Validate year range (reasonable for vehicles)
                if 1900 <= int(year) <= 2030:
                    return AttributeQuery(True, "year", year)
        return AttributeQuery(False)
    
    def _detect_condition(self, query: str) -> AttributeQuery:
        """Detect condition-based queries"""
        for pattern in self.patterns.CONDITION_PATTERNS:
            match = re.search(pattern, query)
            if match:
                potential_condition = match.group(1)
                if potential_condition in self.patterns.CONDITIONS:
                    return AttributeQuery(True, "condition", potential_condition)
        return AttributeQuery(False)
    
    def _detect_general_attribute(self, query: str) -> AttributeQuery:
        """Detect general attribute patterns"""
        general_match = re.search(r"with (\w+) (?:is|=) (\w+)", query)
        if general_match:
            return AttributeQuery(True, general_match.group(1), general_match.group(2))
        return AttributeQuery(False)

class CSVAttributeFilter:
    """Handles CSV-based filtering operations"""
    
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self._validate_dataset()
    
    def _validate_dataset(self) -> None:
        """Validate that the dataset exists and is readable"""
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset not found: {self.dataset_path}")
        
        if not os.path.isfile(self.dataset_path):
            raise ValueError(f"Dataset path is not a file: {self.dataset_path}")
    
    def filter_by_attribute(self, attribute_name: str, 
                          attribute_value: str) -> Tuple[Optional[List[Dict]], Optional[List[str]]]:
        """
        Filter CSV file by attribute value
        
        Args:
            attribute_name (str): Name of the column to filter on
            attribute_value (str): Value to match
            
        Returns:
            tuple: (filtered_rows, header) or (None, None) if error
        """
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                header = reader.fieldnames
                
                if not header or attribute_name not in header:
                    logger.warning(f"Attribute '{attribute_name}' not found in dataset")
                    if header:
                        logger.info(f"Available attributes: {', '.join(header)}")
                    return None, None
                
                matched_rows = []
                for row in reader:
                    if attribute_name in row and row[attribute_name]:
                        if row[attribute_name].lower() == attribute_value.lower():
                            matched_rows.append(row)
                            
                return matched_rows, header
                
        except Exception as e:
            logger.error(f"Error reading dataset: {str(e)}")
            return None, None
    
    def count_total_rows(self) -> int:
        """Count total rows in the dataset (excluding header)"""
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                return sum(1 for row in reader) - 1  # Subtract header
        except Exception as e:
            logger.error(f"Error counting rows: {str(e)}")
            return 0

class AttributeAnalyzer:
    """Provides statistical analysis of attribute filtering results"""
    
    def __init__(self, csv_filter: CSVAttributeFilter):
        self.csv_filter = csv_filter
        self.detector = AttributeQueryDetector()
    
    def analyze_query(self, query: str) -> Optional[QueryResult]:
        """
        Analyze a query and return detailed results
        
        Args:
            query (str): The user query
            
        Returns:
            QueryResult: Analysis results or None if error
        """
        # Detect the query
        parsed_query = self.detector.detect(query)
        
        if not parsed_query.is_attribute_query:
            logger.info(f"Query not recognized as attribute query: {query}")
            return None
        
        # Filter the data
        matched_rows, header = self.csv_filter.filter_by_attribute(
            parsed_query.attribute_name, parsed_query.attribute_value
        )
        
        if matched_rows is None:
            return None
        
        # Calculate statistics
        count = len(matched_rows)
        total = self.csv_filter.count_total_rows()
        percentage = (count / total * 100) if total > 0 else 0
        
        result = QueryResult(
            count=count,
            total=total,
            percentage=percentage,
            attribute=parsed_query.attribute_name,
            value=parsed_query.attribute_value,
            matched_rows=matched_rows
        )
        
        logger.info(str(result))
        return result

class DatasetDiscovery:
    """Handles discovery and validation of datasets"""
    
    POSSIBLE_PATHS = [
        "exports/vehicles.csv",
        "data/vehicles.csv",
        "../exports/vehicles.csv", 
        "../data/vehicles.csv",
        "Auto-Analyst/auto-analyst-backend/exports/vehicles.csv",
        "Auto-Analyst/auto-analyst-backend/data/vehicles.csv"
    ]
    
    @classmethod
    def find_dataset(cls) -> Optional[str]:
        """Find the vehicles dataset"""
        for path in cls.POSSIBLE_PATHS:
            if os.path.exists(path):
                logger.info(f"Found dataset at {path}")
                return path
        
        logger.warning("Could not find vehicles dataset")
        logger.info(f"Searched paths: {', '.join(cls.POSSIBLE_PATHS)}")
        return None

# Legacy function compatibility for existing code
def detect_attribute_query(query: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """Legacy compatibility function"""
    detector = AttributeQueryDetector()
    result = detector.detect(query)
    return result.is_attribute_query, result.attribute_name, result.attribute_value

def filter_csv_by_attribute(dataset_path: str, attribute_name: str, 
                          attribute_value: str) -> Tuple[Optional[List[Dict]], Optional[List[str]]]:
    """Legacy compatibility function"""
    try:
        csv_filter = CSVAttributeFilter(dataset_path)
        return csv_filter.filter_by_attribute(attribute_name, attribute_value)
    except (FileNotFoundError, ValueError):
        return None, None

def count_attribute_values(dataset_path: str, attribute_name: str, 
                         attribute_value: str) -> Optional[Dict]:
    """Legacy compatibility function"""
    try:
        csv_filter = CSVAttributeFilter(dataset_path)
        analyzer = AttributeAnalyzer(csv_filter)
        
        # Create a synthetic query for the analyzer based on attribute type
        if attribute_name == "color":
            query = f"how many {attribute_value} vehicles"
        elif attribute_name == "make":
            query = f"how many {attribute_value} vehicles"
        elif attribute_name == "year":
            query = f"vehicles from {attribute_value}"
        elif attribute_name == "condition":
            query = f"{attribute_value} condition vehicles"
        else:
            query = f"how many {attribute_value} {attribute_name}"
            
        result = analyzer.analyze_query(query)
        
        if result:
            return {
                'count': result.count,
                'total': result.total,
                'percentage': result.percentage,
                'attribute': result.attribute,
                'value': result.value,
                'matched_rows': result.matched_rows
            }
        return None
    except Exception as e:
        logger.error(f"Error in count_attribute_values: {str(e)}")
        return None

def find_dataset() -> Optional[str]:
    """Legacy compatibility function"""
    return DatasetDiscovery.find_dataset()

# Main execution and example usage
if __name__ == "__main__":
    # Example usage
    dataset_path = find_dataset()
    if dataset_path:
        try:
            csv_filter = CSVAttributeFilter(dataset_path)
            analyzer = AttributeAnalyzer(csv_filter)
            
            # Test some queries
            test_queries = [
                "how many green vehicles do we have?",
                "count of Toyota cars",
                "vehicles from 2022",
                "excellent condition vehicles"
            ]
            
            for query in test_queries:
                print(f"\nAnalyzing: {query}")
                result = analyzer.analyze_query(query)
                if result:
                    print(f"Result: {result}")
                else:
                    print("No results found")
                    
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("No dataset found for analysis") 