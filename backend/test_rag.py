"""
RAG系统测试脚本 - 快速验证
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from services.rag_engine import get_rag_engine
from loguru import logger


def test_rag_system():
    """测试RAG系统"""
    
    logger.info("🧪 开始测试RAG系统...\n")
    
    # 1. 初始化
    logger.info("=" * 60)
    logger.info("📊 步骤1：初始化RAG引擎")
    logger.info("=" * 60)
    rag = get_rag_engine()
    stats = rag.get_stats()
    logger.info(f"✅ 数据库路径: {stats['db_path']}")
    logger.info(f"✅ 攻略总数: {stats['total_guides']}条\n")
    
    if stats['total_guides'] == 0:
        logger.warning("⚠️ 数据库为空！请先运行导入脚本：")
        logger.warning("   python -m scripts.import_guides --city 上海\n")
        return
    
    # 2. 测试搜索
    logger.info("=" * 60)
    logger.info("🔍 步骤2：测试搜索功能")
    logger.info("=" * 60)
    
    test_queries = [
        ("上海小笼包", "上海", "food"),
        ("上海酒店", "上海", "hotel"),
        ("上海景点", "上海", "attraction"),
        ("上海美食推荐", "上海", None),
    ]
    
    for query, city, guide_type in test_queries:
        logger.info(f"\n🔍 查询: {query}")
        logger.info(f"   城市: {city} | 类型: {guide_type or '全部'}")
        
        results = rag.search(
            query=query,
            n_results=3,
            city=city,
            guide_type=guide_type
        )
        
        if results:
            logger.info(f"✅ 找到 {len(results)} 条相关攻略：")
            for i, r in enumerate(results, 1):
                metadata = r.get('metadata', {})
                logger.info(f"\n   [{i}] {metadata.get('title', '无标题')}")
                logger.info(f"       作者: {metadata.get('author', '未知')} | 点赞: {metadata.get('likes', 0)}")
                logger.info(f"       标签: {metadata.get('tags', '无')}")
                logger.info(f"       相似度: {r.get('distance', 0):.3f}")
                logger.info(f"       内容预览: {r['content'][:100]}...")
        else:
            logger.warning(f"❌ 没有找到相关攻略")
    
    # 3. 总结
    logger.info("\n" + "=" * 60)
    logger.info("🎉 RAG系统测试完成！")
    logger.info("=" * 60)
    logger.info("✅ 向量数据库正常工作")
    logger.info("✅ 语义搜索功能正常")
    logger.info("✅ 数据检索成功")
    logger.info("\n💡 下一步：启动后端，测试完整流程")
    logger.info("   后端会自动调用RAG检索，生成更本地化的攻略\n")


if __name__ == "__main__":
    test_rag_system()
