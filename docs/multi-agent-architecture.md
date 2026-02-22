# 野游记 4 个智能体架构详解

**更新时间**：2026-02-20 14:30

---

## 🎯 整体架构

野游记使用 **4 个智能体协同工作**，基于 **状态机模式**（Gemini 建议）：

```
用户查询
    ↓
① Profile Agent (理解用户)
    ↓
② Wild-Routing Agent (规划行程)
    ↓
③ Pricing Agent (智能比价)
    ↓
④ Content Agent (生成分享内容)
    ↓
完整攻略 + 小红书内容
```

---

## 📊 核心设计：全局状态对象 (TripState)

**关键思想**：所有 Agent 共享同一个"流水线产品"

```python
class TripState:
    # 用户输入
    original_query: str        # "海口3天游，带两个孩子"
    
    # ① Profile Agent 填充
    preferences: UserPreferences  # 偏好：亲子、预算、风格
    requirements: TripRequirements  # 需求：目的地、天数
    
    # ② Wild-Routing Agent 填充
    itinerary: List[DailyItinerary]  # 每日行程
    hotels: List[HotelRecommendation]  # 酒店推荐
    restaurants: List[RestaurantRecommendation]  # 餐厅推荐
    
    # ③ Pricing Agent 填充
    pricing_insights: List[PricingInsight]  # 比价建议
    
    # ④ Content Agent 填充
    markdown_content: str  # Markdown 攻略
    xiaohongshu_content: str  # 小红书内容
    
    # 路由控制（Gemini 状态机）
    next_agent: str  # 下一个执行哪个 Agent
    is_finished: bool  # 是否完成
```

**优势**：
- ✅ 结构化、可序列化
- ✅ 支持断点续传（Agent 失败可恢复）
- ✅ 每个 Agent 只操作自己负责的字段

---

## 🤖 4 个智能体详解

### ① Profile Agent - 理解用户

**代码位置**：`backend/services/user_profile.py`

**职责**：从用户查询中提取结构化偏好

**提取能力**：
- 👨‍👩‍👧‍👦 **亲子出行**：识别孩子年龄（7岁、4岁）
- 💰 **预算等级**：low（经济）/ mid（中等）/ high（豪华）
- 🎨 **旅行风格**：文化 / 自然 / 美食 / 休闲
- 📷 **装备设备**：相机 / 无人机
- 🚶 **行动能力**：正常 / 受限（老人、孕妇）
- 🍽️ **饮食限制**：素食 / 清真

**示例**：

```python
输入: "海口3天游，带7岁和4岁两个孩子，预算5000"

输出 (UserPreferences):
{
  "has_kids": true,
  "kids_ages": [7, 4],
  "budget_level": "mid",
  "travel_style": [],
  "equipment": [],
  "mobility": "normal",
  "dietary": []
}
```

**路由决策**：
- ✅ 信息完整（目的地明确） → 转到 `wild_routing`
- ❌ 信息不足（目的地未知） → 继续澄清 `profile`

---

### ② Wild-Routing Agent - 规划行程

**代码位置**：`backend/core/agent_orchestrator.py` (wild_routing_agent_handler)

**职责**：调用 AI 生成个性化"野路子"行程

**核心逻辑**：
```python
# 1. 根据偏好增强 Prompt
enhanced_prompt = build_wildtrip_prompt(
    query=state.original_query,
    mode='full',
    preferences=state.preferences  # 注入用户偏好
)

# 2. 调用 AI 生成
content = ai_engine.generate(enhanced_prompt, query, 'full')

# 3. 解析结构化数据
state.itinerary = parse_itinerary(content)  # 每日行程
state.hotels = parse_hotels(content)  # 酒店列表
state.restaurants = parse_restaurants(content)  # 餐厅列表
```

**"反套路"规则**：
- ❌ 不推荐抖音播放量 > 100万的网红景点
- ❌ 不推荐需要排队 > 1小时的餐厅
- ✅ 优先推荐小红书 < 500篇笔记的宝藏地
- ✅ 优先推荐本地人周末去的地方

