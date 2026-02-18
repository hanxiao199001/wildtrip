# 内容排版工具

专门为公众号和小红书优化内容格式的工具。

## 功能

### 1. 公众号格式 (format-gongzhonghao.cjs)

**输出：** HTML文件，带完整样式

**特点：**
- 移动端优化（最大宽度750px）
- 清晰的标题层级
- 引用块高亮
- 列表格式化
- 可直接在浏览器打开预览

**使用方法：**
```bash
node format-gongzhonghao.cjs input.md > output.html
# 在浏览器打开output.html
# Ctrl+A全选 → Ctrl+C复制 → 粘贴到公众号编辑器
```

### 2. 小红书格式 (format-xiaohongshu.cjs)

**输出：** 纯文本，带emoji和视觉分隔

**特点：**
- Emoji点缀（📌✅💡）
- 短段落（易读）
- 视觉分隔符
- 自动添加话题标签
- CTA引导（评论/点赞）

**使用方法：**
```bash
node format-xiaohongshu.cjs input.md > output.txt
# 复制output.txt内容 → 粘贴到小红书app
```

## 示例

详见 `example.md` → 运行工具查看效果

## 在对话中使用

直接告诉我：
- "用公众号格式排版这篇文章"
- "转成小红书格式"

我会自动调用这个skill处理。
