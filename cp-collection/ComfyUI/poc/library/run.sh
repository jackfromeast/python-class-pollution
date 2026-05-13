#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
LIB_DIR="$SCRIPT_DIR/repo"

# Clone ComfyUI if not already present
if [ ! -d "$LIB_DIR" ]; then
    echo "[+] Cloning ComfyUI..."
    git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git "$LIB_DIR"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "[+] Creating virtual environment at: $VENV_PATH"
    python3 -m venv "$VENV_PATH"
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Install ComfyUI's own dependencies
if [ -f "$LIB_DIR/requirements.txt" ]; then
    echo "[+] Installing ComfyUI dependencies..."
    pip install -r "$LIB_DIR/requirements.txt" -q
fi

# Run the PoC with repo on PYTHONPATH
echo "[+] Running PoC..."
PYTHONPATH="$LIB_DIR:$PYTHONPATH" python "$SCRIPT_DIR/poc.py"
