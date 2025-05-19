// API URLs and configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
export const PREVIEW_API_URL = process.env.NEXT_PUBLIC_PREVIEW_API_URL || 'http://localhost:8080';
export const UPLOAD_API_URL = process.env.NEXT_PUBLIC_UPLOAD_API_URL || 'http://localhost:8001';
export const AUTOMOTIVE_API_URL = API_URL;

// Demo mode detection - can be enabled to use fallback data
export const DEMO_MODE = true;

// API status checking utility
export const checkApiStatus = async () => {
  const endpoints = [
    { url: API_URL, name: 'Main API' },
    { url: UPLOAD_API_URL, name: 'File Server' },
    { url: AUTOMOTIVE_API_URL, name: 'Automotive API' }
  ];

  const results = await Promise.all(
    endpoints.map(async (endpoint) => {
      try {
        const response = await fetch(`${endpoint.url}/health`, { 
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
          // Short timeout to avoid long waits
          signal: AbortSignal.timeout(1000) 
        });
        return { 
          name: endpoint.name, 
          url: endpoint.url, 
          status: response.ok ? 'online' : 'error',
          statusCode: response.status
        };
      } catch (error) {
        console.warn(`Could not connect to ${endpoint.name} at ${endpoint.url}`);
        return { 
          name: endpoint.name, 
          url: endpoint.url, 
          status: 'offline',
          statusCode: 0
        };
      }
    })
  );

  // Return the overall status and details for each endpoint
  return {
    allOnline: results.every(r => r.status === 'online'),
    results
  };
};

// Export API_URL as default export
export default API_URL; 