#!/usr/bin/env python3
"""
测试聚推客联盟API
"""

import os

import requests
import json

# 聚推客配置
PUB_ID = os.getenv("JUTUIKE_PUB_ID", "")
API_KEY = os.getenv("JUTUIKE_API_KEY", "")  # 从 .env 读取，不要硬编码
API_BASE = "https://api.jutulke.com"  # 假设的API地址

print("=" * 70)
print("🔥 聚推客联盟API测试")
print("=" * 70)

print(f"\n📌 配置信息:")
print(f"PUB_ID: {PUB_ID}")
print(f"API_KEY: {API_KEY[:20]}...")

# 测试1：商品搜索
print(f"\n1️⃣ 测试商品搜索API:")

# 常见的聚推客API格式（根据文档可能需要调整）
search_url = f"{API_BASE}/goods/search"
params = {
    'pub_id': PUB_ID,
    'apikey': API_KEY,
    'keyword': '海口酒店',
    'platform': 'meituan',  # 或 'taobao', 'jd'
    'page': 1,
    'page_size': 10
}

headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'WildTrip/1.0'
}

try:
    response = requests.get(search_url, params=params, headers=headers, timeout=10)
    print(f"请求URL: {response.url}")
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ API调用成功")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
    else:
        print(f"\n⚠️ API返回错误")
        
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 测试2：链接转换
print(f"\n\n2️⃣ 测试链接转换API:")

convert_url = f"{API_BASE}/link/convert"
convert_params = {
    'pub_id': PUB_ID,
    'apikey': API_KEY,
    'url': 'https://www.meituan.com/meishi',
    'platform': 'meituan'
}

try:
    response = requests.post(convert_url, json=convert_params, headers=headers, timeout=10)
    print(f"请求URL: {convert_url}")
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ 转链成功")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"\n⚠️ 转链失败")
        
except Exception as e:
    print(f"❌ 请求失败: {e}")

print("\n" + "=" * 70)
print("📝 下一步：查看API文档，确认正确的接口地址和参数格式")
print("文档地址：https://www.jutulke.com/document")
print("=" * 70)
