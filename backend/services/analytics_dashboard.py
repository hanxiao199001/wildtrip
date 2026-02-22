"""
野游记 SEO 仪表盘
监控：收录、流量、转化
"""

import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
import json
from loguru import logger


class AnalyticsDashboard:
    """分析仪表盘"""
    
    def __init__(self):
        """初始化"""
        self.guides_dir = Path("/root/clawd/wildtrip/web/guides")
        self.metadata_file = self.guides_dir / "metadata.json"
        
    def get_total_pages(self) -> int:
        """获取总页面数"""
        html_files = list(self.guides_dir.glob("guide-*.html"))
        return len(html_files)
    
    def get_page_urls(self) -> List[str]:
        """获取所有页面URL"""
        base_url = "https://wildtrip.ai/guides"  # 替换为你的真实域名
        urls = []
        
        for html_file in self.guides_dir.glob("guide-*.html"):
            filename = html_file.name
            urls.append(f"{base_url}/{filename}")
        
        return urls
    
    def check_baidu_inclusion(self, url: str) -> bool:
        """
        检查URL是否被百度收录
        
        Args:
            url: 页面URL
            
        Returns:
            是否收录
        """
        try:
            # 百度site查询
            search_url = f"https://www.baidu.com/s?wd=site:{url}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            # 简单判断：如果搜索结果包含URL，说明被收录
            return url in response.text and '百度为您找到相关结果约0个' not in response.text
            
        except Exception as e:
            logger.warning(f"检查收录失败 {url}: {e}")
            return False
    
    def get_inclusion_stats(self, sample_size: int = 10) -> Dict:
        """
        获取收录统计（抽样）
        
        Args:
            sample_size: 抽样数量
            
        Returns:
            统计数据
        """
        urls = self.get_page_urls()
        total = len(urls)
        
        # 抽样检查
        import random
        sample_urls = random.sample(urls, min(sample_size, total))
        
        included_count = 0
        for url in sample_urls:
            if self.check_baidu_inclusion(url):
                included_count += 1
            # 避免请求太快
            import time
            time.sleep(1)
        
        # 推算总收录数
        estimated_inclusion_rate = included_count / len(sample_urls)
        estimated_included = int(total * estimated_inclusion_rate)
        
        return {
            'total_pages': total,
            'sample_size': len(sample_urls),
            'sample_included': included_count,
            'estimated_inclusion_rate': estimated_inclusion_rate,
            'estimated_included': estimated_included
        }
    
    def get_metadata_stats(self) -> Dict:
        """
        从metadata.json获取统计
        
        Returns:
            元数据统计
        """
        if not self.metadata_file.exists():
            return {}
        
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            guides = metadata.get('guides', [])
            
            # 城市分布
            city_counts = {}
            for guide in guides:
                city = guide.get('city', 'unknown')
                city_counts[city] = city_counts.get(city, 0) + 1
            
            # 生成时间分布
            dates = [g.get('timestamp', '')[:10] for g in guides if g.get('timestamp')]
            date_counts = {}
            for date in dates:
                date_counts[date] = date_counts.get(date, 0) + 1
            
            return {
                'total_guides': len(guides),
                'cities': city_counts,
                'generation_dates': date_counts
            }
            
        except Exception as e:
            logger.error(f"读取metadata失败: {e}")
            return {}
    
    def generate_sitemap_if_missing(self) -> str:
        """生成sitemap.xml（如果不存在）"""
        sitemap_file = self.guides_dir / "sitemap.xml"
        
        if sitemap_file.exists():
            return str(sitemap_file)
        
        # 生成sitemap
        urls = self.get_page_urls()
        now = datetime.now().strftime('%Y-%m-%d')
        
        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        for url in urls:
            xml_content += f'  <url>\n'
            xml_content += f'    <loc>{url}</loc>\n'
            xml_content += f'    <lastmod>{now}</lastmod>\n'
            xml_content += f'    <changefreq>weekly</changefreq>\n'
            xml_content += f'    <priority>0.8</priority>\n'
            xml_content += f'  </url>\n'
        
        xml_content += '</urlset>'
        
        sitemap_file.write_text(xml_content, encoding='utf-8')
        logger.info(f"✅ 生成sitemap: {sitemap_file}")
        
        return str(sitemap_file)
    
    def print_dashboard(self):
        """打印仪表盘"""
        print("\n" + "="*60)
        print("🎯 野游记 SEO 仪表盘")
        print("="*60)
        
        # 1. 页面统计
        total_pages = self.get_total_pages()
        print(f"\n📄 页面总数: {total_pages}")
        
        # 2. 元数据统计
        meta_stats = self.get_metadata_stats()
        if meta_stats:
            print(f"📊 元数据统计:")
            print(f"   - 总攻略数: {meta_stats.get('total_guides', 0)}")
            print(f"   - 城市分布: {dict(list(meta_stats.get('cities', {}).items())[:5])}")
        
        # 3. Sitemap检查
        sitemap_file = self.guides_dir / "sitemap.xml"
        if sitemap_file.exists():
            print(f"✅ Sitemap: {sitemap_file}")
        else:
            print(f"⚠️  Sitemap 不存在，生成中...")
            sitemap_path = self.generate_sitemap_if_missing()
            print(f"✅ 已生成: {sitemap_path}")
        
        # 4. 百度收录检查（抽样）
        print(f"\n🔍 百度收录检查 (抽样10个页面)...")
        print(f"   ⏳ 请稍候...")
        
        # 暂时跳过实际检查，因为需要真实域名
        print(f"   ⚠️  需要真实域名才能检查收录")
        print(f"   💡 部署后运行: python analytics_dashboard.py --check-inclusion")
        
        # 5. 百度统计检查
        print(f"\n📊 百度统计:")
        seo_file = Path("/root/clawd/backend/services/seo_optimizer.py")
        if seo_file.exists():
            content = seo_file.read_text(encoding='utf-8')
            if 'your_baidu_analytics_id_here' in content:
                print(f"   ⚠️  百度统计ID未配置")
                print(f"   👉 去 https://tongji.baidu.com 注册并获取ID")
            else:
                print(f"   ✅ 百度统计ID已配置")
        
        # 6. 下一步行动
        print(f"\n🎯 下一步行动:")
        print(f"   1. 注册百度统计: https://tongji.baidu.com")
        print(f"   2. 更新 seo_optimizer.py 中的百度统计ID")
        print(f"   3. 重新生成所有页面（埋入统计代码）")
        print(f"   4. 部署到真实域名")
        print(f"   5. 提交sitemap到百度搜索资源平台")
        print(f"   6. 等待1-2天，查看百度统计后台")
        
        print("\n" + "="*60)


def main():
    """主函数"""
    dashboard = AnalyticsDashboard()
    dashboard.print_dashboard()


if __name__ == '__main__':
    main()
