#!/usr/bin/env python3
"""
测试VIP API
"""
import requests
import json

BASE_URL = 'http://localhost:5000'


def test_vip_products():
    """测试获取VIP商品列表"""
    print("\n" + "="*60)
    print("📦 测试: 获取VIP商品列表")
    print("="*60)
    
    url = f"{BASE_URL}/api/vip/products"
    response = requests.get(url)
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    if data['success']:
        print(f"\n✅ 找到 {len(data['products'])} 个VIP商品:")
        for product in data['products']:
            print(f"   - {product['name']}: ¥{product['price']} ({product['duration_days']}天)")


def test_create_vip_order():
    """测试创建VIP订单"""
    print("\n" + "="*60)
    print("💳 测试: 创建VIP订单")
    print("="*60)
    
    url = f"{BASE_URL}/api/vip/create_order"
    payload = {
        'openid': 'test_user_vip_001',
        'product_id': 'vip_month'
    }
    
    response = requests.post(url, json=payload)
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    if data['success']:
        order = data['order']
        print(f"\n✅ 订单创建成功:")
        print(f"   订单号: {order['order_no']}")
        print(f"   商品: {order['product_name']}")
        print(f"   金额: ¥{order['amount']/100}")
        print(f"   状态: {order['status']}")
        return order['order_no']
    else:
        print(f"\n❌ 失败: {data.get('error')}")
        return None


def test_query_order(order_id):
    """测试查询订单"""
    print("\n" + "="*60)
    print("🔍 测试: 查询订单")
    print("="*60)
    
    url = f"{BASE_URL}/api/payment/query_order?order_id={order_id}"
    response = requests.get(url)
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    if data['success']:
        order = data['order']
        print(f"\n✅ 订单详情:")
        print(f"   订单号: {order['order_no']}")
        print(f"   状态: {order['status']}")
        print(f"   金额: ¥{order['amount']/100}")


def test_my_orders():
    """测试我的订单列表"""
    print("\n" + "="*60)
    print("📋 测试: 我的订单列表")
    print("="*60)
    
    url = f"{BASE_URL}/api/payment/my_orders?openid=test_user_vip_001"
    response = requests.get(url)
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    
    if data['success']:
        print(f"\n✅ 找到 {data['total']} 个订单:")
        for order in data['orders']:
            print(f"   - {order['order_no']}: {order['product_name']} - ¥{order['amount']/100} ({order['status']})")
    else:
        print(f"\n❌ 失败: {data.get('error')}")


def test_payment_stats():
    """测试订单统计"""
    print("\n" + "="*60)
    print("📊 测试: 订单统计")
    print("="*60)
    
    url = f"{BASE_URL}/api/payment/stats"
    response = requests.get(url)
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    if data['success']:
        stats = data['stats']
        print(f"\n✅ 统计结果:")
        print(f"   总订单: {stats['total']}")
        print(f"   已支付: {stats['paid']}")
        print(f"   待支付: {stats['pending']}")
        print(f"   总金额: ¥{stats['amount']/100:.2f}")


if __name__ == '__main__':
    print("\n🧪 开始测试VIP API...")
    
    # 测试1: 获取商品列表
    test_vip_products()
    
    # 测试2: 创建VIP订单
    order_id = test_create_vip_order()
    
    if order_id:
        # 测试3: 查询订单
        test_query_order(order_id)
        
        # 测试4: 我的订单列表
        test_my_orders()
    
    # 测试5: 订单统计
    test_payment_stats()
    
    print("\n✅ 所有测试完成!\n")
