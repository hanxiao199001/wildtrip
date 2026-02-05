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
        # 联盟链接状态
        self.meituan_status = 'pending'  # pending | approved
        self.fliggy_status = 'pending'   # pending | approved
        
        # 联盟链接模板（审核通过后填入）
        self.meituan_template = None  # 例如: "https://union.meituan.com/..."
        self.fliggy_template = None   # 例如: "https://s.click.taobao.com/..."
    
    def generate_booking_link(
        self, 
        poi_type: str,  # 'restaurant' | 'hotel' | 'ticket'
        name: str, 
        city: str = '',
        affiliate_link: Optional[str] = None
    ) -> Dict[str, str]:
        """
        生成预订链接
        
        Args:
            poi_type: POI类型（餐厅/酒店/门票）
            name: 名称
            city: 城市（可选）
            affiliate_link: 联盟链接（审核通过后）
        
        Returns:
            {
                'url': '链接地址',
                'text': '显示文本',
                'status': 'approved' | 'pending',
                'platform': 'meituan' | 'fliggy'
            }
        """
        if poi_type == 'restaurant':
            return self._generate_meituan_link(name, city, affiliate_link)
        elif poi_type in ['hotel', 'ticket']:
            return self._generate_fliggy_link(poi_type, name, city, affiliate_link)
        else:
            return self._generate_search_link(name, city)
    
    def _generate_meituan_link(
        self, 
        name: str, 
        city: str = '',
        affiliate_link: Optional[str] = None
    ) -> Dict[str, str]:
        """生成美团链接（餐饮）"""
        
        if self.meituan_status == 'approved' and affiliate_link:
            # 审核通过，使用联盟链接
            return {
                'url': affiliate_link,
                'text': f'🛒 团购：{name}',
                'status': 'approved',
                'platform': 'meituan'
            }
        else:
            # 审核中，使用搜索链接
            keyword = f"{city} {name}" if city else name
            search_url = f"https://www.meituan.com/s/{quote(keyword)}"
            
            return {
                'url': search_url,
                'text': f'🔍 美团搜索：{name}',
                'status': 'pending',
                'platform': 'meituan'
            }
    
    def _generate_fliggy_link(
        self,
        poi_type: str,
        name: str,
        city: str = '',
        affiliate_link: Optional[str] = None
    ) -> Dict[str, str]:
        """生成飞猪链接（酒店/门票）"""
        
        if self.fliggy_status == 'approved' and affiliate_link:
            # 审核通过，使用联盟链接
            type_emoji = '🏨' if poi_type == 'hotel' else '🎫'
            type_text = '酒店预订' if poi_type == 'hotel' else '门票预订'
            
            return {
                'url': affiliate_link,
                'text': f'{type_emoji} {type_text}：{name}',
                'status': 'approved',
                'platform': 'fliggy'
            }
        else:
            # 审核中，使用搜索链接
            keyword = f"{city} {name}" if city else name
            
            if poi_type == 'hotel':
                # 飞猪酒店搜索
                search_url = f"https://s.fliggy.com/hotel/?keyword={quote(keyword)}"
                return {
                    'url': search_url,
                    'text': f'🔍 飞猪搜索：{name}',
                    'status': 'pending',
                    'platform': 'fliggy'
                }
            else:
                # 飞猪门票搜索
                search_url = f"https://s.fliggy.com/ticket/?keyword={quote(keyword)}"
                return {
                    'url': search_url,
                    'text': f'🔍 飞猪搜索：{name}',
                    'status': 'pending',
                    'platform': 'fliggy'
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
        渲染预订按钮HTML
        
        Args:
            poi_type: POI类型
            name: 名称
            price: 价格（可选）
            cashback: 返现金额（可选）
            city: 城市
            affiliate_link: 联盟链接
        
        Returns:
            HTML字符串（审核中返回空字符串）
        """
        link_info = self.generate_booking_link(poi_type, name, city, affiliate_link)
        
        # 🔥 审核中不显示任何按钮
        if link_info['status'] == 'pending':
            return ''
        
        # 审核通过 - 显示绿色按钮
        button_text = link_info['text']
        if cashback:
            button_text += f' 💰返¥{cashback}'
        
        return f'''<a href="{link_info['url']}" class="booking-btn approved" target="_blank" rel="noopener">
    {button_text}
</a>'''


# 单例
_manager = None

def get_affiliate_manager():
    global _manager
    if _manager is None:
        _manager = AffiliateManager()
    return _manager
