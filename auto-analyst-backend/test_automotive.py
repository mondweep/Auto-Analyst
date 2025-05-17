#!/usr/bin/env python
import unittest
import requests
import json

class TestAutomotiveFeatures(unittest.TestCase):
    """Test suite for the Automotive Pricing Intelligence features"""
    
    # Base URLs for API endpoints
    AUTOMOTIVE_API_URL = "http://localhost:8003"
    FILE_SERVER_URL = "http://localhost:8001"
    
    def test_server_health(self):
        """Test that both servers are healthy"""
        # Test automotive API health
        response = requests.get(f"{self.AUTOMOTIVE_API_URL}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        
        # Test file server health
        response = requests.get(f"{self.FILE_SERVER_URL}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
    
    def test_vehicles_endpoint(self):
        """Test the vehicles endpoint returns valid data"""
        response = requests.get(f"{self.AUTOMOTIVE_API_URL}/api/vehicles")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('vehicles', data)
        self.assertTrue(len(data['vehicles']) > 0)
        
        # Validate vehicle schema
        vehicle = data['vehicles'][0]
        required_fields = [
            'id', 'make', 'model', 'year', 'color', 'price', 'mileage',
            'condition', 'fuel_type', 'days_in_inventory', 'vin', 'is_sold'
        ]
        for field in required_fields:
            self.assertIn(field, vehicle)
    
    def test_market_data_endpoint(self):
        """Test the market data endpoint returns valid data"""
        response = requests.get(f"{self.AUTOMOTIVE_API_URL}/api/market-data")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('market_data', data)
        self.assertTrue(len(data['market_data']) > 0)
        
        # Validate market data schema
        market_item = data['market_data'][0]
        required_fields = [
            'id', 'make', 'model', 'year', 'market_price', 
            'price_difference', 'price_difference_percent', 'days_in_inventory'
        ]
        for field in required_fields:
            self.assertIn(field, market_item, f"Missing field: {field}")
    
    def test_opportunities_endpoint(self):
        """Test the opportunities endpoint returns valid data"""
        response = requests.get(f"{self.AUTOMOTIVE_API_URL}/api/opportunities")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('opportunities', data)
        
        # No need to test length as opportunities may be empty in some cases
        if data['opportunities']:
            # Validate opportunity schema
            opportunity = data['opportunities'][0]
            required_fields = [
                'id', 'make', 'model', 'year', 'your_price', 'market_price', 'potential_profit'
            ]
            for field in required_fields:
                self.assertIn(field, opportunity, f"Missing field: {field}")
    
    def test_statistics_endpoint(self):
        """Test the statistics endpoint returns valid data"""
        response = requests.get(f"{self.AUTOMOTIVE_API_URL}/api/statistics")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('statistics', data)
        
        # Validate statistics contains required data
        stats = data['statistics']
        required_sections = [
            'makes', 'conditions', 'price_ranges', 'inventory_age', 'summary'
        ]
        for section in required_sections:
            self.assertIn(section, stats, f"Missing statistics section: {section}")
        
        # Validate summary has required metrics
        summary = stats['summary']
        required_metrics = [
            'total_vehicles', 'available_vehicles', 'sold_vehicles',
            'average_price', 'average_days_in_inventory'
        ]
        for metric in required_metrics:
            self.assertIn(metric, summary, f"Missing summary metric: {metric}")
    
    def test_file_downloads(self):
        """Test that export files can be downloaded"""
        export_files = [
            'vehicles.csv', 
            'market_data.csv', 
            'automotive_analysis.csv'
        ]
        
        for file in export_files:
            response = requests.head(f"{self.FILE_SERVER_URL}/exports/{file}")
            self.assertEqual(response.status_code, 200, f"Failed to access {file}")
    
    def test_frontend_api_connection(self):
        """Test that the frontend is correctly configured to use our API"""
        import os
        
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'auto-analyst-frontend', 
            'config', 
            'automotive-api.ts'
        )
        
        with open(config_path, 'r') as f:
            config_content = f.read()
        
        self.assertIn(f"{self.AUTOMOTIVE_API_URL}", config_content)

if __name__ == '__main__':
    unittest.main() 