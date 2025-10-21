#!/bin/zsh
set -e

# Double-click to launch breathVOICE locally
# This script starts the Gradio service and auto-opens your browser.

# Move to project root (directory of this script)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "[breathVOICE] Preparing to start service..."

# Free common Gradio ports to avoid conflicts (including 7866)
for p in 7860 7861 7862 7863 7864 7865 7866 7867 7868 7869; do
  pid=$(lsof -ti tcp:$p 2>/dev/null || true)
  if [[ -n "$pid" ]]; then
    echo "[breathVOICE] Killing process on port $p (PID: $pid)"
    kill -9 $pid 2>/dev/null || true
    sleep 1
  fi
done

# Try to activate conda environment if available
if command -v conda >/dev/null 2>&1; then
  # Load conda shell functions
  source "$(conda info --base)/etc/profile.d/conda.sh" 2>/dev/null || true
  # Activate gradio_env if it exists
  conda activate gradio_env >/dev/null 2>&1 || true
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
  echo "[breathVOICE] Creating virtual environment..."
  if ! python3 -m venv venv; then
    echo "[breathVOICE] Error: Failed to create virtual environment. Please ensure Python 3 is installed."
    exit 1
  fi
  echo "[breathVOICE] Installing dependencies..."
  source venv/bin/activate
  if ! pip install -r requirements.txt; then
    echo "[breathVOICE] Error: Failed to install dependencies. Please check your internet connection."
    exit 1
  fi
else
  echo "[breathVOICE] Activating virtual environment..."
  source venv/bin/activate
fi

echo "[breathVOICE] Using Python: $(which python)"
echo "[breathVOICE] Launching app..."
echo "[breathVOICE] Local access: http://0.0.0.0:7866"
echo "[breathVOICE] LAN access: http://[Your-IP-Address]:7866"

# Set Gradio environment variables
export GRADIO_SERVER_NAME="0.0.0.0"
export GRADIO_SERVER_PORT=7866
export GRADIO_ROOT_PATH=""

# Launch app; Gradio will auto-open the default browser due to inbrowser=True
# Set GRADIO_SERVER_PORT to allow port flexibility
export GRADIO_SERVER_PORT=7866
python app.py