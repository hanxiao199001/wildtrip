#!/usr/bin/env python3
"""
生成 guides 目录的索引页面
"""

import sys
sys.path.insert(0, '/root/clawd/wildtrip-existing/backend')

from pathlib import Path
import re
from datetime import datetime


def extract_title_from_html(html_file: Path) -> str:
    """从HTML提取标题"""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 提取 <title> 标签
        title_match = re.search(r'<title>([^<]+)</title>', content)
        if title_match:
            title = title_match.group(1)
            # 移除后缀
            title = title.replace(' - 野游记AI攻略 | 不走寻常路的旅行指南', '')
            title = title.replace(' - 野游记AI攻略', '')
            return title.strip()
        
        # 提取第一个 <h1>
        h1_match = re.search(r'<h1>([^<]+)</h1>', content)
        if h1_match:
            return h1_match.group(1).strip()
        
        return html_file.stem
        
    except Exception as e:
        return html_file.stem


def generate_index():
    """生成索引页面"""
    guides_dir = Path("/root/clawd/web/guides")
    
    # 获取所有攻略文件
    guides = []
    for html_file in guides_dir.glob("guide-*.html"):
        if 'test' in html_file.name:
            continue  # 跳过测试文件
            
        title = extract_title_from_html(html_file)
        mtime = html_file.stat().st_mtime
        
        guides.append({
            'filename': html_file.name,
            'title': title,
            'mtime': mtime,
            'date': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
        })
    
    # 按时间倒序
    guides.sort(key=lambda x: x['mtime'], reverse=True)
    
    # 生成HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>野游记攻略列表 - 最新旅游攻略</title>
    <meta name="description" content="野游记AI生成的个性化旅游攻略，覆盖海口、三亚等热门目的地">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(to bottom right, #fff5e6, #ffffff, #e6f3ff);
        }}
        
        h1 {{
            color: #ff6b35;
            text-align: center;
            margin-bottom: 40px;
        }}
        
        .stats {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }}
        
        .guides-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .guide-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .guide-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }}
        
        .guide-title {{
            font-size: 16px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 10px;
            line-height: 1.4;
        }}
        
        .guide-meta {{
            font-size: 12px;
            color: #999;
            margin-bottom: 15px;
        }}
        
        .guide-link {{
            display: inline-block;
            padding: 8px 16px;
            background: linear-gradient(135deg, #ff6b35, #ff8c00);
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-size: 14px;
            transition: opacity 0.2s;
        }}
        
        .guide-link:hover {{
            opacity: 0.9;
        }}
        
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            color: #ff6b35;
            text-decoration: none;
        }}
        
        .back-link:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <a href="/" class="back-link">← 返回首页</a>
    
    <h1>🌴 野游记攻略列表</h1>
    
    <div class="stats">
        共 {len(guides)} 篇攻略 | 持续更新中
    </div>
    
    <div class="guides-grid">
"""
    
    for guide in guides:
        html += f"""        <div class="guide-card">
            <div class="guide-title">{guide['title']}</div>
            <div class="guide-meta">📅 {guide['date']}</div>
            <a href="/guides/{guide['filename']}" class="guide-link">查看攻略 →</a>
        </div>
"""
    
    html += """    </div>
    
    <div style="text-align: center; margin-top: 40px; color: #999; font-size: 14px;">
        <p>由野游记AI自动生成 | <a href="/" style="color: #ff6b35;">生成你的专属攻略</a></p>
    </div>
</body>
</html>
"""
    
    # 保存
    index_file = guides_dir / "index.html"
    index_file.write_text(html, encoding='utf-8')
    
    print(f"✅ 索引页面已生成: {index_file}")
    print(f"📊 共 {len(guides)} 篇攻略")


if __name__ == '__main__':
    generate_index()
