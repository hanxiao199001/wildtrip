# 野游记 SaaS - 通义千问配置指南

## 📋 配置通义千问 API

### 方法1：自动配置（推荐）

```bash
cd /root/clawd/wildtrip-existing/backend
./setup_qwen.sh
```

按提示输入：
1. 通义千问 API Key
2. 选择模型（推荐 qwen-plus）
3. 是否立即测试

---

### 方法2：手动配置

#### 1. 获取 API Key

访问 https://dashscope.console.aliyun.com/

1. 登录阿里云账号
2. 进入 DashScope 控制台
3. 创建 API Key
4. 复制 API Key（格式：`sk-xxxxxxxxxxxxxxxx`）

#### 2. 配置环境变量

**选项A：创建 `.env` 文件**（推荐）

```bash
cd /root/clawd/wildtrip-existing/backend
cat > .env << EOF
AI_API_KEY=sk-xxxxxxxxxxxxxxxx
AI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AI_MODEL=qwen-plus
EOF
```

**选项B：临时环境变量**（测试用）

```bash
export AI_API_KEY="sk-xxxxxxxxxxxxxxxx"
export AI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export AI_MODEL="qwen-plus"
```

**选项C：永久环境变量**

```bash
echo 'export AI_API_KEY="sk-xxxxxxxxxxxxxxxx"' >> ~/.bashrc
echo 'export AI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"' >> ~/.bashrc
echo 'export AI_MODEL="qwen-plus"' >> ~/.bashrc
source ~/.bashrc
```

#### 3. 测试 API

```bash
cd /root/clawd/wildtrip-existing/backend

# 加载环境变量（如果用的是 .env 文件）
export $(cat .env | grep -v '^#' | xargs)

# 测试 API
python3 saas/test_qwen_api.py
```

成功输出示例：
```
✅ API 调用成功！

回复内容：
可以的！我们欢迎10kg以下的小型犬和猫咪...

🎉 通义千问 API 配置正确，可以正常使用！
```

---

## 🤖 模型选择

| 模型 | 价格 | 特点 | 适用场景 |
|------|------|------|---------|
| **qwen-turbo** | ¥0.3/百万tokens | 快速、便宜 | 测试、简单问答 |
| **qwen-plus** | ¥0.8/百万tokens | **推荐**、性价比高 | 生产环境、客服对话 |
| **qwen-max** | ¥20/百万tokens | 最强、最贵 | 复杂推理、高质量内容 |

**建议：** 
- 测试阶段用 `qwen-turbo`
- 正式上线用 `qwen-plus`（成本约 ¥0.008/次对话）

---

## 🧪 测试对话功能

### 测试1：简单 API 调用

```bash
cd /root/clawd/wildtrip-existing/backend
python3 saas/test_qwen_api.py
```

### 测试2：交互式对话

```bash
python3 saas/test_conversation.py
```

输入问题测试：
```
👤 客人: 你们能带狗吗？
🤖 AI助手: 可以的！我们欢迎10kg以下的小型犬...
```

### 测试3：批量问题测试

```bash
python3 saas/test_conversation.py batch
```

自动测试 7 个常见问题，验证 AI 回复质量。

---

## ⚠️ 常见问题

### 1. API 调用失败

**错误：** `Invalid API Key`

**解决：**
- 检查 API Key 是否正确
- 确认 API Key 有余额
- 访问 https://dashscope.console.aliyun.com/ 充值

---

### 2. 模块导入错误

**错误：** `ModuleNotFoundError: No module named 'openai'`

**解决：**
```bash
pip3 install openai loguru
```

---

### 3. 环境变量未生效

**错误：** `⚠️ AI_API_KEY未配置，将使用Mock数据`

**解决：**
```bash
# 检查环境变量
echo $AI_API_KEY

# 如果为空，重新加载
export $(cat .env | grep -v '^#' | xargs)

# 或者
source ~/.bashrc
```

---

### 4. 回复内容不符合预期

**问题：** AI 回复太长 / 太短 / 不够友好

**解决：** 优化 Prompt 模板

编辑 `saas/ai/hotel_qa_engine.py`，调整 `_build_prompt()` 方法：

```python
system_prompt = f"""
你是"{self.hotel_name}"的AI客服助手。

回复要求：
- 简洁明了，控制在100字以内
- 语气友好自然，像朋友聊天
- 用 emoji 增加亲和力（适度）
"""
```

---

## 📊 成本估算

### 单次对话成本（qwen-plus）

- **输入 tokens**：~500（Prompt + 历史）
- **输出 tokens**：~200（AI 回复）
- **总 tokens**：~700
- **成本**：700 / 1,000,000 × ¥0.8 = **¥0.00056**

**每天 1000 次对话 = ¥0.56**

极低成本 💰

---

## 🚀 快速启动

完整启动流程：

```bash
# 1. 进入项目目录
cd /root/clawd/wildtrip-existing/backend

# 2. 配置通义千问（首次运行）
./setup_qwen.sh

# 3. 测试 API
python3 saas/test_qwen_api.py

# 4. 交互式对话测试
python3 saas/test_conversation.py

# 5. 启动微信 Webhook（后续步骤）
python3 saas/webhook/wechat_handler.py
```

---

## 📝 下一步

配置完成后，可以：

1. **优化 Prompt** - 调整回复风格和长度
2. **添加知识库** - 录入酒店 FAQ 和周边玩法
3. **接入微信** - 配置公众号 webhook
4. **测试真实场景** - 邀请首批酒店试用

完整开发计划见 `docs/wildtrip-saas-mvp-progress.md`
