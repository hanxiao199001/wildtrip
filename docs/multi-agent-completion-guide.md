# 野游记多智能体架构完善指南

**更新时间**：2026-02-20 14:40

---

## ✅ 已完成的工作

### 1. 核心文件创建完成

| 文件 | 状态 | 功能 |
|------|------|------|
| `core/trip_state.py` | ✅ | 全局状态对象 |
| `core/agent_orchestrator.py` | ✅ | 编排器 + 4个Agent框架 |
| `services/user_profile.py` | ✅ | Profile Agent（用户偏好提取） |
| `services/content_parser.py` | ✅ 新增 | 内容解析器 |
| `services/pricing_monitor.py` | ✅ 新增 | 比价监控 |
| `services/content_generator.py` | ✅ 新增 | 小红书内容生成 |
| `test_multi_agent.py` | ✅ 新增 | 完整测试脚本 |

### 2. 测试结果

**单个 Agent 测试**：✅ 全部通过

```bash
cd /root/clawd/wildtrip-existing/backend
python3 test_multi_agent.py --mode single
```

**测试结果**：
- ✅ Profile Agent：正确识别亲子、预算、风格
- ✅ Content Parser：成功解析酒店信息
- ✅ Pricing Monitor：Mock 比价数据正常
- ✅ Content Generator：生成306字小红书内容

---

## 🔧 需要完善的部分

### 1. Wild-Routing Agent（最重要）

**当前状态**：框架完成，但缺少真实 AI 调用

**需要做的**：

#### 步骤1：集成现有 AI 引擎

```python
# 文件：core/agent_orchestrator.py

async def wild_routing_agent_handler(state: TripState, context: dict) -> TripState:
    from services.ai_engine import AIEngine
    from prompts.wildtrip_prompt import build_wildtrip_prompt
    from services.user_profile import enhance_prompt_with_preferences
    
    # 1. 构建 Prompt（注入用户偏好）
    base_prompt = build_wildtrip_prompt(
        query=state.original_query,
        mode='full'
    )
    
    # 2. 增强 Prompt
    enhanced_prompt = enhance_prompt_with_preferences(
        base_prompt,
        state.preferences
    )
    
    # 3. 调用 AI 生成
    ai_engine = AIEngine()
    content = ai_engine.generate(
        enhanced_prompt,
        state.original_query,
        mode='full'  # 注意：不是 'chat'
    )
    
    # 4. 解析结构化数据
    from services.content_parser import (
        parse_itinerary,
        parse_hotels,
        parse_restaurants
    )
    
    state.itinerary = parse_itinerary(content)
    state.hotels = parse_hotels(content, state.requirements.destination)
    state.restaurants = parse_restaurants(content, state.requirements.destination)
    state.markdown_content = content
    
    logger.info(f"🗺️ 生成行程: {len(state.itinerary)}天, {len(state.hotels)}家酒店")
    
    # 5. 路由决策
    if state.hotels:
        state.next_agent = 'pricing'
    else:
        state.next_agent = 'content'
    
    return state
```

#### 步骤2：优化内容解析器

**问题**：当前正则表达式匹配率不高

**解决方案**：

```python
# 文件：services/content_parser.py

def parse_hotels(markdown_content: str, destination: str = "") -> List[HotelRecommendation]:
    """
    优化版：支持多种格式
    """
    hotels = []
    
    # 格式1：**酒店名称**
    pattern1 = r'\*\*(.+?酒店|.+?民宿)\*\*'
    
    # 格式2：### 酒店名称
    pattern2 = r'###\s+(.+?酒店|.+?民宿)'
    
    # 格式3：1. 酒店名称
    pattern3 = r'\d+\.\s+(.+?酒店|.+?民宿)'
    
    # 合并所有匹配
    all_patterns = [pattern1, pattern2, pattern3]
    
    for pattern in all_patterns:
        matches = re.findall(pattern, markdown_content)
        # ... 解析逻辑
    
    return hotels
```

---

### 2. Pricing Agent 优化

**当前状态**：使用 Mock 数据

**集成真实 pricing-system 的方案**：

#### 方案A：调用 pricing-system API（推荐）

