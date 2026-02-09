#!/usr/bin/env python3
"""
测试美团联盟API
"""

import os
import requests
import hashlib
import time
from urllib.parse import urlencode

# 从.env读取配置
from dotenv import load_dotenv
load_dotenv()

APP_KEY = os.getenv('MEITUAN_APP_KEY')
SECRET = os.getenv('MEITUAN_SECRET')
PID = os.getenv('MEITUAN_PID')

print(f"APP_KEY: {APP_KEY}")
print(f"SECRET: {SECRET}")
print(f"PID: {PID}")

def generate_sign(params: dict) -> str:
    """生成签名"""
    # 按key排序
    sorted_params = sorted(params.items())
    # 拼接: key1value1key2value2...
    sign_str = ''.join([f'{k}{v}' for k, v in sorted_params])
    # 加密: SECRET + sign_str + SECRET
    sign_str = SECRET + sign_str + SECRET
    # MD5
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

def test_deeplink_convert():
    """测试深度链接转换"""
    # 美团联盟深度链接转换API
    url = "https://openapi.meituan.com/api/deeplink/convert"
    
    params = {
        'appkey': APP_KEY,
        'timestamp': str(int(time.time())),
        'sid': '001',
        'url': 'https://i.meituan.com/search?q=海口希尔顿酒店'
    }
    params['sign'] = generate_sign(params)
    
    print(f"\n=== 测试深度链接转换 ===")
    print(f"请求URL: {url}")
    print(f"参数: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        return response.json()
    except Exception as e:
        print(f"错误: {e}")
        return None

def test_simple_link():
    """测试简单推广链接"""
    # 直接在URL中添加联盟参数
    base_url = "https://i.meituan.com/search"
    params = {
        'q': '海口希尔顿酒店',
        'actId': '418',
        'sid': '001',
        'pid': PID
    }
    
    link = f"{base_url}?{urlencode(params)}"
    print(f"\n=== 简单推广链接 ===")
    print(f"链接: {link}")
    return link

if __name__ == '__main__':
    # 测试深度链接API
    result = test_deeplink_convert()
    
    # 测试简单链接
    simple_link = test_simple_link()
    
    print(f"\n=== 总结 ===")
    print(f"如果API不可用，使用简单推广链接格式")
    print(f"格式: https://i.meituan.com/search?q=关键词&actId=418&sid=001&pid={PID}")
