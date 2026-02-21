"""
发布机器人 - Publisher Bot
保存静态页、更新sitemap、验证访问
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from loguru import logger
from typing import Dict, List
from datetime import datetime
import xml.etree.ElementTree as ET


class PublisherBot:
    """发布机器人 - 保存 + 验证"""
    
    def __init__(self, base_url: str = "https://www.wildtrip.com.cn"):
        from services.seo_service import get_seo_service
        
        self.seo_service = get_seo_service()
        self.base_url = base_url
        self.static_dir = Path(__file__).parent.parent.parent / 'web' / 'guides'
        self.static_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ 发布机器人初始化完成")
    
    def publish(self, topic: str, content: str, stats: Dict) -> Dict:
        """
        发布单篇攻略
        
        Steps:
        1. 保存静态 HTML
        2. 更新 sitemap
        3. 验证页面可访问
        
        Returns:
            {
                'success': True/False,
                'url': '...',
                'file_path': '...',
                'accessible': True/False
            }
        """
        logger.info(f"📤 开始发布: {topic}")
        
        # 1. 保存静态页
        result = self.seo_service.save_guide(topic, content, stats)
        
        # 检查是否因隐私原因跳过
        if 'skip_reason' in result:
            logger.warning(f"⚠️ 跳过发布: {result['skip_reason']}")
            return {
                'success': False,
                'error': result['skip_reason']
            }
        
        # 检查是否保存成功
        if not result.get('slug'):
            logger.error(f"❌ 保存失败")
            return {
                'success': False,
                'error': '保存失败，未返回 slug'
            }
        
        file_path = result['full_path']
        url = self.base_url + result['url']
        
        logger.info(f"  ✅ 已保存: {file_path}")
        logger.info(f"  🔗 URL: {url}")
        
        # 2. 更新 sitemap
        self._update_sitemap(url, file_path)
        
        # 3. 验证访问
        accessible = self._verify_access(url)
        
        if accessible:
            logger.success(f"✅ 发布成功: {url}")
        else:
            logger.warning(f"⚠️ 发布完成但访问验证失败: {url}")
        
        return {
            'success': True,
            'url': url,
            'file_path': file_path,
            'accessible': accessible
        }
    
    def _update_sitemap(self, url: str, file_path: str):
        """更新 sitemap.xml"""
        sitemap_path = Path(__file__).parent.parent.parent / 'web' / 'sitemap.xml'
        
        try:
            # 读取现有 sitemap
            if sitemap_path.exists():
                tree = ET.parse(sitemap_path)
                root = tree.getroot()
            else:
                # 创建新 sitemap
                root = ET.Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
                tree = ET.ElementTree(root)
            
            # 检查 URL 是否已存在
            existing_locs = [loc.text for loc in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
            
            if url not in existing_locs:
                # 添加新 URL
                url_elem = ET.SubElement(root, 'url')
                
                loc = ET.SubElement(url_elem, 'loc')
                loc.text = url
                
                lastmod = ET.SubElement(url_elem, 'lastmod')
                lastmod.text = datetime.now().strftime('%Y-%m-%d')
                
                changefreq = ET.SubElement(url_elem, 'changefreq')
                changefreq.text = 'monthly'
                
                priority = ET.SubElement(url_elem, 'priority')
                priority.text = '0.8'
                
                # 保存
                tree.write(sitemap_path, encoding='utf-8', xml_declaration=True)
                logger.info(f"  ✅ Sitemap 已更新")
            else:
                logger.debug(f"  ℹ️ URL 已在 sitemap 中")
        
        except Exception as e:
            logger.warning(f"  ⚠️ Sitemap 更新失败: {e}")
    
    def _verify_access(self, url: str) -> bool:
        """验证页面可访问"""
        try:
            # 如果是本地文件，检查文件是否存在
            if url.startswith('file://'):
                file_path = url.replace('file://', '')
                return Path(file_path).exists()
            
            # 如果是 HTTP(S)，发送请求
            response = requests.head(url, timeout=5, allow_redirects=True)
            return response.status_code == 200
            
        except Exception as e:
            logger.debug(f"  ⚠️ 访问验证失败: {e}")
            return False
    
    def batch_publish(self, contents: List[Dict]) -> Dict:
        """
        批量发布
        
        Args:
            contents: [{"topic": "...", "content": "...", "stats": {...}}, ...]
            
        Returns:
            {
                'total': 10,
                'success': 8,
                'failed': 2,
                'results': [...]
            }
        """
        logger.info(f"📤 开始批量发布 | 总数: {len(contents)}")
        
        results = []
        success_count = 0
        
        for i, item in enumerate(contents, 1):
            logger.info(f"  [{i}/{len(contents)}] {item['topic']}")
            
            try:
                result = self.publish(
                    topic=item['topic'],
                    content=item['content'],
                    stats=item.get('stats', {})
                )
                
                results.append(result)
                
                if result['success']:
                    success_count += 1
                    
            except Exception as e:
                logger.error(f"❌ 发布失败: {item['topic']} | {e}")
                results.append({
                    'success': False,
                    'error': str(e)
                })
        
        logger.success(f"✅ 批量发布完成 | {success_count}/{len(contents)} 成功")
        
        return {
            'total': len(contents),
            'success': success_count,
            'failed': len(contents) - success_count,
            'results': results
        }
    
    def submit_to_search_engines(self):
        """提交到搜索引擎（百度、Google）"""
        sitemap_url = f"{self.base_url}/sitemap.xml"
        
        # 百度站长平台
        baidu_api = "http://data.zz.baidu.com/urls"
        baidu_token = "你的百度站长token"  # 需要配置
        
        # Google Search Console
        google_api = "https://www.google.com/ping"
        
        logger.info("🚀 提交到搜索引擎...")
        
        # 这里需要实际的 API token 和实现
        logger.warning("⚠️ 搜索引擎提交需要配置 API token")
        
        return {
            'baidu': 'pending',
            'google': 'pending'
        }


def main():
    """测试运行"""
    bot = PublisherBot()
    
    # 测试单个发布
    result = bot.publish(
        topic="海口周末带7岁男孩测试",
        content="# 测试内容\n\n这是一个测试攻略。",
        stats={'word_count': 100, 'hotels_count': 1, 'restaurants_count': 2}
    )
    
    print("\n【发布结果】")
    print(f"成功: {result['success']}")
    print(f"URL: {result.get('url')}")
    print(f"可访问: {result.get('accessible')}")


if __name__ == "__main__":
    main()
