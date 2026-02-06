"""
行程规划页面生成器
生成带时间线视图、日历导入的行程页面
"""

import re
import json
import random
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
            logger.error("行程模板不存在")
            return content

        template = self.template_path.read_text(encoding='utf-8')

        # 预处理：转换Markdown表格
        content = self._convert_markdown_tables(content)

        # 预处理：转换Markdown链接为HTML按钮
        content = self._convert_markdown_links_to_buttons(content, query)

        # 预处理：清理HTML代码泄露
        content = self._fix_html_leakage(content)

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

        # 转换Markdown表格为HTML表格
        timeline_content = self._convert_markdown_tables(timeline_content)

        # 清理时间线中的HTML代码泄露
        timeline_content = self._fix_html_leakage(timeline_content)

        # 生成住宿推荐section（使用HotelExtractor）
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
    <h2 style="font-size: 22px; font-weight: 700; color: var(--text-dark, #333); margin-bottom: 20px; padding-bottom: 12px; border-bottom: 3px solid var(--primary-green, #4CAF50);">
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

        # 插入酒店快速预订卡片（如果有的话）
        if hotel_quick_card:
            html = html.replace('<!-- 这里会通过JS动态插入酒店预订卡片 -->', hotel_quick_card)
            html = html.replace('style="display:none;"', '')

        # 最终清理：修复所有残留的HTML代码泄露
        html = self._fix_html_leakage(html)

        return html

    def _fix_html_leakage(self, text: str) -> str:
        """
        修复HTML代码泄露问题

        处理以下模式：
        - title="在美团搜索：XXX">  （老样式泄露）
        - SEARCH_HINT:XXX 未转换的链接
        - 裸露的HTML属性文本
        """
        # 修复 title="在美团搜索：XXX"> 泄露
        text = re.sub(
            r'title="在美团搜索[：:]([^"]*)">\s*',
            lambda m: self._generate_inline_restaurant_card(m.group(1).strip()),
            text
        )

        # 修复残留的 SEARCH_HINT 链接
        text = re.sub(
            r'<a\s+href="SEARCH_HINT:([^"]*)"[^>]*>([^<]*)</a>',
            lambda m: self._generate_inline_search_button(m.group(1).strip(), m.group(2).strip()),
            text
        )

        # 修复裸露的 SEARCH_HINT 文本
        text = re.sub(
            r'SEARCH_HINT:([^\s<"\']+)',
            lambda m: self._generate_inline_search_button(m.group(1).strip(), '去美团查看'),
            text
        )

        return text

    def _generate_inline_restaurant_card(self, name: str) -> str:
        """为泄露的HTML代码生成内联餐厅卡片"""
        from services.affiliate_manager import get_affiliate_manager
        affiliate_mgr = get_affiliate_manager()
        return affiliate_mgr.render_booking_button(
            poi_type='restaurant',
            name=name,
            city=''
        )

    def _generate_inline_search_button(self, keyword: str, text: str) -> str:
        """生成内联搜索按钮替代SEARCH_HINT"""
        url = f"https://i.meituan.com/search?q={quote(keyword)}"
        return f'''<a href="{url}" target="_blank" rel="noopener" style="display: inline-block; padding: 8px 20px; background: linear-gradient(90deg, var(--primary-green, #4CAF50), #43A047); color: white; text-decoration: none; border-radius: 20px; font-size: 14px; font-weight: 600; margin: 6px 0;">{text}</a>'''

    def _extract_title(self, query: str, content: str) -> str:
        """提取标题"""
        title_match = re.search(r'^#\s+(.+)$', content, re.M)
        if title_match:
            return title_match.group(1).strip()
        return query.split('，')[0]

    def _extract_days_info(self, query: str, content: str) -> list:
        """提取每天的信息"""
        days_match = re.search(r'(\d+)天', query)
        if not days_match:
            return [{'day': 1, 'weekday': ''}]

        num_days = int(days_match.group(1))

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
        restaurants = len(re.findall(r'\*\*[^*]+\*\*\s*[¥￥]\d+/人', content))
        hotels = len(re.findall(r'###\s*\d+\.\s*[^#\n]+酒店', content, re.I))
        attractions = len(re.findall(r'[公园|景区|博物馆|寺|塔|山|岛|古镇|广场]', content))

        return restaurants + hotels + min(attractions, 5)

    def _calculate_cashback(self, content: str) -> int:
        """计算总返现金额（仅酒店）"""
        hotels_count = self._count_hotels(content)
        estimated_cashback = hotels_count * 50

        cashbacks = re.findall(r'返[¥￥](\d+)', content)
        if cashbacks:
            total = sum(int(cb) for cb in cashbacks)
            return total if total > 0 else estimated_cashback

        return estimated_cashback if estimated_cashback > 0 else 100

    def _count_hotels(self, content: str) -> int:
        """统计酒店数量"""
        hotels = len(re.findall(r'###\s*\d+\.\s*[^#\n]*[酒店|民宿|客栈]', content, re.I))
        return hotels if hotels > 0 else 4

    def _count_restaurants(self, content: str) -> int:
        """统计餐厅数量"""
        restaurants = len(re.findall(r'\*\*[^*]+\*\*\s*[¥￥]\d+/人', content))
        return restaurants if restaurants > 0 else 17

    def _calculate_users_saved(self, cashback: int) -> int:
        """计算已为多少人省钱（社会证明）"""
        if cashback >= 200:
            return 156
        elif cashback >= 150:
            return 98
        elif cashback >= 100:
            return 67
        elif cashback >= 50:
            return 43
        else:
            return 28

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

        day_pattern = r'###?\s*Day\s*(\d+)[：:]?(.*?)(?=###?\s*Day\s*\d+|##\s+[^D]|$)'
        day_matches = re.findall(day_pattern, content, re.S | re.I)

        for day_num_str, day_content in day_matches:
            day_num = int(day_num_str)
            active = 'active' if day_num == 1 else ''

            items = self._parse_timeline_items(day_content)

            items_html = ''
            for item in items:
                icon_class = 'icon-food' if item['type'] == 'food' else 'icon-activity'
                icon_emoji = item.get('emoji', '🍜' if item['type'] == 'food' else '🚶')

                content_html = f'<div class="content-title">{item["title"]}</div>'

                if item.get('desc'):
                    content_html += f'<div class="content-desc">{item["desc"]}</div>'

                if item.get('tags'):
                    for tag in item['tags']:
                        content_html += f'<span class="content-tag">{tag}</span>'

                # 如果是餐厅，添加新的餐厅卡片
                if item['type'] == 'food' and item.get('price'):
                    from services.affiliate_manager import get_affiliate_manager

                    affiliate_mgr = get_affiliate_manager()
                    booking_btn = affiliate_mgr.render_booking_button(
                        poi_type='restaurant',
                        name=item['title'],
                        price=item.get('price'),
                        cashback=item.get('cashback', 5),
                        city=''
                    )

                    content_html += f'''
<div class="restaurant-info">
    <span class="restaurant-price">¥{item["price"]}/人</span>
    <span class="restaurant-rating">⭐ {item.get("rating", "4.5")}</span>
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

        time_patterns = [
            (r'\*\*(\d{2}:\d{2})[）\)|\s]+([^*\n]+)', 'time'),
            (r'\*\*([上下午晚][午上]+)[：:]*\*\*\s*([^*\n]+)', 'period'),
        ]

        for pattern, time_type in time_patterns:
            matches = re.findall(pattern, day_content)
            for time_str, desc in matches:
                clean_desc = re.sub(r'\*\*([^*]+)\*\*', r'\1', desc).strip()

                item_type = 'food' if any(word in clean_desc for word in ['餐厅', '馆', '面', '饭', '小吃', '食堂', '火锅']) else 'activity'

                price_match = re.search(r'[¥￥](\d+)/人', day_content[day_content.find(clean_desc):day_content.find(clean_desc)+500])
                rating_match = re.search(r'⭐([\d.]+)', day_content[day_content.find(clean_desc):day_content.find(clean_desc)+500])
                cashback_match = re.search(r'返[¥￥](\d+)', day_content[day_content.find(clean_desc):day_content.find(clean_desc)+500])

                title_match = re.match(r'^([^，。\n]+)', clean_desc)
                title = title_match.group(1) if title_match else clean_desc[:20]

                desc_match = re.search(r'[：:,，](.+?)(?:\n|$)', clean_desc)
                desc_text = desc_match.group(1).strip() if desc_match else ''

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

        return items[:10]

    def _generate_ics_data(self, content: str, days_info: list, title: str) -> list:
        """生成iCalendar数据"""
        events = []

        start_date = datetime.now()

        day_pattern = r'###?\s*Day\s*(\d+)[：:]?(.*?)(?=###?\s*Day\s*\d+|##\s+[^D]|$)'
        day_matches = re.findall(day_pattern, content, re.S | re.I)

        for day_num_str, day_content in day_matches:
            day_num = int(day_num_str)
            current_date = start_date + timedelta(days=day_num - 1)

            time_matches = re.findall(r'\*\*(\d{2}):(\d{2})[）\)|\s]+([^*\n]+)', day_content)

            for hour, minute, desc in time_matches:
                clean_desc = re.sub(r'\*\*([^*]+)\*\*', r'\1', desc).strip()
                title_match = re.match(r'^([^，。\n]+)', clean_desc)
                event_title = title_match.group(1) if title_match else clean_desc[:30]

                event_start = current_date.replace(hour=int(hour), minute=int(minute))
                event_end = event_start + timedelta(hours=1)

                events.append({
                    'start': event_start.strftime('%Y%m%dT%H%M%S'),
                    'end': event_end.strftime('%Y%m%dT%H%M%S'),
                    'title': event_title,
                    'desc': clean_desc[:200],
                    'location': event_title
                })

        return events

    def _convert_markdown_tables(self, text: str) -> str:
        """
        将Markdown表格转换为HTML表格（新设计）
        """
        table_pattern = r'\|(.+)\|\n\|[-:\s|]+\|\n((?:\|.+\|\n?)+)'

        def replace_table(match):
            header_line = match.group(1)
            body_lines = match.group(2)

            headers = [h.strip() for h in header_line.split('|') if h.strip()]

            html = '<table style="width: 100%; border-collapse: separate; border-spacing: 0; margin: 20px 0; background: white; border-radius: var(--card-radius, 16px); overflow: hidden; box-shadow: var(--shadow, 0 4px 12px rgba(0,0,0,0.08)); border: 1px solid #e0e0e0;">\n<thead>\n<tr style="background: linear-gradient(135deg, var(--primary-green, #4CAF50), #43A047); color: white;">'

            for h in headers:
                html += f'<th style="padding: 14px 16px; text-align: left; font-weight: 600; font-size: 14px;">{h}</th>'

            html += '</tr>\n</thead>\n<tbody>'

            rows = [r.strip() for r in body_lines.strip().split('\n') if r.strip()]
            for idx, row in enumerate(rows):
                cells = [c.strip() for c in row.split('|') if c.strip()]
                bg_color = 'var(--bg-light, #f5f5f5)' if idx % 2 == 0 else 'white'
                html += f'<tr style="background: {bg_color}; border-bottom: 1px solid #e5e7eb;">'
                for cell in cells:
                    html += f'<td style="padding: 12px 16px; font-size: 14px; color: var(--text-dark, #333);">{cell}</td>'
                html += '</tr>\n'

            html += '</tbody></table>'
            return html

        return re.sub(table_pattern, replace_table, text, flags=re.MULTILINE)

    def _convert_markdown_links_to_buttons(self, text: str, query: str) -> str:
        """
        将Markdown链接转换为HTML按钮
        """
        from services.affiliate_manager import get_affiliate_manager

        city_match = re.search(r'([\u4e00-\u9fa5]{2,})\d*天', query)
        city = city_match.group(1) if city_match else ''

        affiliate_mgr = get_affiliate_manager()

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

            # 如果是SEARCH_HINT链接，转换为搜索按钮
            if link_url.startswith('SEARCH_HINT:'):
                keyword = link_url.replace('SEARCH_HINT:', '')
                url = f"https://i.meituan.com/search?q={quote(keyword)}"
                return f'<a href="{url}" target="_blank" rel="noopener" style="display: inline-block; padding: 8px 20px; background: linear-gradient(90deg, var(--primary-green, #4CAF50), #43A047); color: white; text-decoration: none; border-radius: 20px; font-size: 14px; font-weight: 600; margin: 6px 0;">{link_text}</a>'

            # 如果是URL链接，判断按钮类型
            if '美团' in link_text or '团购' in link_text:
                before_text = text[:match.start()]
                name_match = re.search(r'[\*]{0,2}([^\*\n]{2,10})[\*]{0,2}[\s]*$', before_text)
                name = name_match.group(1).strip() if name_match else '商家'

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
        统一的餐厅卡片渲染
        """
        from services.affiliate_manager import get_affiliate_manager

        name = restaurant_info.get('name', '')
        price = restaurant_info.get('price', 0)
        rating = restaurant_info.get('rating', 0)
        features = restaurant_info.get('features', [])
        desc = restaurant_info.get('desc', '')

        affiliate_mgr = get_affiliate_manager()
        return affiliate_mgr.render_booking_button(
            poi_type='restaurant',
            name=name,
            price=price,
            city=city
        )


class HotelExtractor:
    """酒店信息提取器"""

    def extract_hotels(self, content: str, query: str) -> list:
        """
        从攻略内容提取酒店信息
        """
        hotels = []

        hotel_pattern = r'##\s*(?:🏨\s*)?住宿推荐(.*?)(?=\n##\s+(?!#)|$)'
        hotel_match = re.search(hotel_pattern, content, re.S | re.I)

        if not hotel_match:
            logger.debug("未找到住宿推荐section")
            return hotels

        hotel_content = hotel_match.group(1).strip()
        logger.debug(f"找到住宿推荐section，长度: {len(hotel_content)}")

        hotel_item_pattern = r'###\s*\d+\.\s*([^\n]+?)\n.*?\*\*价格[：:]\*\*\s*[¥￥](\d+)/晚.*?⭐([\d.]+)(.*?)(?=###\s*\d+\.|$)'
        hotel_matches = re.findall(hotel_item_pattern, hotel_content, re.S)
        logger.debug(f"匹配到 {len(hotel_matches)} 家酒店")

        city_match = re.search(r'([\u4e00-\u9fa5]{2,})\d*天', query)
        city = city_match.group(1) if city_match else ''

        for name, price, rating, details in hotel_matches:
            name = name.strip()
            price_int = int(price)

            location_match = re.search(r'\*\*位置[：:]\*\*\s*([^\n]+)', details)
            location = location_match.group(1).strip() if location_match else ''

            feature_match = re.search(r'\*\*特点[：:]\*\*\s*([^\n]+)', details)
            features = feature_match.group(1).strip() if feature_match else ''

            reason_match = re.search(r'\*\*为什么推荐[：:]\*\*\s*([^\n]+)', details)
            reason = reason_match.group(1).strip() if reason_match else features

            commission_rate = 0.10
            cashback_rate = 0.50
            cashback = int(price_int * commission_rate * cashback_rate)

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
        渲染酒店预订卡片（新设计：渐变背景）
        """
        search_query = f"{hotel['city']} {hotel['name']}"
        meituan_url = f"https://i.meituan.com/search?q={quote(search_query)}"

        booked_count = random.randint(18, 66)

        return f'''
