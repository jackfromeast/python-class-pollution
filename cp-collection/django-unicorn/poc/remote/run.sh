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

# Start Django server in background
echo "[+] Starting Django app from: $APP_DIR"
cd "$APP_DIR"
python manage.py runserver 0.0.0.0:8000 &>/dev/null &
SERVER_PID=$!
cd "$SCRIPT_DIR"

# Wait for server to be ready
echo "[+] Waiting for server to start..."
for i in $(seq 1 15); do
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        break
    fi
    sleep 1
done

# Run the basic class pollution trigger
echo "[+] Running PoC (basic class pollution trigger)..."
python "$SCRIPT_DIR/poc.py"

echo ""
echo "[*] Exploit scripts available in exploit/:"
echo "    - poc-xss-reflected.py   (Reflected XSS via bs4 sanitizer overwrite)"
echo "    - poc-xss-stored.py      (Stored XSS via MORPHER_NAMES + json_script_escapes)"
echo "    - poc-xss-errorpage.py   (Stored XSS via Django error page template)"
echo "    - poc-auth-bypass.py     (Auth bypass via SECRET_KEY overwrite)"
echo "    - poc-dos.py             (DoS via timed decorator overwrite)"

# Cleanup
echo ""
echo "[+] Stopping server..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null
