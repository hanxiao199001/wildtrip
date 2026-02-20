#!/usr/bin/env node
/**
 * 小红书排版工具
 * 用法: node format-xiaohongshu.js input.md > output.txt
 */

const fs = require('fs');

function formatXiaohongshu(content) {
  let result = [];
  
  // 移除Markdown标记但保留内容
  content = content.replace(/^#{1,6} /gm, '');
  content = content.replace(/\*\*/g, '');
  content = content.replace(/\*/g, '');
  
  // 分段处理
  const paragraphs = content.split('\n\n').filter(p => p.trim());
  
  for (let i = 0; i < paragraphs.length; i++) {
    let para = paragraphs[i].trim();
    
    // 跳过空段落
    if (!para) continue;
    
    // 标题变大emoji
    if (i === 0) {
      result.push(`📌 ${para}`);
      result.push('');
      continue;
    }
    
    // 检测是否是列表
    if (para.includes('\n- ') || para.startsWith('- ')) {
      const items = para.split('\n').filter(l => l.trim());
      items.forEach(item => {
        item = item.replace(/^- /, '');
        result.push(`✅ ${item}`);
      });
      result.push('');
      continue;
    }
    
    // 检测是否是引用
    if (para.startsWith('>')) {
      para = para.replace(/^> ?/gm, '');
      result.push(`💡 ${para}`);
      result.push('');
      continue;
    }
    
    // 普通段落 - 拆分长段落
    const lines = para.split('\n');
    let currentPara = [];
    
    for (let line of lines) {
      line = line.trim();
      if (!line) continue;
      
      currentPara.push(line);
      
      // 每3-5行分一段
      if (currentPara.length >= 3) {
        result.push(currentPara.join('\n'));
        result.push('');
        currentPara = [];
      }
    }
    
    // 剩余的行
    if (currentPara.length > 0) {
      result.push(currentPara.join('\n'));
      result.push('');
    }
  }
  
  // 添加分隔符（每几段加一个）
  const withDividers = [];
  for (let i = 0; i < result.length; i++) {
    withDividers.push(result[i]);
    
    // 每隔5个非空段落加一个分隔符
    if (result[i] && i > 0 && i % 10 === 0) {
      withDividers.push('- - - - -');
      withDividers.push('');
    }
  }
  
  // 末尾添加常见CTA
  withDividers.push('');
  withDividers.push('———');
  withDividers.push('');
  withDividers.push('💬 你有什么想法？评论区聊聊');
  withDividers.push('');
  withDividers.push('❤️ 觉得有用就点个赞吧');
  withDividers.push('');
  withDividers.push('#旅行 #攻略 #深度游 #人文旅行');
  
  return withDividers.join('\n');
}

// 主程序
const inputFile = process.argv[2];

if (!inputFile) {
  console.error('用法: node format-xiaohongshu.js <input-file>');
  process.exit(1);
}

try {
  const content = fs.readFileSync(inputFile, 'utf-8');
  const formatted = formatXiaohongshu(content);
  console.log(formatted);
} catch (err) {
  console.error('错误:', err.message);
  process.exit(1);
}
