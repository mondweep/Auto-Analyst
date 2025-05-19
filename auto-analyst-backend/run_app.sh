#!/bin/bash
# Kill any existing app.py or file_server.py processes
pkill -f "python app.py" || true
pkill -f "python file_server.py" || true

# Export environment variables
export MODEL_PROVIDER=gemini
export MODEL_NAME=gemini-1.5-pro
export TEMPERATURE=0.7
export MAX_TOKENS=6000
export GEMINI_API_KEY=AIzaSyBdZJNOA_w8lpyX4HUQzicoVWlN9xYINQ0
export GOOGLE_API_KEY=AIzaSyBdZJNOA_w8lpyX4HUQzicoVWlN9xYINQ0
export DATABASE_URL=sqlite:///auto_analyst.db
export ENV=development

# First start the file server
echo "Starting file server..."
python file_server.py &
sleep 2

# Then start the main app with the virtual environment
echo "Starting app server..."
source venv/bin/activate
python app.py 