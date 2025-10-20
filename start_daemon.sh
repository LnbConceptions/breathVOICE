#!/bin/bash
set -e

# breathVOICE 后台运行脚本 for macOS
# 适用于SSH远程连接，断开连接后仍保持运行

# 获取脚本所在目录并切换到项目根目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 日志文件路径
LOG_FILE="$SCRIPT_DIR/breathvoice_daemon.log"
PID_FILE="$SCRIPT_DIR/breathvoice.pid"

echo "🎤 [breathVOICE Daemon] 正在准备后台启动服务..."

# 检查是否已经在运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "❌ [breathVOICE Daemon] 服务已在运行 (PID: $PID)"
        echo "   如需重启，请先运行: ./stop_daemon.sh"
        exit 1
    else
        echo "🧹 [breathVOICE Daemon] 清理过期的PID文件"
        rm -f "$PID_FILE"
    fi
fi

# 释放常用的 Gradio 端口以避免冲突
echo "🔧 [breathVOICE Daemon] 检查并释放端口..."
for port in 7860 7861 7862 7863 7864 7865 7866; do
  pid=$(lsof -ti tcp:$port 2>/dev/null || true)
  if [[ -n "$pid" ]]; then
    echo "   ⚠️  正在终止端口 $port 上的进程 (PID: $pid)"
    kill -9 $pid 2>/dev/null || true
    sleep 1
  fi
done

# 尝试激活 conda 环境（如果可用）
if command -v conda >/dev/null 2>&1; then
  echo "🐍 [breathVOICE Daemon] 检测到 Conda，尝试激活环境..."
  # 加载 conda shell 函数
  source "$(conda info --base)/etc/profile.d/conda.sh" 2>/dev/null || true
  # 激活 gradio_env 环境（如果存在）
  conda activate gradio_env >/dev/null 2>&1 || echo "   ℹ️  未找到 gradio_env 环境，继续使用虚拟环境"
fi

# 检查虚拟环境是否存在，不存在则创建
if [ ! -d "venv" ]; then
  echo "📦 [breathVOICE Daemon] 创建虚拟环境..."
  python3 -m venv venv
  echo "📥 [breathVOICE Daemon] 安装依赖包..."
  source venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
else
  echo "🔄 [breathVOICE Daemon] 激活虚拟环境..."
  source venv/bin/activate
fi

# 显示使用的 Python 版本和路径
echo "🐍 [breathVOICE Daemon] 使用 Python: $(which python)"
echo "📋 [breathVOICE Daemon] Python 版本: $(python --version)"

# 检查必要的依赖是否已安装
echo "🔍 [breathVOICE Daemon] 检查依赖..."
python -c "import gradio; print(f'   ✅ Gradio {gradio.__version__}')" 2>/dev/null || {
  echo "   ❌ Gradio 未安装，正在安装..."
  pip install gradio
}

# 启动应用到后台
echo ""
echo "🚀 [breathVOICE Daemon] 启动后台服务..."
echo "   📝 日志文件: $LOG_FILE"
echo "   🆔 PID文件: $PID_FILE"
echo "   🌐 本地访问地址: http://0.0.0.0:7866"
echo "   🌐 局域网访问地址: http://[您的IP地址]:7866"
echo "   ⏹️  停止服务: ./stop_daemon.sh"
echo ""

# 设置Gradio环境变量
export GRADIO_SERVER_NAME="0.0.0.0"
export GRADIO_SERVER_PORT=7866
# 在反向代理下将root_path设为子路径，以正确生成URL
export GRADIO_ROOT_PATH="/gradio_api"

# 使用nohup在后台运行，并记录PID
nohup python app.py > "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"

echo "✅ [breathVOICE Daemon] 服务已启动 (PID: $(cat $PID_FILE))"
echo "   您现在可以安全地断开SSH连接"
echo "   查看日志: tail -f $LOG_FILE"
echo "   停止服务: ./stop_daemon.sh"