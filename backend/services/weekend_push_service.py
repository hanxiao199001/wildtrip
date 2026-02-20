"""
周末计划推送服务
"""

import os
import requests
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger


class WeekendPushService:
    """周末计划推送服务"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.appid = os.getenv('WECHAT_APPID')
        self.secret = os.getenv('WECHAT_SECRET')
        self.template_id = os.getenv('WECHAT_SUBSCRIBE_TEMPLATE_WEEKEND')
        self.access_token = None
        self.token_expires_at = 0
    
    def start(self):
        """启动定时任务"""
        # 🔥 每周四晚 8 点推送
        self.scheduler.add_job(
            func=self.push_weekend_plans,
            trigger=CronTrigger(day_of_week='thu', hour=20, minute=0),
            id='weekend_push',
            name='周末计划推送',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("✅ 周末推送定时任务已启动(每周四 20:00)")
    
    def stop(self):
        """停止定时任务"""
        self.scheduler.shutdown()
        logger.info("❌ 周末推送定时任务已停止")
    
    def get_access_token(self) -> str:
        """
        获取微信 access_token
        
        自动缓存,过期前 5 分钟刷新
        """
        now = datetime.now().timestamp()
        
        # 如果 token 还有效,直接返回
        if self.access_token and now < self.token_expires_at - 300:
            return self.access_token
        
        # 重新获取
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            'grant_type': 'client_credential',
            'appid': self.appid,
            'secret': self.secret
        }
        
        response = requests.get(url, params=params, timeout=10)
        result = response.json()
        
        if 'access_token' in result:
            self.access_token = result['access_token']
            self.token_expires_at = now + result['expires_in']  # 通常 7200 秒
            logger.info("✅ 获取 access_token 成功")
            return self.access_token
        else:
            raise Exception(f"获取 access_token 失败: {result}")
    
    def push_weekend_plans(self):
        """
        推送周末计划给所有订阅用户
        """
        logger.info("=" * 60)
        logger.info("🚀 开始推送周末计划...")
        logger.info(f"⏰ 时间: {datetime.now()}")
        
        # 1. 获取所有订阅用户
        from api.subscription import get_all_subscribed_users
        users = get_all_subscribed_users()
        
        logger.info(f"📊 订阅用户数: {len(users)}")
        
        if len(users) == 0:
            logger.warning("⚠️ 没有订阅用户,跳过推送")
            return
        
        # 2. 为每个用户生成个性化推荐并推送
        success_count = 0
        fail_count = 0
        
        for user_data in users:
            try:
                openid = user_data['openid']
                self.push_to_user(openid)
                success_count += 1
                
            except Exception as e:
                logger.error(f"❌ 推送失败 {user_data['openid']}: {e}")
                fail_count += 1
        
        logger.info("=" * 60)
        logger.info(f"✅ 推送完成! 成功:{success_count} 失败:{fail_count}")
        logger.info("=" * 60)
    
    def push_to_user(self, openid: str):
        """
        推送给单个用户
        
        Args:
            openid: 用户的 openid
        """
        # 1. 生成个性化推荐
        recommendation = self.generate_recommendation(openid)
        
        # 2. 发送订阅消息
        self.send_subscribe_message(
            openid=openid,
            recommendation=recommendation
        )
        
        # 3. 更新推送记录
        self.update_push_record(openid)
        
        logger.info(f"✅ 推送成功: {openid} → {recommendation['destination']}")
    
    def generate_recommendation(self, openid: str) -> dict:
        """
        生成个性化推荐
        
        🔥 这里接入之前的 Multi-Agent 系统
        """
        # TODO: 接入 Agent 系统
        # from core.agent_orchestrator import create_trip_orchestrator
        # from core.trip_state import TripState
        
        # 这里先返回模拟数据
        return {
            'id': f"weekend_{datetime.now().strftime('%Y%m%d')}",
            'destination': '万宁神州半岛',
            'date': '2024-02-24',
            'highlight': '避开人群,亲子玩水,适合航拍',
            'tip': '记得带遥控积木和防晒霜',
            'page_path': 'pages/weekend-detail/weekend-detail?id=test001'
        }
    
    def send_subscribe_message(self, openid: str, recommendation: dict):
        """
        发送订阅消息
        
        Args:
            openid: 用户 openid
            recommendation: 推荐内容
        """
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}"
        
        # 构建消息数据
        data = {
            "touser": openid,
            "template_id": self.template_id,
            "page": recommendation['page_path'],
            "data": {
                "thing1": {
                    "value": recommendation['destination'][:20]  # 限制 20 字
                },
                "date2": {
                    "value": recommendation['date']
                },
                "thing3": {
                    "value": recommendation['highlight'][:20]
                },
                "thing4": {
                    "value": recommendation['tip'][:20]
                }
            },
            "miniprogram_state": "formal"  # formal | trial | developer
        }
        
        # 发送请求
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        # 检查结果
        if result.get('errcode') == 0:
            logger.debug(f"✅ 消息发送成功: {openid}")
        else:
            raise Exception(f"微信接口错误 {result.get('errcode')}: {result.get('errmsg')}")
    
    def update_push_record(self, openid: str):
        """更新推送记录"""
        from api.subscription import subscriptions
        
        if openid in subscriptions:
            subscriptions[openid]['last_push_at'] = datetime.now().isoformat()
            subscriptions[openid]['push_count'] = subscriptions[openid].get('push_count', 0) + 1


# 🔥 手动触发推送(测试用)
def manual_push_test(openid: str):
    """
    手动触发推送测试
    
    Usage:
        from services.weekend_push_service import manual_push_test
        manual_push_test('oXXXXXXXXXXXXXXX')
    """
    service = WeekendPushService()
    service.push_to_user(openid)
    logger.info("✅ 测试推送完成")


# 单例
_service = None

def get_weekend_push_service() -> WeekendPushService:
    """获取推送服务实例"""
    global _service
    if _service is None:
        _service = WeekendPushService()
    return _service
