#!/bin/bash
# 查看每日生产任务进度

echo "📊 野游记每日生产任务进度"
echo "================================"
echo ""

# 检查是否有正在运行的任务
if pgrep -f "daily_production.py" > /dev/null; then
  echo "✅ 任务正在运行中..."
  echo ""
  
  # 显示最近的日志
  echo "📋 最近日志（最后 20 行）："
  echo "---"
  tail -20 /root/clawd/wildtrip-existing/backend/logs/wildtrip.log 2>/dev/null || echo "（日志文件未找到）"
  echo ""
else
  echo "❌ 没有正在运行的任务"
  echo ""
fi

# 显示今日报告（如果存在）
TODAY=$(date +%Y-%m-%d)
REPORT_FILE="/root/clawd/wildtrip-existing/backend/data/daily_reports/report_${TODAY}.json"

if [ -f "$REPORT_FILE" ]; then
  echo "📄 今日报告："
  echo "---"
  cat "$REPORT_FILE" | python3 -m json.tool 2>/dev/null | head -30
  echo ""
  
  # 统计成功数
  SUCCESS=$(cat "$REPORT_FILE" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('success', 0))" 2>/dev/null)
  TARGET=$(cat "$REPORT_FILE" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('target', 15))" 2>/dev/null)
  
  if [ -n "$SUCCESS" ] && [ -n "$TARGET" ]; then
    echo "📊 进度: $SUCCESS / $TARGET 篇"
  fi
else
  echo "⏳ 今日报告尚未生成"
fi

echo ""
echo "================================"
echo ""
echo "💡 提示："
echo "  - 实时日志: tail -f backend/logs/wildtrip.log"
echo "  - 查看选题: cat backend/data/daily_topics/topics_${TODAY}.json"
echo "  - 查看生成页面: ls -lh /root/clawd/wildtrip/web/guides/ | tail -20"
