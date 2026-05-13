#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
LIB_DIR="$SCRIPT_DIR/repo"

# Clone EasyCV if not already present
if [ ! -d "$LIB_DIR" ]; then
    echo "[+] Cloning EasyCV..."
    git clone --depth 1 https://github.com/alibaba/EasyCV.git "$LIB_DIR"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "[+] Creating virtual environment at: $VENV_PATH"
    python3 -m venv "$VENV_PATH"
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Install deps (mmengine replaces mmcv which no longer builds on Python 3.12+)
pip install mmengine==0.10.7 pyyaml==6.0.3 tqdm==4.67.1 -q

# Create mmcv shim that redirects to mmengine
SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")
mkdir -p "$SITE_PACKAGES/mmcv"
cat > "$SITE_PACKAGES/mmcv/__init__.py" << 'PYEOF'
from mmengine import Config
from mmengine.utils import import_modules_from_strings
PYEOF

# Run the PoC with EasyCV on PYTHONPATH
echo "[+] Running PoC..."
PYTHONPATH="$LIB_DIR:$PYTHONPATH" python "$SCRIPT_DIR/poc.py"
