#!/bin/bash

# Check if virtual environment directory exists
if [ -d "venv" ]; then
    # Activate the virtual environment
    source venv/bin/activate
else
    echo "Error: venv directory not found."
    exit 1
fi

# Configure Flask environment variables
export FLASK_APP=server.py
export FLASK_DEBUG=1

# Launch the Flask application
flask run