"""
内容转换器
将原始Markdown内容转换为带样式的HTML组件
"""

import re
from urllib.parse import quote
from services.ui_fix_complete import (
    render_overview_card,
    render_day_header,
    render_timeline_item,
    render_restaurant_card,
    render_hotel_card,
    render_cashback_banner
)


class ContentTransformer:
    """Markdown到HTML组件的转换器"""
    
    def __init__(self, city: str = ''):
        self.city = city
        
    def transform(self, raw_content: str) -> str:
        """
        将原始Markdown内容转换为样式化HTML
        
        Args:
            raw_content: Markdown格式的攻略内容
            
        Returns:
            HTML格式的样式化内容
        """
        html_parts = []
        
        # 1. 提取并渲染概览信息
        title = self._extract_title(raw_content)
        days = self._extract_days(raw_content)
        budget = self._extract_budget(raw_content)
        highlights = self._extract_highlights(raw_content)
        
        if highlights:
            html_parts.append(render_overview_card(title, days, budget, highlights[:5]))
        
        # 2. 计算并添加返现横幅
        total_cashback = self._calculate_total_cashback(raw_content)
        if total_cashback > 0:
            html_parts.append(render_cashback_banner(total_cashback))
        
        # 3. 按天处理内容
        day_sections = self._split_by_days(raw_content)
        
        for day_num, day_content in day_sections:
            # 提取当天主题
            theme = self._extract_day_theme(day_content) or f"第{day_num}天行程"
            
            # 渲染Day标题
            html_parts.append(render_day_header(day_num, theme))
            
            # 提取时间线项目
            timeline_items = self._parse_timeline_items(day_content)
            
            for item in timeline_items:
                # 基础时间线渲染
                timeline_html = render_timeline_item(
                    time=item['time'],
                    icon=item['icon'],
                    name=item['name'],
                    description=item['description'],
                    tips=item.get('tips'),
                    duration=item.get('duration')
                )
                html_parts.append(timeline_html)
                
                # 如果是餐厅，添加餐厅卡片
                if item['type'] == 'restaurant':
                    restaurant_card = render_restaurant_card(
                        name=item['name'],
                        price=item.get('price', 50),
                        rating=item.get('rating', 4.5),
                        dishes=item.get('dishes', ''),
                        city=self.city
                    )
                    html_parts.append(restaurant_card)
                
                # 如果是酒店，添加酒店卡片
                elif item['type'] == 'hotel':
                    hotel_card = render_hotel_card(
                        name=item['name'],
                        price=item.get('price', 300),
                        rating=item.get('rating', 4.5),
                        location=item.get('location', self.city),
                        features=item.get('features', []),
                        city=self.city
                    )
                    html_parts.append(hotel_card)
        
        # 4. 处理住宿推荐章节
        hotel_section_html = self._extract_hotel_section(raw_content)
        if hotel_section_html:
            html_parts.append(hotel_section_html)
        
        # 5. 处理其他章节（费用明细、注意事项等）
        other_sections = self._extract_other_sections(raw_content)
        html_parts.extend(other_sections)
        
        return '\n\n'.join(html_parts)
    
    def _extract_title(self, content: str) -> str:
        """提取标题"""
        title_match = re.search(r'^#\s*(.+?)$', content, re.M)
        return title_match.group(1).strip() if title_match else f"{self.city}旅游攻略"
    
    def _extract_days(self, content: str) -> int:
        """提取天数"""
        days_match = re.search(r'(\d+)\s*[天日]', content)
        return int(days_match.group(1)) if days_match else 2
    
    def _extract_budget(self, content: str) -> int:
        """提取预算"""
        budget_match = re.search(r'[预预算¥￥]\s*(\d+)', content)
        return int(budget_match.group(1)) if budget_match else 1000
    
    def _extract_highlights(self, content: str) -> list:
        """提取核心亮点"""
        highlights = []
        
        # 尝试多种模式
        patterns = [
            r'✨\s*(.+?)(?:\n|$)',
            r'[核核]心亮点[：:]\s*(.+?)(?:\n|$)',
            r'特色[：:]\s*(.+?)(?:\n|$)',
            r'亮点[：:]\s*(.+?)(?:\n|$)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.M)
            highlights.extend([m.strip() for m in matches if m.strip()])
        
        # 去重
        seen = set()
        unique_highlights = []
        for h in highlights:
            if h not in seen:
                seen.add(h)
                unique_highlights.append(h)
        
        return unique_highlights
    
    def _calculate_total_cashback(self, content: str) -> int:
        """计算总返现金额"""
        # 提取所有返现金额
        cashbacks = re.findall(r'返[¥￥](\d+)', content)
        if cashbacks:
            return sum(int(cb) for cb in cashbacks)
        
        # 如果没有明确金额，估算
        hotel_count = len(re.findall(r'酒店|民宿', content))
        restaurant_count = len(re.findall(r'餐厅|美食|吃', content))
        
        estimated = hotel_count * 20 + restaurant_count * 5
        return max(estimated, 50)  # 至少50元
    
    def _split_by_days(self, content: str) -> list:
        """按天分割内容"""
        day_pattern = r'###?\s*Day\s*(\d+)[：:]?(.*?)(?=###?\s*Day\s*\d+|##\s+[^D]|$)'
        day_matches = re.findall(day_pattern, content, re.S | re.I)
        
        return [(int(num), content_text) for num, content_text in day_matches]
    
    def _extract_day_theme(self, day_content: str) -> str:
        """提取当天主题"""
        # 尝试提取主题
        theme_patterns = [
            r'主题[：:]\s*\*?\*?(.+?)\*?\*?(?:\n|$)',
            r'^\s*\*?\*?([^：:\n]+?)\*?\*?$'
        ]
        
        for pattern in theme_patterns:
            match = re.search(pattern, day_content, re.M)
            if match:
                theme = match.group(1).strip()
                if theme and len(theme) < 50:  # 避免提取过长的文本
                    return theme
        
        return ''
    
    def _parse_timeline_items(self, day_content: str) -> list:
        """解析时间线项目"""
        items = []
        
        # 匹配时间点（09:00、9:00等格式）
        time_pattern = r'(\d{1,2}[：:]\d{2})[^】\n]*?[】\[]?([^】\[\n]+)[】\]]?(.*?)(?=\n\d{1,2}[：:]|\n##|\n\*\*|$)'
        time_matches = re.findall(time_pattern, day_content, re.S)
        
        for time_str, name, after_text in time_matches:
            # 清理名称
            name = name.strip()
            if not name:
                continue
            
            # 判断类型
            item_type = self._identify_type(name, after_text)
            
            # 提取图标
            icon = self._get_icon_for_type(item_type)
            
            # 提取描述
            description = self._extract_description(after_text)
            
            # 提取Tips
            tips = self._extract_tips(after_text)
            
            # 提取时长
            duration = self._extract_duration(after_text)
            
            # 提取价格（餐厅/酒店）
            price = self._extract_price(after_text) if item_type in ['restaurant', 'hotel'] else None
            
            # 提取评分
            rating = self._extract_rating(after_text)
            
            # 提取特色/菜品
            dishes_or_features = self._extract_features(after_text)
            
            item = {
                'time': time_str,
                'name': name,
                'description': description,
                'type': item_type,
                'icon': icon,
                'tips': tips,
                'duration': duration,
                'price': price,
                'rating': rating
            }
            
            if item_type == 'restaurant':
                item['dishes'] = dishes_or_features
            elif item_type == 'hotel':
                item['features'] = dishes_or_features.split('、') if dishes_or_features else []
                item['location'] = description[:30] if description else self.city
            
            items.append(item)
        
        return items
    
    def _identify_type(self, name: str, context: str) -> str:
        """识别项目类型"""
        text = name + context[:100]
        
        if any(k in text for k in ['早餐', '午餐', '晚餐', '小吃', '美食', '餐厅', '面馆', '火锅', '菜']):
            return 'restaurant'
        elif any(k in text for k in ['酒店', '住宿', '民宿', '入住', '客栈']):
            return 'hotel'
        elif any(k in text for k in ['景区', '公园', '博物馆', '古镇', '寺庙', '塔', '山', '岛']):
            return 'attraction'
        elif any(k in text for k in ['咖啡', '茶馆', '下午茶']):
            return 'cafe'
        else:
            return 'activity'
    
    def _get_icon_for_type(self, item_type: str) -> str:
        """根据类型获取图标"""
        icon_map = {
            'restaurant': '🍜',
            'hotel': '🏨',
            'attraction': '🏔️',
            'cafe': '☕',
            'activity': '🚶'
        }
        return icon_map.get(item_type, '🚶')
    
    def _extract_description(self, text: str) -> str:
        """提取描述"""
        # 清理格式符号
        text = re.sub(r'\*\*', '', text)
        text = re.sub(r'[【】\[\]]', '', text)
        
        # 提取第一句话或前100字符
        sentences = re.split(r'[。！？\n]', text)
        if sentences:
            desc = sentences[0].strip()
            return desc[:100] if desc else ''
        
        return text[:100].strip()
    
    def _extract_tips(self, text: str) -> str:
        """提取Tips"""
        tips_match = re.search(r'[Tt]ip[s]?[：:]\s*(.+?)(?:\n|$)', text)
        return tips_match.group(1).strip() if tips_match else None
    
    def _extract_duration(self, text: str) -> str:
        """提取时长"""
        duration_match = re.search(r'(\d+\.?\d*)\s*小时', text)
        return f"{duration_match.group(1)}小时" if duration_match else None
    
    def _extract_price(self, text: str) -> int:
        """提取价格"""
        price_match = re.search(r'[¥￥](\d+)', text)
        return int(price_match.group(1)) if price_match else None
    
    def _extract_rating(self, text: str) -> float:
        """提取评分"""
        rating_match = re.search(r'[⭐★](\d+\.?\d*)', text)
        return float(rating_match.group(1)) if rating_match else 4.5
    
    def _extract_features(self, text: str) -> str:
        """提取特色/菜品"""
        # 寻找推荐、特色等关键词后的内容
        features_patterns = [
            r'推荐[：:]\s*(.+?)(?:\n|$)',
            r'特色[：:]\s*(.+?)(?:\n|$)',
            r'必点[：:]\s*(.+?)(?:\n|$)'
        ]
        
        for pattern in features_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return ''
    
    def _extract_hotel_section(self, content: str) -> str:
        """提取住宿推荐章节"""
        hotel_pattern = r'##\s*🏨?\s*住宿推荐(.*?)(?=##|\Z)'
        match = re.search(hotel_pattern, content, re.S | re.I)
        
        if not match:
            return ''
        
        hotel_section = match.group(1)
        html_parts = ['<div class="section-title">🏨 住宿推荐</div>']
        
        # 提取各个酒店块
        hotel_blocks = re.split(r'###\s*\d+\.', hotel_section)
        
        for block in hotel_blocks[1:]:  # 跳过第一个空块
            name_match = re.search(r'^\s*(.+?)(?:\n|$)', block)
            if not name_match:
                continue
            
            name = name_match.group(1).strip()
            
            # 提取信息
            price_match = re.search(r'[¥￥](\d+)/晚', block)
            price = int(price_match.group(1)) if price_match else 300
            
            rating_match = re.search(r'[⭐★](\d+\.?\d*)', block)
            rating = float(rating_match.group(1)) if rating_match else 4.5
            
            location_match = re.search(r'位置[：:]\s*\*?\*?(.+?)(?:\n|$)', block)
            location = location_match.group(1).strip() if location_match else self.city
            
            features_match = re.search(r'特点[：:]\s*\*?\*?(.+?)(?:\n|$)', block)
            features_text = features_match.group(1).strip() if features_match else ''
            features = features_text.split('、') if features_text else []
            
            hotel_card = render_hotel_card(name, price, rating, location, features, self.city)
            html_parts.append(hotel_card)
        
        return '\n'.join(html_parts) if len(html_parts) > 1 else ''
    
    def _extract_other_sections(self, content: str) -> list:
        """提取其他章节（费用明细、注意事项等）"""
        html_parts = []
        
        # 费用明细
        cost_pattern = r'##\s*💰?\s*费用[预估预算明细]+(.*?)(?=##|\Z)'
        cost_match = re.search(cost_pattern, content, re.S | re.I)
        if cost_match:
            cost_html = self._render_cost_section(cost_match.group(1))
            if cost_html:
                html_parts.append(cost_html)
        
        # 注意事项 / Tips
        tips_pattern = r'##\s*⚠️?\s*[注注]意事项(.*?)(?=##|\Z)'
        tips_match = re.search(tips_pattern, content, re.S | re.I)
        if tips_match:
            tips_html = self._render_tips_section(tips_match.group(1))
            if tips_html:
                html_parts.append(tips_html)
        
        return html_parts
    
    def _render_cost_section(self, cost_text: str) -> str:
        """渲染费用明细"""
        items = []
        total = 0
        
        for line in cost_text.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # 解析 "项目：¥金额" 或 "| 项目 | 金额 |"
            match = re.search(r'(.+?)[：:]\s*[¥￥](\d+)', line)
            if match:
                label = match.group(1).strip()
                amount = int(match.group(2))
                items.append((label, amount))
                total += amount
        
        if not items:
            return ''
        
        html = '<div class="cost-section"><div class="cost-title">💰 费用预估</div>'
        
        for label, amount in items:
            html += f'<div class="cost-item"><span class="cost-label">{label}</span><span class="cost-value">¥{amount}</span></div>'
        
        html += f'<div class="cost-total"><span class="label">总计</span><span class="value">¥{total}</span></div>'
        html += '</div>'
        
        return html
    
    def _render_tips_section(self, tips_text: str) -> str:
        """渲染注意事项"""
        tips_items = []
        
        for line in tips_text.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            line = re.sub(r'^[-*•]\s*', '', line)
            if line:
                tips_items.append(line)
        
        if not tips_items:
            return ''
        
        html = '<div class="section-title">⚠️ 注意事项</div>'
        for tip in tips_items:
            html += f'<div class="tips-box">{tip}</div>'
        
        return html
