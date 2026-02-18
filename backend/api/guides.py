"""
攻略API - CRUD操作
<<<<<<< HEAD
功能：列表、详情、收藏、删除、分享
=======
功能：列表、详情、收藏、删除、分享、精选推荐、相关推荐
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3
"""

from flask import Blueprint, jsonify, request
from loguru import logger
import os
<<<<<<< HEAD
=======
import re
import random
import hashlib
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3
from pathlib import Path

# 创建Blueprint
guides_bp = Blueprint('guides', __name__)

# 攻略存储路径
GUIDES_DIR = Path(__file__).parent.parent.parent / 'web' / 'guides'

# 用户收藏存储（内存，实际应该用数据库）
user_favorites = set()  # 存储 slug


<<<<<<< HEAD
@guides_bp.route('/guides', methods=['GET'])
def list_guides():
    """
    获取所有已保存的攻略列表
    
    响应：
    [
        {
            "slug": "haikou-3day-family-trip",
            "url": "/guides/haikou-3day-family-trip.html",
            "created_at": "2026-02-04",
            "title": "海口3天亲子游"
        },
        ...
    ]
    """
    try:
        from services.seo_service import get_seo_service
        
        seo = get_seo_service()
        guides = seo.get_all_guides()
        
        # 提取标题（从slug中提取）
        for guide in guides:
            # slug格式：城市-天数-类型-时间戳-hash
            # 示例：上海3天美食游测试-202602041633-51b4d9df
            slug_parts = guide['slug'].rsplit('-', 2)  # 分割最后两部分（时间和hash）
            guide['title'] = slug_parts[0] if slug_parts else guide['slug']
        
        logger.info(f"📋 返回攻略列表: {len(guides)}篇")
        
        return jsonify(guides), 200
        
    except Exception as e:
        logger.error(f"获取攻略列表失败: {e}")
        return jsonify({
            'error': str(e),
            'code': 'INTERNAL_ERROR'
        }), 500
=======
# ==========================================
# 推荐系统辅助函数 & 数据
# ==========================================

# 热门城市封面图（稳定CDN直链，每城市一张精选图片）
CITY_IMAGES = {
    '海口': 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=800&h=600&fit=crop',   # 海口海滨
    '三亚': 'https://images.unsplash.com/photo-1540979388789-6cee28a1cdc9?w=800&h=600&fit=crop',  # 三亚海滩
    '成都': 'https://images.unsplash.com/photo-1590559899731-a382839e5549?w=800&h=600&fit=crop',   # 成都熊猫
    '重庆': 'https://images.unsplash.com/photo-1584464491033-06628f3a6b7b?w=800&h=600&fit=crop',   # 重庆夜景
    '上海': 'https://images.unsplash.com/photo-1537531383496-f4749b67fd74?w=800&h=600&fit=crop',   # 上海外滩
    '北京': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800&h=600&fit=crop',   # 北京故宫
    '西安': 'https://images.unsplash.com/photo-1603366445787-09714680cbf1?w=800&h=600&fit=crop',   # 西安古城
    '杭州': 'https://images.unsplash.com/photo-1598887142487-3c854d51eabb?w=800&h=600&fit=crop',   # 杭州西湖
    '厦门': 'https://images.unsplash.com/photo-1564578933883-cb2ae1a58e98?w=800&h=600&fit=crop',   # 厦门鼓浪屿
    '大理': 'https://images.unsplash.com/photo-1587974928442-77dc3e0dba72?w=800&h=600&fit=crop',   # 大理洱海
    '丽江': 'https://images.unsplash.com/photo-1573China553531-1f5e5e7e11f2?w=800&h=600&fit=crop', # 丽江古城
    '桂林': 'https://images.unsplash.com/photo-1529921879218-f99546d03a94?w=800&h=600&fit=crop',   # 桂林山水
    '青岛': 'https://images.unsplash.com/photo-1584464491033-06628f3a6b7b?w=800&h=600&fit=crop',   # 青岛海滨
    '南京': 'https://images.unsplash.com/photo-1583265627959-fb7042f56448?w=800&h=600&fit=crop',   # 南京古都
    '长沙': 'https://images.unsplash.com/photo-1583265627959-fb7042f56448?w=800&h=600&fit=crop',   # 长沙橘子洲
    '武汉': 'https://images.unsplash.com/photo-1583265627959-fb7042f56448?w=800&h=600&fit=crop',   # 武汉樱花
    '广州': 'https://images.unsplash.com/photo-1583265627959-fb7042f56448?w=800&h=600&fit=crop',   # 广州塔
    '深圳': 'https://images.unsplash.com/photo-1518098268026-4e89f1a2cd8e?w=800&h=600&fit=crop',   # 深圳现代
    '昆明': 'https://images.unsplash.com/photo-1587974928442-77dc3e0dba72?w=800&h=600&fit=crop',   # 昆明春城
    '拉萨': 'https://images.unsplash.com/photo-1585409677983-0f6c41ca9c3b?w=800&h=600&fit=crop',   # 拉萨布达拉宫
    '太原': 'https://images.unsplash.com/photo-1547981609-4b6bfe67ca0b?w=800&h=600&fit=crop',      # 太原古建筑
    '沈阳': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800&h=600&fit=crop',   # 沈阳故宫
    '哈尔滨': 'https://images.unsplash.com/photo-1516912481808-3406841bd33c?w=800&h=600&fit=crop', # 哈尔滨冰雪
    '苏州': 'https://images.unsplash.com/photo-1598887142487-3c854d51eabb?w=800&h=600&fit=crop',   # 苏州园林
}

