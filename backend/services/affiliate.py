"""
美团联盟返佣链接生成器
支持：酒店、餐饮团购、景点门票、玩乐娱乐
使用美团API模式（更强大）
"""

from urllib.parse import urlencode
from typing import Dict, Optional
from loguru import logger
from .meituan_api import get_meituan_api


class MeituanAffiliate:
    """美团联盟返佣链接生成"""
    
    def __init__(self, act_id: Optional[str] = None, sid: Optional[str] = None):
        """
        初始化美团联盟配置
        
        Args:
            act_id: 美团活动ID（审核通过后获取）
            sid: 推广位ID（审核通过后获取）
        """
        self.act_id = act_id or "待审核"
        self.sid = sid or "待审核"
        self.is_configured = bool(act_id and sid and act_id != "待审核")
        
        if not self.is_configured:
            logger.warning("美团联盟未配置，将返回普通链接（无返佣）")
    
    def get_hotel_link(self, hotel_id: str, city_name: str = "", hotel_name: str = "") -> Dict:
        """
        生成酒店返佣链接
        
        Args:
            hotel_id: 美团酒店ID
            city_name: 城市名称（用于fallback搜索）
            hotel_name: 酒店名称（用于fallback搜索）
            
        Returns:
            {
                'url': '返佣链接',
                'fallback_url': '备用链接（搜索页）',
                'has_commission': True/False
            }
        """
        if self.is_configured:
            # 返佣链接
            params = {
                'actId': self.act_id,
                'sid': self.sid
            }
            url = f"https://i.meituan.com/hotel/{hotel_id}?{urlencode(params)}"
            has_commission = True
        else:
            # 普通链接（审核前使用）
            url = f"https://i.meituan.com/hotel/{hotel_id}"
            has_commission = False
        
        # Fallback搜索链接
        if city_name and hotel_name:
            search_params = {'q': f"{city_name} {hotel_name}"}
            fallback_url = f"https://i.meituan.com/hotel/search?{urlencode(search_params)}"
        else:
            fallback_url = url
        
        return {
            'url': url,
            'fallback_url': fallback_url,
            'has_commission': has_commission,
            'type': 'hotel'
        }
    
    def get_food_link(self, deal_id: str, restaurant_name: str = "", city_name: str = "") -> Dict:
        """
        生成餐饮团购返佣链接
        
        Args:
            deal_id: 美团团购ID
            restaurant_name: 餐厅名称
            city_name: 城市名称
            
        Returns:
            {
                'url': '返佣链接',
                'fallback_url': '备用链接',
                'has_commission': True/False
            }
        """
        if self.is_configured:
            params = {
                'actId': self.act_id,
                'sid': self.sid
            }
            url = f"https://i.meituan.com/deal/{deal_id}?{urlencode(params)}"
            has_commission = True
        else:
            url = f"https://i.meituan.com/deal/{deal_id}"
            has_commission = False
        
        # Fallback搜索
        if city_name and restaurant_name:
            search_params = {'q': f"{city_name} {restaurant_name}"}
            fallback_url = f"https://i.meituan.com/search?{urlencode(search_params)}"
        else:
            fallback_url = url
        
        return {
            'url': url,
            'fallback_url': fallback_url,
            'has_commission': has_commission,
            'type': 'food'
        }
    
    def get_ticket_link(self, poi_id: str, poi_name: str = "", city_name: str = "") -> Dict:
        """
        生成景点门票返佣链接
        
        Args:
            poi_id: 美团景点POI ID
            poi_name: 景点名称
            city_name: 城市名称
            
        Returns:
            {
                'url': '返佣链接',
                'fallback_url': '备用链接',
                'has_commission': True/False
            }
        """
        if self.is_configured:
            params = {
                'actId': self.act_id,
                'sid': self.sid
            }
            url = f"https://i.meituan.com/ticket/{poi_id}?{urlencode(params)}"
            has_commission = True
        else:
            url = f"https://i.meituan.com/ticket/{poi_id}"
            has_commission = False
        
        # Fallback搜索
        if city_name and poi_name:
            search_params = {'q': f"{city_name} {poi_name} 门票"}
            fallback_url = f"https://i.meituan.com/search?{urlencode(search_params)}"
        else:
            fallback_url = url
        
        return {
            'url': url,
            'fallback_url': fallback_url,
            'has_commission': has_commission,
            'type': 'ticket'
        }
    
    def get_search_link(self, query: str, category: str = "all") -> str:
        """
        生成美团搜索提示（临时方案 - 等待联盟审核）
        
        Args:
            query: 搜索关键词
            category: 分类（hotel/food/ticket/all）
            
        Returns:
            特殊格式的字符串，前端会渲染为纯文字提示
        """
        # 🔥 临时方案：返回特殊格式 SEARCH_HINT:{关键词}
        # 前端检测到这个格式，会渲染为"📱 美团搜索：XXX"的纯文字
        # 不是可点击的链接，用户需要手动复制到美团App
        
        # 清理关键词（去掉城市名，只保留商家名）
        clean_query = query.split()[-1] if ' ' in query else query
        
        return f"SEARCH_HINT:{clean_query}"
    
    def format_recommendation(self, item: Dict) -> str:
        """
        格式化推荐内容（Markdown）
        
        Args:
            item: {
                'name': '商品名称',
                'price': 100,
                'original_price': 150,  # 可选
                'rating': 4.5,
                'tags': ['标签1', '标签2'],
                'link': {...}  # 由get_hotel_link等生成
            }
            
        Returns:
            Markdown格式的推荐文本
        """
        name = item.get('name', '未知')
        price = item.get('price', 0)
        original_price = item.get('original_price')
        rating = item.get('rating')
        tags = item.get('tags', [])
        link_info = item.get('link', {})
        url = link_info.get('url', '#')
        
        # 价格显示
        if original_price and original_price > price:
            price_str = f"~~¥{original_price}~~ **¥{price}**"
            discount = int((1 - price / original_price) * 100)
            price_str += f" 🔥省{discount}%"
        else:
            price_str = f"**¥{price}**"
        
        # 评分显示
        rating_str = f"⭐{rating}" if rating else ""
        
        # 标签显示
        tags_str = " ".join([f"`{tag}`" for tag in tags[:3]]) if tags else ""
        
        # 组合
        result = f"**{name}** {price_str}"
        if rating_str:
            result += f" {rating_str}"
        if tags_str:
            result += f"\n{tags_str}"
        result += f"\n[👉 查看详情]({url})"
        
        return result


