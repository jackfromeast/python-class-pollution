#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
LIB_DIR="$VENV_PATH/lib/pystringattr"

# Create virtual environment if it does not exist
if [ ! -d "$VENV_PATH" ]; then
    echo "[+] Creating virtual environment at: $VENV_PATH"
    python3 -m venv "$VENV_PATH"
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Clone pystringattr (no setup.py, must be added to path)
if [ ! -d "$LIB_DIR" ]; then
    echo "[+] Cloning pystringattr..."
    git clone -q https://github.com/dansimau/pystringattr.git "$LIB_DIR"
fi

# Run the PoC
echo "[+] Running PoC..."
PYTHONPATH="$(dirname $LIB_DIR):$PYTHONPATH" python "$SCRIPT_DIR/poc.py"
