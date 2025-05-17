#!/usr/bin/env python
import unittest
import requests
import json
import os

class TestServers(unittest.TestCase):
    """Test suite for validating all server functionalities"""
    
    # File Server Tests (Port 8001)
    def test_file_server_health(self):
        """Test that the file server health endpoint responds correctly"""
        response = requests.get('http://localhost:8001/health')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertIn('File server', data['message'])
    
    def test_file_server_export_files(self):
        """Test that the file server can serve all expected export files"""
        files = ['vehicles.csv', 'market_data.csv', 'automotive_analysis.csv']
        for file in files:
            response = requests.head(f'http://localhost:8001/exports/{file}')
            self.assertEqual(response.status_code, 200, f"File {file} not found")
    
    # Automotive API Tests (Port 8003)
    def test_automotive_api_health(self):
        """Test that the automotive API health endpoint responds correctly"""
        response = requests.get('http://localhost:8003/health')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
    
    def test_automotive_api_vehicles(self):
        """Test that the vehicles endpoint returns valid data"""
        response = requests.get('http://localhost:8003/api/vehicles')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('vehicles', data)
        self.assertTrue(len(data['vehicles']) > 0)
        # Validate first vehicle has expected fields
        vehicle = data['vehicles'][0]
        expected_fields = ['id', 'make', 'model', 'year', 'price', 'color']
        for field in expected_fields:
            self.assertIn(field, vehicle)
    
    def test_automotive_api_market_data(self):
        """Test that the market data endpoint returns valid data"""
        response = requests.get('http://localhost:8003/api/market-data')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('market_data', data)
        self.assertTrue(len(data['market_data']) > 0)
    
    def test_automotive_api_opportunities(self):
        """Test that the opportunities endpoint returns valid data"""
        response = requests.get('http://localhost:8003/api/opportunities')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('opportunities', data)
    
    def test_automotive_api_statistics(self):
        """Test that the statistics endpoint returns valid data"""
        response = requests.get('http://localhost:8003/api/statistics')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('statistics', data)
    
    # Frontend Connection Test
    def test_frontend_api_config(self):
        """Test that the frontend is configured to use the correct API URL"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   'auto-analyst-frontend', 'config', 'automotive-api.ts')
        with open(config_path, 'r') as f:
            content = f.read()
        self.assertIn("http://localhost:8003", content)

if __name__ == '__main__':
    unittest.main() 