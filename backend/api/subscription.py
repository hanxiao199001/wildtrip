"""
订阅消息管理 API
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from loguru import logger
import os

subscription_bp = Blueprint('subscription', __name__)

# 简单的内存存储(生产环境应使用数据库)
# TODO: 迁移到数据库
subscriptions = {}


@subscription_bp.route('/user/subscription/sync', methods=['POST'])
def sync_subscription():
    """
    同步用户订阅状态
    
    小程序端调用,将用户的订阅状态同步到后端
    """
    try:
        data = request.json
        openid = data.get('openid')
        subscriptions_data = data.get('subscriptions')  # {'tmplId': 'accept'}
        
        if not openid:
            return jsonify({
                'success': False,
                'message': 'openid 不能为空'
            }), 400
        
        # 保存订阅状态
        subscriptions[openid] = {
            'openid': openid,
            'subscriptions': subscriptions_data,
            'subscribed_at': datetime.now().isoformat(),
            'last_push_at': None,
            'push_count': 0
        }
        
        logger.info(f"✅ 订阅状态已同步: {openid}")
        
        return jsonify({
            'success': True,
            'message': '订阅状态已更新'
        })
        
    except Exception as e:
        logger.error(f"同步订阅状态失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@subscription_bp.route('/user/subscription/status', methods=['GET'])
def get_subscription_status():
    """
    查询用户订阅状态
    """
    try:
        openid = request.args.get('openid')
        
        if not openid:
            return jsonify({
                'success': False,
                'message': 'openid 不能为空'
            }), 400
        
        # 查询订阅状态
        user_sub = subscriptions.get(openid)
        
        if user_sub:
            # 检查订阅是否有效
            template_id = os.getenv('WECHAT_SUBSCRIBE_TEMPLATE_WEEKEND')
            is_subscribed = user_sub['subscriptions'].get(template_id) == 'accept'
            
            return jsonify({
                'success': True,
                'subscribed': is_subscribed,
                'subscribed_at': user_sub.get('subscribed_at'),
                'last_push_at': user_sub.get('last_push_at'),
                'push_count': user_sub.get('push_count', 0)
            })
        else:
            return jsonify({
                'success': True,
                'subscribed': False
            })
        
    except Exception as e:
        logger.error(f"查询订阅状态失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@subscription_bp.route('/user/subscription/cancel', methods=['POST'])
def cancel_subscription():
    """
    取消订阅
    """
    try:
        data = request.json
        openid = data.get('openid')
        
        if not openid:
            return jsonify({
                'success': False,
                'message': 'openid 不能为空'
            }), 400
        
        # 删除订阅状态
        if openid in subscriptions:
            del subscriptions[openid]
            logger.info(f"✅ 已取消订阅: {openid}")
        
        return jsonify({
            'success': True,
            'message': '已取消订阅'
        })
        
    except Exception as e:
        logger.error(f"取消订阅失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@subscription_bp.route('/subscription/stats', methods=['GET'])
def get_subscription_stats():
    """
    获取订阅统计数据(管理后台用)
    """
    try:
        total = len(subscriptions)
        active = sum(1 for s in subscriptions.values() 
                    if s['subscriptions'].get(os.getenv('WECHAT_SUBSCRIBE_TEMPLATE_WEEKEND')) == 'accept')
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'active': active,
                'inactive': total - active
            },
            'recent_subscriptions': list(subscriptions.values())[-10:]  # 最近 10 条
        })
        
    except Exception as e:
        logger.error(f"获取统计数据失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


def get_all_subscribed_users():
    """
    获取所有订阅用户列表
    
    供定时推送任务调用
    """
    template_id = os.getenv('WECHAT_SUBSCRIBE_TEMPLATE_WEEKEND')
    
    active_users = [
        user_data for user_data in subscriptions.values()
        if user_data['subscriptions'].get(template_id) == 'accept'
    ]
    
    return active_users
