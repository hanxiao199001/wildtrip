#!/usr/bin/env python3
"""
多智能体架构完整测试
测试 4 个 Agent 的协同工作
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from core.trip_state import TripState, TripRequirements
from core.agent_orchestrator import create_trip_orchestrator
from loguru import logger

# 配置日志
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | {message}")


async def test_full_pipeline():
    """测试完整的 Agent 管道"""
    
    print("="*80)
    print("🤖 野游记多智能体架构测试")
    print("="*80)
    print()
    
    # 创建初始状态
    initial_state = TripState(
        original_query="海口3天游，带7岁和4岁两个孩子，预算5000",
        session_id="test_001",
        requirements=TripRequirements(
            destination="海口",
            days=3,
            budget=5000,
            travelers=4
        )
    )
    
    print(f"📝 用户查询: {initial_state.original_query}")
    print(f"🎯 目的地: {initial_state.requirements.destination}")
    print(f"⏱️  天数: {initial_state.requirements.days}")
    print()
    
    # 创建编排器
    orchestrator = create_trip_orchestrator()
    
    # 进度回调
    def progress_callback(progress: int, message: str):
        print(f"[{progress:3d}%] {message}")
    
    # 执行 Agent 链路
    print("🚀 开始执行 Agent 链路...\n")
    
    try:
        final_state = await orchestrator.execute(
            initial_state=initial_state,
            progress_callback=progress_callback
        )
        
        print("\n" + "="*80)
        print("✅ 执行完成！")
        print("="*80)
        print()
        
        # 显示结果
        print("📊 **执行结果**\n")
        
        # 1. 用户偏好
        print("1️⃣  **用户偏好** (Profile Agent)")
        print(f"   - 亲子出行: {final_state.preferences.has_kids}")
        if final_state.preferences.kids_ages:
            print(f"   - 孩子年龄: {', '.join([str(age) for age in final_state.preferences.kids_ages])}岁")
        print(f"   - 预算等级: {final_state.preferences.budget_level}")
        if final_state.preferences.travel_style:
            print(f"   - 旅行风格: {', '.join(final_state.preferences.travel_style)}")
        print()
        
        # 2. 行程规划
        print("2️⃣  **行程规划** (Wild-Routing Agent)")
        print(f"   - 行程天数: {len(final_state.itinerary)}天")
        print(f"   - 推荐酒店: {len(final_state.hotels)}家")
        print(f"   - 推荐餐厅: {len(final_state.restaurants)}家")
        
        if final_state.itinerary:
            print("\n   行程概览:")
            for day in final_state.itinerary[:3]:
                print(f"   Day {day.day}: {day.theme}")
        
        if final_state.hotels:
            print("\n   酒店推荐:")
            for hotel in final_state.hotels[:2]:
                print(f"   - {hotel.name} (¥{hotel.price}/晚)")
        print()
        
        # 3. 比价建议
        print("3️⃣  **比价建议** (Pricing Agent)")
        print(f"   - 比价数据: {len(final_state.pricing_insights)}条")
        
        if final_state.pricing_insights:
            for insight in final_state.pricing_insights[:2]:
                print(f"   - {insight.hotel_name}")
                print(f"     {insight.platform} ¥{insight.current_price} ({insight.trend})")
                print(f"     💡 {insight.suggestion}")
        print()
        
        # 4. 分享内容
        print("4️⃣  **分享内容** (Content Agent)")
        if final_state.xiaohongshu_content:
            preview = final_state.xiaohongshu_content[:200]
            print(f"   小红书内容: {len(final_state.xiaohongshu_content)}字")
            print(f"   预览:\n")
            for line in preview.split('\n')[:5]:
                print(f"   {line}")
            print("   ...")
        else:
            print("   ⚠️  小红书内容未生成")
        print()
        
        # 5. Markdown 攻略
        if final_state.markdown_content:
            print("5️⃣  **完整攻略**")
            print(f"   字数: {len(final_state.markdown_content)}")
            print(f"   状态: ✅ 已生成")
        else:
            print("5️⃣  **完整攻略**: ⚠️  未生成（需要真实 AI 调用）")
        
        print("\n" + "="*80)
        
        # 保存结果到文件
        output_file = "test_multi_agent_output.json"
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_state.to_json(), f, ensure_ascii=False, indent=2)
        
        print(f"💾 完整结果已保存到: {output_file}")
        print("="*80)
        
        return final_state
    
    except Exception as e:
        logger.error(f"❌ 执行失败: {e}", exc_info=True)
        raise


async def test_single_agent():
    """测试单个 Agent"""
    
    print("="*80)
    print("🧪 测试单个 Agent")
    print("="*80)
    print()
    
    # 测试 Profile Agent
    print("1️⃣  测试 Profile Agent")
    print("-"*80)
    
    from services.user_profile import extract_preferences
    
    test_queries = [
        "海口3天游，带7岁和4岁两个孩子，预算5000",
        "穷游云南，吃货一枚，想找小众美食",
        "我想去拍VLOG，找个能看海、适合写代码的地方度周末"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        prefs = extract_preferences(query)
        print(f"偏好: {prefs.model_dump()}")
    
    print("\n" + "="*80)
    
    # 测试内容解析器
    print("2️⃣  测试内容解析器")
    print("-"*80)
    
    from services.content_parser import parse_hotels, parse_restaurants
    
    test_content = """
