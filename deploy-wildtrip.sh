#!/bin/bash
# Wildtrip 服务器部署脚本
# 在服务器上运行（47.236.103.89）

set -e

echo "🚀 开始部署 Wildtrip API 服务器..."

# 1. 安装 Certbot（如果没有）
echo "📦 检查 Certbot..."
if ! command -v certbot &> /dev/null; then
    echo "安装 Certbot..."
    apt update
    apt install -y certbot python3-certbot-nginx
else
    echo "✅ Certbot 已安装"
fi

# 2. 申请 SSL 证书
echo "🔒 申请 SSL 证书..."
certbot certonly --nginx -d api.wildtrip.com.cn --non-interactive --agree-tos --email han272624836@gmail.com

# 3. 部署 Nginx 配置
echo "⚙️ 部署 Nginx 配置..."
cat > /etc/nginx/sites-available/wildtrip <<'EOF'
server {
    listen 80;
    server_name api.wildtrip.com.cn;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.wildtrip.com.cn;
    
    ssl_certificate /etc/letsencrypt/live/api.wildtrip.com.cn/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.wildtrip.com.cn/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    access_log /var/log/nginx/wildtrip_access.log;
    error_log /var/log/nginx/wildtrip_error.log;
    
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /health {
        return 200 "OK\n";
        add_header Content-Type text/plain;
    }
}
EOF

# 4. 启用站点
echo "🔗 启用站点..."
ln -sf /etc/nginx/sites-available/wildtrip /etc/nginx/sites-enabled/wildtrip

# 5. 测试 Nginx 配置
echo "🧪 测试 Nginx 配置..."
nginx -t

# 6. 重启 Nginx
echo "🔄 重启 Nginx..."
systemctl restart nginx

# 7. 检查 Flask 是否运行
echo "🐍 检查 Flask 后端..."
if ! pgrep -f "python.*app.py\|gunicorn" > /dev/null; then
    echo "⚠️ Flask 后端未运行！"
    echo "请到项目目录运行："
    echo "  cd /root/wildtrip-backend"
    echo "  nohup python app.py > flask.log 2>&1 &"
    echo "或使用 Gunicorn："
    echo "  gunicorn -w 4 -b 127.0.0.1:5000 app:app --daemon"
else
    echo "✅ Flask 后端正在运行"
fi

# 8. 测试 API
echo "🧪 测试 API..."
sleep 2
curl -k https://api.wildtrip.com.cn/health || echo "⚠️ 健康检查失败"

echo ""
echo "✅ 部署完成！"
echo ""
echo "📋 后续检查："
echo "  1. 确认 Flask 在 5000 端口运行"
echo "  2. 测试：curl https://api.wildtrip.com.cn/health"
echo "  3. 测试：curl https://api.wildtrip.com.cn/api/test"
echo "  4. 查看日志：tail -f /var/log/nginx/wildtrip_error.log"
echo ""
echo "🔄 SSL 证书会自动续期（Certbot 定时任务）"
