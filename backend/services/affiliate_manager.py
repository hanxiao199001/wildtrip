"""
联盟链接管理器
<<<<<<< HEAD
支持美团联盟（餐饮）+ 淘宝联盟（酒店/门票/美食券）
=======
支持美团联盟（餐饮）+ 飞猪联盟（酒店/门票）
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3
"""

import re
import random
<<<<<<< HEAD
import os
from typing import Dict, Optional, List
from loguru import logger
from urllib.parse import quote, urlencode

# 导入淘宝联盟
try:
    from services.taobao_affiliate import get_taobao_affiliate
    TAOBAO_AVAILABLE = True
except ImportError:
    TAOBAO_AVAILABLE = False
    logger.warning("⚠️ 淘宝联盟模块未找到")
=======
from typing import Dict, Optional
from loguru import logger
from urllib.parse import quote
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3


class AffiliateManager:
    """联盟链接管理器"""

    def __init__(self):
<<<<<<< HEAD
        # 实际变现情况（2026-02-09更新）
        # 优先使用淘宝联盟（聚推客）
        self.hotel_status = 'approved'
        self.hotel_has_commission = True

        # 餐饮：同时提供美团+淘宝
        self.restaurant_status = 'approved'
        self.restaurant_has_commission = True

        # 门票：同时提供美团+淘宝
        self.ticket_status = 'approved'
        self.ticket_has_commission = True

        # 🔥 美团联盟配置（从.env读取）
        self.meituan_pid = os.getenv('MEITUAN_PID', 'clcj473753202602031236059_001')
        self.meituan_act_id = os.getenv('MEITUAN_ACT_ID', '418')
        self.meituan_sid = os.getenv('MEITUAN_SID', '001')
        
        # 🔥 淘宝联盟（聚推客）
        self.taobao_available = TAOBAO_AVAILABLE
        if self.taobao_available:
            self.taobao = get_taobao_affiliate()
            logger.info(f"✅ 淘宝联盟已启用（聚推客）")
        
        logger.info(f"✅ 联盟配置完成 | 美团+淘宝双链接模式")

    def _build_relay_url(self, name: str, city: str, poi_type: str) -> str:
        """生成野游记中转页URL（负责CPS追踪 + 精准搜索落地）"""
        from urllib.parse import urlencode
        server = os.getenv('SERVER_BASE_URL', 'http://47.82.159.93:5000')
        params = {'keyword': name, 'type': poi_type}
        if city:
            params['city'] = city
        return f"{server}/api/relay/meituan?{urlencode(params)}"
