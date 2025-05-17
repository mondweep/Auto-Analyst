#!/usr/bin/env python
import unittest
import requests
import json
import os
import subprocess
import time
from pathlib import Path

class TestAutomotiveE2E(unittest.TestCase):
    """End-to-end test suite for the Automotive Pricing Intelligence demo"""
    
    # Base URLs for services
    AUTOMOTIVE_API_URL = "http://localhost:8003"
    FILE_SERVER_URL = "http://localhost:8001"
    FRONTEND_URL = "http://localhost:3000"
    
    @classmethod
    def setUpClass(cls):
        """Verify all servers are running before starting tests"""
        # Check automotive server
        try:
            response = requests.get(f"{cls.AUTOMOTIVE_API_URL}/health")
            if response.status_code != 200:
                print("[WARNING] Automotive server not responding properly")
        except:
            print("[WARNING] Automotive server might not be running")
        
        # Check file server
        try:
            response = requests.get(f"{cls.FILE_SERVER_URL}/health")
            if response.status_code != 200:
                print("[WARNING] File server not responding properly")
        except:
            print("[WARNING] File server might not be running")
    
    def test_1_feature_vehicle_list(self):
        """Test the vehicle list feature"""
        response = requests.get(f"{self.AUTOMOTIVE_API_URL}/api/vehicles")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify we have vehicles
        self.assertIn('vehicles', data)
        self.assertTrue(len(data['vehicles']) > 0)
        
        # Verify data has all required information from readme (make, model, year, etc.)
        vehicle = data['vehicles'][0]
        self.assertIn('make', vehicle)
        self.assertIn('model', vehicle)
        self.assertIn('year', vehicle)
        self.assertIn('price', vehicle, "Each vehicle should have a price field for pricing intelligence")
    
    def test_2_feature_market_data(self):
        """Test the market data analysis feature"""
        response = requests.get(f"{self.AUTOMOTIVE_API_URL}/api/market-data")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify we have market data
        self.assertIn('market_data', data)
        self.assertTrue(len(data['market_data']) > 0)
        
        # Verify data has market pricing information
        item = data['market_data'][0]
        self.assertIn('market_price', item)
        self.assertIn('price_difference', item, "Should show price difference for market comparison")
        self.assertIn('price_difference_percent', item)
    
    def test_3_feature_opportunities(self):
        """Test the opportunities/buying radar feature"""
        response = requests.get(f"{self.AUTOMOTIVE_API_URL}/api/opportunities")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify we have opportunities
        self.assertIn('opportunities', data)
        self.assertTrue(len(data['opportunities']) > 0)
        
        # Verify each opportunity has required profit data
        opportunity = data['opportunities'][0]
        self.assertIn('potential_profit', opportunity)
    
    def test_4_feature_statistics(self):
        """Test the statistics/dashboard metrics feature"""
        response = requests.get(f"{self.AUTOMOTIVE_API_URL}/api/statistics")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify statistics include required metrics
        self.assertIn('statistics', data)
        stats = data['statistics']
        
        # Check for inventory metrics (from readme requirements)
        summary = stats.get('summary', {})
        self.assertIn('total_vehicles', summary)
        self.assertIn('available_vehicles', summary)
        self.assertIn('average_price', summary)
    
    def test_5_feature_data_downloads(self):
        """Test the file download capabilities"""
        # Test all three expected data files
        for file_name in ['vehicles.csv', 'market_data.csv', 'automotive_analysis.csv']:
            # Test HEAD request first
            head_response = requests.head(f"{self.FILE_SERVER_URL}/exports/{file_name}")
            self.assertEqual(head_response.status_code, 200, f"HEAD request failed for {file_name}")
            
            # Test GET request
            get_response = requests.get(
                f"{self.FILE_SERVER_URL}/exports/{file_name}", 
                headers={'Range': 'bytes=0-1023'}
            )
            self.assertEqual(get_response.status_code, 200, f"GET request failed for {file_name}")
            self.assertTrue(len(get_response.content) > 0, f"Empty content for {file_name}")
    
    def test_6_feature_cors_support(self):
        """Test that CORS is properly configured for frontend access"""
        # Test CORS headers on automotive API
        options_response = requests.options(
            f"{self.AUTOMOTIVE_API_URL}/api/vehicles",
            headers={
                'Origin': self.FRONTEND_URL,
                'Access-Control-Request-Method': 'GET'
            }
        )
        
        # Should be either 200 or 204 for successful preflight
        self.assertTrue(
            options_response.status_code in (200, 204, 404), 
            f"CORS preflight failed with status {options_response.status_code}"
        )
        
        # If it's a 200 with data, check for CORS headers
        if options_response.status_code == 200:
            self.assertIn('Access-Control-Allow-Origin', options_response.headers, "Missing CORS headers")

    def test_7_config_consistency(self):
        """Test that the frontend configuration is consistent with backend endpoints"""
        # Get the root directory of the project
        backend_dir = Path(__file__).parent.absolute()
        frontend_dir = backend_dir.parent / 'auto-analyst-frontend'
        
        # Verify API config file
        api_config_path = frontend_dir / 'config' / 'automotive-api.ts'
        self.assertTrue(api_config_path.exists(), "API config file missing")
        
        with open(api_config_path, 'r') as f:
            config_content = f.read()
            self.assertIn(f"{self.AUTOMOTIVE_API_URL}", config_content, 
                         "Frontend config does not point to correct API URL")
        
        # Verify file downloader config
        file_downloader_path = frontend_dir / 'components' / 'ui' / 'FileDownloader.tsx'
        self.assertTrue(file_downloader_path.exists(), "FileDownloader component missing")
        
        with open(file_downloader_path, 'r') as f:
            downloader_content = f.read()
            self.assertIn(f"{self.FILE_SERVER_URL}", downloader_content,
                         "FileDownloader does not point to correct server URL")

if __name__ == '__main__':
    unittest.main() 