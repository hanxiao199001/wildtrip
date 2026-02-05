# 🌐 野游记 WildTrip - 访问指南

## 🎯 立即体验

### 本地访问
```
http://localhost:8080
```

### 远程访问
```
http://47.82.159.93:8080
```

⚠️ **注意**: 如果远程访问不通，需要在阿里云控制台开放端口 8080

## 🔧 阿里云端口开放步骤

1. 登录阿里云控制台
2. 进入 ECS 实例管理
3. 找到当前服务器（IP: 47.82.159.93）
4. 点击 "安全组配置"
5. 添加规则：
   - 端口范围: 8080/8080
   - 授权对象: 0.0.0.0/0
   - 协议: TCP
6. 保存生效

或者使用 **iptables**（临时开放）:
```bash
sudo iptables -I INPUT -p tcp --dport 8080 -j ACCEPT
```

## 📱 测试流程

### 1. 打开浏览器
访问: http://47.82.159.93:8080

### 2. 输入测试查询
```
海口3天亲子游，预算5000，带6岁小孩
```

### 3. 选择模式
- 🗺️ 完整攻略（推荐）
- 🏨 只推酒店
- 🍜 只推美食

### 4. 点击生成按钮
等待AI生成（约30-90秒）

### 5. 查看结果
- 完整的野路子攻略
- 带美团返现链接
- 支持一键复制

## 🔍 检查服务状态

### 后端服务（Port 5000）
```bash
ps aux | grep "python.*app.py"
curl http://localhost:5000/api/health
```

### 前端服务（Port 8080）
```bash
ps aux | grep "python.*http.server"
curl -I http://localhost:8080
```

### 查看日志
```bash
# 后端日志
tail -f /root/clawd/wildtrip/backend/logs/server.log

# 前端日志（浏览器控制台）
按F12打开开发者工具
```

## 🛠️ 重启服务

### 一键重启
```bash
cd /root/clawd/wildtrip/web
bash start.sh
```

### 手动重启

#### 停止所有服务
```bash
pkill -f "python.*app.py"
pkill -f "python.*http.server"
```

#### 启动后端
```bash
cd /root/clawd/wildtrip/backend
screen -dmS wildtrip-backend bash -c "python3 app.py 2>&1 | tee logs/server.log"
```

#### 启动前端
```bash
cd /root/clawd/wildtrip/web
python3 -m http.server 8080 &
```

## 📊 功能演示

### ✅ 已实现功能
- [x] 用户输入旅行需求
- [x] 三种生成模式切换
- [x] 实时显示生成进度
- [x] Markdown格式化显示
- [x] 美团返现链接自动嵌入
- [x] 一键复制攻略内容
- [x] 响应式设计（手机/电脑）

### 🚀 待优化功能
- [ ] WebSocket实时推送（替代轮询）
- [ ] 用户登录系统
- [ ] 攻略收藏功能
- [ ] 历史记录查询
- [ ] 分享生成短链接
- [ ] SEO优化（SSR）
- [ ] 表格和代码块渲染优化

## 🐞 问题排查

### 问题1: 页面无法访问
**症状**: 浏览器显示"无法连接"

**解决方案**:
1. 检查服务是否运行: `ps aux | grep http.server`
2. 检查端口监听: `netstat -tlnp | grep 8080`
3. 检查防火墙: `sudo iptables -L -n | grep 8080`
4. 开放端口: `sudo iptables -I INPUT -p tcp --dport 8080 -j ACCEPT`

### 问题2: API调用失败
**症状**: 控制台显示CORS错误或连接失败

**解决方案**:
1. 检查后端服务: `curl http://localhost:5000/api/health`
2. 启用CORS支持（后端 `app.py`）:
```python
from flask_cors import CORS
CORS(app)
```
3. 重启后端服务

### 问题3: 生成超时
**症状**: 进度卡在某个百分比不动

**解决方案**:
1. 查看后端日志: `tail -50 backend/logs/server.log`
2. 检查DeepSeek API配额
3. 检查网络连接
4. 延长前端超时时间（`app.js` 第60行）

### 问题4: 样式丢失
**症状**: 页面显示但没有样式

**解决方案**:
1. 检查网络连接（Tailwind CSS从CDN加载）
2. 浏览器控制台查看加载失败的资源
3. 考虑使用本地Tailwind CSS

## 📞 技术支持

遇到其他问题？
- 查看日志: `tail -f backend/logs/server.log`
- 联系开发团队
- 提交Issue

---

**🎉 享受你的野游记体验！**
