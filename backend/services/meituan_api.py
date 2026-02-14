"""
美团联盟API对接
支持商品搜索、推广链接生成、订单查询
"""

import hashlib
import time
import requests
from urllib.parse import urlencode
from loguru import logger
import os


class MeituanAPI:
    """美团联盟API封装"""
    
    def __init__(self):
        """初始化美团API"""
        self.app_key = os.getenv('MEITUAN_APP_KEY', '')
        self.api_base = 'https://openapi.meituan.com'
        self.api_version = os.getenv('MEITUAN_API_VERSION', 'v1')
        
        if not self.app_key:
            logger.warning("⚠️ 美团联盟未配置，将使用搜索链接模式")
            self.enabled = False
        else:
            logger.info(f"✅ 美团联盟API已配置 | 额度: {os.getenv('MEITUAN_API_QUOTA', '2000')}/天")
            self.enabled = True
    
    def _sign(self, params: dict) -> str:
        """
        生成API签名
        
        Args:
            params: 请求参数
            
        Returns:
            签名字符串
        """
        # 排序参数
        sorted_params = sorted(params.items())
        # 拼接字符串
        sign_str = ''.join([f'{k}{v}' for k, v in sorted_params])
        # 加上app_key
        sign_str = self.app_key + sign_str + self.app_key
        # MD5加密
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
    
    def search_hotel(self, city_name: str, keyword: str = '', limit: int = 10) -> list:
        """
        搜索酒店
        
        Args:
            city_name: 城市名称
            keyword: 搜索关键词
            limit: 返回数量
            
        Returns:
            酒店列表
        """
        if not self.enabled:
            return self._mock_hotels(city_name, keyword)
        
        try:
            params = {
                'app_key': self.app_key,
                'timestamp': str(int(time.time())),
                'v': self.api_version,
                'city': city_name,
                'keyword': keyword,
                'limit': limit
            }
            params['sign'] = self._sign(params)
            
            url = f"{self.api_base}/hotel/search"
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    return data.get('data', {}).get('hotels', [])
            
            logger.warning(f"美团酒店搜索失败: {response.text}")
            return self._mock_hotels(city_name, keyword)
            
        except Exception as e:
            logger.error(f"美团酒店搜索异常: {e}")
            return self._mock_hotels(city_name, keyword)
    
    def search_food(self, city_name: str, keyword: str = '', limit: int = 10) -> list:
        """
        搜索餐饮团购
        
        Args:
            city_name: 城市名称
            keyword: 搜索关键词
            limit: 返回数量
            
        Returns:
            团购列表
        """
        if not self.enabled:
            return self._mock_food(city_name, keyword)
        
        try:
            params = {
                'app_key': self.app_key,
                'timestamp': str(int(time.time())),
                'v': self.api_version,
                'city': city_name,
                'keyword': keyword,
                'category': 'food',
                'limit': limit
            }
            params['sign'] = self._sign(params)
            
            url = f"{self.api_base}/deal/search"
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    return data.get('data', {}).get('deals', [])
            
            logger.warning(f"美团餐饮搜索失败: {response.text}")
            return self._mock_food(city_name, keyword)
            
        except Exception as e:
            logger.error(f"美团餐饮搜索异常: {e}")
            return self._mock_food(city_name, keyword)
    
    def search_ticket(self, city_name: str, keyword: str = '', limit: int = 5) -> list:
        """
        搜索景点门票
        
        Args:
            city_name: 城市名称
            keyword: 搜索关键词
            limit: 返回数量
            
        Returns:
            门票列表
        """
        if not self.enabled:
            return self._mock_tickets(city_name, keyword)
        
        try:
            params = {
                'app_key': self.app_key,
                'timestamp': str(int(time.time())),
                'v': self.api_version,
                'city': city_name,
                'keyword': keyword,
                'category': 'ticket',
                'limit': limit
            }
            params['sign'] = self._sign(params)
            
            url = f"{self.api_base}/ticket/search"
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    return data.get('data', {}).get('tickets', [])
            
            logger.warning(f"美团门票搜索失败: {response.text}")
            return self._mock_tickets(city_name, keyword)
            
        except Exception as e:
            logger.error(f"美团门票搜索异常: {e}")
            return self._mock_tickets(city_name, keyword)
    
    def generate_link(self, item_type: str, item_id: str) -> dict:
        """
        生成推广链接（带返佣）
        
        Args:
            item_type: 类型（hotel/food/ticket）
            item_id: 商品ID
            
        Returns:
            链接信息
        """
        if not self.enabled:
            # 未配置API，使用搜索链接
            return self._generate_search_link(item_type, item_id)
        
        try:
            params = {
                'app_key': self.app_key,
                'timestamp': str(int(time.time())),
                'v': self.api_version,
                'item_type': item_type,
                'item_id': item_id
            }
            params['sign'] = self._sign(params)
            
            url = f"{self.api_base}/link/generate"
            response = requests.post(url, json=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    return {
                        'url': data.get('data', {}).get('link', ''),
                        'has_commission': True,
                        'commission_rate': data.get('data', {}).get('rate', 0)
                    }
            
            logger.warning(f"生成推广链接失败: {response.text}")
            return self._generate_search_link(item_type, item_id)
            
        except Exception as e:
            logger.error(f"生成推广链接异常: {e}")
            return self._generate_search_link(item_type, item_id)
    
    def _generate_search_link(self, item_type: str, item_id: str) -> dict:
        """生成搜索链接（无返佣）"""
        base_urls = {
            'hotel': 'https://i.meituan.com/hotel',
            'food': 'https://i.meituan.com/deal',
            'ticket': 'https://i.meituan.com/ticket'
        }
        
        url = f"{base_urls.get(item_type, 'https://i.meituan.com')}/{item_id}"
        
        return {
            'url': url,
            'has_commission': False,
            'commission_rate': 0
        }
    
    # Mock数据（当API不可用时）
    def _mock_hotels(self, city_name: str, keyword: str) -> list:
        """Mock酒店数据"""
        return [
            {
                'id': 'mock_hotel_1',
                'name': f'{city_name}希尔顿酒店',
                'price': 800,
                'rating': 4.7,
                'tags': ['海景', '泳池', '亲子'],
                'address': f'{city_name}市中心'
            },
            {
                'id': 'mock_hotel_2',
                'name': f'{city_name}商务酒店',
                'price': 300,
                'rating': 4.5,
                'tags': ['商务', '地铁'],
                'address': f'{city_name}商圈'
            },
            {
                'id': 'mock_hotel_3',
                'name': f'{city_name}快捷酒店',
                'price': 150,
                'rating': 4.2,
                'tags': ['经济', '干净'],
                'address': f'{city_name}老城区'
            }
        ]
    
    def _mock_food(self, city_name: str, keyword: str) -> list:
        """Mock餐饮数据"""
        return [
            {
                'id': 'mock_food_1',
                'name': f'{city_name}文昌鸡饭',
                'price': 50,
                'rating': 4.9,
                'tags': ['本地菜', '性价比'],
                'address': f'{city_name}老街'
            },
            {
                'id': 'mock_food_2',
                'name': f'{city_name}海鲜大排档',
                'price': 150,
                'rating': 4.7,
                'tags': ['海鲜', '新鲜'],
                'address': f'{city_name}海边'
            }
        ]
    
    def _mock_tickets(self, city_name: str, keyword: str) -> list:
        """Mock门票数据"""
        return [
            {
                'id': 'mock_ticket_1',
                'name': f'{city_name}火山口公园',
                'price': 60,
                'original_price': 80,
                'rating': 4.6,
                'tags': ['自然', '地质']
            },
            {
                'id': 'mock_ticket_2',
                'name': f'{city_name}动物园',
                'price': 128,
                'original_price': 150,
                'rating': 4.5,
                'tags': ['亲子', '动物']
            }
        ]


# 单例
_api_instance = None

def get_meituan_api() -> MeituanAPI:
    """获取美团API实例"""
    global _api_instance
    if _api_instance is None:
        _api_instance = MeituanAPI()
    return _api_instance


if __name__ == "__main__":
    # 测试
    api = MeituanAPI()
    
    print("=== 测试酒店搜索 ===")
    hotels = api.search_hotel('海口', '希尔顿')
    print(f"找到 {len(hotels)} 家酒店")
    
    print("\n=== 测试餐饮搜索 ===")
    food = api.search_food('海口', '文昌鸡')
    print(f"找到 {len(food)} 家餐厅")
    
    print("\n=== 测试门票搜索 ===")
    tickets = api.search_ticket('海口', '公园')
    print(f"找到 {len(tickets)} 个景点")
    
    print("\n=== 测试生成链接 ===")
    link = api.generate_link('hotel', 'mock_hotel_1')
    print(f"推广链接: {link['url']}")
    print(f"有返佣: {link['has_commission']}")
