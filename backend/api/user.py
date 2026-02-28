"""
用户API - 登录、历史记录、收藏等
"""

import os
import requests as http_requests
from flask import Blueprint, request, jsonify
from loguru import logger

# 创建Blueprint
user_bp = Blueprint('user', __name__)


@user_bp.route('/user/login', methods=['POST'])
def login():
    """
    微信小程序登录（code换openid）

    请求体:
    {
        "code": "wx.login()返回的code"
    }

    响应:
    {
        "success": true,
        "openid": "oXXXX...",
        "user_id": "abc123",
        "nickname": "用户xxxx",
        "guide_count": 5
    }
    """
    try:
        data = request.json
        code = data.get('code', '').strip() if data else ''

        if not code:
            return jsonify({
                'success': False,
                'error': 'code不能为空',
                'code': 'EMPTY_CODE'
            }), 400

        # 获取微信配置
        appid = os.getenv('WECHAT_APPID', '')
        secret = os.getenv('WECHAT_SECRET', '')

        if not appid or not secret:
            logger.error("❌ 微信凭证未配置: WECHAT_APPID 或 WECHAT_SECRET 为空")
            return jsonify({
                'success': False,
                'error': '服务器微信配置缺失，请联系管理员',
                'code': 'WECHAT_CONFIG_MISSING'
            }), 500

        # 调用微信 jscode2session 接口，用 code 换 openid
        wx_url = (
            f"https://api.weixin.qq.com/sns/jscode2session"
            f"?appid={appid}"
            f"&secret={secret}"
            f"&js_code={code}"
            f"&grant_type=authorization_code"
        )

        wx_resp = http_requests.get(wx_url, timeout=10)
        wx_data = wx_resp.json()

        logger.info(f"微信jscode2session响应: {wx_data}")

        # 检查微信返回结果
        if 'errcode' in wx_data and wx_data['errcode'] != 0:
            logger.error(f"❌ 微信登录失败: {wx_data}")
            return jsonify({
                'success': False,
                'error': f"微信登录失败: {wx_data.get('errmsg', '未知错误')}",
                'code': 'WECHAT_LOGIN_FAILED'
            }), 400

        openid = wx_data.get('openid', '')
        session_key = wx_data.get('session_key', '')

        if not openid:
            logger.error(f"❌ 未获取到openid: {wx_data}")
            return jsonify({
                'success': False,
                'error': '未获取到用户标识',
                'code': 'NO_OPENID'
            }), 400

        # 使用 openid 创建或获取用户
        from services.user_service import get_user_service

        service = get_user_service()
        user = service.create_or_get_user_by_openid(openid)

        logger.info(f"✅ 微信登录成功: openid={openid[:8]}... user_id={user['user_id']}")

        return jsonify({
            'success': True,
            'openid': openid,
            **user
        }), 200

    except http_requests.exceptions.Timeout:
        logger.error("❌ 调用微信接口超时")
        return jsonify({
            'success': False,
            'error': '微信服务超时，请重试',
            'code': 'WECHAT_TIMEOUT'
        }), 504

    except Exception as e:
        logger.error(f"登录失败: {e}")
        return jsonify({
            'success': False,
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
