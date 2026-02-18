#!/usr/bin/env python3
"""
历史人物数据自动生成工具
策略：
- 用DeepSeek API生成数据（不爬虫，不加载大模型）
- 单线程顺序处理，避免内存堆积
- 每个人物单独生成、单独保存、单独入库
- 严格内存控制：每步完成后主动释放
"""

import sys
import os
import json
import time
import gc
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')

from loguru import logger

# ─── 历史人物配置表 ─────────────────────────────────────────────
# 每次只处理一个，内存友好
HISTORY_PERSONS = {
    "玄奘": {
        "description": "唐代高僧，西天取经，历时17年，行程5万里",
        "key_locations": ["长安", "凉州", "玉门关", "沙州", "高昌", "碎叶城", "天竺", "那烂陀寺"],
        "key_years": "629-645年",
        "theme": "不畏艰难，追求真理，东方文化使者",
        "travel_type": "取经之路/丝绸之路"
    },
    "李白": {
        "description": "唐代诗人，字太白，号青莲居士，浪漫主义诗仙",
        "key_locations": ["江油", "成都", "长安", "庐山", "黄鹤楼", "天门山", "宣城", "当涂"],
        "key_years": "701-762年",
        "theme": "仗剑天涯，饮酒赋诗，飘逸洒脱的浪漫主义",
        "travel_type": "诗人漫游之路"
    },
    "徐霞客": {
        "description": "明代地理学家、旅行家，足迹遍及全国，著《徐霞客游记》",
        "key_locations": ["江阴", "天台山", "雁荡山", "黄山", "武夷山", "桂林", "云南", "腾冲"],
        "key_years": "1607-1641年",
        "theme": "不畏险阻，探索自然，中国第一旅行家",
        "travel_type": "探险考察之路"
    },
    "杜甫": {
        "description": "唐代诗人，字子美，号少陵野老，现实主义诗圣",
        "key_locations": ["洛阳", "长安", "成都草堂", "夔州", "岳阳", "江陵", "潭州"],
        "key_years": "712-770年",
        "theme": "忧国忧民，漂泊一生，诗圣的家国情怀",
        "travel_type": "流离漂泊之路"
    }
}

# ─── JSON数据生成Prompt ────────────────────────────────────────
GENERATE_TIMELINE_PROMPT = """
请为"{person_name}"生成一份结构化的历史时间线JSON数据，用于旅游攻略生成系统。

背景信息：
- 人物简介：{description}
- 关键地点：{key_locations}
- 活跃年代：{key_years}
- 主题：{theme}
- 路线类型：{travel_type}

要求：
1. 只返回JSON，不要其他文字
2. 格式严格参照以下示例：

{{
  "人物": "人物全名",
  "生卒年": "XXX-XXX",
  "核心主题": "主题描述",
  "总结": "一句话总结人物旅行意义（50字内）",
  "核心事件时间线": [
    {{
      "序号": 1,
      "时间": "具体年份",
      "地点": "地名（古称）",
      "事件": "简洁描述发生了什么",
      "意义": "这个节点的历史意义",
      "代表作品": ["作品1", "作品2"],  // 如有
      "名句": "代表名句",  // 如有
      "遗迹": "现代遗址名称",  // 如有
      "史料来源": "《XXX》"
    }}
  ],
  "旅游路线设计思路": {{
    "核心主题": "旅游主题",
    "路线": "地点1 → 地点2 → ...",
    "时长建议": "X-X天",
    "适合人群": "适合什么类型的旅行者",
    "卖点": "这条路线的核心卖点"
  }}
}}

要求：
- 时间线至少8个关键节点
- 每个节点都要有史料来源
- 遗迹尽量写现代可访问的景点名称
- 旅游化表达（不要教科书式）
"""

GENERATE_POEMS_PROMPT = """
请为"{person_name}"生成一份代表诗词/著作JSON数据，用于旅游攻略生成系统。

背景信息：
- 人物简介：{description}
- 活跃年代：{key_years}

要求：只返回JSON，不要其他文字。

格式如下（至少6首/篇）：

{{
  "诗词库": [
    {{
      "id": 1,
      "标题": "作品标题",
      "作者": "{person_name}",
      "创作时间": "具体年份",
      "创作地点": "地名",
      "全文": "原文（诗词写全文，散文写片段）",
      "名句": "最著名的一句",
      "创作背景": "当时发生了什么，心境如何（50-100字）",
      "核心主题": "作品主题",
      "现代体验": "旅行者可以在哪里、怎么体验这首诗的意境（具体可操作）",
      "旅游tips": "去对应地点的实用建议",
      "史料来源": "《XXX》"
    }}
  ]
}}
"""

