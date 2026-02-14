"""
攻略数据导入脚本
从爬虫获取数据 → 导入Chroma向量数据库
"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.rag_engine import get_rag_engine
from crawlers.xiaohongshu_crawler import get_xiaohongshu_crawler
from loguru import logger


def import_city_guides(city: str, categories: list = None):
    """
    导入指定城市的攻略数据
    
    Args:
        city: 城市名称（如"上海"）
        categories: 分类列表（["food", "hotel", "attraction"]）
    """
    if categories is None:
        categories = ["food", "hotel", "attraction"]
    
    rag = get_rag_engine()
    crawler = get_xiaohongshu_crawler()
    
    total_imported = 0
    
    for category in categories:
        # 构建搜索关键词
        keyword_map = {
            "food": f"{city}美食",
            "hotel": f"{city}酒店",
            "attraction": f"{city}景点"
        }
        keyword = keyword_map.get(category, f"{city}旅游")
        
        logger.info(f"📥 开始导入: {city} - {category}")
        
        # 爬取数据
        notes = crawler.search_notes(keyword, count=20)
        
        # 转换格式并导入
        guides = []
        for note in notes:
            # 🔥 修复：tags转成字符串（Chroma不支持list）
            tags_list = note.get("tags", [])
            tags_str = ", ".join(tags_list) if isinstance(tags_list, list) else str(tags_list)
            
            guide = {
                "id": note["note_id"],
                "content": f"{note['title']}\n\n{note['content']}",
                "metadata": {
                    "city": city,
                    "type": category,
                    "source": "xiaohongshu",
                    "author": note["author"],
                    "likes": note.get("likes", 0),
                    "tags": tags_str,  # 🔥 改成字符串
                    "create_time": note.get("create_time", ""),
                    "title": note["title"]
                }
            }
            guides.append(guide)
        
        # 批量导入
        rag.batch_add_guides(guides)
        total_imported += len(guides)
        
        logger.info(f"✅ {category} 导入完成: {len(guides)}条")
        
        # 请求频控
        crawler.rate_limit(delay=2.0)
    
    logger.info(f"🎉 全部导入完成: {city} | 总计: {total_imported}条")
    
    # 显示统计
    stats = rag.get_stats()
    logger.info(f"📊 数据库统计: {stats}")


def import_top_cities():
    """导入TOP10城市的数据"""
    top_cities = [
        "上海", "北京", "广州", "深圳", "杭州",
        "成都", "西安", "重庆", "海口", "三亚"
    ]
    
    for city in top_cities:
        logger.info(f"\n{'='*60}")
        logger.info(f"🏙️  正在导入: {city}")
        logger.info(f"{'='*60}\n")
        
        try:
            import_city_guides(city)
        except Exception as e:
            logger.error(f"❌ {city} 导入失败: {e}")
            continue


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="导入攻略数据到RAG数据库")
    parser.add_argument("--city", type=str, help="指定城市（如: 上海）")
    parser.add_argument("--all", action="store_true", help="导入TOP10城市")
    parser.add_argument("--categories", nargs="+", 
                       choices=["food", "hotel", "attraction"],
                       help="指定分类（默认全部）")
    
    args = parser.parse_args()
    
    if args.all:
        # 导入TOP10城市
        import_top_cities()
    elif args.city:
        # 导入指定城市
        import_city_guides(args.city, args.categories)
    else:
        # 默认：导入上海
        logger.info("未指定城市，默认导入上海数据")
        logger.info("使用 --city 上海 或 --all 导入所有城市\n")
        import_city_guides("上海")
    
    logger.info("\n✅ 导入任务完成！")
    logger.info("💡 使用 RAG引擎 搜索: from services.rag_engine import get_rag_engine")
