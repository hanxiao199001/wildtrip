#!/usr/bin/env node
/**
 * 小红书内容批量生成
 * 目标：生成100篇爆款小红书笔记内容
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');

const API_BASE = 'http://localhost:5000/api';
const OUTPUT_DIR = './xiaohongshu-content';

// 🔥 热门城市列表
const cities = [
  '北京', '上海', '广州', '深圳', '成都', '杭州', '重庆', '西安', '苏州', '武汉',
  '南京', '厦门', '三亚', '丽江', '大理', '桂林', '青岛', '长沙', '郑州', '天津',
  '福州', '哈尔滨', '济南', '南宁', '昆明', '太原', '兰州', '海口', '珠海', '威海'
];

// 🔥 小红书爆款标题模板
const titleTemplates = [
  // 公式1：城市+天数+人群+痛点
  '{city}{days}天{days-1}夜｜本地人私藏路线，避开所有网红店',
  '{city}{days}日游｜带父母玩转{city}，老人小孩都适合',
  '{city}穷游攻略｜人均{budget}玩转{city}，超详细！',
  
  // 公式2：数字+反常识+悬念
  '去了{times}次{city}，这{highlights}个地方游客根本不知道',
  '{city}旅游避坑指南｜{highlights}条建议，能省一半钱',
  '{city}美食清单｜{highlights}家店，本地人从小吃到大',
  
  // 公式3：情绪+场景+解决方案
  '受够了人挤人！这份{city}冷门攻略我先收藏了',
  '{city}周末游｜2天1夜说走就走，治愈emo的宝藏路线',
  '{city}真的绝了！{days}天玩出{budget}元的快乐',
  
  // 公式4：对比+颠覆认知
  '{city}旅游别再去XX了！本地人都去这{highlights}个地方',
  '{city}{days}天实测｜网红店vs本地店，差距惊人',
  '{city}攻略被骗了{times}次后，我总结了这份避坑指南'
];

// 攻略类型配置
const guideTypes = [
  { days: 2, budget: 800, type: '周末游' },
  { days: 3, budget: 1500, type: '深度游' },
  { days: 4, budget: 2500, type: '休闲游' },
  { days: 5, budget: 3500, type: '全景游' }
];

// 人群标签
const audiences = ['亲子', '情侣', '闺蜜', '独行', '带父母', '学生党'];

// 生成小红书风格标题
function generateXHSTitle(city, config) {
  const template = titleTemplates[Math.floor(Math.random() * titleTemplates.length)];
  const times = Math.floor(Math.random() * 5) + 3; // 3-8次
  const highlights = Math.floor(Math.random() * 3) + 3; // 3-6个
  
  return template
    .replace(/{city}/g, city)
    .replace(/{days}/g, config.days)
    .replace(/{days-1}/g, config.days - 1)
    .replace(/{budget}/g, config.budget)
    .replace(/{times}/g, times)
    .replace(/{highlights}/g, highlights);
}

// 生成小红书风格简介
function generateXHSIntro(city, config, audience) {
  const intros = [
    `🌟 ${city}${config.days}天超全攻略来啦！\n💰 人均${config.budget}元，${audience}出游必看！\n📍 含吃住行玩全攻略+避坑指南\n🎁 文末有野游记小程序链接，30秒生成专属路线~`,
    
    `💡 ${city}本地人整理的${config.days}天攻略\n✨ ${audience}友好，预算${config.budget}左右\n🔥 小众景点+美食推荐+住宿指南\n📲 想要完整版？搜索【野游记】小程序，输入城市直接生成`,
    
    `📖 ${city}${config.days}日游保姆级攻略！\n👥 超适合${audience}出游\n💸 实测人均${config.budget}元搞定\n⚠️ 避坑tips都在这了！\n🔗 完整攻略戳👉野游记小程序`,
  ];
  
  return intros[Math.floor(Math.random() * intros.length)];
}

// 生成引流话术
function generateDrainageTips() {
  return {
    comment: [
      '🔥 完整攻略太长放不下，VX搜【野游记】小程序，输入城市直接生成',
      '💡 想要定制路线？搜索野游记小程序，30秒生成专属攻略',
      '📲 攻略生成神器推荐！野游记小程序，AI帮你规划路线'
    ],
    bio: '🔥 30秒生成专属攻略 → 野游记小程序',
    imageText: [
      '完整版攻略 → 野游记小程序',
      '更多城市攻略 → 搜索"野游记"',
      '定制你的专属路线 → 野游记'
    ]
  };
}

// 提取攻略亮点（从生成的攻略中）
function extractHighlights(guideContent) {
  // 简单提取：找出景点、美食、住宿推荐
  const highlights = [];
  
  // 正则匹配景点名称（示例）
  const attractions = guideContent.match(/(?:前往|参观|游览)([^，。\n]+)/g) || [];
  highlights.push(...attractions.slice(0, 3));
  
  // 正则匹配美食
  const foods = guideContent.match(/(?:品尝|美食|特色)([^，。\n]+)/g) || [];
  highlights.push(...foods.slice(0, 2));
  
  return highlights.slice(0, 5);
}

// 生成攻略并转换为小红书内容
async function generateXHSContent(city, config) {
  try {
    const audience = audiences[Math.floor(Math.random() * audiences.length)];
    const query = `${city}${config.days}天${config.type}，预算${config.budget}，${audience}出游`;
    
    console.log(`  📝 生成: ${query}`);
    
    // 1. 调用API生成攻略
    const taskResponse = await axios.post(`${API_BASE}/generate`, {
      query,
      mode: 'full',
      options: {}
    });
    
    const taskId = taskResponse.data.task_id;
    
    // 2. 等待任务完成
    let result = null;
    for (let i = 0; i < 90; i++) {
      await new Promise(resolve => setTimeout(resolve, 2000));
      const statusResponse = await axios.get(`${API_BASE}/task/${taskId}`);
      
      if (statusResponse.data.status === 'completed') {
        result = statusResponse.data.result;
        break;
      } else if (statusResponse.data.status === 'failed') {
        throw new Error(statusResponse.data.error);
      }
    }
    
    if (!result) {
      throw new Error('任务超时');
    }
    
    // 3. 生成小红书内容
    const xhsTitle = generateXHSTitle(city, config);
    const xhsIntro = generateXHSIntro(city, config, audience);
    const highlights = extractHighlights(result.content || '');
    const drainageTips = generateDrainageTips();
    
    return {
      success: true,
      data: {
        city,
        title: xhsTitle,
        intro: xhsIntro,
        highlights,
        guideUrl: result.web_url,
        guideId: result.guide_id,
        stats: result.stats,
        drainageTips,
        fullGuide: result.content,
        tags: [
          `#${city}旅游攻略`,
          `#${city}${config.days}日游`,
          `#${audience}出游`,
          '#旅行攻略',
          '#野游记'
        ]
      }
    };
    
  } catch (error) {
    console.error(`  ❌ 生成失败: ${error.message}`);
    return { success: false, error: error.message };
  }
}

// 保存为Markdown文件
function saveToMarkdown(content, filename) {
  const md = `# ${content.title}

## 📋 基本信息
- 🏙️ 目的地：${content.city}
- 👥 适合人群：${content.tags.find(t => t.includes('出游'))}
- 💰 预算参考：${content.intro.match(/\d+元/)?.[0] || '见正文'}
- 🔗 攻略链接：${content.guideUrl}

## ✨ 小红书文案

${content.intro}

## 🎯 内容亮点
${content.highlights.map((h, i) => `${i + 1}. ${h}`).join('\n')}

## 🏷️ 推荐标签
${content.tags.join(' ')}

## 💬 引流话术

### 评论区自动回复
${content.drainageTips.comment.map((c, i) => `${i + 1}. ${c}`).join('\n')}

### 个人简介
${content.drainageTips.bio}

### 图片文字
${content.drainageTips.imageText.map((t, i) => `${i + 1}. ${t}`).join('\n')}

## 📊 数据统计
- 字数：${content.stats?.word_count || 0}
- 酒店：${content.stats?.hotels_count || 0}家
- 餐厅：${content.stats?.restaurants_count || 0}家
- 景点：${content.stats?.attractions_count || 0}个

---

**完整攻略：** ${content.guideUrl}

**生成时间：** ${new Date().toLocaleString('zh-CN')}
`;

  fs.writeFileSync(filename, md, 'utf-8');
}

// 批量生成
async function batchGenerate(count = 30) {
  console.log(`🚀 开始批量生成小红书内容 (${count}篇)...`);
  console.log('');
  
  // 创建输出目录
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }
  
  let completed = 0;
  let failed = 0;
  const results = [];
  
  for (let i = 0; i < count && i < cities.length; i++) {
    const city = cities[i];
    const config = guideTypes[i % guideTypes.length];
    
    console.log(`\n[${i + 1}/${count}] ${city} - ${config.type}`);
    
    const result = await generateXHSContent(city, config);
    
    if (result.success) {
      completed++;
      results.push(result.data);
      
      // 保存为Markdown
      const filename = path.join(OUTPUT_DIR, `${city}_${config.days}天_${Date.now()}.md`);
      saveToMarkdown(result.data, filename);
      
      console.log(`  ✅ 成功 | ${result.data.stats?.word_count || 0}字 | 已保存`);
    } else {
      failed++;
      console.log(`  ❌ 失败: ${result.error}`);
    }
    
    // 进度
    console.log(`  进度: ${completed + failed}/${count} | 成功: ${completed} | 失败: ${failed}`);
    
    // 休息3秒，避免过载
    if (i + 1 < count) {
      await new Promise(resolve => setTimeout(resolve, 3000));
    }
  }
  
  // 生成汇总文件
  const summaryPath = path.join(OUTPUT_DIR, '_汇总.json');
  fs.writeFileSync(summaryPath, JSON.stringify(results, null, 2), 'utf-8');
  
  console.log('\n' + '='.repeat(60));
  console.log(`🎉 批量生成完成！`);
  console.log(`总数: ${count} | 成功: ${completed} | 失败: ${failed}`);
  console.log(`成功率: ${(completed / count * 100).toFixed(1)}%`);
  console.log(`输出目录: ${OUTPUT_DIR}`);
  console.log('='.repeat(60));
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  const count = parseInt(args[0]) || 30;
  
  await batchGenerate(count);
}

main().catch(console.error);