**海口朗廷酒店**
- 价格: ¥680/晚
- 推荐理由: 无边泳池，儿童设施完善

**梅姨海南粉**
- 人均: ¥15
- 推荐菜: 海南粉、椰子饼
"""
    
    hotels = parse_hotels(test_content, "海口")
    print(f"\n解析酒店: {len(hotels)}家")
    for hotel in hotels:
        print(f"  - {hotel.name}: ¥{hotel.price}")
    
    restaurants = parse_restaurants(test_content, "海口")
    print(f"\n解析餐厅: {len(restaurants)}家")
    for r in restaurants:
        print(f"  - {r.name}: 人均¥{r.price_per_person}")
    
    print("\n" + "="*80)
    
    # 测试 Pricing Agent
    print("3️⃣  测试 Pricing Agent")
    print("-"*80)
    
    from services.pricing_monitor import PricingMonitor
    
    monitor = PricingMonitor()
    insight = monitor.check_price("海口朗廷酒店", "海口")
    
    if insight:
        print(f"\n{insight.hotel_name}")
        print(f"  平台: {insight.platform}")
        print(f"  价格: ¥{insight.current_price}")
        print(f"  趋势: {insight.trend}")
        print(f"  建议: {insight.suggestion}")
    
    print("\n" + "="*80)
    
    # 测试 Content Agent
    print("4️⃣  测试 Content Agent")
    print("-"*80)
    
    from services.content_generator import generate_xiaohongshu
    
    content = generate_xiaohongshu(
        itinerary=[
            {'day': 1, 'theme': '慢享海口老城', 'morning': '骑楼老街', 'afternoon': '五公祠'}
        ],
        hotels=[
            {'name': '海口朗廷酒店', 'price': 680, 'features': ['泳池', '亲子']}
        ],
        destination="海口",
        preferences={'has_kids': True, 'kids_ages': [7, 4]}
    )
    
    print(f"\n生成小红书内容: {len(content)}字")
    print("\n预览:")
    for line in content.split('\n')[:10]:
        print(f"  {line}")
    
    print("\n" + "="*80)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='野游记多智能体测试')
    parser.add_argument('--mode', choices=['full', 'single'], default='full',
                       help='测试模式: full=完整链路, single=单个Agent')
    
    args = parser.parse_args()
    
    if args.mode == 'full':
        asyncio.run(test_full_pipeline())
    else:
        asyncio.run(test_single_agent())