```python
# 文件：services/pricing_monitor.py

class PricingMonitor:
    def __init__(self):
        # pricing-system 的 API 地址
        self.pricing_api = os.getenv(
            'PRICING_API_URL',
            'http://localhost:5001'
        )
        self.enable_real_pricing = True  # 启用真实比价
    
    def _check_price_real(self, hotel_name, destination, check_in):
        try:
            response = requests.get(
                f"{self.pricing_api}/api/hotels/compare",
                params={
                    'hotel': hotel_name,
                    'city': destination,
                    'check_in': check_in
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                return PricingInsight(
                    hotel_name=hotel_name,
                    platform=data['best_platform'],
                    current_price=data['best_price'],
                    trend=data['price_trend'],
                    suggestion=self._generate_suggestion(data)
                )
        except Exception as e:
            logger.warning(f"真实比价失败，使用 Mock: {e}")
            return self._check_price_mock(hotel_name, destination)
```

#### 方案B：如果 pricing-system 不可用

保持当前 Mock 方案，但优化建议生成：

```python
def _generate_suggestion(self, price_data):
    """根据价格数据生成建议"""
    if price_data['trend'] == 'falling':
        return f"价格下降中，预计还会降¥{price_data['estimated_drop']}，可再观察1-2天"
    elif price_data['trend'] == 'rising':
        return f"价格正在上涨，建议尽快预订，否则可能涨¥{price_data['estimated_rise']}"
    else:
        return "价格稳定，可随时预订"
```

---

### 3. Content Agent 优化

**当前问题**：餐厅列表是硬编码

**优化方案**：从解析后的 `state.restaurants` 提取

```python
# 文件：services/content_generator.py

def generate_xiaohongshu(
    itinerary: List[Dict],
    hotels: List[Dict],
    destination: str,
    preferences: Dict = None,
    restaurants: List[Dict] = None  # 新增参数
) -> str:
    # ... 前面的代码
    
    # ========== 美食打卡 ==========
    lines.append("🍜 **美食打卡**")
    lines.append("")
    
    if restaurants:
        for r in restaurants[:3]:  # 最多3家
            name = r.get('name', '')
            reason = r.get('reason', '')
            dishes = r.get('dishes', [])
            
            dish_str = '、'.join(dishes[:2]) if dishes else ''
            lines.append(f"- {name}: {dish_str} {reason}")
    else:
        # 降级：从行程中提取
        lines.append("- 本地特色美食推荐（详见攻略）")
    
    # ... 后面的代码
```

---

### 4. 与现有代码集成

**最重要的一步**：修改 `api/generate.py`

#### 当前生成流程

```python
# 文件：api/generate.py

def run_generation_task(task_id, query, mode, options, user_id):
    # 当前：直接调用 AI
    content = ai_engine.generate(prompt, query, mode)
    
    # 保存结果
    active_tasks[task_id]['result'] = content
```

#### 改为多智能体流程

```python
def run_generation_task(task_id, query, mode, options, user_id):
    """
    使用多智能体流程生成攻略
    """
    import asyncio
    from core.trip_state import TripState, TripRequirements
    from core.agent_orchestrator import create_trip_orchestrator
    from prompts.wildtrip_prompt import extract_city_name, extract_days, extract_budget
    
    # 1. 创建初始状态
    initial_state = TripState(
        original_query=query,
        user_id=user_id,
        session_id=task_id,
        requirements=TripRequirements(
            destination=extract_city_name(query),
            days=extract_days(query),
            budget=extract_budget(query),
            travelers=options.get('travelers', 1)
        )
    )
    
    # 2. 创建编排器
    orchestrator = create_trip_orchestrator()
    
    # 3. 执行 Agent 链路
    def emit_agent_progress(progress, message):
        emit_progress(socketio, task_id, 'agent', message, progress)
    
    final_state = asyncio.run(
        orchestrator.execute(
            initial_state,
            progress_callback=emit_agent_progress
        )
    )
    
    # 4. 保存结果（兼容现有前端）
    active_tasks[task_id]['result'] = {
        'content': final_state.markdown_content,  # 主攻略
        'xiaohongshu': final_state.xiaohongshu_content,  # 小红书
        
        # 新增：结构化数据
        'preferences': final_state.preferences.dict(),
        'hotels': [h.dict() for h in final_state.hotels],
        'restaurants': [r.dict() for r in final_state.restaurants],
        'pricing_insights': [p.dict() for p in final_state.pricing_insights],
    }
    
    active_tasks[task_id]['status'] = 'completed'
```

