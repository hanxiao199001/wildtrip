"""
野游记内容策略引擎
三大方向：季节性、海南深度、问答型短内容
"""

from datetime import datetime, timedelta
from typing import List, Dict
from loguru import logger


class ContentStrategy:
    """内容策略引擎"""
    
    # 海南重点城市（按优先级）
    HAINAN_CITIES = [
        "海口",
        "三亚", 
        "万宁",
        "文昌",
        "陵水",
        "琼海",
        "儋州",
        "五指山"
    ]
    
    # 2026年假期（清明、五一、端午、中秋、国庆）
    HOLIDAYS_2026 = [
        {"name": "清明", "date": "2026-04-05", "days": 3, "weeks_before": 3},
        {"name": "五一", "date": "2026-05-01", "days": 5, "weeks_before": 3},
        {"name": "端午", "date": "2026-06-22", "days": 3, "weeks_before": 2},
        {"name": "中秋", "date": "2026-10-01", "days": 3, "weeks_before": 2},
        {"name": "国庆", "date": "2026-10-01", "days": 7, "weeks_before": 4},
    ]
    
    def __init__(self):
        """初始化"""
        pass
    
    # ========== 1. 季节性内容引擎 ==========
    
    def get_upcoming_holidays(self, weeks_ahead: int = 8) -> List[Dict]:
        """
        获取即将到来的假期
        
        Args:
            weeks_ahead: 提前几周
            
        Returns:
            假期列表
        """
        today = datetime.now()
        upcoming = []
        
        for holiday in self.HOLIDAYS_2026:
            holiday_date = datetime.strptime(holiday['date'], '%Y-%m-%d')
            days_until = (holiday_date - today).days
            
            # 在搜索高峰期前2-4周
            start_create = holiday['weeks_before'] * 7
            
            if 0 <= days_until <= weeks_ahead * 7:
                upcoming.append({
                    **holiday,
                    'days_until': days_until,
                    'should_create_now': days_until <= start_create
                })
        
        return upcoming
    
    def generate_holiday_queries(self, holiday: Dict, city: str) -> List[str]:
        """
        生成假期相关查询
        
        Args:
            holiday: 假期信息
            city: 城市
            
        Returns:
            查询列表
        """
        name = holiday['name']
        days = holiday['days']
        
        queries = [
            # 基础查询
            f"{name}{city}{days}天亲子游",
            f"{name}{city}{days}天自驾游",
            f"{name}{city}怎么玩",
            f"{name}去{city}人多吗",
            
            # 带老人/孩子
            f"{name}{city}带老人去哪",
            f"{name}{city}适合小孩吗",
            f"{name}{city}亲子酒店推荐",
            
            # 预算相关
            f"{name}{city}穷游攻略",
            f"{name}{city}3000元够吗",
            f"{name}{city}省钱攻略",
            
            # 天气/季节
            f"{name}{city}天气怎么样",
            f"{name}{city}下海冷不冷",
            f"{name}{city}适合游泳吗",
            
            # 避坑
            f"{name}{city}避坑指南",
            f"{name}{city}人少的地方",
            f"{name}{city}本地人推荐",
        ]
        
        return queries
    
    # ========== 2. 海南深度内容引擎 ==========
    
    def generate_hainan_deep_queries(self, city: str) -> List[str]:
        """
        生成海南深度查询（50-100个细分场景）
        
        Args:
            city: 海南城市
            
        Returns:
            查询列表
        """
        queries = []
        
        # 1. 时长维度（1-7天）
        for days in range(1, 8):
            queries.extend([
                f"{city}{days}天{days-1}晚怎么玩",
                f"{city}{days}日游攻略",
                f"{city}{days}天够吗",
            ])
        
        # 2. 人群维度
        demographics = [
            "亲子游", "带老人", "情侣", "闺蜜", "独自", "学生党", "穷游"
        ]
        for demo in demographics:
            queries.extend([
                f"{city}{demo}攻略",
                f"{city}适合{demo}吗",
                f"{city}{demo}酒店推荐",
                f"{city}{demo}美食推荐",
            ])
        
        # 3. 预算维度
        budgets = [1000, 2000, 3000, 5000, 10000]
        for budget in budgets:
            queries.extend([
                f"{city}预算{budget}元",
                f"{city}{budget}元够吗",
                f"{city}{budget}元怎么玩",
            ])
        
        # 4. 主题维度
        themes = [
            "美食", "海鲜", "海滩", "潜水", "冲浪", "温泉", "骑行", 
            "徒步", "露营", "民宿", "五星酒店", "本地生活"
        ]
        for theme in themes:
            queries.extend([
                f"{city}{theme}攻略",
                f"{city}{theme}推荐",
                f"{city}哪里{theme}好",
            ])
        
        # 5. 季节维度
        seasons = ["春节", "暑假", "冬天", "夏天", "淡季", "旺季"]
        for season in seasons:
            queries.extend([
                f"{city}{season}怎么样",
                f"{city}{season}去合适吗",
                f"{city}{season}人多吗",
            ])
        
        # 6. 交通/住宿
        queries.extend([
            f"{city}住哪里方便",
            f"{city}市区住还是海边住",
            f"{city}机场到市区怎么走",
            f"{city}租车划算吗",
            f"{city}打车贵不贵",
        ])
        
        # 7. 避坑/省钱
        queries.extend([
            f"{city}避坑指南",
            f"{city}旅游陷阱",
            f"{city}本地人推荐",
            f"{city}省钱攻略",
            f"{city}免费景点",
        ])
        
        return queries
    
    # ========== 3. 问答型短内容引擎 ==========
    
    def generate_qa_queries(self, city: str) -> List[Dict]:
        """
        生成问答型查询（500-800字）
        
        Args:
            city: 城市
            
        Returns:
            问答列表 [{'question': ..., 'type': ...}]
        """
        qa_list = []
        
        # 1. 天气/季节类
        qa_list.extend([
            {"question": f"{city}二月份下海冷不冷", "type": "weather"},
            {"question": f"{city}几月份去最好", "type": "weather"},
            {"question": f"{city}夏天热不热", "type": "weather"},
            {"question": f"{city}冬天冷吗", "type": "weather"},
        ])
        
        # 2. 比较类
        if city == "三亚":
            qa_list.extend([
                {"question": "三亚湾和亚龙湾哪个适合带小孩", "type": "compare"},
                {"question": "三亚海棠湾和亚龙湾哪个好", "type": "compare"},
                {"question": "三亚大东海和三亚湾哪个好玩", "type": "compare"},
            ])
        
        if city == "万宁":
            qa_list.extend([
                {"question": "万宁日月湾几月份浪最小", "type": "specific"},
                {"question": "万宁神州半岛和石梅湾哪个好", "type": "compare"},
            ])
        
        # 3. 价格/费用类
        qa_list.extend([
            {"question": f"{city}旅游花费大概多少", "type": "budget"},
            {"question": f"{city}吃饭贵不贵", "type": "budget"},
            {"question": f"{city}海鲜多少钱一斤", "type": "budget"},
            {"question": f"{city}酒店一晚多少钱", "type": "budget"},
        ])
        
        # 4. 时间/时长类
        qa_list.extend([
            {"question": f"{city}玩几天合适", "type": "duration"},
            {"question": f"{city}3天够吗", "type": "duration"},
            {"question": f"{city}一天能玩完吗", "type": "duration"},
        ])
        
        # 5. 推荐类
        qa_list.extend([
            {"question": f"{city}必去景点有哪些", "type": "recommend"},
            {"question": f"{city}有什么好吃的", "type": "recommend"},
            {"question": f"{city}本地人去哪吃", "type": "recommend"},
            {"question": f"{city}小众景点推荐", "type": "recommend"},
        ])
        
        # 6. 是否类
        qa_list.extend([
            {"question": f"{city}值得去吗", "type": "yesno"},
            {"question": f"{city}适合亲子游吗", "type": "yesno"},
            {"question": f"{city}人多吗", "type": "yesno"},
            {"question": f"{city}需要提前订酒店吗", "type": "yesno"},
        ])
        
        return qa_list
    
    # ========== 内容优先级规划 ==========
    
    def get_priority_tasks(self) -> Dict:
        """
        获取优先级任务
        
        Returns:
            任务字典
        """
        tasks = {
            "urgent": [],  # 紧急（2周内假期）
            "high": [],    # 高优先级（1个月内假期 + 海南深度）
            "medium": [],  # 中优先级（问答型）
            "low": []      # 低优先级（其他城市）
        }
        
        # 1. 季节性紧急任务
        upcoming = self.get_upcoming_holidays(weeks_ahead=8)
        for holiday in upcoming:
            if holiday['should_create_now']:
                # 海南城市
                for city in self.HAINAN_CITIES[:3]:  # 前3个城市
                    queries = self.generate_holiday_queries(holiday, city)
                    tasks['urgent'].extend([
                        {'query': q, 'city': city, 'type': 'holiday', 'holiday': holiday['name']}
                        for q in queries[:5]  # 每个城市5个查询
                    ])
        
        # 2. 海南深度内容（高优先级）
        for city in self.HAINAN_CITIES[:2]:  # 海口、三亚
            queries = self.generate_hainan_deep_queries(city)
            tasks['high'].extend([
                {'query': q, 'city': city, 'type': 'deep'}
                for q in queries[:30]  # 每个城市30个
            ])
        
        # 3. 问答型短内容（中优先级）
        for city in self.HAINAN_CITIES[:3]:
            qa_list = self.generate_qa_queries(city)
            tasks['medium'].extend([
                {'query': qa['question'], 'city': city, 'type': 'qa', 'qa_type': qa['type']}
                for qa in qa_list[:20]  # 每个城市20个
            ])
        
        return tasks
    
    def print_strategy(self):
        """打印内容策略"""
        print("\n" + "="*60)
        print("📝 野游记内容策略")
        print("="*60)
        
        # 1. 即将到来的假期
        print("\n🎉 即将到来的假期:")
        upcoming = self.get_upcoming_holidays(weeks_ahead=12)
        for holiday in upcoming:
            status = "🔥 现在创作!" if holiday['should_create_now'] else "⏳ 等待中"
            print(f"   {holiday['name']} ({holiday['date']}) - {holiday['days_until']}天后 - {status}")
        
        # 2. 优先级任务
        print("\n🎯 内容优先级:")
        tasks = self.get_priority_tasks()
        print(f"   🔴 紧急 (季节性): {len(tasks['urgent'])} 个查询")
        print(f"   🟠 高优先级 (海南深度): {len(tasks['high'])} 个查询")
        print(f"   🟡 中优先级 (问答型): {len(tasks['medium'])} 个查询")
        
        # 3. 示例查询
        if tasks['urgent']:
            print("\n🔥 紧急查询示例:")
            for task in tasks['urgent'][:5]:
                print(f"   - {task['query']} ({task['city']})")
        
        if tasks['high']:
            print("\n🌴 海南深度查询示例:")
            for task in tasks['high'][:5]:
                print(f"   - {task['query']} ({task['city']})")
        
        if tasks['medium']:
            print("\n❓ 问答型查询示例:")
            for task in tasks['medium'][:5]:
                print(f"   - {task['query']} ({task['city']})")
        
        print("\n" + "="*60)


def main():
    """主函数"""
    strategy = ContentStrategy()
    strategy.print_strategy()


if __name__ == '__main__':
    main()
