"""
测试百度统计代码是否正确埋入
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.dual_engine_generator import DualEngineGenerator
from pathlib import Path
from loguru import logger


def test_analytics():
    """测试百度统计"""
    
    logger.info("📊 测试百度统计代码...")
    
    # 生成一个测试攻略
    generator = DualEngineGenerator()
    
    result = generator.generate_guide(
        query="海口2天亲子游测试百度统计",
        output_format='html',
        city='海口'
    )
    
    if not result.get('success'):
        logger.error(f"❌ 生成失败: {result.get('error')}")
        return
    
    html_file = result.get('file')
    logger.info(f"✅ 生成成功: {html_file}")
    
    # 检查是否包含百度统计代码
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    baidu_id = "2f348a42f00786d4955004971d986ec18"
    
    if baidu_id in html_content:
        logger.success(f"✅ 百度统计代码已正确埋入!")
        logger.info(f"   统计ID: {baidu_id}")
        
        # 显示代码片段
        start = html_content.find('var _hmt')
        if start > 0:
            snippet = html_content[start:start+200]
            logger.info(f"\n代码片段:\n{snippet}\n")
    else:
        logger.error(f"❌ 百度统计代码未找到!")
        logger.warning(f"   请检查 seo_optimizer.py 配置")
    
    # 提示
    logger.info(f"\n{'='*60}")
    logger.info(f"🎯 下一步:")
    logger.info(f"   1. 用浏览器打开: {html_file}")
    logger.info(f"   2. 打开浏览器开发者工具 (F12)")
    logger.info(f"   3. 查看 Network 面板,应该能看到:")
    logger.info(f"      hm.baidu.com/hm.js?{baidu_id}")
    logger.info(f"   4. 20分钟后去百度统计后台查看实时访客")
    logger.info(f"{'='*60}")


if __name__ == '__main__':
    test_analytics()
