#!/usr/bin/env python3
"""
对话测试脚本（不需要微信接入）
"""
import sys
import os
import logging

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from saas.conversation.intent_classifier import get_intent
from saas.conversation.context_manager import get_context_manager
from saas.ai.hotel_qa_engine import HotelQAEngine, DEMO_HOTEL_KB

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

logger = logging.getLogger(__name__)


def test_conversation():
    """
    模拟对话测试
    """
    hotel_id = "hotel_demo_001"
    user_id = "test_user_123"
    
    # 创建引擎
    engine = HotelQAEngine(hotel_id, "海边小筑")
    ctx_manager = get_context_manager()
    
    print("="*70)
    print("🤖 野游记 AI 客服测试")
    print("="*70)
    print("提示：输入 'quit' 退出，输入 'reset' 重置对话")
    print("="*70)
    print()
    
    while True:
        # 用户输入
        user_input = input("\n👤 客人: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() == 'quit':
            print("\n再见！👋")
            break
        
        if user_input.lower() == 'reset':
            # 重置对话上下文
            ctx_manager.contexts.pop(f"{hotel_id}_{user_id}", None)
            print("\n✅ 对话已重置\n")
            continue
        
        try:
            # 获取上下文
            context = ctx_manager.get_or_create_context(hotel_id, user_id)
            
            # 识别意图
            intent = get_intent(user_input)
            print(f"   [Intent: {intent}]")
            
            # 添加用户消息
            context.add_message('user', user_input, intent=intent)
            
            # 生成回复
            reply = engine.answer_question(
                question=user_input,
                context=context.get_context_for_ai(),
                intent=intent,
                hotel_kb=DEMO_HOTEL_KB
            )
            
            # 添加助手回复
            context.add_message('assistant', reply)
            
            # 显示回复
            print(f"\n🤖 AI助手: {reply}\n")
            print("-"*70)
        
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            print(f"\n❌ 出错了: {e}\n")


def test_batch_questions():
    """
    批量测试问题
    """
    hotel_id = "hotel_demo_001"
    user_id = "batch_test_user"
    
    engine = HotelQAEngine(hotel_id, "海边小筑")
    
    test_cases = [
        "你们能带狗吗？",
        "周末带孩子去你们那有什么好玩的？",
        "多少钱一晚？",
        "早餐几点开始？",
        "怎么去你们酒店？",
        "有停车位吗？",
        "可以延迟退房吗？",
    ]
    
    print("="*70)
    print("📋 批量测试")
    print("="*70)
    
    for i, question in enumerate(test_cases, 1):
        print(f"\n【测试 {i}/{len(test_cases)}】")
        print(f"Q: {question}")
        
        intent = get_intent(question)
        print(f"Intent: {intent}")
        
        reply = engine.answer_question(
            question=question,
            context="",
            intent=intent,
            hotel_kb=DEMO_HOTEL_KB
        )
        
        print(f"\nA: {reply}")
        print("-"*70)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'batch':
        # 批量测试
        test_batch_questions()
    else:
        # 交互式对话
        test_conversation()
