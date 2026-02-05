"""
用户API - 登录、历史记录、收藏等
"""

from flask import Blueprint, request, jsonify
from loguru import logger

# 创建Blueprint
user_bp = Blueprint('user', __name__)


@user_bp.route('/user/login', methods=['POST'])
def login():
    """
    用户登录（手机号）
    
    请求体:
    {
        "phone": "13800138000",
        "nickname": "张三"  // 可选
    }
    
    响应:
    {
        "user_id": "abc123",
        "phone": "8000",  // 后4位
        "nickname": "张三",
        "guide_count": 5
    }
    """
    try:
        data = request.json
        phone = data.get('phone', '').strip()
        nickname = data.get('nickname', '').strip()
        
        if not phone:
            return jsonify({
                'error': '手机号不能为空',
                'code': 'EMPTY_PHONE'
            }), 400
        
        # 简单验证手机号格式
        if not phone.isdigit() or len(phone) != 11:
            return jsonify({
                'error': '手机号格式不正确',
                'code': 'INVALID_PHONE'
            }), 400
        
        from services.user_service import get_user_service
        
        service = get_user_service()
        user = service.create_or_get_user(phone, nickname)
        
        logger.info(f"✅ 用户登录: {user['user_id']}")
        
        return jsonify(user), 200
        
    except Exception as e:
        logger.error(f"登录失败: {e}")
        return jsonify({
            'error': str(e),
            'code': 'INTERNAL_ERROR'
        }), 500


@user_bp.route('/user/<user_id>/guides', methods=['GET'])
def get_user_guides(user_id):
    """
    获取用户历史攻略
    
    查询参数:
    - limit: 返回数量（默认50）
    
    响应:
    [
        {
            "guide_id": "abc123",
            "query": "上海3天游",
            "created_at": "2026-02-04T12:00:00",
            "stats": {...},
            "seo_url": "/guides/xxx.html",
            "favorite": false
        },
        ...
    ]
    """
    try:
        limit = int(request.args.get('limit', 50))
        
        from services.user_service import get_user_service
        
        service = get_user_service()
        guides = service.get_user_guides(user_id, limit)
        
        # 不返回完整content（太大），只返回摘要
        for guide in guides:
            if 'content' in guide:
                guide['content_preview'] = guide['content'][:200] + '...'
                del guide['content']
        
        logger.info(f"📋 返回用户历史: {user_id} | {len(guides)}篇")
        
        return jsonify(guides), 200
        
    except Exception as e:
        logger.error(f"获取历史失败: {e}")
        return jsonify({
            'error': str(e),
            'code': 'INTERNAL_ERROR'
        }), 500


@user_bp.route('/user/<user_id>/guides/<guide_id>', methods=['GET'])
def get_guide(user_id, guide_id):
    """
    获取单个攻略详情
    
    响应:
    {
        "guide_id": "abc123",
        "query": "上海3天游",
        "content": "完整内容...",
        ...
    }
    """
    try:
        from services.user_service import get_user_service
        
        service = get_user_service()
        guide = service.get_guide_by_id(user_id, guide_id)
        
        if not guide:
            return jsonify({
                'error': '攻略不存在',
                'code': 'GUIDE_NOT_FOUND'
            }), 404
        
        return jsonify(guide), 200
        
    except Exception as e:
        logger.error(f"获取攻略失败: {e}")
        return jsonify({
            'error': str(e),
            'code': 'INTERNAL_ERROR'
        }), 500


@user_bp.route('/user/<user_id>/guides/<guide_id>', methods=['DELETE'])
def delete_guide(user_id, guide_id):
    """删除攻略"""
    try:
        from services.user_service import get_user_service
        
        service = get_user_service()
        success = service.delete_guide(user_id, guide_id)
        
        if not success:
            return jsonify({
                'error': '攻略不存在',
                'code': 'GUIDE_NOT_FOUND'
            }), 404
        
        logger.info(f"🗑️ 删除攻略: {user_id} | {guide_id}")
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logger.error(f"删除失败: {e}")
        return jsonify({
            'error': str(e),
            'code': 'INTERNAL_ERROR'
        }), 500


@user_bp.route('/user/<user_id>/guides/<guide_id>/favorite', methods=['POST'])
def toggle_favorite(user_id, guide_id):
    """切换收藏状态"""
    try:
        from services.user_service import get_user_service
        
        service = get_user_service()
        favorite = service.toggle_favorite(user_id, guide_id)
        
        return jsonify({
            'favorite': favorite
        }), 200
        
    except Exception as e:
        logger.error(f"切换收藏失败: {e}")
        return jsonify({
            'error': str(e),
            'code': 'INTERNAL_ERROR'
        }), 500


@user_bp.route('/user/stats', methods=['GET'])
def get_stats():
    """
    获取用户统计
    
    响应:
    {
        "total_users": 100,
        "total_guides": 500,
        "new_users_week": 20,
        "avg_guides_per_user": 5.0
    }
    """
    try:
        from services.user_service import get_user_service
        
        service = get_user_service()
        stats = service.get_stats()
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"获取统计失败: {e}")
        return jsonify({
            'error': str(e),
            'code': 'INTERNAL_ERROR'
        }), 500