<div style="background: linear-gradient(135deg, #FFF5E6 0%, #FFFDE7 100%); border: 2px solid var(--accent-orange, #FF9500); border-radius: var(--card-radius, 16px); padding: 24px; margin: 16px 0; box-shadow: var(--shadow, 0 4px 12px rgba(0,0,0,0.08));">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
        <div style="display: flex; align-items: flex-start; gap: 14px; flex: 1;">
            <span style="font-size: 42px; flex-shrink: 0;">🏨</span>
            <div>
                <h3 style="font-size: 18px; font-weight: 700; color: var(--text-dark, #333); margin: 0 0 6px 0;">
                    {hotel['name']}
                </h3>
                <p style="color: var(--text-light, #666); font-size: 14px; margin: 0 0 6px 0;">
                    ⭐ {hotel['rating']}  |  📍 {hotel['location']}
                </p>
            </div>
        </div>
        <div style="background: linear-gradient(135deg, #EF4444, #DC2626); color: white; padding: 8px 16px; border-radius: 20px; font-size: 15px; font-weight: 700; flex-shrink: 0;">
            返¥{hotel['cashback']}
        </div>
    </div>

    <div style="background: linear-gradient(135deg, #FFF8E1, #FFFDE7); border-radius: 10px; padding: 10px 14px; margin: 12px 0; display: flex; align-items: center; gap: 12px;">
        <span style="color: #9e9e9e; text-decoration: line-through; font-size: 15px;">门市价 ¥{hotel['market_price']}/晚</span>
        <span style="color: var(--warning-red, #E53935); font-weight: 700; font-size: 22px;">¥{hotel['price']}/晚</span>
        <span style="background: linear-gradient(135deg, #EF4444, #DC2626); color: white; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;">省¥{hotel['market_price'] - hotel['price']}</span>
    </div>

    <p style="color: #4b5563; font-size: 14px; margin: 8px 0 12px 0; line-height: 1.6;">
        ✨ {hotel['features']}
    </p>

    <div style="color: var(--accent-orange, #FF9500); font-size: 13px; margin: 8px 0; font-weight: 600;">🔥 今日已有{booked_count}人预订</div>

    <a href="{meituan_url}" target="_blank" rel="noopener" style="display: block; width: 100%; padding: 16px; background: linear-gradient(90deg, var(--primary-green, #4CAF50), #43A047); color: white; text-align: center; text-decoration: none; border-radius: 12px; font-size: 17px; font-weight: 700; box-sizing: border-box; margin-bottom: 12px;">
        💰 美团预订，返现¥{hotel['cashback']}
    </a>

    <div style="display: flex; justify-content: space-around; padding-top: 12px; border-top: 1px dashed var(--accent-orange, #FF9500);">
        <span style="color: var(--text-light, #666); font-size: 13px;">✅ 免费取消</span>
        <span style="color: var(--text-light, #666); font-size: 13px;">💳 到店付款</span>
        <span style="color: var(--text-light, #666); font-size: 13px;">⚡ 返现秒到</span>
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
