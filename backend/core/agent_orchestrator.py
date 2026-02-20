"""
野游记 Agent 编排器 (Orchestrator)
基于状态图的多智能体协同
"""

from typing import Callable, Dict, List
from loguru import logger
from .trip_state import TripState


class AgentNode:
    """单个 Agent 节点"""
    
    def __init__(self, name: str, handler: Callable, dependencies: List[str] = None):
        self.name = name
        self.handler = handler
        self.dependencies = dependencies or []
    
    async def execute(self, state: TripState) -> TripState:
        """执行 Agent,更新状态"""
        logger.info(f"🤖 执行 Agent: {self.name}")
        
        try:
            # 获取该 Agent 需要的上下文
            context = state.get_context_for_agent(self.name)
            
            # 执行 Agent 逻辑
            updated_state = await self.handler(state, context)
            
            logger.info(f"✅ Agent {self.name} 完成")
            return updated_state
            
        except Exception as e:
            logger.error(f"❌ Agent {self.name} 失败: {e}")
            raise


class TripOrchestrator:
    """
    野游记编排器
    
    按照 DAG (有向无环图) 执行 Agent 链路:
    
    Profile Agent → Wild-Routing Agent → Pricing Agent → Content Agent
         ↓                 ↓                    ↓               ↓
      提取偏好          生成行程            比价建议        生成内容
    """
    
    def __init__(self):
        self.agents: Dict[str, AgentNode] = {}
        self.execution_order: List[str] = []
    
    def register_agent(self, node: AgentNode):
        """注册 Agent"""
        self.agents[node.name] = node
        logger.info(f"📝 注册 Agent: {node.name}")
    
    def build_execution_graph(self):
        """
        构建执行图 (拓扑排序)
        
        根据依赖关系确定执行顺序
        """
        visited = set()
        order = []
        
        def visit(name: str):
            if name in visited:
                return
            visited.add(name)
            
            agent = self.agents[name]
            for dep in agent.dependencies:
                if dep in self.agents:
                    visit(dep)
            
            order.append(name)
        
        for name in self.agents:
            visit(name)
        
        self.execution_order = order
        logger.info(f"📊 执行顺序: {' → '.join(self.execution_order)}")
    
    async def execute(self, initial_state: TripState, progress_callback=None) -> TripState:
        """
        执行完整的 Agent 链路 (基于 Gemini 的状态机思路)
        
        Args:
            initial_state: 初始状态
            progress_callback: 进度回调函数
            
        Returns:
            最终状态
        """
        state = initial_state
        max_iterations = 20  # 防止死循环
        iteration = 0
        
        logger.info(f"🚀 开始执行 Agent 链路,初始 Agent: {state.next_agent}")
        
        # 🔥 Gemini 的状态机循环
        while not state.is_finished and iteration < max_iterations:
            iteration += 1
            
            current_agent_name = state.next_agent
            
            # 检查 Agent 是否存在
            if current_agent_name not in self.agents:
                logger.error(f"❌ Agent '{current_agent_name}' 不存在!")
                state.is_finished = True
                break
            
            agent = self.agents[current_agent_name]
            
            # 更新进度
            if progress_callback:
                progress = min(iteration * 25, 90)  # 每个 Agent 约 25%
                progress_callback(progress, f"🤖 执行 {current_agent_name}...")
            
            logger.info(f"🔄 [{iteration}] 执行 Agent: {current_agent_name}")
            
            # 执行 Agent (Agent 内部会修改 state.next_agent)
            state = await agent.execute(state)
            
            # 更新元数据
            state.status = current_agent_name
            state.updated_at = state.created_at.__class__.now()
            
            # 如果 Agent 没有设置 next_agent,说明已完成
            if not state.next_agent or state.next_agent == 'done':
                state.is_finished = True
        
        if iteration >= max_iterations:
            logger.warning("⚠️ 达到最大迭代次数,强制结束")
        
        state.status = 'completed'
        
        if progress_callback:
            progress_callback(100, "✅ 所有 Agent 执行完成")
        
        logger.info(f"✅ Agent 链路执行完成,共 {iteration} 步")
        return state


