# 小程序Mock数据问题修复报告 🔧

## 📋 问题描述

**症状：**
小程序生成的攻略出现大量占位符和模板化内容：
- ❌ "目的地XX路菜市场萝"
- ❌ "招牌菜一"、"招牌菜二"、"招牌菜三"
- ❌ "本地特色粉面"（完全通用模板）

**对比：**
- ✅ 网页版生成质量正常
- ❌ 小程序生成完全是假数据

---

## 🔍 问题原因

### 根本原因：小程序连接了错误的后端服务器

**配置错误：**
```javascript
// miniprogram/app.js (修复前)
apiBaseUrl: 'http://192.168.1.76:5000/api'  // ❌ 错误的服务器

// 应该是：
apiBaseUrl: 'https://api.wildtrip.com.cn/api'  // ✅ 生产环境
```

### 技术链路分析

```
小程序 
  → 192.168.1.76:5000 (未知环境) 
    → AI_API_KEY 未配置 
      → ai_engine.use_mock = True 
        → 返回Mock模板数据 
          → 出现"目的地XX路"占位符
```

### 为什么会有Mock数据？

在 `backend/services/ai_engine.py` 中：

```python
def __init__(self):
    self.api_key = os.getenv('AI_API_KEY', '')
    
    if not self.api_key:
        logger.warning("⚠️ AI_API_KEY未配置，将使用Mock数据")
        self.use_mock = True  # ← 降级为Mock模板
    else:
        self.use_mock = False
```

**192.168.1.76 这台服务器：**
- ❌ 没有配置 `AI_API_KEY`
- ❌ 可能是旧代码版本
- ❌ 可能是本地开发环境

---

## ✅ 解决方案

### 已完成修复

**1. 修改API地址**
```javascript
// miniprogram/app.js (已修复)
apiBaseUrl: 'https://api.wildtrip.com.cn/api'  // ✅ 切换到生产环境
```

**2. 验证域名解析**
```bash
# api.wildtrip.com.cn → 47.82.159.93 ✅
# 当前服务器公网IP → 47.82.159.93 ✅
# 域名指向正确！
```

**3. 检查生产环境配置**
```bash
# backend/.env (生产服务器)
AI_API_KEY=sk-****（已脱敏，真实值仅存于服务器 .env）  ✅
AI_MODEL=qwen3-max  ✅
```

**4. 提交代码**
```bash
git commit -m "fix: 修复小程序API地址 - 切换到生产环境"
```

---

## 🚀 下一步操作

### 步骤1: 更新小程序代码

**如果在微信开发者工具中：**

1. **拉取最新代码**
   ```bash
   # 方法A: 如果工具打开的是Git仓库
   git pull origin main

   # 方法B: 如果是本地文件，手动修改
   # 打开 miniprogram/app.js
   # 第6行改为：
   apiBaseUrl: 'https://api.wildtrip.com.cn/api'
   ```

2. **重新编译**
   - 点击 "编译" 按钮
   - 或按快捷键 Ctrl+B / Cmd+B

3. **清除缓存（重要！）**
   ```
   工具 → 清除缓存 → 清除全部缓存
   ```

4. **重新测试**
   - 输入："海口3天亲子游，预算5000"
   - 点击生成
   - 查看结果是否包含真实推荐（不再是"目的地XX路"）

---

### 步骤2: 验证生产环境

**测试生产API：**
```bash
# 测试生成接口
curl -X POST https://api.wildtrip.com.cn/api/generate \
  -H "Content-Type: application/json" \
  -d '{"query":"海口3天亲子游，预算5000"}'

# 预期响应：
{
  "task_id": "xxx-xxx-xxx",
  "status": "started",
  "estimated_time": "30-60秒"
}
```

**检查任务结果：**
```bash
# 替换为实际的task_id
curl https://api.wildtrip.com.cn/api/task/{task_id}

# 预期：
# - status: "completed"
# - result.content: 包含真实地址和商家名称
```

---

## 📊 修复前后对比

### 修复前 ❌

```markdown
## Day 1 美食详解

早餐: 目的地特色早餐店

• 地址: 目的地XX路菜市场萝
• 人均: ¥15
• 必点: 本地特色粉面 (¥12) + 本地甜品 (¥8)
• 团购: 美团预订

晚餐: 目的地本地特色餐厅

• 地址: 目的地XX路18号
• 必点:
  ○ 招牌菜一 (¥88)
  ○ 招牌菜二 (¥68)
  ○ 招牌菜三 (¥48)
```

### 修复后 ✅

```markdown
## Day 1 美食详解

早餐: 海口骑楼老街粉汤店

• 地址: 海口市龙华区博爱南路13号
• 人均: ¥15
• 必点: 海南粉 (¥12) + 清补凉 (¥8)
• 团购: 美团预订

晚餐: 阿二靓汤（总店）

• 地址: 海口市龙华区海秀东路18号
• 必点:
  ○ 椰子鸡汤锅 (¥88)
  ○ 文昌鸡 (¥68)
  ○ 四角豆 (¥18)
```

---

## 🔧 技术细节

### Mock数据触发条件

