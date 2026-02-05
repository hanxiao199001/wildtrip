"""
攻略API - CRUD操作
功能：列表、详情、收藏、删除、分享
"""

from flask import Blueprint, jsonify, request
from loguru import logger
import os
from pathlib import Path

# 创建Blueprint
guides_bp = Blueprint('guides', __name__)

# 攻略存储路径
GUIDES_DIR = Path(__file__).parent.parent.parent / 'web' / 'guides'

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
        html_path = GUIDES_DIR / f"{slug}.html"
        if not html_path.exists():
            return jsonify({
                'error': '攻略不存在',
                'code': 'NOT_FOUND'
            }), 404
        
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


@guides_bp.route('/guides/<slug>/favorite', methods=['POST'])
def favorite_guide(slug):
    """收藏攻略"""
    try:
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
        html_path = GUIDES_DIR / f"{slug}.html"
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
