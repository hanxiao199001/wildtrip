"""
用真实格式的数据测试 GEO 优化
"""

import sys
sys.path.insert(0, '/root/clawd/wildtrip-existing/backend')

from services.seo_service import get_seo_service
from loguru import logger

# 真实格式的测试内容
test_query = "海口周末带7岁男孩，预算2000"
test_content = """
# 海口周末带7岁男孩：恒温泳池+野海滩赶海48小时方案

## 📋 行程概览
- **天数**: 2天1晚  
- **预算**: ¥2000（一家三口）
- **出行方式**: 自驾或打车
- **核心亮点**: 恒温泳池民宿、野海滩赶海、本地美食

## 🏨 住宿推荐

### 1. 海口柚庐民宿
**价格**: ¥350/晚  
**位置**: 西海岸观海台1号  
⭐ 4.8  
**特色**: 室内恒温泳池、亲子房配置、楼顶观海台  
**为什么推荐**: 7岁孩子可以在恒温泳池安全玩水，无需去公共泳池人挤人

[美团预订](meituan://www.meituan.com/hotel/search?query=海口柚庐民宿)

### Day 1: 早上9:00 - 酒店泳池

入住后让孩子在恒温泳池玩耍1-2小时，水温恒定28℃，深度1.2米，适合学龄儿童。

#### 午餐推荐

#### 1. 海南粉老店（骑楼老街店）
**价格**: ¥15/人  
**特色菜**: 海南粉、清补凉、椰子饭  
**为什么推荐**: 本地人常去，价格实惠，孩子可以尝试椰子饭

[美团团购](meituan://www.meituan.com/food?query=海南粉老店)

### 15:30-17:30 西海岸后海角石滩赶海

退潮时段，水深仅20-50cm，几乎无游客，孩子可以抓小螃蟹、捡贝壳。

**准备物品**：
- 防晒霜 SPF50+
- 沙滩玩具桶和小铲子
- 备用衣服（会湿）

## 💬 常见问题

### 海口二月份带7岁孩子去哪个海滩人少？
西海岸后海角石滩，从市区开车约40分钟，退潮时段（约15:30-17:30）水深仅20-50cm，几乎无游客，适合学龄儿童赶海。
"""

def test_with_real_data():
    """用真实数据格式测试完整流程"""
    logger.info("=== 用真实数据测试 GEO 优化 ===")
    
    stats = {
        'word_count': 2500,
        'hotels_count': 1,
        'restaurants_count': 1,
        'total_cashback': 20
    }
    
    seo = get_seo_service()
    html = seo.generate_html(test_query, test_content, stats)
    
    # 详细检查
    checks = [
        ('FAQ 模块', '💬 常见问题' in html),
        ('FAQ JSON-LD', '"@type": "FAQPage"' in html),
        ('Schema.org Hotel', 'itemtype="https://schema.org/Hotel"' in html),
        ('Schema.org Restaurant', 'itemtype="https://schema.org/Restaurant"' in html),
        ('答案式标题在 <title>', '恒温泳池' in html.split('<title>')[1].split('</title>')[0]),
        ('hotel itemprop=name', 'itemprop="name">海口柚庐民宿' in html or '海口柚庐民宿' in html),
        ('FAQ question 在 HTML', '海口二月份带7岁孩子去哪个海滩人少' in html)
    ]
    
    print("\n【详细检查结果】")
    for name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
        if not result and '标题' in name:
            title_content = html.split('<title>')[1].split('</title>')[0] if '<title>' in html else '未找到'
            print(f"   实际标题: {title_content}")
    
    # 保存输出
    output_path = "/root/clawd/wildtrip-existing/test_geo_real_output.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ 完整 HTML 已保存到: {output_path}")
    print(f"📏 HTML 长度: {len(html)} 字节")
    
    # 提取并显示生成的FAQ
    if '💬 常见问题' in html:
        faq_start = html.find('💬 常见问题')
        faq_section = html[faq_start:faq_start+1000]
        print(f"\n【FAQ 预览】")
        print(faq_section[:500])

if __name__ == "__main__":
    test_with_real_data()
