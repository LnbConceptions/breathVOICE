#!/bin/bash
set -e

# breathVOICE 一键启动脚本 for macOS
# 双击或在终端运行此脚本即可启动 breathVOICE 应用

# 获取脚本所在目录并切换到项目根目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🎤 [breathVOICE] 正在准备启动服务..."

# 释放常用的 Gradio 端口以避免冲突
echo "🔧 [breathVOICE] 检查并释放端口..."
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
  echo "🐍 [breathVOICE] 检测到 Conda，尝试激活环境..."
  # 加载 conda shell 函数
  source "$(conda info --base)/etc/profile.d/conda.sh" 2>/dev/null || true
  # 激活 gradio_env 环境（如果存在）
  conda activate gradio_env >/dev/null 2>&1 || echo "   ℹ️  未找到 gradio_env 环境，继续使用虚拟环境"
fi

# 检查虚拟环境是否存在，不存在则创建
if [ ! -d "venv" ]; then
  echo "📦 [breathVOICE] 创建虚拟环境..."
  python3 -m venv venv
  echo "📥 [breathVOICE] 安装依赖包..."
  source venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
else
  echo "🔄 [breathVOICE] 激活虚拟环境..."
  source venv/bin/activate
fi

# 显示使用的 Python 版本和路径
echo "🐍 [breathVOICE] 使用 Python: $(which python)"
echo "📋 [breathVOICE] Python 版本: $(python --version)"

# 检查必要的依赖是否已安装
echo "🔍 [breathVOICE] 检查依赖..."
python -c "import gradio; print(f'   ✅ Gradio {gradio.__version__}')" 2>/dev/null || {
  echo "   ❌ Gradio 未安装，正在安装..."
  pip install gradio
}

# 启动应用
echo ""
echo "🚀 [breathVOICE] 启动应用..."
echo "   📱 应用将在浏览器中自动打开"
echo "   🌐 本地访问地址: http://0.0.0.0:7866"
echo "   🌐 局域网访问地址: http://[您的IP地址]:7866"
echo "   ⏹️  按 Ctrl+C 停止服务"
echo ""

# 设置Gradio环境变量
export GRADIO_SERVER_NAME="0.0.0.0"
export GRADIO_SERVER_PORT=7866

# 启动应用，Gradio 会因为 inbrowser=True 自动打开默认浏览器
python app.py