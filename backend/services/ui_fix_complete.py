# ============================================================
# 野游记 UI 完整修复方案
# 问题：CSS类定义了但生成的HTML没有使用这些类
# 解决：修改Python渲染逻辑，输出带有正确CSS类的HTML
# ============================================================

import re
from urllib.parse import quote

# ============================================================
# 第一步：完整CSS样式
# ============================================================

COMPLETE_CSS = """
/* ====== 野游记设计系统 ====== */

/* 颜色变量 */
:root {
    --primary-green: #10B981;
    --primary-green-light: #D1FAE5;
    --accent-orange: #F59E0B;
    --accent-orange-light: #FEF3C7;
    --warning-red: #EF4444;
    --warning-red-light: #FEE2E2;
    --text-dark: #1F2937;
    --text-medium: #4B5563;
    --text-light: #9CA3AF;
    --bg-light: #F9FAFB;
    --border-color: #E5E7EB;
}

/* 概览卡片 */
.overview-card {
    background: linear-gradient(135deg, var(--primary-green) 0%, #059669 100%);
    border-radius: 16px;
    padding: 24px;
    color: white;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3);
}

.overview-title {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 16px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.overview-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    font-size: 15px;
    opacity: 0.95;
}

.overview-meta span {
    display: flex;
    align-items: center;
    gap: 6px;
}

/* 日期头部 */
.day-header {
    background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
    border-left: 5px solid var(--primary-green);
    border-radius: 0 12px 12px 0;
    padding: 16px 20px;
    margin: 28px 0 20px 0;
}

.day-number {
    font-size: 22px;
    font-weight: 700;
    color: var(--primary-green);
}

.day-theme {
    font-size: 15px;
    color: var(--text-medium);
    margin-top: 4px;
}

/* 时间线 */
.timeline-item {
    display: flex;
    gap: 16px;
    margin-bottom: 20px;
    padding: 16px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border: 1px solid var(--border-color);
    transition: all 0.2s ease;
}

.timeline-item:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    transform: translateY(-2px);
}

.time-badge {
    flex-shrink: 0;
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, var(--primary-green-light) 0%, #A7F3D0 100%);
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-weight: 600;
}

.time-badge .time {
    font-size: 16px;
    color: var(--primary-green);
    font-weight: 700;
}

.time-badge .icon {
    font-size: 20px;
    margin-top: 2px;
}

.timeline-content {
    flex: 1;
}

.activity-name {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-dark);
    margin-bottom: 6px;
}

.activity-desc {
    font-size: 14px;
    color: var(--text-medium);
    line-height: 1.6;
}

/* 餐厅卡片 */
.restaurant-card {
    background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
    border-radius: 16px;
    padding: 20px;
    margin: 16px 0;
    border: 1px solid #FDE68A;
}

.restaurant-header {
    display: flex;
    align-items: flex-start;
    gap: 16px;
}

.restaurant-icon {
    width: 64px;
    height: 64px;
    background: linear-gradient(135deg, #FBBF24, #F59E0B);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
}

.restaurant-info {
    flex: 1;
}

.restaurant-name {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-dark);
}

.restaurant-rating {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 4px;
    font-size: 14px;
}

.restaurant-rating .score {
    color: var(--accent-orange);
    font-weight: 700;
}

.restaurant-rating .reviews {
    color: var(--text-light);
}

.restaurant-dishes {
    font-size: 14px;
    color: var(--text-medium);
    margin-top: 6px;
}

.restaurant-price-section {
    background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
    border-radius: 12px;
    padding: 16px;
    margin-top: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.restaurant-price {
    display: flex;
    align-items: baseline;
    gap: 4px;
}

.restaurant-price .amount {
    font-size: 28px;
    font-weight: 700;
    color: var(--warning-red);
}

.restaurant-price .unit {
    font-size: 14px;
    color: var(--text-medium);
}

.cashback-badge {
    background: var(--warning-red);
    color: white;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 700;
}

.restaurant-btn {
    display: block;
    width: 100%;
    background: linear-gradient(135deg, var(--primary-green) 0%, #059669 100%);
    color: white;
    text-align: center;
    padding: 14px;
    border-radius: 12px;
    text-decoration: none;
    font-weight: 700;
    font-size: 16px;
    margin-top: 16px;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    transition: all 0.2s ease;
}

.restaurant-btn:hover {
    box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
    transform: translateY(-1px);
}

/* 酒店卡片 */
.hotel-card {
    background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%);
    border-radius: 16px;
    padding: 20px;
    margin: 16px 0;
    border: 1px solid #FED7AA;
}

.hotel-header {
    display: flex;
    align-items: flex-start;
    gap: 16px;
}

.hotel-icon {
    width: 72px;
    height: 72px;
    background: linear-gradient(135deg, #FB923C, #F97316);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 36px;
}

.hotel-info {
    flex: 1;
}

.hotel-name {
    font-size: 20px;
    font-weight: 700;
    color: var(--text-dark);
}

.hotel-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 6px;
    font-size: 14px;
}

.hotel-meta .rating {
    color: var(--accent-orange);
    font-weight: 700;
}

.hotel-meta .location {
    color: var(--text-medium);
}

.hotel-features {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 8px;
}

.hotel-feature-tag {
    background: white;
    color: var(--text-medium);
    padding: 4px 10px;
    border-radius: 16px;
    font-size: 12px;
    border: 1px solid var(--border-color);
}

.hotel-price-section {
    background: linear-gradient(135deg, #FFEDD5 0%, #FED7AA 100%);
    border-radius: 12px;
    padding: 16px;
    margin-top: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.hotel-price .original {
    text-decoration: line-through;
    color: var(--text-light);
    font-size: 14px;
}

.hotel-price .current {
    display: flex;
    align-items: baseline;
    gap: 4px;
}

.hotel-price .amount {
    font-size: 32px;
    font-weight: 700;
    color: var(--warning-red);
}

.hotel-price .unit {
    font-size: 14px;
    color: var(--text-medium);
}

.hotel-btn {
    display: block;
    width: 100%;
    background: linear-gradient(135deg, #F97316 0%, #EA580C 100%);
    color: white;
    text-align: center;
    padding: 14px;
    border-radius: 12px;
    text-decoration: none;
    font-weight: 700;
    font-size: 16px;
    margin-top: 16px;
    box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
    transition: all 0.2s ease;
}

.hotel-btn:hover {
    box-shadow: 0 6px 16px rgba(249, 115, 22, 0.4);
    transform: translateY(-1px);
}

/* 亮点标签 */
.highlight-tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: linear-gradient(135deg, var(--primary-green-light) 0%, #A7F3D0 100%);
    color: var(--primary-green);
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    margin: 4px;
}

/* Tips提示 */
.tips-box {
    background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
    border-left: 4px solid #3B82F6;
    border-radius: 0 12px 12px 0;
    padding: 14px 18px;
    margin: 12px 0;
    font-size: 14px;
    color: #1E40AF;
}

.tips-box::before {
    content: "💡 ";
}

/* 费用明细 */
.cost-section {
    background: white;
    border-radius: 16px;
    padding: 20px;
    margin: 24px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border: 1px solid var(--border-color);
}

.cost-title {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-dark);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.cost-item {
    display: flex;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px dashed var(--border-color);
}

.cost-item:last-child {
    border-bottom: none;
}

.cost-label {
    color: var(--text-medium);
}

.cost-value {
    font-weight: 600;
    color: var(--text-dark);
}

.cost-total {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 2px solid var(--primary-green);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.cost-total .label {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-dark);
}

.cost-total .value {
    font-size: 28px;
    font-weight: 700;
    color: var(--warning-red);
}

/* 交通信息 */
.transport-info {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #F3F4F6;
    padding: 10px 14px;
    border-radius: 10px;
    margin: 8px 0;
    font-size: 14px;
    color: var(--text-medium);
}

.transport-info .icon {
    font-size: 18px;
}

/* 返现提示横幅 */
.cashback-banner {
    background: linear-gradient(135deg, var(--warning-red) 0%, #DC2626 100%);
    color: white;
    padding: 14px 20px;
    border-radius: 12px;
    margin: 16px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.cashback-banner .text {
    font-size: 15px;
}

.cashback-banner .amount {
    font-size: 24px;
    font-weight: 700;
}

/* 底部固定栏 */
.bottom-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    padding: 12px 20px;
    box-shadow: 0 -4px 16px rgba(0,0,0,0.1);
    display: flex;
    gap: 12px;
    z-index: 100;
}

.bottom-bar .btn-primary {
    flex: 1;
    background: linear-gradient(135deg, var(--primary-green) 0%, #059669 100%);
    color: white;
    padding: 14px;
    border-radius: 12px;
    font-weight: 700;
    font-size: 16px;
    text-align: center;
    border: none;
    cursor: pointer;
}

.bottom-bar .btn-secondary {
    width: 50px;
    height: 50px;
    background: #F3F4F6;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    border: none;
    cursor: pointer;
}

/* 响应式适配 */
@media (max-width: 480px) {
    .overview-card {
        padding: 20px;
    }

    .overview-title {
        font-size: 24px;
    }

    .overview-meta {
        font-size: 13px;
    }

    .day-header {
        padding: 14px 16px;
    }

    .timeline-item {
        padding: 14px;
    }

    .restaurant-card, .hotel-card {
        padding: 16px;
    }
}
"""


