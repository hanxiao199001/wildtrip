#!/bin/bash
# 启动每日生产任务

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "🌴 野游记每日生产任务"
echo "================================"
echo ""

# 检查 API Key
if [ -z "$AI_API_KEY" ]; then
  echo "⚠️ 警告: AI_API_KEY 未配置"
  echo ""
  echo "请配置 API Key："
  echo "1. 创建 .env 文件"
  echo "2. 添加以下内容："
  echo ""
  echo "AI_API_KEY=sk-xxxxx"
  echo "AI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1"
  echo "AI_MODEL=qwen-plus"
  echo ""
  echo "或者使用环境变量："
  echo "export AI_API_KEY=sk-xxxxx"
  echo ""
  read -p "是否继续使用 Mock 数据测试？(y/n): " choice
  
  if [ "$choice" != "y" ]; then
    echo "已取消"
    exit 0
  fi
  
  echo ""
  echo "📝 使用 Mock 数据进行测试..."
  echo ""
fi

# 执行生产任务
cd backend
python3 bots/daily_production.py

echo ""
echo "✅ 任务完成"
echo ""
echo "📄 查看报告："
echo "cat backend/data/daily_reports/report_$(date +%Y-%m-%d).json"
echo ""
echo "📁 查看生成的页面："
echo "ls -lh "$PROJECT_ROOT"/web/guides/ | tail -20"
