#!/bin/bash
# 野游记项目快速启动脚本

cd "$(dirname "$0")"

echo "=================================================="
echo "🚀 野游记快速启动"
echo "=================================================="
echo ""

# 加载环境变量
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ 已加载环境变量"
else
    echo "⚠️  未找到 .env 文件，部分功能可能不可用"
fi

echo ""
echo "请选择要运行的功能："
echo ""
echo "  1. 测试单个 Agent（快速）"
echo "  2. 测试完整流程（需要 AI_API_KEY）"
echo "  3. 启动 Flask API 服务"
echo "  4. 修复 Pydantic V2 兼容性"
echo "  5. 运行自定义 Python 文件"
echo "  0. 退出"
echo ""
read -p "请输入选项 (0-5): " choice

case $choice in
    1)
        echo ""
        echo "🧪 运行单个 Agent 测试..."
        python3 test_multi_agent.py --mode single
        ;;
    2)
        echo ""
        echo "🧪 运行完整流程测试..."
        python3 test_multi_agent.py --mode full
        ;;
    3)
        echo ""
        echo "🌐 启动 Flask API 服务..."
        echo "访问地址: http://localhost:5000"
        python3 api/app.py
        ;;
    4)
        echo ""
        echo "🔧 修复 Pydantic V2 兼容性..."
        python3 fix_pydantic_v2.py
        ;;
    5)
        echo ""
        read -p "请输入 Python 文件路径: " file_path
        if [ -f "$file_path" ]; then
            python3 "$file_path"
        else
            echo "❌ 文件不存在: $file_path"
        fi
        ;;
    0)
        echo "👋 再见！"
        exit 0
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac
