#!/bin/bash
set -e

# Navigate to the project root directory (one level up from scripts directory)
cd "$(dirname "$0")/.."

# Check if a virtual environment exists; if not, create one and install pytest
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv .venv
    echo "Installing pytest..."
    .venv/bin/pip install pytest
fi

# Ensure that the src folder is in PYTHONPATH so tests can import the modules
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"

echo "Running tests..."
# Use python from the virtual environment
.venv/bin/python -m pytest src/tests/
