"""
野游记攻略生成API
支持3种模式：full（完整攻略）、hotel（只推酒店）、food（只推美食）
"""

from flask import Blueprint, request, jsonify
from flask_socketio import emit, join_room, leave_room
import uuid
import threading
import time
from loguru import logger
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.ai_engine import AIEngine
from services.affiliate import get_meituan_affiliate
from prompts.wildtrip_prompt import build_wildtrip_prompt

# 创建Blueprint
generate_bp = Blueprint('generate', __name__)

# 存储活跃任务
active_tasks = {}

# 初始化服务
ai_engine = AIEngine()
affiliate = get_meituan_affiliate()  # 🔥 修复：使用函数读取环境变量


@generate_bp.route('/generate', methods=['POST'])
def create_generate_task():
    """
    创建攻略生成任务
    
    请求体:
    {
        "query": "海口3天亲子游，预算5000",
        "mode": "full",  // full/hotel/food
        "options": {
            "budget": 5000,
            "travelers": 4,
            "preferences": ["亲子", "海景"]
        }
    }
    
    响应:
    {
        "task_id": "uuid",
        "estimated_time": "30-60秒",
        "status": "started"
    }
    """
    try:
        data = request.json
        query = data.get('query', '').strip()
        mode = data.get('mode', 'full')
        options = data.get('options', {})
        
        if not query:
            return jsonify({
                'error': '查询不能为空',
                'code': 'EMPTY_QUERY'
            }), 400
        
        if mode not in ['full', 'hotel', 'food']:
            return jsonify({
                'error': '无效的mode参数（支持：full/hotel/food）',
                'code': 'INVALID_MODE'
            }), 400
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 预估时间
        estimated_time = {
            'full': '30-60秒',
            'hotel': '20-30秒',
            'food': '20-30秒'
        }.get(mode, '30-60秒')
        
        # 记录任务
        active_tasks[task_id] = {
            'query': query,
            'mode': mode,
            'options': options,
            'status': 'pending',
            'created_at': time.time(),
            'progress': 0,
            'result': None,
            'error': None
        }
        
        # 启动后台任务
        thread = threading.Thread(
            target=run_generation_task,
            args=(task_id, query, mode, options),
            daemon=True
        )
        thread.start()
        
        logger.info(f"🎯 创建任务: {task_id} | 查询: {query} | 模式: {mode}")
        
        return jsonify({
            'task_id': task_id,
            'estimated_time': estimated_time,
            'status': 'started',
            'mode': mode
        }), 200
        
    except Exception as e:
        logger.error(f"创建任务失败: {e}")
        return jsonify({
            'error': str(e),
            'code': 'INTERNAL_ERROR'
        }), 500


