#!/bin/bash
# 野游记 WildTrip 启动脚本

echo "🔥 野游记 WildTrip 启动中..."

# 检查.env文件
if [ ! -f .env ]; then
    echo "⚠️  .env文件不存在，复制.env.example..."
    cp .env.example .env
    echo "✅ 请编辑.env文件，填写配置信息"
    exit 1
fi

# 创建日志目录
mkdir -p logs

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 安装依赖
if [ ! -d "venv" ]; then
    echo "📦 首次运行，安装依赖..."
    pip install -r requirements.txt
fi

# 启动服务
echo "🚀 启动Flask服务..."
python app.py