# ========== Agent 处理函数 ==========

async def profile_agent_handler(state: TripState, context: dict) -> TripState:
    """
    Profile Agent: 提取用户偏好
    
    🔥 Gemini 建议: 深度挖掘潜在需求
    - 如果用户提到两个孩子(7岁/4岁),自动推断需要家庭联房
    - 结合常驻地,限定在高铁2小时或自驾3小时辐射圈内
    """
    from services.user_profile import extract_preferences
    
    # 从查询中提取偏好
    preferences = extract_preferences(context['query'])
    
    # 更新状态
    state.preferences = preferences
    
    # 🔥 路由决策:信息是否完整?
    if not state.requirements.destination:
        # 目的地未知,需要继续澄清
        state.next_agent = 'profile'  # 回到自己继续澄清
        logger.info(f"👤 偏好已提取,但目的地未知,需继续澄清")
    else:
        # 信息完整,转到规划 Agent
        state.next_agent = 'wild_routing'
        logger.info(f"👤 用户偏好: {preferences.model_dump()}, 转到规划 Agent")
    
    return state


async def wild_routing_agent_handler(state: TripState, context: dict) -> TripState:
    """
    Wild-Routing Agent: 生成行程
    
    🔥 Gemini 建议: 生成 3-4 个不同概念方案
    - 方案A: 绝对纯玩(避开人群)
    - 方案B: 轻度探索(经典+小众)
    - 方案C: 亲子专属(适合带孩子)
    """
    from services.ai_engine import AIEngine
    from prompts.wildtrip_prompt import build_wildtrip_prompt
    from services.user_profile import enhance_prompt_with_preferences
    from services.content_parser import parse_itinerary, parse_hotels, parse_restaurants
    
    logger.info(f"🗺️ 开始生成行程: {state.requirements.destination} {state.requirements.days}天")
    
    # 1. 构建基础 Prompt
    base_prompt = build_wildtrip_prompt(
        query=state.original_query,
        mode='full'
    )
    
    # 2. 根据用户偏好增强 Prompt
    enhanced_prompt = enhance_prompt_with_preferences(
        base_prompt,
        state.preferences
    )
    
    logger.info(f"📝 Prompt 已增强，包含用户偏好")
    
    # 3. 调用 AI 生成攻略
    try:
        ai_engine = AIEngine()
        content = ai_engine.generate(
            enhanced_prompt,
            state.original_query,
            mode='full'  # 注意：使用 full 模式，不是 chat
        )
        
        logger.info(f"✅ AI 生成完成: {len(content)}字")
        
        # 保存完整内容
        state.markdown_content = content
        
    except Exception as e:
        logger.error(f"❌ AI 生成失败: {e}")
        # 降级：使用简化内容
        state.markdown_content = f"# {state.requirements.destination}{state.requirements.days}天攻略\n\n攻略生成中..."
        state.next_agent = 'done'
        return state
    
    # 4. 从 Markdown 内容中提取结构化数据
    try:
        logger.info("🔍 开始解析结构化数据...")
        
        state.itinerary = parse_itinerary(content)
        state.hotels = parse_hotels(content, state.requirements.destination)
        state.restaurants = parse_restaurants(content, state.requirements.destination)
        
        logger.info(
            f"✅ 解析完成: "
            f"{len(state.itinerary)}天行程, "
            f"{len(state.hotels)}家酒店, "
            f"{len(state.restaurants)}家餐厅"
        )
        
    except Exception as e:
        logger.warning(f"⚠️ 结构化数据解析失败: {e}")
        # 解析失败不影响主流程，继续
    
    # 5. 路由决策
    if state.hotels and len(state.hotels) > 0:
        # 有酒店推荐，转到比价 Agent
        state.next_agent = 'pricing'
        logger.info(f"🔄 路由到 Pricing Agent (发现{len(state.hotels)}家酒店)")
    else:
        # 没有酒店推荐，跳过比价，直接到内容生成
        state.next_agent = 'content'
        logger.info(f"🔄 路由到 Content Agent (跳过比价)")
    
    return state


