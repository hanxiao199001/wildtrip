"""
SEO服务 - 将生成的攻略保存为静态HTML页面
支持：标题优化、meta标签、sitemap生成
"""

import os
import hashlib
from datetime import datetime
from pathlib import Path
from loguru import logger


class SEOService:
    """SEO服务 - 攻略静态页面生成和管理"""
    
    def __init__(self, static_dir: str = "/root/clawd/wildtrip/web/guides"):
        """
        初始化SEO服务
        
        Args:
            static_dir: 静态页面保存目录
        """
        self.static_dir = Path(static_dir)
        self.static_dir.mkdir(parents=True, exist_ok=True)
        
        # sitemap保存路径
        self.sitemap_path = Path("/root/clawd/wildtrip/web/sitemap.xml")
        
        logger.info(f"✅ SEO服务初始化完成 | 静态目录: {self.static_dir}")
    
    def generate_slug(self, query: str) -> str:
        """
        生成URL友好的slug
        
        Args:
            query: 用户查询（如"海口3天亲子游"）
            
        Returns:
            slug（如"haikou-3day-family-trip"）
        """
        # 提取关键词
        import re
        
        # 移除特殊字符
        clean = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]+', '-', query)
        
        # 生成唯一ID（基于query的hash）
        hash_id = hashlib.md5(query.encode()).hexdigest()[:8]
        
        # 组合：关键词-时间戳
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        slug = f"{clean}-{timestamp}-{hash_id}"
        
        return slug.lower()
    
    def generate_html(self, query: str, content: str, stats: dict) -> str:
        """
        生成SEO优化的HTML页面
        
        Args:
            query: 用户查询
            content: 攻略内容（Markdown格式）
            stats: 统计信息
            
        Returns:
            完整的HTML内容
        """
        from prompts.wildtrip_prompt import extract_city_name
        
        # 提取城市
        city = extract_city_name(query)
        
        # 生成标题（SEO优化）
        title = f"{query} - 野游记AI攻略 | 不走寻常路的旅行指南"
        
        # 生成描述（SEO优化）
        description = f"野游记为你生成{query}的个性化攻略，包含本地美食推荐、酒店预订、景点门票，带美团返现链接。{stats.get('word_count', 0)}字详细攻略，{stats.get('restaurants_count', 0)}家餐厅推荐。"
        
        # 提取关键词
        keywords = f"{city},旅游攻略,{city}旅游,{city}美食,{city}酒店,{city}景点,野游记,AI攻略"
        
        # 🔥 使用行程规划生成器（新UI，不降级）
        from services.itinerary_generator import get_itinerary_generator
        
        generator = get_itinerary_generator()
        html = generator.generate(query, content, stats)
        logger.info("✅ 使用行程规划生成器")
        return html
        
        # 生成完整HTML
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}">
    <meta name="author" content="野游记 WildTrip">
    
    <!-- Open Graph / 微信分享 -->
    <meta property="og:type" content="article">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:site_name" content="野游记 WildTrip">
    
    <!-- 结构化数据 - 帮助搜索引擎理解 -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "{query}",
        "description": "{description}",
        "author": {{
            "@type": "Organization",
            "name": "野游记 WildTrip"
        }},
        "datePublished": "{datetime.now().isoformat()}",
        "wordCount": {stats.get('word_count', 0)}
    }}
    </script>
    
    <title>{title}</title>
    
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1, h2, h3 {{
            color: #FF6B35;
        }}
        .stats {{
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .back-link {{
            display: inline-block;
            margin: 20px 0;
            padding: 10px 20px;
            background: #FF6B35;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }}
        .back-link:hover {{
            background: #E55A2B;
        }}
    </style>
</head>
<body>
    <a href="/" class="back-link">🌴 返回野游记首页</a>
    
    <h1>{query}</h1>
    
    <div class="stats">
        📝 {stats.get('word_count', 0)} 字
        {f"• 🏨 {stats['hotels_count']} 家酒店" if stats.get('hotels_count', 0) > 0 else ""}
        {f"• 🍜 {stats['restaurants_count']} 家餐厅" if stats.get('restaurants_count', 0) > 0 else ""}
        {f"• 🎫 {stats['tickets_count']} 个景点" if stats.get('tickets_count', 0) > 0 else ""}
    </div>
    
    <div class="content">
        {html_content}
    </div>
    
    <hr>
    
    <p style="text-align: center; color: #999;">
        由野游记AI生成 | <a href="/">生成你的专属攻略</a>
    </p>
</body>
</html>
"""
        return html
    
    def save_guide(self, query: str, content: str, stats: dict) -> dict:
        """
        保存攻略为静态页面（自动清洗隐私信息）
        
        Args:
            query: 用户查询
            content: 攻略内容
            stats: 统计信息
            
        Returns:
            {
                'slug': 'haikou-3day-family-trip',
                'url': '/guides/haikou-3day-family-trip.html',
                'full_path': '/path/to/file.html',
                'privacy_cleaned': True/False
            }
        """
        # 🔥 隐私清洗
        from services.privacy_cleaner import get_privacy_cleaner
        
        cleaner = get_privacy_cleaner()
        
        # 判断是否应该保存为公开页面
        should_save, reason = cleaner.should_save_to_seo(query, content)
        
        if not should_save:
            logger.warning(f"⚠️ 攻略不适合公开: {reason} | 查询: {query[:30]}...")
            return {
                'slug': None,
                'url': None,
                'full_path': None,
                'privacy_cleaned': False,
                'skip_reason': reason
            }
        
        # 清洗query和content
        cleaned_query, is_query_sensitive = cleaner.clean_query(query)
        cleaned_content = cleaner.clean_content(content)
        
        if is_query_sensitive:
            logger.info(f"🔒 Query已清洗: {query[:30]}... → {cleaned_query[:30]}...")
        
        # 生成slug（使用清洗后的query）
        slug = self.generate_slug(cleaned_query)
        
        # 生成HTML（使用清洗后的内容）
        html = self.generate_html(cleaned_query, cleaned_content, stats)
        
        # 🔥 SEO优化增强
        from services.seo_optimizer import get_seo_optimizer
        from prompts.wildtrip_prompt import extract_city_name
        
        optimizer = get_seo_optimizer()
        city = extract_city_name(cleaned_query)
        html = optimizer.optimize_html(html, cleaned_query, city, slug)
        logger.info(f"✅ SEO优化完成: CTA + 关键词 + 内部链接 + 统计")
        
        # 保存文件
        file_path = self.static_dir / f"{slug}.html"
        file_path.write_text(html, encoding='utf-8')
        
        logger.info(f"✅ 攻略已保存（隐私已保护）: {slug}")
        
        # 更新sitemap（使用清洗后的query）
        self.update_sitemap(slug, cleaned_query)
        
        return {
            'slug': slug,
            'url': f'/guides/{slug}.html',
            'full_path': str(file_path),
            'privacy_cleaned': is_query_sensitive  # 是否进行了隐私清洗
        }
    
    def update_sitemap(self, slug: str, query: str):
        """
        更新sitemap.xml（让搜索引擎快速收录）
        
        Args:
            slug: 攻略的slug
            query: 用户查询
        """
        # 读取现有sitemap（如果存在）
        existing_urls = set()
        if self.sitemap_path.exists():
            content = self.sitemap_path.read_text(encoding='utf-8')
            import re
            existing_urls = set(re.findall(r'<loc>(.*?)</loc>', content))
        
        # 添加新URL
        new_url = f"https://wildtrip.com.cn/guides/{slug}.html"
        existing_urls.add(new_url)
        
        # 生成sitemap.xml
        sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        for url in existing_urls:
            sitemap += f'''  <url>
    <loc>{url}</loc>
    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
'''
        
        sitemap += '</urlset>'
        
        # 保存sitemap
        self.sitemap_path.write_text(sitemap, encoding='utf-8')
        
        logger.info(f"✅ Sitemap已更新: {len(existing_urls)}个页面")
    
    def get_all_guides(self) -> list:
        """
        获取所有已保存的攻略
        
        Returns:
            [{'slug': 'xxx', 'url': '/guides/xxx.html', 'created_at': '2026-02-04'}, ...]
        """
        guides = []
        
        for file_path in self.static_dir.glob("*.html"):
            guides.append({
                'slug': file_path.stem,
                'url': f'/guides/{file_path.name}',
                'created_at': datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d")
            })
        
        return sorted(guides, key=lambda x: x['created_at'], reverse=True)


# 单例
_seo_service_instance = None


def get_seo_service() -> SEOService:
    """获取SEO服务实例（单例模式）"""
    global _seo_service_instance
    
    if _seo_service_instance is None:
        _seo_service_instance = SEOService()
    
    return _seo_service_instance


# 示例用法
if __name__ == "__main__":
    seo = SEOService()
    
    # 测试保存攻略
    result = seo.save_guide(
        query="海口3天亲子游，预算5000",
        content="# 海口3天亲子游攻略\n\n...",
        stats={'word_count': 3000, 'hotels_count': 3, 'restaurants_count': 5}
    )
    
    print("保存结果:", result)
    
    # 测试获取所有攻略
    guides = seo.get_all_guides()
    print(f"已保存攻略: {len(guides)}篇")
