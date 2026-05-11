#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
LIB_DIR="$SCRIPT_DIR/repo"

# Clone minGPT if not already present
if [ ! -d "$LIB_DIR" ]; then
    echo "[+] Cloning minGPT..."
    git clone --depth 1 https://github.com/karpathy/minGPT.git "$LIB_DIR"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "[+] Creating virtual environment at: $VENV_PATH"
    python3 -m venv "$VENV_PATH"
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Install minimal deps for the utils module
pip install torch numpy -q 2>/dev/null || pip install numpy -q

# Run the PoC with minGPT on PYTHONPATH
echo "[+] Running PoC..."
PYTHONPATH="$LIB_DIR:$PYTHONPATH" python "$SCRIPT_DIR/poc.py"