GENERATE_LOCATIONS_PROMPT = """
请为"{person_name}的{travel_type}"生成核心地点JSON数据，用于旅游攻略生成系统。

背景信息：
- 人物简介：{description}
- 关键地点：{key_locations}

要求：只返回JSON，不要其他文字。

格式如下（4-6个核心地点）：

{{
  "路线地点": [
    {{
      "id": 1,
      "古代地名": "历史地名",
      "今日地名": "现代省市名",
      "历史意义": "这个地点对人物的重要性（一句话）",
      "停留时间": "人物在此时间",
      "主要遗迹": [
        {{
          "名称": "景点名称",
          "位置": "在哪里",
          "历史": "与人物的关联",
          "现状": "现在保存状况",
          "游览建议": "怎么游览"
        }}
      ],
      "必游体验": ["体验1", "体验2", "体验3"],
      "必吃美食": [
        {{
          "名称": "食物名",
          "历史": "历史渊源",
          "特点": "口味特点"
        }}
      ],
      "交通": "从主要城市如何到达",
      "住宿建议": "推荐住哪里",
      "停留时间建议": "建议游玩X天"
    }}
  ]
}}
"""


def check_memory():
    """检查内存，返回可用MB"""
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
        available = int([l for l in meminfo.split('\n') if 'MemAvailable' in l][0].split()[1])
        return available // 1024  # 转为MB
    except:
        return 999


def call_deepseek(prompt: str, max_tokens: int = 2000) -> str:
    """调用DeepSeek API生成数据（低内存友好）"""
    import openai
    
    api_key = os.getenv('AI_API_KEY', '')
    base_url = os.getenv('AI_BASE_URL', 'https://api.deepseek.com')
    model = os.getenv('AI_MODEL', 'deepseek-chat')
    
    client = openai.OpenAI(api_key=api_key, base_url=base_url, timeout=120.0)
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个历史数据专家，专门生成结构化的旅游历史数据JSON。只返回JSON，不要其他文字。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,  # 低temperature，保证JSON格式稳定
        max_tokens=max_tokens,
        timeout=120
    )
    
    content = response.choices[0].message.content.strip()
    
    # 主动释放
    del response
    del client
    gc.collect()
    
    return content


def clean_json_response(text: str) -> str:
    """清理AI返回的JSON（去掉markdown代码块等）"""
    text = text.strip()
    if text.startswith('```json'):
        text = text[7:]
    elif text.startswith('```'):
        text = text[3:]
    if text.endswith('```'):
        text = text[:-3]
    return text.strip()


