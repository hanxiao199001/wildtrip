#!/usr/bin/env python3
"""
清理所有攻略 HTML 文件：
1. 删除所有美团预订 booking-card div
2. 删除所有带美团链接的 Schema.org Restaurant div
3. 删除整个"住宿推荐"section（从 <h2>🏨 住宿推荐 到下一个 --- 分隔线）
"""
import re
import glob
import os

GUIDES_DIR = "/root/clawd/web/guides"

def clean_html(content):
    # 1. 删除 booking-card div（包含 meituan 链接的）
    # 匹配 <div class="booking-card">...</div>（可能多行）
    content = re.sub(
        r'<div class="booking-card">.*?</div>\s*',
        '',
        content,
        flags=re.DOTALL
    )

    # 2. 删除 Schema.org Restaurant div（整个 itemscope 块）
    content = re.sub(
        r'<div\s+itemscope\s+itemtype="https://schema\.org/(?:Restaurant|LocalBusiness)"[^>]*>.*?</div>\s*',
        '',
        content,
        flags=re.DOTALL
    )

    # 3. 删除"← 🔥省¥..." 之类的尾随促销文本行
    content = re.sub(r'\s*←\s*🔥[^\n]*\n?', '\n', content)

    # 4. 删除整个"住宿推荐"section
    # 从 <h2> 含 "住宿推荐" 开始，到下一个 <hr> 或 "---" 分隔线之前
    # 常见格式：<h2>🏨 住宿推荐......</h2> ... <hr> 或 <p>---</p>
    content = re.sub(
        r'<h2>[^<]*住宿推荐[^<]*</h2>.*?(?=<h2>|<hr\s*/?>|<p>\s*---\s*</p>)',
        '',
        content,
        flags=re.DOTALL
    )

    # 清理多余空行（连续3行以上空行压缩为2行）
    content = re.sub(r'\n{3,}', '\n\n', content)

    return content

files = sorted(glob.glob(os.path.join(GUIDES_DIR, "guide-*.html")))
print(f"找到 {len(files)} 个攻略文件")

modified = 0
for path in files:
    with open(path, 'r', encoding='utf-8') as f:
        original = f.read()
    
    cleaned = clean_html(original)
    
    if cleaned != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        orig_size = len(original)
        new_size = len(cleaned)
        print(f"  ✅ {os.path.basename(path)}  {orig_size} → {new_size} bytes (-{orig_size - new_size})")
        modified += 1
    else:
        print(f"  — {os.path.basename(path)}  (无变化)")

print(f"\n完成：{modified}/{len(files)} 个文件已修改")
