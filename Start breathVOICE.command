#!/bin/zsh
set -e

# Double-click to launch breathVOICE locally
# This script starts the Gradio service and auto-opens your browser.

# Move to project root (directory of this script)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "[breathVOICE] Preparing to start service..."

# Free common Gradio ports to avoid conflicts
for p in 7860 7861 7862; do
  pid=$(lsof -ti tcp:$p || true)
  if [[ -n "$pid" ]]; then
    echo "[breathVOICE] Killing process on port $p (PID: $pid)"
    kill -9 $pid || true
  fi
done

# Try to activate conda environment if available
if command -v conda >/dev/null 2>&1; then
  # Load conda shell functions
  source "$(conda info --base)/etc/profile.d/conda.sh" || true
  # Activate gradio_env if it exists
  conda activate gradio_env >/dev/null 2>&1 || true
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
  echo "[breathVOICE] Creating virtual environment..."
  python3 -m venv venv
  echo "[breathVOICE] Installing dependencies..."
  source venv/bin/activate
  pip install -r requirements.txt
else
  echo "[breathVOICE] Activating virtual environment..."
  source venv/bin/activate
fi

echo "[breathVOICE] Using Python: $(which python)"
echo "[breathVOICE] Launching app..."

# Launch app; Gradio will auto-open the default browser due to inbrowser=True
python app.py