# 旅游分类标签
TRAVEL_CATEGORIES = ['亲子游', '美食游', '穷游', '周末游', '蜜月游', '自驾游', '文化游', '海岛游']


def _extract_destination(text):
    """从slug或查询文本中智能提取目的地城市"""
    for city in CITY_IMAGES.keys():
        if city in text:
            return city
    return None


def _extract_info_from_slug(slug):
    """从slug中提取目的地、天数、分类等信息"""
    info = {
        'destination': None,
        'days': None,
        'category': None,
        'budget': None
    }
    info['destination'] = _extract_destination(slug)

    days_match = re.search(r'(\d+)\s*[天日]', slug)
    if days_match:
        info['days'] = int(days_match.group(1))

    for cat in TRAVEL_CATEGORIES:
        if cat.replace('游', '') in slug:
            info['category'] = cat
            break

    budget_match = re.search(r'(\d{3,5})', slug)
    if budget_match:
        info['budget'] = int(budget_match.group(1))

    return info


def _get_city_image(city, width=800, height=600):
    """获取城市封面图片URL（稳定CDN直链）"""
    # 优先匹配城市固定图片
    if city in CITY_IMAGES:
        return CITY_IMAGES[city]
    # 未匹配的城市，使用通用旅游图片
    return 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&h=600&fit=crop'


def _generate_stable_stats(slug):
    """基于slug生成稳定的模拟统计数据"""
    hash_val = int(hashlib.md5(slug.encode()).hexdigest()[:8], 16)
    return {
        'views': 100 + (hash_val % 900),
        'likes': 10 + (hash_val % 90)
    }


def _build_guide_card(slug, title=None):
    """构建攻略卡片数据（优先使用元数据）"""
    # 🔥 先尝试从元数据获取完整信息
    try:
        from services.seo_service import get_seo_service
        seo = get_seo_service()
        metadata = seo.load_metadata(slug)
        if metadata and metadata.get('title'):
            stats = _generate_stable_stats(slug)
            return {
                'slug': slug,
                'title': metadata.get('title', slug),
                'destination': metadata.get('destination', '旅游'),
                'days': metadata.get('days'),
                'category': metadata.get('category', '自由行'),
                'budget': metadata.get('budget'),
                'cover_image': metadata.get('cover_image', ''),
                'views': metadata.get('views', 0) or stats['views'],
                'likes': metadata.get('likes', 0) or stats['likes'],
                'url': f"/guides/{slug}.html"
            }
    except Exception:
        pass

    # 回退：从slug中提取信息
    info = _extract_info_from_slug(slug)

    # 🔥 更好的标题提取：去掉末尾的时间戳和hash
    if not title:
        # slug格式：中文内容-时间戳-hash（如"深圳3天美食游-202602151234-abc12345"）
        # 去掉最后两段（时间戳和hash）
        parts = slug.rsplit('-', 2)
        if len(parts) >= 3:
            title = parts[0]
        elif len(parts) == 2:
            # 可能时间戳和hash连在一起
            title = parts[0]
        else:
            title = slug
        # 清理标题中的特殊字符
        title = re.sub(r'[_\-]+', ' ', title).strip()
        if not title:
            title = slug[:30]

    city = info['destination'] or '旅游'
    stats = _generate_stable_stats(slug)

    return {
        'slug': slug,
        'title': title,
        'destination': city,
        'days': info['days'],
        'category': info['category'] or '自由行',
        'budget': info['budget'],
        'cover_image': _get_city_image(city),
        'views': stats['views'],
        'likes': stats['likes'],
        'url': f"/guides/{slug}.html"
    }


