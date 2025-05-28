// port-redirect.js - Redirect requests from port 8000 to 8000 (deprecated - using cors-bypass.js instead)
// Add this script to the app or page layout to ensure all requests are properly routed

if (typeof window !== 'undefined') {
  // Create a proxy for fetch that redirects URLs
  const originalFetch = window.fetch;
  
  window.fetch = function(url, options) {
    // If this is a URL to port 8000, keep it on port 8000 (updated to match backend)
    if (typeof url === 'string' && url.includes('localhost:8000')) {
      const newUrl = url; // No redirection needed anymore
      console.log(`Request to ${url} (no redirection needed)`);
      return originalFetch(newUrl, options);
    }
    
    // Otherwise, use the original URL
    return originalFetch(url, options);
  };
  
  console.log('✅ Port redirection initialized - keeping requests on port 8000 (deprecated script)');
} 