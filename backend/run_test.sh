#!/bin/bash
# 野游记多智能体测试快速启动脚本

cd "$(dirname "$0")"

echo "=================================================="
echo "🚀 野游记多智能体测试"
echo "=================================================="
echo ""

# 加载环境变量
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ 已加载 .env 配置"
else
    echo "⚠️  未找到 .env 文件"
fi

echo ""

# 选择测试模式
if [ "$1" = "full" ]; then
    echo "🧪 运行完整测试（4个 Agent）..."
    echo ""
    python3 test_multi_agent.py --mode full
elif [ "$1" = "single" ]; then
    echo "🧪 运行单个 Agent 测试..."
    echo ""
    python3 test_multi_agent.py --mode single
else
    echo "使用方法："
    echo "  ./run_test.sh single   # 测试单个 Agent（快速）"
    echo "  ./run_test.sh full     # 测试完整流程（需要 AI_API_KEY）"
    echo ""
    echo "示例："
    echo "  ./run_test.sh single"
    exit 1
fi
