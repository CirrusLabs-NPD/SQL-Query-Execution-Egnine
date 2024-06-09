#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Create a virtual environment
python -m venv myapp

# Activate the virtual environment
source myapp/bin/activate

# Run the Flask application
flask run --host=0.0.0.0 --port=8000