**输出结构**：
```python
DailyItinerary:
{
  "day": 1,
  "theme": "慢享海口老城",
  "morning": "骑楼老街漫步，避开10点后人流",
  "lunch": {
    "name": "梅姨海南粉",
    "cuisine": "本地小吃",
    "price_per_person": 15,
    "reason": "本地人常去，游客少"
  },
  "afternoon": "五公祠，人文历史",
  "dinner": {...},
  "accommodation": {...},
  "wild_tips": ["带孩子去骑楼街拍照，早上8点光线最好"]
}
```

**路由决策**：
- ✅ 有酒店推荐 → 转到 `pricing`
- ❌ 无酒店推荐 → 直接 `done`

---

### ③ Pricing Agent - 智能比价

**代码位置**：`backend/core/agent_orchestrator.py` (pricing_agent_handler)

**职责**：对比多平台价格，生成预订建议

**核心功能**：
```python
from services.pricing_monitor import PricingMonitor

monitor = PricingMonitor()

for hotel in state.hotels:
    insight = monitor.check_price(
        hotel_name=hotel.name,
        destination=state.requirements.destination,
        check_in_date=state.requirements.start_date
    )
    
    # 分析价格趋势
    if insight.trend == 'rising':
        insight.suggestion = "价格正在上涨，建议尽快预订"
    elif insight.trend == 'falling':
        insight.suggestion = "价格下降中，可再观察1-2天"
    
    state.pricing_insights.append(insight)
```

**输出示例**：
```markdown
💰 比价建议

海口朗廷酒店:
- 携程: ¥680/晚 ⬇️ (比昨天降¥50)
- 飞猪: ¥720/晚
- 美团: ¥690/晚

💡 建议: 现在订最划算！携程处于近7天最低价
```

**Gemini 建议增强**：
- 精品酒店：生成"直连话术"，教用户绕过 OTA
- 价格波动大：提示"切换更深度的比价通道"

**路由决策**：
- ✅ 比价完成 → 转到 `content`
- ⚠️ 比价失败 → 友好提示，继续 `content`

---

### ④ Content Agent - 生成分享内容

**代码位置**：`backend/core/agent_orchestrator.py` (content_agent_handler)

**职责**：生成小红书风格的图文内容

**输出示例**：
```markdown
📍 海口3天2晚亲子游 | 人均2500超全攻略

✨ 适合人群
👨‍👩‍👧‍👦 7岁+4岁孩子的家庭
💰 预算中等，追求性价比

🏨 住宿推荐
Day1-2: 海口朗廷酒店
- 无边泳池，孩子超爱
- 早餐丰盛，儿童餐很棒
- 💰比价: 携程¥680最低

🍜 美食打卡
- 梅姨海南粉: 本地人常去，游客少
- 文昌鸡饭老店: 比网红店好吃还便宜

📸 野路子小贴士
- 骑楼老街早上8点去，光线最好
- 五公祠人少，适合带孩子慢慢逛

#海口亲子游 #野游记 #小众路线
```

**核心功能**：
```python
from services.content_generator import generate_xiaohongshu

xiaohongshu = generate_xiaohongshu(
    itinerary=state.itinerary,
    hotels=state.hotels,
    destination=state.requirements.destination
)

state.xiaohongshu_content = xiaohongshu
```

**路由决策**：
- ✅ 完成 → `next_agent = 'done'`, `is_finished = True`

---

## 🔄 编排器 (Orchestrator)

**代码位置**：`backend/core/agent_orchestrator.py` (TripOrchestrator)

**核心机制**：基于 **Gemini 状态机模式**

```python
# 状态机循环
while not state.is_finished:
    current_agent = state.next_agent  # 读取下一个 Agent
    
    # 执行 Agent
    state = await agents[current_agent].execute(state)
    
    # Agent 内部会设置 state.next_agent
    # 如果 next_agent = 'done'，则 is_finished = True
```

**优势**：
- ✅ **动态路由**：Agent 自己决定下一步
- ✅ **灵活性**：可以回到之前的 Agent（如 Profile 继续澄清）
- ✅ **容错性**：Agent 失败可以跳过或重试

