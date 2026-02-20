"""
用户偏好提取服务
从用户查询中智能提取偏好信息
"""

import re
from typing import Dict, List
from core.trip_state import UserPreferences


def extract_preferences(query: str) -> UserPreferences:
    """
    从查询中提取用户偏好
    
    Args:
        query: 用户原始查询
        
    Returns:
        结构化的用户偏好
    """
    preferences = UserPreferences()
    
    # ========== 亲子相关 ==========
    if any(kw in query for kw in ['带小孩', '亲子', '带孩子', '家庭出游', '孩子']):
        preferences.has_kids = True
        
        # 提取孩子年龄
        age_pattern = r'(\d+)岁'
        ages = re.findall(age_pattern, query)
        if ages:
            preferences.kids_ages = [int(age) for age in ages]
    
    # ========== 预算等级 ==========
    if any(kw in query for kw in ['穷游', '省钱', '经济', '便宜', '预算有限']):
        preferences.budget_level = 'low'
    elif any(kw in query for kw in ['奢华', '高端', '五星', '豪华', '不差钱']):
        preferences.budget_level = 'high'
    else:
        preferences.budget_level = 'mid'
    
    # ========== 旅行风格 ==========
    if any(kw in query for kw in ['人文', '历史', '博物馆', '古迹', '文化']):
        preferences.travel_style.append('culture')
    
    if any(kw in query for kw in ['自然', '风光', '山水', '海滩', '户外', '徒步']):
        preferences.travel_style.append('nature')
    
    if any(kw in query for kw in ['美食', '吃货', '探店', '小吃', '餐厅']):
        preferences.travel_style.append('food')
    
    if any(kw in query for kw in ['休闲', '度假', '放松', '慢节奏', '发呆']):
        preferences.travel_style.append('relax')
    
    # ========== 设备装备 ==========
    if any(kw in query for kw in ['VLOG', '拍摄', 'Pocket', '相机', '摄影']):
        preferences.equipment.append('camera')
    
    if '无人机' in query or 'drone' in query.lower():
        preferences.equipment.append('drone')
    
    # ========== 行动能力 ==========
    if any(kw in query for kw in ['老人', '腿脚不便', '轮椅', '行动不便']):
        preferences.mobility = 'limited'
    
    # ========== 饮食限制 ==========
    if '素食' in query or '吃素' in query:
        preferences.dietary.append('vegetarian')
    
    if '清真' in query or 'halal' in query.lower():
        preferences.dietary.append('halal')
    
    return preferences


def enhance_prompt_with_preferences(base_prompt: str, preferences: UserPreferences) -> str:
    """
    根据用户偏好增强 Prompt
    
    Args:
        base_prompt: 基础 Prompt
        preferences: 用户偏好
        
    Returns:
        增强后的 Prompt
    """
    enhancements = []
    
    # 亲子相关
    if preferences.has_kids:
        if preferences.kids_ages:
            ages_str = '、'.join([f'{age}岁' for age in preferences.kids_ages])
            enhancements.append(
                f"⚠️ 重要:用户带{ages_str}的孩子出行,行程安排需要特别注意:\n"
                f"- 酒店必须有亲子设施(儿童泳池、游乐区、儿童餐等)\n"
                f"- 每天行程不要超过3个景点,预留午休时间\n"
                f"- 餐厅要有儿童椅和儿童餐\n"
                f"- 避免长时间步行,建议打车或租车"
            )
        else:
            enhancements.append(
                "⚠️ 用户带小孩出行,推荐的酒店要有亲子设施,行程节奏不要太赶"
            )
    
    # 预算等级
    if preferences.budget_level == 'low':
        enhancements.append(
            "💰 预算有限,优先推荐:\n"
            "- 经济型酒店、青旅、民宿\n"
            "- 本地人常去的平价餐厅\n"
            "- 免费或低价景点\n"
            "- 公共交通出行"
        )
    elif preferences.budget_level == 'high':
        enhancements.append(
            "👑 高端出行,优先推荐:\n"
            "- 五星级酒店、奢华度假村\n"
            "- 米其林餐厅、网红高档餐厅\n"
            "- VIP体验、私人向导\n"
            "- 专车接送"
        )
    
    # 旅行风格
    if 'culture' in preferences.travel_style:
        enhancements.append(
            "🏛️ 用户偏好人文历史,多推荐:\n"
            "- 博物馆、历史遗迹\n"
            "- 老街古巷、传统建筑\n"
            "- 有故事的景点"
        )
    
    if 'food' in preferences.travel_style:
        enhancements.append(
            "🍜 用户是吃货,重点推荐:\n"
            "- 本地特色美食\n"
            "- 老字号餐厅\n"
            "- 隐藏的苍蝇小馆\n"
            "- 每顿饭都要推荐2-3个选择"
        )
    
    # 设备装备
    if 'camera' in preferences.equipment:
        enhancements.append(
            "📸 用户喜欢拍摄VLOG/摄影:\n"
            "- 标注每个景点的最佳拍摄时间和机位\n"
            "- 推荐光线好的时段\n"
            "- 提醒需要拍摄许可的地方"
        )
    
    # 行动能力
    if preferences.mobility == 'limited':
        enhancements.append(
            "♿ 行动不便,特别注意:\n"
            "- 酒店要有电梯和无障碍设施\n"
            "- 景点要有轮椅通道\n"
            "- 避免台阶多的地方\n"
            "- 安排较短的步行距离"
        )
    
    # 饮食限制
    if preferences.dietary:
        dietary_str = '、'.join(preferences.dietary)
        enhancements.append(
            f"🥗 饮食限制({dietary_str}),推荐餐厅时:\n"
            f"- 必须有对应的菜品选择\n"
            f"- 标注哪些菜符合要求"
        )
    
    # 组合增强
    if enhancements:
        enhanced_prompt = base_prompt + "\n\n## 🎯 用户偏好约束\n\n" + "\n\n".join(enhancements)
        return enhanced_prompt
    
    return base_prompt


# ========== 测试代码 ==========
if __name__ == '__main__':
    test_queries = [
        "海口3天游,带7岁和4岁两个孩子,预算5000",
        "我想去拍VLOG,找个能看海、适合写代码的地方度周末",
        "穷游云南,吃货一枚,想找小众美食",
        "带老人去北京,腿脚不便,想看历史文化"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        prefs = extract_preferences(query)
        print(f"偏好: {prefs.dict()}")
