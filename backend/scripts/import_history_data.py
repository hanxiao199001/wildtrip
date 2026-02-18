#!/usr/bin/env python3
"""
导入历史数据到ChromaDB
将时间线、诗词、地点数据转换为向量并存储
"""

import sys
import json
from pathlib import Path

# 添加backend路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.rag_engine import get_rag_engine
from loguru import logger


def load_json(file_path):
    """加载JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def import_sudongpo_timeline():
    """导入苏东坡时间线"""
    logger.info("📚 导入苏东坡时间线...")
    
    data_path = Path(__file__).parent.parent / 'data/history/苏东坡/时间线.json'
    data = load_json(data_path)
    
    rag = get_rag_engine()
    guides = []
    
    # 核心事件时间线
    for event in data.get('核心事件时间线', []):
        # 构建内容文本（用于向量化）
        content_parts = [
            f"## 苏东坡 - {event['事件']}",
            f"时间：{event['时间']}",
            f"地点：{event['地点']}",
            f"意义：{event.get('意义', '')}",
        ]
        
        # 添加代表作品
        if '代表作品' in event:
            content_parts.append(f"代表作品：{', '.join(event['代表作品'])}")
        
        # 添加名句
        if '名句' in event:
            if isinstance(event['名句'], list):
                content_parts.append(f"名句：{'; '.join(event['名句'])}")
            else:
                content_parts.append(f"名句：{event['名句']}")
        
        # 添加背景、心境等
        for key in ['背景', '心境', '心境变化', '核心转折', '终极感悟']:
            if key in event:
                content_parts.append(f"{key}：{event[key]}")
        
        # 添加遗迹
        if '遗迹' in event:
            if isinstance(event['遗迹'], list):
                content_parts.append(f"遗迹：{', '.join(event['遗迹'])}")
            else:
                content_parts.append(f"遗迹：{event['遗迹']}")
        
        content = '\n'.join(content_parts)
        
        # 生成ID
        guide_id = f"sudongpo_timeline_{event['序号']}"
        
        # 元数据
        metadata = {
            "person": "苏东坡",
            "type": "history",
            "category": "timeline",
            "time": event['时间'],
            "location": event['地点'],
            "event": event['事件'],
            "source": event.get('史料来源', ''),
            "sequence": event['序号']
        }
        
        guides.append({
            "id": guide_id,
            "content": content,
            "metadata": metadata
        })
    
    # 批量导入
    if guides:
        rag.batch_add_guides(guides)
        logger.info(f"✅ 导入苏东坡时间线: {len(guides)}条")
    
    return len(guides)


def import_sudongpo_poems():
    """导入苏东坡诗词"""
    logger.info("📚 导入苏东坡诗词...")
    
    data_path = Path(__file__).parent.parent / 'data/history/诗词/苏东坡诗词库.json'
    data = load_json(data_path)
    
    rag = get_rag_engine()
    guides = []
    
    for poem in data.get('诗词库', []):
        # 构建内容
        content_parts = [
            f"## {poem['标题']}",
            f"作者：{poem.get('作者', '苏轼')}",
            f"创作时间：{poem.get('创作时间', '')}",
        ]
        
        # 处理创作地点（可能是字符串或对象）
        location = poem.get('创作地点', '')
        if isinstance(location, dict):
            location_str = f"{location.get('古称', '')}（今{location.get('今称', '')}）"
            content_parts.append(f"创作地点：{location_str}")
        elif location:
            content_parts.append(f"创作地点：{location}")
        
        content_parts.append("")
        
        # 添加全文
        if '全文' in poem:
            content_parts.append("### 诗词原文")
            content_parts.append(poem['全文'])
            content_parts.append("")
        
        # 添加创作背景
        if '创作背景' in poem:
            content_parts.append(f"### 创作背景")
            content_parts.append(poem['创作背景'])
            content_parts.append("")
        
        # 添加名句
        if '名句' in poem:
            content_parts.append(f"### 名句")
            content_parts.append(poem['名句'])
            content_parts.append("")
        elif '名句精选' in poem:
            content_parts.append(f"### 名句精选")
            for mingju in poem['名句精选']:
                content_parts.append(f"- {mingju}")
            content_parts.append("")
        
        # 添加核心主题/哲学思考
        for key in ['核心主题', '哲学思考', '哲学升华', '意义']:
            if key in poem:
                content_parts.append(f"### {key}")
                content_parts.append(poem[key])
                content_parts.append("")
        
        # 添加现代体验
        if '现代体验' in poem:
            content_parts.append("### 现代体验")
            content_parts.append(poem['现代体验'])
            content_parts.append("")
        
        # 添加旅游tips
        if '旅游tips' in poem:
            content_parts.append(f"### 旅游建议")
            content_parts.append(poem['旅游tips'])
            content_parts.append("")
        
        # 添加美食攻略
        if '美食攻略' in poem:
            content_parts.append(f"### 美食攻略")
            content_parts.append(poem['美食攻略'])
            content_parts.append("")
        
        content = '\n'.join(content_parts)
        
        # 生成ID
        guide_id = f"sudongpo_poem_{poem.get('id', poem['标题'])}"
        
        # 处理地点元数据
        location_meta = ""
        if isinstance(poem.get('创作地点'), dict):
            location_meta = poem['创作地点'].get('今称', '')
        elif poem.get('创作地点'):
            location_meta = poem['创作地点']
        
        # 元数据
        metadata = {
            "person": "苏东坡",
            "type": "history",
            "category": "poem",
            "title": poem['标题'],
            "time": poem.get('创作时间', ''),
            "location": location_meta,
            "source": poem.get('史料来源', '')
        }
        
        guides.append({
            "id": guide_id,
            "content": content,
            "metadata": metadata
        })
    
    # 批量导入
    if guides:
        rag.batch_add_guides(guides)
        logger.info(f"✅ 导入苏东坡诗词: {len(guides)}条")
    
    return len(guides)


def import_sudongpo_locations():
    """导入苏东坡路线地点"""
    logger.info("📚 导入苏东坡路线地点...")
    
    data_path = Path(__file__).parent.parent / 'data/history/地点/苏东坡路线地点.json'
    data = load_json(data_path)
    
    rag = get_rag_engine()
    guides = []
    
    for location in data.get('路线地点', []):
        # 构建内容
        content_parts = [
            f"## {location['古代地名']}（{location['今日地名']}）",
            f"历史意义：{location.get('历史意义', '')}",
            "",
        ]
        
        # 添加停留时间
        if '停留时间' in location:
            if isinstance(location['停留时间'], list):
                content_parts.append(f"停留时间：{'; '.join(location['停留时间'])}")
            else:
                content_parts.append(f"停留时间：{location['停留时间']}")
            content_parts.append("")
        
        # 添加主要遗迹
        if '主要遗迹' in location:
            content_parts.append("### 主要遗迹")
            for site in location['主要遗迹']:
                content_parts.append(f"\n#### {site['名称']}")
                if '位置' in site:
                    content_parts.append(f"位置：{site['位置']}")
                if '历史' in site:
                    content_parts.append(f"历史：{site['历史']}")
                if '现状' in site:
                    content_parts.append(f"现状：{site['现状']}")
                if '游览建议' in site:
                    content_parts.append(f"游览建议：{site['游览建议']}")
                if '核心看点' in site:
                    content_parts.append("核心看点：")
                    for point in site['核心看点']:
                        content_parts.append(f"- {point}")
            content_parts.append("")
        
        # 添加必吃美食
        if '必吃美食' in location:
            content_parts.append("### 必吃美食")
            for food in location['必吃美食']:
                if isinstance(food, dict):
                    content_parts.append(f"\n#### {food['名称']}")
                    if '起源' in food:
                        content_parts.append(f"起源：{food['起源']}")
                    if '历史' in food:
                        content_parts.append(f"历史：{food['历史']}")
                    if '特点' in food:
                        content_parts.append(f"特点：{food['特点']}")
                    if '推荐餐厅' in food:
                        if isinstance(food['推荐餐厅'], list):
                            content_parts.append("推荐餐厅：")
                            for rest in food['推荐餐厅']:
                                content_parts.append(f"- {rest}")
                        else:
                            content_parts.append(f"推荐：{food['推荐餐厅']}")
                else:
                    content_parts.append(f"- {food}")
            content_parts.append("")
        
        # 添加必做体验
        if '必做体验' in location or '必游体验' in location:
            experiences = location.get('必做体验') or location.get('必游体验', [])
            content_parts.append("### 必做体验")
            for exp in experiences:
                content_parts.append(f"- {exp}")
            content_parts.append("")
        
        # 添加交通和住宿
        if '交通' in location:
            content_parts.append(f"### 交通")
            content_parts.append(location['交通'])
            content_parts.append("")
        
        if '住宿建议' in location:
            content_parts.append(f"### 住宿建议")
            content_parts.append(location['住宿建议'])
            content_parts.append("")
        
        if '停留时间建议' in location:
            content_parts.append(f"### 停留时间建议")
            content_parts.append(location['停留时间建议'])
            content_parts.append("")
        
        content = '\n'.join(content_parts)
        
        # 生成ID
        guide_id = f"sudongpo_location_{location.get('id', location['古代地名'])}"
        
        # 元数据
        metadata = {
            "person": "苏东坡",
            "type": "history",
            "category": "location",
            "location": location['古代地名'],
            "modern_location": location['今日地名'],
            "significance": location.get('历史意义', '')
        }
        
        guides.append({
            "id": guide_id,
            "content": content,
            "metadata": metadata
        })
    
    # 批量导入
    if guides:
        rag.batch_add_guides(guides)
        logger.info(f"✅ 导入苏东坡路线地点: {len(guides)}条")
    
    return len(guides)


def main():
    """主函数"""
    logger.info("🚀 开始导入历史数据到ChromaDB...")
    
    total = 0
    
    # 导入时间线
    count = import_sudongpo_timeline()
    total += count
    
    # 导入诗词
    count = import_sudongpo_poems()
    total += count
    
    # 导入地点
    count = import_sudongpo_locations()
    total += count
    
    logger.info(f"\n✅ 全部导入完成！总计: {total}条数据")
    
    # 验证
    logger.info("\n🔍 验证导入结果...")
    rag = get_rag_engine()
    stats = rag.get_stats()
    logger.info(f"数据库总量: {stats['total_guides']}")
    
    # 测试检索
    logger.info("\n🧪 测试检索...")
    results = rag.search("黄州赤壁", n_results=3)
    logger.info(f"检索'黄州赤壁'找到 {len(results)} 条结果")
    for i, r in enumerate(results, 1):
        logger.info(f"{i}. {r['id']} - {r['content'][:100]}...")


if __name__ == '__main__':
    main()
