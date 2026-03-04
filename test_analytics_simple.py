"""
简单测试百度统计代码
"""

import sys
sys.path.insert(0, '/root/clawd/backend/services')

from seo_optimizer import get_seo_optimizer

# 创建优化器
optimizer = get_seo_optimizer()

# 生成百度统计代码
analytics_html = optimizer.generate_baidu_analytics()

print("="*60)
print("📊 百度统计代码:")
print("="*60)
print(analytics_html)
print("="*60)

# 检查ID
baidu_id = "2f348a42f00786d4955004971d986ec18"
if baidu_id in analytics_html:
    print(f"✅ 统计ID配置正确: {baidu_id}")
else:
    print(f"❌ 统计ID未找到!")
    print(f"   期望: {baidu_id}")
