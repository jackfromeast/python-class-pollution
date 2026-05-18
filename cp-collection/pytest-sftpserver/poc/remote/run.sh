#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
APP_DIR="$SCRIPT_DIR/app"
PORT=3373

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "[+] Creating virtual environment at: $VENV_PATH"
    python3 -m venv "$VENV_PATH"
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Install app dependencies and PoC dependencies
echo "[+] Installing dependencies..."
pip install -r "$APP_DIR/requirements.txt" -q
pip install -r "$SCRIPT_DIR/requirements.txt" -q

# Kill any existing process on the target port
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo "[+] Killing existing process on port $PORT..."
    kill $(lsof -ti:$PORT) 2>/dev/null
    sleep 2
fi

# Start SFTP server in background
echo "[+] Starting SFTP server on port $PORT..."
python "$APP_DIR/main.py" > /tmp/sftpserver.log 2>&1 &
SERVER_PID=$!

# Wait for server to be ready
echo "[+] Waiting for server to start..."
for i in $(seq 1 10); do
    if nc -z localhost $PORT 2>/dev/null; then
        echo "[+] Server is up!"
        break
    fi
    if ! kill -0 $SERVER_PID 2>/dev/null; then
        echo "[-] Server process died unexpectedly."
        cat /tmp/sftpserver.log
        exit 1
    fi
    sleep 1
done

if ! nc -z localhost $PORT 2>/dev/null; then
    echo "[-] Server failed to start within 10 seconds."
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

# Run the PoC
echo "[+] Running class pollution PoC..."
python "$SCRIPT_DIR/poc-pollution.py"

# Cleanup
echo "[+] Stopping server..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null
echo "[+] Done."
