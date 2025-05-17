#!/usr/bin/env python
import os
import http.server
import socketserver
import json
import cgi
from urllib.parse import urlparse, unquote
import sys
import csv

PORT = 8001
EXPORTS_DIR = os.path.join(os.path.dirname(__file__), "exports")

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Session-ID')
        self.send_header('Access-Control-Max-Age', '86400')  # 24 hours
        self.end_headers()
        self.wfile.write(b'{}')
    
    def do_GET(self):
        """Handle GET requests"""
        # Parse the URL path
        parsed_path = urlparse(self.path)
        path = unquote(parsed_path.path)
        
        print(f"GET request: {path}")
        
        # Add special routes first to make sure they're handled correctly
        routes = {
            '/health': self.handle_health,
            '/api/health': self.handle_health,
            '/api/default-dataset': self.handle_default_dataset,
            '/api/': self.handle_api_root,
            '/files': self.handle_list_files,
            '/files/': self.handle_list_files,
        }
        
        # Check if the path matches any of our special routes
        if path in routes:
            routes[path]()
            return
            
        # Check for exports folder request
        if path.startswith('/exports/'):
            self.handle_exports_file(path)
            return
        
        # Default to the root page with file listing
        self.handle_root()
    
    def handle_health(self):
        """Handler for health check endpoint"""
        self._send_json_response(200, {
            "status": "ok",
            "message": "File server is running"
        })
    
    def handle_api_root(self):
        """Handler for API root endpoint"""
        self._send_json_response(200, {
            "status": "ok",
            "endpoints": [
                "/api/health",
                "/api/default-dataset",
                "/exports/<filename>"
            ]
        })
    
    def handle_default_dataset(self):
        """Handler for default dataset endpoint"""
        # Set the default file
        default_file = os.path.join(EXPORTS_DIR, 'vehicles.csv')
        
        if os.path.exists(default_file):
            try:
                print(f"Serving default dataset: {default_file}")
                
                # Read the CSV file
                with open(default_file, 'r') as file:
                    csv_reader = csv.reader(file)
                    headers = next(csv_reader)  # Get the headers
                    
                    # Get a sample of rows (up to 10)
                    rows = []
                    for i, row in enumerate(csv_reader):
                        if i < 10:  # Limit to 10 rows
                            rows.append(row)
                        else:
                            break
                
                # Create the response data structure
                response_data = {
                    "headers": headers,
                    "rows": rows,
                    "name": "Automotive Data",
                    "description": "Vehicle inventory dataset containing information about automotive vehicles, pricing, and sales data"
                }
                
                self._send_json_response(200, response_data)
                return
            except Exception as e:
                print(f"Error reading default dataset: {e}")
                self._send_error_response(500, f'Error reading default dataset: {str(e)}')
                return
        else:
            print(f"Default dataset file not found: {default_file}")
            # If the original file doesn't exist, create a sample default dataset
            try:
                fallback_data = {
                    "headers": ["id", "make", "model", "year", "color", "price", "mileage", "condition"],
                    "rows": [
                        ["1", "Toyota", "Camry", "2021", "Black", "28500", "32000", "Excellent"],
                        ["2", "Honda", "Civic", "2022", "White", "24700", "18000", "Good"],
                        ["3", "Ford", "F-150", "2020", "Blue", "38900", "45000", "Good"],
                        ["4", "BMW", "3 Series", "2021", "Black", "43200", "22000", "Excellent"],
                        ["5", "Audi", "Q5", "2022", "Gray", "47800", "18500", "Excellent"]
                    ],
                    "name": "Automotive Data",
                    "description": "Vehicle inventory dataset containing information about automotive vehicles, pricing, and sales data"
                }
                self._send_json_response(200, fallback_data)
                return
            except Exception as e:
                print(f"Error creating fallback dataset: {e}")
                self._send_error_response(500, f'Error creating fallback dataset: {str(e)}')
                return
    
    def handle_exports_file(self, path):
        """Handler for file downloads from exports directory"""
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
    
    def handle_list_files(self):
        """Handler for listing files in exports directory"""
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
    
    def handle_root(self):
        """Handler for root page"""
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
        files = [f for f in os.listdir(EXPORTS_DIR) if os.path.isfile(os.path.join(EXPORTS_DIR, f))]
        for file in files:
            print(f"✅ Found file: {file}")
    else:
        print(f"❌ Exports directory not found, creating: {EXPORTS_DIR}")
        os.makedirs(EXPORTS_DIR, exist_ok=True)
    
    # Start the server
    try:
        print(f"Starting file server on port {PORT}...")
        print(f"Serving files from {EXPORTS_DIR}")
        print("Available endpoints:")
        print("  - /health")
        print("  - /exports/<filename> (GET)")
        print("  - /files (GET)")
        print("  - /upload (POST)")
        print("  - /api/default-dataset")
        
        # Ensure the server can be reused if we restart it
        handler = CustomHandler
        
        # Set allow_reuse_address to avoid "Address already in use" error
        class ReusableTCPServer(socketserver.TCPServer):
            allow_reuse_address = True
        
        with ReusableTCPServer(("", PORT), handler) as httpd:
            print(f"Server running at http://localhost:{PORT}")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print("Error starting server: [Errno 48] Address already in use")
            print("Port may be in use. Make sure no other instances are running.")
            sys.exit(1)
        else:
            print(f"Error starting server: {e}")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 