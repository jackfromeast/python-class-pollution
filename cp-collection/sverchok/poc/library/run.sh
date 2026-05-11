#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
LIB_DIR="$SCRIPT_DIR/repo"

# Clone sverchok if not already present
if [ ! -d "$LIB_DIR" ]; then
    echo "[+] Cloning sverchok (sparse)..."
    git clone --depth 1 --filter=blob:none --sparse \
        https://github.com/nortikin/sverchok.git "$LIB_DIR"
    cd "$LIB_DIR" && git sparse-checkout set nodes/object_nodes/getsetprop_mk2.py nodes/__init__.py nodes/object_nodes/__init__.py
    # Ensure __init__.py files exist
    touch "$LIB_DIR/nodes/__init__.py" "$LIB_DIR/nodes/object_nodes/__init__.py"
    cd "$SCRIPT_DIR"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "[+] Creating virtual environment at: $VENV_PATH"
    python3 -m venv "$VENV_PATH"
fi

source "$VENV_PATH/bin/activate"

# Run the PoC with repo on PYTHONPATH (bpy is mocked in poc.py)
echo "[+] Running PoC..."
PYTHONPATH="$LIB_DIR:$PYTHONPATH" python "$SCRIPT_DIR/poc.py"