# 预设精选攻略数据（当数据库中没有足够攻略时使用）
PRESET_FEATURED = [
    {
        'slug': '_preset_haikou_3day',
        'title': '海口3天亲子游攻略',
        'destination': '海口',
        'days': 3,
        'category': '亲子游',
        'budget': 5000,
        'cover_image': _get_city_image('海口'),
        'views': 856,
        'likes': 72,
        'query': '海口3天亲子游，预算5000'
    },
    {
        'slug': '_preset_chengdu_2day',
        'title': '成都2天美食之旅',
        'destination': '成都',
        'days': 2,
        'category': '美食游',
        'budget': 2000,
        'cover_image': _get_city_image('成都'),
        'views': 1203,
        'likes': 98,
        'query': '成都2天美食游，预算2000'
    },
    {
        'slug': '_preset_shanghai_weekend',
        'title': '上海周末轻松游',
        'destination': '上海',
        'days': 2,
        'category': '周末游',
        'budget': 1000,
        'cover_image': _get_city_image('上海'),
        'views': 645,
        'likes': 51,
        'query': '上海周末游，预算1000'
    },
    {
        'slug': '_preset_xian_4day',
        'title': '西安4天深度穷游',
        'destination': '西安',
        'days': 4,
        'category': '穷游',
        'budget': 800,
        'cover_image': _get_city_image('西安'),
        'views': 932,
        'likes': 85,
        'query': '西安4天穷游，预算800'
    },
    {
        'slug': '_preset_hangzhou_3day',
        'title': '杭州3天文化之旅',
        'destination': '杭州',
        'days': 3,
        'category': '文化游',
        'budget': 3000,
        'cover_image': _get_city_image('杭州'),
        'views': 778,
        'likes': 63,
        'query': '杭州3天文化游，预算3000'
    },
    {
        'slug': '_preset_xiamen_3day',
        'title': '厦门3天海岛度假',
        'destination': '厦门',
        'days': 3,
        'category': '海岛游',
        'budget': 3500,
        'cover_image': _get_city_image('厦门'),
        'views': 1024,
        'likes': 89,
        'query': '厦门3天海岛游，预算3500'
    },
]


def _extract_text_from_html(html_content):
    """
    从HTML攻略内容中提取可读的Markdown文本
    用于旧攻略（没有单独保存Markdown文件的情况）
    """
    import re

    # 移除 script 和 style 标签
    text = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', html_content, flags=re.IGNORECASE)
    text = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', html_content, flags=re.IGNORECASE)

    # 移除 head 标签
    text = re.sub(r'<head[^>]*>[\s\S]*?</head>', '', text, flags=re.IGNORECASE)

    # 提取 timeline-content 区域（主要内容区）
    timeline_blocks = re.findall(
        r'<div class="timeline-content">([\s\S]*?)</div>\s*</div>',
        text, flags=re.IGNORECASE
    )

    # 提取 day-title 标题
    day_titles = re.findall(
        r'<(?:h2|div)[^>]*class="[^"]*day-title[^"]*"[^>]*>([\s\S]*?)</(?:h2|div)>',
        text, flags=re.IGNORECASE
    )

    # 如果有 timeline 内容，组装为 Markdown
    if timeline_blocks or day_titles:
        md_parts = []
        # 提取标题
        title_match = re.search(r'<h1[^>]*>(.*?)</h1>', text, flags=re.IGNORECASE)
        if title_match:
            title_text = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
            md_parts.append(f"# {title_text}\n")

        # 提取所有day区块
        day_pattern = re.compile(
            r'<div[^>]*class="[^"]*day-section[^"]*"[^>]*>([\s\S]*?)(?=<div[^>]*class="[^"]*day-section|$)',
            re.IGNORECASE
        )
        for day_match in day_pattern.finditer(text):
            block = day_match.group(1)
            # 提取day标题
            dt = re.search(r'Day\s*(\d+)', block)
            subtitle = re.search(r'day-subtitle[^>]*>(.*?)</', block)
            if dt:
                day_num = dt.group(1)
                sub_text = ''
                if subtitle:
                    sub_text = re.sub(r'<[^>]+>', '', subtitle.group(1)).strip()
                md_parts.append(f"\n## Day {day_num} {sub_text}\n")

            # 提取时间点和活动
            time_points = re.findall(r'time-point[^>]*>(.*?)</', block)
            activity_titles = re.findall(r'activity-title[^>]*>(.*?)</', block)
            activity_descs = re.findall(r'activity-desc[^>]*>(.*?)</', block)

            for i in range(max(len(time_points), len(activity_titles))):
                tp = time_points[i].strip() if i < len(time_points) else ''
                at = re.sub(r'<[^>]+>', '', activity_titles[i]).strip() if i < len(activity_titles) else ''
                ad = re.sub(r'<[^>]+>', '', activity_descs[i]).strip() if i < len(activity_descs) else ''
                if tp or at:
                    line = f"**{tp}** {at}" if tp else f"**{at}**"
                    md_parts.append(line)
                    if ad:
                        md_parts.append(f"  {ad}\n")

        if md_parts:
            return '\n'.join(md_parts)

    # 最后的回退：简单去除所有HTML标签
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    # 截取前5000字符
    return text[:5000] if len(text) > 5000 else text


