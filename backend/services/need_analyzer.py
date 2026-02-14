"""
野游记 - 智能需求分析器
提取用户输入中的结构化信息
"""

import re
from typing import Dict, List, Optional
from anthropic import Anthropic
import os

class NeedAnalyzer:
    """智能需求分析"""
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    def analyze(self, user_input: str) -> Dict:
        """
        分析用户需求，提取结构化信息
        
        Args:
            user_input: 用户输入的原始文本
            
        Returns:
            {
                "destination": "海口",
                "days": 3,
                "budget": 5000,
                "travelers": {"adults": 2, "kids": 1, "kids_ages": [5]},
                "preferences": ["海边", "亲子"],
                "dates": "2026-02-08",
                "missing": ["budget"]  // 缺失的关键信息
            }
        """
        
        system_prompt = """你是旅游需求分析专家。从用户输入中提取以下信息：

1. destination (目的地城市)
2. days (游玩天数)
3. budget (预算金额，单位元)
4. travelers (同行人信息)
   - adults: 成人数量
   - kids: 儿童数量
   - kids_ages: 儿童年龄列表
5. preferences (偏好标签，如：海滩、美食、亲子、文化等)
6. dates (出发日期，格式YYYY-MM-DD)

规则：
- 如果信息明确，提取出来
- 如果信息缺失，对应字段返回null
- missing字段列出所有缺失的【关键信息】（destination/days/budget必须有）
- preferences尽量多提取，哪怕是隐含的（如"带孩子"→亲子）

返回JSON格式，不要其他文字。"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4",
                max_tokens=1024,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_input
                }]
            )
            
            # 解析Claude返回的JSON
            import json
            result = json.loads(response.content[0].text)
            
            # 确保missing字段存在
            if 'missing' not in result:
                result['missing'] = []
                
            return result
            
        except Exception as e:
            # 降级方案：简单正则提取
            return self._simple_extract(user_input)
    
    def _simple_extract(self, text: str) -> Dict:
        """降级方案：简单正则提取"""
        result = {
            "destination": None,
            "days": None,
            "budget": None,
            "travelers": {"adults": None, "kids": None, "kids_ages": []},
            "preferences": [],
            "dates": None,
            "missing": []
        }
        
        # 提取目的地（常见城市）
        cities = ["海口", "三亚", "北京", "上海", "广州", "深圳", "杭州", "成都", "西安", "重庆"]
        for city in cities:
            if city in text:
                result["destination"] = city
                break
        
        # 提取天数
        days_match = re.search(r'(\d+)天', text)
        if days_match:
            result["days"] = int(days_match.group(1))
        
        # 提取预算
        budget_match = re.search(r'(\d+)块|(\d+)元|预算(\d+)', text)
        if budget_match:
            result["budget"] = int(budget_match.group(1) or budget_match.group(2) or budget_match.group(3))
        
        # 提取人数
        adults_match = re.search(r'(\d+)大', text)
        kids_match = re.search(r'(\d+)小', text)
        if adults_match:
            result["travelers"]["adults"] = int(adults_match.group(1))
        if kids_match:
            result["travelers"]["kids"] = int(kids_match.group(1))
        
        # 提取偏好
        if "海" in text or "海边" in text or "海景" in text:
            result["preferences"].append("海滩")
        if "孩子" in text or "小孩" in text or "宝宝" in text:
            result["preferences"].append("亲子")
        if "美食" in text or "吃" in text:
            result["preferences"].append("美食")
        
        # 检查缺失
        if not result["destination"]:
            result["missing"].append("destination")
        if not result["days"]:
            result["missing"].append("days")
        if not result["budget"]:
            result["missing"].append("budget")
        
        return result
    
    def generate_follow_up(self, analysis: Dict) -> Optional[str]:
        """
        根据分析结果生成补充提问
        
        Args:
            analysis: analyze()的返回结果
            
        Returns:
            补充问题文本，如果信息齐全则返回None
        """
        
        missing = analysis.get('missing', [])
        
        if not missing:
            return None  # 信息齐全，不需要问
        
        questions = []
        
        if 'destination' in missing:
            questions.append("去哪个城市玩？")
        
        if 'days' in missing:
            questions.append("玩几天？")
        
        if 'budget' in missing:
            questions.append("预算大概多少？（说个范围也行）")
        
        # 非关键信息，温柔地问
        travelers = analysis.get('travelers', {})
        if not travelers.get('kids_ages') and travelers.get('kids'):
            questions.append("顺便问一下，孩子多大？（方便推荐合适的景点）")
        
        if len(questions) == 0:
            return None
        
        # 组合问题
        if len(questions) == 1:
            return f"收到！{questions[0]}"
        else:
            return f"收到！顺便问一下：\n" + "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions))


# 使用示例
if __name__ == "__main__":
    analyzer = NeedAnalyzer()
    
    # 测试1：信息完整
    result1 = analyzer.analyze("下周末带老婆和5岁儿子去海口玩3天，预算5000，想住海边")
    print("测试1（信息完整）:")
    print(result1)
    print("补充提问:", analyzer.generate_follow_up(result1))
    print()
    
    # 测试2：信息缺失
    result2 = analyzer.analyze("海口3天亲子游")
    print("测试2（信息缺失）:")
    print(result2)
    print("补充提问:", analyzer.generate_follow_up(result2))
