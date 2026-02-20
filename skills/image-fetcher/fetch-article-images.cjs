#!/usr/bin/env node
/**
 * 为文章自动抓取配图
 * 用法: node fetch-article-images.cjs article.md --config images.json
 */

const fs = require('fs');
const path = require('path');
const { searchUnsplash, searchPexels, downloadImage } = require('./fetch-image.cjs');

// 从文章中提取图片需求
function extractImageRequirements(content) {
  const requirements = [];
  
  // 匹配图片占位符格式：［配图：描述］或 ![描述]
  const patterns = [
    /［配图[：:]\s*([^］]+)］/g,
    /\[配图[：:]\s*([^\]]+)\]/g,
    /!\[([^\]]+)\]/g
  ];

  for (const pattern of patterns) {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      requirements.push({
        description: match[1].trim(),
        position: match.index
      });
    }
  }

  return requirements;
}

// 从配置文件读取图片需求
function loadImageConfig(configPath) {
  if (!fs.existsSync(configPath)) {
    throw new Error(`配置文件不存在: ${configPath}`);
  }

  const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
  
  // 配置格式：
  // {
  //   "images": [
  //     {"keyword": "West Lake sunset", "filename": "hangzhou-1.jpg"},
  //     {"keyword": "Red Cliff Yangtze", "filename": "huangzhou-1.jpg"}
  //   ]
  // }
  
  return config.images || [];
}

// 主函数
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === '--help') {
    console.log(`
用法: node fetch-article-images.cjs <文章文件> [选项]

选项:
  --config <file>     图片配置文件 (JSON格式)
  --output <dir>      输出目录 (默认: ./images/)
  --auto              自动从文章中提取图片占位符

配置文件格式 (images.json):
{
  "images": [
    {"keyword": "West Lake sunset", "filename": "hangzhou-1.jpg", "orientation": "landscape"},
    {"keyword": "Red Cliff Yangtze", "filename": "huangzhou-1.jpg"}
  ]
}

示例:
  node fetch-article-images.cjs article.md --config images.json
  node fetch-article-images.cjs article.md --auto --output ./pics/
    `);
    process.exit(0);
  }

  const articlePath = args[0];
  let configPath = null;
  let output = './images/';
  let autoMode = false;

  // 解析参数
  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--config') configPath = args[i + 1];
    if (args[i] === '--output') output = args[i + 1];
    if (args[i] === '--auto') autoMode = true;
  }

  // 读取文章
  if (!fs.existsSync(articlePath)) {
    console.error(`❌ 文章文件不存在: ${articlePath}`);
    process.exit(1);
  }

  const content = fs.readFileSync(articlePath, 'utf-8');

  // 创建输出目录
  if (!fs.existsSync(output)) {
    fs.mkdirSync(output, { recursive: true });
  }

  let imageRequests = [];

  if (autoMode) {
    // 自动模式：从文章中提取
    console.log('🤖 自动模式：从文章中提取图片需求...\n');
    const requirements = extractImageRequirements(content);
    
    if (requirements.length === 0) {
      console.log('❌ 未找到图片占位符');
      console.log('提示：使用格式 ［配图：描述］ 或 ![描述]');
      process.exit(1);
    }

    imageRequests = requirements.map((req, i) => ({
      keyword: req.description,
      filename: `image-${i + 1}.jpg`,
      orientation: 'landscape'
    }));

  } else if (configPath) {
    // 配置文件模式
    console.log(`📋 从配置文件读取: ${configPath}\n`);
    imageRequests = loadImageConfig(configPath);
  } else {
    console.error('❌ 请指定 --config 或使用 --auto 模式');
    process.exit(1);
  }

  console.log(`📸 需要下载 ${imageRequests.length} 张图片\n`);

  const metadata = [];

  // 下载每张图片
  for (let i = 0; i < imageRequests.length; i++) {
    const req = imageRequests[i];
    console.log(`[${i + 1}/${imageRequests.length}] "${req.keyword}"`);

    try {
      // 搜索图片
      let images = await searchUnsplash(req.keyword, 1);
      
      if (images.length === 0) {
        console.log('   尝试 Pexels...');
        images = await searchPexels(req.keyword, 1);
      }

      if (images.length === 0) {
        console.log('   ❌ 未找到图片\n');
        continue;
      }

      const img = images[0];
      const filepath = path.join(output, req.filename);

      // 下载
      await downloadImage(img.url, filepath);
      console.log(`   ✅ 已保存: ${filepath}\n`);

      metadata.push({
        keyword: req.keyword,
        filename: req.filename,
        source: img.source,
        author: img.author,
        author_url: img.author_url,
        credit: `Photo by ${img.author} on ${img.source}`,
        license: 'Free to use'
      });

    } catch (err) {
      console.log(`   ❌ 失败: ${err.message}\n`);
    }
  }

  // 保存元数据
  const metaPath = path.join(output, 'images-metadata.json');
  fs.writeFileSync(metaPath, JSON.stringify(metadata, null, 2));
  
  console.log(`📋 元数据已保存: ${metaPath}`);
  console.log(`\n🎉 完成！下载了 ${metadata.length}/${imageRequests.length} 张图片`);
}

main();