# ==========================================
# API 路由（注意：featured/related 必须在 <slug> 之前）
# ==========================================

@guides_bp.route('/guides', methods=['GET'])
def list_guides():
    """获取所有已保存的攻略列表"""
    try:
        from services.seo_service import get_seo_service

        seo = get_seo_service()
        guides = seo.get_all_guides()

        for guide in guides:
            slug_parts = guide['slug'].rsplit('-', 2)
            guide['title'] = slug_parts[0] if slug_parts else guide['slug']

        logger.info(f"📋 返回攻略列表: {len(guides)}篇")
        return jsonify(guides), 200

    except Exception as e:
        logger.error(f"获取攻略列表失败: {e}")
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3


@guides_bp.route('/guides/featured', methods=['GET'])
def get_featured_guides():
<<<<<<< HEAD
    """
    获取精选攻略（取最近生成的N篇）

    参数：
      limit: 返回数量（默认6）
    """
    try:
        from services.seo_service import get_seo_service
        limit = int(request.args.get('limit', 6))
        seo = get_seo_service()
        all_guides = seo.get_all_guides()

        if not all_guides:
            return jsonify([]), 200

        # 按时间倒序，取前N篇
        featured = sorted(all_guides, key=lambda g: g.get('created_at', ''), reverse=True)[:limit]

        for guide in featured:
            slug_parts = guide['slug'].rsplit('-', 2)
            guide['title'] = slug_parts[0] if slug_parts else guide['slug']

        logger.info(f"⭐ 返回精选攻略: {len(featured)}篇")
=======
    """获取精选攻略（首页展示）- 优先使用元数据"""
    try:
        limit = request.args.get('limit', 6, type=int)
        limit = min(limit, 12)

        featured = []

        # 🔥 优先从元数据加载（包含封面图、目的地等完整信息）
        try:
            from services.seo_service import get_seo_service
            seo = get_seo_service()
            all_metadata = seo.get_all_metadata()

            for meta in all_metadata[:limit]:
                # 生成稳定的统计数据（如果元数据没有）
                stats = _generate_stable_stats(meta.get('slug', ''))
                featured.append({
                    'slug': meta.get('slug', ''),
                    'title': meta.get('title', '旅行攻略'),
                    'destination': meta.get('destination', '旅游'),
                    'days': meta.get('days'),
                    'category': meta.get('category', '自由行'),
                    'budget': meta.get('budget'),
                    'cover_image': meta.get('cover_image', ''),
                    'views': meta.get('views', 0) or stats['views'],
                    'likes': meta.get('likes', 0) or stats['likes'],
                    'url': meta.get('url', f"/guides/{meta.get('slug', '')}.html")
                })
            logger.info(f"🌟 从元数据加载精选攻略: {len(featured)}篇")
        except Exception as e:
            logger.warning(f"⚠️ 元数据加载失败，回退到文件扫描: {e}")

        # 如果元数据不够，从文件系统补充
        if len(featured) < limit and GUIDES_DIR.exists():
            existing_slugs = {g['slug'] for g in featured}
            html_files = sorted(
                GUIDES_DIR.glob('*.html'),
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )
            for html_file in html_files:
                if len(featured) >= limit:
                    break
                slug = html_file.stem
                if slug not in existing_slugs:
                    card = _build_guide_card(slug)
                    featured.append(card)
                    existing_slugs.add(slug)

        # 如果还不够，使用预设数据补充
        if len(featured) < limit:
            remaining = limit - len(featured)
            existing_destinations = {g.get('destination') for g in featured}
            for preset in PRESET_FEATURED:
                if remaining <= 0:
                    break
                if preset['destination'] not in existing_destinations:
                    featured.append(preset)
                    existing_destinations.add(preset['destination'])
                    remaining -= 1

        logger.info(f"🌟 返回精选攻略: {len(featured)}篇")
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3
        return jsonify(featured), 200

    except Exception as e:
        logger.error(f"获取精选攻略失败: {e}")
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


