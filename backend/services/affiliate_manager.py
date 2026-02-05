"""
联盟链接管理器
支持美团联盟（餐饮）+ 飞猪联盟（酒店/门票）
"""

import re
from typing import Dict, Optional
from loguru import logger
from urllib.parse import quote


class AffiliateManager:
    """联盟链接管理器"""
    
    def __init__(self):
        # 🔥 实际变现情况（2026-02-05更新）
        # 酒店：美团联盟有活动，可返佣
        self.hotel_status = 'approved'  # 酒店可以用联盟链接
        self.hotel_has_commission = True
        
        # 餐饮：暂无返佣，但保留搜索链接（提升用户体验）
        self.restaurant_status = 'search_only'  # 只能搜索，无返佣
        self.restaurant_has_commission = False
        
        # 门票：待定（需查"到综"或接入飞猪）
        self.ticket_status = 'pending'  # 待定
        self.ticket_has_commission = False
        
        # 联盟链接模板（一键取链生成）
        self.meituan_hotel_template = None  # 酒店推广链接
        self.fliggy_template = None  # 飞猪联盟（备用）
    
    def generate_booking_link(
        self, 
        poi_type: str,  # 'restaurant' | 'hotel' | 'ticket'
        name: str, 
        city: str = '',
        affiliate_link: Optional[str] = None
    ) -> Dict[str, str]:
        """
        生成预订链接（根据实际变现情况）
        
        Args:
            poi_type: POI类型（餐厅/酒店/门票）
            name: 名称
            city: 城市（可选）
            affiliate_link: 联盟链接（一键取链生成）
        
        Returns:
            {
                'url': '链接地址',
                'text': '显示文本',
                'status': 'approved' | 'search_only',
                'platform': 'meituan',
                'has_commission': True | False
            }
        """
        if poi_type == 'restaurant':
            # 餐饮：无返佣，搜索链接
            return self._generate_meituan_link(name, city, affiliate_link)
        elif poi_type == 'hotel':
            # 酒店：美团联盟有返佣
            return self._generate_hotel_link(name, city, affiliate_link)
        elif poi_type == 'ticket':
            # 门票：待定
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
        
        # 🔥 餐饮暂无返佣，只提供搜索链接
        keyword = f"{city} {name}" if city else name
        search_url = f"https://i.meituan.com/search?q={quote(keyword)}"
        
        return {
            'url': search_url,
            'text': f'去美团查看',  # 不显示"搜索"，更友好
            'status': 'search_only',  # 特殊状态：只搜索，无返佣
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
            # 有联盟链接，显示返佣按钮
            return {
                'url': affiliate_link,
                'text': f'预订返现',  # 简洁有力
                'status': 'approved',
                'platform': 'meituan',
                'has_commission': True
            }
        else:
            # 暂无联盟链接，使用搜索（但提示可返现）
            keyword = f"{city} {name}" if city else name
            search_url = f"https://i.meituan.com/search?q={quote(keyword)}"
            
            return {
                'url': search_url,
                'text': f'去美团预订',
                'status': 'approved',  # 酒店是approved，只是暂无具体链接
                'platform': 'meituan',
                'has_commission': True  # 潜在有返佣
            }
    
    def _generate_ticket_link(
        self,
        name: str,
        city: str = '',
        affiliate_link: Optional[str] = None
    ) -> Dict[str, str]:
        """生成门票链接（待定：美团或飞猪）"""
        
        # 🔥 门票暂时用美团搜索（后续可切换到飞猪）
        keyword = f"{city} {name} 门票" if city else f"{name} 门票"
        search_url = f"https://i.meituan.com/search?q={quote(keyword)}"
        
        return {
            'url': search_url,
            'text': f'查看门票',
            'status': 'search_only',
            'platform': 'meituan',
            'has_commission': False  # 待确认
        }
    
    def _generate_search_link(self, name: str, city: str = '') -> Dict[str, str]:
        """生成通用搜索链接"""
        keyword = f"{city} {name}" if city else name
        search_url = f"https://www.baidu.com/s?wd={quote(keyword)}"
        
        return {
            'url': search_url,
            'text': f'🔍 搜索：{name}',
            'status': 'pending',
            'platform': 'search'
        }
    
    def render_booking_button(
        self,
        poi_type: str,
        name: str,
        price: Optional[int] = None,
        cashback: Optional[int] = None,
        city: str = '',
        affiliate_link: Optional[str] = None
    ) -> str:
        """
        渲染预订按钮HTML（根据实际变现情况）
        
        Args:
            poi_type: POI类型
            name: 名称
            price: 价格（可选）
            cashback: 返现金额（可选，仅酒店显示）
            city: 城市
            affiliate_link: 联盟链接（一键取链）
        
        Returns:
            HTML字符串
        """
        link_info = self.generate_booking_link(poi_type, name, city, affiliate_link)
        
        # 构建按钮文本
        button_text = link_info['text']
        
        # 🔥 只有酒店显示返现金额
        if poi_type == 'hotel' and link_info.get('has_commission') and cashback:
            button_text += f' 💰返¥{cashback}'
        
        # 按钮样式
        if link_info.get('has_commission'):
            # 有返佣：绿色按钮
            button_class = 'booking-btn has-commission'
        else:
            # 无返佣（如餐饮）：蓝色按钮
            button_class = 'booking-btn no-commission'
        
        return f'''<a href="{link_info['url']}" class="{button_class}" target="_blank" rel="noopener">
    {button_text}
</a>'''


# 单例
_manager = None

def get_affiliate_manager():
    global _manager
    if _manager is None:
        _manager = AffiliateManager()
    return _manager
