"""
用户API - 登录、历史记录、收藏等
"""

from flask import Blueprint, request, jsonify
from loguru import logger
import requests as http_requests
import os

user_bp = Blueprint('user', __name__)


@user_bp.route('/user/login', methods=['POST'])
def login():
    try:
        data = request.json
        code = data.get('code', '').strip() if data.get('code') else ''
        if code:
            return _wechat_code_login(code)
        phone = data.get('phone', '').strip() if data.get('phone') else ''
        nickname = data.get('nickname', '').strip() if data.get('nickname') else ''
        if not phone:
            return jsonify({'error': '请提供code或phone参数', 'code': 'MISSING_PARAMS'}), 400
        if not phone.isdigit() or len(phone) != 11:
            return jsonify({'error': '手机号格式不正确', 'code': 'INVALID_PHONE'}), 400
        from services.user_service import get_user_service
        service = get_user_service()
        user = service.create_or_get_user(phone, nickname)
        logger.info(f"用户登录(手机号): {user['user_id']}")
        return jsonify(user), 200
    except Exception as e:
        logger.error(f"登录失败: {e}")
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


def _wechat_code_login(code):
    appid = os.getenv('WECHAT_APPID', '')
    secret = os.getenv('WECHAT_SECRET', '')
    if not appid or not secret or appid.startswith('wxXXX'):
        import hashlib
        fake_openid = 'dev_' + hashlib.md5(code.encode()).hexdigest()[:16]
        logger.warning(f"微信凭据未配置，使用开发模式openid: {fake_openid}")
        return jsonify({'success': True, 'openid': fake_openid, 'mode': 'dev'}), 200
    url = 'https://api.weixin.qq.com/sns/jscode2session'
    params = {'appid': appid, 'secret': secret, 'js_code': code, 'grant_type': 'authorization_code'}
    try:
        resp = http_requests.get(url, params=params, timeout=10)
        result = resp.json()
        if 'openid' in result:
            openid = result['openid']
            logger.info(f"微信登录成功, openid: {openid[:8]}...")
            return jsonify({'success': True, 'openid': openid}), 200
        else:
            errcode = result.get('errcode', 'unknown')
            errmsg = result.get('errmsg', '未知错误')
            logger.error(f"微信登录失败: {errcode} - {errmsg}")
            return jsonify({'success': False, 'error': errmsg, 'code': str(errcode)}), 400
    except Exception as e:
        logger.error(f"调用微信接口异常: {e}")
        return jsonify({'success': False, 'error': '微信服务请求失败', 'code': 'WECHAT_API_ERROR'}), 500


@user_bp.route('/user/<user_id>/guides', methods=['GET'])
def get_user_guides(user_id):
    try:
        limit = int(request.args.get('limit', 50))
        from services.user_service import get_user_service
        service = get_user_service()
        guides = service.get_user_guides(user_id, limit)
        for guide in guides:
            if 'content' in guide:
                guide['content_preview'] = guide['content'][:200] + '...'
                del guide['content']
        logger.info(f"返回用户历史: {user_id} | {len(guides)}篇")
        return jsonify(guides), 200
    except Exception as e:
        logger.error(f"获取历史失败: {e}")
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@user_bp.route('/user/<user_id>/guides/<guide_id>', methods=['GET'])
def get_guide(user_id, guide_id):
    try:
        from services.user_service import get_user_service
        service = get_user_service()
        guide = service.get_guide_by_id(user_id, guide_id)
        if not guide:
            return jsonify({'error': '攻略不存在', 'code': 'GUIDE_NOT_FOUND'}), 404
        return jsonify(guide), 200
    except Exception as e:
        logger.error(f"获取攻略失败: {e}")
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@user_bp.route('/user/<user_id>/guides/<guide_id>', methods=['DELETE'])
def delete_guide(user_id, guide_id):
    try:
        from services.user_service import get_user_service
        service = get_user_service()
        success = service.delete_guide(user_id, guide_id)
        if not success:
            return jsonify({'error': '攻略不存在', 'code': 'GUIDE_NOT_FOUND'}), 404
        logger.info(f"删除攻略: {user_id} | {guide_id}")
        return jsonify({'success': True}), 200
    except Exception as e:
        logger.error(f"删除失败: {e}")
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@user_bp.route('/user/<user_id>/guides/<guide_id>/favorite', methods=['POST'])
def toggle_favorite(user_id, guide_id):
    try:
        from services.user_service import get_user_service
        service = get_user_service()
        favorite = service.toggle_favorite(user_id, guide_id)
        return jsonify({'favorite': favorite}), 200
    except Exception as e:
        logger.error(f"切换收藏失败: {e}")
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@user_bp.route('/user/stats', methods=['GET'])
def get_stats():
    try:
        from services.user_service import get_user_service
        service = get_user_service()
        stats = service.get_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"获取统计失败: {e}")
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500
