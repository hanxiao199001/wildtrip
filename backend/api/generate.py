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
from services.ai_engine_streaming import get_streaming_ai_engine  # 🔥 新增：流式引擎
from services.affiliate import get_meituan_affiliate
from prompts.wildtrip_prompt import build_wildtrip_prompt

# 创建Blueprint
generate_bp = Blueprint('generate', __name__)

# 存储活跃任务
active_tasks = {}

# 初始化服务
ai_engine = AIEngine()  # 保留旧引擎作为fallback
streaming_ai_engine = get_streaming_ai_engine()  # 🔥 新增：流式引擎
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
        user_id = data.get('user_id')  # 🔥 新增：用户ID（可选）
        
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
            'user_id': user_id,  # 🔥 新增：保存用户ID
            'status': 'pending',
            'created_at': time.time(),
            'progress': 0,
            'result': None,
            'error': None
        }
        
        # 启动后台任务
        thread = threading.Thread(
            target=run_generation_task,
            args=(task_id, query, mode, options, user_id),  # 🔥 新增：传递user_id
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


def run_generation_task(task_id: str, query: str, mode: str, options: dict, user_id: str = None):
    """
    执行攻略生成任务（后台线程）
    
    Args:
        task_id: 任务ID
        query: 用户查询
        mode: 模式
        options: 选项
        user_id: 用户ID（可选，如果提供则保存到用户历史）
    """
    from app import socketio  # 延迟导入避免循环依赖
    from prompts.wildtrip_prompt import extract_city_name
    
    try:
        # 更新状态
        active_tasks[task_id]['status'] = 'running'
        emit_progress(socketio, task_id, 'start', '🔥 野游记开始工作...', 0)
        
        # 提取城市信息
        city = extract_city_name(query)
        emit_progress(socketio, task_id, 'parsing', f'📍 识别目的地: {city}', 5)
        time.sleep(0.3)
        
        # 构建prompt
        emit_progress(socketio, task_id, 'building_prompt', '🧠 正在理解你的需求...', 10)
        time.sleep(0.5)
        
        full_prompt = build_wildtrip_prompt(query, mode)
        
        # 检索RAG数据
        emit_progress(socketio, task_id, 'rag_search', '🔍 正在搜索本地攻略数据库...', 15)
        time.sleep(0.8)
        
        # 调用AI生成（使用流式引擎，实时更新进度）
        emit_progress(socketio, task_id, 'generating', f'✍️ AI正在生成{city}攻略...', 25)
        
        # 🔥 定义进度回调函数（供流式引擎调用）
        def on_ai_progress(progress, message, chunk):
            """AI流式输出进度回调"""
            emit_progress(socketio, task_id, 'generating', message, progress)
        
        # 🔥 使用流式引擎生成（实时反馈进度，不再阻塞）
        content = streaming_ai_engine.generate_stream(
            full_prompt, 
            query, 
            mode,
            progress_callback=on_ai_progress
        )
        
        # 🔥 后处理：替换AI生成的[预算]占位符为真实数字
        import re
        budget_match = re.search(r'预算\s*[：:]\s*(\d+)', query, re.I)
        if budget_match:
            budget_value = budget_match.group(1)
            content = content.replace('[预算]', budget_value)
            logger.info(f"✅ 已替换[预算] → {budget_value}")
        
        # AI生成完成
        emit_progress(socketio, task_id, 'ai_done', '✅ 攻略生成完成！', 65)
        time.sleep(0.5)
        
        # 插入返佣链接
        emit_progress(socketio, task_id, 'affiliate_start', '🔗 正在添加美团返佣链接...', 70)
        time.sleep(0.5)
        
        emit_progress(socketio, task_id, 'affiliate_hotels', '🏨 正在匹配酒店链接...', 75)
        time.sleep(0.3)
        
        emit_progress(socketio, task_id, 'affiliate_food', '🍜 正在匹配餐厅链接...', 80)
        time.sleep(0.3)
        
        emit_progress(socketio, task_id, 'affiliate_tickets', '🎫 正在匹配景点门票...', 85)
        
        enhanced_content, recommendations = enhance_with_affiliate(content, query, mode)
        
        emit_progress(socketio, task_id, 'affiliate_done', '💰 返佣链接添加完成！', 90)
        time.sleep(0.3)
        
        # 🔥 图片增强：已禁用（当前UI无图片设计）
        # emit_progress(socketio, task_id, 'images', '🖼️ 正在爬取真实图片...', 92)
        # try:
        #     from services.image_crawler import ImageCrawler
        #     image_crawler = ImageCrawler()
        #     enhanced_content = image_crawler.enrich_content_with_images(enhanced_content)
        #     logger.info(f"✅ 图片增强完成")
        # except Exception as e:
        #     logger.warning(f"⚠️ 图片爬取失败: {e}")
        
        logger.info(f"⏭️ 跳过图片爬取（当前UI无图片）")
        emit_progress(socketio, task_id, 'images_done', '⏭️ 跳过图片爬取', 95)
        time.sleep(0.2)
        
        # 统计信息
        emit_progress(socketio, task_id, 'stats', '📊 正在统计攻略信息...', 96)
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
        
        # 🔥 SEO优化：保存为静态页面
        emit_progress(socketio, task_id, 'seo', '📄 正在生成SEO页面...', 98)
        
        try:
            from services.seo_service import get_seo_service
            seo = get_seo_service()
            seo_result = seo.save_guide(query, enhanced_content, stats)
            logger.info(f"📄 SEO页面已生成: {seo_result['url']}")
        except Exception as e:
            logger.warning(f"⚠️ SEO页面生成失败: {e}")
            seo_result = None
        
        # 🔥 保存到用户历史（如果提供了user_id）
        guide_id = None
        if user_id:
            try:
                from services.user_service import get_user_service
                user_service = get_user_service()
                guide_id = user_service.save_user_guide(user_id, {
                    'query': query,
                    'mode': mode,
                    'content': enhanced_content,
                    'stats': stats,
                    'seo_url': seo_result.get('url') if seo_result else None
                })
                logger.info(f"💾 攻略已保存到用户历史: {user_id} | {guide_id}")
            except Exception as e:
                logger.warning(f"⚠️ 保存用户历史失败: {e}")
        
        # 完成
        active_tasks[task_id]['status'] = 'completed'
        active_tasks[task_id]['progress'] = 100
        active_tasks[task_id]['result'] = {
            'content': enhanced_content,
            'recommendations': recommendations,
            'links': all_links,  # 🔥 新增：所有可点击链接
            'stats': stats,
            'seo': seo_result,  # 🔥 新增：SEO页面信息
            'slug': seo_result.get('slug') if seo_result else None,  # 🔥 新增：攻略slug（用于收藏、分享等）
            'guide_id': guide_id  # 🔥 新增：用户攻略ID（如果已登录）
        }
        
        emit_progress(socketio, task_id, 'done', '🎉 攻略生成完成！', 100)
        
        logger.info(f"✅ 任务完成: {task_id} | 字数: {stats['word_count']} | 酒店: {stats['hotels_count']}")
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"❌ 任务失败: {task_id} | 错误: {e}\n{error_traceback}")
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
    
    # === 2. 酒店链接替换（优化正则，匹配更多格式） ===
    # 格式：### 1. XX酒店 或 ### XX酒店 或 **XX酒店**
    hotel_patterns = [
        r'###\s+(?:\d+\.\s+)?(?:[\u4e00-\u9fa5]+之选[：:]\s*)?([^#\n]*?(?:酒店|宾馆|客栈|民宿|度假村|青旅|旅馆|Hotel|Inn)[^#\n]*?)(?:\s+[⭐⭐⭐⭐⭐\s]*)?$',
        r'\*\*([^*]+?(?:酒店|宾馆|客栈|民宿|度假村|青旅|旅馆)[^*]*?)\*\*(?:\s+¥\d+)',  # **酒店名** ¥价格
    ]
    
    seen_hotels = set()
    for pattern in hotel_patterns:
        hotel_matches = list(re.finditer(pattern, content, re.MULTILINE))
        for match in hotel_matches:
            hotel_name = match.group(1).strip()
            
            # 清理名称
            clean_name = re.sub(r'[⭐️\s（）]+', '', hotel_name).strip()
            clean_name = re.sub(r'（.*?）', '', clean_name).strip()
            
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
    
    # 🔥 替换所有酒店的预订链接
    for hotel in recommendations['hotels']:
        hotel_name = hotel['name']
        link = hotel['link']

        # 方案1：替换Markdown格式 [携程/美团](链接占位)
        content = re.sub(
            r'\[(?:携程|美团|预订)[^\]]*?\]\((?:链接占位|占位|#)\)',
            f'[美团预订]({link})',
            content,
            count=1
        )
        # 方案2：替换纯文本"查看详情"
        content = re.sub(
            r'预订[：:]\s*查看详情',
            f'预订：[查看详情]({link})',
            content,
            count=1
        )

    # 🔥 酒店兜底：为没有预订链接的酒店注入链接
    # 查找酒店section中每个 ### N. 酒店名 块，如果缺少预订链接则追加
    for hotel in recommendations['hotels']:
        hotel_name = re.escape(hotel['name'])
        link = hotel['link']
        # 检查该酒店附近是否已有预订链接（向后搜索到下一个 ### 或 ## 为止）
        hotel_section_pattern = rf'(###\s+\d+\.\s+[^\n]*?{hotel_name}[^\n]*?\n)(.*?)(?=###\s+\d+\.|##\s+[^#]|$)'
        hotel_section_match = re.search(hotel_section_pattern, content, re.S)
        if hotel_section_match:
            section_text = hotel_section_match.group(2)
            # 如果这个section中没有美团预订链接
            if '美团预订' not in section_text and 'meituan.com' not in section_text and 'LINK_HOTEL' not in section_text:
                # 在section末尾（下一个 ### 之前）注入预订链接
                insert_point = hotel_section_match.end(2)
                booking_line = f'\n- **预订：** [美团预订]({link})\n'
                content = content[:insert_point] + booking_line + content[insert_point:]
                logger.info(f"🏨 兜底注入酒店链接: {hotel['name']}")
    
    # === 3. 餐厅链接替换（优化正则，匹配多种格式） ===
    # 格式1：**XX文昌鸡饭** ¥50/人
    # 格式2：**午餐：海南粉老店**
    # 格式3：#### 1. 海口文昌鸡饭老店 ¥50-80/人
    food_patterns = [
        # 带价格的餐厅（**餐厅名** ¥价格）
        r'\*\*([^*]+?(?:餐厅|饭店|小吃|海鲜|鸡饭|鸭|羊肉|牛肉|面馆|粉店|粉面|茶餐厅|大排档|火锅|烤肉|烧烤|酒楼|老店|馆|坊|居|轩|斋|记|家|房|厅|店|楼)[^*]*?)\*\*\s*[¥￥]',
        # 标题格式（### 1. 餐厅名）
        r'####?\s+\d+\.\s+([^¥\n]+?(?:餐厅|饭店|海鲜|鸡|鸭|羊|牛|面|粉|饺子|包子|小吃|老店|馆|坊|店)[^¥\n]*)',
        # 纯餐厅名格式（**餐厅名** 后面没有价格）
        r'\*\*([^*]+?(?:馆|坊|楼|厅|店|家|记))\*\*(?!\s*[¥￥])',
    ]
    
    seen_restaurants = set()
    for pattern in food_patterns:
        food_matches = list(re.finditer(pattern, content))
        for match in food_matches:
            restaurant_name = match.group(1).strip()
            
            # 清理名称
            clean_name = re.sub(r'（.*?）', '', restaurant_name).strip()
            clean_name = re.sub(r'\s*店$', '', clean_name).strip()
            
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
    
    # 🔥 餐厅链接替换（改进版：防止重复替换导致嵌套）
    replacement_count = 0
    for restaurant in recommendations['restaurants']:
        restaurant_name = restaurant['name']
        link = restaurant['link']
        
        # 查找包含餐厅名的段落（附近100字符内）
        # 格式示例：**馋人小馆** ... [美团团购](链接占位)
        pattern = rf'\*\*{re.escape(restaurant_name)}[^[]*?\[([^\]]+?团购[^\]]*?)\]\((链接占位|占位|#)\)'
        match = re.search(pattern, content)
        
        if match:
            # 替换这个具体的链接
            old_link_text = f'[{match.group(1)}]({match.group(2)})'
            new_link_text = f'[美团团购]({link})'
            content = content.replace(old_link_text, new_link_text, 1)
            replacement_count += 1
            logger.debug(f"替换餐厅链接: {restaurant_name} -> {link}")
        else:
            # 如果没找到，尝试通用替换（只替换第一个未替换的占位符）
            content = re.sub(
                r'\[([^\]]*?团购[^\]]*?)\]\((链接占位|占位|#)\)',
                f'[美团团购]({link})',
                content,
                count=1
            )
            replacement_count += 1
    
    logger.info(f"餐厅链接替换完成: {replacement_count}个")
    
    # === 4. 门票链接替换（优化正则，匹配DeepSeek实际格式） ===
    # 实际格式：- **雷琼世界地质公园** 门票¥0，免费！[官方预约](链接占位)
    #          - **海南热带野生动植物园** 门票¥158/成人，[提前1天美团购票](链接占位)
    
    # 匹配：**景点名** 门票...链接占位
    # 扩充景点关键词，覆盖更多类型
    ticket_pattern = r'\*\*([^*]+?(?:公园|景区|景点|博物馆|美术馆|纪念馆|动物园|植物园|海洋馆|水族馆|游乐园|乐园|主题公园|古镇|古城|寺|庙|寺庙|塔|楼|阁|山|岛|湖|海|湾|瀑布|溶洞|峡谷|地质公园|森林公园|湿地|温泉|滑雪场|影视城)[^*]*?)\*\*\s+(?:门票|票价)[^[\n]*?\[.*?\]\((?:链接占位|占位|LINK_TICKET)\)'
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
    
    # === 5. 替换LINK_格式占位符（优先处理） ===
    # 格式：[美团团购 💰有返现](LINK_FOOD_餐厅名)
    link_pattern = r'\[([^\]]+)\]\(LINK_(FOOD|HOTEL|TICKET)_([^)]+)\)'
    link_matches = list(re.finditer(link_pattern, content))
    
    logger.info(f"发现 {len(link_matches)} 个LINK_格式占位符")
    
    # 从后往前替换（避免位置偏移）
    for match in reversed(link_matches):
        link_text = match.group(1)  # 链接文字（如"美团团购 💰有返现"）
        link_type = match.group(2)  # FOOD/HOTEL/TICKET
        name = match.group(3)       # 商家名称
        
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
        
        # 替换（保留原文字，只替换链接）
        old_text = match.group(0)
        new_text = f'[{link_text}]({link})'
        content = content[:match.start()] + new_text + content[match.end():]
        
        logger.debug(f"替换LINK_{link_type}: {name} -> {link}")
    
    logger.info(f"LINK_格式替换完成: {len(link_matches)}个")
    
    # === 6. 替换所有剩余的占位符（兜底方案 - 改进版） ===
    # 只替换明确的占位符，避免替换已有的真实链接
    placeholder_patterns = [
        (r'\[([^\]]+)\]\((链接占位|占位|#)\)', None),  # 通用占位符匹配
    ]
    
    replaced_count = 0
    for pattern, _ in placeholder_patterns:
        matches = list(re.finditer(pattern, content))
        
        # 从后往前替换（避免位置偏移）
        for match in reversed(matches):
            link_text = match.group(1)
            placeholder = match.group(2)
            
            # 根据链接文本判断类别
            if '门票' in link_text or '预约' in link_text:
                category = 'ticket'
            elif '酒店' in link_text or '预订' in link_text or '住宿' in link_text:
                category = 'hotel'
            else:
                category = 'food'  # 默认美食
            
            # 生成搜索链接
            search_query = f"{city}"
            link = affiliate.get_search_link(query=search_query, category=category)
            
            # 替换（精确位置替换，避免错误）
            old_text = match.group(0)
            new_text = f'[{link_text}]({link})'
            content = content[:match.start()] + new_text + content[match.end():]
            replaced_count += 1
    
    if replaced_count > 0:
        logger.info(f"兜底替换完成: {replaced_count}个占位符")
    
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
