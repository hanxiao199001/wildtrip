#!/usr/bin/env node
/**
 * 图片抓取工具 - 从免费图库下载图片
 * 用法: node fetch-image.cjs "关键词" --output ./images/
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
  unsplash: {
    // Demo access key (公开，限流50次/小时)
    accessKey: 'demo-access-key',
    apiUrl: 'https://api.unsplash.com'
  },
  pexels: {
    // Demo key
    apiKey: 'demo-key',
    apiUrl: 'https://api.pexels.com'
  },
  output: './images/',
  orientation: 'landscape' // landscape, portrait, square
};

// 加载自定义配置
function loadConfig() {
  try {
    const configPath = path.join(__dirname, 'image-config.json');
    if (fs.existsSync(configPath)) {
      const custom = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
      Object.assign(CONFIG.unsplash, custom.unsplash || {});
      Object.assign(CONFIG.pexels, custom.pexels || {});
      if (custom.output) CONFIG.output = custom.output;
      if (custom.orientation) CONFIG.orientation = custom.orientation;
    }
  } catch (err) {
    // 使用默认配置
  }
}

// 从Unsplash搜索图片
async function searchUnsplash(query, count = 5) {
  return new Promise((resolve, reject) => {
    const url = `https://api.unsplash.com/search/photos?query=${encodeURIComponent(query)}&per_page=${count}&orientation=${CONFIG.orientation}`;
    
    const options = {
      headers: {
        'Authorization': `Client-ID ${CONFIG.unsplash.accessKey}`
      }
    };

    https.get(url, options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          if (json.results && json.results.length > 0) {
            resolve(json.results.map(img => ({
              id: img.id,
              url: img.urls.regular,
              download_url: img.links.download,
              author: img.user.name,
              author_url: img.user.links.html,
              description: img.description || img.alt_description || query,
              source: 'Unsplash'
            })));
          } else {
            resolve([]);
          }
        } catch (err) {
          reject(err);
        }
      });
    }).on('error', reject);
  });
}

// 从Pexels搜索图片
async function searchPexels(query, count = 5) {
  return new Promise((resolve, reject) => {
    const url = `https://api.pexels.com/v1/search?query=${encodeURIComponent(query)}&per_page=${count}&orientation=${CONFIG.orientation}`;
    
    const options = {
      headers: {
        'Authorization': CONFIG.pexels.apiKey
      }
    };

    https.get(url, options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          if (json.photos && json.photos.length > 0) {
            resolve(json.photos.map(img => ({
              id: img.id,
              url: img.src.large,
              download_url: img.src.original,
              author: img.photographer,
              author_url: img.photographer_url,
              description: query,
              source: 'Pexels'
            })));
          } else {
            resolve([]);
          }
        } catch (err) {
          reject(err);
        }
      });
    }).on('error', reject);
  });
}

// 下载图片
async function downloadImage(url, filepath) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(filepath);
    
    https.get(url, (response) => {
      response.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve(filepath);
      });
    }).on('error', (err) => {
      fs.unlink(filepath, () => {});
      reject(err);
    });
  });
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help') {
    console.log(`
用法: node fetch-image.cjs "关键词" [选项]

选项:
  --output <dir>      输出目录 (默认: ./images/)
  --count <n>         下载数量 (默认: 5)
  --source <name>     图库选择 (unsplash/pexels/auto, 默认: auto)
  --orientation <o>   方向 (landscape/portrait/square, 默认: landscape)

示例:
  node fetch-image.cjs "West Lake sunset"
  node fetch-image.cjs "赤壁长江" --count 3 --source unsplash
    `);
    process.exit(0);
  }

  loadConfig();

  const query = args[0];
  let output = CONFIG.output;
  let count = 5;
  let source = 'auto';

  // 解析参数
  for (let i = 1; i < args.length; i += 2) {
    if (args[i] === '--output') output = args[i + 1];
    if (args[i] === '--count') count = parseInt(args[i + 1]);
    if (args[i] === '--source') source = args[i + 1];
    if (args[i] === '--orientation') CONFIG.orientation = args[i + 1];
  }

  // 创建输出目录
  if (!fs.existsSync(output)) {
    fs.mkdirSync(output, { recursive: true });
  }

  console.log(`🔍 搜索图片: "${query}"`);
  console.log(`📁 输出目录: ${output}`);
  console.log(`🔢 数量: ${count}\n`);

  let images = [];

  try {
    // 搜索图片
    if (source === 'unsplash' || source === 'auto') {
      console.log('📸 从 Unsplash 搜索...');
      const unsplashResults = await searchUnsplash(query, count);
      images = images.concat(unsplashResults);
    }

    if ((source === 'pexels' || source === 'auto') && images.length < count) {
      console.log('📸 从 Pexels 搜索...');
      const pexelsResults = await searchPexels(query, count - images.length);
      images = images.concat(pexelsResults);
    }

    if (images.length === 0) {
      console.log('❌ 未找到图片');
      process.exit(1);
    }

    console.log(`✅ 找到 ${images.length} 张图片\n`);

    // 下载图片
    const metadata = [];
    const slug = query.toLowerCase().replace(/[^a-z0-9\u4e00-\u9fa5]+/g, '-');

    for (let i = 0; i < Math.min(images.length, count); i++) {
      const img = images[i];
      const filename = `${slug}-${i + 1}.jpg`;
      const filepath = path.join(output, filename);

      console.log(`⬇️  下载 ${i + 1}/${count}: ${img.description || ''}...`);
      
      try {
        await downloadImage(img.url, filepath);
        console.log(`   ✅ 已保存: ${filepath}`);
        
        metadata.push({
          filename,
          source: img.source,
          author: img.author,
          author_url: img.author_url,
          description: img.description,
          license: 'Free to use (商业使用免费)',
          credit: `Photo by ${img.author} on ${img.source}`
        });
      } catch (err) {
        console.log(`   ❌ 下载失败: ${err.message}`);
      }
    }

    // 保存元数据
    const metaPath = path.join(output, `${slug}-metadata.json`);
    fs.writeFileSync(metaPath, JSON.stringify(metadata, null, 2));
    console.log(`\n📋 元数据已保存: ${metaPath}`);
    console.log('\n🎉 完成！');

  } catch (err) {
    console.error('❌ 错误:', err.message);
    process.exit(1);
  }
}

// 导出函数供其他脚本使用
module.exports = {
  searchUnsplash,
  searchPexels,
  downloadImage,
  CONFIG
};

// 如果直接运行
if (require.main === module) {
  main();
}
