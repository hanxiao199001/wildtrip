"""
攻略API - CRUD操作
功能：列表、详情、收藏、删除、分享、精选推荐、相关推荐
"""

from flask import Blueprint, jsonify, request
from loguru import logger
import os
import re
import random
import hashlib
from pathlib import Path

# 创建Blueprint
guides_bp = Blueprint('guides', __name__)

# 攻略存储路径
GUIDES_DIR = Path(__file__).parent.parent.parent / 'web' / 'guides'

# 用户收藏存储（内存，实际应该用数据库）
user_favorites = set()  # 存储 slug


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
    """构建攻略卡片数据"""
    info = _extract_info_from_slug(slug)
    if not title:
        slug_parts = slug.rsplit('-', 2)
        title = slug_parts[0] if slug_parts else slug

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


@guides_bp.route('/guides/featured', methods=['GET'])
def get_featured_guides():
    """获取精选攻略（首页展示）"""
    try:
        limit = request.args.get('limit', 6, type=int)
        limit = min(limit, 12)

        featured = []

        if GUIDES_DIR.exists():
            html_files = sorted(
                GUIDES_DIR.glob('*.html'),
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )
            for html_file in html_files[:limit]:
                slug = html_file.stem
                card = _build_guide_card(slug)
                featured.append(card)

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
        return jsonify(featured), 200

    except Exception as e:
        logger.error(f"获取精选攻略失败: {e}")
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


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
    """获取攻略详情"""
    try:
        html_path = GUIDES_DIR / f"{slug}.html"
        if not html_path.exists():
            return jsonify({
                'error': '攻略不存在',
                'code': 'NOT_FOUND'
            }), 404

        content = html_path.read_text(encoding='utf-8')
        slug_parts = slug.rsplit('-', 2)
        title = slug_parts[0] if slug_parts else slug
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
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@guides_bp.route('/guides/<slug>/favorite', methods=['POST'])
def favorite_guide(slug):
    """收藏攻略"""
    try:
        html_path = GUIDES_DIR / f"{slug}.html"
        if not html_path.exists():
            return jsonify({'error': '攻略不存在', 'code': 'NOT_FOUND'}), 404

        user_favorites.add(slug)
        logger.info(f"⭐ 收藏攻略: {slug}")
        return jsonify({'success': True, 'is_favorited': True}), 200

    except Exception as e:
        logger.error(f"收藏失败: {e}")
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@guides_bp.route('/guides/<slug>/favorite', methods=['DELETE'])
def unfavorite_guide(slug):
    """取消收藏"""
    try:
        user_favorites.discard(slug)
        logger.info(f"⭐ 取消收藏: {slug}")
        return jsonify({'success': True, 'is_favorited': False}), 200

    except Exception as e:
        logger.error(f"取消收藏失败: {e}")
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@guides_bp.route('/guides/<slug>', methods=['DELETE'])
def delete_guide(slug):
    """删除攻略"""
    try:
        html_path = GUIDES_DIR / f"{slug}.html"
        if not html_path.exists():
            return jsonify({'error': '攻略不存在', 'code': 'NOT_FOUND'}), 404

        html_path.unlink()
        user_favorites.discard(slug)
        logger.info(f"🗑️ 删除攻略: {slug}")
        return jsonify({'success': True}), 200

    except Exception as e:
        logger.error(f"删除失败: {e}")
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@guides_bp.route('/guides/<slug>/share', methods=['POST'])
def share_guide(slug):
    """生成分享链接"""
    try:
        html_path = GUIDES_DIR / f"{slug}.html"
        if not html_path.exists():
            return jsonify({'error': '攻略不存在', 'code': 'NOT_FOUND'}), 404

        share_url = f"https://wildtrip.vip/guides/{slug}.html"
        logger.info(f"🔗 生成分享链接: {slug}")
        return jsonify({'share_url': share_url, 'slug': slug}), 200

    except Exception as e:
        logger.error(f"生成分享链接失败: {e}")
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500
