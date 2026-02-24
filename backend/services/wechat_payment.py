"""
微信支付服务
支持小程序支付(JSAPI)和H5支付
"""

import hashlib
import time
import requests
import uuid
from typing import Dict, Optional
from loguru import logger
import xml.etree.ElementTree as ET
import os


class WechatPayment:
    """微信支付服务"""
    
    def __init__(self):
        # 从环境变量读取配置
        self.appid = os.getenv('WECHAT_APPID', '')
        self.mchid = os.getenv('WECHAT_MCHID', '')  # 商户号审核通过后填写
        self.api_key = os.getenv('WECHAT_API_KEY', '')  # 商户号审核通过后设置
        self.notify_url = os.getenv('PAYMENT_NOTIFY_URL', 'https://api.wildtrip.com.cn/api/payment/notify')
        
        # 是否使用沙箱环境
        self.use_sandbox = os.getenv('PAYMENT_SANDBOX', 'true').lower() == 'true'
        
        if self.use_sandbox:
            logger.warning("⚠️  使用微信支付沙箱环境(仅供测试)")
        
        logger.info(f"✅ 微信支付服务初始化 | 沙箱: {self.use_sandbox}")
    
    def create_order(self, user_openid: str, order_id: str, 
                     total_fee: int, description: str) -> Dict:
        """
        创建支付订单(小程序JSAPI)
        
        Args:
            user_openid: 用户的openid
            order_id: 订单号(自己生成,唯一)
            total_fee: 金额(分),例如4.9元 = 490分
            description: 商品描述
        
        Returns:
            {
                'appId': 'xxx',
                'timeStamp': 'xxx',
                'nonceStr': 'xxx',
                'package': 'prepay_id=xxx',
                'signType': 'MD5',
                'paySign': 'xxx'
            }
        """
        logger.info(f"创建支付订单: {order_id} | 金额: ¥{total_fee/100} | 用户: {user_openid[:10]}...")
        
        # 构建请求参数
        params = {
            'appid': self.appid,
            'mch_id': self.mchid,
            'nonce_str': self._generate_nonce_str(),
            'body': description,
            'out_trade_no': order_id,
            'total_fee': str(total_fee),
            'spbill_create_ip': '127.0.0.1',
            'notify_url': self.notify_url,
            'trade_type': 'JSAPI',
            'openid': user_openid
        }
        
        # 生成签名
        params['sign'] = self._generate_sign(params)
        
        # 转换为XML
        xml_data = self._dict_to_xml(params)
        
        # 调用微信统一下单API
        url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
        if self.use_sandbox:
            url = 'https://api.mch.weixin.qq.com/sandboxnew/pay/unifiedorder'
        
        response = requests.post(
            url,
            data=xml_data.encode('utf-8'),
            headers={'Content-Type': 'application/xml'},
            timeout=10
        )
        
        # 解析返回
        result = self._xml_to_dict(response.text)
        
        if result.get('return_code') != 'SUCCESS':
            error_msg = result.get('return_msg', '未知错误')
            logger.error(f"❌ 微信支付统一下单失败: {error_msg}")
            raise Exception(f"微信支付失败: {error_msg}")
        
        if result.get('result_code') != 'SUCCESS':
            error_msg = result.get('err_code_des', result.get('err_code', '未知错误'))
            logger.error(f"❌ 微信支付业务失败: {error_msg}")
            raise Exception(f"支付失败: {error_msg}")
        
        # 返回小程序需要的支付参数
        prepay_id = result['prepay_id']
        pay_params = self._build_pay_params(prepay_id)
        
        logger.success(f"✅ 支付订单创建成功: {order_id}")
        return pay_params
    
    def create_h5_order(self, order_id: str, total_fee: int, 
                       description: str, client_ip: str) -> str:
        """
        创建H5支付订单
        
        Args:
            order_id: 订单号
            total_fee: 金额(分)
            description: 商品描述
            client_ip: 用户IP地址
        
        Returns:
            mweb_url: 支付跳转链接
        """
        logger.info(f"创建H5支付订单: {order_id} | 金额: ¥{total_fee/100}")
        
        params = {
            'appid': self.appid,
            'mch_id': self.mchid,
            'nonce_str': self._generate_nonce_str(),
            'body': description,
            'out_trade_no': order_id,
            'total_fee': str(total_fee),
            'spbill_create_ip': client_ip,
            'notify_url': self.notify_url,
            'trade_type': 'MWEB',
            'scene_info': '{"h5_info": {"type":"Wap","wap_url": "https://wildtrip.com.cn","wap_name": "野游记"}}'
        }
        
        params['sign'] = self._generate_sign(params)
        xml_data = self._dict_to_xml(params)
        
        url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
        if self.use_sandbox:
            url = 'https://api.mch.weixin.qq.com/sandboxnew/pay/unifiedorder'
        
        response = requests.post(
            url,
            data=xml_data.encode('utf-8'),
            headers={'Content-Type': 'application/xml'},
            timeout=10
        )
        
        result = self._xml_to_dict(response.text)
        
        if result.get('return_code') != 'SUCCESS':
            raise Exception(f"创建订单失败: {result.get('return_msg')}")
        
        if result.get('result_code') != 'SUCCESS':
            raise Exception(f"支付失败: {result.get('err_code_des', result.get('err_code'))}")
        
        mweb_url = result['mweb_url']
        logger.success(f"✅ H5支付订单创建成功: {order_id}")
        
        return mweb_url
    
    def verify_notify(self, xml_data: str) -> Dict:
        """
        验证支付回调
        
        Args:
            xml_data: 微信发来的XML数据
        
        Returns:
            解析后的数据字典
        """
        data = self._xml_to_dict(xml_data)
        
        # 验证签名
        sign = data.pop('sign', '')
        calculated_sign = self._generate_sign(data)
        
        if sign != calculated_sign:
            logger.error(f"❌ 支付回调签名验证失败")
            raise Exception("签名验证失败")
        
        logger.success(f"✅ 支付回调签名验证成功: {data.get('out_trade_no')}")
        return data
    
    def _build_pay_params(self, prepay_id: str) -> Dict:
        """构建小程序支付参数"""
        timestamp = str(int(time.time()))
        nonce_str = self._generate_nonce_str()
        
        params = {
            'appId': self.appid,
            'timeStamp': timestamp,
            'nonceStr': nonce_str,
            'package': f'prepay_id={prepay_id}',
            'signType': 'MD5'
        }
        
        # 生成paySign
        params['paySign'] = self._generate_sign(params)
        
        return params
    
    def _generate_sign(self, params: Dict) -> str:
        """生成签名"""
        # 排序参数(过滤空值)
        sorted_params = sorted([(k, v) for k, v in params.items() if v])
        
        # 拼接字符串
        string = '&'.join([f'{k}={v}' for k, v in sorted_params])
        string += f'&key={self.api_key}'
        
        # MD5加密
        return hashlib.md5(string.encode('utf-8')).hexdigest().upper()
    
    def _generate_nonce_str(self) -> str:
        """生成随机字符串"""
        return uuid.uuid4().hex
    
    def _dict_to_xml(self, data: Dict) -> str:
        """字典转XML"""
        xml = ['<xml>']
        for k, v in data.items():
            xml.append(f'<{k}><![CDATA[{v}]]></{k}>')
        xml.append('</xml>')
        return ''.join(xml)
    
    def _xml_to_dict(self, xml_str: str) -> Dict:
        """XML转字典"""
        root = ET.fromstring(xml_str)
        return {child.tag: child.text for child in root}


# 单例模式
_payment_service = None

def get_payment_service() -> WechatPayment:
    """获取支付服务实例"""
    global _payment_service
    if _payment_service is None:
        _payment_service = WechatPayment()
    return _payment_service


if __name__ == '__main__':
    # 测试代码
    payment = get_payment_service()
    print(f"沙箱模式: {payment.use_sandbox}")
    print(f"AppID: {payment.appid}")
    print(f"商户号: {payment.mchid}")
