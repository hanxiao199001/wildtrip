"""
攻略解锁支付API
单篇攻略解锁,无会员制度
"""

from flask import Blueprint, request, jsonify
from loguru import logger
from models import OrderStatus
from services.order_service import OrderService

vip_bp = Blueprint('vip', __name__)

# 攻略商品配置
GUIDE_PRODUCTS = {
    'guide_travel': {
        'name': '旅行攻略解锁',
        'amount': 480,  # 4.8元
        'type': 'travel'
    },
    'guide_history': {
        'name': '人文历史路线解锁',
        'amount': 980,  # 9.8元
        'type': 'history'
    }
}


@vip_bp.route('/products', methods=['GET'])
def get_guide_products():
    """
    获取攻略商品列表
    
    响应:
    {
        "success": true,
        "products": [
            {
                "id": "guide_travel",
                "name": "旅行攻略解锁",
                "amount": 480,
                "price": "4.80",
                "type": "travel"
            },
            ...
        ]
    }
    """
    products = []
    for product_id, info in GUIDE_PRODUCTS.items():
        products.append({
            'id': product_id,
            'name': info['name'],
            'amount': info['amount'],
            'price': f"{info['amount']/100:.2f}",
            'type': info['type']
        })
    
    return jsonify({
        'success': True,
        'products': products
    })


@vip_bp.route('/create_order', methods=['POST'])
def create_guide_order():
    """
    创建攻略解锁订单
    
    请求:
    {
        "openid": "用户openid",
        "product_id": "guide_travel",
        "guide_id": "攻略ID"
    }
    
    响应:
    {
        "success": true,
        "order": {...},
        "pay_params": {...}
    }
    """
    try:
        data = request.json
        openid = data.get('openid')
        product_id = data.get('product_id')
        guide_id = data.get('guide_id')  # 攻略ID
        
        if not openid:
            return jsonify({
                'success': False,
                'error': '缺少openid'
            }), 400
        
        if not product_id or product_id not in GUIDE_PRODUCTS:
            return jsonify({
                'success': False,
                'error': f'无效的商品ID: {product_id}'
            }), 400
        
        if not guide_id:
            return jsonify({
                'success': False,
                'error': '缺少guide_id'
            }), 400
        
        # 获取商品信息
        product = GUIDE_PRODUCTS[product_id]
        
        # 创建订单 (product_name包含guide_id方便后续解锁)
        order = OrderService.create_order(
            openid=openid,
            product_type=product_id,
            product_name=f"{product['name']} - {guide_id}",
            amount=product['amount'],
            client_ip=request.headers.get('X-Real-IP', request.remote_addr),
            user_agent=request.headers.get('User-Agent'),
            remark=f"guide_id:{guide_id}"  # 记录攻略ID
        )
        
        # 调用微信支付
        from services.wechat_payment import get_payment_service
        payment = get_payment_service()
        
        pay_params = payment.create_order(
            user_openid=openid,
            order_id=order.order_no,
            total_fee=order.amount,
            description=order.product_name
        )
        
        # 保存预支付ID
        order.prepay_id = pay_params.get('package', '').replace('prepay_id=', '')
        from models import db
        db.session.commit()
        
        logger.success(f"✅ 攻略解锁订单创建成功: {order.order_no} | {guide_id} | {product['name']} | ¥{product['amount']/100}")
        
        return jsonify({
            'success': True,
            'order': order.to_dict(),
            'pay_params': pay_params,
            'guide_id': guide_id
        })
        
    except Exception as e:
        logger.error(f"❌ 创建攻略解锁订单失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vip_bp.route('/check_unlock', methods=['GET'])
def check_guide_unlock():
    """
    检查攻略是否已解锁
    
    参数:
    ?openid=xxx&guide_id=xxx
    
    响应:
    {
        "success": true,
        "unlocked": true,
        "order_no": "WT123456",
        "paid_at": "2026-02-25 00:00:00"
    }
    """
    openid = request.args.get('openid')
    guide_id = request.args.get('guide_id')
    
    if not openid:
        return jsonify({
            'success': False,
            'error': '缺少openid'
        }), 400
    
    if not guide_id:
        return jsonify({
            'success': False,
            'error': '缺少guide_id'
        }), 400
    
    # 查询该用户是否有该攻略的已支付订单
    orders = OrderService.get_user_orders(openid, limit=100)
    
    for order in orders:
        if order.status == OrderStatus.PAID.value and guide_id in (order.remark or ''):
            return jsonify({
                'success': True,
                'unlocked': True,
                'order_no': order.order_no,
                'paid_at': order.paid_at.isoformat() if order.paid_at else None,
                'amount': order.amount
            })
    
    return jsonify({
        'success': True,
        'unlocked': False
    })


@vip_bp.route('/my_unlocked', methods=['GET'])
def my_unlocked_guides():
    """
    我已解锁的攻略列表
    
    参数:
    ?openid=xxx
    
    响应:
    {
        "success": true,
        "guides": [
            {
                "guide_id": "xxx",
                "product_name": "旅行攻略解锁",
                "amount": 480,
                "paid_at": "2026-02-25 00:00:00"
            }
        ]
    }
    """
    openid = request.args.get('openid')
    
    if not openid:
        return jsonify({
            'success': False,
            'error': '缺少openid'
        }), 400
    
    # 获取所有已支付订单
    orders = OrderService.get_user_orders(openid, limit=100)
    
    guides = []
    for order in orders:
        if order.status == OrderStatus.PAID.value and order.product_type.startswith('guide_'):
            # 从remark中提取guide_id
            guide_id = None
            if order.remark and 'guide_id:' in order.remark:
                guide_id = order.remark.split('guide_id:')[1].strip()
            
            guides.append({
                'guide_id': guide_id,
                'product_name': order.product_name,
                'product_type': order.product_type,
                'amount': order.amount,
                'order_no': order.order_no,
                'paid_at': order.paid_at.isoformat() if order.paid_at else None
            })
    
    return jsonify({
        'success': True,
        'guides': guides,
        'total': len(guides)
    })
