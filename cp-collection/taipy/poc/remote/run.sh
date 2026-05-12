#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
APP_DIR="$SCRIPT_DIR/app"
PORT=5003

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "[+] Creating virtual environment at: $VENV_PATH"
    python3 -m venv "$VENV_PATH"
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Install app dependencies (taipy-gui + openai) and PoC dependencies (socketio client + requests)
echo "[+] Installing dependencies..."
pip install -r "$APP_DIR/requirements.txt" -q
pip install -r "$SCRIPT_DIR/requirements.txt" -q

# Patch flask-socketio 5.4.1 compatibility issue with flask 3.1.x
# (ctx.session property is read-only in newer Flask)
FLASK_SIO_FILE=$(find "$VENV_PATH" -path "*/flask_socketio/__init__.py" 2>/dev/null | head -1)
if [ -n "$FLASK_SIO_FILE" ] && grep -q "ctx.session = session_obj" "$FLASK_SIO_FILE"; then
    echo "[+] Patching flask-socketio for flask 3.1.x compatibility..."
    python -c "
with open('$FLASK_SIO_FILE', 'r') as f:
    lines = f.readlines()
with open('$FLASK_SIO_FILE', 'w') as f:
    for line in lines:
        if 'ctx.session = session_obj' in line:
            indent = line[:len(line) - len(line.lstrip())]
            f.write(indent + 'try:\n')
            f.write(indent + '    ' + line.lstrip())
            f.write(indent + 'except AttributeError:\n')
            f.write(indent + '    pass\n')
        else:
            f.write(line)
"
fi

# Set OpenAI API key if not already set
export OPENAI_API_KEY="${OPENAI_API_KEY}"

# Kill any existing process on the target port
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo "[+] Killing existing process on port $PORT..."
    kill $(lsof -ti:$PORT) 2>/dev/null
    sleep 2
fi

# Clean up any previous RCE artifact
rm -f /tmp/pwned

# Start Taipy server in background
echo "[+] Starting Taipy app on port $PORT..."
python "$APP_DIR/main.py" > /tmp/taipy-server.log 2>&1 &
SERVER_PID=$!

# Wait for server to be ready
echo "[+] Waiting for server to start..."
for i in $(seq 1 30); do
    if curl -s "http://localhost:$PORT/" > /dev/null 2>&1; then
        echo "[+] Server is up!"
        break
    fi
    if ! kill -0 $SERVER_PID 2>/dev/null; then
        echo "[-] Server process died unexpectedly."
        exit 1
    fi
    sleep 1
done

if ! curl -s "http://localhost:$PORT/" > /dev/null 2>&1; then
    echo "[-] Server failed to start within 30 seconds."
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

# Run the RCE PoC with a timeout (race condition may take some time)
echo "[+] Running RCE PoC (race condition class pollution)..."
timeout 60 python "$SCRIPT_DIR/poc-rce.py" 2>&1 | grep -v "^Exception in thread\|^Traceback\|^  File\|^    "

# Wait briefly for the RCE payload to execute on the server side
sleep 3

# Verify RCE
if [ -f /tmp/pwned ]; then
    echo "[+] RCE successful! /tmp/pwned was created."
else
    echo "[-] RCE artifact not found. The race may need more attempts."
fi

# Cleanup
echo "[+] Stopping server..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null
echo "[+] Done."
