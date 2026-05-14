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

cd "$APP_DIR"
python manage.py migrate -v 0
python manage.py collectstatic --noinput -v 0

# Start Django server
echo "[+] Starting NovaMart demo at http://localhost:8000"
ADMIN_TOKEN=$(DJANGO_SETTINGS_MODULE=settings python -c "from django.core.signing import Signer; print(Signer().sign('admin'))")
echo "[+] Admin API token: $ADMIN_TOKEN"
echo "[+] Dashboard: http://localhost:8000/api/admin/dashboard/?token=$ADMIN_TOKEN"
echo ""
echo "[*] Exploit scripts available in exploit/:"
echo "    - poc-rce.py             (RCE via os.environ.BROWSER + antigravity)"
echo "    - poc-dos.py             (DoS via timed decorator overwrite)"
echo "    - poc-auth-bypass.py     (Auth bypass via SECRET_KEY overwrite)"
echo "    - poc-xss-stored.py      (Stored XSS via MORPHER_NAMES + json_script)"
echo "    - poc-xss-reflected.py   (Reflected XSS via bs4 sanitizer overwrite)"
echo "    - poc-xss-errorpage.py   (Stored XSS via Django error page template)"
echo "    - run-all.py             (Run all exploits sequentially)"
echo ""
echo "[*] Press Ctrl+C to stop"
python manage.py runserver 0.0.0.0:8000
