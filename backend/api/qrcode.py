"""
小程序码API - 生成真实微信小程序码
用于分享海报中的二维码
"""

from flask import Blueprint, jsonify, request, Response
from loguru import logger
import os
import time
import hashlib
import requests
from pathlib import Path

# 创建Blueprint
qrcode_bp = Blueprint('qrcode', __name__)

# 小程序码缓存目录
QRCODE_DIR = Path(__file__).parent.parent.parent / 'web' / 'qrcodes'
QRCODE_DIR.mkdir(parents=True, exist_ok=True)

# Access Token 缓存
_access_token_cache = {
    'token': '',
    'expires_at': 0
}


def _get_access_token():
    """
    获取微信小程序 access_token（带缓存）
    需要在 .env 中配置 WECHAT_APPID 和 WECHAT_SECRET
    """
    global _access_token_cache

    # 检查缓存是否有效（提前5分钟过期）
    if _access_token_cache['token'] and _access_token_cache['expires_at'] > time.time() + 300:
        return _access_token_cache['token']

    appid = os.getenv('WECHAT_APPID', '')
    secret = os.getenv('WECHAT_SECRET', '')

    if not appid or not secret:
        logger.error("❌ 未配置 WECHAT_APPID 或 WECHAT_SECRET，无法生成小程序码")
        return None

    try:
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}"
        resp = requests.get(url, timeout=10)
        data = resp.json()

        if 'access_token' in data:
            _access_token_cache['token'] = data['access_token']
            _access_token_cache['expires_at'] = time.time() + data.get('expires_in', 7200)
            logger.info(f"✅ 获取 access_token 成功，有效期 {data.get('expires_in', 7200)}s")
            return data['access_token']
        else:
            logger.error(f"❌ 获取 access_token 失败: {data}")
            return None
    except Exception as e:
        logger.error(f"❌ 请求 access_token 异常: {e}")
        return None


@qrcode_bp.route('/qrcode/generate', methods=['POST'])
def generate_qrcode():
    """
    生成微信小程序码

    请求参数:
    {
        "guide_id": "攻略slug或taskId",
        "page": "pages/result/result"  // 跳转页面
    }

    返回: PNG图片二进制数据
    """
    try:
        data = request.get_json() or {}
        guide_id = data.get('guide_id', 'demo')
        page = data.get('page', 'pages/result/result')

        # 生成缓存key
        cache_key = hashlib.md5(f"{guide_id}_{page}".encode()).hexdigest()
        cache_path = QRCODE_DIR / f"{cache_key}.png"

        # 检查缓存
        if cache_path.exists():
            logger.info(f"📱 返回缓存小程序码: {guide_id}")
            return Response(
                cache_path.read_bytes(),
                mimetype='image/png',
                headers={'Content-Type': 'image/png'}
            )

        # 获取 access_token
        access_token = _get_access_token()
        if not access_token:
            logger.warning("⚠️ 无 access_token，返回空白占位图")
            return jsonify({'error': '未配置微信凭证', 'code': 'NO_CREDENTIALS'}), 503

        # 调用微信 wxacode.getUnlimited 接口
        # 使用 scene 参数（最多32位），不限制数量
        scene = guide_id[:32] if len(guide_id) > 32 else guide_id

        url = f"https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={access_token}"
        payload = {
            "scene": scene,
            "page": page,
            "width": 430,
            "auto_color": False,
            "line_color": {"r": 255, "g": 107, "b": 53},  # 野游记主题橙色
            "is_hyaline": False
        }

        resp = requests.post(url, json=payload, timeout=15)

        # 检查返回类型
        content_type = resp.headers.get('Content-Type', '')

        if 'image' in content_type:
            # 成功返回图片
            cache_path.write_bytes(resp.content)
            logger.info(f"✅ 小程序码生成成功: {guide_id} ({len(resp.content)} bytes)")

            return Response(
                resp.content,
                mimetype='image/png',
                headers={'Content-Type': 'image/png'}
            )
        else:
            # 返回了错误JSON
            error_data = resp.json()
            logger.error(f"❌ 生成小程序码失败: {error_data}")
            return jsonify({
                'error': error_data.get('errmsg', '生成失败'),
                'code': str(error_data.get('errcode', 'UNKNOWN'))
            }), 500

    except Exception as e:
        logger.error(f"❌ 生成小程序码异常: {e}")
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500
