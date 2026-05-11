#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
LIB_DIR="$SCRIPT_DIR/repo"

# Clone tensorpack if not already present
if [ ! -d "$LIB_DIR" ]; then
    echo "[+] Cloning tensorpack (sparse)..."
    git clone --depth 1 --filter=blob:none --sparse \
        https://github.com/tensorpack/tensorpack.git "$LIB_DIR"
    cd "$LIB_DIR" && git sparse-checkout set examples/FasterRCNN/config.py
    cd "$SCRIPT_DIR"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "[+] Creating virtual environment at: $VENV_PATH"
    python3 -m venv "$VENV_PATH"
fi

source "$VENV_PATH/bin/activate"

# Run the PoC
echo "[+] Running PoC..."
PYTHONPATH="$LIB_DIR:$PYTHONPATH" python "$SCRIPT_DIR/poc.py"
