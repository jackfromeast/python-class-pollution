#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
LIB_DIR="$SCRIPT_DIR/repo"

# Clone ragflow if not already present
if [ ! -d "$LIB_DIR" ]; then
    echo "[+] Cloning ragflow (sparse)..."
    git clone --depth 1 --filter=blob:none --sparse \
        https://github.com/infiniflow/ragflow.git "$LIB_DIR"
    cd "$LIB_DIR" && git sparse-checkout set agent/component/base.py agent/__init__.py agent/component/__init__.py
    # Ensure __init__.py files exist
    touch "$LIB_DIR/agent/__init__.py" "$LIB_DIR/agent/component/__init__.py"
    cd "$SCRIPT_DIR"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "[+] Creating virtual environment at: $VENV_PATH"
    python3 -m venv "$VENV_PATH"
fi

source "$VENV_PATH/bin/activate"

# Install deps needed for import
pip install pandas -q

# Run the PoC with repo on PYTHONPATH
echo "[+] Running PoC..."
PYTHONPATH="$LIB_DIR:$PYTHONPATH" python "$SCRIPT_DIR/poc.py"
