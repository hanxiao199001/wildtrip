#!/usr/bin/env python3
"""
测试通义千问 API 配置
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.ai_engine import AIEngine
from loguru import logger

# 配置日志
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | {message}")


def test_qwen_api():
    """测试通义千问 API"""
    
    print("="*70)
    print("🧪 测试通义千问 API 配置")
    print("="*70)
    
    # 检查环境变量
    api_key = os.getenv('AI_API_KEY', '')
    base_url = os.getenv('AI_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
    model = os.getenv('AI_MODEL', 'qwen-plus')
    
    print(f"\n配置信息：")
    print(f"  API Key: {api_key[:20]}..." if api_key else "  ❌ API Key 未配置")
    print(f"  Base URL: {base_url}")
    print(f"  Model: {model}")
    print()
    
    if not api_key:
        print("❌ 请先配置 AI_API_KEY 环境变量")
        print("\n配置方法：")
        print("  export AI_API_KEY='sk-xxxxxxxx'")
        print("  export AI_BASE_URL='https://dashscope.aliyuncs.com/compatible-mode/v1'")
        print("  export AI_MODEL='qwen-plus'")
        return False
    
    # 创建 AI 引擎
    engine = AIEngine()
    
    # 测试问题
    test_prompt = """
你是一个友好的酒店AI客服助手。

客人问：你们能带宠物吗？

请简短回复（50字以内），语气友好自然。
"""
    
    print("📝 测试问题：你们能带宠物吗？")
    print("⏳ 正在调用 API...\n")
    
    try:
        reply = engine.generate(
            prompt=test_prompt,
            query="你们能带宠物吗？",
            mode='chat'
        )
        
        print("✅ API 调用成功！")
        print(f"\n回复内容：\n{reply}\n")
        print("="*70)
        print("🎉 通义千问 API 配置正确，可以正常使用！")
        print("="*70)
        return True
    
    except Exception as e:
        print(f"\n❌ API 调用失败：{e}")
        print("\n常见问题：")
        print("  1. API Key 是否正确？")
        print("  2. API Key 是否有余额？")
        print("  3. Base URL 是否正确？")
        print(f"     当前：{base_url}")
        print(f"     应该：https://dashscope.aliyuncs.com/compatible-mode/v1")
        return False


def test_saas_conversation():
    """测试 SaaS 对话功能（使用通义千问）"""
    
    print("\n" + "="*70)
    print("🤖 测试 SaaS 对话功能")
    print("="*70)
    
    from saas.conversation.intent_classifier import get_intent
    from saas.conversation.context_manager import get_context_manager
    from saas.ai.hotel_qa_engine import HotelQAEngine, DEMO_HOTEL_KB
    
    hotel_id = "hotel_qwen_test"
    user_id = "test_user_001"
    
    engine = HotelQAEngine(hotel_id, "海边小筑")
    ctx_manager = get_context_manager()
    
    test_questions = [
        "你们能带狗吗？",
        "周末带孩子去你们那有什么好玩的？",
        "多少钱一晚？"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n【问题 {i}】 {question}")
        print("-"*70)
        
        # 获取上下文
        context = ctx_manager.get_or_create_context(hotel_id, user_id)
        
        # 识别意图
        intent = get_intent(question)
        print(f"意图: {intent}")
        
        # 添加用户消息
        context.add_message('user', question, intent=intent)
        
        # 生成回复
        try:
            reply = engine.answer_question(
                question=question,
                context=context.get_context_for_ai(),
                intent=intent,
                hotel_kb=DEMO_HOTEL_KB
            )
            
            # 添加助手回复
            context.add_message('assistant', reply)
            
            print(f"\n回复:\n{reply}")
        
        except Exception as e:
            print(f"❌ 生成失败: {e}")
    
    print("\n" + "="*70)


if __name__ == '__main__':
    # 先测试 API 配置
    if test_qwen_api():
        # API 配置正确，继续测试对话
        test_saas_conversation()
    else:
        print("\n请先修复 API 配置问题再测试对话功能。")
