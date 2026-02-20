"""
测试 Agent 编排器
基于 Gemini 的状态机思路
"""

import asyncio
from core.trip_state import TripState, TripRequirements
from core.agent_orchestrator import create_trip_orchestrator
from loguru import logger


async def test_wildtrip_workflow():
    """测试完整的 Agent 链路"""
    
    # 🔥 模拟用户输入
    user_input = "周末想带老婆和两个儿子(7岁和4岁)出去喘口气,不想走太远,要有水能玩,我不喜欢人挤人"
    
    print(f"👤 用户输入: {user_input}")
    print("-" * 60)
    
    # 🔥 创建初始状态
    initial_state = TripState(
        original_query=user_input,
        session_id="test-001",
        requirements=TripRequirements(
            destination="海口",  # 假设已提取
            days=3,
            budget=5000,
            travelers=4
        ),
        next_agent='profile'  # 从 Profile Agent 开始
    )
    
    # 🔥 创建编排器
    orchestrator = create_trip_orchestrator()
    
    # 🔥 进度回调
    def on_progress(progress: int, message: str):
        print(f"[{progress}%] {message}")
    
    # 🔥 执行 Agent 链路
    try:
        final_state = await orchestrator.execute(
            initial_state,
            progress_callback=on_progress
        )
        
        print("-" * 60)
        print("🎉 【最终结果】")
        print(f"状态: {final_state.status}")
        print(f"是否完成: {final_state.is_finished}")
        print(f"用户偏好: {final_state.preferences.dict()}")
        print(f"行程天数: {len(final_state.itinerary)}")
        print(f"酒店数量: {len(final_state.hotels)}")
        print(f"比价建议: {len(final_state.pricing_insights)}")
        
        if final_state.markdown_content:
            print(f"\n攻略内容预览:")
            print(final_state.markdown_content[:500] + "...")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_wildtrip_workflow())
