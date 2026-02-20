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
        执行完整的 Agent 链路
        
        Args:
            initial_state: 初始状态
            progress_callback: 进度回调函数
            
        Returns:
            最终状态
        """
        state = initial_state
        total_agents = len(self.execution_order)
        
        for i, agent_name in enumerate(self.execution_order):
            agent = self.agents[agent_name]
            
            # 更新进度
            if progress_callback:
                progress = int((i / total_agents) * 100)
                progress_callback(progress, f"🤖 执行 {agent_name}...")
            
            # 执行 Agent
            state = await agent.execute(state)
            
            # 更新状态
            state.status = agent_name
            state.updated_at = state.created_at.__class__.now()
        
        state.status = 'completed'
        
        if progress_callback:
            progress_callback(100, "✅ 所有 Agent 执行完成")
        
        return state


# ========== Agent 处理函数 ==========

async def profile_agent_handler(state: TripState, context: dict) -> TripState:
    """
    Profile Agent: 提取用户偏好
    """
    from services.user_profile import extract_preferences
    
    # 从查询中提取偏好
    preferences = extract_preferences(context['query'])
    
    # 更新状态
    state.preferences = preferences
    
    logger.info(f"👤 用户偏好: {preferences.dict()}")
    return state


async def wild_routing_agent_handler(state: TripState, context: dict) -> TripState:
    """
    Wild-Routing Agent: 生成行程
    """
    from services.ai_engine import AIEngine
    from prompts.wildtrip_prompt import build_wildtrip_prompt
    
    # 构建 Prompt
    prompt = build_wildtrip_prompt(
        query=state.original_query,
        mode='full',
        preferences=context['preferences']
    )
    
    # 调用 AI 生成
    ai_engine = AIEngine()
    content = ai_engine.generate(prompt, state.original_query, 'full')
    
    # 从内容中提取结构化数据
    from services.content_parser import parse_itinerary, parse_hotels, parse_restaurants
    
    state.itinerary = parse_itinerary(content)
    state.hotels = parse_hotels(content, state.requirements.destination)
    state.restaurants = parse_restaurants(content, state.requirements.destination)
    state.markdown_content = content
    
    logger.info(f"🗺️ 生成行程: {len(state.itinerary)}天, {len(state.hotels)}家酒店")
    return state


async def pricing_agent_handler(state: TripState, context: dict) -> TripState:
    """
    Pricing Agent: 比价和建议
    """
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
    return state


async def content_agent_handler(state: TripState, context: dict) -> TripState:
    """
    Content Agent: 生成分享内容
    """
    from services.content_generator import generate_xiaohongshu
    
    # 生成小红书内容
    xiaohongshu = generate_xiaohongshu(
        itinerary=context['itinerary'],
        hotels=context['hotels'],
        destination=state.requirements.destination
    )
    
    state.xiaohongshu_content = xiaohongshu
    
    logger.info(f"📱 生成小红书内容: {len(xiaohongshu)}字")
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
