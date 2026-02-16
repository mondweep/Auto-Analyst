#!/usr/bin/env python
import os
import http.server
import socketserver
import json
import cgi
from urllib.parse import urlparse, unquote
import sys
import csv
import re

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
            '/preview': self.handle_preview_file,
            '/api/preview': self.handle_preview_file,
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
                "/api/preview",
                "/exports/<filename>"
            ]
        })
    
    def handle_preview_file(self):
        """Handler for file preview endpoint"""
        # Always send CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Session-ID')
        self.end_headers()
        
        # Default to the vehicles.csv file if no specific file is requested
        preview_file = os.path.join(EXPORTS_DIR, 'vehicles.csv')
        
        try:
            # Read the CSV file
            with open(preview_file, 'r') as file:
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
            
            self.wfile.write(json.dumps(response_data).encode())
        except Exception as e:
            print(f"Error during file preview: {e}")
            fallback_data = {
                "headers": ["id", "make", "model", "year", "color", "price", "mileage", "condition"],
                "rows": [
                    ["1", "Toyota", "Camry", "2021", "Black", "28500", "32000", "Excellent"],
                    ["2", "Honda", "Civic", "2022", "White", "24700", "18000", "Good"],
                    ["3", "Ford", "F-150", "2020", "Blue", "38900", "45000", "Good"],
                    ["4", "BMW", "3 Series", "2021", "Black", "43200", "22000", "Excellent"],
                    ["5", "Audi", "Q5", "2022", "Gray", "47800", "18500", "Excellent"]
                ],
                "name": "Automotive Data (Fallback)",
                "description": "Sample vehicle inventory dataset (fallback data)"
            }
            self.wfile.write(json.dumps(fallback_data).encode())
    
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
        
        # Add API documentation
        self.wfile.write(b"""
            </ul>
            <h2>API Endpoints:</h2>
            <ul>
                <li><a href="/health">/health</a> - Check server health</li>
                <li><a href="/api/default-dataset">/api/default-dataset</a> - Get default dataset</li>
                <li><a href="/api/preview">/api/preview</a> - Preview CSV file</li>
                <li><a href="/files">/files</a> - List available files</li>
            </ul>
        </body>
        </html>
        """)
    
    def do_POST(self):
        """Handle POST requests"""
        # Parse the URL path
        parsed_path = urlparse(self.path)
        path = unquote(parsed_path.path)
        
        print(f"POST request: {path}")
        
        # Route to appropriate handler based on path
        if path == '/api/preview-csv' or path == '/api/preview':
            self.handle_preview_csv()
        elif path == '/upload' or path == '/api/upload':
            self.handle_upload()
        else:
            self._send_error_response(404, 'Endpoint not found')
    
    def handle_preview_csv(self):
        """Handle preview of CSV file content"""
        try:
            # Return default dataset preview for now
            self.handle_preview_file()
        except Exception as e:
            print(f"Error in preview CSV: {e}")
            self._send_error_response(500, f'Error in preview: {str(e)}')
    
    def handle_upload(self):
        """Handle file upload"""
        try:
            # Parse the multipart form data
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            
            # Check if the file field is in the form
            if 'file' not in form:
                self._send_error_response(400, 'No file in form data')
                return
            
            fileitem = form['file']
            
            # Check if the field contains a file
            if not fileitem.file:
                self._send_error_response(400, 'Field is not a file')
                return
            
            # Validate file type (allow only CSV files)
            filename = fileitem.filename
            if not filename.lower().endswith('.csv'):
                self._send_error_response(400, 'Only CSV files are allowed')
                return
            
            # Read file content
            file_content = fileitem.file.read()
            
            # Save the file
            filepath = os.path.join(EXPORTS_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(file_content)
            
            # Parse the CSV data for the response
            try:
                # Decode the file content
                csv_content = file_content.decode('utf-8', errors='replace')
                csv_lines = csv_content.split('\n')
                
                # Extract headers and data
                headers = []
                data = []
                
                if csv_lines and len(csv_lines) > 0:
                    # Process the header row
                    first_line = csv_lines[0].strip()
                    headers = [h.strip() for h in first_line.split(',')]
                    
                    # Process data rows (up to 100 for preview)
                    max_rows = min(100, len(csv_lines) - 1)
                    for i in range(1, max_rows + 1):
                        if i < len(csv_lines) and csv_lines[i].strip():
                            # Split by comma but handle quoted values correctly
                            row_values = []
                            in_quotes = False
                            current_value = ""
                            
                            for char in csv_lines[i]:
                                if char == '"':
                                    in_quotes = not in_quotes
                                elif char == ',' and not in_quotes:
                                    row_values.append(current_value.strip())
                                    current_value = ""
                                else:
                                    current_value += char
                            
                            # Add the last value
                            row_values.append(current_value.strip())
                            
                            # Create dictionary of column name -> value
                            row_data = {}
                            for j, header in enumerate(headers):
                                if j < len(row_values):
                                    # Remove quotes if present
                                    value = row_values[j]
                                    if value.startswith('"') and value.endswith('"'):
                                        value = value[1:-1]
                                    row_data[header] = value
                                else:
                                    row_data[header] = ""
                            
                            data.append(row_data)
                
                # Calculate column types
                column_types = {}
                for header in headers:
                    # Check if numeric
                    numeric_count = 0
                    date_count = 0
                    sample_value = ""
                    
                    for row in data[:20]:  # Check first 20 rows for type detection
                        if header in row and row[header]:
                            sample_value = row[header]
                            # Check if it looks like a number
                            try:
                                float(row[header].replace(',', ''))
                                numeric_count += 1
                            except ValueError:
                                # Check if it looks like a date
                                if re.match(r'\d{1,4}[-/]\d{1,2}[-/]\d{1,4}', row[header]):
                                    date_count += 1
                    
                    # Determine type based on majority of samples
                    if numeric_count > len(data[:20]) / 2:
                        column_types[header] = "numeric"
                    elif date_count > len(data[:20]) / 2:
                        column_types[header] = "date"
                    else:
                        column_types[header] = "string"
                
                # Respond with success and include parsed data
                self._send_json_response(200, {
                    'status': 'success',
                    'message': f'File {filename} uploaded successfully',
                    'file_path': filepath,
                    'headers': headers,
                    'column_types': column_types,
                    'data': data,
                    'total_rows': len(csv_lines) - 1 if len(csv_lines) > 1 else 0,
                    'preview_rows': len(data)
                })
            except Exception as e:
                print(f"Error parsing CSV: {e}")
                # Still return success since we saved the file, but include error info
                self._send_json_response(200, {
                    'status': 'partial_success',
                    'message': f'File {filename} uploaded but could not be parsed: {str(e)}',
                    'file_path': filepath,
                    'headers': [],
                    'data': [],
                    'error': str(e)
                })
        except Exception as e:
            print(f"Error in upload: {e}")
            self._send_error_response(500, f'Error in upload: {str(e)}')
    
    def _send_json_response(self, status_code, data):
        """Helper to send JSON response with proper headers"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Session-ID')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_error_response(self, status_code, message):
        """Helper to send error response with proper headers"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Session-ID')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'error',
            'message': message
        }).encode())

