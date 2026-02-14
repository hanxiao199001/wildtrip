"""
美团返佣链接生成器（聚推客联盟版）
通过聚推客联盟 CPS 平台生成美团返佣链接
支持：小程序跳转（navigateToMiniProgram）+ H5 备用链接
"""

from urllib.parse import urlencode, quote
from typing import Dict, Optional
from loguru import logger
from .jutuike_api import get_jutuike_api


class MeituanAffiliate:
    """美团返佣链接生成（聚推客联盟版）"""

    def __init__(self):
        """初始化：对接聚推客联盟"""
        self.jutuike = get_jutuike_api()
        self.is_configured = self.jutuike.enabled

        # 缓存小程序跳转信息（避免每次都调API）
        self._cached_mp_info = None

        if self.is_configured:
            logger.info("美团返佣已配置（聚推客联盟）")
        else:
            logger.warning("美团返佣未配置，将返回搜索链接（无返佣）")

    def _get_mp_info(self) -> Dict:
        """获取并缓存小程序跳转信息"""
        if self._cached_mp_info is None:
            self._cached_mp_info = self.jutuike.get_meituan_miniprogram_info()
        return self._cached_mp_info

    def get_miniprogram_jump_info(self) -> Dict:
        """
        获取美团小程序跳转参数（供小程序前端使用）

        Returns:
            {
                'app_id': 'wxde8ac0a21135c07d',
                'page_path': '/index/pages/h5/h5?weburl=...',
                'enabled': True/False
            }
        """
        mp_info = self._get_mp_info()
        return {
            'app_id': mp_info.get('app_id', 'wxde8ac0a21135c07d'),
            'page_path': mp_info.get('page_path', ''),
            'h5_url': mp_info.get('h5_url', ''),
            'enabled': self.is_configured and bool(mp_info.get('page_path'))
        }

    def get_search_link(self, query: str, category: str = "all") -> str:
        """
        生成美团搜索链接（H5 备用）

        Args:
            query: 搜索关键词（如"海口 希尔顿酒店"）
            category: 分类（hotel/food/ticket/all）

        Returns:
            美团搜索URL
        """
        return f"https://i.meituan.com/search?q={quote(query)}"

    def get_hotel_link(self, hotel_id: str = "", city_name: str = "", hotel_name: str = "") -> Dict:
        """生成酒店链接"""
        search_query = f"{city_name} {hotel_name}".strip()
        fallback_url = f"https://i.meituan.com/search?q={quote(search_query)}" if search_query else ""

        return {
            'url': fallback_url,
            'fallback_url': fallback_url,
            'has_commission': self.is_configured,
            'type': 'hotel',
            'jump_type': 'miniprogram' if self.is_configured else 'h5'
        }

    def get_food_link(self, deal_id: str = "", restaurant_name: str = "", city_name: str = "") -> Dict:
        """生成餐饮团购链接"""
        search_query = f"{city_name} {restaurant_name}".strip()
        fallback_url = f"https://i.meituan.com/search?q={quote(search_query)}" if search_query else ""

        return {
            'url': fallback_url,
            'fallback_url': fallback_url,
            'has_commission': self.is_configured,
            'type': 'food',
            'jump_type': 'miniprogram' if self.is_configured else 'h5'
        }

    def get_ticket_link(self, poi_id: str = "", poi_name: str = "", city_name: str = "") -> Dict:
        """生成景点门票链接"""
        search_query = f"{city_name} {poi_name} 门票".strip()
        fallback_url = f"https://i.meituan.com/search?q={quote(search_query)}" if search_query else ""

        return {
            'url': fallback_url,
            'fallback_url': fallback_url,
            'has_commission': self.is_configured,
            'type': 'ticket',
            'jump_type': 'miniprogram' if self.is_configured else 'h5'
        }

    def format_recommendation(self, item: Dict) -> str:
        """格式化推荐内容（Markdown）"""
        name = item.get('name', '未知')
        price = item.get('price', 0)
        original_price = item.get('original_price')
        rating = item.get('rating')
        tags = item.get('tags', [])
        link_info = item.get('link', {})
        url = link_info.get('url', '#')

        if original_price and original_price > price:
            price_str = f"~~¥{original_price}~~ **¥{price}**"
            discount = int((1 - price / original_price) * 100)
            price_str += f" 省{discount}%"
        else:
            price_str = f"**¥{price}**"

        rating_str = f"⭐{rating}" if rating else ""
        tags_str = " ".join([f"`{tag}`" for tag in tags[:3]]) if tags else ""

        result = f"**{name}** {price_str}"
        if rating_str:
            result += f" {rating_str}"
        if tags_str:
            result += f"\n{tags_str}"
        result += f"\n[查看详情]({url})"

        return result


# 单例
_affiliate_instance = None


def get_meituan_affiliate() -> MeituanAffiliate:
    """获取美团联盟实例（单例模式）"""
    global _affiliate_instance
    if _affiliate_instance is None:
        _affiliate_instance = MeituanAffiliate()
    return _affiliate_instance


if __name__ == "__main__":
    affiliate = MeituanAffiliate()
    print(f"配置状态: {'已配置' if affiliate.is_configured else '未配置'}")

    # 获取小程序跳转信息
    mp_info = affiliate.get_miniprogram_jump_info()
    print(f"\n小程序跳转信息:")
    print(f"  AppID: {mp_info['app_id']}")
    print(f"  Path: {mp_info['page_path'][:60]}...")
    print(f"  启用: {mp_info['enabled']}")

    # 生成搜索链接
    link = affiliate.get_search_link("海口 希尔顿酒店", "hotel")
    print(f"\n搜索链接: {link}")
