#!/bin/bash

# WildTrip 一键启动脚本

echo "🌴 野游记 WildTrip - 启动中..."

# 检查后端是否运行
BACKEND_PID=$(ps aux | grep "python.*app.py" | grep -v grep | awk '{print $2}')
if [ -n "$BACKEND_PID" ]; then
    echo "✅ 后端已在运行 (PID: $BACKEND_PID)"
else
    echo "🚀 启动后端服务..."
    cd ../backend
    screen -dmS wildtrip-backend bash -c "python3 app.py 2>&1 | tee logs/server.log"
    sleep 3
    echo "✅ 后端启动完成"
fi

# 检查前端是否运行
FRONTEND_PID=$(ps aux | grep "python.*http.server.*8080" | grep -v grep | awk '{print $2}')
if [ -n "$FRONTEND_PID" ]; then
    echo "✅ 前端已在运行 (PID: $FRONTEND_PID)"
else
    echo "🎨 启动前端服务..."
    cd ../web
    python3 -m http.server 8080 > /dev/null 2>&1 &
    sleep 2
    echo "✅ 前端启动完成"
fi

echo ""
echo "================================================"
echo "🎉 所有服务启动成功！"
echo "================================================"
echo ""
echo "📡 后端API: http://localhost:5000"
echo "🌐 前端界面: http://localhost:8080"
echo ""
echo "💡 使用说明:"
echo "  - 在浏览器打开 http://localhost:8080"
echo "  - 输入旅行需求，点击生成按钮"
echo "  - 等待AI生成完整攻略"
echo ""
echo "📊 查看日志:"
echo "  - 后端: tail -f backend/logs/server.log"
echo "  - 前端: 浏览器控制台 (F12)"
echo ""
echo "🛑 停止服务:"
echo "  pkill -f 'python.*app.py'"
echo "  pkill -f 'python.*http.server'"
echo "================================================"
