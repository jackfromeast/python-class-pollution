#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Path to the virtual environment
VENV_PATH="$SCRIPT_DIR/venv"

# Check if the virtual environment exists
if [ -d "$VENV_PATH" ]; then
    echo "[+] Virtual environment found in: $VENV_PATH"
else
    echo "[!] No virtual environment found. Creating one at: $VENV_PATH"
    python3 -m venv "$VENV_PATH"
    if [ $? -ne 0 ]; then
        echo "[!] Failed to create virtual environment. Ensure Python 3 and venv module are installed."
        exit 1
    fi
    echo "[+] Virtual environment created at: $VENV_PATH"

    # Install requirements if requirements.txt exists
    if [ -f "$REQUIREMENTS_FILE" ]; then
        echo "[+] Installing dependencies from $REQUIREMENTS_FILE..."
        pip3 install -r "$REQUIREMENTS_FILE"
        if [ $? -eq 0 ]; then
            echo "[+] Dependencies installed successfully."
        else
            echo "[!] Failed to install dependencies. Check the requirements.txt file."
            exit 1
        fi
    else
        echo "[!] No requirements.txt file found. Skipping dependency installation."
    fi
fi

# Activate the virtual environment in the current shell
# Check if the activate script exists
ACTIVATE_SCRIPT="$VENV_PATH/bin/activate"
if [ -f "$ACTIVATE_SCRIPT" ]; then
    # Source the activation script to activate it in the current shell
    source "$ACTIVATE_SCRIPT"
    echo "[+] Virtual environment activated. (Python: $(which python))"
else
    echo "[!] Activation script not found. Something went wrong with the virtual environment setup."
    exit 1
fi
