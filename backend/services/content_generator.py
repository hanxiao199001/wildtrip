"""
内容生成服务
生成小红书、朋友圈等分享内容
"""

from typing import List, Dict
from loguru import logger


def generate_xiaohongshu(
    itinerary: List[Dict],
    hotels: List[Dict],
    destination: str,
    preferences: Dict = None
) -> str:
    """
    生成小红书风格的图文内容
    
    Args:
        itinerary: 行程列表
        hotels: 酒店列表
        destination: 目的地
        preferences: 用户偏好
        
    Returns:
        小红书风格的 Markdown 内容
    """
    lines = []
    
    # ========== 标题 ==========
    days = len(itinerary)
    
    if preferences and preferences.get('has_kids'):
        lines.append(f"📍 {destination}{days}天{days-1}晚亲子游 | 超全攻略")
    elif preferences and 'food' in preferences.get('travel_style', []):
        lines.append(f"📍 {destination}{days}天{days-1}晚美食之旅 | 吃货必看")
    else:
        lines.append(f"📍 {destination}{days}天{days-1}晚深度游 | 野路子攻略")
    
    lines.append("")
    
    # ========== 适合人群 ==========
    lines.append("✨ **适合人群**")
    
    if preferences:
        if preferences.get('has_kids'):
            kids_ages = preferences.get('kids_ages', [])
            if kids_ages:
                ages_str = '+'.join([str(age) for age in kids_ages])
                lines.append(f"👨‍👩‍👧‍👦 {ages_str}岁孩子的家庭")
            else:
                lines.append("👨‍👩‍👧‍👦 亲子家庭")
        
        budget = preferences.get('budget_level', 'mid')
        if budget == 'low':
            lines.append("💰 预算有限，追求性价比")
        elif budget == 'high':
            lines.append("👑 高端出行，不差钱")
        else:
            lines.append("💰 预算中等，追求性价比")
        
        styles = preferences.get('travel_style', [])
        if 'food' in styles:
            lines.append("🍜 吃货必看")
        if 'culture' in styles:
            lines.append("🏛️ 人文爱好者")
    
    lines.append("")
    
    # ========== 住宿推荐 ==========（2026-03: 已禁用，只保留文字推荐）
    # if hotels: ...
    
    # ========== 行程亮点 ==========
    lines.append("📸 **行程亮点**")
    lines.append("")
    
    for idx, day in enumerate(itinerary[:3], 1):  # 最多3天
        day_num = day.get('day', idx)
        theme = day.get('theme', f'Day {day_num}')
        morning = day.get('morning', '')
        afternoon = day.get('afternoon', '')
        
        lines.append(f"**Day {day_num}: {theme}**")
        if morning:
            lines.append(f"- 上午: {morning[:50]}...")
        if afternoon:
            lines.append(f"- 下午: {afternoon[:50]}...")
        lines.append("")
    
    # ========== 美食打卡 ==========
    lines.append("🍜 **美食打卡**")
    lines.append("")
    
    # 从行程中提取餐厅（简化版）
    restaurant_names = [
        "梅姨海南粉: 本地人常去，游客少",
        "文昌鸡饭老店: 比网红店好吃还便宜"
    ]
    for r in restaurant_names:
        lines.append(f"- {r}")
    lines.append("")
    
    # ========== 野路子小贴士 ==========
    lines.append("💡 **野路子小贴士**")
    lines.append("")
    lines.append("- 避开10点后的人流高峰")
    lines.append("- 本地人推荐的小店都藏在巷子里")
    lines.append("- 早上8点光线最好，适合拍照")
    lines.append("")
    
    # ========== 话题标签 ==========
    tags = [
        f"#{destination}旅游",
        "#野游记",
        "#小众路线"
    ]
    
    if preferences:
        if preferences.get('has_kids'):
            tags.append("#亲子游")
        if 'food' in preferences.get('travel_style', []):
            tags.append("#美食攻略")
        if preferences.get('budget_level') == 'low':
            tags.append("#穷游")
    
    lines.append(" ".join(tags))
    
    content = "\n".join(lines)
    
    logger.info(f"✅ 生成小红书内容: {len(content)}字")
    
    return content


def generate_wechat_moments(
    destination: str,
    days: int,
    highlights: List[str]
) -> str:
    """
    生成朋友圈文案
    
    Args:
        destination: 目的地
        days: 天数
        highlights: 亮点列表
        
    Returns:
        朋友圈文案
    """
    lines = [
        f"📍 {destination} {days}天{days-1}晚",
        "",
        "💫 这次玩得太爽了！"
    ]
    
    for highlight in highlights[:3]:
        lines.append(f"✨ {highlight}")
    
    lines.append("")
    lines.append("🔗 完整攻略看野游记小程序")
    
    return "\n".join(lines)


# ========== 测试代码 ==========
if __name__ == '__main__':
    # 测试数据
    test_itinerary = [
        {
            'day': 1,
            'theme': '慢享海口老城',
            'morning': '骑楼老街漫步，避开10点后人流',
            'afternoon': '五公祠，人文历史'
        },
        {
            'day': 2,
            'theme': '火山口地质公园',
            'morning': '火山口公园徒步',
            'afternoon': '石山古村落探访'
        }
    ]
    
    test_hotels = [
        {
            'name': '海口朗廷酒店',
            'price': 680,
            'features': ['无边泳池', '儿童设施', '含早餐'],
            'reason': '亲子友好，性价比高'
        }
    ]
    
    test_preferences = {
        'has_kids': True,
        'kids_ages': [7, 4],
        'budget_level': 'mid',
        'travel_style': ['food']
    }
    
    print("="*60)
    print("测试小红书内容生成")
    print("="*60)
    
    content = generate_xiaohongshu(
        itinerary=test_itinerary,
        hotels=test_hotels,
        destination="海口",
        preferences=test_preferences
    )
    
    print(content)
    
    print("\n" + "="*60)
    print("测试朋友圈文案")
    print("="*60)
    
    moments = generate_wechat_moments(
        destination="海口",
        days=3,
        highlights=[
            "骑楼老街超美，早上8点去光线最好",
            "火山口公园人少景美",
            "梅姨海南粉太好吃了！"
        ]
    )
    
    print(moments)