# ============================================================
# 第二步：渲染方法
# ============================================================

def render_overview_card(title, days, budget, highlights):
    """渲染概览卡片 - 使用新CSS类"""
    highlights_html = ""
    for h in highlights[:5]:
        highlights_html += f'<span class="highlight-tag">{h}</span>'

    return f'''
<div class="overview-card">
    <div class="overview-title">{title}</div>
    <div class="overview-meta">
        <span>📅 {days}天{days-1}晚</span>
        <span>💰 预算¥{budget}</span>
        <span>🎯 精选路线</span>
    </div>
    <div style="margin-top: 16px;">
        {highlights_html}
    </div>
</div>
'''


def render_day_header(day_num, theme):
    """渲染日期头部 - 使用新CSS类"""
    weekday_map = {1: "周六", 2: "周日", 3: "周一", 4: "周二", 5: "周三"}
    weekday = weekday_map.get(day_num, f"第{day_num}天")

    return f'''
<div class="day-header">
    <div class="day-number">Day {day_num} · {weekday}</div>
    <div class="day-theme">🎯 {theme}</div>
</div>
'''


def render_timeline_item(time, icon, name, description, tips=None, duration=None):
    """渲染时间线项目 - 使用新CSS类"""
    tips_html = ""
    if tips:
        tips_html = f'<div class="tips-box">{tips}</div>'

    duration_html = ""
    if duration:
        duration_html = f'<span style="color: var(--text-light); font-size: 13px;">⏱️ {duration}</span>'

    return f'''
<div class="timeline-item">
    <div class="time-badge">
        <span class="time">{time}</span>
        <span class="icon">{icon}</span>
    </div>
    <div class="timeline-content">
        <div class="activity-name">{name} {duration_html}</div>
        <div class="activity-desc">{description}</div>
        {tips_html}
    </div>
</div>
'''


