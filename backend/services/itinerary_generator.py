"""
行程规划页面生成器
生成带时间线视图、日历导入的行程页面
"""

import re
import json
from pathlib import Path
from loguru import logger
from datetime import datetime, timedelta
from urllib.parse import quote


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
        
        # 🔥 预处理：转换Markdown表格
        content = self._convert_markdown_tables(content)
        
        # 🔥 预处理：转换Markdown链接为HTML按钮
        content = self._convert_markdown_links_to_buttons(content, query)
        
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
        
        # 🔥 转换Markdown表格为HTML表格
        timeline_content = self._convert_markdown_tables(timeline_content)
        
        # 🔥 生成住宿推荐section（使用HotelExtractor）
        hotel_extractor = HotelExtractor()
        hotels = hotel_extractor.extract_hotels(content, query)
        hotel_quick_card = ''
        
        if hotels:
            # 渲染所有酒店卡片
            hotels_html = '\n'.join([hotel_extractor.render_hotel_card(hotel) for hotel in hotels])
            
            # 提取第一家酒店信息，生成顶部快速预订卡片
            hotel_quick_card = hotel_extractor.render_hotel_card(hotels[0])
            
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
        
        # 🔥 插入酒店快速预订卡片（如果有的话）
        if hotel_quick_card:
            html = html.replace('<!-- 这里会通过JS动态插入酒店预订卡片 -->', hotel_quick_card)
            html = html.replace('style="display:none;"', '')  # 显示卡片容器
        
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


    def _generate_hotel_quick_card(self, content: str) -> str:
        """
        生成顶部酒店快速预订卡片（醒目位置）
        
        提取第一家推荐酒店的信息
        """
        # 查找住宿section
        hotel_pattern = r'##\s*(?:🏨\s*)?住宿推荐(.*?)(?=##\s+[^#]|$)'
        hotel_match = re.search(hotel_pattern, content, re.S | re.I)
        
        if not hotel_match:
            return ''
        
        hotel_content = hotel_match.group(1).strip()
        
        # 解析第一家酒店信息
        hotel_item_pattern = r'###\s*\d+\.\s*([^¥\n]+)[¥￥](\d+)/晚.*?⭐([\d.]+)(.*?)(?=###\s*\d+\.|$)'
        hotels = re.findall(hotel_item_pattern, hotel_content, re.S)
        
        if not hotels:
            return ''
        
        # 取第一家酒店
        name, price, rating, details = hotels[0]
        name = name.strip()
        price = int(price)
        
        # 提取特点
        feature_match = re.search(r'\*\*特点[：:]\*\*\s*([^\n]+)', details)
        features = feature_match.group(1).strip() if feature_match else name
        
        # 计算返现和折扣后价格
        cashback = 50  # 假设返现50元
        discounted_price = price - cashback
        
        # 生成酒店预订按钮
        from services.affiliate_manager import get_affiliate_manager
        
        affiliate_mgr = get_affiliate_manager()
        booking_link_info = affiliate_mgr.generate_booking_link('hotel', name, '')
        booking_url = booking_link_info['url']
        
        return f"""
<div class="hotel-quick-card" style="position: relative;">
    <div class="hotel-cashback-tag">返¥{cashback}</div>
    <div class="hotel-quick-header">
        <div class="hotel-quick-icon">🏨</div>
        <div class="hotel-quick-info">
            <h3>{features}</h3>
            <div class="hotel-quick-price">
                <span class="hotel-price-original">¥{price}</span>
                <span>→</span>
                <span class="hotel-price-discount">¥{discounted_price}/晚</span>
            </div>
        </div>
    </div>
    <a href="{booking_url}" class="hotel-quick-book-btn" target="_blank" rel="noopener">
        💰 ¥{cashback} 即将到账 → 立即预订
    </a>
</div>
"""


    def _convert_markdown_tables(self, text: str) -> str:
        """
        将Markdown表格转换为HTML表格（增强版）
        
        支持格式：
        | 项目 | 金额 | 说明 |
        |------|------|------|
        | 住宿 | ¥900 | 2晚 |
        """
        import re
        
        # 匹配Markdown表格（更宽松的正则）
        table_pattern = r'\|(.+)\|\n\|[-:\s|]+\|\n((?:\|.+\|\n?)+)'
        
        def replace_table(match):
            header_line = match.group(1)
            body_lines = match.group(2)
            
            # 解析表头
            headers = [h.strip() for h in header_line.split('|') if h.strip()]
            
            # 生成HTML表格（带美观样式）
            html = '''<table class="budget-table" style="width: 100%; border-collapse: collapse; margin: 20px 0; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
<thead>
<tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">'''
            
            for h in headers:
                html += f'<th style="padding: 16px; text-align: left; font-weight: 600; font-size: 15px;">{h}</th>'
            
            html += '</tr>\n</thead>\n<tbody>'
            
            # 解析行
            rows = [r.strip() for r in body_lines.strip().split('\n') if r.strip()]
            for idx, row in enumerate(rows):
                cells = [c.strip() for c in row.split('|') if c.strip()]
                bg_color = '#f9fafb' if idx % 2 == 0 else 'white'
                html += f'<tr style="background: {bg_color}; border-bottom: 1px solid #e5e7eb;">'
                for cell in cells:
                    html += f'<td style="padding: 14px; font-size: 14px;">{cell}</td>'
                html += '</tr>\n'
            
            html += '</tbody></table>'
            return html
        
        return re.sub(table_pattern, replace_table, text, flags=re.MULTILINE)

    def _convert_markdown_links_to_buttons(self, text: str, query: str) -> str:
        """
        将Markdown链接转换为HTML按钮
        
        修复问题：[美团预订](url)等Markdown链接没有渲染
        """
        import re
        from services.affiliate_manager import get_affiliate_manager
        
        # 提取城市（用于生成联盟链接）
        city_match = re.search(r'([\u4e00-\u9fa5]{2,})\d*天', query)
        city = city_match.group(1) if city_match else ''
        
        affiliate_mgr = get_affiliate_manager()
        
        # 查找所有Markdown链接：[文本](url) 或 [文本](LINK_XXX_名称)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        def replace_link(match):
            link_text = match.group(1)
            link_url = match.group(2)
            
            # 如果是占位符（LINK_FOOD_名称等），生成真实按钮
            if link_url.startswith('LINK_'):
                parts = link_url.split('_', 2)
                if len(parts) == 3:
                    _, poi_type, name = parts
                    type_map = {'FOOD': 'restaurant', 'HOTEL': 'hotel', 'TICKET': 'ticket'}
                    real_type = type_map.get(poi_type, 'restaurant')
                    return affiliate_mgr.render_booking_button(
                        poi_type=real_type,
                        name=name,
                        city=city
                    )
            
            # 如果是URL链接，判断按钮类型
            if '美团' in link_text or '团购' in link_text:
                # 从前文提取名称
                before_text = text[:match.start()]
                name_match = re.search(r'[\*]{0,2}([^\*\n]{2,10})[\*]{0,2}[\s]*$', before_text)
                name = name_match.group(1).strip() if name_match else '商家'
                
                # 判断类型
                if '酒店' in name or '宾馆' in name or '民宿' in name:
                    poi_type = 'hotel'
                elif any(word in name for word in ['餐厅', '馆', '店', '楼', '坊']):
                    poi_type = 'restaurant'
                else:
                    poi_type = 'ticket'
                
                return affiliate_mgr.render_booking_button(
                    poi_type=poi_type,
                    name=name,
                    city=city
                )
            
            # 保留原样（普通链接）
            return match.group(0)
        
        return re.sub(link_pattern, replace_link, text)

    def _render_restaurant_card(self, restaurant_info: dict, city: str = '') -> str:
        """
        统一的餐厅卡片渲染（增强版）
        
        Args:
            restaurant_info: 餐厅信息字典
            city: 城市名
        
        Returns:
            HTML字符串
        """
        from urllib.parse import quote
        
        name = restaurant_info.get('name', '')
        price = restaurant_info.get('price', 0)
        rating = restaurant_info.get('rating', 0)
        features = restaurant_info.get('features', [])
        desc = restaurant_info.get('desc', '')
        
        # 生成预订按钮
        from services.affiliate_manager import get_affiliate_manager
        
        affiliate_mgr = get_affiliate_manager()
        booking_btn = affiliate_mgr.render_booking_button(
            poi_type='restaurant',
            name=name,
            price=price,
            city=city
        )
        
        return f"""
<div class="restaurant-card" style="background: white; border-radius: 12px; padding: 20px; margin: 16px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid #10B981;">
    <div class="card-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <h4 style="font-size: 18px; font-weight: 700; color: #1f2937; margin: 0;">🍜 {name}</h4>
        <div class="rating" style="display: flex; align-items: center; gap: 12px;">
            <span style="color: #F59E0B; font-size: 14px;">⭐ {rating}</span>
            <span style="color: #DC2626; font-weight: 600; font-size: 16px;">¥{price}/人</span>
        </div>
    </div>
    
    {f'<p style="color: #6b7280; font-size: 14px; margin-bottom: 12px;">{desc}</p>' if desc else ''}
    
    {f'<div class="features" style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px;">' + ''.join([f'<span style="background: #F3F4F6; color: #4B5563; padding: 4px 12px; border-radius: 12px; font-size: 13px;">{f}</span>' for f in features]) + '</div>' if features else ''}
    
    {booking_btn}
</div>
"""



