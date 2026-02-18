"""
聚推客联盟API封装
官网: https://pub.jutuike.com
接口文档: https://www.jutuike.com/document
"""

import os
import time
import requests
from typing import Optional, Dict
from loguru import logger


# 活动ID配置
ACT_IDS = {
    'food':   27,   # 【美食团购】全城必吃 错过馋一年！
    'hotel':  10,   # 美团酒店个性化分发页面
    'minsu':   6,   # 【民宿】民宿大促销
    'movie':  17,   # 电影票在线预定活动
    'flight': 24,   # 美团机票特惠活动
}

# 缓存（避免频繁请求）
_cache: Dict[str, Dict] = {}
_CACHE_TTL = 86400  # 24小时


class JutuikeAPI:
    """聚推客联盟API封装"""

    def __init__(self):
        self.apikey = os.getenv('JUTUIKE_API_KEY', '')
        self.api_base = 'http://api.jutuike.com'
        self.pub_id = os.getenv('JUTUIKE_PUB_ID', '451888')

        if not self.apikey:
            logger.warning("⚠️ 聚推客APIKey未配置，将使用备用推广链接")
            self.enabled = False
        else:
            logger.info(f"✅ 聚推客联盟已配置 | pub_id={self.pub_id}")
            self.enabled = True

    def get_act_link(self, act_id: int, sid: str = 'wildtrip') -> Optional[Dict]:
        """
        获取活动推广链接

        Args:
            act_id: 活动ID（见 ACT_IDS）
            sid: 自定义追踪参数（如用户ID/场景）

        Returns:
            {
                'h5': '推广短链接',
                'mp_appid': '小程序AppID',
                'mp_path': '小程序路径（含weburl）',
                'mp_username': '小程序原始ID',
                'act_name': '活动名称'
            }
        """
        cache_key = f"{act_id}"
        now = time.time()

        # 检查缓存
        if cache_key in _cache:
            cached = _cache[cache_key]
            if now - cached['ts'] < _CACHE_TTL:
                logger.debug(f"📦 命中缓存: act_id={act_id}")
                return cached['data']

        if not self.enabled:
            return None

        try:
            url = f"{self.api_base}/union/act"
            params = {
                'apikey': self.apikey,
                'sid': sid,
                'act_id': act_id,
            }
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            result = resp.json()

            if result.get('code') != 1:
                logger.warning(f"聚推客API返回错误: act_id={act_id} msg={result.get('msg')}")
                return None

            data = result.get('data', {})
            we_app = data.get('we_app_info', {}) or {}

            link_info = {
                'h5': data.get('h5') or data.get('long_h5', ''),
                'mp_appid': we_app.get('app_id', 'wxde8ac0a21135c07d'),
                'mp_path': we_app.get('page_path', ''),
                'mp_username': data.get('original_id', 'gh_870576f3c6f9'),
                'act_name': data.get('act_name', ''),
            }

            # 写入缓存
            _cache[cache_key] = {'ts': now, 'data': link_info}
            logger.info(f"✅ 聚推客链接获取成功: act_id={act_id} | {link_info['act_name']} | {link_info['h5']}")
            return link_info

        except Exception as e:
            logger.error(f"聚推客API请求失败: act_id={act_id} | {e}")
            return None

    def get_food_link(self, sid: str = 'food') -> Optional[Dict]:
        """获取美食团购推广链接"""
        return self.get_act_link(ACT_IDS['food'], sid)

    def get_hotel_link(self, sid: str = 'hotel') -> Optional[Dict]:
        """获取美团酒店推广链接"""
        return self.get_act_link(ACT_IDS['hotel'], sid)

    def get_minsu_link(self, sid: str = 'minsu') -> Optional[Dict]:
        """获取民宿推广链接"""
        return self.get_act_link(ACT_IDS['minsu'], sid)


# 单例
_instance: Optional[JutuikeAPI] = None


def get_jutuike_api() -> JutuikeAPI:
    """获取聚推客API实例（单例）"""
    global _instance
    if _instance is None:
        _instance = JutuikeAPI()
    return _instance


if __name__ == '__main__':
    # 测试
    api = JutuikeAPI()
    for name, act_id in ACT_IDS.items():
        result = api.get_act_link(act_id)
        if result:
            print(f"✅ {name}(act_id={act_id}): {result['h5']} | {result['act_name']}")
        else:
            print(f"❌ {name}(act_id={act_id}): 获取失败")
