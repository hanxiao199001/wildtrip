#!/bin/bash
# Wildtrip 一键部署脚本
# 复制整个文件内容，SSH到服务器后粘贴执行

set -e

echo "🚀 开始部署 Wildtrip..."

# 1. 进入项目目录
cd /root/clawd/wildtrip || { echo "❌ 项目目录不存在"; exit 1; }

# 2. 检查部署文件
if [ ! -f "deploy/deploy-wildtrip.sh" ]; then
    echo "❌ 找不到部署脚本"
    exit 1
fi

# 3. 修改邮箱地址
echo "📧 配置邮箱地址..."
sed -i 's/your-email@example.com/han272624836@gmail.com/g' deploy/deploy-wildtrip.sh

# 4. 安装依赖
echo "📦 检查依赖..."
if ! command -v certbot &> /dev/null; then
    apt update
    apt install -y certbot python3-certbot-nginx
fi

if ! command -v pip3 &> /dev/null; then
    apt install -y python3-pip
fi

pip3 install -q gunicorn flask flask-cors requests || true

# 5. 执行部署脚本
echo "🔧 执行 Nginx + SSL 部署..."
chmod +x deploy/deploy-wildtrip.sh
bash deploy/deploy-wildtrip.sh

# 6. 部署 systemd 服务
echo "⚙️ 配置 Flask 自动启动..."
cp deploy/wildtrip-backend.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable wildtrip-backend
systemctl restart wildtrip-backend

# 7. 等待服务启动
echo "⏳ 等待服务启动..."
sleep 3

# 8. 检查服务状态
echo ""
echo "📊 服务状态："
systemctl status wildtrip-backend --no-pager || true

# 9. 测试接口
echo ""
echo "🧪 测试 API..."
echo "本地测试："
curl -s http://127.0.0.1:5000/api/test || echo "⚠️ 本地 Flask 连接失败"

echo ""
echo "HTTPS 测试："
sleep 2
curl -s https://api.wildtrip.com.cn/health || echo "⚠️ HTTPS 健康检查失败"

echo ""
echo "✅ 部署完成！"
echo ""
echo "📋 验证命令："
echo "  systemctl status wildtrip-backend"
echo "  systemctl status nginx"
echo "  curl https://api.wildtrip.com.cn/api/test"
echo ""
echo "📖 查看日志："
echo "  journalctl -u wildtrip-backend -f"
echo "  tail -f /var/log/nginx/wildtrip_error.log"
