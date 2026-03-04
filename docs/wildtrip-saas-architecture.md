# 野游记 B端 SaaS 技术架构设计

## 项目概述

**产品定位**：AI智能掌柜 - 为精品民宿/单体酒店提供的私域直销 SaaS 工具

**核心价值**：
- 7x24小时AI客服，自动回答客人咨询
- 智能推荐周边野路子玩法
- 促成直销预订，降低OTA佣金成本

---

## 系统架构

### 1. 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        客人端                                │
│  微信公众号 / 企业微信 (酒店官方账号)                        │
└─────────────────┬───────────────────────────────────────────┘
                  │ 发送消息
                  ↓
┌─────────────────────────────────────────────────────────────┐
│                   野游记 SaaS 后端                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  消息接收层 (Webhook)                                │   │
│  │  - 微信公众号消息接收                                │   │
│  │  - 企业微信消息接收                                  │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │  对话管理层                                          │   │
│  │  - 识别酒店ID (通过公众号/企微账号)                  │   │
│  │  - 对话上下文管理                                    │   │
│  │  - 意图识别 (咨询问题 vs 预订意图)                   │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│         ┌───────────┴──────────┬────────────────────┐       │
│         ↓                      ↓                    ↓       │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐ │
│  │ AI客服引擎  │      │ 攻略生成    │      │ 预订引导    │ │
│  │             │      │ 引擎        │      │ 模块        │ │
│  │ - 基础问答  │      │             │      │             │ │
│  │ - RAG检索   │      │ - 周边玩法  │      │ - 生成预订  │ │
│  │   酒店知识库│      │ - 路线规划  │      │   链接      │ │
│  └─────────────┘      └─────────────┘      └─────────────┘ │
│         │                      │                    │       │
│         └───────────┬──────────┴────────────────────┘       │
│                     ↓                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  AI 模型调用层                                        │   │
│  │  - DeepSeek API (主要)                               │   │
│  │  - Prompt 模板管理                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │  数据存储层                                          │   │
│  │  - ChromaDB: 酒店知识库 + 周边玩法库                 │   │
│  │  - PostgreSQL: 酒店信息、对话记录、订单统计          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                   酒店管理后台                               │
│  - 酒店信息管理                                              │
│  - 知识库录入 (常见问题、周边玩法)                            │
│  - 对话记录查看                                              │
│  - 数据统计 (咨询量、转化率)                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 核心模块设计

### 2.1 消息接收层

**技术选型**：
- 微信公众号：开发者模式 + 服务器配置
- 企业微信：应用消息 API

**实现**：
```python
# /backend/saas/webhook/wechat_handler.py

from flask import Flask, request
import hashlib

app = Flask(__name__)

@app.route('/wechat/callback/<hotel_id>', methods=['GET', 'POST'])
def wechat_callback(hotel_id):
    """
    微信公众号消息回调
    每个酒店有独立的 webhook URL
    """
    if request.method == 'GET':
        # 微信服务器验证
        return verify_wechat_signature(request.args)
    
    elif request.method == 'POST':
        # 接收用户消息
        msg = parse_wechat_message(request.data)
        
        # 识别酒店
        hotel = get_hotel_by_id(hotel_id)
        
        # 调用对话管理层
        reply = handle_conversation(hotel, msg)
        
        # 返回 XML 格式回复
        return format_wechat_reply(reply)
```

**URL 格式**：
```
https://api.wildtrip.com/saas/wechat/callback/{hotel_id}
```

每个酒店独立的 webhook，方便追踪和管理。

---

### 2.2 对话管理层

**核心功能**：
1. 识别用户意图
2. 管理多轮对话上下文
3. 路由到不同的处理引擎

**意图分类**：
```python
# /backend/saas/conversation/intent_classifier.py

class IntentClassifier:
    """
    用户意图分类
    """
    INTENTS = {
        'BASIC_QA': [
            '有儿童拖鞋吗',
            '能带宠物吗',
            '早餐几点',
            '怎么去你们那',
        ],
        'ACTIVITY_REQUEST': [
            '周边有什么好玩的',
            '附近景点推荐',
            '带孩子去哪玩',
        ],
        'BOOKING_INTENT': [
            '预订',
            '订房',
            '多少钱',
            '有房吗',
        ]
    }
    
    def classify(self, user_message):
        """
        简单关键词匹配 + AI 意图识别
        """
        # 先用关键词快速匹配
        for intent, keywords in self.INTENTS.items():
            if any(kw in user_message for kw in keywords):
                return intent
        
        # 如果关键词匹配不到，调用 AI 识别
        return self.ai_classify(user_message)
```

