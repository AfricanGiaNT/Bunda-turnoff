#!/bin/bash
# Shell script to start the application on Render

# Print environment information
echo "Current directory: $(pwd)"
echo "Python locations:"
which python || echo "python not found"
which python3 || echo "python3 not found"
echo "PATH: $PATH"

# Add potential Python paths
export PATH="/opt/render/project/python/bin:$PATH"
export PATH="/opt/python/latest/bin:$PATH"

# Try to find Python
PYTHON_CMD=""
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "ERROR: Python not found in PATH"
    exit 1
fi

# Print Python version
echo "Using Python: $($PYTHON_CMD --version)"

# Run the application
echo "Starting application..."
exec $PYTHON_CMD app.py
