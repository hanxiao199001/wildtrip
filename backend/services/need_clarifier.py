"""
野游记 - 需求澄清服务
智能分析用户输入，生成选择题补充缺失信息
"""

import re
from typing import Dict, List, Any


class NeedClarifier:
    """需求澄清器 - 分析用户输入并生成补充问题"""

    # 常见城市列表
    CITIES = [
        "海口", "三亚", "成都", "重庆", "西安", "北京", "上海", "杭州",
        "南京", "苏州", "广州", "深圳", "厦门", "青岛", "大连", "长沙",
        "武汉", "天津", "郑州", "沈阳", "哈尔滨", "昆明", "贵阳", "福州",
        "济南", "合肥", "南昌", "太原", "石家庄", "兰州", "银川", "西宁",
        "拉萨", "呼和浩特", "乌鲁木齐", "桂林", "丽江", "大理", "张家界",
        "黄山", "九寨沟", "洛阳", "开封", "敦煌", "香格里拉", "凤凰古城",
        "平遥", "泰山", "峨眉山", "乐山", "宜昌", "北海", "珠海", "东莞",
        "佛山", "无锡", "常州", "扬州", "泉州", "烟台", "威海", "秦皇岛"
    ]

    # 问题模板库
    QUESTION_TEMPLATES = {
        "budget": {
            "id": "budget",
            "question": "预算范围？",
            "type": "single_choice",
            "required": True,
            "options": [
                {"value": "budget_low", "label": "穷游省钱", "icon": "💰", "description": "人均¥500-1500"},
                {"value": "budget_mid", "label": "舒适出行", "icon": "💎", "description": "人均¥1500-4000"},
                {"value": "budget_high", "label": "品质享受", "icon": "👑", "description": "人均¥4000+"},
            ]
        },
        "people": {
            "id": "people",
            "question": "几个人出行？",
            "type": "single_choice",
            "required": True,
            "options": [
                {"value": "solo", "label": "一个人", "icon": "🧑", "description": "独自旅行"},
                {"value": "couple", "label": "两人同行", "icon": "👫", "description": "情侣/朋友"},
                {"value": "family", "label": "家庭出游", "icon": "👨‍👩‍👧‍👦", "description": "3-5人带小孩"},
                {"value": "group", "label": "多人团体", "icon": "👥", "description": "5人以上"},
            ]
        },
        "accommodation": {
            "id": "accommodation",
            "question": "住宿偏好？",
            "type": "single_choice",
            "required": False,
            "options": [
                {"value": "budget_hotel", "label": "经济型", "icon": "🏠", "description": "快捷酒店/青旅"},
                {"value": "comfort_hotel", "label": "舒适型", "icon": "🏨", "description": "品牌连锁酒店"},
                {"value": "luxury_hotel", "label": "高端型", "icon": "🏰", "description": "五星级/度假酒店"},
                {"value": "homestay", "label": "特色民宿", "icon": "🏡", "description": "体验当地生活"},
            ]
        },
        "food_preference": {
            "id": "food_preference",
            "question": "美食偏好？",
            "type": "single_choice",
            "required": False,
            "options": [
                {"value": "local", "label": "本地特色", "icon": "🍜", "description": "地道小吃老字号"},
                {"value": "diverse", "label": "什么都吃", "icon": "🍽️", "description": "各种都想试试"},
                {"value": "light", "label": "清淡为主", "icon": "🥗", "description": "不太能吃辣/油腻"},
            ]
        },
        "travel_style": {
            "id": "travel_style",
            "question": "玩法偏好？",
            "type": "single_choice",
            "required": False,
            "options": [
                {"value": "culture", "label": "人文历史", "icon": "🏛️", "description": "博物馆/古迹/文化"},
                {"value": "nature", "label": "自然风光", "icon": "🏔️", "description": "山水/海滩/户外"},
                {"value": "food_tour", "label": "美食探店", "icon": "🍲", "description": "以吃为主的旅行"},
                {"value": "relax", "label": "休闲度假", "icon": "🧘", "description": "不赶行程，慢慢逛"},
            ]
        },
        "days": {
            "id": "days",
            "question": "玩几天？",
            "type": "single_choice",
            "required": True,
            "options": [
                {"value": "1", "label": "1天", "icon": "📅", "description": "一日游"},
                {"value": "2-3", "label": "2-3天", "icon": "🗓️", "description": "周末短途"},
                {"value": "4-5", "label": "4-5天", "icon": "📆", "description": "小长假"},
                {"value": "6+", "label": "6天以上", "icon": "🌍", "description": "深度长线游"},
            ]
        },
    }

    def analyze_need(self, query: str) -> Dict[str, Any]:
        """
        分析用户需求，返回需要澄清的问题

        Args:
            query: 用户原始输入

        Returns:
            {
                "original_query": "海口3天亲子游",
                "detected": {"destination": "海口", "days": 3, ...},
                "questions": [...],  # 需要用户回答的问题
                "need_clarify": True/False
            }
        """
        detected = self._extract_info(query)
        questions = self._generate_questions(detected, query)

        return {
            "original_query": query,
            "detected": detected,
            "questions": questions,
            "need_clarify": len(questions) > 0
        }

    def _extract_info(self, query: str) -> Dict[str, Any]:
        """从用户输入中提取已有信息"""
        info = {
            "destination": None,
            "days": None,
            "budget": None,
            "people_type": None,
            "has_kids": False,
            "preferences": []
        }

        # 提取目的地
        for city in self.CITIES:
            if city in query:
                info["destination"] = city
                break

        # 提取天数
        days_match = re.search(r'(\d+)\s*[天日]', query)
        if days_match:
            info["days"] = int(days_match.group(1))

        # 提取预算
        budget_match = re.search(r'预算\s*(\d+)|(\d+)\s*[块元]|(\d{3,})', query)
        if budget_match:
            info["budget"] = int(budget_match.group(1) or budget_match.group(2) or budget_match.group(3))

        # 提取人群类型
        if any(kw in query for kw in ["亲子", "孩子", "小孩", "宝宝", "儿童", "娃"]):
            info["people_type"] = "family"
            info["has_kids"] = True
        elif any(kw in query for kw in ["情侣", "蜜月", "约会", "两个人"]):
            info["people_type"] = "couple"
        elif any(kw in query for kw in ["一个人", "独自", "独行", "solo"]):
            info["people_type"] = "solo"
        elif any(kw in query for kw in ["团", "同事", "朋友们", "一群"]):
            info["people_type"] = "group"

        # 提取偏好
        pref_keywords = {
            "美食": ["美食", "吃", "小吃", "餐厅", "好吃", "觅食"],
            "海滩": ["海", "海边", "海景", "沙滩", "冲浪"],
            "文化": ["文化", "历史", "古迹", "博物馆", "寺庙"],
            "自然": ["山", "湖", "自然", "风景", "徒步", "户外"],
            "购物": ["购物", "买", "逛街", "商场"],
            "休闲": ["休闲", "度假", "放松", "慢"],
        }
        for pref, keywords in pref_keywords.items():
            if any(kw in query for kw in keywords):
                info["preferences"].append(pref)

        # 提取预算等级关键词
        if any(kw in query for kw in ["穷游", "省钱", "便宜", "经济"]):
            info["budget_level"] = "low"
        elif any(kw in query for kw in ["豪华", "高端", "奢华", "五星"]):
            info["budget_level"] = "high"

        return info

    def _generate_questions(self, detected: Dict, query: str) -> List[Dict]:
        """根据已检测到的信息，生成需要补充的问题"""
        questions = []

        # 必问：预算（如果没有明确预算）
        if not detected.get("budget") and not detected.get("budget_level"):
            questions.append(self.QUESTION_TEMPLATES["budget"])

        # 必问：出行人数（如果没有检测到）
        if not detected.get("people_type"):
            questions.append(self.QUESTION_TEMPLATES["people"])

        # 可选：天数（如果没有）
        if not detected.get("days"):
            questions.append(self.QUESTION_TEMPLATES["days"])

        # 可选：住宿偏好（2天以上的行程才问）
        days = detected.get("days", 0)
        if days >= 2 or not days:
            if len(questions) < 4:  # 控制问题数量不超过4个
                questions.append(self.QUESTION_TEMPLATES["accommodation"])

        # 可选：玩法偏好（如果没有明确偏好）
        if not detected.get("preferences") and len(questions) < 5:
            questions.append(self.QUESTION_TEMPLATES["travel_style"])

        # 最多返回5个问题
        return questions[:5]

    def enhance_query(self, original_query: str, answers: Dict[str, str]) -> str:
        """
        根据用户回答增强原始查询

        Args:
            original_query: 原始查询
            answers: 用户选择的答案 {"budget": "budget_mid", "people": "family", ...}

        Returns:
            增强后的查询字符串
        """
        parts = [original_query]

        # 预算
        budget_map = {
            "budget_low": "预算有限，穷游省钱，人均1000左右",
            "budget_mid": "预算中等，追求舒适，人均3000左右",
            "budget_high": "预算充足，追求品质，人均5000以上",
        }
        if "budget" in answers:
            parts.append(budget_map.get(answers["budget"], ""))

        # 出行人数
        people_map = {
            "solo": "一个人出行",
            "couple": "两人同行（情侣/朋友）",
            "family": "家庭出游（带小孩）",
            "group": "多人团体出行（5人以上）",
        }
        if "people" in answers:
            parts.append(people_map.get(answers["people"], ""))

        # 天数
        days_map = {
            "1": "1天行程",
            "2-3": "2-3天行程",
            "4-5": "4-5天行程",
            "6+": "6天以上深度游",
        }
        if "days" in answers:
            parts.append(days_map.get(answers["days"], ""))

        # 住宿偏好
        accommodation_map = {
            "budget_hotel": "住经济型酒店（快捷/青旅）",
            "comfort_hotel": "住舒适型品牌连锁酒店",
            "luxury_hotel": "住高端五星级酒店",
            "homestay": "住特色民宿",
        }
        if "accommodation" in answers:
            parts.append(accommodation_map.get(answers["accommodation"], ""))

        # 美食偏好
        food_map = {
            "local": "想吃本地特色小吃和老字号",
            "diverse": "美食什么都想试试",
            "light": "饮食偏清淡",
        }
        if "food_preference" in answers:
            parts.append(food_map.get(answers["food_preference"], ""))

        # 玩法偏好
        style_map = {
            "culture": "偏好人文历史、博物馆、古迹",
            "nature": "偏好自然风光、山水、户外",
            "food_tour": "以美食探店为主",
            "relax": "休闲度假为主，不赶行程",
        }
        if "travel_style" in answers:
            parts.append(style_map.get(answers["travel_style"], ""))

        enhanced = "，".join(filter(None, parts))
        return enhanced