# 单例
_affiliate_instance = None


def get_meituan_affiliate(act_id: Optional[str] = None, sid: Optional[str] = None) -> MeituanAffiliate:
    """获取美团联盟实例（单例模式）"""
    global _affiliate_instance
    
    if _affiliate_instance is None:
        # 尝试从环境变量读取
        import os
        act_id = act_id or os.getenv('MEITUAN_ACT_ID')
        sid = sid or os.getenv('MEITUAN_SID')
        _affiliate_instance = MeituanAffiliate(act_id, sid)
    
    return _affiliate_instance


# 示例用法
if __name__ == "__main__":
    # 测试（未配置联盟时）
    affiliate = MeituanAffiliate()
    
    # 酒店链接
    hotel_link = affiliate.get_hotel_link(
        hotel_id="12345",
        city_name="海口",
        hotel_name="希尔顿酒店"
    )
    print("酒店链接:", hotel_link)
    
    # 餐饮链接
    food_link = affiliate.get_food_link(
        deal_id="67890",
        restaurant_name="文昌鸡饭",
        city_name="海口"
    )
    print("餐饮链接:", food_link)
    
    # 门票链接
    ticket_link = affiliate.get_ticket_link(
        poi_id="11111",
        poi_name="火山口公园",
        city_name="海口"
    )
    print("门票链接:", ticket_link)
    
    # 格式化推荐
    recommendation = affiliate.format_recommendation({
        'name': '海口希尔顿酒店',
        'price': 800,
        'original_price': 1000,
        'rating': 4.7,
        'tags': ['海景房', '亲子', '泳池'],
        'link': hotel_link
    })
    print("\n格式化推荐:\n", recommendation)
