"""
批量生成野游记攻略
基于内容策略优先级
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.content_strategy import ContentStrategy
from services.dual_engine_generator import DualEngineGenerator
from loguru import logger
import time


def batch_generate(priority: str = 'high', limit: int = 10):
    """
    批量生成
    
    Args:
        priority: urgent/high/medium/low
        limit: 生成数量
    """
    strategy = ContentStrategy()
    generator = DualEngineGenerator()
    
    # 获取任务
    tasks = strategy.get_priority_tasks()
    
    if priority not in tasks:
        logger.error(f"无效的优先级: {priority}")
        return
    
    task_list = tasks[priority][:limit]
    
    if not task_list:
        logger.warning(f"没有 {priority} 优先级的任务")
        return
    
    logger.info(f"📝 开始批量生成 {len(task_list)} 个{priority}优先级攻略...")
    
    success_count = 0
    fail_count = 0
    
    for i, task in enumerate(task_list, 1):
        query = task['query']
        city = task['city']
        
        logger.info(f"\n[{i}/{len(task_list)}] 生成: {query}")
        
        try:
            # 生成攻略
            result = generator.generate_guide(
                query=query,
                output_format='html',
                city=city
            )
            
            if result.get('success'):
                logger.success(f"✅ 成功: {result.get('file')}")
                success_count += 1
            else:
                logger.error(f"❌ 失败: {result.get('error')}")
                fail_count += 1
            
            # 避免请求太快
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"❌ 异常: {e}")
            fail_count += 1
    
    logger.info(f"\n{'='*60}")
    logger.info(f"📊 批量生成完成:")
    logger.info(f"   ✅ 成功: {success_count}")
    logger.info(f"   ❌ 失败: {fail_count}")
    logger.info(f"{'='*60}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='批量生成野游记攻略')
    parser.add_argument('--priority', 
                       choices=['urgent', 'high', 'medium', 'low'],
                       default='high',
                       help='优先级')
    parser.add_argument('--limit', 
                       type=int,
                       default=10,
                       help='生成数量')
    
    args = parser.parse_args()
    
    batch_generate(priority=args.priority, limit=args.limit)


if __name__ == '__main__':
    main()
