import os
import subprocess
import time
import signal
import sys
import logging
import atexit
from typing import Dict, List, Optional, Tuple

from .server_management import (
    is_port_in_use,
    ensure_port_available,
    wait_for_server,
    check_server_health,
    kill_process_on_port
)

logger = logging.getLogger("server-manager")

class ServerConfig:
    """Configuration for a server component."""
    
    def __init__(
        self,
        name: str,
        port: int,
        start_command: str,
        health_url: str,
        dependencies: List[str] = None,
        cwd: str = None,
        env: Dict[str, str] = None,
        startup_timeout: int = 30
    ):
        self.name = name
        self.port = port
        self.start_command = start_command
        self.health_url = health_url
        self.dependencies = dependencies or []
        self.cwd = cwd or os.getcwd()
        self.env = env or {}
        self.startup_timeout = startup_timeout
        self.process = None

class ServerManager:
    """Manager for server components."""
    
    def __init__(self, force_kill: bool = False):
        self.servers: Dict[str, ServerConfig] = {}
        self.force_kill = force_kill
        self.running_servers: Dict[str, subprocess.Popen] = {}
        
        # Register cleanup on exit
        atexit.register(self.shutdown_all)
        
        # Register signal handlers
        for sig in [signal.SIGINT, signal.SIGTERM]:
            signal.signal(sig, self._signal_handler)
    
    def _signal_handler(self, sig, frame):
        """Handle termination signals."""
        logger.info(f"Received signal {sig}, shutting down servers...")
        self.shutdown_all()
        sys.exit(0)
    
    def add_server(self, server_config: ServerConfig):
        """Add a server to the manager."""
        self.servers[server_config.name] = server_config
        logger.info(f"Added server configuration for {server_config.name} on port {server_config.port}")
    
    def check_port(self, name: str, force_kill: bool = None) -> bool:
        """Check if a server's port is available."""
        if name not in self.servers:
            logger.error(f"Server {name} not found in configuration")
            return False
        
        server = self.servers[name]
        use_force = self.force_kill if force_kill is None else force_kill
        return ensure_port_available(server.port, server.name, use_force)
    
    def check_dependencies(self, name: str) -> bool:
        """Check if all dependencies for a server are running."""
        if name not in self.servers:
            logger.error(f"Server {name} not found in configuration")
            return False
        
        server = self.servers[name]
        for dep in server.dependencies:
            if dep not in self.running_servers:
                logger.error(f"Dependency {dep} for {name} is not running")
                return False
            
            if not check_server_health(self.servers[dep].health_url):
                logger.error(f"Dependency {dep} for {name} is not healthy")
                return False
        
        return True
    
    def start_server(self, name: str) -> bool:
        """Start a server by name."""
        if name not in self.servers:
            logger.error(f"Server {name} not found in configuration")
            return False
        
        if name in self.running_servers and self.running_servers[name].poll() is None:
            logger.warning(f"Server {name} is already running")
            return True
        
        server = self.servers[name]
        
        # Check port
        if not self.check_port(name):
            return False
        
        # Check dependencies
        if not self.check_dependencies(name):
            logger.error(f"Cannot start {name} due to missing dependencies")
            return False
        
        # Start the server
        try:
            logger.info(f"Starting server {name} on port {server.port}")
            
            # Prepare environment
            env = os.environ.copy()
            env.update(server.env)
            
            # Start the process
            process = subprocess.Popen(
                server.start_command,
                shell=True,
                cwd=server.cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            self.running_servers[name] = process
            
            # Wait for server to start
            if not wait_for_server(server.health_url, max_retries=server.startup_timeout):
                logger.error(f"Server {name} failed to start within timeout")
                self.shutdown_server(name)
                return False
            
            logger.info(f"Server {name} started successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error starting server {name}: {str(e)}")
            return False
    
    def start_all(self) -> bool:
        """Start all servers in dependency order."""
        # Sort servers by dependencies
        remaining = list(self.servers.keys())
        started = []
        
        while remaining:
            # Find a server with all dependencies satisfied
            for name in remaining[:]:
                server = self.servers[name]
                if all(dep in started for dep in server.dependencies):
                    if self.start_server(name):
                        started.append(name)
                        remaining.remove(name)
                    else:
                        logger.error(f"Failed to start {name}, aborting startup")
                        return False
                    break
            else:
                # If we get here, we have a circular dependency or all remaining servers failed to start
                logger.error(f"Could not resolve dependencies for remaining servers: {remaining}")
                return False
        
        return True
    
    def shutdown_server(self, name: str) -> bool:
        """Shutdown a server by name."""
        if name not in self.running_servers:
            logger.warning(f"Server {name} is not running")
            return True
        
        process = self.running_servers[name]
        if process.poll() is not None:
            logger.info(f"Server {name} has already exited")
            del self.running_servers[name]
            return True
        
        logger.info(f"Shutting down server {name}")
        try:
            # Try graceful shutdown first
            process.terminate()
            
            # Wait for process to exit
            for _ in range(5):
                if process.poll() is not None:
                    logger.info(f"Server {name} shut down gracefully")
                    del self.running_servers[name]
                    return True
                time.sleep(1)
            
            # Force kill if necessary
            logger.warning(f"Server {name} did not exit gracefully, force killing")
            process.kill()
            process.wait()
            del self.running_servers[name]
            
            # Ensure port is released
            server = self.servers[name]
            if is_port_in_use(server.port):
                logger.warning(f"Port {server.port} is still in use after shutting down {name}")
                kill_process_on_port(server.port)
            
            return True
        
        except Exception as e:
            logger.error(f"Error shutting down server {name}: {str(e)}")
            return False
    
    def shutdown_all(self) -> bool:
        """Shutdown all running servers in reverse dependency order."""
        # Shutdown in reverse dependency order
        success = True
        
        # Get the dependency graph
        graph = {name: server.dependencies for name, server in self.servers.items()}
        
        # Compute shutdown order (reverse topological sort)
        visited = set()
        shutdown_order = []
        
        def visit(node):
            if node in visited:
                return
            visited.add(node)
            # Visit dependent servers first
            for srv in self.servers:
                if node in graph.get(srv, []):
                    visit(srv)
            shutdown_order.append(node)
        
        for name in self.servers:
            visit(name)
        
        # Shutdown in computed order
        for name in shutdown_order:
            if name in self.running_servers:
                if not self.shutdown_server(name):
                    success = False
        
        return success
    
    def check_all_running(self) -> bool:
        """Check if all servers are running and healthy."""
        for name, server in self.servers.items():
            if name not in self.running_servers or self.running_servers[name].poll() is not None:
                logger.error(f"Server {name} is not running")
                return False
            
            if not check_server_health(server.health_url):
                logger.error(f"Server {name} is not healthy")
                return False
        
        return True 