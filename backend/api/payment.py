"""
支付API路由
小程序支付 + Web H5支付
"""

from flask import Blueprint, request, jsonify
from loguru import logger
import time
import uuid

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
        
        # 生成订单号
        order_id = f"WT{int(time.time())}{uuid.uuid4().hex[:8].upper()}"
        
        # 金额转换为分
        total_fee = int(amount * 100)
        
        # 商品描述
        description = f"野游记个性化攻略"
        
        # TODO: 保存订单到数据库
        # save_order(order_id, guide_id, openid, total_fee, 'pending')
        
        # 调用微信支付
        from services.wechat_payment import get_payment_service
        payment = get_payment_service()
        
        pay_params = payment.create_order(
            user_openid=openid,
            order_id=order_id,
            total_fee=total_fee,
            description=description
        )
        
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
        
        # 生成订单号
        order_id = f"WT{int(time.time())}{uuid.uuid4().hex[:8].upper()}"
        
        # 金额转换为分
        total_fee = int(amount * 100)
        
        # 获取客户端IP
        client_ip = request.headers.get('X-Real-IP', request.remote_addr)
        
        # 商品描述
        description = f"野游记个性化攻略"
        
        # TODO: 保存订单到数据库
        # save_order(order_id, guide_id, None, total_fee, 'pending')
        
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
            
            # TODO: 更新订单状态
            # update_order_status(order_id, 'paid', transaction_id)
            
            # TODO: 解锁攻略内容
            # unlock_guide_content(order_id)
            
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
    
    # TODO: 从数据库查询订单
    # order = get_order_by_id(order_id)
    
    # 临时返回模拟数据
    return jsonify({
        'success': True,
        'order': {
            'order_id': order_id,
            'status': 'pending',
            'amount': 4.9,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    })
