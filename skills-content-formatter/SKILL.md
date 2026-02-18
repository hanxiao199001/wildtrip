---
name: content-formatter
description: Format articles for WeChat Official Account (公众号) and Xiaohongshu (小红书) with proper styling and emoji.
---

# Content Formatter

Format raw text/markdown into platform-optimized layouts.

## Platforms

### 公众号 (WeChat Official Account)
- HTML output with inline styles
- Clean typography, proper spacing
- Highlight boxes for key quotes
- Mobile-optimized (max-width 750px)

### 小红书 (Xiaohongshu)
- Emoji-rich, eye-catching
- Short paragraphs (3-5 lines max)
- Hashtags at end
- Visual breaks between sections

## Usage

Call `format-gongzhonghao.cjs` or `format-xiaohongshu.cjs` with content file path:

```bash
# 公众号格式
node format-gongzhonghao.cjs input.md > output.html

# 小红书格式  
node format-xiaohongshu.cjs input.md > output.txt
```

Or use directly in conversation:
> "用公众号格式排版这篇文章：[paste content]"
> "把这个转成小红书格式"

## Output

**公众号**: Self-contained HTML file, open in browser → Ctrl+A → copy → paste to editor

**小红书**: Text with emoji, copy-paste directly to Xiaohongshu app

## Tips

- 公众号: Avoid markdown tables, use bullet lists
- 小红书: Lead with hook (悬念/痛点/好奇), end with CTA
- Both: Break long paragraphs, use visual rhythm
