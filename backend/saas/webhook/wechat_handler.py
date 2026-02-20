"""
微信公众号消息接收处理
"""
from flask import Flask, request, make_response
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)


def verify_wechat_signature(params):
    """
    验证微信服务器签名
    """
    signature = params.get('signature', '')
    timestamp = params.get('timestamp', '')
    nonce = params.get('nonce', '')
    echostr = params.get('echostr', '')
    
    # TODO: 从数据库读取酒店的 token
    token = "wildtrip_saas_token"  # 临时写死，后续从配置读取
    
    # 字典序排序
    tmp_list = [token, timestamp, nonce]
    tmp_list.sort()
    tmp_str = ''.join(tmp_list)
    
    # SHA1 加密
    hash_obj = hashlib.sha1(tmp_str.encode('utf-8'))
    hashcode = hash_obj.hexdigest()
    
    if hashcode == signature:
        return echostr
    else:
        return "Invalid signature"


def parse_wechat_message(xml_data):
    """
    解析微信 XML 消息
    """
    root = ET.fromstring(xml_data)
    
    msg = {
        'ToUserName': root.find('ToUserName').text,
        'FromUserName': root.find('FromUserName').text,
        'CreateTime': root.find('CreateTime').text,
        'MsgType': root.find('MsgType').text,
    }
    
    # 文本消息
    if msg['MsgType'] == 'text':
        msg['Content'] = root.find('Content').text
        msg['MsgId'] = root.find('MsgId').text
    
    # 事件消息（关注、点击菜单等）
    elif msg['MsgType'] == 'event':
        msg['Event'] = root.find('Event').text
        if msg['Event'] == 'CLICK':
            msg['EventKey'] = root.find('EventKey').text
    
    return msg


def format_wechat_reply(to_user, from_user, reply_text):
    """
    格式化微信回复消息（XML）
    """
    reply_xml = f"""<xml>
<ToUserName><![CDATA[{to_user}]]></ToUserName>
<FromUserName><![CDATA[{from_user}]]></FromUserName>
<CreateTime>{int(datetime.now().timestamp())}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{reply_text}]]></Content>
</xml>"""
    
    return reply_xml


@app.route('/wechat/callback/<hotel_id>', methods=['GET', 'POST'])
def wechat_callback(hotel_id):
    """
    微信公众号消息回调
    每个酒店有独立的 webhook URL
    
    URL示例: https://api.wildtrip.com/saas/wechat/callback/hotel_001
    """
    try:
        if request.method == 'GET':
            # 微信服务器验证
            echostr = verify_wechat_signature(request.args)
            return echostr
        
        elif request.method == 'POST':
            # 接收用户消息
            xml_data = request.data
            logger.info(f"[Hotel {hotel_id}] Received message: {xml_data}")
            
            msg = parse_wechat_message(xml_data)
            
            # 只处理文本消息
            if msg['MsgType'] != 'text':
                return "success"  # 其他类型暂不处理
            
            user_message = msg['Content']
            user_id = msg['FromUserName']
            
            # 调用对话处理（暂时先写死回复，后续接入AI）
            # TODO: 接入对话管理层
            reply_text = handle_conversation_temp(hotel_id, user_id, user_message)
            
            # 返回 XML 格式回复
            reply_xml = format_wechat_reply(
                to_user=msg['FromUserName'],
                from_user=msg['ToUserName'],
                reply_text=reply_text
            )
            
            response = make_response(reply_xml)
            response.content_type = 'application/xml'
            return response
    
    except Exception as e:
        logger.error(f"Error handling wechat message: {e}", exc_info=True)
        return "success"  # 即使出错也返回success，避免微信重试


def handle_conversation_temp(hotel_id, user_id, message):
    """
    对话处理函数（接入 AI）
    """
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    
    from saas.conversation.intent_classifier import get_intent
    from saas.conversation.context_manager import get_context_manager
    from saas.ai.hotel_qa_engine import HotelQAEngine, DEMO_HOTEL_KB
    
    try:
        # 1. 获取或创建对话上下文
        ctx_manager = get_context_manager()
        context = ctx_manager.get_or_create_context(hotel_id, user_id)
        
        # 2. 识别意图
        intent = get_intent(message)
        
        # 3. 添加用户消息到上下文
        context.add_message('user', message, intent=intent)
        
        # 4. 创建 AI 引擎
        engine = HotelQAEngine(hotel_id, "海边小筑")
        
        # 5. 生成回复
        reply = engine.answer_question(
            question=message,
            context=context.get_context_for_ai(),
            intent=intent,
            hotel_kb=DEMO_HOTEL_KB
        )
        
        # 6. 添加助手回复到上下文
        context.add_message('assistant', reply)
        
        return reply
    
    except Exception as e:
        logger.error(f"Error in conversation handling: {e}", exc_info=True)
        # 降级回复
        return "您好！我是野游记AI助手～有什么想了解的尽管问我 😊"


if __name__ == '__main__':
    # 测试环境运行
    app.run(host='0.0.0.0', port=8001, debug=True)
