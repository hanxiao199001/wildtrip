"""
每日生产任务 - Daily Production
每天生产 15 篇高质量长尾攻略（海南本地优先）
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# 🔥 加载 .env 配置文件
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

from loguru import logger
from datetime import datetime
import json

from bots.topic_hunter import TopicHunterBot
from bots.content_generator import ContentGeneratorBot
from bots.publisher import PublisherBot


class DailyProductionBot:
    """每日生产机器人 - 15 篇高质量攻略"""
    
    def __init__(self):
        self.topic_hunter = TopicHunterBot()
        self.content_generator = ContentGeneratorBot()
        self.publisher = PublisherBot()
        
        # 每日目标
        self.daily_target = 15
        
        # 🔥 海南本地优先配置
        self.hainan_cities = [
            '海口', '三亚', '万宁', '文昌', '琼海',
            '陵水', '保亭', '五指山', '儋州', '东方'
        ]
        
        # 🔥 高质量长尾关键词（极其具体）
        self.high_quality_keywords = {
            '年龄段': ['3岁宝宝', '7岁男孩', '8岁小孩', '小学生', '学龄前'],
            '时间': ['周末', '过年期间', '春节', '寒假', '暑假'],
            '场景': ['不晒', '不开车', '冲浪', '参观', '不涨价'],
            '地点': ['日月湾', '航天发射场', '骑楼老街', '假日海滩', '免税店'],
            '问题': ['安全吗', '怎么玩', '去哪', '哪些', '攻略']
        }
        
        logger.info("✅ 每日生产机器人初始化完成 | 目标: 15 篇/天")
    
    def generate_today_topics(self) -> list:
        """
        生成今日 15 个选题（海南本地 + 高质量长尾）
        
        策略：
        1. 手动种子选题（5 个）
        2. 百度搜索建议（5 个）
        3. 模板生成（5 个备用）
        """
        logger.info("📋 生成今日选题...")
        
        topics = []
        
        # ========== 1. 手动种子选题（你提供的示例）==========
        seed_topics = [
            "海口带3岁宝宝周末去哪不晒",
            "三亚不开车怎么玩3天亲子游",
            "万宁日月湾冲浪带8岁小孩安全吗",
            "海口过年期间哪些餐厅不涨价",
            "文昌航天发射场带小学生参观攻略"
        ]
        
        for topic in seed_topics:
            topics.append({
                'title': topic,
                'source': 'manual',
                'score': 1.0  # 手动选题最高分
            })
        
        logger.info(f"  ✅ 手动种子选题: {len(seed_topics)} 个")
        
        # ========== 2. 从百度搜索建议获取（5 个）==========
        baidu_topics = self._hunt_hainan_topics_from_baidu(count=5)
        topics.extend(baidu_topics)
        logger.info(f"  ✅ 百度搜索建议: {len(baidu_topics)} 个")
        
        # ========== 3. 高质量模板生成（5 个备用）==========
        template_topics = self._generate_high_quality_templates(count=5)
        topics.extend(template_topics)
        logger.info(f"  ✅ 模板生成: {len(template_topics)} 个")
        
        # 去重 + 排序
        unique_topics = self._deduplicate(topics)
        final_topics = unique_topics[:15]
        
        logger.success(f"✅ 今日选题完成: {len(final_topics)} 个")
        
        # 保存选题
        self._save_daily_topics(final_topics)
        
        return final_topics
    
    def _hunt_hainan_topics_from_baidu(self, count: int = 5) -> list:
        """从百度搜索建议获取海南相关选题"""
        import requests
        import time
        
        topics = []
        api_url = "https://www.baidu.com/sugrec"
        
        # 组合查询词（海南城市 + 长尾关键词）
        queries = []
        for city in self.hainan_cities[:5]:  # 限制城市数量
            for age in self.high_quality_keywords['年龄段'][:2]:
                queries.append(f"{city}{age}")
            for scene in self.high_quality_keywords['场景'][:2]:
                queries.append(f"{city}{scene}")
        
        for query in queries[:20]:  # 限制总数
            try:
                params = {'prod': 'pc', 'wd': query}
                response = requests.get(api_url, params=params, timeout=3)
                
                if response.status_code == 200:
                    import re
                    text = response.text
                    match = re.search(r's:\[(.*?)\]', text)
                    if match:
                        suggestions_str = match.group(1)
                        suggestions = re.findall(r'"([^"]+)"', suggestions_str)
                        
                        for suggestion in suggestions:
                            # 过滤：只保留海南相关
                            if any(city in suggestion for city in self.hainan_cities):
                                topics.append({
                                    'title': suggestion,
                                    'source': 'baidu',
                                    'score': 0.9
                                })
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.debug(f"  ⚠️ 百度查询失败: {query}")
                continue
        
        return topics[:count]
    
    def _generate_high_quality_templates(self, count: int = 5) -> list:
        """
        生成高质量模板选题（极其具体）
        
        模板规则：
        {城市} + {年龄段} + {时间} + {场景} + {问题}
        """
        import random
        
        topics = []
        
        templates = [
            "{city}带{age}{time}{scene}",
            "{city}{age}{scene}{question}",
            "{city}{time}{location}{question}",
            "{city}{scene}怎么玩{age}",
            "{city}{location}适合{age}吗",
        ]
        
        for i in range(count):
            template = random.choice(templates)
            
            title = template.format(
                city=random.choice(self.hainan_cities),
                age=random.choice(self.high_quality_keywords['年龄段']),
                time=random.choice(self.high_quality_keywords['时间']),
                scene=random.choice(self.high_quality_keywords['场景']),
                location=random.choice(self.high_quality_keywords['地点']),
                question=random.choice(self.high_quality_keywords['问题'])
            )
            
            topics.append({
                'title': title,
                'source': 'template',
                'score': 0.8
            })
        
        return topics
    
    def _deduplicate(self, topics: list) -> list:
        """去重（基于标题）"""
        import re
        
        unique = []
        seen = set()
        
        for topic in topics:
            title = topic['title']
            normalized = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', title)
            
            if normalized not in seen:
                seen.add(normalized)
                unique.append(topic)
        
        # 按分数排序
        unique.sort(key=lambda x: x['score'], reverse=True)
        
        return unique
    
    def _save_daily_topics(self, topics: list):
        """保存今日选题"""
        today = datetime.now().strftime('%Y-%m-%d')
        output_dir = Path(__file__).parent.parent / 'data' / 'daily_topics'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f'topics_{today}.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'date': today,
                'count': len(topics),
                'topics': topics
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📁 今日选题已保存: {output_file}")
    
    def run_daily_production(self):
        """
        执行每日生产任务
        
        Steps:
        1. 生成 15 个选题
        2. 逐个生成 + 质检
        3. 发布
        
        Returns:
            执行报告
        """
        logger.info("🚀 开始每日生产任务...")
        start_time = datetime.now()
        
        # Step 1: 生成选题
        topics = self.generate_today_topics()
        
        # Step 2: 生成内容 + 质检
        logger.info("📝 开始内容生产...")
        
        results = []
        for i, topic in enumerate(topics, 1):
            logger.info(f"  [{i}/{len(topics)}] {topic['title']}")
            
            try:
                content, qa_report = self.content_generator.generate_with_qa(topic['title'])
                
                if qa_report['passed']:
                    logger.success(f"    ✅ 质检通过 | 分数: {qa_report['score']:.2f}")
                    
                    # 发布
                    publish_result = self.publisher.publish(
                        topic=topic['title'],
                        content=content,
                        stats={
                            'word_count': len(content),
                            'hotels_count': content.count('住宿推荐'),
                            'restaurants_count': content.count('餐厅'),
                            'total_cashback': 0
                        }
                    )
                    
                    results.append({
                        'topic': topic['title'],
                        'success': True,
                        'qa_score': qa_report['score'],
                        'url': publish_result.get('url')
                    })
                    
                else:
                    logger.warning(f"    ⚠️ 质检未通过 | 分数: {qa_report['score']:.2f}")
                    results.append({
                        'topic': topic['title'],
                        'success': False,
                        'qa_score': qa_report['score'],
                        'issues': qa_report['issues']
                    })
                    
            except Exception as e:
                logger.error(f"    ❌ 生成失败: {e}")
                results.append({
                    'topic': topic['title'],
                    'success': False,
                    'error': str(e)
                })
        
        # 统计
        success_count = sum(1 for r in results if r['success'])
        end_time = datetime.now()
        total_minutes = (end_time - start_time).total_seconds() / 60
        
        # 保存报告
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'total_time_minutes': round(total_minutes, 1),
            'target': self.daily_target,
            'success': success_count,
            'failed': len(results) - success_count,
            'results': results
        }
        
        self._save_daily_report(report)
        
        logger.success(f"✅ 每日生产完成 | {success_count}/{self.daily_target} 成功 | 用时: {total_minutes:.1f} 分钟")
        
        return report
    
    def _save_daily_report(self, report: dict):
        """保存每日报告"""
        today = datetime.now().strftime('%Y-%m-%d')
        output_dir = Path(__file__).parent.parent / 'data' / 'daily_reports'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f'report_{today}.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📄 每日报告已保存: {output_file}")


def main():
    """命令行入口"""
    bot = DailyProductionBot()
    
    # 预览今日选题
    print("\n" + "="*60)
    print("📋 今日选题预览")
    print("="*60)
    
    topics = bot.generate_today_topics()
    
    for i, topic in enumerate(topics, 1):
        source_emoji = {
            'manual': '✍️',
            'baidu': '🔍',
            'template': '📝'
        }.get(topic['source'], '❓')
        
        print(f"{i:2d}. {source_emoji} [{topic['score']:.1f}] {topic['title']}")
    
    print("\n" + "="*60)
    
    # 询问是否继续
    choice = input("\n是否开始生产？(y/n): ").strip().lower()
    
    if choice == 'y':
        report = bot.run_daily_production()
        
        print("\n" + "="*60)
        print("📊 执行总结")
        print("="*60)
        print(f"成功: {report['success']}/{report['target']} 篇")
        print(f"用时: {report['total_time_minutes']} 分钟")
        print("="*60)
    else:
        print("\n已取消")


if __name__ == "__main__":
    main()
