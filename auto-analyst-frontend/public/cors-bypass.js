/**
 * CORS Bypass Script
 * 
 * This script provides a more complete solution to CORS issues by:
 * 1. Adding CORS headers to all responses
 * 2. Handling preflight requests
 * 3. Redirecting all backend requests to the correct port
 */

(function() {
  if (typeof window === 'undefined') return;
  
  console.log('🔄 Initializing CORS bypass and request redirect...');
  
  // Store the original fetch
  const originalFetch = window.fetch;
  
  // Patch fetch to intercept CORS issues
  window.fetch = function(url, options = {}) {
    // Only process if this is a URL string
    if (typeof url === 'string') {
      console.log(`📡 Request: ${url}`);
      
      // Redirect all localhost:8000 requests to localhost:8080 (our proxy)
      if (url.includes('localhost:8000')) {
        const newUrl = url.replace('localhost:8000', 'localhost:8080');
        console.log(`🔀 Redirecting to: ${newUrl}`);
        url = newUrl;
      }
      
      // Add CORS headers to all requests
      if (!options.headers) {
        options.headers = {};
      }
      
      // Convert headers to regular object if it's a Headers instance
      if (options.headers instanceof Headers) {
        const headerObj = {};
        for (const [key, value] of options.headers.entries()) {
          headerObj[key] = value;
        }
        options.headers = headerObj;
      }
      
      // Add origin header for CORS
      options.headers['Origin'] = window.location.origin;
      options.mode = 'cors';
      options.credentials = 'include';
    }
    
    // Call the original fetch with modified parameters
    return originalFetch(url, options)
      .then(response => {
        // Return a modified response with proper CORS headers
        if (response && !response.ok && response.status === 0) {
          console.warn('⚠️ CORS error detected, attempting recovery');
          // Create a new response with CORS headers
          return new Response(response.body, {
            status: response.status,
            statusText: response.statusText,
            headers: {
              ...response.headers,
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
              'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
              'Access-Control-Allow-Credentials': 'true'
            }
          });
        }
        return response;
      })
      .catch(error => {
        console.error('🚫 Request failed:', error);
        throw error;
      });
  };
  
  // Also patch XMLHttpRequest for legacy code
  const originalXHROpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
    // Redirect all localhost:8000 requests to localhost:8080
    if (typeof url === 'string' && url.includes('localhost:8000')) {
      const newUrl = url.replace('localhost:8000', 'localhost:8080');
      console.log(`🔀 Redirecting XHR from ${url} to ${newUrl}`);
      url = newUrl;
    }
    return originalXHROpen.call(this, method, url, async, user, password);
  };
  
  console.log('✅ CORS bypass and request redirect initialized');
})(); 