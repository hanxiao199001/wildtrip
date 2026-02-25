#!/usr/bin/env python3
"""
测试完整的VIP支付流程
"""
from flask import Flask
from models import db, Order, User, OrderStatus
from services.order_service import OrderService
from services.user_service import UserService
from api.vip import VIP_PRODUCTS
from pathlib import Path
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)

# 数据库配置
DB_DIR = os.getenv('DB_DIR', '/root/clawd/wildtrip/data')
DB_PATH = Path(DB_DIR) / 'orders.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


def test_complete_flow():
    """测试完整流程"""
    
    with app.app_context():
        print("\n" + "="*70)
        print("🧪 测试VIP支付完整流程")
        print("="*70)
        
        test_openid = 'test_vip_user_002'
        
        # 步骤1: 创建/获取用户
        print("\n[步骤1] 创建用户")
        user = UserService.get_or_create_user(test_openid)
        print(f"✅ 用户openid: {user.openid}")
        print(f"   VIP状态: {user.is_vip}")
        print(f"   生成次数: {user.generate_count}")
        
        # 步骤2: 查看VIP商品
        print("\n[步骤2] VIP商品列表")
        for product_id, product in VIP_PRODUCTS.items():
            print(f"✅ {product['name']}: ¥{product['amount']/100} ({product['duration_days']}天)")
        
        # 步骤3: 创建订单
        print("\n[步骤3] 创建VIP订单")
        product = VIP_PRODUCTS['vip_month']
        order = OrderService.create_order(
            openid=test_openid,
            product_type='vip_month',
            product_name=product['name'],
            amount=product['amount'],
            client_ip='127.0.0.1'
        )
        print(f"✅ 订单号: {order.order_no}")
        print(f"   商品: {order.product_name}")
        print(f"   金额: ¥{order.amount/100}")
        print(f"   状态: {order.status}")
        
        # 步骤4: 模拟支付成功
        print("\n[步骤4] 模拟支付成功")
        OrderService.update_order_status(
            order_no=order.order_no,
            status=OrderStatus.PAID,
            transaction_id='wx_test_payment_123',
            remark='测试支付'
        )
        print(f"✅ 订单状态已更新: {order.order_no} -> paid")
        
        # 步骤5: 激活VIP
        print("\n[步骤5] 激活VIP")
        user = UserService.activate_vip(test_openid, product['duration_days'])
        print(f"✅ VIP已激活!")
        print(f"   到期时间: {user.vip_expire_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   剩余天数: {user.vip_days_left()}天")
        
        # 步骤6: 更新用户统计
        print("\n[步骤6] 更新用户统计")
        UserService.add_paid_amount(test_openid, product['amount'])
        UserService.increment_generate_count(test_openid)
        
        user = User.query.filter_by(openid=test_openid).first()
        print(f"✅ 累计消费: ¥{user.total_paid/100}")
        print(f"   生成次数: {user.generate_count}")
        print(f"   订单数量: {user.order_count}")
        
        # 步骤7: 检查VIP状态
        print("\n[步骤7] 检查VIP状态")
        vip_status = UserService.check_vip_status(test_openid)
        print(f"✅ VIP状态: {vip_status['is_vip']}")
        print(f"   到期时间: {vip_status['expire_at']}")
        print(f"   剩余天数: {vip_status['days_left']}天")
        
        # 步骤8: 查询订单历史
        print("\n[步骤8] 查询订单历史")
        orders = OrderService.get_user_orders(test_openid)
        print(f"✅ 找到 {len(orders)} 个订单:")
        for o in orders:
            print(f"   - {o.order_no}: {o.product_name} (¥{o.amount/100}) - {o.status}")
        
        # 步骤9: 订单统计
        print("\n[步骤9] 全局订单统计")
        stats = OrderService.get_stats()
        print(f"✅ 总订单: {stats['total']}")
        print(f"   已支付: {stats['paid']} (¥{stats['amount']/100:.2f})")
        print(f"   待支付: {stats['pending']}")
        
        # 步骤10: VIP用户列表
        print("\n[步骤10] VIP用户列表")
        vip_users = UserService.get_vip_users()
        print(f"✅ 当前VIP用户: {len(vip_users)}人")
        for u in vip_users:
            days_left = u.vip_days_left()
            print(f"   - {u.openid}: 剩余{days_left}天 (到期: {u.vip_expire_at.strftime('%Y-%m-%d')})")
        
        print("\n" + "="*70)
        print("✅ 完整流程测试通过!")
        print("="*70 + "\n")


if __name__ == '__main__':
    test_complete_flow()
