#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
LIB_DIR="$SCRIPT_DIR/repo"

# Clone tournesol if not already present
if [ ! -d "$LIB_DIR" ]; then
    echo "[+] Cloning tournesol (sparse)..."
    git clone --depth 1 --filter=blob:none --sparse \
        https://github.com/tournesol-app/tournesol.git "$LIB_DIR"
    cd "$LIB_DIR" && git sparse-checkout set solidago/src
    cd "$SCRIPT_DIR"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "[+] Creating virtual environment at: $VENV_PATH"
    python3 -m venv "$VENV_PATH"
fi

source "$VENV_PATH/bin/activate"

# Install solidago from the cloned source
pip install -e "$LIB_DIR/solidago" -q 2>/dev/null || \
    PYTHONPATH="$LIB_DIR/solidago/src:$PYTHONPATH" python "$SCRIPT_DIR/poc.py" && exit 0

# Run the PoC
echo "[+] Running PoC..."
PYTHONPATH="$LIB_DIR/solidago/src:$PYTHONPATH" python "$SCRIPT_DIR/poc.py"
