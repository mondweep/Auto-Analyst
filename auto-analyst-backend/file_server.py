#!/usr/bin/env python
import os
import http.server
import socketserver
import json
import cgi
from urllib.parse import urlparse, unquote
import sys

PORT = 8001
EXPORTS_DIR = os.path.join(os.path.dirname(__file__), "exports")

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '86400')  # 24 hours
        self.end_headers()
        self.wfile.write(b'{}')
    
    def do_GET(self):
        """Handle GET requests"""
        # Parse the URL path
        parsed_path = urlparse(self.path)
        path = unquote(parsed_path.path)
        
        print(f"GET request: {path}")
        
        # Add a health check endpoint
        if path == '/health':
            self._send_json_response(200, {
                "status": "ok",
                "message": "File server is running"
            })
            return
        
        # Check if the request is for a file in the exports directory
        if path.startswith('/exports/'):
            # Get the filename from the path
            filename = path.split('/')[-1]
            
            # Check if it's an allowed file or if we should allow all files
            allowed_files = ['vehicles.csv', 'market_data.csv', 'automotive_analysis.csv']
            if filename in allowed_files or True:  # Allow all files for now
                file_path = os.path.join(EXPORTS_DIR, filename)
                
                if os.path.exists(file_path):
                    # Print debug info
                    print(f"Serving file: {file_path}")
                    
                    # Set headers for file download
                    self.send_response(200)
                    self.send_header('Content-type', 'text/csv')
                    self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', '*')
                    self.end_headers()
                    
                    # Send the file content
                    with open(file_path, 'rb') as file:
                        self.wfile.write(file.read())
                    return
                else:
                    print(f"File not found: {file_path}")
                    self._send_error_response(404, 'File not found')
                    return
        
        # List all files in exports directory
        if path == '/files' or path == '/files/':
            try:
                files = [f for f in os.listdir(EXPORTS_DIR) if os.path.isfile(os.path.join(EXPORTS_DIR, f))]
                self._send_json_response(200, {
                    "files": files
                })
                return
            except Exception as e:
                print(f"Error listing files: {e}")
                self._send_error_response(500, f'Error listing files: {str(e)}')
                return
        
        # Default response for other requests
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(b"""
        <html>
        <head><title>Auto-Analyst File Server</title></head>
        <body>
            <h1>Auto-Analyst File Server</h1>
            <p>This server provides CSV files for the Auto-Analyst application.</p>
            <h2>Available Files:</h2>
            <ul>
        """)
        
        try:
            files = [f for f in os.listdir(EXPORTS_DIR) if os.path.isfile(os.path.join(EXPORTS_DIR, f))]
            for file in files:
                self.wfile.write(f'<li><a href="/exports/{file}">{file}</a></li>'.encode())
        except Exception as e:
            self.wfile.write(f'<p>Error listing files: {str(e)}</p>'.encode())
        
        self.wfile.write(b"""
            </ul>
            <h2>Upload File:</h2>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file" />
                <input type="submit" value="Upload" />
            </form>
        </body>
        </html>
        """)
    
    def do_POST(self):
        """Handle POST requests for file uploads"""
        # Parse the URL path
        parsed_path = urlparse(self.path)
        path = unquote(parsed_path.path)
        
        print(f"POST request: {path}")
        
        if path == '/upload':
            try:
                # Parse the form data
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )
                
                # Get the file field
                if 'file' in form:
                    fileitem = form['file']
                    if fileitem.filename:
                        # Save the file
                        filename = os.path.basename(fileitem.filename)
                        filepath = os.path.join(EXPORTS_DIR, filename)
                        with open(filepath, 'wb') as f:
                            f.write(fileitem.file.read())
                        
                        print(f"File uploaded: {filepath}")
                        
                        # Redirect back to the file list
                        self.send_response(303)  # 303 See Other
                        self.send_header('Location', '/')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        return
                
                # If we get here, something went wrong
                self._send_error_response(400, 'No file was uploaded')
                return
            except Exception as e:
                print(f"Error handling file upload: {e}")
                self._send_error_response(500, f'Error handling file upload: {str(e)}')
                return
        
        self._send_error_response(404, 'Endpoint not found')
    
    def _send_json_response(self, status_code, data):
        """Helper to send a JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_error_response(self, status_code, message):
        """Helper to send an error response"""
        self._send_json_response(status_code, {
            "error": message
        })


if __name__ == "__main__":
    # Check if files exist in the exports directory
    print(f"Checking exports directory: {EXPORTS_DIR}")
    if os.path.exists(EXPORTS_DIR):
        for file in ['vehicles.csv', 'market_data.csv', 'automotive_analysis.csv']:
            file_path = os.path.join(EXPORTS_DIR, file)
            if os.path.exists(file_path):
                print(f"✅ Found file: {file}")
            else:
                print(f"❌ Missing file: {file}")
    else:
        print(f"❌ Exports directory not found: {EXPORTS_DIR}")
        os.makedirs(EXPORTS_DIR, exist_ok=True)
        print(f"Created exports directory: {EXPORTS_DIR}")
    
    # Create a CORS-enabled server
    handler = CustomHandler
    
    print(f"Starting file server on port {PORT}...")
    print(f"Serving files from {EXPORTS_DIR}")
    print(f"Available endpoints:")
    print(f"  - /health")
    print(f"  - /exports/<filename> (GET)")
    print(f"  - /files (GET)")
    print(f"  - /upload (POST)")
    
    try:
        # Try to reuse the port if already in use
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            print(f"Server running at http://localhost:{PORT}")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("Server stopped by user")
                httpd.server_close()
    except OSError as e:
        print(f"Error starting server: {e}")
        print("Port may be in use. Make sure no other instances are running.")
        sys.exit(1) 