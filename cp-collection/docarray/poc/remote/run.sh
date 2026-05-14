#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
APP_DIR="$SCRIPT_DIR/app"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "[+] Creating virtual environment at: $VENV_PATH"
    python3 -m venv "$VENV_PATH"
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Install requirements
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "[+] Installing dependencies..."
    pip install -r "$REQUIREMENTS_FILE" -q
fi

# Start server in background
echo "[+] Starting Thesis Processing API (FastAPI + docarray)..."
python "$APP_DIR/main.py" &
SERVER_PID=$!

# Wait for server to be ready
echo "[+] Waiting for server to start..."
for i in $(seq 1 30); do
    if curl -s http://localhost:8080/docs > /dev/null 2>&1; then
        break
    fi
    sleep 1
done

# Run the PoC
echo "[+] Running PoC (DoS via MultiModalDataset class pollution)..."
echo ""
python "$SCRIPT_DIR/poc.py"

# Cleanup
echo ""
echo "[+] Stopping server..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null
