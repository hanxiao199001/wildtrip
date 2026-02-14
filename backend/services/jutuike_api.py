"""
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
        if not self.enabled:
            return None

        try:
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


def get_jutuike_api() -> JutuikeAPI:
    """获取聚推客API实例（单例）"""
    global _instance
    if _instance is None:
        _instance = JutuikeAPI()
    return _instance


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
