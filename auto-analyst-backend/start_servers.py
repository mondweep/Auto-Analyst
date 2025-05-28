#!/usr/bin/env python3
import os
import sys
import logging
import argparse
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('server.log')
    ]
)

logger = logging.getLogger("start-servers")

# Add the current directory to the path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.server_manager import ServerManager, ServerConfig

def parse_args():
    parser = argparse.ArgumentParser(description='Start Auto-Analyst backend servers')
    parser.add_argument('--force-kill', action='store_true', help='Force kill any processes using required ports')
    parser.add_argument('--attribute-server-only', action='store_true', help='Start only the attribute server')
    parser.add_argument('--proxy-only', action='store_true', help='Start only the proxy server (requires attribute server)')
    parser.add_argument('--main-app-only', action='store_true', help='Start only the main application server')
    parser.add_argument('--local-dir', action='store_true', help='Use local directory for server paths')
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Determine the backend directory
    if args.local_dir:
        backend_dir = os.path.dirname(os.path.abspath(__file__))
    else:
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'auto-analyst-backend'))
    
    logger.info(f"Using backend directory: {backend_dir}")
    
    # Create server manager
    manager = ServerManager(force_kill=args.force_kill)
    
    # Define our servers
    attribute_server = ServerConfig(
        name="attribute_server",
        port=8002,
        start_command="python3 ./standalone_attribute_server.py",
        health_url="http://localhost:8002/health",
        cwd=backend_dir,
        env={},
        dependencies=[]
    )
    
    proxy_server = ServerConfig(
        name="proxy_server",
        port=8080,
        start_command="python3 ./attribute_proxy.py",
        health_url="http://localhost:8080/health",
        cwd=backend_dir,
        env={},
        dependencies=["attribute_server"]
    )
    
    main_app = ServerConfig(
        name="main_app",
        port=8000,
        start_command="uvicorn app:app --host 0.0.0.0 --port 8000",
        health_url="http://localhost:8000/health",
        cwd=backend_dir,
        env={
            "DATABASE_URL": "sqlite:///./auto_analyst.db",
            "FRONTEND_URL": "http://localhost:3000"
        },
        dependencies=["attribute_server"]
    )
    
    # Add servers based on command line arguments
    if args.attribute_server_only:
        manager.add_server(attribute_server)
    elif args.proxy_only:
        manager.add_server(attribute_server)
        manager.add_server(proxy_server)
    elif args.main_app_only:
        manager.add_server(attribute_server)
        manager.add_server(main_app)
    else:
        # Start all servers
        manager.add_server(attribute_server)
        manager.add_server(proxy_server)
        manager.add_server(main_app)
    
    # Start the servers
    if manager.start_all():
        logger.info("All servers started successfully")
        
        # Keep the script running to maintain the server processes
        try:
            while manager.check_all_running():
                import time
                time.sleep(10)
        except KeyboardInterrupt:
            logger.info("Shutting down servers...")
            manager.shutdown_all()
    else:
        logger.error("Failed to start all servers")
        manager.shutdown_all()
        sys.exit(1)

if __name__ == "__main__":
    main() 