---

## 📋 完善步骤清单

### 阶段1：核心功能完善（本周）

- [ ] **Wild-Routing Agent 集成**
  - [ ] 接入 AI 引擎调用
  - [ ] 优化内容解析器（提高匹配率）
  - [ ] 测试解析效果

- [ ] **Content Agent 优化**
  - [ ] 从 state.restaurants 提取餐厅
  - [ ] 优化小红书内容模板

- [ ] **测试完整链路**
  - [ ] 运行 `python3 test_multi_agent.py --mode full`
  - [ ] 验证 4 个 Agent 协同工作

### 阶段2：集成到现有系统（下周）

- [ ] **修改 generate.py**
  - [ ] 使用多智能体流程
  - [ ] 保持与前端兼容

- [ ] **前端展示优化**
  - [ ] 显示用户偏好卡片
  - [ ] 显示比价建议
  - [ ] 添加"分享到小红书"按钮

### 阶段3：优化和扩展（两周后）

- [ ] **Pricing Agent 真实集成**
  - [ ] 对接 pricing-system API
  - [ ] 或对接携程/美团公开 API

- [ ] **用户偏好持久化**
  - [ ] 保存到数据库
  - [ ] 下次生成时自动应用

- [ ] **性能优化**
  - [ ] Agent 并行执行（无依赖的可以同时跑）
  - [ ] 结果缓存

---

## 🧪 测试方法

### 测试单个 Agent

```bash
cd /root/clawd/wildtrip-existing/backend
python3 test_multi_agent.py --mode single
```

### 测试完整链路

```bash
python3 test_multi_agent.py --mode full
```

**注意**：完整测试需要 AI_API_KEY 配置

### 测试特定模块

```bash
# 测试 Profile Agent
python3 services/user_profile.py

# 测试内容解析器
python3 services/content_parser.py

# 测试 Pricing Monitor
python3 services/pricing_monitor.py

# 测试内容生成器
python3 services/content_generator.py
```

---

## 📝 下一步建议

### 立即可做（今天）

1. **测试 Wild-Routing Agent**
   - 配置 AI_API_KEY
   - 运行完整测试
   - 验证解析效果

2. **优化内容解析器**
   - 提高酒店/餐厅匹配率
   - 支持更多 Markdown 格式

### 本周内

1. **集成到 generate.py**
2. **前端展示优化**
3. **真实场景测试**

### 两周内

1. **Pricing Agent 真实集成**
2. **用户偏好持久化**
3. **性能优化**

---

## 💡 关键决策点

### 决策1：是否保留现有生成流程？

**方案A**：完全替换为多智能体
- ✅ 优势：功能更强大，结构化数据丰富
- ❌ 风险：需要前端配合改造

**方案B**：双模式共存
- 简单查询：使用原有流程（快）
- 复杂查询：使用多智能体（功能多）

**建议**：先用方案B，逐步过渡到方案A

### 决策2：Pricing Agent 是否集成 pricing-system？

**方案A**：集成真实比价
- ✅ 用户价值大
- ❌ 需要 pricing-system 稳定运行

**方案B**：暂时使用 Mock
- ✅ 快速上线
- ❌ 用户价值有限

**建议**：先用 Mock 上线，后续优化

---

## 🎯 总结

**当前进度**：核心架构完成 ✅，缺少 Wild-Routing Agent 的真实 AI 调用

**关键任务**：
1. Wild-Routing Agent 接入 AI 引擎（最重要）
2. 优化内容解析器
3. 集成到 generate.py

**预计时间**：
- 核心功能完善：2-3天
- 集成到系统：1-2天
- 总计：1周内可以上线测试

---

**文件位置**：
- 本文档：`docs/multi-agent-completion-guide.md`
- 测试脚本：`backend/test_multi_agent.py`
- 核心代码：`backend/core/`, `backend/services/`
