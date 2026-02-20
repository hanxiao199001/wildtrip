"""
用户意图识别
"""
import logging

logger = logging.getLogger(__name__)


class IntentClassifier:
    """
    用户意图分类器
    """
    
    # 意图关键词映射
    INTENT_KEYWORDS = {
        'BOOKING': [
            '预订', '订房', '有房', '多少钱', '价格', '房型',
            '入住', '退房', '空房', '房间'
        ],
        'ACTIVITY': [
            '好玩', '景点', '玩', '周边', '推荐', '去哪',
            '附近', '逛', '游玩', '带孩子'
        ],
        'PET': [
            '宠物', '狗', '猫', '带狗', '带猫', '可以带'
        ],
        'FACILITIES': [
            '儿童', '拖鞋', '牙刷', '早餐', '吃', '设施',
            '停车', '接送', 'wifi', '洗衣'
        ],
        'LOCATION': [
            '怎么去', '地址', '路线', '导航', '远吗', '交通'
        ],
        'CHECKIN': [
            '入住时间', '退房时间', '几点', '办理', '取消'
        ]
    }
    
    def classify(self, user_message):
        """
        分类用户意图
        
        Returns:
            str: 意图类型 (BOOKING/ACTIVITY/PET/FACILITIES/LOCATION/CHECKIN/UNKNOWN)
        """
        message = user_message.lower()
        
        # 遍历关键词，找第一个匹配的意图
        for intent, keywords in self.INTENT_KEYWORDS.items():
            if any(keyword in message for keyword in keywords):
                logger.info(f"Intent classified: {intent} for message: {user_message}")
                return intent
        
        # 如果没有匹配到，返回 UNKNOWN
        logger.info(f"Intent UNKNOWN for message: {user_message}")
        return 'UNKNOWN'
    
    def classify_with_ai(self, user_message):
        """
        使用 AI 进行意图识别（更准确但更慢）
        暂未实现，留作后续优化
        """
        # TODO: 调用 DeepSeek API 进行意图识别
        pass


# 全局实例
classifier = IntentClassifier()


def get_intent(message):
    """
    便捷函数：获取消息意图
    """
    return classifier.classify(message)
