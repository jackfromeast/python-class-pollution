#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
LIB_DIR="$SCRIPT_DIR/repo"

# Clone GCFT if not already present
if [ ! -d "$LIB_DIR" ]; then
    echo "[+] Cloning GCFT..."
    git clone --depth 1 https://github.com/LagoLunatic/GCFT.git "$LIB_DIR"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "[+] Creating virtual environment at: $VENV_PATH"
    python3 -m venv "$VENV_PATH"
fi

source "$VENV_PATH/bin/activate"

# Run the PoC with GCFT on PYTHONPATH (Qt is mocked in poc.py)
echo "[+] Running PoC..."
PYTHONPATH="$LIB_DIR:$PYTHONPATH" python "$SCRIPT_DIR/poc.py"
