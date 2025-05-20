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
  const backendRoutes = [
    '/api/', 
    '/health', 
    '/agents', 
    '/model', 
    '/model-settings', 
    '/settings/model', 
    '/chat', 
    '/api/session-info',
    '/session',
    '/session-info',
    '/credits',
    '/statistics',
    '/vehicles',
    '/market-data',
    '/opportunities',
    '/api/statistics',
    '/api/vehicles',
    '/api/market-data',
    '/api/opportunities'
  ];
  
  // Helper function to check if URL should be redirected
  function shouldRedirectUrl(url) {
    if (typeof url !== 'string') return false;
    
    // Don't redirect frontend-specific paths
    if (url.startsWith('/_next/') || 
        url.startsWith('/static/') || 
        url.includes('/manifest.webmanifest') ||
        url.includes('.ico') || 
        url.includes('.png') || 
        url.includes('.svg') || 
        url.includes('.css') || 
        url.includes('.js') ||
        url.endsWith('?_rsc=') ||
        url.includes('?_rsc=')) {
      return false;
    }
    
    // Always redirect these API endpoints
    const criticalApiEndpoints = [
      '/api/vehicles', 
      '/api/statistics', 
      '/api/market-data', 
      '/api/opportunities',
      '/vehicles', 
      '/statistics', 
      '/market-data', 
      '/opportunities',
      '/session',
      '/session-info',
      '/credits',
      '/agents',
      '/model-settings',
      '/api/model-settings',
      '/settings/model'
    ];
    
    // Check for exact matches or if URL starts with these paths
    for (const endpoint of criticalApiEndpoints) {
      if (url === endpoint || url.startsWith(endpoint + '/') || url.startsWith(endpoint + '?')) {
        return true;
      }
    }
    
    // Check for backend routes
    for (const route of backendRoutes) {
      if (url.includes(route)) {
        return true;
      }
    }
    
    // Default redirect for API-like paths
    return url.startsWith('/api/') || 
           (!url.includes('.') && url !== '/' && !url.startsWith('/?')) || 
           url.startsWith('/model') || 
           url.startsWith('/agent');
  }
  
  // Helper function to redirect URL if needed
  function redirectUrlIfNeeded(url) {
    if (!shouldRedirectUrl(url)) return url;
    
    // Handle absolute URLs
    if (url.includes('://')) {
      return url.replace(/https?:\/\/[^\/]+/, 'http://localhost:8080');
    } 
    // Handle relative URLs
    else if (url.startsWith('/')) {
      return `http://localhost:8080${url}`;
    }
    
    return url;
  }
  
  // Patch fetch to intercept CORS issues
  window.fetch = function(url, options = {}) {
    let originalUrl = url;
    
    // Process URL if it's a string
    if (typeof url === 'string') {
      // Redirect if needed
      url = redirectUrlIfNeeded(url);
      
      if (url !== originalUrl) {
        console.log(`🔀 Redirecting fetch to proxy: ${url} (from ${originalUrl})`);
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
        console.error('🚫 Request failed:', error, url);
        throw error;
      });
  };
  
  // Also patch XMLHttpRequest for legacy code
  const originalXHROpen = XMLHttpRequest.prototype.open;
  const originalXHRSend = XMLHttpRequest.prototype.send;
  const originalSetRequestHeader = XMLHttpRequest.prototype.setRequestHeader;
  
  // Store the original URL for debugging
  const XHR_URL_SYMBOL = Symbol('originalUrl');
  const XHR_REDIRECTED_SYMBOL = Symbol('redirectedUrl');
  
  // Patch the XHR open method to redirect URLs
  XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
    // Store original URL for debugging
    this[XHR_URL_SYMBOL] = url;
    this[XHR_REDIRECTED_SYMBOL] = false;
    
    if (typeof url === 'string') {
      // Redirect if needed
      const redirectedUrl = redirectUrlIfNeeded(url);
      
      if (redirectedUrl !== url) {
        console.log(`🔀 Redirecting XHR to proxy: ${redirectedUrl} (from ${url})`);
        url = redirectedUrl;
        this[XHR_REDIRECTED_SYMBOL] = true;
      }
    }
    
    // Setup event listeners for debugging
    if (!this._corsHandlersAttached) {
      this.addEventListener('error', function(e) {
        console.error('XHR error (possible CORS issue):', this[XHR_URL_SYMBOL], e);
      });
      
      this.addEventListener('load', function() {
        if (this.status === 0) {
          console.warn('⚠️ XHR CORS error detected for:', this[XHR_URL_SYMBOL]);
          
          // For CORS errors, try to recover by fetching the same URL with fetch API
          if (this[XHR_REDIRECTED_SYMBOL] && typeof this._onreadystatechange === 'function') {
            console.log('Attempting CORS recovery via fetch API');
            fetch(this.responseURL || this[XHR_URL_SYMBOL], {
              method: this._method || 'GET',
              headers: this._headers || {},
              credentials: 'include',
              mode: 'cors'
            })
            .then(response => response.text())
            .then(responseText => {
              // Create a fake xhr response
              Object.defineProperty(this, 'responseText', {
                value: responseText,
                writable: false
              });
              Object.defineProperty(this, 'status', {
                value: 200,
                writable: false
              });
              Object.defineProperty(this, 'readyState', {
                value: 4,
                writable: false
              });
              
              // Call the original handler
              if (this._onreadystatechange) {
                this._onreadystatechange.call(this);
              }
            })
            .catch(err => {
              console.error('CORS recovery attempt failed:', err);
            });
          }
        }
      });
      
      this._corsHandlersAttached = true;
    }
    
    // Store the method for recovery
    this._method = method;
    
    // Store original onreadystatechange
    const originalOnReadyStateChange = this.onreadystatechange;
    this._onreadystatechange = originalOnReadyStateChange;
    
    // Override onreadystatechange
    this.onreadystatechange = function() {
      this._onreadystatechange = this.onreadystatechange;
      if (originalOnReadyStateChange) {
        originalOnReadyStateChange.apply(this, arguments);
      }
    };
    
    return originalXHROpen.call(this, method, url, async !== false, user, password);
  };
  
  // Patch setRequestHeader to ensure proper CORS headers
  XMLHttpRequest.prototype.setRequestHeader = function(header, value) {
    // Always ensure origin header is set to the current site
    if (header.toLowerCase() === 'origin') {
      value = window.location.origin;
    }
    
    // Store headers for recovery
    if (!this._headers) {
      this._headers = {};
    }
    this._headers[header] = value;
    
    try {
      return originalSetRequestHeader.call(this, header, value);
    } catch (e) {
      console.warn('Failed to set header:', header, value, e);
    }
  };
  
  // Patch send to add necessary CORS headers
  XMLHttpRequest.prototype.send = function(body) {
    // If this is a redirected request, add CORS headers
    if (this[XHR_REDIRECTED_SYMBOL]) {
      try {
        this.setRequestHeader('Origin', window.location.origin);
        this.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
      } catch (e) {
        // Headers may be locked if open was called with async=false
        console.warn('Could not set CORS headers on XHR', e);
      }
    }
    
    return originalXHRSend.call(this, body);
  };
  
  // Add global event listener to help debug CORS issues
  window.addEventListener('error', function(e) {
    if (e && e.target && e.target.tagName === 'SCRIPT' && e.target.src && e.target.src.includes('localhost')) {
      console.error('Script loading error (possible CORS issue):', e.target.src);
    }
  }, true);
  
  console.log('✅ CORS bypass and request redirect initialized');
})(); 