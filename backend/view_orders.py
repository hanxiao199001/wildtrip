#!/usr/bin/env python3
"""
查看订单数据库
"""
from flask import Flask
from models import db, Order
from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import datetime

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


def view_orders():
    """查看所有订单"""
    with app.app_context():
        orders = Order.query.order_by(Order.created_at.desc()).all()
        
        print("\n" + "="*100)
        print(f"📊 订单数据库 ({len(orders)} 条记录)")
        print("="*100)
        
        if not orders:
            print("暂无订单")
            return
        
        # 表头
        print(f"\n{'订单号':<25} {'商品':<20} {'金额':<8} {'状态':<10} {'创建时间':<20}")
        print("-"*100)
        
        # 数据行
        for order in orders:
            amount_str = f"¥{order.amount/100:.2f}"
            created_str = order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else '-'
            
            # 状态颜色
            status_map = {
                'pending': '⏳待支付',
                'paid': '✅已支付',
                'expired': '⌛已过期',
                'refunded': '💰已退款',
                'cancelled': '❌已取消'
            }
            status_display = status_map.get(order.status, order.status)
            
            print(f"{order.order_no:<25} {order.product_name:<20} {amount_str:<8} {status_display:<12} {created_str:<20}")
        
        # 统计
        print("\n" + "-"*100)
        total_amount = sum(o.amount for o in orders if o.status == 'paid')
        paid_count = len([o for o in orders if o.status == 'paid'])
        pending_count = len([o for o in orders if o.status == 'pending'])
        
        print(f"\n📈 统计:")
        print(f"   总订单: {len(orders)}")
        print(f"   已支付: {paid_count} ({total_amount/100:.2f}元)")
        print(f"   待支付: {pending_count}")
        
        print("\n" + "="*100 + "\n")


if __name__ == '__main__':
    view_orders()
