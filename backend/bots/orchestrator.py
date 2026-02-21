"""
三机器人流水线编排器 - Orchestrator
协调 Topic Hunter → Content Generator → Publisher
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from datetime import datetime
from loguru import logger

from bots.topic_hunter import TopicHunterBot
from bots.content_generator import ContentGeneratorBot
from bots.publisher import PublisherBot


class ProductionOrchestrator:
    """三机器人流水线编排器"""
    
    def __init__(self):
        self.topic_hunter = TopicHunterBot()
        self.content_generator = ContentGeneratorBot()
        self.publisher = PublisherBot()
        
        # 输出目录
        self.output_dir = Path(__file__).parent.parent.parent / 'data' / 'production'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ 流水线编排器初始化完成")
    
    def run_full_pipeline(
        self,
        target_count: int = 10,
        topic_time_limit: int = 20,
        skip_topic_hunting: bool = False,
        topics_file: str = None
    ) -> Dict:
        """
        运行完整流水线
        
        Args:
            target_count: 目标生成数量
            topic_time_limit: 选题时限（分钟）
            skip_topic_hunting: 跳过选题（使用现有选题文件）
            topics_file: 选题文件路径（如果 skip_topic_hunting=True）
            
        Returns:
            {
                'total_time_minutes': 120,
                'topics_count': 10,
                'generated_count': 8,
                'published_count': 7,
                'results': [...]
            }
        """
        start_time = datetime.now()
        logger.info(f"🚀 启动三机器人流水线 | 目标: {target_count} 篇")
        
        # ========== Step 1: 选题机器人 ==========
        if skip_topic_hunting and topics_file:
            logger.info("📋 使用现有选题文件...")
            with open(topics_file, 'r', encoding='utf-8') as f:
                topics_data = json.load(f)
                topics = [t['title'] for t in topics_data['topics'][:target_count]]
        else:
            logger.info("🔍 Step 1: 选题机器人启动...")
            topic_results = self.topic_hunter.hunt_topics(
                max_topics=target_count,
                time_limit_minutes=topic_time_limit
            )
            topics = [t['title'] for t in topic_results]
        
        logger.info(f"  ✅ 选题完成: {len(topics)} 个")
        
        # ========== Step 2: 内容生产机器人 ==========
        logger.info("📝 Step 2: 内容生产机器人启动...")
        
        generation_results = []
        for i, topic in enumerate(topics, 1):
            logger.info(f"  [{i}/{len(topics)}] {topic}")
            
            try:
                content, qa_report = self.content_generator.generate_with_qa(topic)
                
                generation_results.append({
                    'topic': topic,
                    'content': content,
                    'qa_report': qa_report,
                    'success': qa_report['passed']
                })
                
                # 输出质检报告
                if qa_report['passed']:
                    logger.success(f"    ✅ 质检通过 | 分数: {qa_report['score']:.2f}")
                else:
                    logger.warning(f"    ⚠️ 质检未通过 | 分数: {qa_report['score']:.2f}")
                    logger.warning(f"    问题: {qa_report['issues']}")
                
            except Exception as e:
                logger.error(f"    ❌ 生成失败: {e}")
                generation_results.append({
                    'topic': topic,
                    'content': '',
                    'qa_report': {'passed': False, 'error': str(e)},
                    'success': False
                })
        
        # 统计生成成功数
        successful_contents = [r for r in generation_results if r['success']]
        logger.info(f"  ✅ 内容生成完成: {len(successful_contents)}/{len(topics)} 成功")
        
        # ========== Step 3: 发布机器人 ==========
        logger.info("📤 Step 3: 发布机器人启动...")
        
        publish_contents = []
        for result in successful_contents:
            publish_contents.append({
                'topic': result['topic'],
                'content': result['content'],
                'stats': {
                    'word_count': len(result['content']),
                    'hotels_count': result['content'].count('住宿推荐'),
                    'restaurants_count': result['content'].count('餐厅'),
                    'total_cashback': 0
                }
            })
        
        publish_results = self.publisher.batch_publish(publish_contents)
        
        logger.info(f"  ✅ 发布完成: {publish_results['success']}/{publish_results['total']} 成功")
        
        # ========== 总结 ==========
        end_time = datetime.now()
        total_minutes = (end_time - start_time).total_seconds() / 60
        
        summary = {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'total_time_minutes': round(total_minutes, 1),
            'topics_count': len(topics),
            'generated_count': len(successful_contents),
            'published_count': publish_results['success'],
            'generation_results': generation_results,
            'publish_results': publish_results['results']
        }
        
        # 保存报告
        self._save_report(summary)
        
        logger.success(f"🎉 流水线完成 | 用时: {total_minutes:.1f} 分钟")
        logger.success(f"  选题: {len(topics)} → 生成: {len(successful_contents)} → 发布: {publish_results['success']}")
        
        return summary
    
    def _save_report(self, summary: Dict):
        """保存执行报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.output_dir / f'production_report_{timestamp}.json'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📄 报告已保存: {report_file}")
    
    def run_step_by_step(self, target_count: int = 5):
        """
        分步运行（用于调试）
        
        每一步都会暂停等待用户确认
        """
        logger.info("🔧 分步运行模式")
        
        # Step 1
        logger.info("Step 1: 选题机器人")
        topics = [t['title'] for t in self.topic_hunter.hunt_topics(max_topics=target_count)]
        
        print(f"\n选题结果（{len(topics)}个）：")
        for i, topic in enumerate(topics, 1):
            print(f"  {i}. {topic}")
        
        input("\n按 Enter 继续到 Step 2...")
        
        # Step 2
        logger.info("Step 2: 内容生产机器人")
        topic = topics[0]  # 只测试第一个
        
        content, qa_report = self.content_generator.generate_with_qa(topic)
        
        print(f"\n质检报告：")
        print(f"  通过: {qa_report['passed']}")
        print(f"  分数: {qa_report['score']:.2f}")
        print(f"  问题: {qa_report['issues']}")
        
        input("\n按 Enter 继续到 Step 3...")
        
        # Step 3
        logger.info("Step 3: 发布机器人")
        
        result = self.publisher.publish(
            topic=topic,
            content=content,
            stats={'word_count': len(content), 'hotels_count': 1, 'restaurants_count': 2}
        )
        
        print(f"\n发布结果：")
        print(f"  成功: {result['success']}")
        print(f"  URL: {result.get('url')}")
        
        logger.success("✅ 分步运行完成")


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='野游记三机器人流水线')
    parser.add_argument('--mode', choices=['full', 'step'], default='full', help='运行模式')
    parser.add_argument('--count', type=int, default=10, help='目标生成数量')
    parser.add_argument('--topic-time', type=int, default=20, help='选题时限（分钟）')
    parser.add_argument('--skip-topics', action='store_true', help='跳过选题（使用现有）')
    parser.add_argument('--topics-file', type=str, help='选题文件路径')
    
    args = parser.parse_args()
    
    orchestrator = ProductionOrchestrator()
    
    if args.mode == 'full':
        summary = orchestrator.run_full_pipeline(
            target_count=args.count,
            topic_time_limit=args.topic_time,
            skip_topic_hunting=args.skip_topics,
            topics_file=args.topics_file
        )
        
        print("\n" + "="*60)
        print("📊 执行总结")
        print("="*60)
        print(f"用时: {summary['total_time_minutes']} 分钟")
        print(f"选题: {summary['topics_count']} 个")
        print(f"生成: {summary['generated_count']} 篇")
        print(f"发布: {summary['published_count']} 篇")
        print("="*60)
        
    else:
        orchestrator.run_step_by_step(target_count=args.count)


if __name__ == "__main__":
    main()