<<<<<<< HEAD
@guides_bp.route('/guides/<slug>', methods=['GET'])
def get_guide_detail(slug):
    """
    获取攻略详情
    
    响应：
    {
        "slug": "...",
        "title": "...",
        "content": "...",
        "word_count": 2010,
        "is_favorited": false,
        "created_at": "2026-02-04"
    }
    """
    try:
        # 读取HTML文件
=======
@guides_bp.route('/guides/related', methods=['GET'])
def get_related_guides():
    """获取相关推荐攻略（结果页展示）"""
    try:
        destination = request.args.get('destination', '')
        current_slug = request.args.get('slug', '')
        limit = request.args.get('limit', 3, type=int)
        limit = min(limit, 6)

        related = []

        if GUIDES_DIR.exists():
            html_files = list(GUIDES_DIR.glob('*.html'))
            same_dest = []
            diff_dest = []

            for html_file in html_files:
                slug = html_file.stem
                if slug == current_slug:
                    continue
                info = _extract_info_from_slug(slug)
                if info['destination'] == destination:
                    same_dest.append(slug)
                else:
                    diff_dest.append(slug)

            candidates = same_dest + diff_dest
            for slug in candidates[:limit]:
                card = _build_guide_card(slug)
                related.append(card)

        if len(related) < limit:
            remaining = limit - len(related)
            existing_slugs = {g['slug'] for g in related}
            existing_slugs.add(current_slug)
            for preset in PRESET_FEATURED:
                if remaining <= 0:
                    break
                if preset['slug'] not in existing_slugs and preset['destination'] != destination:
                    related.append(preset)
                    existing_slugs.add(preset['slug'])
                    remaining -= 1

        logger.info(f"🔗 返回相关推荐: {len(related)}篇 (目的地: {destination})")
        return jsonify(related), 200

    except Exception as e:
        logger.error(f"获取相关推荐失败: {e}")
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@guides_bp.route('/guides/<slug>', methods=['GET'])
def get_guide_detail(slug):
    """获取攻略详情（包含元数据）"""
    try:
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3
        html_path = GUIDES_DIR / f"{slug}.html"
        if not html_path.exists():
            return jsonify({
                'error': '攻略不存在',
                'code': 'NOT_FOUND'
            }), 404
<<<<<<< HEAD
        
        content = html_path.read_text(encoding='utf-8')
        
        # 提取标题
        slug_parts = slug.rsplit('-', 2)
        title = slug_parts[0] if slug_parts else slug
        
        # 统计字数（简单统计，实际应该去除HTML标签）
        word_count = len(content)
        
        logger.info(f"📖 返回攻略详情: {slug}")
        
        return jsonify({
            'slug': slug,
            'title': title,
            'content': content,
            'word_count': word_count,
            'is_favorited': slug in user_favorites,
            'created_at': html_path.stat().st_mtime,
            'url': f"/guides/{slug}.html"
        }), 200
        
    except Exception as e:
        logger.error(f"获取攻略详情失败: {e}")
        return jsonify({
            'error': str(e),
            'code': 'INTERNAL_ERROR'
        }), 500
