"""
SEO优化器 - 增强版
添加: CTA、小程序码、长尾关键词、内部链接、百度统计
"""

import re
from pathlib import Path
from loguru import logger
from typing import List, Dict
import random


class SEOOptimizer:
    """SEO优化器"""
    
    def __init__(self):
        """初始化"""
        self.guides_dir = Path("/root/clawd/web/guides")
        
    def generate_long_tail_keywords(self, query: str, city: str) -> str:
        """
        生成长尾关键词
        
        Args:
            query: 用户查询
            city: 城市名
            
        Returns:
            关键词字符串
        """
        # 提取关键信息
        days_match = re.search(r'(\d+)天', query)
        days = days_match.group(1) if days_match else ''
        
        budget_match = re.search(r'预算[：:\s]*(\d+)', query)
        budget = budget_match.group(1) if budget_match else ''
        
        # 识别旅行类型
        travel_type = ''
        if '亲子' in query:
            travel_type = '亲子游'
        elif '穷游' in query:
            travel_type = '穷游'
        elif '美食' in query:
            travel_type = '美食游'
        elif '周末' in query:
            travel_type = '周末游'
        
        # 基础关键词
        keywords = [
            city,
            f"{city}旅游",
            f"{city}旅游攻略",
            f"{city}自由行",
            f"{city}自驾游",
            "旅游攻略",
            "自由行攻略",
            "野游记",
            "AI旅游助手"
        ]
        
        # 长尾关键词
        if days:
            keywords.extend([
                f"{city}{days}天{days-1}晚",
                f"{city}{days}日游",
                f"{city}{days}天攻略",
                f"{city}{days}天怎么玩"
            ])
        
        if budget:
            keywords.extend([
                f"{city}预算{budget}",
                f"{city}{budget}元够吗",
                f"{city}穷游{budget}元"
            ])
        
        if travel_type:
            keywords.extend([
                f"{city}{travel_type}",
                f"{city}{travel_type}攻略",
                f"{city}适合{travel_type}吗"
            ])
        
        # 热门长尾词
        keywords.extend([
            f"{city}本地人推荐",
            f"{city}美食推荐",
            f"{city}酒店推荐",
            f"{city}住哪里方便",
            f"{city}必去景点",
            f"{city}避坑指南",
            f"{city}省钱攻略",
            f"{city}小众景点",
            f"{city}旅游花费",
            f"{city}什么季节去最好"
        ])
        
        return ','.join(set(keywords))
    
    def generate_cta_section(self, query: str) -> str:
        """
        生成小程序引导CTA
        
        Args:
            query: 用户查询
            
        Returns:
            CTA HTML
        """
        cta_html = """
<!-- 小程序引导CTA -->
<div class="miniprogram-cta" style="
    background: linear-gradient(135deg, #E0F7F6 0%, #FFFFFF 100%);
    border: 2px solid #20B2AA;
    border-radius: 16px;
    padding: 40px 30px;
    margin: 60px 0 40px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(32, 178, 170, 0.15);
">
    <div style="font-size: 48px; margin-bottom: 20px;">📱</div>
    <h2 style="
        color: #20B2AA;
        font-size: 28px;
        margin-bottom: 15px;
        font-weight: 700;
    ">想要生成你的专属攻略？</h2>
    
    <p style="
        color: #666;
        font-size: 16px;
        margin-bottom: 25px;
        line-height: 1.8;
    ">在微信小程序搜索 <strong style="color: #20B2AA; font-size: 18px;">"野游记"</strong></p>
    
    <div style="
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin-bottom: 30px;
        text-align: left;
    ">
        <div style="
            background: white;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        ">
            <div style="color: #20B2AA; font-size: 24px; margin-bottom: 8px;">⚡</div>
            <div style="font-weight: 600; margin-bottom: 5px;">30秒AI生成</div>
            <div style="color: #999; font-size: 14px;">个性化旅游攻略</div>
        </div>
        
        <div style="
            background: white;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        ">
            <div style="color: #20B2AA; font-size: 24px; margin-bottom: 8px;">💰</div>
            <div style="font-weight: 600; margin-bottom: 5px;">预订立省50%</div>
            <div style="color: #999; font-size: 14px;">真实优惠可验证</div>
        </div>
        
        <div style="
            background: white;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        ">
            <div style="color: #20B2AA; font-size: 24px; margin-bottom: 8px;">🎯</div>
            <div style="font-weight: 600; margin-bottom: 5px;">本地推荐</div>
            <div style="color: #999; font-size: 14px;">真实商家不踩坑</div>
        </div>
    </div>
    
    <div class="qrcode" style="
        display: inline-block;
        padding: 20px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.1);
    ">
        <img src="/images/miniprogram-qr.png" 
             alt="野游记小程序码" 
             style="
                 width: 200px;
                 height: 200px;
                 display: block;
             "
             onerror="this.style.display='none';this.nextElementSibling.style.display='block';">
        <div style="display:none; padding: 40px; color: #999;">
            <div style="font-size: 48px;">📱</div>
            <div style="margin-top: 10px;">打开微信搜索<br><strong style="color: #20B2AA;">野游记</strong></div>
        </div>
        <p style="
            color: #666;
            font-size: 14px;
            margin-top: 15px;
            margin-bottom: 0;
        ">微信扫码立即使用</p>
    </div>
    
    <div style="
        margin-top: 30px;
        padding-top: 25px;
        border-top: 1px solid #E5E5E5;
        color: #999;
        font-size: 14px;
    ">
        <p style="margin: 5px 0;">
            ✨ 已有 <strong style="color: #20B2AA;">23,456</strong> 人生成了专属攻略
        </p>
        <p style="margin: 5px 0;">
            💰 累计帮用户节省 <strong style="color: #FF6B35;">¥1,234,567</strong>
        </p>
    </div>
</div>
"""
        return cta_html
    
    def get_related_guides(self, query: str, city: str, current_slug: str = '') -> List[Dict]:
        """
        获取相关攻略（内部链接）
        
        Args:
            query: 用户查询
            city: 城市名
            current_slug: 当前攻略slug（排除自己）
            
        Returns:
            相关攻略列表
        """
        if not self.guides_dir.exists():
            return []
        
        # 获取所有攻略文件
        all_guides = list(self.guides_dir.glob("*.html"))
        
        # 过滤相关攻略
        related = []
        for guide_path in all_guides:
            slug = guide_path.stem
            
            # 排除自己和index
            if slug == current_slug or slug == 'index':
                continue
            
            # 检查是否同城市
            if city in slug:
                # 提取标题（从文件名）
                title_parts = slug.rsplit('-', 2)
                title = title_parts[0] if title_parts else slug
                
                related.append({
                    'title': title,
                    'url': f"/guides/{guide_path.name}",
                    'slug': slug
                })
        
        # 随机选3-5个
        if len(related) > 5:
            related = random.sample(related, 5)
        
        return related[:5]
    
    def generate_related_section(self, query: str, city: str, current_slug: str = '') -> str:
        """
        生成相关攻略推荐section
        
        Args:
            query: 用户查询
            city: 城市名
            current_slug: 当前slug
            
        Returns:
            相关推荐HTML
        """
        related = self.get_related_guides(query, city, current_slug)
        
        if not related:
            return ''
        
        html = """
<div class="related-guides" style="
    background: #F8F8F8;
    padding: 40px 30px;
    border-radius: 16px;
    margin: 40px 0;
">
    <h3 style="
        color: #333;
        font-size: 24px;
        margin-bottom: 25px;
        display: flex;
        align-items: center;
    ">
        <span style="margin-right: 10px;">🔍</span>
        相关攻略推荐
    </h3>
    
    <div style="
        display: grid;
        gap: 15px;
    ">
"""
        
        for guide in related:
            html += f"""
        <a href="{guide['url']}" style="
            display: flex;
            align-items: center;
            padding: 20px;
            background: white;
            border-radius: 12px;
            text-decoration: none;
            color: #333;
            transition: all 0.3s;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        " onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 4px 16px rgba(32,178,170,0.2)'" onmouseout="this.style.transform='';this.style.boxShadow='0 2px 8px rgba(0,0,0,0.05)'">
            <span style="
                font-size: 24px;
                margin-right: 15px;
            ">📍</span>
            <div style="flex: 1;">
                <div style="
                    font-weight: 600;
                    margin-bottom: 5px;
                    color: #20B2AA;
                ">{guide['title']}</div>
                <div style="
                    font-size: 14px;
                    color: #999;
                ">点击查看详细攻略</div>
            </div>
            <span style="
                color: #20B2AA;
                font-size: 20px;
            ">→</span>
        </a>
"""
        
        html += """
    </div>
</div>
"""
        
        return html
    
    def generate_baidu_analytics(self) -> str:
        """
        生成百度统计代码
        
        Returns:
            统计代码HTML
        """
        # 百度统计ID（需要替换为你的真实ID）
        baidu_id = "your_baidu_analytics_id_here"
        
        analytics_html = f"""
<!-- 百度统计 -->
<script>
var _hmt = _hmt || [];
(function() {{
  var hm = document.createElement("script");
  hm.src = "https://hm.baidu.com/hm.js?{baidu_id}";
  var s = document.getElementsByTagName("script")[0]; 
  s.parentNode.insertBefore(hm, s);
}})();
</script>

<!-- Google Analytics (可选) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
"""
        
        return analytics_html
    
    def optimize_html(self, html: str, query: str, city: str, slug: str = '') -> str:
        """
        优化HTML（添加所有SEO增强）
        
        Args:
            html: 原始HTML
            query: 用户查询
            city: 城市名
            slug: 攻略slug
            
        Returns:
            优化后的HTML
        """
        # 1. 优化关键词（在<head>中）
        long_tail_keywords = self.generate_long_tail_keywords(query, city)
        html = html.replace(
            'content="',
            f'content="{long_tail_keywords},',
            1  # 只替换第一个keywords
        )
        
        # 2. 添加CTA（在</body>前）
        cta_section = self.generate_cta_section(query)
        html = html.replace('</body>', f'{cta_section}\n</body>')
        
        # 3. 添加相关推荐（在CTA前）
        related_section = self.generate_related_section(query, city, slug)
        if related_section:
            html = html.replace(cta_section, f'{related_section}\n{cta_section}')
        
        # 4. 添加百度统计（在</head>前）
        analytics = self.generate_baidu_analytics()
        html = html.replace('</head>', f'{analytics}\n</head>')
        
        return html


# 单例
_optimizer = None

def get_seo_optimizer():
    """获取SEO优化器实例"""
    global _optimizer
    if _optimizer is None:
        _optimizer = SEOOptimizer()
    return _optimizer
