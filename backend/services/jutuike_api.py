"""
<<<<<<< HEAD
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
    'feizhu': 29,   # 【渠道专享红包】飞猪酒店活动
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

=======
聚推客联盟 API 对接
支持美团团购到店 CPS 转链，返回小程序跳转参数
官方文档：https://www.jutuike.com/document
"""

import requests
from loguru import logger
from typing import Optional, Dict
import os


class JutuikeAPI:
    """聚推客联盟 API 封装"""

    API_BASE = 'http://api.jutuike.com'

    def __init__(self):
        self.apikey = os.getenv('JUTUIKE_APIKEY', '')
        self.default_sid = os.getenv('JUTUIKE_SID', '123456')
        # 活动ID：36=玩乐变美(4.1%), 27=吃喝玩乐每日福利(最高15%)
        self.default_act_id = os.getenv('JUTUIKE_ACT_ID', '27')

        if not self.apikey:
            logger.warning("聚推客联盟未配置 apikey，将无法生成返佣链接")
            self.enabled = False
        else:
            logger.info(f"聚推客联盟已配置 | sid={self.default_sid} | actId={self.default_act_id}")
            self.enabled = True

    def get_activity_link(
        self,
        act_id: Optional[str] = None,
        sid: Optional[str] = None,
        link_type: int = 15
    ) -> Optional[Dict]:
        """
        获取美团活动转链（券包/团购到店）

        Args:
            act_id: 活动ID（不传则用默认）
            sid: 渠道标识（用于追踪订单归属）
            link_type: 活动类型，15=美团券包

        Returns:
            {
                'h5': 'H5链接',
                'short_h5': '短链',
                'deeplink': 'deeplink',
                'we_app_info': {
                    'app_id': '小程序AppID',
                    'page_path': '小程序路径',
                    'miniCode': '小程序码URL'
                }
            }
        """
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3
        if not self.enabled:
            return None

        try:
<<<<<<< HEAD
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

    def get_feizhu_link(self, sid: str = 'feizhu') -> Optional[Dict]:
        """获取飞猪酒店推广链接"""
        return self.get_act_link(ACT_IDS['feizhu'], sid)

    def get_minsu_link(self, sid: str = 'minsu') -> Optional[Dict]:
        """获取民宿推广链接"""
        return self.get_act_link(ACT_IDS['minsu'], sid)


# 单例
_instance: Optional[JutuikeAPI] = None
=======
            params = {
                'apikey': self.apikey,
                'type': link_type,
                'sid': sid or self.default_sid,
            }
            if act_id:
                params['actId'] = act_id

            resp = requests.get(
                f'{self.API_BASE}/Meituan/act',
                params=params,
                timeout=10
            )

            if resp.status_code == 200:
                data = resp.json()
                if data.get('code') == 1 or data.get('data'):
                    result = data.get('data', data)
                    logger.debug(f"聚推客转链成功: {result.get('short_h5', '')[:50]}")
                    return result
                else:
                    logger.warning(f"聚推客转链失败: {data}")
                    return None
            else:
                logger.warning(f"聚推客API请求失败: HTTP {resp.status_code}")
                return None

        except Exception as e:
            logger.error(f"聚推客API异常: {e}")
            return None

    def get_meituan_miniprogram_info(
        self,
        act_id: Optional[str] = None,
        sid: Optional[str] = None
    ) -> Dict:
        """
        获取美团小程序跳转信息（供小程序端使用）

        Returns:
            {
                'app_id': 'wxde8ac0a21135c07d',
                'page_path': '/index/pages/h5/h5?weburl=...',
                'h5_url': 'H5备用链接'
            }
        """
        result = self.get_activity_link(act_id=act_id, sid=sid)

        if result and result.get('we_app_info'):
            we_app = result['we_app_info']
            return {
                'app_id': we_app.get('app_id', 'wxde8ac0a21135c07d'),
                'page_path': we_app.get('page_path', ''),
                'mini_code': we_app.get('miniCode', ''),
                'h5_url': result.get('short_h5', result.get('h5', ''))
            }

        # 返回默认（静态配置的跳转参数）
        logger.warning("聚推客API未返回小程序信息，使用默认配置")
        return {
            'app_id': 'wxde8ac0a21135c07d',
            'page_path': '',
            'mini_code': '',
            'h5_url': ''
        }


# 单例
_instance = None
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3


def get_jutuike_api() -> JutuikeAPI:
    """获取聚推客API实例（单例）"""
    global _instance
    if _instance is None:
        _instance = JutuikeAPI()
    return _instance


<<<<<<< HEAD
if __name__ == '__main__':
    # 测试
    api = JutuikeAPI()
    for name, act_id in ACT_IDS.items():
        result = api.get_act_link(act_id)
        if result:
            print(f"✅ {name}(act_id={act_id}): {result['h5']} | {result['act_name']}")
        else:
            print(f"❌ {name}(act_id={act_id}): 获取失败")
=======
if __name__ == "__main__":
    api = JutuikeAPI()
    print(f"启用状态: {api.enabled}")

    if api.enabled:
        print("\n=== 测试活动转链 ===")
        link = api.get_activity_link(act_id='27')
        if link:
            print(f"H5链接: {link.get('short_h5', 'N/A')}")
            we_app = link.get('we_app_info', {})
            print(f"小程序AppID: {we_app.get('app_id', 'N/A')}")
            print(f"小程序路径: {we_app.get('page_path', 'N/A')[:80]}")

        print("\n=== 测试小程序信息 ===")
        mp_info = api.get_meituan_miniprogram_info()
        print(f"AppID: {mp_info['app_id']}")
        print(f"Path: {mp_info['page_path'][:80]}")
>>>>>>> 43391bb678dd7937350065a348a1412a963940c3
