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

    每日配比（固定）:
    - 4篇：海南不同城市深度旅游攻略，每篇来自不同城市，轮转覆盖全岛
    - 1篇：海南人文历史深度游（文化/历史/民族主题）
    """
    all_tasks = strategy.get_priority_tasks()

    # 分离常规深度场景 vs 人文历史
    regular_tasks = [t for t in all_tasks['high'] if t.get('type') != 'cultural_history']
    cultural_tasks = [t for t in all_tasks['high'] if t.get('type') == 'cultural_history']

    today_tasks = []
    used_cities = set()

    # ---- 按城市分组，轮转选题 ----
    from collections import defaultdict
    city_tasks = defaultdict(list)
    for t in regular_tasks:
        city_tasks[t['city']].append(t)

    # 所有城市列表（固定顺序保证轮转稳定）
    all_cities = list(strategy.HAINAN_CITIES)
    num_cities = len(all_cities)

    # city_index：记录每个城市消费到第几个任务
    city_index = progress.get('city_index', {c: 0 for c in all_cities})

    # 今日从哪个城市开始轮转（全局偏移）
    day_offset = progress.get('day_offset', 0)

    for i in range(num_cities):
        if len(today_tasks) >= 4:
            break
        city = all_cities[(day_offset + i) % num_cities]
        tasks_for_city = city_tasks.get(city, [])
        city_idx = city_index.get(city, 0)
        if city_idx < len(tasks_for_city):
            today_tasks.append(tasks_for_city[city_idx])
            city_index[city] = city_idx + 1
            used_cities.add(city)

    # 更新进度：下次从下4个城市开始
    progress['day_offset'] = (day_offset + 4) % num_cities
    progress['city_index'] = city_index

    # ---- 1篇：人文历史（避免与今天城市重复）----
    cultural_start = progress.get('cultural_index', 0)
    c_idx = cultural_start
    cultural_added = False
    for _ in range(len(cultural_tasks)):
        task = cultural_tasks[c_idx % len(cultural_tasks)]
        c_idx += 1
        if task.get('city', '') not in used_cities:
            today_tasks.append(task)
            cultural_added = True
            break
    if not cultural_added and cultural_tasks:
        today_tasks.append(cultural_tasks[cultural_start % len(cultural_tasks)])
    progress['cultural_index'] = c_idx % len(cultural_tasks) if cultural_tasks else 0

    return today_tasks[:5]


XHS_PROMPT = """
你是小红书爆款文案写手。根据以下旅游攻略内容，生成一篇小红书笔记。

【攻略内容】
{content}

【要求】
1. 标题：20字以内，带1-2个emoji，要有吸引力，突出"本地人才知道""隐藏玩法""避坑"等痛点词
2. 正文：
   - 每天行程用📍Day1/📍Day2格式
   - 每个地点用简短的一句话描述亮点
   - 加入真实感的细节（几点去、吃什么、多少钱）
   - 控制在300字以内，小红书用户没耐心看长文
3. 结尾固定格式（必须包含）：
   💬 想要完整攻略的姐妹/朋友，评论区留言「发我」
   🔖 收藏这篇，下次去海南直接用！
4. 标签：5-8个，格式 #海南旅游 #城市名 等
5. 风格：口语化、真实感、有温度，像闺蜜分享而不是广告

只输出笔记内容，不要解释，不要加"以下是"之类的前缀。
"""


def generate_xiaohongshu_post(ai, query: str, content: str) -> str:
    """为攻略生成小红书文案"""
    try:
        prompt = XHS_PROMPT.format(content=content[:3000])  # 避免太长
        xhs = ai.generate(prompt, query, mode='full', use_real_poi=False)
        return xhs.strip()
    except Exception as e:
        logger.warning(f"⚠️  小红书文案生成失败: {e}")
        return ""


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
            # 根据任务类型选择生成模式
            task_type = task.get('type', 'deep_scenario')
            if task_type == 'cultural_history':
                mode = 'history'  # 人文历史深度游模式
            else:
                mode = 'full'  # 常规完整攻略模式
            
            # 构建prompt (告诉AI目标字数)
            prompt = build_wildtrip_prompt(query, mode=mode)
            prompt += f"\n\n目标字数: {target_words}字以上，确保内容深度和实用性。"
            
            # 生成
            content = ai.generate(prompt, query, mode=mode, use_real_poi=True)
            
            # 保存HTML
            stats = {
                'word_count': len(content),
                'generation_time': 0,
                'city': city
            }
            
            html = seo.generate_html(query, content, stats)
            
            # 🔧 后处理：确保小程序二维码路径正确 + 美团按钮含Logo
            # 模板文件位于:
            #   - QR码: wildtrip-existing/backend/services/markdown_renderer.py
            #   - 美团按钮: wildtrip-existing/backend/services/affiliate_manager.py
            MEITUAN_LOGO_IMG = '<img src="/images/meituan-logo.png" style="width:20px;height:20px;vertical-align:middle;margin-right:6px;border-radius:4px;">'
            html = html.replace('src="/static/mp-qrcode.svg"', 'src="/images/miniprogram-qrcode.jpg"')
            if MEITUAN_LOGO_IMG not in html:
                html = html.replace('美团预订 ', MEITUAN_LOGO_IMG + '美团预订 ')
                html = html.replace('美团预订\n', MEITUAN_LOGO_IMG + '美团预订\n')
            
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
        
        message = f"""📝 野游记每日攻略已生成

📅 日期: {today}
✅ 成功: {success_count}/{len(tasks)} 篇
📊 累计: {progress['total_generated']} 篇

今日生成列表:
"""
        for i, task in enumerate(tasks[:success_count], 1):
            message += f"{i}. {task['query']}\n"

        message += f"""
📖 全部攻略: https://wildtrip.com.cn/guides/

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