async def pricing_agent_handler(state: TripState, context: dict) -> TripState:
    """
    Pricing Agent: 比价和建议
    
    🔥 Gemini 建议:
    - 对比不同平台的价格差,找出"真实底价"
    - 如果是精品酒店,生成直连话术,教用户绕过 OTA
    """
    try:
        from services.pricing_monitor import PricingMonitor
        
        monitor = PricingMonitor()
        
        for hotel in context['hotels']:
            insight = monitor.check_price(
                hotel_name=hotel['name'],
                destination=context['destination'],
                check_in=context.get('check_in_date')
            )
            
            if insight:
                state.pricing_insights.append(insight)
        
        logger.info(f"💰 比价完成: {len(state.pricing_insights)}条建议")
        
    except Exception as e:
        logger.warning(f"⚠️ 比价失败: {e},跳过此步骤")
        # 🔥 Gemini 建议:失败时友好提示
        # 这里可以设置一个标志,让前端显示"正在切换更深度的比价通道"
    
    # 🔥 路由决策:比价完成,进入内容生成
    state.next_agent = 'content'
    
    return state


async def content_agent_handler(state: TripState, context: dict) -> TripState:
    """
    Content Agent: 生成分享内容
    """
    logger.info("📱 开始生成分享内容...")
    
    try:
        from services.content_generator import generate_xiaohongshu
        
        # 转换为 dict 格式（content_generator 需要）
        itinerary_dicts = [
            {
                'day': it.day,
                'theme': it.theme,
                'morning': it.morning,
                'afternoon': it.afternoon
            }
            for it in state.itinerary
        ] if state.itinerary else []
        
        hotel_dicts = [
            {
                'name': h.name,
                'price': h.price,
                'features': h.features,
                'reason': h.reason
            }
            for h in state.hotels
        ] if state.hotels else []
        
        restaurant_dicts = [
            {
                'name': r.name,
                'cuisine': r.cuisine,
                'price_per_person': r.price_per_person,
                'dishes': r.dishes,
                'reason': r.reason
            }
            for r in state.restaurants
        ] if state.restaurants else []
        
        preferences_dict = state.preferences.model_dump() if state.preferences else None
        
        # 生成小红书内容
        xiaohongshu = generate_xiaohongshu(
            itinerary=itinerary_dicts,
            hotels=hotel_dicts,
            destination=state.requirements.destination,
            preferences=preferences_dict,
            restaurants=restaurant_dicts
        )
        
        state.xiaohongshu_content = xiaohongshu
        
        logger.info(f"✅ 小红书内容生成完成: {len(xiaohongshu)}字")
        
    except Exception as e:
        logger.warning(f"⚠️ 小红书内容生成失败: {e}")
        # 生成简化版本
        state.xiaohongshu_content = f"📍 {state.requirements.destination}{state.requirements.days}天游 | 野游记攻略\n\n详细攻略请查看完整版本～"
    
    # 🔥 路由决策:全部完成
    state.next_agent = 'done'
    state.is_finished = True
    
    logger.info("🎉 所有 Agent 执行完成！")
    
    return state


# ========== 初始化编排器 ==========

def create_trip_orchestrator() -> TripOrchestrator:
    """创建野游记编排器"""
    orchestrator = TripOrchestrator()
    
    # 注册 Agent (按依赖顺序)
    orchestrator.register_agent(AgentNode(
        name='profile',
        handler=profile_agent_handler,
        dependencies=[]  # 无依赖,第一个执行
    ))
    
    orchestrator.register_agent(AgentNode(
        name='wild_routing',
        handler=wild_routing_agent_handler,
        dependencies=['profile']  # 依赖 Profile
    ))
    
    orchestrator.register_agent(AgentNode(
        name='pricing',
        handler=pricing_agent_handler,
        dependencies=['wild_routing']  # 依赖行程生成
    ))
    
    orchestrator.register_agent(AgentNode(
        name='content',
        handler=content_agent_handler,
        dependencies=['pricing']  # 依赖比价
    ))
    
    # 构建执行图
    orchestrator.build_execution_graph()
    
    return orchestrator
