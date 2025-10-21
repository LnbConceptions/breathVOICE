#!/bin/zsh
set -e

# Double-click to launch breathVOICE locally
# This script starts the Gradio service and auto-opens your browser.

# Move to project root (directory of this script)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "[breathVOICE] Preparing to start service..."

# Function to find available port
find_available_port() {
  local start_port=${1:-7866}
  local port=$start_port
  while [ $port -le $((start_port + 20)) ]; do
    if ! lsof -ti tcp:$port >/dev/null 2>&1; then
      echo $port
      return 0
    fi
    port=$((port + 1))
  done
  echo "0"  # No available port found
}

# Free common Gradio ports to avoid conflicts (including 7866)
for p in 7860 7861 7862 7863 7864 7865 7866 7867 7868 7869; do
  pid=$(lsof -ti tcp:$p 2>/dev/null || true)
  if [[ -n "$pid" ]]; then
    echo "[breathVOICE] Killing process on port $p (PID: $pid)"
    kill -9 $pid 2>/dev/null || true
    sleep 1
  fi
done

# Find available port
AVAILABLE_PORT=$(find_available_port 7866)
if [ "$AVAILABLE_PORT" = "0" ]; then
  echo "[breathVOICE] Error: No available port found in range 7866-7886"
  exit 1
fi

echo "[breathVOICE] Using port: $AVAILABLE_PORT"

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
echo "[breathVOICE] Local access: http://127.0.0.1:$AVAILABLE_PORT"
echo "[breathVOICE] LAN access: http://[Your-IP-Address]:$AVAILABLE_PORT"

# Set Gradio environment variables
export GRADIO_SERVER_NAME="127.0.0.1"
export GRADIO_SERVER_PORT=$AVAILABLE_PORT
export GRADIO_ROOT_PATH=""

# Launch app; Gradio will auto-open the default browser due to inbrowser=True
python app.py