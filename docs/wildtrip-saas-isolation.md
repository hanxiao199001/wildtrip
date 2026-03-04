# 野游记 vs SaaS 客服 - 功能隔离设计

## 📋 背景

野游记项目包含两个核心功能：
1. **野游记主功能** - 生成旅游攻略（长文本，4000+字）
2. **SaaS 客服** - 酒店客服对话（短文本，100-200字）

两者共用基础设施（API、数据库、部署），但需要逻辑隔离，避免混淆。

---

## 🎯 隔离策略

### 1. **通过 mode 参数隔离**

所有 AI 调用都通过 `mode` 参数区分场景：

```python
from services.ai_engine import AIEngine

ai = AIEngine()

# 野游记攻略生成
ai.generate(prompt, query, mode='full')    # 完整攻略
ai.generate(prompt, query, mode='hotel')   # 酒店推荐
ai.generate(prompt, query, mode='food')    # 美食推荐
ai.generate(prompt, query, mode='history') # 历史路线

# SaaS 客服对话
ai.generate(prompt, query, mode='chat')    # 酒店客服
```

### 2. **独立的 Prompt 模板**

| 功能 | Prompt 模板文件 | 特点 |
|------|----------------|------|
| 野游记攻略 | `prompts/wildtrip_prompt.py` | 4000+字长文本，Markdown格式 |
| SaaS 客服 | `saas/ai/hotel_qa_engine.py` | 100-200字短文本，自然对话 |

**示例：**

```python
# 野游记
from prompts.wildtrip_prompt import build_wildtrip_prompt
prompt = build_wildtrip_prompt(query, mode='full')

# SaaS 客服
from saas.ai.hotel_qa_engine import HotelQAEngine
engine = HotelQAEngine(hotel_id, hotel_name)
prompt = engine._build_prompt(question, context, intent, hotel_kb)
```

### 3. **独立的数据库表**

| 功能 | 数据表 | 用途 |
|------|--------|------|
| 野游记 | `guides` | 存储生成的攻略 |
| 野游记 | `rag_guides` (ChromaDB) | 攻略向量库 |
| SaaS 客服 | `hotels` | 酒店信息 |
| SaaS 客服 | `conversations` | 对话记录 |
| SaaS 客服 | `hotel_knowledge` (ChromaDB) | 酒店知识库 |

**ChromaDB Collection 隔离：**
```python
# 野游记攻略库
rag_guides = chroma.get_collection("rag_guides")

# SaaS 酒店知识库
hotel_knowledge = chroma.get_collection("hotel_knowledge")
```

### 4. **RAG 检索隔离**

- **野游记（mode != 'chat'）**：检索 `rag_guides` 攻略库
- **SaaS 客服（mode == 'chat'）**：**不检索攻略库**，只用酒店知识库

```python
# services/ai_engine.py

if mode == 'chat':
    # SaaS 客服：不检索攻略库，避免混淆
    rag_context = None
else:
    # 野游记：检索攻略库
    rag_context = self._retrieve_relevant_guides(query, mode)
```

### 5. **生成参数隔离**

不同 mode 使用不同的 AI 生成参数：

| 参数 | 野游记攻略 | SaaS 客服 |
|------|-----------|----------|
| `temperature` | 0.9（高创意） | 0.7（稳定） |
| `max_tokens` | 4000（长文本） | 500（短回复） |
| `RAG` | ✅ 检索攻略库 | ❌ 不检索 |

---

## 🛡️ 隔离保障

### ✅ 代码层隔离
- 独立的目录：`/backend/saas/`
- 独立的模块：`saas.ai.hotel_qa_engine`
- 明确的 mode 参数：`chat`

### ✅ 数据层隔离
- 独立的数据库表
- 独立的 ChromaDB Collection
- mode='chat' 时不检索攻略库

### ✅ 配置层隔离
- 共用 API Key（成本低）
- 但通过 mode 区分场景

---

## 📊 对比总结

| 维度 | 野游记攻略 | SaaS 客服 |
|------|-----------|----------|
| **场景** | 旅游规划 | 酒店咨询 |
| **输出** | 4000+字攻略 | 100-200字对话 |
| **Mode** | full/hotel/food/history | **chat** |
| **RAG** | ✅ 检索攻略库 | ❌ 不检索 |
| **知识库** | rag_guides (攻略) | hotel_knowledge (FAQ) |
| **Prompt** | wildtrip_prompt.py | hotel_qa_engine.py |
| **数据表** | guides | conversations |
| **max_tokens** | 4000 | 500 |
| **temperature** | 0.9 | 0.7 |

---

## 🔧 使用示例

### 野游记攻略生成

```python
from prompts.wildtrip_prompt import build_wildtrip_prompt
from services.ai_engine import AIEngine

query = "给我规划一个海口3天2晚攻略"
prompt = build_wildtrip_prompt(query, mode='full')

ai = AIEngine()
guide = ai.generate(prompt, query, mode='full')  # mode='full'
```

### SaaS 客服对话

```python
from saas.ai.hotel_qa_engine import HotelQAEngine

engine = HotelQAEngine(hotel_id="hotel_001", hotel_name="海边小筑")
reply = engine.answer_question(
    question="你们能带宠物吗？",
    context="",
    intent="PET",
    hotel_kb=DEMO_HOTEL_KB
)
# 内部调用：ai.generate(prompt, question, mode='chat')
```

---

## ✅ 为什么不完全分开项目？

### 优势
1. **共用基础设施** - 同一个 API Key，同一个部署
2. **成本低** - 不需要额外服务器和配置
3. **代码复用** - AI 引擎、RAG 引擎复用
4. **维护简单** - 统一的依赖管理

### 风险控制
1. **mode 参数强隔离** - 代码层保证不混淆
2. **独立的数据表** - 数据层完全隔离
3. **明确的文档** - 开发者清楚区别
4. **测试覆盖** - 确保两种模式都正常工作

---

## 🚀 后续优化（如果需要）

如果未来业务增长，SaaS 客服需要独立部署，可以：

1. **拆分为独立服务**
   ```
   wildtrip-guide/      # 野游记攻略
   wildtrip-saas/       # SaaS 客服
   wildtrip-common/     # 共用组件
   ```

2. **独立的 API Key**（如果成本考虑）

3. **独立的数据库**（如果性能考虑）

但当前阶段，**在同一项目内通过 mode 隔离是最优方案** ✅

---

## 📝 总结

- ✅ **当前方案**：同一项目，通过 `mode='chat'` 隔离
- ✅ **隔离保障**：代码、数据、配置三层隔离
- ✅ **成本低**：共用 API 和基础设施
- ✅ **易维护**：统一的代码库和部署

**不会混淆** 🎯
