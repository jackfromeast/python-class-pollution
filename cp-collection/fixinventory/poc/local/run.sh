#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "[+] Creating virtual environment at: $VENV_PATH"
    python3 -m venv "$VENV_PATH"
fi

source "$VENV_PATH/bin/activate"

if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "[+] Installing dependencies..."
    pip install -r "$REQUIREMENTS_FILE" -q
fi

echo "[+] Running PoC..."
python "$SCRIPT_DIR/poc.py"