@generate_bp.route('/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """
    获取任务状态和结果
    
    响应:
    {
        "task_id": "uuid",
        "status": "pending|running|completed|failed",
        "progress": 75,
        "result": {
            "content": "攻略内容（Markdown）",
            "recommendations": {
                "hotels": [...],
                "restaurants": [...],
                "tickets": [...]
            },
            "stats": {
                "word_count": 3000,
                "hotels_count": 3,
                "restaurants_count": 6,
                "tickets_count": 2
            }
        }
    }
    """
    task = active_tasks.get(task_id)
    
    if not task:
        return jsonify({
            'error': '任务不存在或已过期',
            'code': 'TASK_NOT_FOUND'
        }), 404
    
    response = {
        'task_id': task_id,
        'status': task['status'],
        'progress': task['progress'],
        'mode': task.get('mode', 'full'),
        'query': task.get('query', '')
    }
    
    if task['status'] == 'completed' and task['result']:
        response['result'] = task['result']
    
    if task['status'] == 'failed' and task['error']:
        response['error'] = task['error']
    
    return jsonify(response), 200


def run_generation_task(task_id: str, query: str, mode: str, options: dict):
    """
    执行攻略生成任务（后台线程）
    """
    from app import socketio  # 延迟导入避免循环依赖
    
    try:
        # 更新状态
        active_tasks[task_id]['status'] = 'running'
        emit_progress(socketio, task_id, 'start', '🔥 野游记开始工作...', 0)
        
        # 构建prompt
        emit_progress(socketio, task_id, 'building_prompt', '🧠 正在理解你的需求...', 10)
        time.sleep(0.5)  # 模拟思考
        
        full_prompt = build_wildtrip_prompt(query, mode)
        
        # 调用AI生成
        emit_progress(socketio, task_id, 'generating', '✍️ AI正在生成攻略...', 30)
        
        content = ai_engine.generate(full_prompt, query, mode)
        
        emit_progress(socketio, task_id, 'enhancing', '🔗 正在添加返佣链接...', 70)
        
        # 插入返佣链接
        enhanced_content, recommendations = enhance_with_affiliate(content, query, mode)
        
        # 统计信息
        stats = {
            'word_count': len(enhanced_content),
            'hotels_count': len(recommendations.get('hotels', [])),
            'restaurants_count': len(recommendations.get('restaurants', [])),
            'tickets_count': len(recommendations.get('tickets', []))
        }
        
        # 🔥 提取所有链接，供前端渲染按钮
        all_links = []
        for hotel in recommendations.get('hotels', []):
            all_links.append({
                'type': 'hotel',
                'name': hotel['name'],
                'url': hotel['link'],
                'button_text': f"预订 {hotel['name']}"
            })
        for restaurant in recommendations.get('restaurants', []):
            all_links.append({
                'type': 'restaurant',
                'name': restaurant['name'],
                'url': restaurant['link'],
                'button_text': f"团购 {restaurant['name']}"
            })
        for ticket in recommendations.get('tickets', []):
            all_links.append({
                'type': 'ticket',
                'name': ticket['name'],
                'url': ticket['link'],
                'button_text': f"购票 {ticket['name']}"
            })
        
        # 完成
        active_tasks[task_id]['status'] = 'completed'
        active_tasks[task_id]['progress'] = 100
        active_tasks[task_id]['result'] = {
            'content': enhanced_content,
            'recommendations': recommendations,
            'links': all_links,  # 🔥 新增：所有可点击链接
            'stats': stats
        }
        
        emit_progress(socketio, task_id, 'done', '🎉 攻略生成完成！', 100)
        
        logger.info(f"✅ 任务完成: {task_id} | 字数: {stats['word_count']} | 酒店: {stats['hotels_count']}")
        
    except Exception as e:
        logger.error(f"❌ 任务失败: {task_id} | 错误: {e}")
        active_tasks[task_id]['status'] = 'failed'
        active_tasks[task_id]['error'] = str(e)
        emit_progress(socketio, task_id, 'error', f'生成失败: {str(e)}', 0)


def enhance_with_affiliate(content: str, query: str, mode: str) -> tuple:
    """
    在内容中插入返佣链接（优化版）
    
    Returns:
        (enhanced_content, recommendations)
    """
    import re
    
    recommendations = {
        'hotels': [],
        'restaurants': [],
        'tickets': []
    }
    
    # === 1. 提取城市名称（用于搜索） ===
    from prompts.wildtrip_prompt import extract_city_name
    city = extract_city_name(query)
    
    # === 2. 酒店链接替换（优化正则，匹配DeepSeek生成的实际格式） ===
    # 实际格式：### 1. 海口喜来登酒店 ⭐⭐⭐⭐⭐
    #          - **预订：** [携程](链接占位) | [美团](链接占位)
    
    # 方法：查找包含"预订"的段落，向上查找最近的酒店名称
    hotel_booking_pattern = r'\*\*预订[：:]\*\*\s*\[.*?\]\((?:链接占位|占位)\)'
    booking_matches = list(re.finditer(hotel_booking_pattern, content))
    
    seen_hotels = set()
    for booking_match in booking_matches:
        # 找到预订链接的位置
        booking_pos = booking_match.start()
        
        # 向前查找最近的三级标题（酒店名称）
        # 格式：### 1. XX酒店 或 ### ⭐ 推荐：XX酒店
        preceding_text = content[:booking_pos]
        
        # 找最后一个三级标题
        hotel_header_matches = list(re.finditer(
            r'###\s+(?:\d+\.\s+)?(?:⭐\s+推荐[：:]\s*)?([^#\n]+?(?:酒店|宾馆|客栈|民宿|度假村)[^#\n]*?)(?:\s+[⭐⭐⭐⭐⭐\s]*)?$',
            preceding_text,
            re.MULTILINE
        ))
        
        if hotel_header_matches:
            last_hotel_match = hotel_header_matches[-1]
            hotel_name = last_hotel_match.group(1).strip()
            
            # 清理名称
            clean_name = re.sub(r'[⭐️\s（）]+$', '', hotel_name).strip()
            clean_name = re.sub(r'（.*?）', '', clean_name).strip()
            clean_name = re.sub(r'\s*$', '', clean_name)
            
            # 去重和过滤
            if clean_name in seen_hotels or len(clean_name) < 3:
                continue
            seen_hotels.add(clean_name)
            
            search_query = f"{city} {clean_name}"
            link = affiliate.get_search_link(query=search_query, category="hotel")
            
            recommendations['hotels'].append({
                'name': clean_name,
                'link': link,
                'search_query': search_query
            })
            
            # 替换该酒店的第一个预订链接
            # 找到这个酒店段落中的第一个预订链接并替换
            hotel_section_start = last_hotel_match.start()
            hotel_section = content[hotel_section_start:booking_pos + 200]
            
            # 替换第一个[携程]或[美团]链接
            content = content[:hotel_section_start] + re.sub(
                r'\[(携程|美团)\]\((?:链接占位|占位)\)',
                f'[\\1]({link})',
                hotel_section,
                count=2  # 替换两个（携程和美团都指向同一个搜索）
            ) + content[booking_pos + 200:]
    
    # === 3. 餐厅链接替换（优化正则，匹配多种格式） ===
    # 格式1：**XX文昌鸡饭** ¥50/人
    # 格式2：**午餐：海南粉老店**
    # 格式3：#### 1. 海口文昌鸡饭老店 ¥50-80/人
    food_patterns = [
        r'\*\*([^*]+?(?:餐厅|饭店|小吃|海鲜|鸡饭|粉店|茶餐厅|大排档|火锅|烤肉|酒楼|老店)[^*]*?)\*\*\s*¥',  # 带价格
        r'\*\*(?:午餐|晚餐|早餐|夜市小吃)：([^*]+?)\*\*',  # 餐段标题
        r'####\s+\d+\.\s+([^¥\n]+?(?:餐厅|饭店|海鲜|鸡饭|粉店|小吃街|老店)[^¥\n]*)',  # 四级标题
    ]
    
    seen_restaurants = set()
    for pattern in food_patterns:
        food_matches = re.finditer(pattern, content)
        for match in food_matches:
            restaurant_name = match.group(1).strip()
            
            # 清理名称
            clean_name = re.sub(r'（.*?）', '', restaurant_name).strip()
            
            # 去重和过滤
            if clean_name in seen_restaurants or len(clean_name) < 3:
                continue
            seen_restaurants.add(clean_name)
            
            search_query = f"{city} {clean_name}"
            link = affiliate.get_search_link(query=search_query, category="food")
            
            recommendations['restaurants'].append({
                'name': clean_name,
                'link': link,
                'search_query': search_query
            })
            
            # 替换该餐厅下一个出现的团购链接
            # 使用更宽泛的匹配，找到餐厅名称后面的任何团购链接
            context_pattern = re.escape(clean_name) + r'.*?\[.*?团购\]\(占位\)'
            if re.search(context_pattern, content, re.DOTALL):
                content = re.sub(
                    r'(\*\*(?:午餐|晚餐|早餐)?[：:]*' + re.escape(clean_name) + r'.*?)\[.*?团购\]\(占位\)',
                    r'\1[美团团购](' + link + ')',
                    content,
                    count=1,
                    flags=re.DOTALL
                )
            else:
                # 如果没找到，就替换第一个占位符
                content = re.sub(r'\[.*?团购\]\(占位\)', f'[美团团购]({link})', content, count=1)
    
    # === 4. 门票链接替换（优化正则，匹配DeepSeek实际格式） ===
    # 实际格式：- **雷琼世界地质公园** 门票¥0，免费！[官方预约](链接占位)
    #          - **海南热带野生动植物园** 门票¥158/成人，[提前1天美团购票](链接占位)
    
    # 匹配：**景点名** 门票...链接占位
    ticket_pattern = r'\*\*([^*]+?(?:公园|景区|博物馆|动物园|植物园|海洋馆|乐园|古镇|寺庙|塔|电影公社|主题乐园)[^*]*?)\*\*\s+门票[^[\n]*?\[.*?\]\((?:链接占位|占位)\)'
    ticket_matches = re.finditer(ticket_pattern, content, re.DOTALL)
    
    seen_tickets = set()
    for match in ticket_matches:
        poi_name = match.group(1).strip()
        
        # 清理名称
        clean_name = re.sub(r'（.*?）', '', poi_name).strip()
        
        # 去重和过滤
        if clean_name in seen_tickets or len(clean_name) < 3:
            continue
        
        # 排除Tips之类的非景点文本
        if any(keyword in clean_name for keyword in ['Tips', '提示', '注意', '建议']):
            continue
            
        seen_tickets.add(clean_name)
        
        search_query = f"{city} {clean_name} 门票"
        link = affiliate.get_search_link(query=search_query, category="ticket")
        
        recommendations['tickets'].append({
            'name': clean_name,
            'link': link,
            'search_query': search_query
        })
        
        # 替换该景点的门票链接
        # 找到这个景点的整个描述段落，替换其中的第一个链接
        poi_pattern = r'(\*\*' + re.escape(clean_name) + r'\*\*\s+门票[^[\n]*?)\[.*?\]\((?:链接占位|占位)\)'
        content = re.sub(
            poi_pattern,
            r'\1[美团门票](' + link + ')',
            content,
            count=1,
            flags=re.DOTALL
        )
    
    # === 5. 替换新格式占位符（LINK_格式） ===
    # 格式：LINK_FOOD_餐厅名、LINK_HOTEL_酒店名、LINK_TICKET_景点名
    link_pattern = r'\(LINK_(FOOD|HOTEL|TICKET)_([^)]+)\)'
    link_matches = re.finditer(link_pattern, content)
    
    replacements = []
    for match in link_matches:
        link_type = match.group(1)
        name = match.group(2)
        
        # 确定分类
        category_map = {
            'FOOD': 'food',
            'HOTEL': 'hotel',
            'TICKET': 'ticket'
        }
        category = category_map.get(link_type, 'food')
        
        # 生成链接
        search_query = f"{city} {name}"
        if category == 'ticket':
            search_query += " 门票"
        
        link = affiliate.get_search_link(query=search_query, category=category)
        
        # 记录替换（避免重复替换导致位置错乱）
        replacements.append((match.start(), match.end(), f'({link})'))
    
    # 从后往前替换（避免位置偏移）
    for start, end, replacement in reversed(replacements):
        content = content[:start] + replacement + content[end:]
    
    # === 6. 替换所有剩余的占位符（兜底方案） ===
    # 处理各种格式的占位符（从特殊到通用）
    placeholder_patterns = [
        (r'\[美团门票\]\(占位\)', 'ticket'),  # 门票-特定格式
        (r'\[美团搜索\]\(占位\)', 'food'),    # 美食-搜索
        (r'\[美团团购\]\(占位\)', 'food'),    # 美食-团购
        (r'\[查看详情\]\(占位\)', 'hotel'),   # 酒店-查看详情
        (r'\[官方预约\]\(占位\)', 'ticket'),  # 门票-官方预约
        (r'\[.*?团购\]\(链接占位\)', 'food'), # 团购-链接占位
        (r'\[.*?门票\]\(链接占位\)', 'ticket'), # 门票-链接占位
        (r'\]\(占位\)', 'food'),  # 通用兜底
    ]
    
    for pattern, category in placeholder_patterns:
        # 持续替换直到没有匹配为止
        while True:
            match = re.search(pattern, content)
            if not match:
                break
            
            # 提取链接文本
            link_text_match = re.search(r'\[([^\]]+)\]', match.group(0))
            link_text = link_text_match.group(1) if link_text_match else '美团'
            
            # 生成搜索链接
            search_query = f"{city}"
            link = affiliate.get_search_link(query=search_query, category=category)
            
            # 替换
            content = content[:match.start()] + f'[{link_text}]({link})' + content[match.end():]
    
    logger.info(f"🔗 链接替换完成 | 酒店:{len(recommendations['hotels'])} 餐厅:{len(recommendations['restaurants'])} 门票:{len(recommendations['tickets'])}")
    
    return content, recommendations


def emit_progress(socketio, task_id: str, event_type: str, message: str, progress: int):
    """发送进度更新"""
    try:
        if task_id in active_tasks:
            active_tasks[task_id]['progress'] = progress
        
        socketio.emit('wildtrip_progress', {
            'task_id': task_id,
            'type': event_type,
            'message': message,
            'progress': progress,
            'timestamp': time.time()
        }, room=task_id)
        
        logger.debug(f"📡 进度更新: {task_id} | {progress}% | {message}")
        
    except Exception as e:
        logger.error(f"发送进度更新失败: {e}")


def register_socketio_events(socketio):
    """注册WebSocket事件"""
    
    @socketio.on('subscribe')
    def handle_subscribe(data):
        task_id = data.get('task_id')
        
        if not task_id or task_id not in active_tasks:
            emit('error', {'message': '任务不存在'})
            return
        
        join_room(task_id)
        
        task = active_tasks[task_id]
        emit('subscribed', {
            'task_id': task_id,
            'status': task['status'],
            'progress': task['progress']
        })
        
        logger.info(f"📲 客户端订阅: {task_id}")
    
    @socketio.on('unsubscribe')
    def handle_unsubscribe(data):
        task_id = data.get('task_id')
        if task_id:
            leave_room(task_id)
            logger.info(f"📴 客户端取消订阅: {task_id}")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info("📴 客户端断开连接")
