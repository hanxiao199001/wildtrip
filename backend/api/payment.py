"""
支付API路由
小程序支付 + Web H5支付
"""

from flask import Blueprint, request, jsonify, current_app
from loguru import logger
import time
import uuid
from models import OrderStatus
from services.order_service import OrderService

payment_bp = Blueprint('payment', __name__)


@payment_bp.route('/create_order', methods=['POST'])
def create_order():
    """
    创建支付订单(小程序)
    
    请求:
    {
        "openid": "用户openid",
        "guide_id": "攻略ID/任务ID",
        "amount": 4.9
    }
    
    响应:
    {
        "success": true,
        "order_id": "WT1234567890",
        "pay_params": {
            "appId": "xxx",
            "timeStamp": "xxx",
            "nonceStr": "xxx",
            "package": "prepay_id=xxx",
            "signType": "MD5",
            "paySign": "xxx"
        }
    }
    """
    try:
        data = request.json
        openid = data.get('openid')
        guide_id = data.get('guide_id')
        amount = data.get('amount', 4.9)
        
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
        
        # 金额转换为分
        total_fee = int(amount * 100)
        
        # 商品描述
        description = f"野游记个性化攻略"
        
        # 创建订单
        order = OrderService.create_order(
            openid=openid,
            product_type='guide',
            product_name=description,
            amount=total_fee,
            client_ip=request.headers.get('X-Real-IP', request.remote_addr),
            user_agent=request.headers.get('User-Agent')
        )
        
        order_id = order.order_no
        
        # 调用微信支付
        from services.wechat_payment import get_payment_service
        payment = get_payment_service()
        
        pay_params = payment.create_order(
            user_openid=openid,
            order_id=order_id,
            total_fee=total_fee,
            description=description
        )
        
        # 保存预支付ID
        order.prepay_id = pay_params.get('package', '').replace('prepay_id=', '')
        from models import db
        db.session.commit()
        
        logger.info(f"✅ 订单创建成功: {order_id} | 攻略: {guide_id} | 金额: ¥{amount}")
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'amount': amount,
            'pay_params': pay_params
        })
        
    except Exception as e:
        logger.error(f"❌ 创建订单失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@payment_bp.route('/create_h5_order', methods=['POST'])
def create_h5_order():
    """
    创建H5支付订单(Web端)
    
    请求:
    {
        "guide_id": "攻略ID/任务ID",
        "amount": 4.9
    }
    
    响应:
    {
        "success": true,
        "order_id": "WT1234567890",
        "payment_url": "https://wx.tenpay.com/cgi-bin/mmpayweb-bin/checkmweb?prepay_id=xxx"
    }
    """
    try:
        data = request.json
        guide_id = data.get('guide_id')
        amount = data.get('amount', 4.9)
        
        if not guide_id:
            return jsonify({
                'success': False,
                'error': '缺少guide_id'
            }), 400
        
        # 金额转换为分
        total_fee = int(amount * 100)
        
        # 获取客户端IP
        client_ip = request.headers.get('X-Real-IP', request.remote_addr)
        
        # 商品描述
        description = f"野游记个性化攻略"
        
        # 创建订单 (H5支付没有openid)
        order = OrderService.create_order(
            openid='h5_user',  # H5支付用临时标识
            product_type='guide',
            product_name=description,
            amount=total_fee,
            client_ip=client_ip,
            user_agent=request.headers.get('User-Agent')
        )
        
        order_id = order.order_no
        
        # 调用微信支付
        from services.wechat_payment import get_payment_service
        payment = get_payment_service()
        
        payment_url = payment.create_h5_order(
            order_id=order_id,
            total_fee=total_fee,
            description=description,
            client_ip=client_ip
        )
        
        # 添加回跳URL
        redirect_url = f"https://wildtrip.com.cn/payment/result?order_id={order_id}"
        payment_url += f"&redirect_url={redirect_url}"
        
        logger.info(f"✅ H5订单创建成功: {order_id} | 攻略: {guide_id} | 金额: ¥{amount}")
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'amount': amount,
            'payment_url': payment_url
        })
        
    except Exception as e:
        logger.error(f"❌ 创建H5订单失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@payment_bp.route('/notify', methods=['POST'])
def payment_notify():
    """
    支付回调接口
    微信支付成功后会POST XML数据到这个地址
    
    ⚠️ 重要: 
    1. 必须验证签名
    2. 必须返回正确的XML格式
    3. 订单状态更新要幂等(防止重复通知)
    """
    xml_data = request.data.decode('utf-8')
    
    logger.info(f"📥 收到支付回调")
    
    try:
        from services.wechat_payment import get_payment_service
        payment = get_payment_service()
        
        # 验证签名并解析数据
        data = payment.verify_notify(xml_data)
        
        # 检查支付结果
        if data.get('return_code') == 'SUCCESS' and data.get('result_code') == 'SUCCESS':
            order_id = data['out_trade_no']
            transaction_id = data['transaction_id']
            total_fee = int(data['total_fee'])
            
            logger.success(f"✅ 支付成功: {order_id} | 微信订单号: {transaction_id} | 金额: ¥{total_fee/100}")
            
            # 更新订单状态
            OrderService.update_order_status(
                order_no=order_id,
                status=OrderStatus.PAID,
                transaction_id=transaction_id,
                remark='微信支付成功'
            )
            
            # 查询订单详情
            order = OrderService.get_order(order_id)
            
            # 如果是攻略解锁订单,记录日志
            if order and order.product_type.startswith('guide_'):
                try:
                    # 从remark提取guide_id
                    guide_id = None
                    if order.remark and 'guide_id:' in order.remark:
                        guide_id = order.remark.split('guide_id:')[1].strip()
                    
                    logger.success(f"🎉 攻略已解锁: {order.openid} | guide_id: {guide_id} | {order.product_name}")
                    
                    # TODO: 发送订阅消息通知用户
                    # send_unlock_notification(order.openid, guide_id)
                    
                except Exception as e:
                    logger.error(f"❌ 解锁攻略失败: {e}")
            
            # TODO: 发送支付成功通知
            # send_payment_notification(order_id)
            
            # 返回成功
            return '''<xml>
  <return_code><![CDATA[SUCCESS]]></return_code>
  <return_msg><![CDATA[OK]]></return_msg>
</xml>''', 200, {'Content-Type': 'application/xml'}
        
        else:
            logger.warning(f"⚠️  支付失败: {data.get('err_code_des', '未知原因')}")
            
    except Exception as e:
        logger.error(f"❌ 支付回调处理失败: {e}")
    
    # 返回失败
    return '''<xml>
  <return_code><![CDATA[FAIL]]></return_code>
  <return_msg><![CDATA[处理失败]]></return_msg>
</xml>''', 200, {'Content-Type': 'application/xml'}


@payment_bp.route('/query_order', methods=['GET'])
def query_order():
    """
    查询订单状态
    
    参数:
    ?order_id=WT1234567890
    
    响应:
    {
        "success": true,
        "order": {
            "order_id": "WT1234567890",
            "status": "paid",
            "amount": 4.9,
            "paid_at": "2026-02-25 00:00:00"
        }
    }
    """
    order_id = request.args.get('order_id')
    
    if not order_id:
        return jsonify({
            'success': False,
            'error': '缺少order_id'
        }), 400
    
    # 从数据库查询订单
    order = OrderService.get_order(order_id)
    
    if not order:
        return jsonify({
            'success': False,
            'error': '订单不存在'
        }), 404
    
    return jsonify({
        'success': True,
        'order': order.to_dict()
    })


@payment_bp.route('/my_orders', methods=['GET'])
def my_orders():
    """
    获取我的订单列表
    
    参数:
    ?openid=xxx&limit=20
    
    响应:
    {
        "success": true,
        "orders": [...]
    }
    """
    openid = request.args.get('openid')
    limit = int(request.args.get('limit', 20))
    
    if not openid:
        return jsonify({
            'success': False,
            'error': '缺少openid'
        }), 400
    
    orders = OrderService.get_user_orders(openid, limit=limit)
    
    return jsonify({
        'success': True,
        'orders': [order.to_dict() for order in orders],
        'total': len(orders)
    })


@payment_bp.route('/cancel_order', methods=['POST'])
def cancel_order():
    """
    取消订单
    
    请求:
    {
        "order_id": "WT1234567890"
    }
    """
    data = request.json
    order_id = data.get('order_id')
    
    if not order_id:
        return jsonify({
            'success': False,
            'error': '缺少order_id'
        }), 400
    
    order = OrderService.get_order(order_id)
    
    if not order:
        return jsonify({
            'success': False,
            'error': '订单不存在'
        }), 404
    
    # 只能取消待支付订单
    if order.status != OrderStatus.PENDING.value:
        return jsonify({
            'success': False,
            'error': f'订单状态为{order.status},无法取消'
        }), 400
    
    success = OrderService.update_order_status(
        order_no=order_id,
        status=OrderStatus.CANCELLED,
        remark='用户主动取消'
    )
    
    if success:
        logger.info(f"✅ 订单已取消: {order_id}")
        return jsonify({
            'success': True,
            'message': '订单已取消'
        })
    else:
        return jsonify({
            'success': False,
            'error': '取消失败'
        }), 500


@payment_bp.route('/stats', methods=['GET'])
def payment_stats():
    """
    订单统计 (管理员)
    
    参数:
    ?start_date=2026-02-01&end_date=2026-02-28
    
    响应:
    {
        "success": true,
        "stats": {
            "total": 100,
            "paid": 80,
            "amount": 392000,
            "pending": 15
        }
    }
    """
    from datetime import datetime
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    stats = OrderService.get_stats(start_date, end_date)
    
    return jsonify({
        'success': True,
        'stats': stats
    })