=======

        content = html_path.read_text(encoding='utf-8')
        slug_parts = slug.rsplit('-', 2)
        title = slug_parts[0] if slug_parts else slug
        word_count = len(content)

        # 🔥 尝试加载元数据以获取更丰富的信息
        metadata = {}
        try:
            from services.seo_service import get_seo_service
            seo = get_seo_service()
            metadata = seo.load_metadata(slug)
        except Exception as e:
            logger.warning(f"⚠️ 加载元数据失败: {e}")

        # 🔥 尝试加载原始Markdown内容（供小程序原生渲染）
        markdown_content = ''
        md_path = GUIDES_DIR / '_markdown' / f"{slug}.md"
        if md_path.exists():
            try:
                markdown_content = md_path.read_text(encoding='utf-8')
                logger.info(f"📝 加载Markdown内容: {slug}")
            except Exception as e:
                logger.warning(f"⚠️ 加载Markdown失败: {e}")

        # 🔥 如果没有Markdown文件，从HTML中提取纯文本内容
        if not markdown_content:
            markdown_content = _extract_text_from_html(content)

        logger.info(f"📖 返回攻略详情: {slug}")

        return jsonify({
            'slug': slug,
            'title': metadata.get('title', title),
            'content': content,
            'markdown_content': markdown_content,
            'destination': metadata.get('destination', ''),
            'days': metadata.get('days'),
            'budget': metadata.get('budget'),
            'category': metadata.get('category', '自由行'),
            'cover_image': metadata.get('cover_image', ''),
            'word_count': metadata.get('word_count', word_count),
            'hotels_count': metadata.get('hotels_count', 0),
            'restaurants_count': metadata.get('restaurants_count', 0),
            'tickets_count': metadata.get('tickets_count', 0),
            'is_favorited': slug in user_favorites,
            'created_at': metadata.get('created_at', html_path.stat().st_mtime),
            'url': f"/guides/{slug}.html"
        }), 200

    except Exception as e:
        logger.error(f"获取攻略详情失败: {e}")
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3


@guides_bp.route('/guides/<slug>/favorite', methods=['POST'])
def favorite_guide(slug):
    """收藏攻略"""
    try:
<<<<<<< HEAD
        # 检查攻略是否存在
        html_path = GUIDES_DIR / f"{slug}.html"
        if not html_path.exists():
            return jsonify({
                'error': '攻略不存在',
                'code': 'NOT_FOUND'
            }), 404
        
        user_favorites.add(slug)
        logger.info(f"⭐ 收藏攻略: {slug}")
        
        return jsonify({
            'success': True,
            'is_favorited': True
        }), 200
        
    except Exception as e:
        logger.error(f"收藏失败: {e}")
        return jsonify({
            'error': str(e),
            'code': 'INTERNAL_ERROR'
        }), 500
=======
        html_path = GUIDES_DIR / f"{slug}.html"
        if not html_path.exists():
            return jsonify({'error': '攻略不存在', 'code': 'NOT_FOUND'}), 404

        user_favorites.add(slug)
        logger.info(f"⭐ 收藏攻略: {slug}")
        return jsonify({'success': True, 'is_favorited': True}), 200

    except Exception as e:
        logger.error(f"收藏失败: {e}")
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3


@guides_bp.route('/guides/<slug>/favorite', methods=['DELETE'])
def unfavorite_guide(slug):
    """取消收藏"""
    try:
        user_favorites.discard(slug)
        logger.info(f"⭐ 取消收藏: {slug}")
<<<<<<< HEAD
        
        return jsonify({
            'success': True,
            'is_favorited': False
        }), 200
        
    except Exception as e:
        logger.error(f"取消收藏失败: {e}")
        return jsonify({
            'error': str(e),
            'code': 'INTERNAL_ERROR'
        }), 500
=======
        return jsonify({'success': True, 'is_favorited': False}), 200

    except Exception as e:
        logger.error(f"取消收藏失败: {e}")
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3


@guides_bp.route('/guides/<slug>', methods=['DELETE'])
def delete_guide(slug):
    """删除攻略"""
    try:
        html_path = GUIDES_DIR / f"{slug}.html"
        if not html_path.exists():
