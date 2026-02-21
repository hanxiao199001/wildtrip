#!/bin/bash
# 每日生产任务 - 15 篇高质量攻略

cd /root/clawd/wildtrip-existing/backend

echo "🌴 野游记每日生产任务"
echo "目标：15 篇海南本地高质量攻略"
echo "================================"
echo ""

python3 bots/daily_production.py

echo ""
echo "✅ 任务完成"
echo "查看报告: cat data/daily_reports/report_$(date +%Y-%m-%d).json"
