# 🌴 野游记 WildTrip - Web前端

## 🚀 快速启动

### 1. 启动后端服务
```bash
cd /root/clawd/wildtrip/backend
screen -dmS wildtrip-backend bash -c "python3 app.py 2>&1 | tee logs/server.log"
```

### 2. 启动前端服务
```bash
cd /root/clawd/wildtrip/web
python3 -m http.server 8080
```

### 3. 访问地址
- 本地访问: http://localhost:8080
- 远程访问: http://<服务器IP>:8080

## 📁 文件结构

```
web/
├── index.html          # 主页面（UI界面）
├── app.js             # 前端逻辑（API调用）
├── README.md          # 使用说明
└── start.sh           # 启动脚本
```

## 🎨 技术栈

- **UI框架**: Tailwind CSS (CDN)
- **字体**: Google Fonts (Inter)
- **API通信**: Fetch API
- **Markdown渲染**: 自定义轻量级转换器

## ⚙️ 配置说明

### API地址配置
编辑 `app.js` 文件第3行：
```javascript
const API_BASE = 'http://localhost:5000/api';
```

如果后端部署在其他地址，修改为实际地址。

### CORS配置
如果遇到跨域问题，需要在后端 `app.py` 中启用CORS：
```python
from flask_cors import CORS
CORS(app)
```

## 🎯 功能特性

✅ **响应式设计** - 支持手机/平板/电脑
✅ **实时生成** - 轮询任务状态，显示进度
✅ **Markdown渲染** - 格式化显示攻略内容
✅ **一键复制** - 复制攻略到剪贴板
✅ **模式选择** - 完整攻略/只推酒店/只推美食

## 📊 页面流程

1. 用户输入旅行需求
2. 选择生成模式（full/hotel/food）
3. 提交表单，创建生成任务
4. 轮询任务状态（每2秒）
5. 显示生成进度（0% → 100%）
6. 完成后展示攻略内容
7. 支持复制或重新生成

## 🐛 常见问题

### Q: 页面空白？
A: 检查浏览器控制台（F12），查看是否有JS错误或API连接失败。

### Q: 生成超时？
A: 检查后端服务是否正常运行：
```bash
ps aux | grep "python.*app.py"
tail -f backend/logs/server.log
```

### Q: 跨域错误？
A: 后端需要启用CORS支持（见上方配置说明）。

### Q: 样式错乱？
A: 确保有网络连接，Tailwind CSS从CDN加载。

## 🔧 开发调试

### 查看后端日志
```bash
tail -f /root/clawd/wildtrip/backend/logs/server.log
```

### 查看前端服务状态
```bash
ps aux | grep "python.*http.server"
```

### 重启服务
```bash
# 杀掉旧进程
pkill -f "python.*http.server"
pkill -f "python.*app.py"

# 重新启动
cd /root/clawd/wildtrip
bash web/start.sh
```

## 📈 下一步优化

- [ ] 添加WebSocket实时推送（替代轮询）
- [ ] 优化Markdown渲染（表格、代码块）
- [ ] 添加攻略收藏功能
- [ ] 用户登录系统
- [ ] SEO优化（SSR）
- [ ] 历史记录查询
- [ ] 分享功能（生成短链接）

## 💡 生产环境部署

### 使用Nginx反向代理
```nginx
server {
    listen 80;
    server_name wildtrip.example.com;
    
    location / {
        root /root/clawd/wildtrip/web;
        index index.html;
    }
    
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 使用PM2管理进程
```bash
# 安装PM2
npm install -g pm2

# 启动后端
pm2 start backend/app.py --name wildtrip-backend --interpreter python3

# 查看状态
pm2 status
pm2 logs wildtrip-backend
```

## 📧 反馈与支持

遇到问题或有建议？联系开发团队：
- 微信：添加老韩
- Email: support@wildtrip.ai
