"""
用户模型
"""
from datetime import datetime
from models.order import db


class User(db.Model):
    """用户表"""
    __tablename__ = 'users'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 用户标识
    openid = db.Column(db.String(64), unique=True, nullable=False, index=True, comment='微信openid')
    unionid = db.Column(db.String(64), index=True, comment='微信unionid')
    
    # 用户信息
    nickname = db.Column(db.String(128), comment='昵称')
    avatar = db.Column(db.String(512), comment='头像URL')
    gender = db.Column(db.Integer, default=0, comment='性别: 0未知 1男 2女')
    
    # VIP信息
    is_vip = db.Column(db.Boolean, default=False, nullable=False, index=True, comment='是否VIP')
    vip_expire_at = db.Column(db.DateTime, index=True, comment='VIP到期时间')
    vip_activated_at = db.Column(db.DateTime, comment='VIP首次激活时间')
    
    # 统计信息
    generate_count = db.Column(db.Integer, default=0, comment='生成攻略次数')
    order_count = db.Column(db.Integer, default=0, comment='订单数量')
    total_paid = db.Column(db.Integer, default=0, comment='累计消费(分)')
    
    # 时间戳
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True, comment='注册时间')
    last_login_at = db.Column(db.DateTime, comment='最后登录时间')
    
    # 索引
    __table_args__ = (
        db.Index('idx_vip_status', 'is_vip', 'vip_expire_at'),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'openid': self.openid,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'gender': self.gender,
            'is_vip': self.is_vip,
            'vip_expire_at': self.vip_expire_at.isoformat() if self.vip_expire_at else None,
            'vip_activated_at': self.vip_activated_at.isoformat() if self.vip_activated_at else None,
            'generate_count': self.generate_count,
            'order_count': self.order_count,
            'total_paid': self.total_paid,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None
        }
    
    def vip_days_left(self):
        """计算VIP剩余天数"""
        if not self.is_vip or not self.vip_expire_at:
            return 0
        
        now = datetime.now()
        if self.vip_expire_at <= now:
            return 0
        
        delta = self.vip_expire_at - now
        return delta.days
    
    def __repr__(self):
        return f'<User {self.openid} VIP:{self.is_vip}>'
