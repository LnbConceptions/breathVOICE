#!/bin/bash

# breathVOICE 后台服务状态查看脚本

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PID_FILE="$SCRIPT_DIR/breathvoice.pid"
LOG_FILE="$SCRIPT_DIR/breathvoice_daemon.log"

echo "📊 [breathVOICE Daemon] 服务状态检查"
echo "=================================="

# 检查PID文件是否存在
if [ ! -f "$PID_FILE" ]; then
    echo "❌ 状态: 未运行 (未找到PID文件)"
    echo "🚀 启动服务: ./start_daemon.sh"
    exit 0
fi

# 读取PID
PID=$(cat "$PID_FILE")

# 检查进程是否存在
if ps -p $PID > /dev/null 2>&1; then
    echo "✅ 状态: 正在运行"
    echo "🆔 进程ID: $PID"
    echo "🌐 访问地址: http://127.0.0.1:7866"
    echo "📝 日志文件: $LOG_FILE"
    echo ""
    
    # 显示进程信息
    echo "📈 进程信息:"
    ps -p $PID -o pid,ppid,pcpu,pmem,etime,command
    echo ""
    
    # 检查端口占用
    echo "🔌 端口占用:"
    lsof -i :7866 2>/dev/null || echo "   未检测到7866端口占用"
    echo ""
    
    # 显示最近的日志
    if [ -f "$LOG_FILE" ]; then
        echo "📋 最近日志 (最后10行):"
        echo "------------------------"
        tail -n 10 "$LOG_FILE"
    else
        echo "📋 日志文件不存在"
    fi
    
    echo ""
    echo "🛠️  管理命令:"
    echo "   查看实时日志: tail -f $LOG_FILE"
    echo "   停止服务: ./stop_daemon.sh"
    
else
    echo "❌ 状态: 未运行 (进程 $PID 不存在)"
    echo "🧹 清理过期PID文件..."
    rm -f "$PID_FILE"
    echo "🚀 启动服务: ./start_daemon.sh"
fi