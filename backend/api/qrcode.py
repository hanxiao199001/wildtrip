"""
小程序码生成API
调用微信官方接口生成小程序码
"""

from flask import Blueprint, jsonify, request, send_file
from loguru import logger
import requests
import os
from pathlib import Path

qrcode_bp = Blueprint('qrcode', __name__)

# 小程序码缓存目录
QRCODE_DIR = Path(__file__).parent.parent.parent / 'web' / 'qrcodes'
QRCODE_DIR.mkdir(parents=True, exist_ok=True)

def get_access_token():
    """
    获取微信 Access Token
    
    需要在 .env 配置：
    WX_APPID=你的小程序AppID
    WX_SECRET=你的小程序AppSecret
    """
    appid = os.getenv('WX_APPID', '')
    secret = os.getenv('WX_SECRET', '')
    
    if not appid or not secret:
        logger.warning("⚠️ 微信小程序未配置，使用占位二维码")
        return None
    
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}'
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'access_token' in data:
            return data['access_token']
        else:
            logger.error(f"获取 Access Token 失败: {data}")
            return None
    except Exception as e:
        logger.error(f"获取 Access Token 异常: {e}")
        return None


@qrcode_bp.route('/qrcode/generate', methods=['POST'])
def generate_qrcode():
    """
    生成小程序码
    
    参数：
    - guide_id: 攻略ID（用于生成场景值）
    - page: 跳转页面（默认 pages/guide-detail/guide-detail）
    """
    try:
        data = request.json
        guide_id = data.get('guide_id', '')
        page = data.get('page', 'pages/guide-detail/guide-detail')
        
        # 检查缓存
        cache_file = QRCODE_DIR / f'{guide_id}.png'
        if cache_file.exists():
            logger.info(f"✅ 使用缓存二维码: {guide_id}")
            return send_file(str(cache_file), mimetype='image/png')
        
        # 获取 Access Token
        access_token = get_access_token()
        if not access_token:
            return jsonify({
                'status': 'error',
                'message': '小程序未配置，请设置 WX_APPID 和 WX_SECRET'
            }), 500
        
        # 调用微信接口生成小程序码
        url = f'https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={access_token}'
        
        payload = {
            'scene': guide_id,  # 场景值（最多32字符）
            'page': page,
            'width': 280,  # 二维码宽度
            'auto_color': False,
            'line_color': {'r': 0, 'g': 0, 'b': 0},
            'is_hyaline': False
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        # 检查是否返回图片
        if response.headers.get('Content-Type') == 'image/jpeg':
            # 保存到缓存
            with open(cache_file, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✅ 生成小程序码成功: {guide_id}")
            return send_file(str(cache_file), mimetype='image/png')
        else:
            error_data = response.json()
            logger.error(f"❌ 生成小程序码失败: {error_data}")
            return jsonify({
                'status': 'error',
                'message': f"微信接口错误: {error_data.get('errmsg', '未知错误')}"
            }), 500
    
    except Exception as e:
        logger.error(f"❌ 生成小程序码异常: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@qrcode_bp.route('/qrcode/<guide_id>.png', methods=['GET'])
def get_qrcode(guide_id):
    """获取已生成的小程序码"""
    cache_file = QRCODE_DIR / f'{guide_id}.png'
    
    if cache_file.exists():
        return send_file(str(cache_file), mimetype='image/png')
    else:
        return jsonify({'status': 'error', 'message': '二维码不存在'}), 404
