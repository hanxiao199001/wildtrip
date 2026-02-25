"""
订单模型
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()


class OrderStatus(Enum):
    """订单状态"""
    PENDING = "pending"  # 待支付
    PAID = "paid"  # 已支付
    REFUNDING = "refunding"  # 退款中
    REFUNDED = "refunded"  # 已退款
    EXPIRED = "expired"  # 已过期
    CANCELLED = "cancelled"  # 已取消


class Order(db.Model):
    """订单表"""
    __tablename__ = 'orders'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 订单基本信息
    order_no = db.Column(db.String(32), unique=True, nullable=False, index=True, comment='订单号(唯一)')
    openid = db.Column(db.String(64), nullable=False, index=True, comment='用户openid')
    
    # 商品信息
    product_type = db.Column(db.String(32), nullable=False, comment='商品类型: vip_month, vip_year')
    product_name = db.Column(db.String(128), nullable=False, comment='商品名称')
    
    # 价格信息(单位:分)
    amount = db.Column(db.Integer, nullable=False, comment='订单金额(分)')
    
    # 支付信息
    payment_method = db.Column(db.String(32), default='wechat', comment='支付方式: wechat')
    transaction_id = db.Column(db.String(64), index=True, comment='微信支付交易号')
    prepay_id = db.Column(db.String(128), comment='微信预支付ID')
    
    # 订单状态
    status = db.Column(db.String(32), nullable=False, default=OrderStatus.PENDING.value, index=True, comment='订单状态')
    
    # 时间信息
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True, comment='创建时间')
    paid_at = db.Column(db.DateTime, comment='支付时间')
    expired_at = db.Column(db.DateTime, comment='过期时间')
    refunded_at = db.Column(db.DateTime, comment='退款时间')
    
    # 其他信息
    client_ip = db.Column(db.String(64), comment='客户端IP')
    user_agent = db.Column(db.String(512), comment='用户代理')
    remark = db.Column(db.Text, comment='备注')
    
    # 索引
    __table_args__ = (
        db.Index('idx_openid_status', 'openid', 'status'),
        db.Index('idx_created_at', 'created_at'),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'order_no': self.order_no,
            'openid': self.openid,
            'product_type': self.product_type,
            'product_name': self.product_name,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'expired_at': self.expired_at.isoformat() if self.expired_at else None,
            'refunded_at': self.refunded_at.isoformat() if self.refunded_at else None,
            'remark': self.remark
        }
    
    def __repr__(self):
        return f'<Order {self.order_no} - {self.status}>'