=======
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
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3

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
<<<<<<< HEAD
        """生成美团链接（餐饮团购）- 中转页模式：CPS追踪 + 精准搜索落地"""
        relay_url = self._build_relay_url(name, city, 'food')

        # 小程序端：用聚推客API返回的page_path（含CPS token）
        from services.jutuike_api import get_jutuike_api
        api = get_jutuike_api()
        link = api.get_food_link()
        mp_appid = 'wxde8ac0a21135c07d'
        mp_username = 'gh_870576f3c6f9'
        if link and link.get('mp_path'):
            mp_path = link['mp_path']
        else:
            mp_path = f"/index/pages/h5/h5?weburl={quote(relay_url)}"

        logger.info(f"📱 美食团购中转: {name} -> {relay_url}")

        return {
            'url': relay_url,
            'text': f'去美团搜"{name}"团购',
            'status': 'promo',
            'platform': 'meituan',
            'has_commission': True,
            'mp_appid': mp_appid,
            'mp_path': mp_path,
            'mp_username': mp_username,
=======
        """生成美团链接（餐饮）"""
        keyword = f"{city} {name}" if city else name
        search_url = f"https://i.meituan.com/search?q={quote(keyword)}"

        return {
            'url': search_url,
            'text': f'美团团购',
            'status': 'search_only',
            'platform': 'meituan',
            'has_commission': False
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3
        }

    def _generate_hotel_link(
        self,
        name: str,
        city: str = '',
        affiliate_link: Optional[str] = None
    ) -> Dict[str, str]:
<<<<<<< HEAD
        """生成酒店链接（同时支持小程序跳转和H5链接）"""
=======
        """生成酒店链接（美团联盟，有返佣）"""
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3
        if affiliate_link:
            return {
                'url': affiliate_link,
                'text': f'美团预订',
<<<<<<< HEAD
                'status': 'direct',
                'platform': 'meituan',
                'has_commission': False
            }
        else:
            relay_url = self._build_relay_url(name, city, 'hotel')

            from services.jutuike_api import get_jutuike_api
            api = get_jutuike_api()
            link = api.get_hotel_link()
            mp_appid = 'wxde8ac0a21135c07d'
            mp_username = 'gh_870576f3c6f9'
            if link and link.get('mp_path'):
                mp_path = link['mp_path']
            else:
                mp_path = f"/index/pages/h5/h5?weburl={quote(relay_url)}"

            logger.info(f"🏨 酒店中转链接: {name} -> {relay_url}")

            return {
                'url': relay_url,
                'text': f'去美团预订"{name}"',
                'status': 'promo',
                'platform': 'meituan',
                'has_commission': True,
                'mp_appid': mp_appid,
                'mp_path': mp_path,
                'mp_username': mp_username,
=======
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
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3
            }

    def _generate_ticket_link(
        self,
        name: str,
        city: str = '',
        affiliate_link: Optional[str] = None
    ) -> Dict[str, str]:
<<<<<<< HEAD
        """生成门票链接（美食团购活动入口，含景区门票）"""
        relay_url = self._build_relay_url(name, city, 'ticket')

        from services.jutuike_api import get_jutuike_api
        api = get_jutuike_api()
        link = api.get_food_link()
        mp_appid = 'wxde8ac0a21135c07d'
        mp_username = 'gh_870576f3c6f9'
        if link and link.get('mp_path'):
            mp_path = link['mp_path']
        else:
            mp_path = f"/index/pages/h5/h5?weburl={quote(relay_url)}"

        logger.info(f"🎫 门票中转链接: {name} -> {relay_url}")

        return {
            'url': relay_url,
            'text': f'去美团搜"{name}门票"',
            'status': 'promo',
            'platform': 'meituan',
            'has_commission': True,
            'mp_appid': mp_appid,
            'mp_path': mp_path,
            'mp_username': mp_username,
=======
        """生成门票链接（美团搜索）"""
        keyword = f"{city} {name} 门票" if city else f"{name} 门票"
        search_url = f"https://i.meituan.com/search?q={quote(keyword)}"

        return {
            'url': search_url,
            'text': f'查看门票',
            'status': 'search_only',
            'platform': 'meituan',
            'has_commission': False
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3
        }

    def _generate_search_link(self, name: str, city: str = '') -> Dict[str, str]:
        """生成通用搜索链接"""
        keyword = f"{city} {name}" if city else name
<<<<<<< HEAD
        
        # 🔥 添加联盟参数（带返佣）
        params = {
            'q': keyword,
            'actId': self.meituan_act_id,
            'sid': self.meituan_sid,
            'pid': self.meituan_pid
        }
        search_url = f"https://i.meituan.com/search?{urlencode(params)}"
=======
        search_url = f"https://i.meituan.com/search?q={quote(keyword)}"
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3

        return {
            'url': search_url,
            'text': f'去美团查看',
<<<<<<< HEAD
            'status': 'approved',
            'platform': 'meituan',
            'has_commission': True
=======
            'status': 'search_only',
            'platform': 'meituan',
            'has_commission': False
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3
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

<<<<<<< HEAD
    def render_meituan_promo_banner(self, city: str) -> str:
        """
        渲染美团推广横幅（放在攻略底部）
        
        Args:
            city: 城市名
            
        Returns:
            HTML横幅
        """
        # 使用美团团购推广链接
        meituan_url = f"https://click.meituan.com/t?t=1&c=1&q={city}团购"
        
        return f'''
<div style="margin: 30px 0; padding: 20px; background: linear-gradient(135deg, #FFC300 0%, #FFE66D 100%); border-radius: 16px; text-align: center; box-shadow: 0 8px 20px rgba(255,195,0,0.3);">
    <div style="font-size: 24px; font-weight: 700; color: #333; margin-bottom: 10px;">
        💰 美团下单，立享返现
    </div>
    <div style="font-size: 14px; color: rgba(0,0,0,0.7); margin-bottom: 16px;">
        酒店、美食、门票，美团预订即可获得返现
    </div>
    <a href="{meituan_url}" target="_blank" rel="noopener" 
       style="display: inline-block; padding: 12px 32px; background: #FFC300; color: #333; 
              text-decoration: none; border-radius: 24px; font-size: 16px; font-weight: 700; 
              box-shadow: 0 4px 12px rgba(0,0,0,0.15); transition: transform 0.2s;">
        立即领取优惠 →
    </a>
    <div style="margin-top: 12px; font-size: 12px; color: rgba(0,0,0,0.6);">
        ✅ 返现秒到账 · 支持退款 · 官方保障
    </div>
</div>
'''
    
    def render_taobao_cashback_banner(self, city: str) -> str:
        """
        渲染淘宝返现横幅（放在攻略底部）
        
        Args:
            city: 城市名
            
        Returns:
            HTML横幅
        """
        # 使用聚推客的推广页面（需要在后台获取）
        # 临时方案：跳转到淘宝旅行频道
        taobao_travel_url = "https://s.taobao.com/search?q={}旅游酒店".format(city)
        
        # 如果有聚推客的专属推广链接，在这里配置
        jutulke_promo_link = os.getenv('JUTULKE_PROMO_LINK', '')
        if jutulke_promo_link:
            taobao_travel_url = jutulke_promo_link
        
        return f'''
<div style="margin: 30px 0; padding: 20px; background: linear-gradient(135deg, #FF6B6B 0%, #FFE66D 100%); border-radius: 16px; text-align: center; box-shadow: 0 8px 20px rgba(255,107,107,0.3);">
    <div style="font-size: 24px; font-weight: 700; color: #fff; margin-bottom: 10px;">
        💰 淘宝预订，最高返现15%
    </div>
    <div style="font-size: 14px; color: rgba(255,255,255,0.9); margin-bottom: 16px;">
        酒店、门票、美食券，淘宝下单即可获得返现
    </div>
    <a href="{taobao_travel_url}" target="_blank" rel="noopener" 
       style="display: inline-block; padding: 12px 32px; background: #fff; color: #FF6B6B; 
              text-decoration: none; border-radius: 24px; font-size: 16px; font-weight: 700; 
              box-shadow: 0 4px 12px rgba(0,0,0,0.15); transition: transform 0.2s;">
        立即领取优惠 →
    </a>
    <div style="margin-top: 12px; font-size: 12px; color: rgba(255,255,255,0.8);">
        ✅ 返现秒到账 · 支持退款 · 官方保障
    </div>
</div>
'''
    
=======
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3
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
<<<<<<< HEAD
    <a href="{url}" target="_blank" rel="noopener"{mp_attrs} style="display: block; width: 100%; padding: 14px; background: linear-gradient(90deg, var(--primary-green, #4CAF50), #43A047); color: white; text-align: center; text-decoration: none; border-radius: 12px; font-size: 16px; font-weight: 700; box-sizing: border-box;">
=======
    <a href="{url}" target="_blank" rel="noopener" style="display: block; width: 100%; padding: 14px; background: linear-gradient(90deg, var(--primary-green, #4CAF50), #43A047); color: white; text-align: center; text-decoration: none; border-radius: 12px; font-size: 16px; font-weight: 700; box-sizing: border-box;">
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3
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
