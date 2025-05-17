#!/bin/bash
# Start all Auto-Analyst backend services

echo "Starting Auto-Analyst Backend Services..."

# Kill any existing processes (optional, uncomment if needed)
# echo "Stopping any existing Python services..."
# pkill -f "file_server.py"
# pkill -f "automotive_server.py"
# pkill -f "simple_app.py"
# sleep 2

# Start the file server
echo "Starting File Server on port 8001..."
python file_server.py > logs/file_server.log 2>&1 &
FILE_SERVER_PID=$!
echo "File Server started with PID: $FILE_SERVER_PID"

# Wait a bit to ensure port is available
sleep 1

# Start the automotive server
echo "Starting Automotive API Server on port 8003..."
python automotive_server.py > logs/automotive_server.log 2>&1 &
AUTOMOTIVE_SERVER_PID=$!
echo "Automotive API Server started with PID: $AUTOMOTIVE_SERVER_PID"

# Wait a bit to ensure services are up
sleep 2

# Verify services are running
echo "Verifying services..."
curl -s http://localhost:8001/health
echo ""
curl -s http://localhost:8003/health
echo ""

echo "All services started!"
echo "- File Server: http://localhost:8001"
echo "- Automotive API Server: http://localhost:8003"
echo ""
echo "To access the frontend, please make sure it's running at http://localhost:3000"
echo "You can access the automotive demo at http://localhost:3000/automotive"
echo ""
echo "Log files are in the logs/ directory if you need to troubleshoot."

# Create a function to handle server shutdown
function shutdown() {
    echo "Shutting down servers..."
    kill $FILE_SERVER_PID $AUTOMOTIVE_SERVER_PID
    exit 0
}

# Register the shutdown function for when this script is interrupted
trap shutdown SIGINT

# Keep script running (optional)
echo "Press Ctrl+C to stop all servers..."
tail -f logs/file_server.log 