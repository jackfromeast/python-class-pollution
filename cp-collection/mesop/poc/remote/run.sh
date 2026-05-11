#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
APP_DIR="$SCRIPT_DIR/app"

# Create virtual environment if it does not exist
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

# Start mesop server in background
echo "[+] Starting mesop app from: $APP_DIR/chat.py"
mesop "$APP_DIR/chat.py" &>/dev/null &
SERVER_PID=$!

# Wait for server to be ready
echo "[+] Waiting for server to start..."
for i in $(seq 1 15); do
    if curl -s http://localhost:32123/ > /dev/null 2>&1; then
        break
    fi
    sleep 1
done

# Run the basic class pollution trigger
echo "[+] Running PoC (basic class pollution trigger)..."
python "$SCRIPT_DIR/poc.py"

echo ""
echo "[*] Exploit scripts available in exploit/:"
echo "    - poc-dos.py        (DoS via time module overwrite)"
echo "    - poc-jailbreak.py  (Identity confusion via _ROLE_USER overwrite)"

# Cleanup
echo ""
echo "[+] Stopping server..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null
