#!/usr/bin/env python3
"""
测试美团联盟链接生成
"""

import sys
sys.path.insert(0, '/root/clawd/wildtrip-existing/backend')

from services.affiliate_manager import get_affiliate_manager
from dotenv import load_dotenv

load_dotenv()

# 获取管理器实例
manager = get_affiliate_manager()

print("=" * 60)
print("🔥 美团联盟链接测试")
print("=" * 60)

print(f"\n📌 配置信息:")
print(f"PID: {manager.meituan_pid}")
print(f"ActID: {manager.meituan_act_id}")
print(f"SID: {manager.meituan_sid}")

# 测试餐厅链接
print(f"\n1️⃣ 测试餐厅链接:")
restaurant_link = manager.generate_booking_link('restaurant', '海南文昌鸡饭', '海口')
print(f"URL: {restaurant_link['url']}")
print(f"有返佣: {restaurant_link['has_commission']}")
print(f"平台: {restaurant_link['platform']}")
print(f"状态: {restaurant_link['status']}")

# 测试酒店链接
print(f"\n2️⃣ 测试酒店链接:")
hotel_link = manager.generate_booking_link('hotel', '希尔顿酒店', '海口')
print(f"URL: {hotel_link['url']}")
print(f"有返佣: {hotel_link['has_commission']}")
print(f"平台: {hotel_link['platform']}")
print(f"状态: {hotel_link['status']}")

# 测试门票链接
print(f"\n3️⃣ 测试门票链接:")
ticket_link = manager.generate_booking_link('ticket', '火山口公园', '海口')
print(f"URL: {ticket_link['url']}")
print(f"有返佣: {ticket_link['has_commission']}")
print(f"平台: {ticket_link['platform']}")
print(f"状态: {ticket_link['status']}")

print("\n" + "=" * 60)
print("✅ 所有链接都应该包含联盟参数：actId, sid, pid")
print("=" * 60)
