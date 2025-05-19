#!/bin/bash
# Stop any running instances
pkill -f "python app.py" || true
pkill -f "python file_server.py" || true

# Set environment variables
export GEMINI_API_KEY="AIzaSyBdZJNOA_w8lpyX4HUQzicoVWlN9xYINQ0"
export GOOGLE_API_KEY="AIzaSyBdZJNOA_w8lpyX4HUQzicoVWlN9xYINQ0"
export MODEL_PROVIDER="gemini"
export MODEL_NAME="gemini-1.5-pro"

# Start the servers
echo "Starting file server..."
python file_server.py &
sleep 2
echo "Starting app server..."
source venv/bin/activate
python app.py 