"""
测试 CTA 按钮优化
"""

import sys
sys.path.insert(0, '/root/clawd/wildtrip-existing/backend')

from services.affiliate_manager import get_affiliate_manager
from services.itinerary_generator import HotelExtractor
from loguru import logger

def test_restaurant_cta():
    """测试餐厅 CTA 按钮"""
    logger.info("=== 测试餐厅 CTA ===")
    
    mgr = get_affiliate_manager()
    
    html = mgr._render_restaurant_card(
        link_info={'url': 'https://i.meituan.com/search?q=测试餐厅'},
        name='海南粉老店（骑楼老街店）',
        price=45,
        cashback=8,
        rating='4.7',
        features=['海南粉', '清补凉', '椰子饭', '老爸茶'],
        reason='本地人常去，性价比高，孩子可以尝试椰子饭'
    )
    
    # 检查新样式
    checks = [
        ('查看团购详情', '查看团购详情' in html),
        ('优惠标签', '预订优惠' in html),
        ('柔和边框', 'border: 2px solid #e5e7eb' in html),
        ('去除绿色渐变', 'linear-gradient(90deg, var(--primary-green' not in html)
    ]
    
    print("\n【餐厅 CTA 检查】")
    for name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    # 保存输出
    with open('/root/clawd/wildtrip-existing/test_restaurant_cta.html', 'w', encoding='utf-8') as f:
        f.write(f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>餐厅 CTA 测试</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; padding: 20px; background: #f5f5f5; }}
        :root {{
            --primary-green: #4CAF50;
            --accent-orange: #FF9500;
            --text-dark: #333;
            --text-light: #666;
            --card-radius: 16px;
            --shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        .poi-name {{ font-size: 18px; font-weight: 700; margin-bottom: 4px; }}
        .poi-meta {{ display: flex; gap: 12px; font-size: 14px; color: #666; }}
        .feature-tag {{ display: inline-block; background: #f0f0f0; padding: 4px 8px; border-radius: 6px; font-size: 12px; margin-right: 6px; }}
        .recommend-reason {{ margin: 8px 0; padding: 8px; background: #fffbeb; border-left: 3px solid #f59e0b; font-size: 13px; }}
    </style>
</head>
<body>
    <h1>餐厅 CTA 优化测试</h1>
    {html}
</body>
</html>''')
    
    logger.success("✅ 餐厅 CTA HTML 已保存")

def test_hotel_cta():
    """测试酒店 CTA 按钮"""
    logger.info("=== 测试酒店 CTA ===")
    
    hotel_extractor = HotelExtractor()
    
    hotel = {
        'name': '海口柚庐民宿',
        'price': 350,
        'market_price': 412,
        'rating': '4.8',
        'location': '西海岸观海台1号',
        'features': '室内恒温泳池、亲子房配置、楼顶观海台',
        'reason': '7岁孩子可以在恒温泳池安全玩水，无需去公共泳池人挤人',
        'cashback': 18,
        'city': '海口'
    }
    
    html = hotel_extractor.render_hotel_card(hotel)
    
    # 检查新样式
    checks = [
        ('查看房间和价格', '查看房间和价格' in html),
        ('优惠标签', '预订优惠' in html),
        ('白色背景按钮', 'background: white' in html),
        ('橙色边框', 'border: 2px solid #d97706' in html),
        ('去除绿色渐变', '💰 美团预订' not in html)
    ]
    
    print("\n【酒店 CTA 检查】")
    for name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    # 保存输出
    with open('/root/clawd/wildtrip-existing/test_hotel_cta.html', 'w', encoding='utf-8') as f:
        f.write(f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>酒店 CTA 测试</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; padding: 20px; background: #f5f5f5; }}
        :root {{
            --primary-green: #4CAF50;
            --accent-orange: #FF9500;
            --text-dark: #333;
            --text-light: #666;
            --card-radius: 16px;
            --shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        .poi-name {{ font-size: 18px; font-weight: 700; margin-bottom: 4px; }}
        .poi-meta {{ display: flex; gap: 12px; font-size: 14px; }}
        .poi-price {{ font-weight: 700; color: #E53935; }}
        .poi-rating {{ color: #666; }}
        .recommend-reason {{ margin: 12px 0; padding: 10px; background: #fffbeb; border-left: 3px solid #f59e0b; font-size: 14px; line-height: 1.6; }}
    </style>
</head>
<body>
    <h1>酒店 CTA 优化测试</h1>
    {html}
</body>
</html>''')
    
    logger.success("✅ 酒店 CTA HTML 已保存")

if __name__ == "__main__":
    test_restaurant_cta()
    print("\n" + "="*60 + "\n")
    test_hotel_cta()
    
    print("\n📁 测试文件已生成：")
    print("  - test_restaurant_cta.html")
    print("  - test_hotel_cta.html")