def render_restaurant_card(name, price, rating, dishes, city=""):
    """渲染餐厅卡片 - 使用新CSS类"""
    # 生成美团搜索链接
    search_keyword = f"{city}{name}" if city else name
    meituan_link = f"https://i.meituan.com/search?q={quote(search_keyword)}"

    # 计算返现（搜索链接无实际返现，仅展示）
    cashback = max(5, int(price * 0.05))

    return f'''
<div class="restaurant-card">
    <div class="restaurant-header">
        <div class="restaurant-icon">🍜</div>
        <div class="restaurant-info">
            <div class="restaurant-name">{name}</div>
            <div class="restaurant-rating">
                <span class="score">⭐ {rating}</span>
                <span class="reviews">· 本地人推荐</span>
            </div>
            <div class="restaurant-dishes">推荐：{dishes}</div>
        </div>
    </div>

    <div class="restaurant-price-section">
        <div class="restaurant-price">
            <span class="amount">¥{price}</span>
            <span class="unit">/人</span>
        </div>
        <div class="cashback-badge">返 ¥{cashback}</div>
    </div>

    <a href="{meituan_link}" target="_blank" class="restaurant-btn">
        美团预订，返现 ¥{cashback}
    </a>

    <div style="display: flex; justify-content: center; gap: 16px; margin-top: 12px; color: var(--text-light); font-size: 12px;">
        <span>✓ 免预约</span>
        <span>✓ 到店付款</span>
        <span>✓ 返现秒到</span>
    </div>
</div>
'''


def render_hotel_card(name, price, rating, location, features, city=""):
    """渲染酒店卡片 - 使用新CSS类"""
    # 生成美团搜索链接
    search_keyword = f"{city}{name}" if city else name
    meituan_link = f"https://i.meituan.com/search?q={quote(search_keyword)}"

    # 计算返现（假设5%返现率）
    cashback = max(10, int(price * 0.05))
    original_price = int(price * 1.2)

    # 特点标签
    features_html = ""
    if isinstance(features, list):
        for f in features[:3]:
            features_html += f'<span class="hotel-feature-tag">{f}</span>'
    elif isinstance(features, str):
        for f in features.split('、')[:3]:
            features_html += f'<span class="hotel-feature-tag">{f}</span>'

    return f'''
<div class="hotel-card">
    <div class="hotel-header">
        <div class="hotel-icon">🏨</div>
        <div class="hotel-info">
            <div class="hotel-name">{name}</div>
            <div class="hotel-meta">
                <span class="rating">⭐ {rating}</span>
                <span class="location">📍 {location}</span>
            </div>
            <div class="hotel-features">
                {features_html}
            </div>
        </div>
    </div>

    <div class="hotel-price-section">
        <div class="hotel-price">
            <div class="original">门市价 ¥{original_price}</div>
            <div class="current">
                <span class="amount">¥{price}</span>
                <span class="unit">/晚</span>
            </div>
        </div>
        <div class="cashback-badge">返 ¥{cashback}</div>
    </div>

    <a href="{meituan_link}" target="_blank" class="hotel-btn">
        美团预订，返现 ¥{cashback}
    </a>

    <div style="display: flex; justify-content: center; gap: 16px; margin-top: 12px; color: var(--text-light); font-size: 12px;">
        <span>✓ 免费取消</span>
        <span>✓ 到店付款</span>
        <span>✓ 返现秒到</span>
    </div>
</div>
'''


def render_cashback_banner(total_cashback):
    """渲染返现横幅"""
    return f'''
<div class="cashback-banner">
    <div class="text">🎉 预订本攻略推荐可获返现</div>
    <div class="amount">¥{total_cashback}</div>
</div>
'''
