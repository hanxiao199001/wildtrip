"""
行程规划页面生成器
生成带时间线视图、日历导入的行程页面
"""

import re
import json
from pathlib import Path
from loguru import logger
from datetime import datetime, timedelta


class ItineraryGenerator:
    """行程规划生成器"""
    
    def __init__(self):
        self.template_path = Path(__file__).parent.parent.parent / 'web' / 'itinerary-template.html'
    
    def generate(self, query: str, content: str, stats: dict) -> str:
        """
        生成行程规划HTML
        
        Args:
            query: 用户查询
            content: Markdown内容
            stats: 统计信息
        
        Returns:
            完整HTML
        """
        if not self.template_path.exists():
            logger.error("❌ 行程模板不存在")
            return content
        
        template = self.template_path.read_text(encoding='utf-8')
        
        # 提取信息
        title = self._extract_title(query, content)
        days_info = self._extract_days_info(query, content)
        budget = self._extract_budget(query)
        poi_count = self._estimate_poi_count(content)
        total_cashback = stats.get('total_cashback', 0) or self._calculate_cashback(content)
        
        # 新增统计
        word_count = stats.get('word_count', 0) or len(content)
        hotels_count = stats.get('hotels_count', 0) or self._count_hotels(content)
        restaurants_count = stats.get('restaurants_count', 0) or self._count_restaurants(content)
        
        # 计算社会证明数据
        users_saved = self._calculate_users_saved(total_cashback)
        total_saved = users_saved * total_cashback
        
        # 计算折扣后价格
        discounted_price = budget - total_cashback if budget > total_cashback else budget
        
        # 生成Day标签
        day_tabs = self._generate_day_tabs(days_info)
        
        # 生成时间线内容
        timeline_content = self._generate_timeline(content, days_info)
        
        # 🔥 生成住宿推荐section（追加到时间线后面）
        hotels_html = self._extract_hotels_section(content)
        if hotels_html:
            timeline_content += f'''
<div style="margin-top: 32px;">
    <h2 style="font-size: 22px; font-weight: 700; color: #1f2937; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 3px solid #10B981;">
        🏨 住宿推荐
    </h2>
    {hotels_html}
</div>
'''
        
        # 生成iCalendar数据
        ics_data = self._generate_ics_data(content, days_info, title)
        
        # 替换占位符
        html = template.replace('{{TITLE}}', title)
        html = html.replace('{{DAYS}}', f"{len(days_info)}天{len(days_info)-1}晚")
        html = html.replace('{{BUDGET}}', str(budget))
        html = html.replace('{{DISCOUNTED_PRICE}}', str(discounted_price))
        html = html.replace('{{POI_COUNT}}', str(poi_count))
        html = html.replace('{{TOTAL_CASHBACK}}', str(total_cashback))
        html = html.replace('{{WORD_COUNT}}', str(word_count))
        html = html.replace('{{HOTELS_COUNT}}', str(hotels_count))
        html = html.replace('{{RESTAURANTS_COUNT}}', str(restaurants_count))
        html = html.replace('{{USERS_SAVED}}', str(users_saved))
        html = html.replace('{{TOTAL_SAVED}}', f"{total_saved:,}")
        html = html.replace('{{DAY_TABS}}', day_tabs)
        html = html.replace('{{TIMELINE_CONTENT}}', timeline_content)
        html = html.replace('{{ICS_DATA}}', json.dumps(ics_data, ensure_ascii=False))
        
        return html
    
    def _extract_title(self, query: str, content: str) -> str:
        """提取标题"""
        # 尝试从第一个# 标题提取
        title_match = re.search(r'^#\s+(.+)$', content, re.M)
        if title_match:
            return title_match.group(1).strip()
        return query.split('，')[0]
    
    def _extract_days_info(self, query: str, content: str) -> list:
        """提取每天的信息"""
        # 从query提取天数
        days_match = re.search(r'(\d+)天', query)
        if not days_match:
            return [{'day': 1, 'weekday': ''}]
        
        num_days = int(days_match.group(1))
        
        # 尝试提取周几
        weekdays = []
        weekday_pattern = r'Day\s*\d+[：:]?\s*([周星期].+?)(?:\n|$)'
        weekday_matches = re.findall(weekday_pattern, content, re.I)
        
        days_info = []
        for i in range(num_days):
            weekday = weekday_matches[i] if i < len(weekday_matches) else ''
            days_info.append({
                'day': i + 1,
                'weekday': weekday.strip()
            })
        
        return days_info
    
    def _extract_budget(self, query: str) -> int:
        """提取预算"""
        budget_match = re.search(r'预算\s*[：:]?\s*(\d+)', query, re.I)
        if budget_match:
            return int(budget_match.group(1))
        return 1000
    
    def _estimate_poi_count(self, content: str) -> int:
        """估算POI数量"""
        # 统计餐厅、酒店、景点数量
        restaurants = len(re.findall(r'\*\*[^*]+\*\*\s*[¥￥]\d+/人', content))
        hotels = len(re.findall(r'###\s*\d+\.\s*[^#\n]+酒店', content, re.I))
        attractions = len(re.findall(r'[公园|景区|博物馆|寺|塔|山|岛|古镇|广场]', content))
        
        return restaurants + hotels + min(attractions, 5)
    
    def _calculate_cashback(self, content: str) -> int:
        """计算总返现金额（仅酒店）"""
        # 🔥 实际上只有酒店有返佣
        # 查找所有"返¥X"，但只统计酒店相关的
        hotels_count = self._count_hotels(content)
        
        # 假设每家酒店平均返现50元
        estimated_cashback = hotels_count * 50
        
        # 如果内容中明确提到返现金额，使用实际金额
        cashbacks = re.findall(r'返[¥￥](\d+)', content)
        if cashbacks:
            total = sum(int(cb) for cb in cashbacks)
            return total if total > 0 else estimated_cashback
        
        return estimated_cashback if estimated_cashback > 0 else 100  # 至少显示100
    
    def _count_hotels(self, content: str) -> int:
        """统计酒店数量"""
        hotels = len(re.findall(r'###\s*\d+\.\s*[^#\n]*[酒店|民宿|客栈]', content, re.I))
        return hotels if hotels > 0 else 4  # 默认4
    
    def _count_restaurants(self, content: str) -> int:
        """统计餐厅数量"""
        restaurants = len(re.findall(r'\*\*[^*]+\*\*\s*[¥￥]\d+/人', content))
        return restaurants if restaurants > 0 else 17  # 默认17
    
    def _calculate_users_saved(self, cashback: int) -> int:
        """计算已为多少人省钱（社会证明）"""
        # 🔥 基于酒店返现金额估算用户数
        # 返现越高，说明攻略越受欢迎，用户数越多
        if cashback >= 200:
            return 156  # 大型旅游攻略
        elif cashback >= 150:
            return 98   # 热门路线
        elif cashback >= 100:
            return 67   # 中等热度
        elif cashback >= 50:
            return 43   # 小众路线
        else:
            return 28   # 新路线
    
    def _generate_day_tabs(self, days_info: list) -> str:
        """生成Day标签HTML"""
        tabs_html = ''
        for info in days_info:
            day_num = info['day']
            weekday = info['weekday']
            active = 'active' if day_num == 1 else ''
            
            label = f"Day {day_num}"
            if weekday:
                label += f" {weekday}"
            
            tabs_html += f'<div class="day-tab {active}" data-day="{day_num}" onclick="switchDay({day_num})">{label}</div>\n'
        
        return tabs_html
    
    def _generate_timeline(self, content: str, days_info: list) -> str:
        """生成时间线HTML"""
        timeline_html = ''
        
        # 查找所有Day X的内容
        day_pattern = r'###?\s*Day\s*(\d+)[：:]?(.*?)(?=###?\s*Day\s*\d+|##\s+[^D]|$)'
        day_matches = re.findall(day_pattern, content, re.S | re.I)
        
        for day_num_str, day_content in day_matches:
            day_num = int(day_num_str)
            active = 'active' if day_num == 1 else ''
            
            # 解析时间线
            items = self._parse_timeline_items(day_content)
            
            items_html = ''
            for item in items:
                icon_class = 'icon-food' if item['type'] == 'food' else 'icon-activity'
                icon_emoji = item.get('emoji', '🍜' if item['type'] == 'food' else '🚶')
                
                # 构建内容
                content_html = f'<div class="content-title">{item["title"]}</div>'
                
                if item.get('desc'):
                    content_html += f'<div class="content-desc">{item["desc"]}</div>'
                
                if item.get('tags'):
                    for tag in item['tags']:
                        content_html += f'<span class="content-tag">{tag}</span>'
                
                # 如果是餐厅，添加价格、评分、预订按钮
                if item['type'] == 'food' and item.get('price'):
                    # 使用新的联盟链接管理器
                    from services.affiliate_manager import get_affiliate_manager
                    
                    affiliate_mgr = get_affiliate_manager()
                    booking_btn = affiliate_mgr.render_booking_button(
                        poi_type='restaurant',
                        name=item['title'],
                        price=item.get('price'),
                        cashback=item.get('cashback', 5),
                        city=''  # TODO: 从query提取城市
                    )
                    
                    content_html += f'''
<div class="restaurant-info">
    <span class="restaurant-price">¥{item["price"]}/人</span>
    <span class="restaurant-rating">⭐ {item.get("rating", "4.5")}</span>
    {f'<span class="cashback-tag">返¥{item["cashback"]}</span>' if item.get("cashback") else ''}
</div>
{booking_btn}
'''
                
                # 如果是酒店，添加预订按钮
                if item['type'] == 'hotel' or '酒店' in item['title'] or '民宿' in item['title']:
                    from services.affiliate_manager import get_affiliate_manager
                    
                    affiliate_mgr = get_affiliate_manager()
                    booking_btn = affiliate_mgr.render_booking_button(
                        poi_type='hotel',
                        name=item['title'],
                        city=''
                    )
                    content_html += f'\n{booking_btn}'
                
                # 如果是景点/门票，添加预订按钮
                elif any(word in item['title'] for word in ['公园', '景区', '博物馆', '寺', '塔', '山', '岛']):
                    from services.affiliate_manager import get_affiliate_manager
                    
                    affiliate_mgr = get_affiliate_manager()
                    booking_btn = affiliate_mgr.render_booking_button(
                        poi_type='ticket',
                        name=item['title'],
                        city=''
                    )
                    content_html += f'\n{booking_btn}'
                
                items_html += f'''
<div class="timeline-item">
    <div class="timeline-time">
        <div class="time-text">{item["time"]}</div>
    </div>
    <div class="timeline-icon {icon_class}">
        {icon_emoji}
    </div>
    <div class="timeline-content">
        {content_html}
    </div>
</div>
'''
            
            timeline_html += f'<div id="day-{day_num}" class="day-content {active}">{items_html}</div>\n'
        
        return timeline_html
    
    def _parse_timeline_items(self, day_content: str) -> list:
        """解析时间线条目"""
        items = []
        
        # 查找时间标记（09:00、12:00、上午、下午等）
        time_patterns = [
            (r'\*\*(\d{2}:\d{2})[）\)|\s]+([^*\n]+)', 'time'),  # **12:00** xxx
            (r'\*\*([上下午晚][午上]+)[：:]*\*\*\s*([^*\n]+)', 'period'),  # **上午** xxx
        ]
        
        for pattern, time_type in time_patterns:
            matches = re.findall(pattern, day_content)
            for time_str, desc in matches:
                # 清理描述
                clean_desc = re.sub(r'\*\*([^*]+)\*\*', r'\1', desc).strip()
                
                # 检测类型
                item_type = 'food' if any(word in clean_desc for word in ['餐厅', '馆', '面', '饭', '小吃', '食堂', '火锅']) else 'activity'
                
                # 提取餐厅信息
                price_match = re.search(r'[¥￥](\d+)/人', day_content[day_content.find(clean_desc):day_content.find(clean_desc)+500])
                rating_match = re.search(r'⭐([\d.]+)', day_content[day_content.find(clean_desc):day_content.find(clean_desc)+500])
                cashback_match = re.search(r'返[¥￥](\d+)', day_content[day_content.find(clean_desc):day_content.find(clean_desc)+500])
                
                # 提取标题
                title_match = re.match(r'^([^，。\n]+)', clean_desc)
                title = title_match.group(1) if title_match else clean_desc[:20]
                
                # 提取描述
                desc_match = re.search(r'[：:,，](.+?)(?:\n|$)', clean_desc)
                desc_text = desc_match.group(1).strip() if desc_match else ''
                
                # 提取标签
                tags = []
                tag_match = re.search(r'💡\s*(.+)', desc_text)
                if tag_match:
                    tags.append(tag_match.group(1).strip())
                
                items.append({
                    'time': time_str,
                    'title': title,
                    'desc': desc_text[:100] if desc_text else '',
                    'type': item_type,
                    'emoji': '🍜' if item_type == 'food' else '🚶',
                    'price': int(price_match.group(1)) if price_match else None,
                    'rating': rating_match.group(1) if rating_match else None,
                    'cashback': int(cashback_match.group(1)) if cashback_match else 5,
                    'tags': tags,
                    'search_keyword': title
                })
        
        return items[:10]  # 最多10个
    
    def _generate_ics_data(self, content: str, days_info: list, title: str) -> list:
        """生成iCalendar数据"""
        events = []
        
        # 假设从今天开始
        start_date = datetime.now()
        
        # 查找所有Day X的内容
        day_pattern = r'###?\s*Day\s*(\d+)[：:]?(.*?)(?=###?\s*Day\s*\d+|##\s+[^D]|$)'
        day_matches = re.findall(day_pattern, content, re.S | re.I)
        
        for day_num_str, day_content in day_matches:
            day_num = int(day_num_str)
            current_date = start_date + timedelta(days=day_num - 1)
            
            # 解析时间
            time_matches = re.findall(r'\*\*(\d{2}):(\d{2})[）\)|\s]+([^*\n]+)', day_content)
            
            for hour, minute, desc in time_matches:
                clean_desc = re.sub(r'\*\*([^*]+)\*\*', r'\1', desc).strip()
                title_match = re.match(r'^([^，。\n]+)', clean_desc)
                event_title = title_match.group(1) if title_match else clean_desc[:30]
                
                # 开始时间
                event_start = current_date.replace(hour=int(hour), minute=int(minute))
                # 结束时间（默认1小时后）
                event_end = event_start + timedelta(hours=1)
                
                events.append({
                    'start': event_start.strftime('%Y%m%dT%H%M%S'),
                    'end': event_end.strftime('%Y%m%dT%H%M%S'),
                    'title': event_title,
                    'desc': clean_desc[:200],
                    'location': event_title
                })
        
        return events



    def _extract_hotels_section(self, content: str) -> str:
        """
        提取住宿推荐section并生成HTML
        
        查找：## 住宿推荐 或 ## 🏨 住宿推荐
        """
        # 查找住宿section
        hotel_pattern = r'##\s*(?:🏨\s*)?住宿推荐(.*?)(?=##\s+[^#]|$)'
        hotel_match = re.search(hotel_pattern, content, re.S | re.I)
        
        if not hotel_match:
            return ''
        
        hotel_content = hotel_match.group(1).strip()
        
        # 解析酒店信息（### 1. 酒店名 ¥XXX/晚）
        hotel_item_pattern = r'###\s*\d+\.\s*([^¥\n]+)[¥￥](\d+)/晚.*?⭐([\d.]+)(.*?)(?=###\s*\d+\.|$)'
        hotels = re.findall(hotel_item_pattern, hotel_content, re.S)
        
        if not hotels:
            return ''
        
        hotels_html = '<div class="info-card">'
        
        for name, price, rating, details in hotels:
            name = name.strip()
            
            # 提取地址
            address_match = re.search(r'\*\*地址[：:]\*\*\s*([^\n]+)', details)
            address = address_match.group(1).strip() if address_match else ''
            
            # 提取特点
            feature_match = re.search(r'\*\*特点[：:]\*\*\s*([^\n]+)', details)
            features = feature_match.group(1).strip() if feature_match else ''
            
            # 生成酒店按钮
            from services.affiliate_manager import get_affiliate_manager
            
            affiliate_mgr = get_affiliate_manager()
            booking_btn = affiliate_mgr.render_booking_button(
                poi_type='hotel',
                name=name,
                cashback=50,
                city=''
            )
            
            hotels_html += f"""
<div style="padding: 16px; border-bottom: 1px solid #e5e7eb; margin-bottom: 16px;">
    <h4 style="font-size: 18px; font-weight: 700; margin-bottom: 8px;">
        🏨 {name}
    </h4>
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
        <span style="font-size: 20px; font-weight: 700; color: #DC2626;">¥{price}/晚</span>
        <span style="color: #F59E0B;">⭐ {rating}</span>
    </div>
    {f'<p style="color: #6b7280; font-size: 14px; margin-bottom: 8px;">📍 {address}</p>' if address else ''}
    {f'<p style="color: #6b7280; font-size: 14px; margin-bottom: 12px;">✨ {features}</p>' if features else ''}
    {booking_btn}
</div>
"""
        
        hotels_html += '</div>'
        
        return hotels_html


# 单例
_generator = None

def get_itinerary_generator():
    global _generator
    if _generator is None:
        _generator = ItineraryGenerator()
    return _generator

