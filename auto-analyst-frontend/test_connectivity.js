// test_connectivity.js - Tests connectivity between services

// Using dynamic import for node-fetch
async function testConnections() {
  console.log('Testing connections between services...');
  
  const fetch = (await import('node-fetch')).default;
  
  try {
    // Test frontend server
    console.log('\n--- Testing Frontend Server ---');
    const frontendResponse = await fetch('http://localhost:3000/api/health');
    if (frontendResponse.ok) {
      console.log('✅ Frontend server is running');
    } else {
      console.log(`❌ Frontend server response: ${frontendResponse.status} ${frontendResponse.statusText}`);
    }
  } catch (error) {
    console.log(`❌ Cannot connect to frontend server: ${error.message}`);
  }

  try {
    // Test main app server
    console.log('\n--- Testing Main App Server ---');
    const appResponse = await fetch('http://localhost:8000/health');
    if (appResponse.ok) {
      const appData = await appResponse.json();
      console.log(`✅ App server is running: ${JSON.stringify(appData)}`);
    } else {
      console.log(`❌ App server response: ${appResponse.status} ${appResponse.statusText}`);
    }
  } catch (error) {
    console.log(`❌ Cannot connect to app server: ${error.message}`);
  }

  try {
    // Test file server
    console.log('\n--- Testing File Server ---');
    const fileResponse = await fetch('http://localhost:8001/health');
    if (fileResponse.ok) {
      const fileData = await fileResponse.json();
      console.log(`✅ File server is running: ${JSON.stringify(fileData)}`);
    } else {
      console.log(`❌ File server response: ${fileResponse.status} ${fileResponse.statusText}`);
    }
  } catch (error) {
    console.log(`❌ Cannot connect to file server: ${error.message}`);
  }

  try {
    // Test API communication 
    console.log('\n--- Testing API Integration ---');
    const apiResponse = await fetch('http://localhost:8000/api/file-server/datasets');
    if (apiResponse.ok) {
      const datasets = await apiResponse.json();
      console.log('✅ API can access datasets:');
      console.log(datasets);
    } else {
      console.log(`❌ API integration response: ${apiResponse.status} ${apiResponse.statusText}`);
    }
  } catch (error) {
    console.log(`❌ Cannot test API integration: ${error.message}`);
  }
}

testConnections().catch(error => {
  console.error('Error running tests:', error);
}); 