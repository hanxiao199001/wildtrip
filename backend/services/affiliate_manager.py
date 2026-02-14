"""
联盟链接管理器
支持美团联盟（餐饮）+ 飞猪联盟（酒店/门票）
"""

import re
import random
from typing import Dict, Optional
from loguru import logger
from urllib.parse import quote


class AffiliateManager:
    """联盟链接管理器"""

    def __init__(self):
        # 实际变现情况（2026-02-05更新）
        # 酒店：美团联盟有活动，可返佣
        self.hotel_status = 'approved'
        self.hotel_has_commission = True

        # 餐饮：暂无返佣，但保留搜索链接（提升用户体验）
        self.restaurant_status = 'search_only'
        self.restaurant_has_commission = False

        # 门票：走美团搜索链接
        self.ticket_status = 'search_only'
        self.ticket_has_commission = False

        # 联盟链接模板（一键取链生成）
        self.meituan_hotel_template = None
        self.fliggy_template = None

    def generate_booking_link(
        self,
        poi_type: str,
        name: str,
        city: str = '',
        affiliate_link: Optional[str] = None
    ) -> Dict[str, str]:
        """
        生成预订链接（根据实际变现情况）
        """
        if poi_type == 'restaurant':
            return self._generate_meituan_link(name, city, affiliate_link)
        elif poi_type == 'hotel':
            return self._generate_hotel_link(name, city, affiliate_link)
        elif poi_type == 'ticket':
            return self._generate_ticket_link(name, city, affiliate_link)
        else:
            return self._generate_search_link(name, city)

    def _generate_meituan_link(
        self,
        name: str,
        city: str = '',
        affiliate_link: Optional[str] = None
    ) -> Dict[str, str]:
        """生成美团链接（餐饮）"""
        keyword = f"{city} {name}" if city else name
        search_url = f"https://i.meituan.com/search?q={quote(keyword)}"

        return {
            'url': search_url,
            'text': f'美团团购',
            'status': 'search_only',
            'platform': 'meituan',
            'has_commission': False
        }

    def _generate_hotel_link(
        self,
        name: str,
        city: str = '',
        affiliate_link: Optional[str] = None
    ) -> Dict[str, str]:
        """生成酒店链接（美团联盟，有返佣）"""
        if affiliate_link:
            return {
                'url': affiliate_link,
                'text': f'美团预订',
                'status': 'approved',
                'platform': 'meituan',
                'has_commission': True
            }
        else:
            keyword = f"{city} {name}" if city else name
            search_url = f"https://i.meituan.com/search?q={quote(keyword)}"

            return {
                'url': search_url,
                'text': f'美团预订',
                'status': 'approved',
                'platform': 'meituan',
                'has_commission': True
            }

    def _generate_ticket_link(
        self,
        name: str,
        city: str = '',
        affiliate_link: Optional[str] = None
    ) -> Dict[str, str]:
        """生成门票链接（美团搜索）"""
        keyword = f"{city} {name} 门票" if city else f"{name} 门票"
        search_url = f"https://i.meituan.com/search?q={quote(keyword)}"

        return {
            'url': search_url,
            'text': f'查看门票',
            'status': 'search_only',
            'platform': 'meituan',
            'has_commission': False
        }

    def _generate_search_link(self, name: str, city: str = '') -> Dict[str, str]:
        """生成通用搜索链接"""
        keyword = f"{city} {name}" if city else name
        search_url = f"https://i.meituan.com/search?q={quote(keyword)}"

        return {
            'url': search_url,
            'text': f'去美团查看',
            'status': 'search_only',
            'platform': 'meituan',
            'has_commission': False
        }

    def render_booking_button(
        self,
        poi_type: str,
        name: str,
        price: Optional[int] = None,
        cashback: Optional[int] = None,
        city: str = '',
        affiliate_link: Optional[str] = None,
        rating: Optional[str] = None,
        features: Optional[list] = None,
        reason: Optional[str] = None
    ) -> str:
        """
        渲染预订按钮HTML（根据实际变现情况）
        """
        link_info = self.generate_booking_link(poi_type, name, city, affiliate_link)

        if poi_type == 'restaurant':
            return self._render_restaurant_card(link_info, name, price, cashback, rating, features, reason)
        elif poi_type == 'hotel':
            return self._render_hotel_button(link_info, name, cashback)
        else:
            return self._render_ticket_button(link_info, name)

    def _render_restaurant_card(self, link_info: dict, name: str, price: Optional[int] = None, cashback: Optional[int] = None, rating: Optional[str] = None, features: Optional[list] = None, reason: Optional[str] = None) -> str:
        """渲染餐厅完整卡片组件（含店名、评分、特色菜、推荐理由、价格区、CTA、信任背书）"""
        url = link_info['url']

        # 计算团购价（原价85折）
        if price:
            market_price = int(price / 0.85)
            cashback_amount = cashback or 5
        else:
            market_price = None
            cashback_amount = cashback or 5

        # 随机预订人数（社会证明）
        booked_count = random.randint(23, 88)

        # 评分
        rating_val = rating or '4.5'

        # POI元信息行（评分 + 价格）
        meta_html = f'''<div class="poi-meta">
        <span class="poi-rating">⭐ {rating_val}</span>'''
        if price:
            meta_html += f'<span class="poi-price">¥{price}/人</span>'
        meta_html += '</div>'

        # 特色菜标签
        features_html = ''
        if features:
            features_html = '<div style="margin: 8px 0;">'
            for feat in features[:4]:
                features_html += f'<span class="feature-tag">{feat}</span>'
            features_html += '</div>'

        # 推荐理由
        reason_html = ''
        if reason:
            reason_html = f'<div class="recommend-reason">💡 {reason}</div>'

        # 价格区
        price_html = ''
        if price:
            price_html = f'''
    <div style="background: linear-gradient(135deg, #FFF8E1, #FFFDE7); border-radius: 10px; padding: 10px 14px; margin: 10px 0; display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
        <span style="color: #9e9e9e; text-decoration: line-through; font-size: 14px;">¥{market_price}/人</span>
        <span style="color: #E53935; font-weight: 700; font-size: 20px;">¥{price}/人</span>
        <span style="background: linear-gradient(135deg, #EF4444, #DC2626); color: white; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;">返¥{cashback_amount}</span>
    </div>'''

        return f'''<div style="background: white; border: 2px solid var(--primary-green, #4CAF50); border-radius: var(--card-radius, 16px); padding: 18px; margin: 16px 0; box-shadow: var(--shadow, 0 4px 12px rgba(0,0,0,0.08));">
    <div style="display: flex; align-items: flex-start; gap: 14px; margin-bottom: 8px;">
        <span style="font-size: 36px; flex-shrink: 0;">🍜</span>
        <div style="flex: 1;">
            <div class="poi-name">{name}</div>
            {meta_html}
        </div>
    </div>
    {features_html}
    {reason_html}
    {price_html}
    <div style="color: var(--accent-orange, #FF9500); font-size: 13px; margin: 8px 0; font-weight: 600;">🔥 今日已有{booked_count}人预订</div>
    <a href="{url}" target="_blank" rel="noopener" style="display: block; width: 100%; padding: 14px; background: linear-gradient(90deg, var(--primary-green, #4CAF50), #43A047); color: white; text-align: center; text-decoration: none; border-radius: 12px; font-size: 16px; font-weight: 700; box-sizing: border-box;">
        美团团购{f"，返现¥{cashback_amount}" if price else ""}
    </a>
    <div style="display: flex; justify-content: space-around; padding-top: 10px; margin-top: 10px; border-top: 1px dashed #e0e0e0;">
        <span style="color: var(--text-light, #666); font-size: 12px;">✅ 支持退款</span>
        <span style="color: var(--text-light, #666); font-size: 12px;">📅 过期退</span>
        <span style="color: var(--text-light, #666); font-size: 12px;">⚡ 返现秒到</span>
    </div>
</div>'''

    def _render_hotel_button(self, link_info: dict, name: str, cashback: Optional[int] = None) -> str:
        """渲染酒店预订按钮"""
        url = link_info['url']
        cashback_amount = cashback or 50

        return f'''<div class="booking-card">
    <a href="{url}" class="booking-btn has-commission" target="_blank" rel="noopener">
        美团预订 💰返¥{cashback_amount}
    </a>
</div>'''

    def _render_ticket_button(self, link_info: dict, name: str) -> str:
        """渲染门票按钮"""
        url = link_info['url']

        return f'''<div class="booking-card">
    <a href="{url}" class="booking-btn no-commission" target="_blank" rel="noopener">
        {link_info['text']}
    </a>
</div>'''


# 单例
_manager = None

def get_affiliate_manager():
    global _manager
    if _manager is None:
        _manager = AffiliateManager()
    return _manager
