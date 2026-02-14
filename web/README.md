# 野游记 WildTrip - Web 前端

## 快速启动

### 1. 启动后端服务
```bash
cd backend
python3 app.py
# 服务运行在 http://localhost:5000
```

### 2. 启动前端服务
```bash
cd web
python3 -m http.server 8080
```

### 3. 访问地址
- 本地访问: http://localhost:8080
- 远程访问: http://<服务器IP>:8080

> 如果远程访问不通，需要在阿里云安全组中开放 8080 端口（TCP 协议，授权 0.0.0.0/0）。
> 临时开放: `sudo iptables -I INPUT -p tcp --dport 8080 -j ACCEPT`

## 文件结构

```
web/
├── index.html              # 主页面
├── app.js                  # 前端逻辑（API 调用、Markdown 渲染）
├── start.sh                # 一键启动脚本
├── analytics.html          # 数据统计
├── robots.txt              # SEO robots
├── sitemap.xml             # SEO sitemap
├── itinerary-template.html # 攻略模板
├── guides/                 # AI 生成的静态攻略页面
│   └── index.html          # 攻略目录
└── public/                 # 静态资源 (images, css, js)
```

## 技术栈

- **UI 框架**: Tailwind CSS (CDN)
- **字体**: Google Fonts (Inter)
- **API 通信**: Fetch API + WebSocket (Socket.IO)
- **Markdown 渲染**: 自定义轻量级转换器

## 配置说明

### API 地址
编辑 `app.js` 中的 API 基础地址：
```javascript
const API_BASE = 'http://localhost:5000/api';
```

### CORS
如遇跨域问题，在后端 `app.py` 中启用：
```python
from flask_cors import CORS
CORS(app)
```

## 功能特性

- 响应式设计（手机 / 平板 / 电脑）
- 三种生成模式（完整攻略 / 只推酒店 / 只推美食）
- 实时进度显示（WebSocket + 轮询降级）
- Markdown 格式化显示攻略
- 美团返现链接自动嵌入
- 一键复制攻略内容

## 页面流程

1. 用户输入旅行需求（目的地、天数、预算、偏好）
2. 选择生成模式（full / hotel / food）
3. 提交请求，创建异步生成任务
4. WebSocket / 轮询显示实时进度（0% → 100%）
5. 完成后展示格式化攻略
6. 支持复制、分享、重新生成

## 服务检查与重启

```bash
# 检查后端
ps aux | grep "python.*app.py"
curl http://localhost:5000/api/health

# 检查前端
ps aux | grep "python.*http.server"
curl -I http://localhost:8080

# 查看日志
tail -f backend/logs/wildtrip.log

# 重启所有服务
pkill -f "python.*app.py"
pkill -f "python.*http.server"
bash web/start.sh
```

## 生产环境部署

### Nginx 反向代理
```nginx
server {
    listen 80;
    server_name wildtrip.example.com;

    location / {
        root /path/to/wildtrip/web;
        index index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000/socket.io/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 常见问题

| 问题 | 排查方法 |
|------|---------|
| 页面空白 | F12 控制台查看 JS 错误或 API 连接失败 |
| 生成超时 | 检查后端日志、DeepSeek API 配额、网络连接 |
| 跨域错误 | 后端启用 CORS（见上方配置） |
| 样式缺失 | 检查网络（Tailwind CSS 从 CDN 加载） |