class HotelExtractor:
    """酒店信息提取器"""
    
    def extract_hotels(self, content: str, query: str) -> list:
        """
        从攻略内容提取酒店信息
        
        Args:
            content: 攻略内容
            query: 用户查询（用于提取城市）
        
        Returns:
            酒店信息列表
        """
        hotels = []
        
        # 查找住宿推荐section
        hotel_pattern = r'##\s*(?:🏨\s*)?住宿推荐(.*?)(?=\n##\s+(?!#)|$)'
        hotel_match = re.search(hotel_pattern, content, re.S | re.I)
        
        if not hotel_match:
            return hotels
        
        hotel_content = hotel_match.group(1).strip()
        
        # 解析酒店信息（### 1. 酒店名）
        hotel_item_pattern = r'###\s*\d+\.\s*([^\n]+?)\n.*?\*\*价格[：:]\*\*\s*[¥￥](\d+)/晚.*?⭐([\d.]+)(.*?)(?=###\s*\d+\.|$)'
        hotel_matches = re.findall(hotel_item_pattern, hotel_content, re.S)
        
        # 提取城市
        city_match = re.search(r'([\u4e00-\u9fa5]{2,})\d*天', query)
        city = city_match.group(1) if city_match else ''
        
        for name, price, rating, details in hotel_matches:
            name = name.strip()
            price_int = int(price)
            
            # 提取位置
            location_match = re.search(r'\*\*位置[：:]\*\*\s*([^\n]+)', details)
            location = location_match.group(1).strip() if location_match else ''
            
            # 提取特点
            feature_match = re.search(r'\*\*特点[：:]\*\*\s*([^\n]+)', details)
            features = feature_match.group(1).strip() if feature_match else ''
            
            # 提取推荐理由
            reason_match = re.search(r'\*\*为什么推荐[：:]\*\*\s*([^\n]+)', details)
            reason = reason_match.group(1).strip() if reason_match else features
            
            # 计算返现金额（门市价10%佣金率，50%返给用户）
            commission_rate = 0.10  # 10%佣金率
            cashback_rate = 0.50    # 50%返给用户
            cashback = int(price_int * commission_rate * cashback_rate)
            
            # 计算门市价（假设预订价是门市价的85%）
            market_price = int(price_int / 0.85)
            
            hotels.append({
                'name': name,
                'price': price_int,
                'market_price': market_price,
                'rating': rating,
                'location': location,
                'features': features,
                'reason': reason,
                'cashback': cashback,
                'city': city
            })
        
        return hotels
    
    def render_hotel_card(self, hotel: dict) -> str:
        """
        渲染酒店预订卡片
        
        Args:
            hotel: 酒店信息字典
        
        Returns:
            HTML字符串
        """
        # 生成美团搜索链接
        search_query = f"{hotel['city']} {hotel['name']}"
        meituan_url = f"https://i.meituan.com/search?q={quote(search_query)}"
        
        return f'''
<div class="hotel-booking-card" style="background: linear-gradient(135deg, #FFF5E6 0%, #FFE8CC 100%); border: 2px solid #FB923C; border-radius: 16px; padding: 24px; margin: 20px 0; box-shadow: 0 4px 16px rgba(251, 146, 60, 0.25);">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
        <div>
            <h3 style="font-size: 20px; font-weight: 700; color: #1f2937; margin: 0 0 8px 0;">
                🏨 {hotel['name']}
            </h3>
            <p style="color: #6b7280; font-size: 14px; margin: 0 0 8px 0;">
                📍 {hotel['location']}
            </p>
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                <span style="color: #F59E0B; font-size: 14px;">⭐ {hotel['rating']}</span>
                <span style="color: #9ca3af; font-size: 16px; text-decoration: line-through;">¥{hotel['market_price']}/晚</span>
                <span style="color: #DC2626; font-weight: 700; font-size: 24px;">¥{hotel['price']}/晚</span>
            </div>
        </div>
        <div style="background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); color: white; padding: 8px 16px; border-radius: 20px; font-size: 16px; font-weight: 700; box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);">
            返¥{hotel['cashback']}
        </div>
    </div>
    
    <p style="color: #4b5563; font-size: 14px; margin: 0 0 16px 0; line-height: 1.6;">
        ✨ {hotel['features']}
    </p>
    
    <a href="{meituan_url}" target="_blank" rel="noopener" style="display: block; width: 100%; padding: 16px; background: linear-gradient(90deg, #10B981 0%, #059669 100%); color: white; text-align: center; text-decoration: none; border-radius: 12px; font-size: 18px; font-weight: 700; border: none; cursor: pointer; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); margin-bottom: 12px;">
        💰 美团预订，返现¥{hotel['cashback']}
    </a>
    
    <div style="display: flex; justify-content: space-around; padding-top: 12px; border-top: 1px dashed #FB923C;">
        <span style="color: #6b7280; font-size: 13px;">✅ 免费取消</span>
        <span style="color: #6b7280; font-size: 13px;">💳 到店付款</span>
        <span style="color: #6b7280; font-size: 13px;">⚡ 返现秒到</span>
    </div>
</div>
'''



# 单例
_generator = None

def get_itinerary_generator():
    global _generator
    if _generator is None:
        _generator = ItineraryGenerator()
    return _generator

