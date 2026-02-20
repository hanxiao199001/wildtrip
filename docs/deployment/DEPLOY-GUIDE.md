# Wildtrip 服务器部署指南

## 快速部署（3 步搞定）

### 1. 上传文件到服务器

```bash
# 本地执行
scp deploy-wildtrip.sh wildtrip-backend.service root@47.236.103.89:/root/
```

### 2. 运行部署脚本

```bash
# SSH 到服务器
ssh root@47.236.103.89

# 修改脚本中的邮箱地址（用于 SSL 证书通知）
nano deploy-wildtrip.sh
# 找到这行：--email your-email@example.com
# 改成你的邮箱

# 执行部署
chmod +x deploy-wildtrip.sh
./deploy-wildtrip.sh
```

### 3. 配置 Flask 后端自动启动

```bash
# 还在服务器上
# 安装 Gunicorn（如果没有）
pip3 install gunicorn

# 部署 systemd 服务
cp wildtrip-backend.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable wildtrip-backend
systemctl start wildtrip-backend

# 检查状态
systemctl status wildtrip-backend
```

## 验证部署

```bash
# 1. 检查 Nginx
systemctl status nginx
curl https://api.wildtrip.com.cn/health

# 2. 检查 Flask
systemctl status wildtrip-backend
curl http://127.0.0.1:5000/api/test

# 3. 检查 API
curl https://api.wildtrip.com.cn/api/test

# 4. 查看日志
tail -f /var/log/nginx/wildtrip_error.log
tail -f /var/log/wildtrip-backend.log
```

## 常见问题

### SSL 证书申请失败？
- 确保域名 DNS 已解析到服务器 IP
- 检查防火墙：`ufw allow 80,443/tcp`
- 手动申请：`certbot certonly --standalone -d api.wildtrip.com.cn`

### Flask 启动失败？
- 检查端口占用：`lsof -i :5000`
- 检查代码路径：`ls /root/wildtrip-backend/app.py`
- 查看错误日志：`journalctl -u wildtrip-backend -n 50`

### 小程序请求失败？
- 确认域名解析：`ping api.wildtrip.com.cn`
- 测试 HTTPS：`curl -v https://api.wildtrip.com.cn/api/test`
- 检查微信小程序服务器域名配置

## 小程序配置

在微信公众平台 → 开发 → 开发管理 → 服务器域名，添加：

**request 合法域名：**
```
https://api.wildtrip.com.cn
```

## 目录结构

```
/root/wildtrip-backend/     # Flask 后端代码
/etc/nginx/sites-available/wildtrip   # Nginx 配置
/etc/systemd/system/wildtrip-backend.service  # 服务配置
/var/log/nginx/wildtrip_*.log   # Nginx 日志
/var/log/wildtrip-backend.log   # Flask 日志
/etc/letsencrypt/live/api.wildtrip.com.cn/  # SSL 证书
```

## 日常维护

```bash
# 重启服务
systemctl restart wildtrip-backend
systemctl restart nginx

# 查看日志
journalctl -u wildtrip-backend -f
tail -f /var/log/nginx/wildtrip_error.log

# 更新代码
cd /root/wildtrip-backend
git pull
systemctl restart wildtrip-backend

# 续期 SSL（自动，也可手动）
certbot renew
```

## 安全建议

1. **防火墙**：只开放 80, 443, 22 端口
2. **SSH**：禁用密码登录，只用密钥
3. **Flask**：不要用 root 运行（改 systemd 的 User）
4. **日志**：定期清理旧日志

---

搞定后，小程序就可以通过 `https://api.wildtrip.com.cn/api/xxx` 访问了 🎉