**对话上下文**：
```python
# /backend/saas/conversation/context_manager.py

class ConversationContext:
    """
    管理单个用户的对话上下文
    """
    def __init__(self, hotel_id, user_id):
        self.hotel_id = hotel_id
        self.user_id = user_id
        self.messages = []  # 历史消息
        self.intent = None  # 当前意图
        self.state = {}  # 状态变量
    
    def add_message(self, role, content):
        self.messages.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now()
        })
    
    def get_context_for_ai(self):
        """
        返回给 AI 的上下文（最近 5 条消息）
        """
        return self.messages[-5:]
```

---

### 2.3 AI客服引擎

**核心能力**：
1. 回答酒店基础问题
2. RAG检索酒店知识库
3. 自然对话能力

**知识库设计**：
```python
# 酒店知识库数据结构
{
    "hotel_id": "hotel_001",
    "hotel_name": "海边小筑民宿",
    "knowledge_base": [
        {
            "category": "基础设施",
            "qa_pairs": [
                {
                    "question": "有儿童拖鞋吗",
                    "answer": "有的！我们准备了儿童拖鞋、儿童牙刷、儿童浴袍，2-12岁的小朋友都能用。"
                },
                {
                    "question": "能带宠物吗",
                    "answer": "可以带10kg以下的小型犬，需要提前告知我们准备宠物垫。猫咪也欢迎～"
                }
            ]
        },
        {
            "category": "房间信息",
            "qa_pairs": [
                {
                    "question": "早餐几点",
                    "answer": "早餐时间是 7:30-9:30，我们家阿姨现做的海南粉和鸡蛋，还有自制的椰子饼。"
                }
            ]
        }
    ]
}
```

**RAG 检索实现**：
```python
# /backend/saas/ai/qa_engine.py

from services.rag_engine import get_rag_engine

class HotelQAEngine:
    def __init__(self, hotel_id):
        self.hotel_id = hotel_id
        self.rag = get_rag_engine()
    
    def answer_question(self, question, context):
        """
        回答用户问题
        """
        # 1. RAG 检索酒店知识库
        rag_results = self.rag.search(
            query=question,
            filter={"hotel_id": self.hotel_id},
            n_results=3
        )
        
        # 2. 构建 Prompt
        prompt = f"""
你是"{self.hotel_name}"的AI客服助手。

用户咨询：{question}

相关知识库：
{rag_results}

对话历史：
{context}

请用友好、专业的语气回答用户问题。如果知识库中没有相关信息，诚实告知用户"这个问题我需要帮您确认一下，稍后人工客服会联系您"。
"""
        
        # 3. 调用 AI 生成回复
        from services.ai_engine import AIEngine
        ai = AIEngine()
        reply = ai.generate(prompt, question)
        
        return reply
```

---

### 2.4 攻略生成引擎

**核心能力**：
- 基于酒店地理位置生成周边玩法
- 复用野游记现有的攻略生成能力

**实现**：
```python
# /backend/saas/ai/activity_engine.py

class ActivityRecommendationEngine:
    def __init__(self, hotel):
        self.hotel = hotel
        self.location = hotel.location  # {"lat": 19.xx, "lng": 110.xx}
    
    def recommend_activities(self, user_request, context):
        """
        推荐周边玩法
        """
        # 1. 检索周边玩法库
        activities = self.search_nearby_activities(self.location)
        
        # 2. 构建 Prompt
        prompt = f"""
你是"{self.hotel.name}"的AI助手。客人问："{user_request}"

酒店位置：{self.hotel.address}
周边资源：
{activities}

请生成一个"野路子"风格的周边玩法推荐，要求：
1. 避开网红景点，推荐小众、本地人才知道的地方
2. 具体到时间和路线：比如"下午3点办入住，4点可以..."
3. 情绪价值拉满，让客人觉得这趟超值
4. 控制在200字以内

最后引导客人预订："看起来不错的话，可以直接在我们的小程序预订哦～"
"""
        
        # 3. AI 生成
        from services.ai_engine import AIEngine
        ai = AIEngine()
        reply = ai.generate(prompt, user_request)
        
        return reply
    
    def search_nearby_activities(self, location):
        """
        检索周边玩法（从 RAG 或数据库）
        """
        # 可以复用野游记的 POI 数据库
        # 也可以让酒店老板自己录入"独家玩法"
        pass
```

---

### 2.5 预订引导模块

**功能**：
- 识别预订意图
- 生成预订链接（小程序/企微）
- 发送优惠券/红包

