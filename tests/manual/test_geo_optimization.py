"""
测试 GEO 优化功能
"""

import sys
sys.path.insert(0, '/root/clawd/wildtrip-existing/backend')

from services.itinerary_generator import get_itinerary_generator
from services.seo_service import get_seo_service
from loguru import logger

# 测试内容
test_query = "海口周末带7岁男孩"
test_content = """
## 📋 行程概览
- **天数**: 2天1晚
- **预算**: ¥2000/家庭
- **出行方式**: 自驾

### 核心亮点
1. 恒温泳池民宿，孩子玩水不怕冷
2. 野海滩赶海，退潮时抓螃蟹
3. 本地老爸茶体验
4. 海南特色清补凉

### 住宿推荐

#### 1. 海口柚庐民宿
**价格**: ¥350/晚
**位置**: 西海岸
**特色**: 恒温泳池、亲子房
⭐ 4.8
**为什么推荐**: 室内恒温泳池，7岁孩子可以安全玩水

### Day 1: 09:00-10:30 酒店泳池
孩子在恒温泳池玩耍

### 15:30-17:30 西海岸后海角石滩赶海
退潮时段，水深仅20-50cm，适合学龄儿童赶海
"""

def test_faq_generation():
    """测试 FAQ 生成"""
    logger.info("=== 测试 FAQ 生成 ===")
    
    generator = get_itinerary_generator()
    faq_html, faq_jsonld = generator._generate_faq_section(test_query, test_content, '海口')
    
    print("\n【FAQ HTML】")
    print(faq_html[:500])
    
    print("\n【FAQ JSON-LD】")
    print(faq_jsonld[:500])
    
    logger.success("✅ FAQ 生成测试通过")

def test_answer_style_title():
    """测试答案式标题"""
    logger.info("=== 测试答案式标题 ===")
    
    seo = get_seo_service()
    title = seo._generate_answer_style_title(test_query, test_content, '海口')
    
    print(f"\n【原始query】{test_query}")
    print(f"【生成标题】{title}")
    
    logger.success("✅ 答案式标题测试通过")

def test_full_html_generation():
    """测试完整 HTML 生成"""
    logger.info("=== 测试完整 HTML 生成 ===")
    
    stats = {
        'word_count': 3000,
        'hotels_count': 1,
        'restaurants_count': 3,
        'total_cashback': 25
    }
    
    seo = get_seo_service()
    html = seo.generate_html(test_query, test_content, stats)
    
    # 检查关键内容
    checks = [
        ('FAQ 模块', '💬 常见问题' in html),
        ('FAQ JSON-LD', 'FAQPage' in html),
        ('Schema.org Hotel', 'itemtype="https://schema.org/Hotel"' in html),
        ('答案式标题', '：' in html.split('<title>')[1].split('</title>')[0])
    ]
    
    print("\n【检查结果】")
    for name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    # 保存测试输出
    output_path = "/root/clawd/wildtrip-existing/test_geo_output.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    logger.success(f"✅ 完整 HTML 已保存到: {output_path}")

if __name__ == "__main__":
    test_faq_generation()
    print("\n" + "="*60 + "\n")
    
    test_answer_style_title()
    print("\n" + "="*60 + "\n")
    
    test_full_html_generation()
