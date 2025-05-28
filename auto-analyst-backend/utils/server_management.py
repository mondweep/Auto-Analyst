import os
import socket
import subprocess
import time
import logging
from typing import List, Optional, Tuple

logger = logging.getLogger("server-management")

def is_port_in_use(port: int) -> bool:
    """Check if a port is already in use.
    
    Args:
        port: The port number to check
        
    Returns:
        True if the port is in use, False otherwise
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def get_process_on_port(port: int) -> Optional[int]:
    """Get the process ID using a specific port.
    
    Args:
        port: The port number to check
        
    Returns:
        The process ID if found, None otherwise
    """
    try:
        if os.name == 'nt':  # Windows
            output = subprocess.check_output(f'netstat -ano | findstr :{port}', shell=True).decode()
            if output:
                lines = output.strip().split('\n')
                for line in lines:
                    if f':{port}' in line and 'LISTENING' in line:
                        pid = line.split()[-1]
                        return int(pid)
        else:  # Unix/Linux/MacOS
            output = subprocess.check_output(f'lsof -i :{port} -t', shell=True).decode()
            if output:
                return int(output.strip())
    except (subprocess.SubprocessError, ValueError):
        pass
    return None

def kill_process_on_port(port: int) -> bool:
    """Kill the process using a specific port.
    
    Args:
        port: The port number of the process to kill
        
    Returns:
        True if the process was successfully killed, False otherwise
    """
    pid = get_process_on_port(port)
    if pid:
        try:
            if os.name == 'nt':  # Windows
                subprocess.check_call(f'taskkill /F /PID {pid}', shell=True)
            else:  # Unix/Linux/MacOS
                subprocess.check_call(f'kill -9 {pid}', shell=True)
            
            # Wait a moment for the port to be released
            time.sleep(0.5)
            return not is_port_in_use(port)
        except subprocess.SubprocessError:
            logger.error(f"Failed to kill process {pid} on port {port}")
    return False

def ensure_port_available(port: int, service_name: str, force_kill: bool = False) -> bool:
    """Ensure a port is available for use, optionally killing any existing process.
    
    Args:
        port: The port number to check
        service_name: The name of the service (for logging)
        force_kill: Whether to forcibly kill any process using the port
        
    Returns:
        True if the port is available, False otherwise
    """
    if is_port_in_use(port):
        pid = get_process_on_port(port)
        if pid:
            logger.warning(f"Port {port} is in use by process {pid}")
            if force_kill:
                logger.info(f"Attempting to kill process {pid} on port {port}")
                if kill_process_on_port(port):
                    logger.info(f"Successfully killed process on port {port}")
                    return True
                else:
                    logger.error(f"Failed to kill process on port {port}")
                    return False
            else:
                logger.error(f"Port {port} is in use. {service_name} cannot start")
                return False
        else:
            logger.warning(f"Port {port} is in use but no process was found")
            return False
    return True

def check_server_health(url: str, timeout: int = 5) -> bool:
    """Check if a server is healthy by pinging its health endpoint.
    
    Args:
        url: The URL to check, usually ending with /health
        timeout: Timeout in seconds
        
    Returns:
        True if the server is healthy, False otherwise
    """
    try:
        import requests
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Health check failed for {url}: {str(e)}")
        return False

def wait_for_server(url: str, max_retries: int = 10, retry_interval: int = 1) -> bool:
    """Wait for a server to become available.
    
    Args:
        url: The URL to check
        max_retries: Maximum number of retries
        retry_interval: Time between retries in seconds
        
    Returns:
        True if the server became available, False otherwise
    """
    for i in range(max_retries):
        if check_server_health(url):
            return True
        time.sleep(retry_interval)
    return False 