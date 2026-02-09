"""
淘宝联盟（聚推客）- 推广链接生成
"""

import requests
import hashlib
import time
import json
from loguru import logger
from typing import Dict, Optional
import os


class TaobaoAffiliate:
    """淘宝联盟推广（通过聚推客）"""
    
    def __init__(self):
        """初始化聚推客配置"""
        self.pub_id = os.getenv('JUTULKE_PUB_ID', '451888')
        self.api_key = os.getenv('JUTULKE_API_KEY', 'oVlOMmKY3vXKDRoYMjm8jmmy97AUFHId')
        self.api_base = os.getenv('JUTULKE_API_BASE', 'https://api.jutulke.com')
        
        # 聚推客短链接域名
        self.short_domain = 'https://kzurl18.cn'
        
        logger.info(f"✅ 聚推客淘宝联盟已配置 | PUB_ID: {self.pub_id}")
    
    def search_goods(self, keyword: str, category: str = 'hotel', limit: int = 10) -> list:
        """
        搜索淘宝商品
        
        Args:
            keyword: 搜索关键词（如"海口酒店"）
            category: 品类（hotel/food/ticket）
            limit: 返回数量
            
        Returns:
            商品列表
        """
        try:
            # 聚推客API接口（需要根据实际文档调整）
            url = f"{self.api_base}/goods/search"
            
            params = {
                'pub_id': self.pub_id,
                'apikey': self.api_key,
                'keyword': keyword,
                'platform': 'taobao',
                'page': 1,
                'page_size': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    return data.get('data', {}).get('goods', [])
            
            logger.warning(f"⚠️ 淘宝商品搜索失败: {response.text[:200]}")
            return []
            
        except Exception as e:
            logger.error(f"❌ 淘宝商品搜索异常: {e}")
            return []
    
    def convert_link(self, url: str, title: str = '') -> Optional[str]:
        """
        将普通淘宝链接转换为推广链接
        
        Args:
            url: 原始淘宝链接
            title: 商品标题（可选）
            
        Returns:
            推广链接
        """
        try:
            # 聚推客转链API
            api_url = f"{self.api_base}/link/convert"
            
            payload = {
                'pub_id': self.pub_id,
                'apikey': self.api_key,
                'url': url,
                'title': title
            }
            
            response = requests.post(api_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    # 返回短链接
                    return data.get('data', {}).get('short_url')
            
            logger.warning(f"⚠️ 淘宝转链失败: {response.text[:200]}")
            return None
            
        except Exception as e:
            logger.error(f"❌ 淘宝转链异常: {e}")
            return None
    
    def generate_hotel_link(self, city: str, hotel_name: str) -> Dict[str, str]:
        """
        生成酒店推广链接
        
        Args:
            city: 城市名
            hotel_name: 酒店名称
            
        Returns:
            链接信息
        """
        keyword = f"{city} {hotel_name} 酒店"
        
        # 方式1：搜索商品，获取推广链接
        goods = self.search_goods(keyword, 'hotel', limit=1)
        if goods and len(goods) > 0:
            promo_url = goods[0].get('promo_url')
            if promo_url:
                logger.info(f"🏨 生成酒店推广链接: {hotel_name} -> {promo_url}")
                return {
                    'url': promo_url,
                    'text': f'淘宝预订（返现5%-15%）',
                    'platform': 'taobao',
                    'has_commission': True
                }
        
        # 方式2：生成通用搜索链接
        # 淘宝搜索链接格式
        search_url = f"https://s.taobao.com/search?q={keyword}"
        
        # 尝试转链
        promo_url = self.convert_link(search_url, keyword)
        if promo_url:
            logger.info(f"🏨 生成酒店搜索推广链接: {hotel_name} -> {promo_url}")
            return {
                'url': promo_url,
                'text': f'淘宝预订（返现5%-15%）',
                'platform': 'taobao',
                'has_commission': True
            }
        
        # 方式3：使用淘宝普通搜索链接
        logger.warning(f"⚠️ 淘宝转链失败，使用普通搜索链接")
        return {
            'url': search_url,
            'text': f'去淘宝搜"{hotel_name}"',
            'platform': 'taobao',
            'has_commission': False
        }
    
    def generate_food_link(self, city: str, restaurant_name: str) -> Dict[str, str]:
        """
        生成美食推广链接（淘宝美食卡券）
        
        Args:
            city: 城市名
            restaurant_name: 餐厅名称
            
        Returns:
            链接信息
        """
        keyword = f"{city} {restaurant_name} 美食券"
        search_url = f"https://s.taobao.com/search?q={keyword}"
        
        promo_url = self.convert_link(search_url, keyword)
        if promo_url:
            return {
                'url': promo_url,
                'text': f'淘宝领券（返现5%-15%）',
                'platform': 'taobao',
                'has_commission': True
            }
        
        return {
            'url': search_url,
            'text': f'去淘宝搜"{restaurant_name}券"',
            'platform': 'taobao',
            'has_commission': False
        }
    
    def generate_ticket_link(self, city: str, attraction_name: str) -> Dict[str, str]:
        """
        生成门票推广链接
        
        Args:
            city: 城市名
            attraction_name: 景点名称
            
        Returns:
            链接信息
        """
        keyword = f"{city} {attraction_name} 门票"
        search_url = f"https://s.taobao.com/search?q={keyword}"
        
        promo_url = self.convert_link(search_url, keyword)
        if promo_url:
            return {
                'url': promo_url,
                'text': f'淘宝购票（返现5%-15%）',
                'platform': 'taobao',
                'has_commission': True
            }
        
        return {
            'url': search_url,
            'text': f'去淘宝搜"{attraction_name}门票"',
            'platform': 'taobao',
            'has_commission': False
        }


# 单例
_taobao_affiliate = None

def get_taobao_affiliate() -> TaobaoAffiliate:
    """获取淘宝联盟实例"""
    global _taobao_affiliate
    if _taobao_affiliate is None:
        _taobao_affiliate = TaobaoAffiliate()
    return _taobao_affiliate


if __name__ == '__main__':
    # 测试
    affiliate = TaobaoAffiliate()
    
    print("=== 测试淘宝联盟推广 ===")
    
    # 测试酒店链接
    hotel_link = affiliate.generate_hotel_link('海口', '希尔顿酒店')
    print(f"\n酒店推广链接:")
    print(f"URL: {hotel_link['url']}")
    print(f"文案: {hotel_link['text']}")
    print(f"有返佣: {hotel_link['has_commission']}")
    
    # 测试美食链接
    food_link = affiliate.generate_food_link('海口', '文昌鸡饭')
    print(f"\n美食推广链接:")
    print(f"URL: {food_link['url']}")
    print(f"文案: {food_link['text']}")
    print(f"有返佣: {food_link['has_commission']}")
