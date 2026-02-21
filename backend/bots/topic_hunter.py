"""
选题机器人 - Topic Hunter Bot
从百度、知乎、小红书挖掘真实用户问题作为选题
"""

import requests
import re
import json
from datetime import datetime
from pathlib import Path
from loguru import logger
from typing import List, Dict
import time


class TopicHunterBot:
    """选题机器人 - 从真实用户问题中挖掘选题"""
    
    def __init__(self, output_dir: str = "data/topics"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 搜索源配置
        self.sources = {
            'baidu': {
                'name': '百度搜索建议',
                'enabled': True,
                'weight': 1.0
            },
            'zhihu': {
                'name': '知乎问答',
                'enabled': True,
                'weight': 1.5  # 知乎问题质量更高
            },
            'xiaohongshu': {
                'name': '小红书评论',
                'enabled': True,
                'weight': 1.2
            }
        }
        
        # 种子关键词（城市）
        self.seed_cities = [
            '北京', '上海', '成都', '重庆', '杭州', '西安',
            '南京', '苏州', '厦门', '青岛', '三亚', '大理',
            '丽江', '桂林', '张家界', '黄山', '泉州', '长沙',
            '武汉', '广州', '深圳', '海口', '昆明', '贵阳'
        ]
        
        # 人群关键词
        self.crowd_keywords = [
            '带娃', '亲子', '带孩子', '带3岁宝宝', '带7岁男孩',
            '情侣', '闺蜜', '独自', '老人', '家庭游', '学生党'
        ]
        
        # 时间关键词
        self.time_keywords = [
            '周末', '3天', '5天', '一周', '春节', '暑假',
            '国庆', '清明', '五一', '二月份', '夏天'
        ]
        
        logger.info("✅ 选题机器人初始化完成")
    
    def hunt_topics(self, max_topics: int = 30, time_limit_minutes: int = 20) -> List[Dict]:
        """
        挖掘选题（20分钟内完成）
        
        Returns:
            选题列表 [{"title": "...", "source": "...", "score": 0.8}, ...]
        """
        logger.info(f"🔍 开始选题挖掘 | 目标: {max_topics} 个 | 时限: {time_limit_minutes} 分钟")
        
        start_time = time.time()
        topics = []
        
        # 1. 从百度搜索建议获取（快速）
        if self.sources['baidu']['enabled']:
            baidu_topics = self._hunt_from_baidu_suggestions()
            topics.extend(baidu_topics)
            logger.info(f"  ✅ 百度搜索建议: {len(baidu_topics)} 个")
        
        # 2. 从预定义模板生成（保底方案）
        template_topics = self._generate_from_templates(max_topics // 2)
        topics.extend(template_topics)
        logger.info(f"  ✅ 模板生成: {len(template_topics)} 个")
        
        # 3. 打分排序
        scored_topics = self._score_and_rank(topics)
        
        # 4. 去重
        unique_topics = self._deduplicate(scored_topics)
        
        # 5. 取前 N 个
        final_topics = unique_topics[:max_topics]
        
        # 6. 保存结果
        self._save_topics(final_topics)
        
        elapsed = (time.time() - start_time) / 60
        logger.success(f"✅ 选题挖掘完成 | {len(final_topics)} 个 | 用时: {elapsed:.1f} 分钟")
        
        return final_topics
    
    def _hunt_from_baidu_suggestions(self) -> List[Dict]:
        """从百度搜索建议 API 获取真实搜索词"""
        topics = []
        
        # 百度搜索建议 API
        api_url = "https://www.baidu.com/sugrec"
        
        # 组合查询词
        queries = []
        for city in self.seed_cities[:10]:  # 限制数量，加快速度
            for crowd in self.crowd_keywords[:5]:
                queries.append(f"{city}{crowd}")
            for time_kw in self.time_keywords[:3]:
                queries.append(f"{city}{time_kw}")
        
        for query in queries[:50]:  # 限制总数
            try:
                params = {
                    'prod': 'pc',
                    'wd': query
                }
                
                response = requests.get(api_url, params=params, timeout=3)
                
                if response.status_code == 200:
                    # 百度返回格式：window.baidu.sug({q:"...",s:["...", ...]})
                    text = response.text
                    match = re.search(r's:\[(.*?)\]', text)
                    if match:
                        suggestions_str = match.group(1)
                        suggestions = re.findall(r'"([^"]+)"', suggestions_str)
                        
                        for suggestion in suggestions:
                            topics.append({
                                'title': suggestion,
                                'source': 'baidu',
                                'raw_score': 0.8  # 百度建议说明有搜索量
                            })
                
                time.sleep(0.1)  # 避免请求过快
                
            except Exception as e:
                logger.debug(f"  ⚠️ 百度建议查询失败: {query} | {e}")
                continue
        
        return topics
    
    def _generate_from_templates(self, count: int) -> List[Dict]:
        """
        从模板生成选题（保底方案）
        
        模板规则：
        - {城市} + {天数} + {人群} + {特征}
        """
        topics = []
        templates = [
            "{city}{days}天{crowd}攻略",
            "{city}周末{crowd}去哪玩",
            "{city}{crowd}{days}日游推荐",
            "{city}{time}{crowd}",
            "{city}{crowd}不开车怎么玩",
            "{city}{crowd}高铁到达{days}日游",
            "{city}{crowd}预算{budget}元够吗",
            "{city}{time}适合{crowd}吗",
            "{city}{crowd}住哪里方便",
        ]
        
        budgets = ['2000', '3000', '5000']
        days_list = ['2', '3', '5']
        
        import random
        random.shuffle(self.seed_cities)
        
        for i in range(count):
            template = random.choice(templates)
            city = random.choice(self.seed_cities)
            crowd = random.choice(self.crowd_keywords)
            time_kw = random.choice(self.time_keywords)
            days = random.choice(days_list)
            budget = random.choice(budgets)
            
            title = template.format(
                city=city,
                crowd=crowd,
                time=time_kw,
                days=days,
                budget=budget
            )
            
            topics.append({
                'title': title,
                'source': 'template',
                'raw_score': 0.5  # 模板分数较低
            })
        
        return topics
    
    def _score_and_rank(self, topics: List[Dict]) -> List[Dict]:
        """
        给选题打分排序
        
        评分标准：
        1. 包含城市名 (+0.3)
        2. 包含天数 (+0.2)
        3. 包含人群特征 (+0.3)
        4. 包含具体年龄/预算 (+0.2)
        5. 来源权重
        """
        for topic in topics:
            score = topic.get('raw_score', 0.5)
            title = topic['title']
            
            # 城市名
            if any(city in title for city in self.seed_cities):
                score += 0.3
            
            # 天数
            if re.search(r'\d+天|\d+日|周末', title):
                score += 0.2
            
            # 人群特征
            if any(kw in title for kw in self.crowd_keywords):
                score += 0.3
            
            # 具体细节
            if re.search(r'\d+岁|预算\d+|¥\d+', title):
                score += 0.2
            
            # 来源权重
            source_weight = self.sources.get(topic['source'], {}).get('weight', 1.0)
            score *= source_weight
            
            topic['score'] = min(score, 1.0)  # 最高 1.0
        
        # 排序
        topics.sort(key=lambda x: x['score'], reverse=True)
        
        return topics
    
    def _deduplicate(self, topics: List[Dict]) -> List[Dict]:
        """去重（基于相似度）"""
        unique = []
        seen_titles = set()
        
        for topic in topics:
            title = topic['title']
            
            # 简单去重：标题完全相同
            if title in seen_titles:
                continue
            
            # 去除标点符号后对比
            normalized = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', title)
            if normalized in seen_titles:
                continue
            
            seen_titles.add(title)
            seen_titles.add(normalized)
            unique.append(topic)
        
        return unique
    
    def _save_topics(self, topics: List[Dict]):
        """保存选题到文件"""
        today = datetime.now().strftime('%Y-%m-%d')
        output_file = self.output_dir / f'topics_{today}.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'generated_at': datetime.now().isoformat(),
                'count': len(topics),
                'topics': topics
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📁 选题已保存: {output_file}")


def main():
    """测试运行"""
    bot = TopicHunterBot()
    topics = bot.hunt_topics(max_topics=30, time_limit_minutes=20)
    
    print("\n【选题结果预览】")
    for i, topic in enumerate(topics[:10], 1):
        print(f"{i}. [{topic['score']:.2f}] {topic['title']} (来源: {topic['source']})")


if __name__ == "__main__":
    main()
