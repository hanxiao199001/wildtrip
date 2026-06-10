#!/usr/bin/env python3
"""
美团联盟正确的对接方式研究
"""

import os
import requests
import hashlib
import time
from urllib.parse import urlencode, quote
from dotenv import load_dotenv

load_dotenv()

APP_KEY = os.getenv('MEITUAN_APP_KEY')
SECRET = os.getenv('MEITUAN_SECRET')
PID = os.getenv('MEITUAN_PID')

print("=" * 70)
print("🔍 美团联盟API正确对接方式")
print("=" * 70)

def generate_sign(params: dict) -> str:
    """生成签名"""
    sorted_params = sorted(params.items())
    sign_str = ''.join([f'{k}{v}' for k, v in sorted_params])
    sign_str = SECRET + sign_str + SECRET
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

print("\n方案1️⃣：使用美团联盟的关键词搜索推广链接")
print("-" * 70)

# 美团联盟搜索推广链接格式（官方推荐）
# 参考：https://union.meituan.com/docs/
def generate_search_promotion_link(keyword: str) -> str:
    """
    生成搜索推广链接（官方方式）
    格式：美团联盟后台获取的推广链接 + 关键词参数
    """
    # 美团联盟搜索推广链接模板
    base_url = "https://union.meituan.com/v1/media/promotion/generateLink"
    
    params = {
        'appkey': APP_KEY,
        'timestamp': str(int(time.time())),
        'keyword': keyword,
        'actId': '418',  # 美团通用活动
        'sid': '001',
        'pid': PID
    }
    params['sign'] = generate_sign(params)
    
    try:
        response = requests.post(base_url, json=params, timeout=10)
        print(f"请求URL: {base_url}")
        print(f"参数: {params}")
        print(f"响应状态: {response.status_code}")
        print(f"响应内容: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                return data['data']['promotionLink']
        
        return None
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        return None

# 测试
keyword = "海口希尔顿酒店"
promo_link = generate_search_promotion_link(keyword)
if promo_link:
    print(f"\n✅ 推广链接生成成功:")
    print(promo_link)
else:
    print(f"\n⚠️ API方式失败")

print("\n\n方案2️⃣：使用美团联盟短链接生成")
print("-" * 70)

def generate_short_link(original_url: str) -> str:
    """
    将普通美团链接转换为推广短链接
    """
    base_url = "https://openapi.meituan.com/api/link/convert"
    
    params = {
        'appkey': APP_KEY,
        'timestamp': str(int(time.time())),
        'url': original_url,
        'sid': '001',
        'pid': PID
    }
    params['sign'] = generate_sign(params)
    
    try:
        response = requests.post(base_url, json=params, timeout=10)
        print(f"请求URL: {base_url}")
        print(f"原始链接: {original_url}")
        print(f"响应状态: {response.status_code}")
        print(f"响应内容: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                return data['data']['shortLink']
        
        return None
    except Exception as e:
        print(f"❌ 转链失败: {e}")
        return None

# 测试转链
original_url = "https://hotel.meituan.com/beijing/112233"
short_link = generate_short_link(original_url)
if short_link:
    print(f"\n✅ 短链接生成成功:")
    print(short_link)
else:
    print(f"\n⚠️ 转链失败")

print("\n\n方案3️⃣：使用美团联盟通用推广链接（最简单）")
print("-" * 70)

def generate_universal_link(keyword: str, category: str = 'hotel') -> str:
    """
    生成通用推广链接（不调用API，使用固定格式）
    这是美团联盟提供的通用推广链接格式
    """
    # 美团联盟通用推广链接格式
    # 格式：https://s.meituan.com/v1/mwx/...
    # 或者使用 dpurl.cn 短域名
    
    # 方式A：使用美团内部推广域名（需要从后台获取）
    # 方式B：使用固定的推广链接模板
    
    # 实际情况：需要先在美团联盟后台生成"推广位"，获取固定的推广链接
    # 然后在链接后面添加参数
    
    print("⚠️ 该方案需要先在美团联盟后台获取推广位链接")
    print("登录：https://union.meituan.com/")
    print("路径：推广管理 -> 推广位管理 -> 新建推广位")
    print("然后使用推广位链接 + 关键词参数")
    
    return None

generate_universal_link("海口酒店")

print("\n\n" + "=" * 70)
print("📝 总结：正确的美团联盟对接方式")
print("=" * 70)

print("""
1. ❌ 错误方式：直接在美团搜索链接后面加参数
   https://www.meituan.com/search?q=xxx&pid=xxx  ← 不会追踪返佣

2. ✅ 正确方式A：使用美团联盟API转链
   - 调用美团联盟的转链API
   - 将普通链接转换为推广链接
   - 推广链接才能追踪返佣

3. ✅ 正确方式B：使用美团联盟推广位
   - 在美团联盟后台创建"推广位"
   - 获取推广位的固定链接
   - 使用推广位链接 + 动态参数

4. ✅ 正确方式C：使用美团联盟的小程序/H5跳转链接
   - 使用美团提供的专用跳转域名（如 dpurl.cn）
   - 这些链接会自动追踪返佣

🔧 推荐方案：
- 短期：使用固定推广位链接（从美团联盟后台获取）
- 长期：对接美团联盟API，实现动态转链
""")

print("\n🎯 下一步操作：")
print("1. 登录美团联盟后台：https://union.meituan.com/")
print("2. 找到「推广管理」->「推广位管理」")
print("3. 创建新推广位，获取推广链接")
print("4. 将推广链接配置到系统中")
print("=" * 70)