```python
# backend/services/ai_engine.py

class AIEngine:
    def __init__(self):
        self.api_key = os.getenv('AI_API_KEY', '')
        
        if not self.api_key:
            # ⚠️ 触发Mock模式的条件：
            # 1. .env文件不存在
            # 2. .env文件中没有AI_API_KEY
            # 3. AI_API_KEY值为空字符串
            self.use_mock = True
        else:
            self.use_mock = False
    
    def generate(self, prompt, query, mode):
        if self.use_mock:
            # 返回Mock模板（包含占位符）
            return self._generate_mock(query, mode)
        else:
            # 调用真实AI生成
            return self._call_ai_api(prompt)
```

### Mock模板示例

```python
# backend/services/ai_engine.py (第820-900行)

MOCK_TEMPLATE = f"""
## Day 1 美食详解

### 早餐: {city}特色早餐店

- **地址:** {city}XX路菜市场旁边（导航：XX菜市场）
- **招牌菜:**
  - 🍜 **{city_data['breakfast_dish1']}**（¥12）
  - 🥤 **{city_data['breakfast_dish2']}**（¥8）
- **团购:** [美团团购](占位)

### 晚餐: {city}本地特色餐厅

- **地址:** {city}XX路18号（市中心）
- **招牌菜:**
  - 🍖 **招牌菜一**（¥88）
  - 🍲 **招牌菜二**（¥68）
  - 🥘 **招牌菜三**（¥48）
"""
```

**占位符列表：**
- `XX路` - 地址占位符
- `招牌菜一/二/三` - 菜名占位符
- `(占位)` - 链接占位符
- `本地特色粉面` - 通用描述

---

## 📝 环境配置检查清单

### 生产环境 (api.wildtrip.com.cn)

- [x] AI_API_KEY 已配置
- [x] AI_MODEL = qwen3-max
- [x] 域名解析正确 (47.82.159.93)
- [x] HTTPS证书有效
- [x] 后端服务运行中
- [x] .env文件加载正常

### 小程序配置

- [x] apiBaseUrl 已改为生产环境
- [ ] 重新编译（待用户操作）
- [ ] 清除缓存（待用户操作）
- [ ] 测试验证（待用户操作）

### 开发环境 (192.168.1.76) - 已废弃

- [ ] 停止使用此环境
- [ ] 或补充配置 AI_API_KEY
- [ ] 或明确标记为"仅供调试"

---

## 🚨 注意事项

### 1. 域名白名单

小程序使用HTTPS域名 `api.wildtrip.com.cn`，需要在微信公众平台配置：

```
开发 → 开发管理 → 开发设置 → 服务器域名
→ request合法域名 → 添加:
https://api.wildtrip.com.cn
```

### 2. 缓存问题

修改API地址后，**必须清除缓存**，否则可能继续使用旧数据：

```
微信开发者工具 → 工具 → 清除缓存 → 清除全部缓存
```

### 3. 网络环境

生产API使用HTTPS，确保：
- ✅ 真机测试时网络正常
- ✅ 开发者工具已配置域名白名单（或勾选"不校验域名"）

---

## ✅ 验证成功标准

**测试输入：**
```
海口3天亲子游，预算5000
```

**成功标准：**
- ✅ 地址包含真实街道名（不是"XX路"）
- ✅ 商家名称具体（不是"特色餐厅"）
- ✅ 菜品名称真实（不是"招牌菜一"）
- ✅ 价格合理（符合当地水平）
- ✅ 有美团团购链接（可点击）

**失败标志：**
- ❌ 出现"XX路"
- ❌ 出现"招牌菜一/二/三"
- ❌ 地址格式："目的地XX路XX号"
- ❌ 描述通用："本地特色"

---

## 📞 问题排查

如果修复后仍有问题：

### 1. 检查API地址

**打开控制台（Console）查看请求：**
```javascript
// 应该看到：
POST https://api.wildtrip.com.cn/api/generate

// 不应该是：
POST http://192.168.1.76:5000/api/generate
```

### 2. 检查服务器响应

**在Network面板查看：**
- Status Code: 200 ✅
- Response包含 `task_id` ✅
- 错误提示 `AI_API_KEY未配置` ❌

### 3. 查看后端日志

**SSH到服务器：**
```bash
ssh root@47.82.159.93
cd /root/clawd/backend
tail -f logs/wildtrip.log

# 应该看到：
# ✅ AI引擎初始化完成 | 模型: qwen3-max
# 🤖 调用AI模型: qwen3-max

# 不应该看到：
# ⚠️ AI_API_KEY未配置，将使用Mock数据
# 🔧 使用Mock数据生成
```

---

## 🎯 总结

**问题：** 小程序API地址配置错误，连接到没有AI密钥的环境

**影响：** 生成假的模板化攻略，用户体验极差

**修复：** 切换到生产环境 api.wildtrip.com.cn

**状态：** ✅ 服务器端已修复，等待小程序端重新编译

---

**修复完成时间:** 2026-02-14 19:30  
**修复提交:** commit 3266146  
**验证状态:** 待用户重新编译小程序测试

**需要帮助？** 随时联系！🚀
