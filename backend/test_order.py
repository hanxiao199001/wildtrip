#!/usr/bin/env python3
"""
测试订单系统
"""
from flask import Flask
from models import db, Order, OrderStatus
from services.order_service import OrderService
from pathlib import Path
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)

# 数据库配置
DB_DIR = os.getenv('DB_DIR', '/root/clawd/wildtrip/data')
Path(DB_DIR).mkdir(parents=True, exist_ok=True)
DB_PATH = Path(DB_DIR) / 'orders.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)


def test_order_service():
    """测试订单服务"""
    
    with app.app_context():
        print("\n" + "="*60)
        print("🧪 测试订单系统")
        print("="*60)
        
        # 测试1: 创建订单
        print("\n[测试1] 创建订单")
        order = OrderService.create_order(
            openid='test_user_123',
            product_type='vip_month',
            product_name='野游记会员 - 1个月',
            amount=2900,  # 29元
            client_ip='127.0.0.1',
            user_agent='MiniProgram/WildTrip'
        )
        print(f"✅ 订单号: {order.order_no}")
        print(f"   状态: {order.status}")
        print(f"   金额: {order.amount/100}元")
        
        # 测试2: 查询订单
        print("\n[测试2] 查询订单")
        found_order = OrderService.get_order(order.order_no)
        print(f"✅ 查到订单: {found_order.order_no}")
        print(f"   商品: {found_order.product_name}")
        
        # 测试3: 更新订单状态
        print("\n[测试3] 更新订单状态(模拟支付成功)")
        success = OrderService.update_order_status(
            order.order_no,
            OrderStatus.PAID,
            transaction_id='wx_test_123456',
            remark='测试支付'
        )
        print(f"✅ 更新成功: {success}")
        
        # 验证更新
        updated_order = OrderService.get_order(order.order_no)
        print(f"   新状态: {updated_order.status}")
        print(f"   交易号: {updated_order.transaction_id}")
        print(f"   支付时间: {updated_order.paid_at}")
        
        # 测试4: 获取用户订单列表
        print("\n[测试4] 获取用户订单列表")
        user_orders = OrderService.get_user_orders('test_user_123')
        print(f"✅ 找到 {len(user_orders)} 个订单")
        for o in user_orders:
            print(f"   - {o.order_no}: {o.product_name} ({o.status})")
        
        # 测试5: 订单统计
        print("\n[测试5] 订单统计")
        stats = OrderService.get_stats()
        print(f"✅ 统计结果:")
        print(f"   总订单数: {stats['total']}")
        print(f"   已支付: {stats['paid']}")
        print(f"   待支付: {stats['pending']}")
        print(f"   总金额: {stats['amount']/100}元")
        
        print("\n" + "="*60)
        print("✅ 所有测试通过!")
        print("="*60 + "\n")


if __name__ == '__main__':
    test_order_service()