<<<<<<< HEAD
            return jsonify({
                'error': '攻略不存在',
                'code': 'NOT_FOUND'
            }), 404
        
        # 删除文件
        html_path.unlink()
        
        # 从收藏中移除
        user_favorites.discard(slug)
        
        logger.info(f"🗑️ 删除攻略: {slug}")
        
        return jsonify({
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"删除失败: {e}")
        return jsonify({
            'error': str(e),
            'code': 'INTERNAL_ERROR'
        }), 500
=======
            return jsonify({'error': '攻略不存在', 'code': 'NOT_FOUND'}), 404

        html_path.unlink()
        user_favorites.discard(slug)
        logger.info(f"🗑️ 删除攻略: {slug}")
        return jsonify({'success': True}), 200

    except Exception as e:
        logger.error(f"删除失败: {e}")
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3


@guides_bp.route('/guides/<slug>/share', methods=['POST'])
def share_guide(slug):
    """生成分享链接"""
    try:
<<<<<<< HEAD
        # 检查攻略是否存在
        html_path = GUIDES_DIR / f"{slug}.html"
        if not html_path.exists():
            return jsonify({
                'error': '攻略不存在',
                'code': 'NOT_FOUND'
            }), 404
        
        # 生成分享链接（实际应该用短链服务）
        share_url = f"https://wildtrip.vip/guides/{slug}.html"
        
        logger.info(f"🔗 生成分享链接: {slug}")
        
        return jsonify({
            'share_url': share_url,
            'slug': slug
        }), 200
        
    except Exception as e:
        logger.error(f"生成分享链接失败: {e}")
        return jsonify({
            'error': str(e),
            'code': 'INTERNAL_ERROR'
        }), 500
=======
        html_path = GUIDES_DIR / f"{slug}.html"
        if not html_path.exists():
            return jsonify({'error': '攻略不存在', 'code': 'NOT_FOUND'}), 404

        share_url = f"https://wildtrip.vip/guides/{slug}.html"
        logger.info(f"🔗 生成分享链接: {slug}")
        return jsonify({'share_url': share_url, 'slug': slug}), 200

    except Exception as e:
        logger.error(f"生成分享链接失败: {e}")
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@guides_bp.route('/guides/migrate-metadata', methods=['POST'])
def migrate_metadata():
    """
    🔥 一次性迁移工具：为已有HTML攻略生成元数据JSON
    对没有元数据的旧攻略，从slug/文件中提取信息并保存
    """
    try:
        from services.seo_service import get_seo_service
        seo = get_seo_service()

        if not GUIDES_DIR.exists():
            return jsonify({'error': '攻略目录不存在', 'migrated': 0}), 404

        migrated = 0
        skipped = 0

        for html_file in GUIDES_DIR.glob('*.html'):
            slug = html_file.stem
            # 跳过已有元数据的
            existing = seo.load_metadata(slug)
            if existing:
                skipped += 1
                continue

            # 从slug提取信息
            info = _extract_info_from_slug(slug)

            # 从slug提取标题（去掉时间戳和hash）
            parts = slug.rsplit('-', 2)
            title = parts[0] if len(parts) >= 3 else slug
            title = re.sub(r'[_\-]+', ' ', title).strip() or slug[:30]

            city = info['destination'] or '旅游'

            # 构建元数据
            metadata = {
                'slug': slug,
                'title': title,
                'destination': city,
                'days': info['days'],
                'budget': info['budget'],
                'category': info['category'] or '自由行',
                'cover_image': _get_city_image(city),
                'url': f'/guides/{slug}.html',
                'word_count': 0,
                'hotels_count': 0,
                'restaurants_count': 0,
                'tickets_count': 0,
                'created_at': html_file.stat().st_mtime,
                'views': 0,
                'likes': 0
            }

            # 尝试从HTML内容统计字数
            try:
                content = html_file.read_text(encoding='utf-8')
                metadata['word_count'] = len(content)
                # 尝试提取封面图
                cover = seo.extract_cover_image(content, city)
                if cover:
                    metadata['cover_image'] = cover
            except Exception:
                pass

            seo.save_to_metadata(slug, metadata)
            migrated += 1
            logger.info(f"📋 迁移元数据: {slug} | {city} | {title[:20]}")

        logger.info(f"✅ 元数据迁移完成: {migrated}篇新增, {skipped}篇已存在")
        return jsonify({
            'success': True,
            'migrated': migrated,
            'skipped': skipped
        }), 200

    except Exception as e:
        logger.error(f"元数据迁移失败: {e}")
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3
