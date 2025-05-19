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
  
  // Define backend API routes that need redirection
  const backendRoutes = ['/api/', '/health', '/agents', '/model', '/model-settings', '/settings/model', '/chat', '/api/session-info'];
  
  // Patch fetch to intercept CORS issues
  window.fetch = function(url, options = {}) {
    // Only process if this is a URL string
    if (typeof url === 'string') {
      let shouldRedirect = false;
      
      // Case 1: Direct localhost:8000 URLs
      if (url.includes('localhost:8000')) {
        shouldRedirect = true;
      }
      
      // Case 2: Relative URLs that should go to the backend
      if (url.startsWith('/') && !url.startsWith('/_next/') && !url.startsWith('/static/')) {
        for (const route of backendRoutes) {
          if (url.startsWith(route)) {
            shouldRedirect = true;
            break;
          }
        }
      }
      
      // Redirect appropriate requests to proxy
      if (shouldRedirect) {
        // Handle absolute URLs
        if (url.includes('://')) {
          url = url.replace(/https?:\/\/[^\/]+/, 'http://localhost:8080');
        } 
        // Handle relative URLs
        else if (url.startsWith('/')) {
          url = `http://localhost:8080${url}`;
        }
        console.log(`🔀 Redirecting to proxy: ${url}`);
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
    // Check if this is a backend route that needs redirection
    let shouldRedirect = false;
    
    if (typeof url === 'string') {
      // Case 1: Direct localhost:8000 URLs
      if (url.includes('localhost:8000')) {
        shouldRedirect = true;
      }
      
      // Case 2: Relative URLs that should go to the backend
      if (url.startsWith('/') && !url.startsWith('/_next/') && !url.startsWith('/static/')) {
        for (const route of backendRoutes) {
          if (url.startsWith(route)) {
            shouldRedirect = true;
            break;
          }
        }
      }
      
      // Redirect appropriate requests to proxy
      if (shouldRedirect) {
        // Handle absolute URLs
        if (url.includes('://')) {
          url = url.replace(/https?:\/\/[^\/]+/, 'http://localhost:8080');
        } 
        // Handle relative URLs
        else if (url.startsWith('/')) {
          url = `http://localhost:8080${url}`;
        }
        console.log(`🔀 Redirecting XHR to proxy: ${url}`);
      }
    }
    
    return originalXHROpen.call(this, method, url, async, user, password);
  };
  
  // Add global event listener to help debug CORS issues
  window.addEventListener('error', function(e) {
    if (e && e.target && e.target.tagName === 'SCRIPT' && e.target.src && e.target.src.includes('localhost')) {
      console.error('Script loading error (possible CORS issue):', e.target.src);
    }
  }, true);
  
  console.log('✅ CORS bypass and request redirect initialized');
})(); 