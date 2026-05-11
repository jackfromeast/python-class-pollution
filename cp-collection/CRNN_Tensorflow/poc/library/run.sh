#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
LIB_DIR="$SCRIPT_DIR/repo"

# Clone CRNN_Tensorflow if not already present
if [ ! -d "$LIB_DIR" ]; then
    echo "[+] Cloning CRNN_Tensorflow..."
    git clone --depth 1 https://github.com/MaybeShewill-CV/CRNN_Tensorflow.git "$LIB_DIR"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "[+] Creating virtual environment at: $VENV_PATH"
    python3 -m venv "$VENV_PATH"
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Install minimal deps
pip install pyyaml -q

# Run the PoC with repo on PYTHONPATH
echo "[+] Running PoC..."
PYTHONPATH="$LIB_DIR:$PYTHONPATH" python "$SCRIPT_DIR/poc.py"
