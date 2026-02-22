#!/usr/bin/env python3
"""
每天定时生成5篇高质量攻略
"""

import os
import sys

# 使用 wildtrip-existing 的服务
sys.path.insert(0, '/root/clawd/wildtrip-existing/backend')

# 🔥 加载环境变量
from pathlib import Path
env_file = Path('/root/clawd/wildtrip-existing/backend/.env')
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

from loguru import logger
from datetime import datetime
import json

# 导入策略引擎
sys.path.insert(0, '/root/clawd/backend/services')
from content_strategy_v2 import ContentStrategyV2


def load_progress():
    """加载生成进度"""
    progress_file = Path("/root/clawd/backend/.generation_progress.json")
    
    if progress_file.exists():
        with open(progress_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            'last_date': None,
            'total_generated': 0,
            'high_index': 0,
            'medium_index': 0,
            'low_index': 0
        }


def save_progress(progress):
    """保存生成进度"""
    progress_file = Path("/root/clawd/backend/.generation_progress.json")
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


def get_today_tasks(strategy: ContentStrategyV2, progress: dict) -> list:
    """
    获取今天要生成的5个任务
    
    优先级分配:
    - 3篇高优先级 (深度场景)
    - 1篇中优先级 (对比决策)
    - 1篇低优先级 (本地生活)
    """
    all_tasks = strategy.get_priority_tasks()
    
    today_tasks = []
    
    # 3篇高优先级
    high_start = progress['high_index']
    high_tasks = all_tasks['high'][high_start:high_start+3]
    today_tasks.extend(high_tasks)
    progress['high_index'] += len(high_tasks)
    
    # 1篇中优先级
    medium_start = progress['medium_index']
    if medium_start < len(all_tasks['medium']):
        today_tasks.append(all_tasks['medium'][medium_start])
        progress['medium_index'] += 1
    
    # 1篇低优先级
    low_start = progress['low_index']
    if low_start < len(all_tasks['low']):
        today_tasks.append(all_tasks['low'][low_start])
        progress['low_index'] += 1
    
    # 如果不够5篇,继续从高优先级补充
    while len(today_tasks) < 5 and progress['high_index'] < len(all_tasks['high']):
        today_tasks.append(all_tasks['high'][progress['high_index']])
        progress['high_index'] += 1
    
    return today_tasks


def generate_guides(tasks: list):
    """
    生成攻略
    
    Args:
        tasks: 任务列表
    """
    from services.ai_engine import get_ai_engine
    from services.seo_service import get_seo_service
    from prompts.wildtrip_prompt import build_wildtrip_prompt
    
    ai = get_ai_engine()
    seo = get_seo_service()
    
    success_count = 0
    
    for i, task in enumerate(tasks, 1):
        query = task['query']
        city = task['city']
        target_words = task.get('target_words', 3000)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"[{i}/{len(tasks)}] 生成: {query}")
        logger.info(f"目标字数: {target_words}")
        logger.info(f"{'='*80}\n")
        
        try:
            # 构建prompt (告诉AI目标字数)
            prompt = build_wildtrip_prompt(query, mode='full')
            prompt += f"\n\n目标字数: {target_words}字以上，确保内容深度和实用性。"
            
            # 生成
            content = ai.generate(prompt, query, mode='full', use_real_poi=True)
            
            # 保存HTML
            stats = {
                'word_count': len(content),
                'generation_time': 0,
                'city': city
            }
            
            html = seo.generate_html(query, content, stats)
            
            # 保存文件
            slug = seo.generate_slug(query)
            output_file = Path(seo.static_dir) / f"{slug}.html"
            output_file.write_text(html, encoding='utf-8')
            
            logger.success(f"✅ 成功: {output_file}")
            logger.info(f"   字数: {len(content)}")
            
            # 复制到web目录
            import shutil
            web_file = Path("/root/clawd/web/guides") / f"{slug}.html"
            shutil.copy(output_file, web_file)
            logger.info(f"   已部署: {web_file}")
            
            success_count += 1
            
            # 避免请求太快
            import time
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"❌ 生成失败: {e}")
            import traceback
            traceback.print_exc()
    
    return success_count


def main():
    """主函数"""
    logger.info("="*80)
    logger.info("🚀 每日攻略生成任务")
    logger.info("="*80)
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 加载进度
    progress = load_progress()
    
    # 检查今天是否已生成
    if progress['last_date'] == today:
        logger.warning(f"⚠️  今天 ({today}) 已经生成过了")
        logger.info(f"   总共生成: {progress['total_generated']} 篇")
        return
    
    # 获取任务
    strategy = ContentStrategyV2()
    tasks = get_today_tasks(strategy, progress)
    
    if not tasks:
        logger.warning("⚠️  没有更多任务了!")
        return
    
    logger.info(f"📝 今天的任务 ({today}):")
    for i, task in enumerate(tasks, 1):
        logger.info(f"   {i}. {task['query']} ({task['type']}, {task['target_words']}字)")
    
    logger.info("")
    
    # 生成
    success_count = generate_guides(tasks)
    
    # 更新进度
    progress['last_date'] = today
    progress['total_generated'] += success_count
    save_progress(progress)
    
    logger.info("")
    logger.info("="*80)
    logger.info(f"📊 今日完成:")
    logger.info(f"   成功: {success_count}/{len(tasks)}")
    logger.info(f"   总计: {progress['total_generated']} 篇")
    logger.info("="*80)
    
    # 🔄 更新索引页面
    try:
        import subprocess
        subprocess.run([
            'python3', 
            '/root/clawd/backend/scripts/generate_index.py'
        ], check=True)
        logger.info("✅ 索引页面已更新")
    except Exception as e:
        logger.warning(f"⚠️  索引更新失败: {e}")
    
    # 🔔 发送WhatsApp通知
    try:
        import subprocess
        
        message = f"""📝 **野游记每日攻略已生成**

📅 日期: {today}
✅ 成功: {success_count}/{len(tasks)} 篇
📊 累计: {progress['total_generated']} 篇

🔍 **今日生成列表:**

"""
        for i, task in enumerate(tasks[:success_count], 1):
            message += f"{i}. {task['query']}\n"
        
        message += f"""
📖 查看地址:
https://wildtrip.com.cn/guides/

⚠️ 请检查内容质量，如有问题请调整!
"""
        
        # 通过clawdbot发送消息给自己
        subprocess.run([
            'clawdbot', 'message', 'send',
            '--channel', 'whatsapp',
            '--target', '+8613907574397',
            '--message', message
        ], check=False)
        
        logger.info("✅ 已发送WhatsApp通知")
        
    except Exception as e:
        logger.warning(f"⚠️  发送通知失败: {e}")


if __name__ == '__main__':
    main()
