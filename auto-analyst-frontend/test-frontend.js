/**
 * Simple test script to verify the automotive frontend is functioning correctly.
 * Run with: node test-frontend.js
 */

const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');

console.log('🧪 Auto-Analyst Frontend Test');
console.log('============================');

// Get API URL directly from the file
const configPath = path.join(__dirname, 'config', 'automotive-api.ts');
fs.readFile(configPath, 'utf8', (err, data) => {
  if (err) {
    console.error('❌ Failed to read API config file:', err.message);
    return;
  }
  
  // Extract API URL using regex
  const apiUrlMatch = data.match(/['"]http:\/\/localhost:(\d+)['"]/);
  if (!apiUrlMatch) {
    console.error('❌ Failed to find API URL in config file');
    return;
  }
  
  const port = apiUrlMatch[1];
  const apiUrl = `http://127.0.0.1:${port}`;
  
  // Test API Configuration
  console.log('\n1. Testing API Configuration...');
  if (port === '8003') {
    console.log('✅ API configuration is correct');
  } else {
    console.error('❌ API configuration is incorrect:', apiUrl);
    console.error('   Expected: http://localhost:8003');
  }
  
  runTests(apiUrl);
});

function runTests(apiUrl) {
  // Test Automotive API Connection
  console.log('\n2. Testing Automotive API Connection...');
  http.get(`${apiUrl}/health`, (res) => {
    let data = '';
    
    res.on('data', (chunk) => {
      data += chunk;
    });
    
    res.on('end', () => {
      try {
        const health = JSON.parse(data);
        if (health.status === 'ok') {
          console.log(`✅ Automotive API is healthy: ${health.status}`);
        } else {
          console.error('❌ Automotive API health check failed:', health);
        }
      } catch (e) {
        console.error('❌ Failed to parse health check response:', e.message);
      }
      
      // Run next test
      testFileServer(apiUrl);
    });
  }).on('error', (err) => {
    console.error('❌ Failed to connect to Automotive API:', err.message);
    testFileServer(apiUrl);
  });
}

// Test File Server Connection
function testFileServer(apiUrl) {
  console.log('\n3. Testing File Server Connection...');
  http.get('http://127.0.0.1:8001/health', (res) => {
    let data = '';
    
    res.on('data', (chunk) => {
      data += chunk;
    });
    
    res.on('end', () => {
      try {
        const health = JSON.parse(data);
        if (health.status === 'ok') {
          console.log(`✅ File Server is healthy: ${health.status}`);
        } else {
          console.error('❌ File Server health check failed:', health);
        }
      } catch (e) {
        console.error('❌ Failed to parse health check response:', e.message);
      }
      
      // Run next test
      testVehicleData(apiUrl);
    });
  }).on('error', (err) => {
    console.error('❌ Failed to connect to File Server:', err.message);
    testVehicleData(apiUrl);
  });
}

// Test Vehicle Data API
function testVehicleData(apiUrl) {
  console.log('\n4. Testing Vehicle Data API...');
  http.get(`${apiUrl}/api/vehicles`, (res) => {
    let data = '';
    
    res.on('data', (chunk) => {
      data += chunk;
    });
    
    res.on('end', () => {
      try {
        const vehicleData = JSON.parse(data);
        if (vehicleData.vehicles && vehicleData.vehicles.length > 0) {
          console.log(`✅ Vehicle API returned ${vehicleData.vehicles.length} vehicles`);
          console.log(`   Sample: ${vehicleData.vehicles[0].year} ${vehicleData.vehicles[0].make} ${vehicleData.vehicles[0].model}`);
        } else {
          console.error('❌ Vehicle API returned no data or invalid format');
        }
      } catch (e) {
        console.error('❌ Failed to parse vehicle data response:', e.message);
      }
      
      console.log('\n============================');
      console.log('Frontend tests completed.');
      console.log('To view the automotive demo interface, navigate to:');
      console.log('http://localhost:3000/automotive');
    });
  }).on('error', (err) => {
    console.error('❌ Failed to fetch vehicle data:', err.message);
    console.log('\n============================');
    console.log('Frontend tests completed with errors.');
  });
} 