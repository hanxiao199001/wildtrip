"""
图片爬虫服务 - 爬取景点/餐厅/酒店真实图片
支持：百度图片搜索（icrawler）
"""

import requests
import re
import json
import os
from urllib.parse import quote
from loguru import logger
import hashlib
from icrawler.builtin import BingImageCrawler, BaiduImageCrawler
import shutil


class ImageCrawler:
    """图片爬虫"""
    
    def __init__(self, save_dir='/root/clawd/wildtrip/web/public/images', base_url='http://47.82.159.93:5000/public'):
        """初始化"""
        self.save_dir = save_dir
        self.base_url = base_url
        os.makedirs(save_dir, exist_ok=True)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.baidu.com'
        }
        
        # 🔥 图片关键词黑名单（过滤无关图片）
        self.keyword_blacklist = [
            'PS', 'ps', 'Photoshop', 'photoshop',
            '人群', '分析图', '活动分析', '营销', '海报', '广告',
            '设计', '模板', '素材', '矢量', 'PPT', 'ppt',
            '图表', 'chart', 'graph', '统计', 'statistics', 'analysis',
            '封面', 'cover', '宣传', 'promotion', '推广',
            '卡通', 'cartoon', '插画', 'illustration',
            '二维码', 'QR', 'qr', '扫码', '关注', '公众号',
            '水印', 'watermark', 'logo', 'LOGO',
            '健康', '娱乐', '休闲', '智能化', 'Crowd', 'activity'  # 🔥 新增：针对"人群活动分析图"
        ]
    
    def search_and_download_images(self, keyword: str, max_images: int = 1) -> list:
        """
        使用icrawler搜索并下载图片
        
        Args:
            keyword: 搜索关键词
            max_images: 最多下载几张
            
        Returns:
            本地图片路径列表（相对路径，如 /images/xxx.jpg）
        """
        try:
            # 🔥 优化搜索关键词：添加限定词，避免抓到营销图/分析图
            # 检测关键词类型，添加合适的限定词
            enhanced_keyword = keyword
            
            # 酒店类：添加"外观"或"大堂"
            if any(word in keyword for word in ['酒店', '民宿', '客栈', '度假村', '旅馆', '宾馆', '青旅']):
                enhanced_keyword = f"{keyword} 外观 实拍"
            # 餐厅类：添加"店面"或"菜品"
            elif any(word in keyword for word in ['餐厅', '饭店', '火锅', '烧烤', '小吃', '店', '馆', '楼']):
                enhanced_keyword = f"{keyword} 店面 菜品"
            # 景点类：添加"景点"或"风景"，排除"废墟"、"石碑"等
            elif any(word in keyword for word in ['公园', '景区', '海滩', '岛', '山', '寺', '塔', '博物馆', '广场', '古镇', '村']):
                enhanced_keyword = f"{keyword} 景点 风景照 旅游 -废墟 -石碑"
            else:
                # 通用：添加"实拍照片"
                enhanced_keyword = f"{keyword} 实拍照片"
            
            # 为这次搜索创建临时目录
            import time
            temp_dir = f'/tmp/icrawler_{int(time.time() * 1000)}'
            os.makedirs(temp_dir, exist_ok=True)
            
            logger.info(f"🔍 搜索图片: {keyword} → {enhanced_keyword}")
            
            # 使用百度图片爬虫（国内速度快）
            try:
                crawler = BaiduImageCrawler(storage={'root_dir': temp_dir})
                crawler.crawl(keyword=enhanced_keyword, max_num=max_images, min_size=(200, 200))
            except:
                # 百度失败，尝试必应
                logger.warning(f"⚠️ 百度爬取失败，尝试必应...")
                crawler = BingImageCrawler(storage={'root_dir': temp_dir})
                crawler.crawl(keyword=enhanced_keyword, max_num=max_images, min_size=(200, 200))
            
            # 获取下载的图片文件
            downloaded_files = []
            if os.path.exists(temp_dir):
                for filename in os.listdir(temp_dir):
                    if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        temp_path = os.path.join(temp_dir, filename)
                        
                        # 🔥 过滤检查：检查文件名是否包含黑名单关键词
                        filename_lower = filename.lower()
                        is_blacklisted = False
                        for blackword in self.keyword_blacklist:
                            if blackword.lower() in filename_lower:
                                logger.warning(f"⚠️ 过滤无关图片: {filename} (包含: {blackword})")
                                is_blacklisted = True
                                break
                        
                        if is_blacklisted:
                            # 删除这张图片，不保存
                            os.remove(temp_path)
                            continue
                        
                        # 移动到正式目录并重命名
                        keyword_clean = re.sub(r'[^\w\u4e00-\u9fff]', '', keyword)[:20]
                        file_hash = hashlib.md5(open(temp_path, 'rb').read()).hexdigest()[:8]
                        ext = os.path.splitext(filename)[1]
                        new_filename = f"{keyword_clean}_{file_hash}{ext}"
                        final_path = os.path.join(self.save_dir, new_filename)
                        
                        shutil.move(temp_path, final_path)
                        # 返回完整URL（需要URL编码）
                        from urllib.parse import quote
                        encoded_filename = quote(new_filename)
                        image_url = f"{self.base_url}/images/{encoded_filename}"
                        downloaded_files.append(image_url)
                        logger.info(f"✅ 保存图片: {new_filename}")
            
            # 清理临时目录
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            
            # 🔥 手动触发垃圾回收（释放内存）
            import gc
            gc.collect()
            
            logger.info(f"✅ 图片爬取: {keyword} | 成功 {len(downloaded_files)} 张")
            return downloaded_files
            
        except Exception as e:
            logger.error(f"❌ 图片爬取失败: {keyword} | {e}")
            # 清理临时目录
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
            return []
    
    def _translate_keyword(self, keyword: str) -> str:
        """简单的中文关键词 -> 英文映射"""
        # 基础映射表
        mapping = {
            '酒店': 'hotel',
            '民宿': 'hostel',
            '度假村': 'resort',
            '餐厅': 'restaurant',
            '火锅': 'hotpot',
            '海鲜': 'seafood',
            '烧烤': 'barbecue',
            '小吃': 'food',
            '公园': 'park',
            '景区': 'scenic',
            '海滩': 'beach',
            '山': 'mountain',
            '寺': 'temple',
            '博物馆': 'museum',
            '古镇': 'ancient town',
            '火山': 'volcano',
            '海口': 'haikou',
            '三亚': 'sanya'
        }
        
        # 替换关键词
        keyword_en = keyword
        for cn, en in mapping.items():
            if cn in keyword:
                keyword_en = keyword_en.replace(cn, en)
        
        # 如果完全没变化，返回通用类型
        if keyword_en == keyword:
            if '店' in keyword or '馆' in keyword or '楼' in keyword:
                return 'restaurant,food'
            elif '酒店' in keyword or '宾馆' in keyword:
                return 'hotel'
            else:
                return 'travel,scenic,china'
        
        return keyword_en
    
    def download_image(self, image_url: str, keyword: str) -> str:
        """
        下载图片到本地
        
        Args:
            image_url: 图片URL
            keyword: 关键词（用于文件命名）
            
        Returns:
            本地图片路径（相对路径）
        """
        try:
            # 生成唯一文件名（MD5）
            url_hash = hashlib.md5(image_url.encode()).hexdigest()[:12]
            keyword_clean = re.sub(r'[^\w\u4e00-\u9fff]', '', keyword)[:20]  # 清理文件名
            
            # 尝试获取图片格式
            ext = '.jpg'
            if '.png' in image_url:
                ext = '.png'
            elif '.jpeg' in image_url or '.jpg' in image_url:
                ext = '.jpg'
            elif '.webp' in image_url:
                ext = '.webp'
            
            filename = f"{keyword_clean}_{url_hash}{ext}"
            filepath = os.path.join(self.save_dir, filename)
            
            # 如果已存在，直接返回
            if os.path.exists(filepath):
                logger.info(f"✅ 图片已存在: {filename}")
                return f"/images/{filename}"
            
            # 下载图片
            response = requests.get(image_url, headers=self.headers, timeout=15, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)
            
            logger.info(f"✅ 下载成功: {filename} | {len(response.content)} bytes")
            return f"/images/{filename}"
            
        except Exception as e:
            logger.error(f"❌ 下载图片失败: {image_url} | {e}")
            # 返回占位图片
            return f"https://picsum.photos/600/400?random={quote(keyword)}"
    
    def get_poi_image(self, poi_name: str, poi_type: str = 'place') -> str:
        """
        获取POI图片（优先百度图片，失败则用占位图）
        
        Args:
            poi_name: POI名称
            poi_type: POI类型 (place/hotel/food)
            
        Returns:
            图片URL（本地路径或占位图）
        """
        try:
            # 构建搜索关键词
            if poi_type == 'hotel':
                keyword = f"{poi_name} 酒店"
            elif poi_type == 'food':
                keyword = f"{poi_name} 餐厅"
            else:
                keyword = poi_name
            
            # 使用icrawler搜索并下载图片
            image_paths = self.search_and_download_images(keyword, max_images=1)
            
            if image_paths:
                # 返回第一张本地图片路径
                return image_paths[0]
            else:
                # 没找到，返回占位图
                logger.warning(f"⚠️ 未找到图片: {poi_name}，使用占位图")
                return f"https://picsum.photos/600/400?random={quote(poi_name)}"
            
        except Exception as e:
            logger.error(f"❌ 获取POI图片失败: {poi_name} | {e}")
            return f"https://picsum.photos/600/400?random={quote(poi_name)}"
    
    def extract_pois_from_content(self, content: str) -> dict:
        """
        从攻略内容中提取POI名称
        
        Args:
            content: Markdown攻略内容
            
        Returns:
            {'hotels': [...], 'foods': [...], 'places': [...]}
        """
        pois = {
            'hotels': [],
            'foods': [],
            'places': []
        }
        
        try:
            # 正则匹配：**xxx酒店** 或 **xxx**（在酒店推荐章节）
            hotel_pattern = r'\*\*([^\*]+?(?:酒店|民宿|客栈|度假村|旅馆|宾馆|青旅)[^\*]*?)\*\*'
            hotels = re.findall(hotel_pattern, content)
            # 清理括号内容（如"（滨海店）"）
            hotels = [re.sub(r'[（(][^)）]*[)）]', '', h).strip() for h in hotels]
            pois['hotels'] = list(set(hotels))[:10]  # 去重，最多10个
            
            # 正则匹配：**xxx** ¥价格格式（通常是餐厅/酒店）
            # 但排除已经被识别为酒店的
            price_pattern = r'\*\*([^\*]+?)\*\*\s*¥\d+'
            price_items = re.findall(price_pattern, content)
            for item in price_items:
                clean = re.sub(r'[（(][^)）]*[)）]', '', item).strip()
                # 如果不是酒店，且包含餐饮关键词，则认为是餐厅
                if not any(word in clean for word in ['酒店', '民宿', '客栈', '度假村', '旅馆', '宾馆']):
                    # 包含餐饮关键词或长度合理
                    if (any(word in clean for word in ['店', '馆', '楼', '餐厅', '小吃', '粉', '海鲜', '烧烤', '火锅', '家', '乐', '坊', '轩', '阁', '苑', '园', '茶', '鸡', '羊', '豆腐']) 
                        or (len(clean) >= 3 and len(clean) <= 20)):
                        pois['foods'].append(clean)
            pois['foods'] = list(set(pois['foods']))[:20]  # 去重，最多20个
            
            # 正则匹配：景点（明确的景点关键词）
            place_pattern = r'\*\*([^\*\n]{3,30}?(?:公园|景区|海滩|岛|山|寺|塔|博物馆|广场|古镇|村|遗址|群|旅游区|红树林|动植物园|世界遗产)[^\*]*?)\*\*'
            places = re.findall(place_pattern, content)
            for place in places:
                clean = re.sub(r'[（(][^)）]*[)）]', '', place).strip()
                # 过滤掉明显不是景点的（如价格、推荐等）
                # 同时过滤掉已经识别为餐厅的
                if not any(word in clean for word in ['¥', '推荐', '选择', '价格', '位置', '特色']):
                    if clean not in pois['foods'] and len(clean) >= 3 and len(clean) <= 30:
                        pois['places'].append(clean)
            pois['places'] = list(set(pois['places']))[:15]  # 去重，最多15个
            
            logger.info(f"✅ 提取POI: 酒店{len(pois['hotels'])}个 | 餐厅{len(pois['foods'])}个 | 景点{len(pois['places'])}个")
            
        except Exception as e:
            logger.error(f"❌ 提取POI失败: {e}")
        
        return pois
    
    def enrich_content_with_images(self, content: str) -> str:
        """
        为攻略内容添加真实图片
        
        Args:
            content: 原始Markdown内容（含LINK_xxx占位符）
            
        Returns:
            增强后的Markdown内容（含真实图片）
        """
        try:
            # 提取所有POI
            pois = self.extract_pois_from_content(content)
            
            # 为每个POI下载图片
            poi_images = {}
            
            # 处理酒店
            for hotel in pois['hotels']:
                image_url = self.get_poi_image(hotel, 'hotel')
                poi_images[hotel] = image_url
            
            # 处理餐厅
            for food in pois['foods']:
                image_url = self.get_poi_image(food, 'food')
                poi_images[food] = image_url
            
            # 处理景点
            for place in pois['places']:
                image_url = self.get_poi_image(place, 'place')
                poi_images[place] = image_url
            
            # 在Markdown中插入图片（在每个POI名称后）
            enhanced_content = content
            for poi_name, image_url in poi_images.items():
                # 查找 **POI名** 后面是否已有图片
                pattern = rf'(\*\*{re.escape(poi_name)}\*\*.*?)(\n(?!!\[))'
                replacement = rf'\1\n\n![{poi_name}]({image_url})\n'
                enhanced_content = re.sub(pattern, replacement, enhanced_content, count=1, flags=re.DOTALL)
            
            logger.info(f"✅ 内容增强完成: 插入 {len(poi_images)} 张图片")
            return enhanced_content
            
        except Exception as e:
            logger.error(f"❌ 内容增强失败: {e}")
            return content  # 失败则返回原内容


# 快速测试
if __name__ == '__main__':
    crawler = ImageCrawler()
    
    # 测试搜索并下载
    image_paths = crawler.search_and_download_images("海口火山口地质公园", 2)
    print(f"下载 {len(image_paths)} 张图片:")
    for path in image_paths:
        print(f"  {path}")
    
    # 测试POI提取
    test_content = """
## 🏨 住宿推荐

### 1. **海口香格里拉大酒店** ¥800/晚
- 位置好
- [美团预订](LINK_HOTEL_xxx)

### 2. **美食推荐**
**隆仔鸡饭店** ¥60/人
- 好吃
- [美团团购](LINK_FOOD_xxx)
    """
    pois = crawler.extract_pois_from_content(test_content)
    print(f"\n提取POI: {pois}")
