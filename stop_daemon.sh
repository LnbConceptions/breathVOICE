#!/bin/bash

# breathVOICE 后台服务停止脚本

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PID_FILE="$SCRIPT_DIR/breathvoice.pid"
LOG_FILE="$SCRIPT_DIR/breathvoice_daemon.log"

echo "🛑 [breathVOICE Daemon] 正在停止后台服务..."

# 检查PID文件是否存在
if [ ! -f "$PID_FILE" ]; then
    echo "ℹ️ [breathVOICE Daemon] 未找到PID文件，服务可能未运行"
    exit 0
fi

# 读取PID
PID=$(cat "$PID_FILE")

# 检查进程是否存在
if ! ps -p $PID > /dev/null 2>&1; thenecho "ℹ️ [breathVOICE Daemon] 进程 $PID 不存在，清理PID文件"
        rm -f "$PID_FILE"
        exit 00
fi

# 尝试优雅地停止进程
echo "⏹️  [breathVOICE Daemon] 正在停止进程 $PID..."
kill $PID

# 等待进程结束
for i in {1..10}; do
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "✅ [breathVOICE Daemon] 服务已成功停止"
        rm -f "$PID_FILE"
        exit 0
    fi
    echo "   等待进程结束... ($i/10)"
    sleep 1
done

# 如果优雅停止失败，强制终止
echo "⚠️  [breathVOICE Daemon] 优雅停止失败，强制终止进程..."
kill -9 $PID 2>/dev/null || true

# 再次检查
if ! ps -p $PID > /dev/null 2>&1; then
    echo "✅ [breathVOICE Daemon] 服务已强制停止"
    rm -f "$PID_FILE"
else
    echo "❌ [breathVOICE Daemon] 无法停止进程 $PID"
    exit 0
fi