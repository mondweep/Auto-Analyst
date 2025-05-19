// port-redirect.js - Redirect requests from port 8000 to 8080
// Add this script to the app or page layout to ensure all requests are properly routed

if (typeof window !== 'undefined') {
  // Create a proxy for fetch that redirects URLs
  const originalFetch = window.fetch;
  
  window.fetch = function(url, options) {
    // If this is a URL to port 8000, redirect it to port 8080
    if (typeof url === 'string' && url.includes('localhost:8000')) {
      const newUrl = url.replace('localhost:8000', 'localhost:8080');
      console.log(`Redirecting request from ${url} to ${newUrl}`);
      return originalFetch(newUrl, options);
    }
    
    // Otherwise, use the original URL
    return originalFetch(url, options);
  };
  
  console.log('✅ Port redirection initialized - redirecting requests from port 8000 to 8080');
} 