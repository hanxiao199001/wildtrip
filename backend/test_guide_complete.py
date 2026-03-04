#!/usr/bin/env python3
"""
测试攻略解锁完整流程 (模拟支付)
"""
from flask import Flask
from models import db, Order, OrderStatus
from services.order_service import OrderService
from api.vip import GUIDE_PRODUCTS
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


def test_guide_unlock_flow():
    """测试攻略解锁流程"""
    
    with app.app_context():
        print("\n" + "="*70)
        print("🧪 测试攻略解锁支付流程")
        print("="*70)
        
        test_openid = 'test_guide_user_001'
        guide_id_travel = 'guide_beijing_3days'
        guide_id_history = 'guide_xian_history'
        
        # 步骤1: 查看攻略商品
        print("\n[步骤1] 攻略商品列表")
        for product_id, product in GUIDE_PRODUCTS.items():
            print(f"✅ {product['name']}: ¥{product['amount']/100} (type: {product['type']})")
        
        # 步骤2: 创建旅行攻略订单
        print("\n[步骤2] 创建旅行攻略订单")
        product_travel = GUIDE_PRODUCTS['guide_travel']
        order_travel = OrderService.create_order(
            openid=test_openid,
            product_type='guide_travel',
            product_name=f"{product_travel['name']} - {guide_id_travel}",
            amount=product_travel['amount'],
            client_ip='127.0.0.1',
            remark=f"guide_id:{guide_id_travel}"
        )
        print(f"✅ 订单号: {order_travel.order_no}")
        print(f"   攻略ID: {guide_id_travel}")
        print(f"   商品: {order_travel.product_name}")
        print(f"   金额: ¥{order_travel.amount/100}")
        
        # 步骤3: 创建人文历史订单
        print("\n[步骤3] 创建人文历史订单")
        product_history = GUIDE_PRODUCTS['guide_history']
        order_history = OrderService.create_order(
            openid=test_openid,
            product_type='guide_history',
            product_name=f"{product_history['name']} - {guide_id_history}",
            amount=product_history['amount'],
            client_ip='127.0.0.1',
            remark=f"guide_id:{guide_id_history}"
        )
        print(f"✅ 订单号: {order_history.order_no}")
        print(f"   攻略ID: {guide_id_history}")
        print(f"   商品: {order_history.product_name}")
        print(f"   金额: ¥{order_history.amount/100}")
        
        # 步骤4: 模拟支付成功 (旅行攻略)
        print("\n[步骤4] 模拟支付成功 - 旅行攻略")
        OrderService.update_order_status(
            order_no=order_travel.order_no,
            status=OrderStatus.PAID,
            transaction_id='wx_test_travel_123',
            remark=order_travel.remark
        )
        print(f"✅ 订单已支付: {order_travel.order_no}")
        
        # 步骤5: 模拟支付成功 (人文历史)
        print("\n[步骤5] 模拟支付成功 - 人文历史")
        OrderService.update_order_status(
            order_no=order_history.order_no,
            status=OrderStatus.PAID,
            transaction_id='wx_test_history_456',
            remark=order_history.remark
        )
        print(f"✅ 订单已支付: {order_history.order_no}")
        
        # 步骤6: 检查攻略解锁状态
        print("\n[步骤6] 检查攻略解锁状态")
        
        # 检查旅行攻略
        orders = OrderService.get_user_orders(test_openid, limit=100)
        travel_unlocked = False
        history_unlocked = False
        
        for order in orders:
            if order.status == OrderStatus.PAID.value:
                if guide_id_travel in (order.remark or ''):
                    travel_unlocked = True
                    print(f"✅ 旅行攻略已解锁: {guide_id_travel}")
                    print(f"   订单号: {order.order_no}")
                    print(f"   金额: ¥{order.amount/100}")
                
                if guide_id_history in (order.remark or ''):
                    history_unlocked = True
                    print(f"✅ 人文历史已解锁: {guide_id_history}")
                    print(f"   订单号: {order.order_no}")
                    print(f"   金额: ¥{order.amount/100}")
        
        # 步骤7: 获取已解锁攻略列表
        print("\n[步骤7] 已解锁攻略列表")
        unlocked_guides = []
        for order in orders:
            if order.status == OrderStatus.PAID.value and order.product_type.startswith('guide_'):
                guide_id = None
                if order.remark and 'guide_id:' in order.remark:
                    guide_id = order.remark.split('guide_id:')[1].strip()
                
                unlocked_guides.append({
                    'guide_id': guide_id,
                    'product_name': order.product_name,
                    'amount': order.amount,
                    'paid_at': order.paid_at
                })
        
        print(f"✅ 已解锁 {len(unlocked_guides)} 个攻略:")
        for guide in unlocked_guides:
            print(f"   - {guide['guide_id']}: {guide['product_name']} (¥{guide['amount']/100})")
        
        # 步骤8: 订单统计
        print("\n[步骤8] 订单统计")
        stats = OrderService.get_stats()
        print(f"✅ 总订单: {stats['total']}")
        print(f"   已支付: {stats['paid']} (¥{stats['amount']/100:.2f})")
        print(f"   待支付: {stats['pending']}")
        
        # 按类型统计
        travel_orders = [o for o in orders if o.product_type == 'guide_travel' and o.status == OrderStatus.PAID.value]
        history_orders = [o for o in orders if o.product_type == 'guide_history' and o.status == OrderStatus.PAID.value]
        
        print(f"\n   旅行攻略: {len(travel_orders)} 个 (¥{sum(o.amount for o in travel_orders)/100:.2f})")
        print(f"   人文历史: {len(history_orders)} 个 (¥{sum(o.amount for o in history_orders)/100:.2f})")
        
        print("\n" + "="*70)
        print("✅ 攻略解锁流程测试通过!")
        print("="*70 + "\n")


if __name__ == '__main__':
    test_guide_unlock_flow()
