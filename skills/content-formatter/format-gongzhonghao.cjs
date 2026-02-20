#!/usr/bin/env node
/**
 * 公众号排版工具
 * 用法: node format-gongzhonghao.js input.md > output.html
 */

const fs = require('fs');

function formatGongzhonghao(content) {
  // 转义HTML特殊字符
  function escapeHtml(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  // 处理标题
  content = content.replace(/^# (.+)$/gm, (match, p1) => {
    return `<h1>${escapeHtml(p1)}</h1>`;
  });
  
  content = content.replace(/^## (.+)$/gm, (match, p1) => {
    return `<h2>${escapeHtml(p1)}</h2>`;
  });
  
  content = content.replace(/^### (.+)$/gm, (match, p1) => {
    return `<h3>${escapeHtml(p1)}</h3>`;
  });

  // 处理引用块
  content = content.replace(/^> (.+)$/gm, (match, p1) => {
    return `<blockquote>${escapeHtml(p1)}</blockquote>`;
  });

  // 处理粗体
  content = content.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  // 处理斜体
  content = content.replace(/\*(.+?)\*/g, '<em>$1</em>');

  // 处理列表
  content = content.replace(/^- (.+)$/gm, '<li>$1</li>');
  content = content.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

  // 处理段落
  const lines = content.split('\n');
  let inParagraph = false;
  let result = [];
  
  for (let line of lines) {
    line = line.trim();
    
    if (!line) {
      if (inParagraph) {
        result.push('</p>');
        inParagraph = false;
      }
      continue;
    }
    
    // 如果是HTML标签开头，直接添加
    if (line.startsWith('<')) {
      if (inParagraph) {
        result.push('</p>');
        inParagraph = false;
      }
      result.push(line);
    } else {
      // 普通文本行
      if (!inParagraph) {
        result.push('<p>');
        inParagraph = true;
      }
      result.push(line);
    }
  }
  
  if (inParagraph) {
    result.push('</p>');
  }
  
  content = result.join('\n');

  // 生成完整HTML
  const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>公众号文章</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            line-height: 1.8;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }
        
        .container {
            max-width: 750px;
            margin: 0 auto;
            background: white;
            padding: 40px 30px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        }
        
        h1 {
            font-size: 24px;
            line-height: 1.5;
            color: #2c3e50;
            margin-bottom: 30px;
            font-weight: 600;
        }
        
        h2 {
            font-size: 20px;
            color: #2c3e50;
            margin: 40px 0 20px;
            font-weight: 600;
            border-left: 4px solid #20B2AA;
            padding-left: 15px;
        }
        
        h3 {
            font-size: 18px;
            color: #34495e;
            margin: 30px 0 15px;
            font-weight: 600;
        }
        
        p {
            margin-bottom: 20px;
            text-align: justify;
        }
        
        blockquote {
            background: #f9f9f9;
            border-left: 4px solid #20B2AA;
            padding: 15px 20px;
            margin: 20px 0;
            color: #555;
            font-style: italic;
        }
        
        strong {
            font-weight: 600;
            color: #2c3e50;
        }
        
        ul {
            margin: 15px 0 15px 30px;
        }
        
        li {
            margin-bottom: 10px;
        }
        
        hr {
            border: none;
            border-top: 1px solid #eee;
            margin: 40px 0;
        }
        
        .image-placeholder {
            background: #f0f0f0;
            color: #999;
            padding: 60px 20px;
            text-align: center;
            margin: 30px 0;
            font-size: 14px;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
${content}
    </div>
</body>
</html>`;

  return html;
}

// 主程序
const inputFile = process.argv[2];

if (!inputFile) {
  console.error('用法: node format-gongzhonghao.js <input-file>');
  process.exit(1);
}

try {
  const content = fs.readFileSync(inputFile, 'utf-8');
  const html = formatGongzhonghao(content);
  console.log(html);
} catch (err) {
  console.error('错误:', err.message);
  process.exit(1);
}
