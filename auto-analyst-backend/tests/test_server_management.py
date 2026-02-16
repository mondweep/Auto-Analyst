import unittest
import os
import socket
import subprocess
import time
import threading
import sys
from unittest import mock

# Add parent directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.server_management import (
    is_port_in_use,
    get_process_on_port,
    kill_process_on_port,
    ensure_port_available,
    check_server_health,
    wait_for_server
)

class SimpleHTTPServer:
    """A simple HTTP server for testing."""
    
    def __init__(self, port):
        self.port = port
        self.server = None
        self.thread = None
        self.running = False
    
    def start(self):
        """Start the server in a separate thread."""
        self.running = True
        self.thread = threading.Thread(target=self._run_server)
        self.thread.daemon = True
        self.thread.start()
        # Wait for server to start
        time.sleep(0.5)
        return self.running
    
    def _run_server(self):
        """Run a simple HTTP server."""
        import http.server
        import socketserver
        
        handler = http.server.SimpleHTTPRequestHandler
        
        try:
            with socketserver.TCPServer(("", self.port), handler) as httpd:
                self.server = httpd
                httpd.serve_forever()
        except OSError:
            self.running = False
    
    def stop(self):
        """Stop the server."""
        if self.server:
            self.server.shutdown()
            self.server = None
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
            self.thread = None

class TestPortManagement(unittest.TestCase):
    """Test port management utilities."""
    
    def setUp(self):
        """Set up test environment."""
        # Use a port that's likely to be free
        self.test_port = 12345
        self.server = SimpleHTTPServer(self.test_port)
    
    def tearDown(self):
        """Clean up test environment."""
        self.server.stop()
        # Make sure port is released
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('localhost', self.test_port))
        except OSError:
            # Try to force kill any process on port
            subprocess.call(f"kill -9 $(lsof -ti:{self.test_port}) 2>/dev/null || true", shell=True)
    
    def test_is_port_in_use_free(self):
        """Test is_port_in_use with a free port."""
        # Ensure port is free
        self.tearDown()
        self.assertFalse(is_port_in_use(self.test_port))
    
    def test_is_port_in_use_occupied(self):
        """Test is_port_in_use with an occupied port."""
        # Start server on port
        if self.server.start():
            self.assertTrue(is_port_in_use(self.test_port))
        else:
            self.skipTest("Could not start test server")
    
    def test_get_process_on_port_free(self):
        """Test get_process_on_port with a free port."""
        # Ensure port is free
        self.tearDown()
        self.assertIsNone(get_process_on_port(self.test_port))
    
    def test_get_process_on_port_occupied(self):
        """Test get_process_on_port with an occupied port."""
        # This test is tricky to do reliably across platforms
        # because process details are OS-dependent
        # Mock the function call instead
        with mock.patch('subprocess.check_output') as mock_check_output:
            mock_check_output.return_value = b"12345"
            pid = get_process_on_port(self.test_port)
            self.assertEqual(pid, 12345)
    
    def test_ensure_port_available_free(self):
        """Test ensure_port_available with a free port."""
        # Ensure port is free
        self.tearDown()
        self.assertTrue(ensure_port_available(self.test_port, "test_service"))
    
    def test_ensure_port_available_occupied_no_force(self):
        """Test ensure_port_available with an occupied port without force kill."""
        # Start server on port
        if self.server.start():
            self.assertFalse(ensure_port_available(self.test_port, "test_service", force_kill=False))
        else:
            self.skipTest("Could not start test server")
    
    @unittest.skipIf(os.name == 'nt', "Skipping on Windows")
    def test_ensure_port_available_occupied_force(self):
        """Test ensure_port_available with an occupied port with force kill."""
        # This test requires permissions to kill processes and may not work
        # reliably on all systems, so we'll mock it
        with mock.patch('utils.server_management.kill_process_on_port') as mock_kill:
            mock_kill.return_value = True
            with mock.patch('utils.server_management.is_port_in_use') as mock_is_port_in_use:
                # First call returns True (port in use), second call returns False (port freed)
                mock_is_port_in_use.side_effect = [True, False]
                with mock.patch('utils.server_management.get_process_on_port') as mock_get_pid:
                    mock_get_pid.return_value = 12345
                    self.assertTrue(ensure_port_available(self.test_port, "test_service", force_kill=True))
                    mock_kill.assert_called_once_with(self.test_port)

class TestHealthCheck(unittest.TestCase):
    """Test health check utilities."""
    
    def test_check_server_health_success(self):
        """Test check_server_health with a successful response."""
        with mock.patch('requests.get') as mock_get:
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            self.assertTrue(check_server_health("http://localhost/health"))
    
    def test_check_server_health_failure(self):
        """Test check_server_health with a failed response."""
        with mock.patch('requests.get') as mock_get:
            mock_response = mock.MagicMock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response
            self.assertFalse(check_server_health("http://localhost/health"))
    
    def test_check_server_health_error(self):
        """Test check_server_health with an error response."""
        with mock.patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection error")
            self.assertFalse(check_server_health("http://localhost/health"))
    
    def test_wait_for_server_success(self):
        """Test wait_for_server with a successful response."""
        with mock.patch('utils.server_management.check_server_health') as mock_check:
            # Return False on first call, True on second
            mock_check.side_effect = [False, True]
            self.assertTrue(wait_for_server("http://localhost/health", max_retries=2, retry_interval=0.1))
            self.assertEqual(mock_check.call_count, 2)
    
    def test_wait_for_server_timeout(self):
        """Test wait_for_server with timeout."""
        with mock.patch('utils.server_management.check_server_health') as mock_check:
            # Always return False
            mock_check.return_value = False
            self.assertFalse(wait_for_server("http://localhost/health", max_retries=2, retry_interval=0.1))
            self.assertEqual(mock_check.call_count, 2)

if __name__ == '__main__':
    unittest.main() 