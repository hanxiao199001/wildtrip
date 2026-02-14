#!/usr/bin/env node
/**
 * SEO批量生成 - 自动生成100+热门城市攻略
 * 目标：提高百度收录，获取自然流量
 */

const axios = require('axios');

const API_BASE = 'http://localhost:5000/api';

// 🔥 热门城市列表（100个）
const cities = [
  // 一线城市
  '北京', '上海', '广州', '深圳',
  
  // 新一线城市
  '成都', '杭州', '重庆', '西安', '苏州', '武汉', '南京', '天津', '郑州', '长沙',
  '东莞', '沈阳', '青岛', '合肥', '佛山',
  
  // 二线城市（旅游热门）
  '厦门', '福州', '哈尔滨', '济南', '温州', '南宁', '长春', '泉州', '石家庄', '贵阳',
  '南昌', '金华', '常州', '昆明', '徐州', '太原', '嘉兴', '烟台', '惠州', '保定',
  '台州', '中山', '绍兴', '乌鲁木齐', '潍坊', '兰州',
  
  // 旅游城市
  '三亚', '丽江', '大理', '桂林', '张家界', '黄山', '九寨沟', '峨眉山', '稻城',
  '拉萨', '敦煌', '西双版纳', '丽水', '婺源', '凤凰', '阳朔', '香格里拉', '泸沽湖',
  
  // 沿海城市
  '海口', '珠海', '威海', '秦皇岛', '大连', '青岛', '宁波', '舟山', '湛江', '北海',
  
  // 历史文化城市
  '洛阳', '开封', '西安', '南京', '苏州', '杭州', '绍兴', '扬州', '泉州', '潮州',
  
  // 其他热门
  '银川', '呼和浩特', '南通', '盐城', '淮安', '连云港', '泰州', '镇江', '株洲',
  '湘潭', '岳阳', '常德', '衡阳', '邵阳', '益阳', '郴州', '永州', '怀化', '娄底'
];

// 🔥 攻略模板（多样化）
const templates = [
  '{city}3天游，预算3000',
  '{city}周末2日游',
  '{city}5天深度游',
  '{city}亲子游攻略',
  '{city}情侣游推荐',
  '{city}美食之旅',
  '{city}穷游攻略，1000元玩转',
  '{city}自由行完整攻略',
];

// 生成任务
async function createTask(query) {
  try {
    const response = await axios.post(`${API_BASE}/generate`, {
      query,
      mode: 'full',
      options: {}
    });
    
    return response.data.task_id;
  } catch (error) {
    console.error(`❌ 创建任务失败: ${query}`, error.message);
    return null;
  }
}

// 轮询任务状态
async function waitForTask(taskId, maxWait = 180) {
  const startTime = Date.now();
  
  while (true) {
    try {
      const response = await axios.get(`${API_BASE}/task/${taskId}`);
      const data = response.data;
      
      if (data.status === 'completed') {
        return { success: true, data };
      } else if (data.status === 'failed') {
        return { success: false, error: data.error };
      }
      
      // 超时检查
      if ((Date.now() - startTime) / 1000 > maxWait) {
        return { success: false, error: '超时' };
      }
      
      // 等待2秒再查询
      await new Promise(resolve => setTimeout(resolve, 2000));
      
    } catch (error) {
      console.error(`❌ 查询任务失败: ${taskId}`, error.message);
      return { success: false, error: error.message };
    }
  }
}

// 批量生成
async function batchGenerate(count = 100, concurrency = 1) {
  console.log(`🚀 开始批量生成 ${count} 个攻略...`);
  console.log(`并发数: ${concurrency}`);
  console.log('');
  
  const queries = [];
  
  // 生成查询列表
  for (let i = 0; i < count && i < cities.length; i++) {
    const city = cities[i];
    const template = templates[i % templates.length];
    const query = template.replace('{city}', city);
    queries.push(query);
  }
  
  let completed = 0;
  let failed = 0;
  
  // 分批处理
  for (let i = 0; i < queries.length; i += concurrency) {
    const batch = queries.slice(i, i + concurrency);
    
    console.log(`\n📦 批次 ${Math.floor(i/concurrency) + 1}/${Math.ceil(queries.length/concurrency)}`);
    console.log(`查询: ${batch.join(', ')}`);
    
    // 创建任务
    const taskIds = await Promise.all(
      batch.map(query => createTask(query))
    );
    
    // 等待完成
    const results = await Promise.all(
      taskIds.map(taskId => taskId ? waitForTask(taskId) : null)
    );
    
    // 统计结果
    results.forEach((result, idx) => {
      if (!result) {
        failed++;
        console.log(`  ❌ ${batch[idx]}: 创建失败`);
      } else if (result.success) {
        completed++;
        const stats = result.data.result?.stats || {};
        console.log(`  ✅ ${batch[idx]}: ${stats.word_count || 0}字 | ${stats.hotels_count || 0}酒店`);
      } else {
        failed++;
        console.log(`  ❌ ${batch[idx]}: ${result.error}`);
      }
    });
    
    console.log(`\n进度: ${completed + failed}/${queries.length} | 成功: ${completed} | 失败: ${failed}`);
    
    // 避免过载，休息5秒
    if (i + concurrency < queries.length) {
      console.log('💤 休息5秒...');
      await new Promise(resolve => setTimeout(resolve, 5000));
    }
  }
  
  console.log('\n' + '='.repeat(60));
  console.log(`🎉 批量生成完成！`);
  console.log(`总数: ${queries.length} | 成功: ${completed} | 失败: ${failed}`);
  console.log(`成功率: ${(completed / queries.length * 100).toFixed(1)}%`);
  console.log('='.repeat(60));
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  const count = parseInt(args[0]) || 100;
  const concurrency = parseInt(args[1]) || 1;
  
  await batchGenerate(count, concurrency);
}

main().catch(console.error);
