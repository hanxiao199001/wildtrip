"""
对话上下文管理
"""
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class ConversationContext:
    """
    单个用户的对话上下文
    """
    
    def __init__(self, hotel_id, user_id):
        self.hotel_id = hotel_id
        self.user_id = user_id
        self.messages = []  # 消息历史
        self.current_intent = None  # 当前意图
        self.state = {}  # 状态变量（如：是否已询问房型、是否已推荐活动）
        self.created_at = datetime.now()
        self.last_active_at = datetime.now()
    
    def add_message(self, role, content, intent=None):
        """
        添加消息到历史
        
        Args:
            role: 'user' 或 'assistant'
            content: 消息内容
            intent: 意图（仅user消息有）
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        if intent:
            message['intent'] = intent
        
        self.messages.append(message)
        self.last_active_at = datetime.now()
        
        logger.info(f"[{self.hotel_id}/{self.user_id}] Added {role} message: {content[:50]}...")
    
    def get_recent_messages(self, n=5):
        """
        获取最近的 n 条消息
        """
        return self.messages[-n:] if len(self.messages) > n else self.messages
    
    def get_context_for_ai(self):
        """
        返回给 AI 的对话上下文
        格式化为易读的文本
        """
        recent = self.get_recent_messages(5)
        
        context_lines = []
        for msg in recent:
            role_name = "客人" if msg['role'] == 'user' else "助手"
            context_lines.append(f"{role_name}: {msg['content']}")
        
        return "\n".join(context_lines)
    
    def update_state(self, key, value):
        """
        更新状态变量
        """
        self.state[key] = value
        logger.info(f"[{self.hotel_id}/{self.user_id}] State updated: {key}={value}")
    
    def get_state(self, key, default=None):
        """
        获取状态变量
        """
        return self.state.get(key, default)
    
    def is_expired(self, timeout_minutes=30):
        """
        检查会话是否过期（超过 timeout_minutes 未活跃）
        """
        delta = datetime.now() - self.last_active_at
        return delta.total_seconds() > timeout_minutes * 60
    
    def to_dict(self):
        """
        序列化为字典（用于存储到数据库）
        """
        return {
            'hotel_id': self.hotel_id,
            'user_id': self.user_id,
            'messages': self.messages,
            'current_intent': self.current_intent,
            'state': self.state,
            'created_at': self.created_at.isoformat(),
            'last_active_at': self.last_active_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        从字典恢复对象
        """
        ctx = cls(data['hotel_id'], data['user_id'])
        ctx.messages = data.get('messages', [])
        ctx.current_intent = data.get('current_intent')
        ctx.state = data.get('state', {})
        ctx.created_at = datetime.fromisoformat(data['created_at'])
        ctx.last_active_at = datetime.fromisoformat(data['last_active_at'])
        return ctx


class ContextManager:
    """
    全局上下文管理器（管理所有用户的上下文）
    """
    
    def __init__(self):
        # 内存存储（后续可以改为 Redis）
        self.contexts = {}  # key: f"{hotel_id}_{user_id}", value: ConversationContext
    
    def get_or_create_context(self, hotel_id, user_id):
        """
        获取或创建用户上下文
        """
        key = f"{hotel_id}_{user_id}"
        
        if key in self.contexts:
            ctx = self.contexts[key]
            
            # 检查是否过期，过期则重置
            if ctx.is_expired():
                logger.info(f"Context expired for {key}, creating new")
                ctx = ConversationContext(hotel_id, user_id)
                self.contexts[key] = ctx
        else:
            ctx = ConversationContext(hotel_id, user_id)
            self.contexts[key] = ctx
            logger.info(f"Created new context for {key}")
        
        return ctx
    
    def cleanup_expired(self):
        """
        清理过期的上下文（定时任务调用）
        """
        expired_keys = []
        for key, ctx in self.contexts.items():
            if ctx.is_expired():
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.contexts[key]
            logger.info(f"Cleaned up expired context: {key}")
        
        return len(expired_keys)


# 全局单例
_context_manager = ContextManager()


def get_context_manager():
    """
    获取全局上下文管理器
    """
    return _context_manager