**依赖关系**：
```python
orchestrator.register_agent(AgentNode(
    name='profile',
    dependencies=[]  # 第一个，无依赖
))

orchestrator.register_agent(AgentNode(
    name='wild_routing',
    dependencies=['profile']  # 依赖 Profile
))

orchestrator.register_agent(AgentNode(
    name='pricing',
    dependencies=['wild_routing']  # 依赖行程生成
))

orchestrator.register_agent(AgentNode(
    name='content',
    dependencies=['pricing']  # 依赖比价
))
```

**执行顺序**（自动拓扑排序）：
```
profile → wild_routing → pricing → content
```

---

## 🎨 关键设计模式

### 1. 上下文隔离

每个 Agent 只看到自己需要的信息：

```python
def get_context_for_agent(self, agent_name: str) -> dict:
    if agent_name == 'profile':
        return {'query': self.original_query}
    
    elif agent_name == 'wild_routing':
        return {
            'destination': self.requirements.destination,
            'preferences': self.preferences.dict()
        }
    
    elif agent_name == 'pricing':
        return {
            'hotels': [h.dict() for h in self.hotels],
            'destination': self.requirements.destination
        }
```

**避免**：Wild-Routing Agent 看到比价数据，Pricing Agent 看到聊天记录

---

### 2. 状态可序列化

```python
# 保存状态到 Redis
state_json = trip_state.to_json()
redis.set(f'trip_state:{task_id}', json.dumps(state_json))

# 恢复状态
state_data = json.loads(redis.get(f'trip_state:{task_id}'))
trip_state = TripState.from_json(state_data)
```

**用途**：断点续传、多次生成、状态调试

---

### 3. Agent 可插拔

```python
# 轻松添加新 Agent（如翻译 Agent）
orchestrator.register_agent(AgentNode(
    name='translator',
    handler=translator_handler,
    dependencies=['content']  # 依赖内容生成
))
```

---

## 📈 前端集成

**小程序可以展示更丰富的信息**：

```xml
<!-- 用户偏好卡片 -->
<view class="preference-card">
  <text class="card-title">🎯 为您定制</text>
  <view class="tags">
    <text class="tag">👶 亲子友好</text>
    <text class="tag">💰 经济实惠</text>
  </view>
</view>

<!-- 比价建议卡片 -->
<view class="pricing-card" wx:for="{{pricing_insights}}">
  <text class="hotel-name">{{item.hotel_name}}</text>
  <text class="trend">{{item.suggestion}}</text>
  <button bindtap="onBook">立即预订</button>
</view>

<!-- 小红书分享按钮 -->
<button bindtap="shareToXiaohongshu">
  一键分享到小红书
</button>
```

---

## 🚀 实施状态

### ✅ 已完成
- [x] TripState 全局状态对象
- [x] TripOrchestrator 编排器
- [x] Profile Agent 基础版
- [x] 状态机循环逻辑

### ⏳ 进行中
- [ ] Wild-Routing Agent 内容解析器
- [ ] Pricing Agent 集成 pricing-system
- [ ] Content Agent 小红书内容生成

### 📅 计划中
- [ ] 集成到 generate.py
- [ ] 前端展示优化
- [ ] 用户偏好持久化

---

## 💡 Gemini 建议的亮点

1. **状态机模式**：Agent 自己决定 `next_agent`，灵活路由
2. **全局状态对象**：避免"鸡同鸭讲"
3. **上下文隔离**：每个 Agent 只看必要信息
4. **容错设计**：Agent 失败可以优雅降级

---

## 🎯 下一步建议

1. **完善内容解析器**：从 Markdown 提取酒店/餐厅列表
2. **测试完整链路**：跑通 4 个 Agent 流程
3. **前端对接**：展示用户偏好和比价建议
4. **性能优化**：考虑 Agent 并行执行（无依赖的可以同时跑）

---

**代码位置**：
- `backend/core/trip_state.py` - 状态对象
- `backend/core/agent_orchestrator.py` - 编排器 + 4个Agent
- `backend/services/user_profile.py` - Profile Agent
- `docs/guides/多智能体架构实施方案.md` - 详细设计文档