# Check if exports directory exists
if not os.path.exists(EXPORTS_DIR):
    os.makedirs(EXPORTS_DIR)
    print(f"Created exports directory: {EXPORTS_DIR}")

# Check if required files exist in exports directory
print(f"Checking exports directory: {EXPORTS_DIR}")
required_files = ['vehicles.csv', 'market_data.csv', 'automotive_analysis.csv']
for file in required_files:
    file_path = os.path.join(EXPORTS_DIR, file)
    if os.path.exists(file_path):
        print(f"✅ Found file: {file}")
    else:
        print(f"❌ Missing file: {file} - will be created if needed")

# Create a simple TCP server
try:
    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True
    
    handler = CustomHandler
    
    print(f"Starting file server on port {PORT}...")
    print(f"Serving files from {EXPORTS_DIR}")
    print("Available endpoints:")
    print("  - /health")
    print("  - /exports/<filename> (GET)")
    print("  - /files (GET)")
    print("  - /upload (POST)")
    print("  - /api/preview (GET/POST)")
    
    with ReusableTCPServer(("", PORT), handler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        httpd.serve_forever()
except OSError as e:
    if e.errno == 48:  # Address already in use
        print(f"Error starting server: {e}")
        print("Port may be in use. Make sure no other instances are running.")
    else:
        print(f"Error starting server: {e}")
except KeyboardInterrupt:
    print("Server stopped by user.")
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc() 