def generate_person_data(person_name: str, person_info: dict, output_dir: Path) -> bool:
    """
    为一个历史人物生成完整数据集
    
    Returns:
        True = 成功，False = 失败
    """
    # output_dir 已经是 data/history/<person_name>，不要再追加一层
    person_dir = output_dir
    person_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"🏛️ 开始生成：{person_name}")
    logger.info(f"{'='*60}")
    
    # ─── 1. 生成时间线 ────────────────────────────────────────
    mem = check_memory()
    logger.info(f"💾 当前可用内存: {mem}MB")
    
    if mem < 150:
        logger.warning("⚠️ 内存不足150MB，跳过本次生成")
        return False
    
    timeline_file = person_dir / '时间线.json'
    if timeline_file.exists():
        logger.info(f"⏭️ 时间线已存在，跳过")
    else:
        logger.info("📝 生成时间线...")
        try:
            prompt = GENERATE_TIMELINE_PROMPT.format(
                person_name=person_name,
                **person_info
            )
            
            raw = call_deepseek(prompt, max_tokens=2500)
            json_str = clean_json_response(raw)
            data = json.loads(json_str)
            
            with open(timeline_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 时间线已保存: {timeline_file}")
            del raw, json_str, data
            gc.collect()
            time.sleep(2)  # API限速
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON解析失败: {e}")
            # 保存原始文本以便排查
            with open(person_dir / '时间线_raw.txt', 'w', encoding='utf-8') as f:
                f.write(raw)
            return False
        except Exception as e:
            logger.error(f"❌ 时间线生成失败: {e}")
            return False
    
    # ─── 2. 生成诗词/著作 ────────────────────────────────────
    mem = check_memory()
    if mem < 150:
        logger.warning("⚠️ 内存不足，跳过诗词生成")
        return False
    
    poems_dir = Path(str(output_dir.parent) + '/诗词')
    poems_dir.mkdir(exist_ok=True)
    poems_file = poems_dir / f'{person_name}诗词库.json'
    
    if poems_file.exists():
        logger.info("⏭️ 诗词已存在，跳过")
    else:
        logger.info("📝 生成诗词库...")
        try:
            prompt = GENERATE_POEMS_PROMPT.format(
                person_name=person_name,
                **person_info
            )
            
            raw = call_deepseek(prompt, max_tokens=2500)
            json_str = clean_json_response(raw)
            data = json.loads(json_str)
            
            with open(poems_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 诗词库已保存: {poems_file}")
            del raw, json_str, data
            gc.collect()
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"❌ 诗词生成失败: {e}")
            # 非致命错误，继续
    
    # ─── 3. 生成地点 ─────────────────────────────────────────
    mem = check_memory()
    if mem < 150:
        logger.warning("⚠️ 内存不足，跳过地点生成")
        return False
    
    locations_dir = Path(str(output_dir.parent) + '/地点')
    locations_dir.mkdir(exist_ok=True)
    locations_file = locations_dir / f'{person_name}路线地点.json'
    
    if locations_file.exists():
        logger.info("⏭️ 地点已存在，跳过")
    else:
        logger.info("📝 生成路线地点...")
        try:
            prompt = GENERATE_LOCATIONS_PROMPT.format(
                person_name=person_name,
                **person_info
            )
            
            raw = call_deepseek(prompt, max_tokens=2500)
            json_str = clean_json_response(raw)
            data = json.loads(json_str)
            
            with open(locations_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 路线地点已保存: {locations_file}")
            del raw, json_str, data
            gc.collect()
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"❌ 地点生成失败: {e}")
    
    logger.info(f"✅ {person_name} 数据生成完成！\n")
    return True


def import_to_chromadb(person_name: str, data_base_dir: Path):
    """将生成的数据导入ChromaDB（内存友好版）"""
    logger.info(f"📥 导入 {person_name} 到ChromaDB...")
    
    from services.rag_engine import get_rag_engine
    rag = get_rag_engine()
    
    imported = 0
    
    # 导入时间线
    timeline_file = data_base_dir / person_name / '时间线.json'
    if timeline_file.exists():
        with open(timeline_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        guides = []
        for event in data.get('核心事件时间线', []):
            content = f"## {person_name} - {event['事件']}\n时间：{event['时间']}\n地点：{event['地点']}\n意义：{event.get('意义', '')}"
            
            if event.get('名句'):
                if isinstance(event['名句'], list):
                    content += f"\n名句：{'; '.join(event['名句'])}"
                else:
                    content += f"\n名句：{event['名句']}"
            
            guides.append({
                "id": f"{person_name.lower()}_timeline_{event.get('序号', imported)}",
                "content": content,
                "metadata": {
                    "person": person_name,
                    "type": "history",
                    "category": "timeline",
                    "time": event.get('时间', ''),
                    "location": event.get('地点', ''),
                    "event": event.get('事件', ''),
                    "source": event.get('史料来源', '')
                }
            })
        
        if guides:
            rag.batch_add_guides(guides)
            imported += len(guides)
            del guides, data
            gc.collect()
            logger.info(f"  ✅ 时间线：{imported}条")
    
    # 导入诗词
    poems_file = data_base_dir / '诗词' / f'{person_name}诗词库.json'
    if poems_file.exists():
        with open(poems_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        guides = []
        for i, poem in enumerate(data.get('诗词库', []), 1):
            location = poem.get('创作地点', '')
            if isinstance(location, dict):
                location = location.get('今称', location.get('古称', ''))
            
            content = f"## {poem.get('标题', '')}\n作者：{person_name}\n创作时间：{poem.get('创作时间', '')}\n创作地点：{location}\n"
            if poem.get('全文'):
                content += f"\n{poem['全文']}\n"
            if poem.get('名句'):
                content += f"\n名句：{poem['名句']}"
            if poem.get('创作背景'):
                content += f"\n创作背景：{poem['创作背景']}"
            if poem.get('现代体验'):
                content += f"\n现代体验：{poem['现代体验']}"
            
            guides.append({
                "id": f"{person_name.lower()}_poem_{i}",
                "content": content,
                "metadata": {
                    "person": person_name,
                    "type": "history",
                    "category": "poem",
                    "title": poem.get('标题', ''),
                    "time": poem.get('创作时间', ''),
                    "location": location,
                    "source": poem.get('史料来源', '')
                }
            })
        
        if guides:
            rag.batch_add_guides(guides)
            imported += len(guides)
            del guides, data
            gc.collect()
            logger.info(f"  ✅ 诗词：+{len(guides)}条")
    
    # 导入地点
    locations_file = data_base_dir.parent / '地点' / f'{person_name}路线地点.json'
    if locations_file.exists():
        with open(locations_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        guides = []
        for loc in data.get('路线地点', []):
            content = f"## {loc.get('古代地名', '')}（{loc.get('今日地名', '')}）\n历史意义：{loc.get('历史意义', '')}\n"
            
            for exp in loc.get('必游体验', []):
                content += f"- {exp}\n"
            
            if loc.get('必吃美食'):
                content += "\n美食：\n"
                for food in loc['必吃美食']:
                    if isinstance(food, dict):
                        content += f"- {food.get('名称', '')}: {food.get('历史', '')}\n"
            
            guides.append({
                "id": f"{person_name.lower()}_location_{loc.get('id', len(guides)+1)}",
                "content": content,
                "metadata": {
                    "person": person_name,
                    "type": "history",
                    "category": "location",
                    "location": loc.get('古代地名', ''),
                    "modern_location": loc.get('今日地名', '')
                }
            })
        
        if guides:
            rag.batch_add_guides(guides)
            imported += len(guides)
            del guides, data
            gc.collect()
            logger.info(f"  ✅ 地点：+{len(guides)}条")
    
    del rag
    gc.collect()
    
    logger.info(f"  📊 {person_name} 共导入：{imported}条")
    return imported


def main(target_person: str = None):
    """
    主函数
    
    Args:
        target_person: 指定处理某个人物（None=显示菜单）
    """
    data_base = Path(__file__).parent.parent / 'data/history'
    os.environ['CHROMA_DB_PATH'] = str(Path(__file__).parent.parent / 'data/chroma_db')
    
    if target_person and target_person not in HISTORY_PERSONS:
        logger.error(f"❌ 未知人物: {target_person}")
        logger.info(f"支持的人物: {list(HISTORY_PERSONS.keys())}")
        return
    
    persons_to_process = [target_person] if target_person else list(HISTORY_PERSONS.keys())
    
    logger.info(f"\n🚀 野游记历史数据生成工具")
    logger.info(f"📋 待处理人物: {persons_to_process}")
    logger.info(f"💾 初始可用内存: {check_memory()}MB\n")
    
    results = {}
    
    for person_name in persons_to_process:
        person_info = HISTORY_PERSONS[person_name]
        
        # 检查内存
        mem = check_memory()
        if mem < 200:
            logger.warning(f"⚠️ 内存不足({mem}MB)，暂停等待30秒...")
            time.sleep(30)
            gc.collect()
        
        # 生成数据
        success = generate_person_data(person_name, person_info, data_base / person_name)
        
        if success:
            # 导入ChromaDB
            imported = import_to_chromadb(person_name, data_base)
            results[person_name] = imported
        else:
            results[person_name] = 0
        
        # 每个人物处理完后等待，让内存恢复
        gc.collect()
        time.sleep(3)
    
    # 最终统计
    logger.info(f"\n{'='*60}")
    logger.info(f"🎉 全部完成！")
    logger.info(f"{'='*60}")
    for person, count in results.items():
        logger.info(f"  {person}: {count}条数据")
    
    total = sum(results.values())
    logger.info(f"\n  总计：{total}条新数据入库")
    logger.info(f"  最终可用内存: {check_memory()}MB")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='野游记历史数据生成工具')
    parser.add_argument('--person', type=str, help='指定人物（玄奘/李白/徐霞客/杜甫）')
    parser.add_argument('--list', action='store_true', help='列出支持的人物')
    parser.add_argument('--import-only', type=str, help='只导入已有数据（不生成）')
    args = parser.parse_args()
    
    if args.list:
        print("\n支持的历史人物：")
        for name, info in HISTORY_PERSONS.items():
            print(f"  - {name}：{info['description'][:30]}...")
        sys.exit(0)
    
    if args.import_only:
        data_base = Path(__file__).parent.parent / 'data/history'
        os.environ['CHROMA_DB_PATH'] = str(Path(__file__).parent.parent / 'data/chroma_db')
        import_to_chromadb(args.import_only, data_base)
    else:
        main(args.person)
