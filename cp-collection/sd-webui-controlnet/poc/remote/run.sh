#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"

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

# Check if SD WebUI server is running
echo "[+] Checking if SD WebUI server is running at http://localhost:7860..."
if ! curl -s http://localhost:7860/ > /dev/null 2>&1; then
    echo "[!] SD WebUI server with ControlNet extension is NOT running."
    echo ""
    echo "    To start:"
    echo "      git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git"
    echo "      cd stable-diffusion-webui/extensions"
    echo "      git clone https://github.com/Mikubill/sd-webui-controlnet.git"
    echo "      cd .. && ./webui.sh --api --listen"
    echo ""
    echo "    Then re-run this script."
    exit 1
fi

# Run the PoC
echo "[+] Running PoC (HTTP class pollution trigger)..."
python "$SCRIPT_DIR/poc.py"
