"""
野游记内容策略 V2.0
从"水文SEO"到"深度价值内容"
"""

from typing import List, Dict


class ContentStrategyV2:
    """高质量内容策略"""
    
    # 海南重点城市
    HAINAN_CITIES = ["海口", "三亚", "万宁", "文昌", "陵水"]
    
    def __init__(self):
        pass
    
    # ========== 深度场景化内容 ==========
    
    def generate_deep_scenario_queries(self, city: str) -> List[str]:
        """
        生成深度场景化查询
        每个都是3000-5000字的完整攻略
        
        特点：
        - 具体场景
        - 明确预算
        - 真实POI
        - 可执行行程
        """
        queries = []
        
        # 1. 时长 x 人群 x 预算 (高价值组合)
        durations = [2, 3, 5]
        demographics = [
            ("亲子游", "带5岁小孩"),
            ("情侣游", "第一次来"),
            ("闺蜜游", "2个女生"),
            ("带父母", "60岁以上"),
        ]
        budgets = [3000, 5000, 10000]
        
        for days in durations:
            for demo, detail in demographics:
                for budget in budgets:
                    queries.append(
                        f"{city}{days}天{demo}{detail}预算{budget}元行程攻略"
                    )
        
        # 2. 主题深度游 (垂直场景)
        themes = [
            "海鲜美食", "冲浪体验", "温泉度假", "骑行环岛",
            "潜水考证", "高尔夫", "民宿体验", "本地市集"
        ]
        
        for theme in themes:
            queries.extend([
                f"{city}{theme}3天深度体验攻略",
                f"{city}{theme}周末2天1晚路线",
                f"{city}{theme}推荐地点和价格"
            ])
        
        # 3. 特定需求场景 (痛点解决)
        special_needs = [
            "第一次来海南不知道怎么玩",
            "不想去景点只想像本地人生活",
            "预算有限怎么玩得好",
            "带老人行动不便怎么安排",
            "小孩3岁只能玩沙不能下海",
            "只有周末2天从北京出发",
            "冬天避寒住1个月",
            "夏天暑假带孩子玩水"
        ]
        
        for need in special_needs:
            queries.append(f"{city}{need}")
        
        return queries
    
    # ========== 对比决策类内容 ==========
    
    def generate_comparison_queries(self, city: str) -> List[str]:
        """
        生成对比决策类查询
        帮用户做选择,深度分析
        """
        queries = []
        
        if city == "三亚":
            queries.extend([
                "三亚亚龙湾vs海棠湾vs三亚湾哪个适合亲子游详细对比",
                "三亚住海棠湾好还是亚龙湾好预算5000元",
                "三亚免税店和海棠湾免税城哪个更值得去",
                "三亚蜈支洲岛和西岛哪个更适合潜水",
            ])
        
        if city == "海口":
            queries.extend([
                "海口假日海滩vs西秀海滩vs海口湾哪个更好",
                "海口住骑楼老街附近还是海边酒店",
                "海口火山口公园vs热带植物园哪个值得去",
            ])
        
        if city == "万宁":
            queries.extend([
                "万宁日月湾vs石梅湾vs神州半岛怎么选",
                "万宁冲浪新手去哪个海滩比较好",
            ])
        
        return queries
    
    # ========== 季节性深度内容 ==========
    
    def generate_seasonal_deep_queries(self, city: str, season: str) -> List[str]:
        """
        生成季节性深度内容
        不是简单的"几月份去最好",而是深度场景
        """
        queries = []
        
        # 不再是: "海口二月份下海冷不冷"
        # 而是: "海口二月份亲子游3天攻略天气+穿衣+行程"
        
        if season == "冬季":
            queries.extend([
                f"{city}12月-2月避寒游5天攻略老人带小孩",
                f"{city}春节7天攻略人少景点+民宿推荐",
                f"{city}元旦3天怎么玩预算3000元",
            ])
        
        elif season == "夏季":
            queries.extend([
                f"{city}暑假带孩子玩水7天攻略+防晒指南",
                f"{city}7-8月避暑游误区和正确玩法",
                f"{city}夏天淡季酒店性价比推荐",
            ])
        
        return queries
    
    # ========== 人文历史深度游 ==========
    
    def generate_cultural_history_queries(self, city: str) -> List[str]:
        """
        生成人文历史深度游查询
        特点：
        - 历史文化底蕴
        - 名人故事
        - 文化遗产
        - 深度体验
        """
        queries = []
        
        # 海南人文历史主题
        if city == "海口":
            queries.extend([
                "苏东坡被贬海南路线深度游-从儋州到东坡书院",
                "海口骑楼老街人文历史3天深度游-南洋文化探访",
                "海瑞故里与清官文化-海口人文历史一日游",
                "海南侨乡文化深度游-文昌骑楼与归国华侨故事",
                "琼台书院与海南文脉-海口古代教育史探访"
            ])
        
        if city == "三亚":
            queries.extend([
                "鉴真东渡与南山寺-三亚佛教文化深度游",
                "黎族苗族文化村落-三亚少数民族文化体验3天",
                "崖州古城历史文化-三亚千年古城深度游",
                "海上丝绸之路遗迹-三亚港口贸易历史探访"
            ])
        
        if city == "文昌":
            queries.extend([
                "宋氏三姐妹与文昌名人-近代历史人文游",
                "文昌航天文化与科技史-从古文化到现代航天",
                "海南文昌孔庙与儒家文化-古代教育史深度游"
            ])
        
        if city == "儋州":
            queries.extend([
                "苏东坡被贬儋州3年轨迹-东坡文化深度游",
                "千年古盐田与盐业文化-儋州历史产业探访",
                "东坡书院与儋州文化-历史名人足迹深度体验"
            ])
        
        return queries
    
    # ========== 本地生活类内容 ==========
    
    def generate_local_lifestyle_queries(self, city: str) -> List[str]:
        """
        生成本地生活类查询
        深度本地化,野路子
        """
        queries = [
            f"{city}本地人周末去哪玩不去景点",
            f"{city}本地人早餐吃什么在哪吃",
            f"{city}本地人买海鲜去哪个市场",
            f"{city}夜市摊位推荐本地人的选择",
            f"{city}菜市场攻略本地人带你逛",
            f"{city}公园晨练跑步骑行路线本地推荐",
            f"{city}小众咖啡馆书店本地人的秘密基地",
            f"{city}像本地人一样生活1周攻略",
        ]
        
        return queries
    
    def get_priority_tasks(self) -> Dict:
        """
        获取高质量优先级任务
        
        Returns:
            任务字典
        """
        tasks = {
            "high": [],    # 深度场景化 (3000-5000字)
            "medium": [],  # 对比决策 (2000-3000字)
            "low": []      # 本地生活 (1500-2500字)
        }
        
        # 海口 + 三亚优先
        for city in ["海口", "三亚"]:
            # 深度场景
            deep_queries = self.generate_deep_scenario_queries(city)
            tasks['high'].extend([
                {'query': q, 'city': city, 'type': 'deep_scenario', 'target_words': 4000}
                for q in deep_queries[:20]  # 每个城市20个
            ])
            
            # 人文历史深度游 (新增,高优先级)
            cultural_queries = self.generate_cultural_history_queries(city)
            tasks['high'].extend([
                {'query': q, 'city': city, 'type': 'cultural_history', 'target_words': 4000}
                for q in cultural_queries[:5]  # 每个城市5个
            ])
            
            # 对比决策
            comp_queries = self.generate_comparison_queries(city)
            tasks['medium'].extend([
                {'query': q, 'city': city, 'type': 'comparison', 'target_words': 2500}
                for q in comp_queries
            ])
            
            # 本地生活
            local_queries = self.generate_local_lifestyle_queries(city)
            tasks['low'].extend([
                {'query': q, 'city': city, 'type': 'local_lifestyle', 'target_words': 2000}
                for q in local_queries[:10]
            ])
        
        return tasks
    
    def print_strategy(self):
        """打印内容策略"""
        print("\n" + "="*60)
        print("📝 野游记内容策略 V2.0 - 深度价值内容")
        print("="*60)
        
        tasks = self.get_priority_tasks()
        
        print(f"\n🎯 内容优先级:")
        print(f"   🔴 高优先级 (深度场景): {len(tasks['high'])} 个查询")
        print(f"   🟠 中优先级 (对比决策): {len(tasks['medium'])} 个查询")
        print(f"   🟡 低优先级 (本地生活): {len(tasks['low'])} 个查询")
        
        print(f"\n🔥 高优先级示例 (3000-5000字深度攻略):")
        for task in tasks['high'][:5]:
            print(f"   - {task['query']}")
        
        print(f"\n⚖️  中优先级示例 (2000-3000字对比分析):")
        for task in tasks['medium'][:5]:
            print(f"   - {task['query']}")
        
        print(f"\n🌴 低优先级示例 (1500-2500字本地生活):")
        for task in tasks['low'][:5]:
            print(f"   - {task['query']}")
        
        print("\n" + "="*60)


def main():
    """主函数"""
    strategy = ContentStrategyV2()
    strategy.print_strategy()


if __name__ == '__main__':
    main()
