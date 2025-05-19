// port-redirect.js - Redirect requests from port 8000 to 8080
// This script intercepts all fetch requests to port 8000 and redirects them to port 8080

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
  
  // Also hijack XMLHttpRequest for any legacy code
  const originalOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function(method, url, ...args) {
    if (typeof url === 'string' && url.includes('localhost:8000')) {
      const newUrl = url.replace('localhost:8000', 'localhost:8080');
      console.log(`Redirecting XHR from ${url} to ${newUrl}`);
      return originalOpen.call(this, method, newUrl, ...args);
    }
    return originalOpen.call(this, method, url, ...args);
  };
  
  console.log('✅ Port redirection initialized - redirecting requests from port 8000 to 8080');
} 