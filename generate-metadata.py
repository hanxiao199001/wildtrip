#!/usr/bin/env python3
"""
扫描现有攻略HTML文件，生成 metadata.json
用于小程序首页"精选攻略"展示
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime

def extract_info_from_html(html_path):
    """从HTML文件提取元数据"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取标题
    title_match = re.search(r'<title>([^<]+)</title>', content)
    title = title_match.group(1) if title_match else Path(html_path).stem
    title = title.replace(' - 野游记 WildTrip', '').strip()
    
    # 提取目的地
    dest_match = re.search(r'目的地[：:]\s*([^<\n]+)', content)
    destination = dest_match.group(1).strip() if dest_match else ''
    
    # 提取天数
    days_match = re.search(r'(\d+)天', content)
    days = int(days_match.group(1)) if days_match else 0
    
    # 提取预算
    budget_match = re.search(r'预算[：:]\s*[¥￥]?(\d+[-~]?\d*)', content)
    budget = budget_match.group(1) if budget_match else ''
    
    # 提取第一张图片（如果有）
    img_match = re.search(r'<img[^>]+src="([^"]+)"', content)
    cover_image = img_match.group(1) if img_match else None
    
    # 如果没有图片，用 Unsplash 占位图
    if not cover_image and destination:
        cover_image = f'https://source.unsplash.com/800x600/?{destination},travel,landscape'
    elif not cover_image:
        cover_image = 'https://source.unsplash.com/800x600/?travel,adventure'
    
    # 从文件名提取slug
    slug = Path(html_path).stem
    
    # 提取时间戳（从文件名）
    timestamp_match = re.search(r'-(\d{12})-', slug)
    if timestamp_match:
        timestamp_str = timestamp_match.group(1)
        # 格式：202602051054 -> 2026-02-05 10:54
        created_at = f"{timestamp_str[0:4]}-{timestamp_str[4:6]}-{timestamp_str[6:8]} {timestamp_str[8:10]}:{timestamp_str[10:12]}"
    else:
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 生成ID（从文件名提取hash部分）
    id_match = re.search(r'-([a-f0-9]{8})\.html$', slug)
    guide_id = id_match.group(1) if id_match else slug[-8:]
    
    return {
        'id': guide_id,
        'slug': slug,
        'title': title,
        'destination': destination,
        'cover_image': cover_image,
        'days': days,
        'budget': budget,
        'views': 0,
        'likes': 0,
        'created_at': created_at
    }

def main():
    guides_dir = Path('/root/clawd/web/guides')
    metadata = []
    
    # 扫描所有HTML文件（排除index.html）
    for html_file in guides_dir.glob('*.html'):
        if html_file.name == 'index.html':
            continue
        
        try:
            info = extract_info_from_html(html_file)
            metadata.append(info)
            print(f"✅ {info['title']}")
        except Exception as e:
            print(f"❌ {html_file.name}: {e}")
    
    # 按时间倒序排序
    metadata.sort(key=lambda x: x['created_at'], reverse=True)
    
    # 保存到 metadata.json
    output_file = guides_dir / 'metadata.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 生成完成！共 {len(metadata)} 条攻略")
    print(f"📄 文件位置: {output_file}")
    
    # 显示前5条预览
    print("\n📋 前5条预览:")
    for item in metadata[:5]:
        print(f"  - {item['title']} | {item['destination']} | {item['days']}天 | ¥{item['budget']}")

if __name__ == '__main__':
    main()
