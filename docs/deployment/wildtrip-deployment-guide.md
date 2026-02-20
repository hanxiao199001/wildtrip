# Wildtrip 生产环境部署文档

**部署时间：** 2026-02-14  
**服务器：** 47.236.103.89 (阿里云 ECS)  
**域名：** api.wildtrip.com.cn  
**状态：** ✅ 已部署成功

---

## 📋 部署概览

### 服务架构
```
小程序客户端
    ↓ HTTPS
api.wildtrip.com.cn (Nginx 443)
    ↓ 反向代理
Flask 后端 (127.0.0.1:5000)
    ↓
Qwen AI + 美团返现 API
```

### 核心组件
- **后端框架：** Flask + Flask-SocketIO
- **AI 引擎：** Qwen (通义千问)
- **Web 服务器：** Nginx + SSL (Let's Encrypt)
- **进程管理：** nohup (后台运行)
- **域名解析：** api.wildtrip.com.cn → 47.236.103.89

---

## 🔧 服务器配置

### 1. Flask 后端

**代码路径：**
```bash
/root/clawd/backend/
```

**启动方式：**
```bash
cd /root/clawd/backend
nohup python3 app.py > /var/log/wildtrip-backend.log 2>&1 &
```

**检查状态：**
```bash
# 查看进程
ps aux | grep "python3 app.py"

# 查看日志
tail -f /var/log/wildtrip-backend.log

# 测试本地 API
curl http://127.0.0.1:5000/
```

**端口：** 5000 (仅监听 127.0.0.1，不对外暴露)

---

### 2. Nginx 配置

**配置文件：**
```bash
/etc/nginx/sites-available/wildtrip
```

**配置内容：**
```nginx
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
    
    location / {
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
}
```

**管理命令：**
```bash
# 测试配置
nginx -t

# 重启服务
systemctl restart nginx

# 查看状态
systemctl status nginx

# 查看日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

### 3. SSL 证书

**证书提供商：** Let's Encrypt  
**管理工具：** Certbot (snap 版本)  
**证书路径：** `/etc/letsencrypt/live/api.wildtrip.com.cn/`

**证书信息：**
- **颁发时间：** 2026-02-14
- **过期时间：** 2026-05-15 (90天)
- **邮箱：** han272624836@gmail.com

**自动续期：**
Certbot 已配置自动续期任务（cron），每天检查证书有效期。

**手动续期：**
```bash
certbot renew
systemctl reload nginx
```

**查看证书详情：**
```bash
certbot certificates
```

---

## 🌐 域名配置

**域名：** api.wildtrip.com.cn  
**DNS 记录：**
```
A 记录: api.wildtrip.com.cn → 47.236.103.89
```

**验证解析：**
```bash
ping api.wildtrip.com.cn
nslookup api.wildtrip.com.cn
```

---

## 📱 小程序配置

### API 地址
小程序代码中的 API 基础地址：
```javascript
const API_BASE = 'https://api.wildtrip.com.cn/api'
```

### 微信公众平台配置

1. **登录微信公众平台**  
   https://mp.weixin.qq.com

2. **添加服务器域名**  
   开发管理 → 服务器域名 → request合法域名
   
   添加：
   ```
   https://api.wildtrip.com.cn
   ```

3. **重新编译上传**  
   微信开发者工具 → 上传 → 提审/发布

---

## ✅ 部署验证

### 服务器端验证

**1. 测试 HTTPS 访问**
```bash
curl https://api.wildtrip.com.cn/
```
期望返回：HTML 首页

**2. 测试 API 生成**
```bash
curl -X POST https://api.wildtrip.com.cn/api/generate \
  -H "Content-Type: application/json" \
  -d '{"query":"北京2日游","mode":"full"}'
```
期望返回：
```json
{
  "status": "started",
  "task_id": "xxx",
  "estimated_time": "30-60秒"
}
```

**3. 检查服务状态**
```bash
# Flask 后端
ps aux | grep python3

# Nginx
systemctl status nginx

# 端口监听
lsof -i :5000
lsof -i :443
```

### 小程序端验证

1. **真机调试**  
   微信开发者工具 → 真机调试 → 测试生成攻略

2. **网络请求**  
   控制台查看网络请求是否成功 (200 OK)

3. **功能测试**  
   - 输入"北京2日游" → 生成完整攻略
   - 检查美团返现链接是否正常
   - 测试需求澄清功能

---

## 🔄 日常维护

### 重启服务

**重启 Flask 后端：**
```bash
# 找到进程 PID
ps aux | grep "python3 app.py"

# 杀掉进程
kill <PID>

# 重新启动
cd /root/clawd/backend
nohup python3 app.py > /var/log/wildtrip-backend.log 2>&1 &
```

**重启 Nginx：**
```bash
systemctl restart nginx
```

### 查看日志

**Flask 日志：**
```bash
tail -f /var/log/wildtrip-backend.log
```

**Nginx 访问日志：**
```bash
tail -f /var/log/nginx/access.log
```

**Nginx 错误日志：**
```bash
tail -f /var/log/nginx/error.log
```

**系统日志：**
```bash
journalctl -f
```

### 更新代码

```bash
cd /root/clawd/backend

# 备份（可选）
cp -r . ../backend-backup-$(date +%Y%m%d)

# 更新代码（git pull 或手动上传）
git pull

# 重启服务
pkill -f "python3 app.py"
nohup python3 app.py > /var/log/wildtrip-backend.log 2>&1 &
```

### 清理日志

```bash
# 清理旧日志（保留最近 7 天）
find /var/log -name "*.log" -mtime +7 -delete

# 压缩大日志
gzip /var/log/wildtrip-backend.log
```

---

## 🚨 故障排查

### 问题 1: HTTPS 访问失败

**症状：**
```bash
curl https://api.wildtrip.com.cn/
# 报错：Connection refused 或 SSL error
```

**排查步骤：**
```bash
# 1. 检查 Nginx 是否运行
systemctl status nginx

# 2. 检查 SSL 证书
certbot certificates

# 3. 检查防火墙
ufw status
ufw allow 443/tcp

# 4. 测试 Nginx 配置
nginx -t

# 5. 查看错误日志
tail -50 /var/log/nginx/error.log
```

### 问题 2: API 返回 502 Bad Gateway

**症状：**
```bash
curl https://api.wildtrip.com.cn/api/generate
# 返回 502
```

**原因：** Flask 后端未运行

**解决方案：**
```bash
# 检查 Flask 进程
ps aux | grep python3

# 重启 Flask
cd /root/clawd/backend
nohup python3 app.py > /var/log/wildtrip-backend.log 2>&1 &

# 查看启动日志
tail -f /var/log/wildtrip-backend.log
```

### 问题 3: 小程序请求失败

**症状：**  
小程序提示"网络请求失败"

**排查步骤：**
1. **检查域名白名单**  
   微信公众平台 → 服务器域名是否已添加 `https://api.wildtrip.com.cn`

2. **检查 SSL 证书**  
   小程序要求 HTTPS，证书必须有效

3. **测试服务器端 API**  
   ```bash
   curl -X POST https://api.wildtrip.com.cn/api/generate \
     -H "Content-Type: application/json" \
     -d '{"query":"测试","mode":"full"}'
   ```

4. **查看小程序控制台**  
   微信开发者工具 → Console → 查看详细错误

### 问题 4: SSL 证书过期

**症状：**
浏览器提示证书过期

**解决方案：**
```bash
# 手动续期
certbot renew

# 重启 Nginx
systemctl reload nginx

# 检查证书有效期
certbot certificates
```

---

## 📊 监控指标

### 服务健康检查

```bash
# 每 5 分钟检查一次
*/5 * * * * curl -f https://api.wildtrip.com.cn/ > /dev/null 2>&1 || systemctl restart nginx
```

### 资源使用

```bash
# 内存
free -h

# CPU
top

# 磁盘
df -h

# 网络
netstat -tulnp | grep -E '5000|443'
```

---

## 📝 部署清单

- [x] Flask 后端运行在 5000 端口
- [x] Nginx 配置 HTTPS 反向代理
- [x] SSL 证书申请并配置（Let's Encrypt）
- [x] 域名解析配置（api.wildtrip.com.cn）
- [x] 防火墙开放 80/443 端口
- [x] 小程序 API 地址更新
- [x] 微信公众平台域名白名单
- [x] 测试验证通过

---

## 🔗 相关链接

- **微信公众平台：** https://mp.weixin.qq.com
- **Let's Encrypt：** https://letsencrypt.org
- **服务器 IP：** 47.236.103.89
- **API 文档：** https://api.wildtrip.com.cn/

---

## 📞 联系方式

**运维负责人：** han272624836@gmail.com  
**部署日期：** 2026-02-14  
**最后更新：** 2026-02-14

---

**部署完成 ✅ 小程序已上线 🚀**
