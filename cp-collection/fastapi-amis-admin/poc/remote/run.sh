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

# Start FastAPI server in background
echo "[+] Starting fastapi-amis-admin server..."
python "$APP_DIR/main.py" &>/dev/null &
SERVER_PID=$!

# Wait for server to be ready
echo "[+] Waiting for server to start..."
for i in $(seq 1 15); do
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        break
    fi
    sleep 1
done

# Run the PoC
echo "[+] Running PoC (HTTP CRUD class pollution trigger)..."
python "$SCRIPT_DIR/poc.py"

# Cleanup
echo ""
echo "[+] Stopping server..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null
