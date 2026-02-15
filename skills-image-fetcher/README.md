# 图片抓取机器人 🤖

自动从免费图库（Unsplash、Pexels）下载高质量配图。

## 快速开始

### 1. 下载单张图片
```bash
node fetch-image.cjs "West Lake sunset" --output ./images/
```

### 2. 批量下载（用配置文件）
```bash
node fetch-article-images.cjs article.md --config dongpo-images.json
```

### 3. 自动模式（从文章提取）
在文章中用 `［配图：描述］` 标记需要图片的位置：

```markdown
# 杭州西湖

［配图：西湖苏堤清晨］

美丽的西湖...
```

然后运行：
```bash
node fetch-article-images.cjs article.md --auto
```

## 配置API密钥（可选，提升速度）

### 免费注册获取：
1. **Unsplash**: https://unsplash.com/oauth/applications
2. **Pexels**: https://www.pexels.com/api/

### 配置文件 `image-config.json`：
```json
{
  "unsplash": {
    "accessKey": "你的Unsplash密钥"
  },
  "pexels": {
    "apiKey": "你的Pexels密钥"
  },
  "output": "./images/",
  "orientation": "landscape"
}
```

**不配置也能用**，使用demo模式（限流50次/小时）。

## 苏东坡文章配图示例

已经为你准备好了配置文件 `dongpo-images.json`，直接运行：

```bash
cd /usr/lib/node_modules/clawdbot/skills/image-fetcher
node fetch-article-images.cjs /tmp/sudongpo-original.md --config dongpo-images.json --output ~/dongpo-images/
```

会自动下载11张图片：
- hangzhou-sudike.jpg（西湖苏堤）
- hangzhou-leifeng.jpg（雷峰塔）
- huangzhou-chibi.jpg（赤壁矶）
- ... 等等

## 版权说明

所有图片来自：
- **Unsplash**: 免费商用，无需署名
- **Pexels**: 免费商用，无需署名

下载后会自动生成 `images-metadata.json`，包含：
- 摄影师姓名
- 图片来源链接
- 使用许可

## 在对话中使用

直接告诉我：
> "帮我为苏东坡文章下载配图"
> "找10张西湖相关的免费图片"

我会自动调用这个工具。

## 故障排除

**问题：搜索不到图片**
- 尝试用英文关键词
- 换个描述方式，更具体或更宽泛
- 尝试不同的图库（--source pexels）

**问题：下载失败**
- 检查网络连接
- 确认输出目录有写权限
- API限流了，等一小时或配置密钥

## 高级用法

### 批量下载多个关键词
```bash
for keyword in "West Lake" "Red Cliff" "Huizhou"; do
  node fetch-image.cjs "$keyword" --count 3
done
```

### 只搜索不下载（预览）
修改脚本，注释掉下载部分，只打印结果。

### 自定义文件命名
编辑 `fetch-article-images.cjs` 的 `filename` 生成逻辑。
