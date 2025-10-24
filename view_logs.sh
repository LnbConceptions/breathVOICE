#!/bin/bash

# breathVOICE 日志查看器
# 用于查看应用程序运行日志

LOG_FILE="$HOME/Library/Application Support/breathVOICE/breathVOICE.log"

echo "=== breathVOICE 日志查看器 ==="
echo "日志文件位置: $LOG_FILE"
echo ""

if [ ! -f "$LOG_FILE" ]; then
    echo "❌ 日志文件不存在。请先运行 breathVOICE.app 生成日志。"
    exit 1
fi

echo "📊 日志文件信息:"
ls -lh "$LOG_FILE"
echo ""

echo "🔍 选择查看方式:"
echo "1) 查看完整日志"
echo "2) 查看最近50行"
echo "3) 查看启动信息"
echo "4) 查看错误信息"
echo "5) 实时监控日志"
echo ""

read -p "请选择 (1-5): " choice

case $choice in
    1)
        echo "=== 完整日志 ==="
        cat "$LOG_FILE"
        ;;
    2)
        echo "=== 最近50行 ==="
        tail -50 "$LOG_FILE"
        ;;
    3)
        echo "=== 启动信息 ==="
        grep -E "(breathVOICE|INFO)" "$LOG_FILE" | head -20
        ;;
    4)
        echo "=== 错误信息 ==="
        grep -E "(ERROR|CRITICAL|Exception|Traceback)" "$LOG_FILE"
        ;;
    5)
        echo "=== 实时监控 (按 Ctrl+C 退出) ==="
        tail -f "$LOG_FILE"
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac