"""
攻略API - CRUD操作
功能：列表、详情、收藏、删除、分享
"""

from flask import Blueprint, jsonify, request
from loguru import logger
import os
import re
import json
from pathlib import Path

# 创建Blueprint
guides_bp = Blueprint('guides', __name__)

# 攻略存储路径 - 延迟获取，与 seo_service 保持一致
# seo_service 默认保存到 /root/clawd/wildtrip/web/guides（服务器）
# 本地开发时回退到项目相对路径 ../../web/guides
_guides_dir_cache = None

def get_guides_dir():
    """获取攻略存储目录，与seo_service保持一致"""
    global _guides_dir_cache
    if _guides_dir_cache is not None:
        return _guides_dir_cache
    try:
        from services.seo_service import get_seo_service
        seo = get_seo_service()
        _guides_dir_cache = seo.static_dir
        logger.info(f"📂 攻略目录(seo_service): {_guides_dir_cache}")
    except Exception:
        _guides_dir_cache = Path(__file__).parent.parent.parent / 'web' / 'guides'
        logger.info(f"📂 攻略目录(fallback): {_guides_dir_cache}")
    return _guides_dir_cache

# 用户收藏存储（内存，实际应该用数据库）
user_favorites = set()  # 存储 slug


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

        # 过滤掉测试/demo/假攻略
        guides = _filter_valid_guides(guides)

        # 加载 metadata.json
        metadata_map = _load_metadata_map()

        for guide in guides:
            _enrich_guide(guide, metadata_map)

        logger.info(f"📋 返回攻略列表: {len(guides)}篇")

        return jsonify(guides), 200

    except Exception as e:
        logger.error(f"获取攻略列表失败: {e}")
        return jsonify({
            'error': str(e),
            'code': 'INTERNAL_ERROR'
        }), 500


@guides_bp.route('/guides/featured', methods=['GET'])
def get_featured_guides():
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

        # 加载 metadata.json 建立 slug→元数据 映射
        metadata_map = _load_metadata_map()

        # 过滤掉测试/demo/假攻略
        all_guides = _filter_valid_guides(all_guides)

        # 按时间倒序，取前N篇
        featured = sorted(all_guides, key=lambda g: g.get('created_at', ''), reverse=True)[:limit]

        for guide in featured:
            _enrich_guide(guide, metadata_map)

        logger.info(f"⭐ 返回精选攻略: {len(featured)}篇")
        return jsonify(featured), 200

    except Exception as e:
        logger.error(f"获取精选攻略失败: {e}")
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


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
        html_path = get_guides_dir() / f"{slug}.html"
        if not html_path.exists():
            return jsonify({
                'error': '攻略不存在',
                'code': 'NOT_FOUND'
            }), 404
        
        content = html_path.read_text(encoding='utf-8')

        # 提取标题：优先metadata，其次slug，最后HTML
        metadata_map = _load_metadata_map()
        if slug in metadata_map:
            title = _clean_title(metadata_map[slug].get('title', ''))
        else:
            title = _extract_title_from_slug(slug)
            if not title or title.lower() == 'guide' or (len(title) < 4 and title.isascii()):
                title = _extract_title_from_html(html_path)
        
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


@guides_bp.route('/guides/<slug>/favorite', methods=['POST'])
def favorite_guide(slug):
    """收藏攻略"""
    try:
        # 检查攻略是否存在
        html_path = get_guides_dir() / f"{slug}.html"
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


@guides_bp.route('/guides/<slug>/favorite', methods=['DELETE'])
def unfavorite_guide(slug):
    """取消收藏"""
    try:
        user_favorites.discard(slug)
        logger.info(f"⭐ 取消收藏: {slug}")
        
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


@guides_bp.route('/guides/<slug>', methods=['DELETE'])
def delete_guide(slug):
    """删除攻略"""
    try:
        html_path = get_guides_dir() / f"{slug}.html"
        if not html_path.exists():
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


@guides_bp.route('/guides/<slug>/share', methods=['POST'])
def share_guide(slug):
    """生成分享链接"""
    try:
        # 检查攻略是否存在
        html_path = get_guides_dir() / f"{slug}.html"
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


# ===== 辅助函数 =====

# 明确排除的slug列表（测试、demo、重复页面）
_EXCLUDE_SLUGS = {
    'index', 'demo', 'demo-haikou-weekend-7yo-boy-paywall',
    'haikou-weekend-ultimate',
    '上海1天美食游测试-202602042201-ee8f22ca'
}


def _filter_valid_guides(guides):
    """过滤掉测试/demo/假攻略，只保留真实可看的攻略"""
    filtered = []
    for g in guides:
        slug = g['slug']
        # 1. 排除明确的测试/demo页面
        if slug in _EXCLUDE_SLUGS:
            continue
        if slug.startswith('guide-test') or slug.startswith('guide-ui-test'):
            continue
        # 2. 排除文件名中含有未替换占位符的假攻略
        if '金额' in slug or '测试' in slug:
            continue
        # 3. 读取HTML头部检查是否含有[预算]或[金额]占位符
        html_path = get_guides_dir() / f"{slug}.html"
        if html_path.exists():
            try:
                head_content = html_path.read_text(encoding='utf-8')[:500]
                if '[预算]' in head_content or '[金额]' in head_content:
                    continue
            except Exception:
                pass
        filtered.append(g)
    logger.info(f"🔍 攻略过滤: {len(guides)}→{len(filtered)}篇 (排除{len(guides)-len(filtered)}篇假攻略)")
    return filtered


def _load_metadata_map():
    """加载 metadata.json，返回 slug→元数据 映射"""
    metadata_map = {}
    metadata_path = get_guides_dir() / 'metadata.json'
    if metadata_path.exists():
        try:
            meta_list = json.loads(metadata_path.read_text(encoding='utf-8'))
            for m in meta_list:
                metadata_map[m.get('slug', '')] = m
        except Exception as e:
            logger.warning(f"加载metadata.json失败: {e}")
    return metadata_map


def _clean_title(raw_title):
    """清理标题：去掉后缀和开头emoji"""
    if not raw_title:
        return '旅行攻略'
    clean = re.split(r'\s*[-|]\s*(?:野游记|我的行程|省[¥￥])', raw_title)[0].strip()
    # 去掉开头emoji
    clean = re.sub(r'^[\U0001f300-\U0001f9ff\u2600-\u26ff\u2700-\u27bf]+\s*', '', clean)
    return clean or raw_title


def _extract_title_from_slug(slug):
    """从slug提取标题（去掉时间戳和hash后缀）"""
    slug_parts = slug.rsplit('-', 2)
    return slug_parts[0] if slug_parts else slug


def _extract_title_from_html(html_path):
    """从HTML文件的og:title或<title>标签提取标题"""
    try:
        if not html_path.exists():
            return '旅行攻略'
        head = html_path.read_text(encoding='utf-8')[:3000]
        # 优先 og:title
        og_match = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', head)
        if og_match:
            return _clean_title(og_match.group(1))
        # 回退 <title>
        title_match = re.search(r'<title>([^<]+)</title>', head)
        if title_match:
            return _clean_title(title_match.group(1))
        return '旅行攻略'
    except Exception:
        return '旅行攻略'


def _enrich_guide(guide, metadata_map):
    """用metadata或HTML丰富攻略数据"""
    slug = guide['slug']
    if slug in metadata_map:
        meta = metadata_map[slug]
        guide['title'] = _clean_title(meta.get('title', ''))
        guide['destination'] = meta.get('destination', '')
        guide['days'] = meta.get('days', 0)
        guide['budget'] = meta.get('budget', '')
        guide['views'] = meta.get('views', 0)
        guide['likes'] = meta.get('likes', 0)
        guide['cover_image'] = meta.get('cover_image', '')
    else:
        title = _extract_title_from_slug(slug)
        # 如果slug提取的标题是纯英文（非中文），从HTML提取更好的标题
        if not title or title.isascii():
            title = _extract_title_from_html(get_guides_dir() / f"{slug}.html")
        guide['title'] = title
