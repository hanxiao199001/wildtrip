"""
订单服务
"""
from models import db, Order, OrderStatus
from datetime import datetime, timedelta
import uuid
from loguru import logger


class OrderService:
    """订单服务类"""
    
    @staticmethod
    def generate_order_no():
        """生成订单号: WT + 时间戳 + 随机"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = uuid.uuid4().hex[:6].upper()
        return f"WT{timestamp}{random_str}"
    
    @staticmethod
    def create_order(
        openid: str,
        product_type: str,
        product_name: str,
        amount: int,
        client_ip: str = None,
        user_agent: str = None,
        expire_minutes: int = 30,
        remark: str = None
    ):
        """
        创建订单
        
        Args:
            openid: 用户openid
            product_type: 商品类型 (vip_month, vip_year)
            product_name: 商品名称
            amount: 金额(分)
            client_ip: 客户端IP
            user_agent: 用户代理
            expire_minutes: 过期时间(分钟)
            remark: 备注(可存储guide_id等信息)
        
        Returns:
            Order对象
        """
        try:
            order = Order(
                order_no=OrderService.generate_order_no(),
                openid=openid,
                product_type=product_type,
                product_name=product_name,
                amount=amount,
                status=OrderStatus.PENDING.value,
                created_at=datetime.now(),
                expired_at=datetime.now() + timedelta(minutes=expire_minutes),
                client_ip=client_ip,
                user_agent=user_agent,
                remark=remark
            )
            
            db.session.add(order)
            db.session.commit()
            
            logger.info(f"✅ 创建订单成功: {order.order_no} - {product_name} - {amount/100}元")
            return order
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 创建订单失败: {e}")
            raise
    
    @staticmethod
    def get_order(order_no: str):
        """获取订单"""
        return Order.query.filter_by(order_no=order_no).first()
    
    @staticmethod
    def get_order_by_transaction_id(transaction_id: str):
        """通过微信交易号获取订单"""
        return Order.query.filter_by(transaction_id=transaction_id).first()
    
    @staticmethod
    def update_order_status(
        order_no: str,
        status: OrderStatus,
        transaction_id: str = None,
        remark: str = None
    ):
        """
        更新订单状态
        
        Args:
            order_no: 订单号
            status: 新状态
            transaction_id: 微信交易号
            remark: 备注
        """
        try:
            order = OrderService.get_order(order_no)
            if not order:
                logger.error(f"订单不存在: {order_no}")
                return False
            
            order.status = status.value
            
            if transaction_id:
                order.transaction_id = transaction_id
            
            if remark:
                # 追加备注而非覆盖，保留原始的guide_id等关键信息
                if order.remark:
                    order.remark = f"{order.remark} | {remark}"
                else:
                    order.remark = remark
            
            # 更新时间戳
            if status == OrderStatus.PAID:
                order.paid_at = datetime.now()
            elif status == OrderStatus.REFUNDED:
                order.refunded_at = datetime.now()
            
            db.session.commit()
            
            logger.info(f"✅ 更新订单状态: {order_no} -> {status.value}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 更新订单状态失败: {e}")
            return False
    
    @staticmethod
    def get_user_orders(openid: str, limit: int = 20):
        """获取用户订单列表"""
        return Order.query.filter_by(openid=openid)\
            .order_by(Order.created_at.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_pending_orders(openid: str):
        """获取待支付订单"""
        now = datetime.now()
        return Order.query.filter(
            Order.openid == openid,
            Order.status == OrderStatus.PENDING.value,
            Order.expired_at > now
        ).order_by(Order.created_at.desc()).all()
    
    @staticmethod
    def cancel_expired_orders():
        """
        取消过期订单(定时任务)
        返回取消的订单数量
        """
        try:
            now = datetime.now()
            expired_orders = Order.query.filter(
                Order.status == OrderStatus.PENDING.value,
                Order.expired_at <= now
            ).all()
            
            count = 0
            for order in expired_orders:
                order.status = OrderStatus.EXPIRED.value
                count += 1
            
            db.session.commit()
            
            if count > 0:
                logger.info(f"✅ 取消过期订单: {count}个")
            
            return count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 取消过期订单失败: {e}")
            return 0
    
    @staticmethod
    def get_stats(start_date=None, end_date=None):
        """
        获取订单统计
        
        Returns:
            dict: {
                'total': 总订单数,
                'paid': 已支付订单数,
                'amount': 总金额(分),
                'pending': 待支付订单数
            }
        """
        query = Order.query
        
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        if end_date:
            query = query.filter(Order.created_at <= end_date)
        
        all_orders = query.all()
        paid_orders = [o for o in all_orders if o.status == OrderStatus.PAID.value]
        pending_orders = [o for o in all_orders if o.status == OrderStatus.PENDING.value]
        
        return {
            'total': len(all_orders),
            'paid': len(paid_orders),
            'amount': sum(o.amount for o in paid_orders),
            'pending': len(pending_orders)
        }
