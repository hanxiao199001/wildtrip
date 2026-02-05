"""
现代简洁HTML生成器
按照马来西亚攻略的设计风格生成HTML
"""

import re
from pathlib import Path
from loguru import logger


class CleanHTMLGenerator:
    """简洁HTML生成器"""
    
    def __init__(self):
        self.template_path = Path(__file__).parent.parent.parent / 'web' / 'clean-guide-template.html'
    
    def generate(self, query: str, content: str, stats: dict) -> str:
        """
        生成简洁HTML
        
        Args:
            query: 用户查询
            content: Markdown内容
            stats: 统计信息
        
        Returns:
            完整HTML
        """
        if not self.template_path.exists():
            logger.error("❌ 简洁模板不存在")
            return content
        
        template = self.template_path.read_text(encoding='utf-8')
        
        # 提取导航标题
        nav_title = query.split('，')[0].split('预算')[0]
        
        # 转换内容
        html_content = self._convert_content(content)
        
        # 替换占位符
        html = template.replace('{{TITLE}}', query)
        html = html.replace('{{NAV_TITLE}}', nav_title)
        html = html.replace('{{CONTENT}}', html_content)
        
        return html
    
    def _convert_content(self, content: str) -> str:
        """
        转换Markdown为HTML
        
        重点：
        - 提取Day结构
        - 解析时间线（上午/下午/傍晚）
        - 生成信息卡片
        - 保留预订链接
        """
        sections_html = ''
        
        # 1. 提取并生成"行程概览"信息卡片
        overview_html = self._extract_overview(content)
        if overview_html:
            sections_html += f'<div class="section-title">行程规划与路线安排</div>{overview_html}'
        
        # 2. 提取并生成Day卡片
        days_html = self._extract_days(content)
        if days_html:
            sections_html += '<div class="section-title">详细行程安排</div>' + days_html
        
        # 3. 提取并生成其他section（住宿、费用等）
        other_sections = self._extract_other_sections(content)
        sections_html += other_sections
        
        return sections_html
    
    def _extract_overview(self, content: str) -> str:
        """提取行程概览信息"""
        # 查找"行程概览"或"📋 行程概览"部分
        overview_match = re.search(r'##\s*(?:📋\s*)?行程概览(.*?)(?=##|$)', content, re.S)
        if not overview_match:
            return ''
        
        overview_text = overview_match.group(1).strip()
        
        # 提取关键信息
        days_match = re.search(r'天数[：:]\s*(.+)', overview_text)
        budget_match = re.search(r'预算[：:]\s*(.+)', overview_text)
        audience_match = re.search(r'适合人群[：:]\s*(.+)', overview_text)
        
        info_items = []
        if days_match:
            info_items.append(f'<div class="info-item"><span class="info-icon">📅</span><div>总时长：{days_match.group(1).strip()}</div></div>')
        
        if budget_match:
            info_items.append(f'<div class="info-item"><span class="info-icon">💰</span><div>预算：{budget_match.group(1).strip()}</div></div>')
        
        if audience_match:
            info_items.append(f'<div class="info-item"><span class="info-icon">👥</span><div>适合：{audience_match.group(1).strip()}</div></div>')
        
        if not info_items:
            return ''
        
        return f'''
<div class="info-card">
    <h3>整体时间安排</h3>
    {''.join(info_items)}
</div>
'''
    
    def _extract_days(self, content: str) -> str:
        """提取Day结构"""
        days_html = ''
        
        # 查找所有"### Day X"或"## Day X"
        day_pattern = r'###?\s*Day\s*(\d+)[：:]?(.*?)(?=###?\s*Day\s*\d+|##\s+[^D]|$)'
        day_matches = re.findall(day_pattern, content, re.S | re.I)
        
        for day_num, day_content in day_matches:
            day_title = self._extract_day_title(day_content)
            timeline_items = self._extract_timeline(day_content)
            
            if not timeline_items:
                continue
            
            timeline_html = ''.join([
                f'<div class="timeline-item"><div class="timeline-time">{time}</div><div class="timeline-content">{desc}</div></div>'
                for time, desc in timeline_items
            ])
            
            days_html += f'''
<div class="day-card">
    <div class="day-header">
        <div class="day-badge">{day_num}</div>
        <div class="day-title">Day {day_num}{day_title}</div>
    </div>
    {timeline_html}
</div>
'''
        
        return days_html
    
    def _extract_day_title(self, day_content: str) -> str:
        """提取Day的副标题"""
        # 查找第一行作为标题
        first_line = day_content.strip().split('\n')[0].strip()
        # 移除"Day X"部分
        title = re.sub(r'^Day\s*\d+[：:]?', '', first_line, flags=re.I).strip()
        if title and len(title) < 50:
            return f'：{title}'
        return ''
    
    def _extract_timeline(self, day_content: str) -> list:
        """提取时间线（上午/下午/傍晚/晚上）"""
        timeline = []
        
        # 查找时间标记
        time_patterns = [
            (r'\*\*(\d{2}:\d{2})[）\)|\s]+([^*\n]+)', None),  # **12:00** xxx
            (r'\*\*([上下午晚][午上]+)[：:]*\*\*\s*([^*\n]+)', None),  # **上午** xxx
            (r'[^\*]([上下午晚][午上]+)[：:]\s*([^*\n]+)', None),  # 上午：xxx（无加粗）
        ]
        
        for pattern, _ in time_patterns:
            matches = re.findall(pattern, day_content)
            for time_str, desc in matches:
                # 清理描述（移除Markdown标记）
                clean_desc = self._clean_markdown(desc.strip())
                # 提取预订链接并转换
                clean_desc = self._convert_booking_links(clean_desc)
                
                if clean_desc:
                    timeline.append((time_str, clean_desc))
        
        # 如果没有找到时间标记，尝试段落分割
        if not timeline:
            paragraphs = day_content.strip().split('\n\n')
            for i, para in enumerate(paragraphs[:5]):  # 最多5段
                if para.strip() and len(para) > 20:
                    clean_para = self._clean_markdown(para.strip())
                    clean_para = self._convert_booking_links(clean_para)
                    if i == 0:
                        timeline.append(('上午', clean_para))
                    elif i == 1:
                        timeline.append(('下午', clean_para))
                    elif i == 2:
                        timeline.append(('傍晚', clean_para))
        
        return timeline[:5]  # 最多5个时间点
    
    def _clean_markdown(self, text: str) -> str:
        """清理Markdown标记"""
        # 移除图片
        text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', text)
        # 移除加粗
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        # 移除列表标记
        text = re.sub(r'^\s*[-*]\s+', '', text, flags=re.M)
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _convert_booking_links(self, text: str) -> str:
        """转换预订链接为HTML"""
        # 查找SEARCH_HINT链接
        def replace_link(match):
            link_text = match.group(1)
            keyword = match.group(2)
            url = f"https://i.meituan.com/search?q={keyword}"
            return f'<a href="{url}" class="booking-link" target="_blank">{link_text}</a>'
        
        text = re.sub(r'\[([^\]]+)\]\(SEARCH_HINT:([^)]+)\)', replace_link, text)
        return text
    
    def _extract_other_sections(self, content: str) -> str:
        """提取其他section（住宿、费用、Tips等）"""
        sections_html = ''
        
        # 查找所有## 标题（但排除Day相关）
        section_pattern = r'##\s+([^#\n]+)(.*?)(?=##|$)'
        section_matches = re.findall(section_pattern, content, re.S)
        
        for title, section_content in section_matches:
            title = title.strip()
            
            # 跳过Day和行程概览
            if 'day' in title.lower() or '行程概览' in title or '详细行程' in title:
                continue
            
            # 清理内容
            clean_content = self._clean_markdown(section_content.strip())
            clean_content = self._convert_booking_links(clean_content)
            
            if len(clean_content) < 50:  # 太短跳过
                continue
            
            # 简单转换为HTML段落
            paragraphs = clean_content.split('\n')
            content_html = ''.join([f'<div class="info-item"><div>{p}</div></div>' for p in paragraphs if p.strip()])
            
            if content_html:
                sections_html += f'''
<div class="info-card">
    <h3>{title}</h3>
    {content_html}
</div>
'''
        
        return sections_html


# 单例
_generator = None

def get_clean_html_generator():
    global _generator
    if _generator is None:
        _generator = CleanHTMLGenerator()
    return _generator
