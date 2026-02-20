"""
酒店 AI 客服问答引擎
"""
import logging
from typing import Optional
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.ai_engine import AIEngine

logger = logging.getLogger(__name__)


class HotelQAEngine:
    """
    酒店问答引擎
    """
    
    def __init__(self, hotel_id, hotel_name="民宿"):
        self.hotel_id = hotel_id
        self.hotel_name = hotel_name
        self.ai_engine = AIEngine()
    
    def answer_question(self, question, context="", intent=None, hotel_kb=None):
        """
        回答用户问题
        
        Args:
            question: 用户问题
            context: 对话历史上下文
            intent: 识别的意图
            hotel_kb: 酒店知识库（dict）
        
        Returns:
            str: AI 生成的回复
        """
        # 构建 Prompt
        prompt = self._build_prompt(question, context, intent, hotel_kb)
        
        # 调用 AI
        try:
            reply = self.ai_engine.generate(prompt, question, mode='chat')
            logger.info(f"[{self.hotel_id}] AI replied: {reply[:100]}...")
            return reply
        except Exception as e:
            logger.error(f"AI generation error: {e}", exc_info=True)
            return "抱歉，我现在有点忙，请稍后再试～或者您可以直接加我们管家微信：wildtrip001"
    
    def _build_prompt(self, question, context, intent, hotel_kb):
        """
        构建 AI Prompt
        """
        # 基础系统 Prompt
        system_prompt = f"""
你是"{self.hotel_name}"的AI客服助手，性格友好、专业、贴心。

你的任务是：
1. 回答客人关于酒店的问题
2. 推荐周边小众玩法（避开网红景点）
3. 引导客人预订或添加管家微信

回复要求：
- 语气亲切自然，像朋友聊天，不要过于正式
- 回答简洁，控制在150字以内（除非是攻略推荐）
- 用 emoji 增加亲和力（但不要过多）
- 如果不知道答案，诚实告知"这个我需要确认一下"
"""
        
        # 添加酒店知识库（如果有）
        if hotel_kb:
            kb_text = self._format_knowledge_base(hotel_kb)
            system_prompt += f"\n\n【酒店信息】\n{kb_text}"
        
        # 添加对话历史
        if context:
            system_prompt += f"\n\n【对话历史】\n{context}"
        
        # 根据意图添加特定引导
        if intent == 'BOOKING':
            system_prompt += """

【预订引导】
如果客人询问房价或预订，请：
1. 简单介绍房型和价格
2. 引导添加管家微信：wildtrip001（可领取专属优惠）
3. 语气示例："周末想来的话，加我们管家微信 wildtrip001，发'野游记'可以领券哦～"
"""
        
        elif intent == 'ACTIVITY':
            system_prompt += """

【活动推荐】
推荐周边玩法时，请：
1. 避开网红景点，推荐小众、本地人才知道的地方
2. 具体到时间和体验："下午4点可以去..."
3. 带情绪价值，让客人觉得超值
4. 引导预订："看起来不错的话，直接预订我们的房间，我把详细攻略发给你～"
"""
        
        # 用户问题
        user_prompt = f"客人问：{question}"
        
        full_prompt = f"{system_prompt}\n\n{user_prompt}\n\n请回复："
        
        return full_prompt
    
    def _format_knowledge_base(self, hotel_kb):
        """
        格式化酒店知识库为文本
        """
        if not hotel_kb:
            return ""
        
        kb_lines = []
        
        # 基础信息
        if 'basic_info' in hotel_kb:
            kb_lines.append("基础信息：")
            for key, value in hotel_kb['basic_info'].items():
                kb_lines.append(f"  - {key}: {value}")
        
        # 常见问题
        if 'faq' in hotel_kb:
            kb_lines.append("\n常见问题：")
            for qa in hotel_kb['faq']:
                kb_lines.append(f"  Q: {qa['question']}")
                kb_lines.append(f"  A: {qa['answer']}")
        
        # 周边玩法
        if 'activities' in hotel_kb:
            kb_lines.append("\n周边玩法：")
            for activity in hotel_kb['activities']:
                kb_lines.append(f"  - {activity['title']}: {activity['description']}")
        
        return "\n".join(kb_lines)


# 示例：酒店知识库数据结构
DEMO_HOTEL_KB = {
    "basic_info": {
        "酒店名称": "海边小筑民宿",
        "地址": "海南省万宁市石梅湾",
        "房型": "海景大床房(¥580)、亲子套房(¥780)",
        "入住时间": "14:00",
        "退房时间": "12:00",
        "早餐": "7:30-9:30，阿姨现做海南粉、鸡蛋、椰子饼",
        "停车": "免费停车",
        "管家微信": "wildtrip001"
    },
    "faq": [
        {
            "question": "能带宠物吗？",
            "answer": "可以带10kg以下的小型犬和猫咪，需要提前告知我们准备宠物垫。收取100元宠物清洁费。"
        },
        {
            "question": "有儿童设施吗？",
            "answer": "有儿童拖鞋、儿童牙刷、儿童浴袍（2-12岁），还有玩具角（乐高、绘本、积木）。"
        },
        {
            "question": "怎么去你们那？",
            "answer": "从海口出发约1.5小时车程，导航'石梅湾海边小筑'即可。我们提供免费接站服务（需提前预约）。"
        }
    ],
    "activities": [
        {
            "title": "野海滩抓螃蟹",
            "description": "距离酒店5分钟步行，下午4点退潮，带孩子去抓螃蟹，晚上可以让厨房帮忙加工"
        },
        {
            "title": "骑行椰林小道",
            "description": "我们有免费自行车，沿着海边骑到渔村，路上都是椰子树，约30分钟"
        },
        {
            "title": "本地海鲜排档",
            "description": "镇上15分钟车程，没招牌的老店，本地人都去，我们可以帮忙预订"
        }
    ]
}


# 测试代码
if __name__ == '__main__':
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建引擎
    engine = HotelQAEngine("hotel_001", "海边小筑")
    
    # 测试问题
    test_questions = [
        "你们能带宠物吗？",
        "周末带孩子去你们那有什么好玩的？",
        "多少钱一晚？",
        "早餐几点？"
    ]
    
    for q in test_questions:
        print(f"\n{'='*60}")
        print(f"Q: {q}")
        print(f"{'='*60}")
        
        # 识别意图
        from saas.conversation.intent_classifier import get_intent
        intent = get_intent(q)
        print(f"Intent: {intent}")
        
        # 生成回复
        reply = engine.answer_question(
            question=q,
            context="",
            intent=intent,
            hotel_kb=DEMO_HOTEL_KB
        )
        
        print(f"\nA: {reply}")
