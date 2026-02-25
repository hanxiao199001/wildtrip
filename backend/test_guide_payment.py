#!/usr/bin/env python3
"""
测试攻略解锁支付
"""
import requests
import json

BASE_URL = 'http://localhost:5000'


def test_guide_products():
    """测试获取攻略商品"""
    print("\n" + "="*60)
    print("📦 测试: 获取攻略商品列表")
    print("="*60)
    
    url = f"{BASE_URL}/api/vip/products"
    response = requests.get(url)
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    if data['success']:
        print(f"\n✅ 找到 {len(data['products'])} 个攻略商品:")
        for product in data['products']:
            print(f"   - {product['name']}: ¥{product['price']} ({product['type']})")


def test_create_travel_guide_order():
    """测试创建旅行攻略订单"""
    print("\n" + "="*60)
    print("💳 测试: 创建旅行攻略解锁订单")
    print("="*60)
    
    url = f"{BASE_URL}/api/vip/create_order"
    payload = {
        'openid': 'test_user_guide_001',
        'product_id': 'guide_travel',
        'guide_id': 'guide_beijing_3days'
    }
    
    response = requests.post(url, json=payload)
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    if data['success']:
        order = data['order']
        print(f"\n✅ 旅行攻略订单创建成功:")
        print(f"   订单号: {order['order_no']}")
        print(f"   攻略ID: {data.get('guide_id')}")
        print(f"   商品: {order['product_name']}")
        print(f"   金额: ¥{order['amount']/100}")
        return order['order_no'], data.get('guide_id')
    else:
        print(f"\n❌ 失败: {data.get('error')}")
        return None, None


def test_create_history_guide_order():
    """测试创建人文历史订单"""
    print("\n" + "="*60)
    print("💳 测试: 创建人文历史路线解锁订单")
    print("="*60)
    
    url = f"{BASE_URL}/api/vip/create_order"
    payload = {
        'openid': 'test_user_guide_001',
        'product_id': 'guide_history',
        'guide_id': 'guide_xian_history'
    }
    
    response = requests.post(url, json=payload)
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    if data['success']:
        order = data['order']
        print(f"\n✅ 人文历史订单创建成功:")
        print(f"   订单号: {order['order_no']}")
        print(f"   攻略ID: {data.get('guide_id')}")
        print(f"   商品: {order['product_name']}")
        print(f"   金额: ¥{order['amount']/100}")
        return order['order_no'], data.get('guide_id')
    else:
        print(f"\n❌ 失败: {data.get('error')}")
        return None, None


def test_check_unlock(guide_id):
    """测试检查攻略是否解锁"""
    print("\n" + "="*60)
    print(f"🔍 测试: 检查攻略解锁状态 ({guide_id})")
    print("="*60)
    
    url = f"{BASE_URL}/api/vip/check_unlock?openid=test_user_guide_001&guide_id={guide_id}"
    response = requests.get(url)
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    if data['success']:
        if data.get('unlocked'):
            print(f"\n✅ 攻略已解锁!")
            print(f"   订单号: {data.get('order_no')}")
            print(f"   支付时间: {data.get('paid_at')}")
        else:
            print(f"\n⏳ 攻略未解锁")


def test_my_unlocked():
    """测试我的已解锁攻略"""
    print("\n" + "="*60)
    print("📋 测试: 我的已解锁攻略")
    print("="*60)
    
    url = f"{BASE_URL}/api/vip/my_unlocked?openid=test_user_guide_001"
    response = requests.get(url)
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    if data['success']:
        print(f"\n✅ 已解锁 {data['total']} 个攻略:")
        for guide in data['guides']:
            print(f"   - {guide['guide_id']}: {guide['product_name']} (¥{guide['amount']/100})")


if __name__ == '__main__':
    print("\n🧪 开始测试攻略解锁支付...")
    
    # 测试1: 获取商品列表
    test_guide_products()
    
    # 测试2: 创建旅行攻略订单
    order_no1, guide_id1 = test_create_travel_guide_order()
    
    # 测试3: 创建人文历史订单
    order_no2, guide_id2 = test_create_history_guide_order()
    
    # 测试4: 检查解锁状态 (未支付)
    if guide_id1:
        test_check_unlock(guide_id1)
    
    # 测试5: 我的已解锁攻略
    test_my_unlocked()
    
    print("\n✅ 所有测试完成!\n")