**实现**：
```python
# /backend/saas/booking/guide.py

class BookingGuide:
    def generate_booking_link(self, hotel, room_type=None):
        """
        生成预订链接
        """
        # 选项1：跳转酒店自己的小程序
        miniprogram_link = {
            "appid": hotel.miniprogram_appid,
            "page": f"pages/booking?hotel_id={hotel.id}&room={room_type}"
        }
        
        # 选项2：生成企微专属优惠码
        coupon_code = self.generate_coupon(hotel)
        
        reply = f"""
我们的{room_type or '房间'}目前有房哦～

💰 价格：¥{hotel.price}/晚
🎁 野游记专属优惠：立减50元（优惠码：{coupon_code}）

点击预订 → [小程序卡片]

或者加我们管家企微，发送优惠码领取红包～
"""
        return reply
```

---

## 3. 数据存储设计

### 3.1 ChromaDB（向量数据库）

**用途**：存储酒店知识库 + 周边玩法库

**Collection 设计**：
```python
# Collection: hotel_knowledge
{
    "id": "hotel_001_qa_001",
    "hotel_id": "hotel_001",
    "category": "基础设施",
    "question": "有儿童拖鞋吗",
    "answer": "有的！我们准备了...",
    "embeddings": [0.123, 0.456, ...]  # 向量
}

# Collection: nearby_activities
{
    "id": "activity_001",
    "location": {"lat": 19.xx, "lng": 110.xx},
    "title": "野海滩抓螃蟹",
    "description": "酒店背后5分钟走到...",
    "tags": ["亲子", "户外", "小众"],
    "embeddings": [...]
}
```

### 3.2 PostgreSQL（关系数据库）

**表设计**：

```sql
-- 酒店表
CREATE TABLE hotels (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    address TEXT,
    location JSON,  -- {"lat": 19.xx, "lng": 110.xx}
    miniprogram_appid VARCHAR(50),
    subscription_status VARCHAR(20),  -- active/trial/expired
    subscription_start_date DATE,
    created_at TIMESTAMP
);

-- 对话记录表
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    hotel_id VARCHAR(50),
    user_id VARCHAR(100),  -- 微信 openid
    message TEXT,
    role VARCHAR(10),  -- user/assistant
    intent VARCHAR(50),
    created_at TIMESTAMP
);

-- 转化统计表
CREATE TABLE conversion_stats (
    id SERIAL PRIMARY KEY,
    hotel_id VARCHAR(50),
    date DATE,
    total_conversations INT,
    booking_intents INT,  -- 咨询预订的次数
    conversions INT,  -- 实际预订次数（需要酒店后台回传）
    created_at TIMESTAMP
);
```

---

## 4. 技术选型总结

| 模块 | 技术选择 | 原因 |
|------|---------|------|
| Web框架 | Flask | 轻量，适合MVP，已有经验 |
| AI模型 | DeepSeek | 成本低，中文能力强 |
| 向量数据库 | ChromaDB | 已在用，RAG能力成熟 |
| 关系数据库 | PostgreSQL | 稳定，支持JSON字段 |
| 微信接入 | 公众号开发者模式 | 标准方案，文档齐全 |
| 部署 | 阿里云ECS | 现有服务器，成本低 |

---

## 5. MVP 开发计划

### 第1天（今天下午）：
- ✅ 完成架构设计文档
- 🔨 搭建项目框架 `/backend/saas/`
- 🔨 实现微信消息接收 webhook

### 第2-3天：
- 实现对话管理层（意图识别、上下文管理）
- 实现 AI客服引擎（基础问答 + RAG检索）
- 测试：模拟客人咨询场景

### 第4-5天：
- 实现攻略生成引擎
- 实现预订引导模块
- 对接微信小程序卡片

### 第6-7天：
- 开发酒店管理后台（知识库录入界面）
- 数据统计功能
- 完整流程测试

### 第8-10天：
- 首批酒店试用
- 收集反馈，快速迭代
- 准备正式推广材料

---

## 6. 复用现有代码

从野游记现有代码库可以复用：

| 现有模块 | 复用到 SaaS |
|---------|-------------|
| `services/ai_engine.py` | AI客服引擎、攻略生成 |
| `services/rag_engine.py` | 知识库检索 |
| `prompts/wildtrip_prompt.py` | 改造为酒店客服 Prompt |
| 微信支付代码 | 预订支付（如果需要） |

**优势**：大部分核心能力已经有了，主要是做适配和包装 🎯

---

## 下一步

我现在开始：
1. 创建 `/backend/saas/` 目录结构
2. 实现微信 webhook 基础框架
3. 编写第一个测试 Prompt

预计 **今天17点** 前完成 MVP 核心代码，你可以用手机测试对话效果 💪
