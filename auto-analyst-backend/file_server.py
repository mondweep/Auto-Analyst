#!/usr/bin/env python
import os
import http.server
import socketserver
from urllib.parse import urlparse, unquote

PORT = 8001
EXPORTS_DIR = os.path.join(os.path.dirname(__file__), "exports")

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL path
        parsed_path = urlparse(self.path)
        path = unquote(parsed_path.path)
        
        # Check if the request is for a file in the exports directory
        if path.startswith('/exports/'):
            # Get the filename from the path
            filename = path.split('/')[-1]
            
            # Check if it's an allowed file
            allowed_files = ['vehicles.csv', 'market_data.csv', 'automotive_analysis.csv']
            if filename in allowed_files:
                file_path = os.path.join(EXPORTS_DIR, filename)
                
                if os.path.exists(file_path):
                    # Set headers for file download
                    self.send_response(200)
                    self.send_header('Content-type', 'text/csv')
                    self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                    self.send_header('Access-Control-Allow-Origin', '*')  # Enable CORS
                    self.end_headers()
                    
                    # Send the file content
                    with open(file_path, 'rb') as file:
                        self.wfile.write(file.read())
                    return
            
            # If file not found or not allowed
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'File not found')
            return
        
        # For other endpoints, return a simple status message
        elif path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "message": "File server is running"}')
            return
        
        # Provide index info
        elif path == '/' or path == '':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'{"message": "File server running", "endpoints": ["/exports/vehicles.csv", "/exports/market_data.csv", "/exports/automotive_analysis.csv"]}')
            return
        
        # Return 404 for all other paths
        self.send_response(404)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(b'Endpoint not found')

if __name__ == "__main__":
    # Create a CORS-enabled server
    handler = CustomHandler
    
    print(f"Starting file server on port {PORT}...")
    print(f"Serving files from {EXPORTS_DIR}")
    print(f"Available endpoints:")
    print(f"  - /health")
    print(f"  - /exports/vehicles.csv")
    print(f"  - /exports/market_data.csv")
    print(f"  - /exports/automotive_analysis.csv")
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped by user")
            httpd.server_close() 