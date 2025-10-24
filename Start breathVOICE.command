#!/bin/zsh
set -e

# Double-click to launch breathVOICE locally
# This script starts the Gradio service and auto-opens your browser.

# Move to project root (directory of this script)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "[breathVOICE] Preparing to start service..."

# Target port (fixed to 7866)
TARGET_PORT=7866

# Function to ensure port 7866 is available
ensure_port_available() {
  local port=$1
  local max_attempts=3
  local attempt=1
  
  while [ $attempt -le $max_attempts ]; do
    echo "[breathVOICE] Attempt $attempt: Checking port $port..."
    
    # Check if port is in use
    pid=$(lsof -ti tcp:$port 2>/dev/null || true)
    if [[ -n "$pid" ]]; then
      echo "[breathVOICE] Port $port is occupied by process $pid, terminating..."
      kill -9 $pid 2>/dev/null || true
      sleep 2
    else
      echo "[breathVOICE] Port $port is available"
      return 0
    fi
    
    attempt=$((attempt + 1))
  done
  
  echo "[breathVOICE] Error: Unable to free port $port after $max_attempts attempts"
  exit 1
}

# Free common Gradio ports to avoid conflicts
echo "[breathVOICE] Cleaning up common Gradio ports..."
for p in 7860 7861 7862 7863 7864 7865 7866 7867 7868 7869; do
  pid=$(lsof -ti tcp:$p 2>/dev/null || true)
  if [[ -n "$pid" ]]; then
    echo "[breathVOICE] Killing process on port $p (PID: $pid)"
    kill -9 $pid 2>/dev/null || true
    sleep 1
  fi
done

# Ensure target port 7866 is available
ensure_port_available $TARGET_PORT
AVAILABLE_PORT=$TARGET_PORT

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