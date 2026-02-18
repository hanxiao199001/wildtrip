"""
美团中转页 - 解决CPS追踪 + 精准落地页问题

流程:
  1. 用户点击攻略里的「去美团」按钮
  2. 打开本页面（野游记后端提供）
  3. 页面静默触发CPS追踪链接（设置美团返佣cookie）
  4. 自动跳转到美团搜索页，关键词已预填好
  5. 用户直接看到该餐厅/酒店的团购结果，一键下单
"""

from flask import Blueprint, request, make_response
from urllib.parse import quote

relay_bp = Blueprint('relay', __name__)


# 美团城市ID映射（ci参数，直接定位城市，不依赖GPS）
MEITUAN_CITY_IDS = {
    '北京': 1, '上海': 2, '广州': 3, '深圳': 4, '天津': 5,
    '杭州': 6, '南京': 7, '武汉': 8, '西安': 9, '沈阳': 10,
    '青岛': 11, '大连': 12, '苏州': 13, '重庆': 14, '成都': 15,
    '长沙': 16, '郑州': 17, '厦门': 18, '福州': 20, '济南': 21,
    '哈尔滨': 22, '昆明': 23, '合肥': 26, '南昌': 28, '南宁': 29,
    '贵阳': 30, '太原': 35, '兰州': 37, '长春': 38, '乌鲁木齐': 40,
    '宁波': 54, '无锡': 55, '温州': 57, '东莞': 58, '佛山': 59,
    '石家庄': 70, '呼和浩特': 80, '银川': 93, '西宁': 108,
    '海口': 196, '三亚': 252,
}

def get_city_id(city: str) -> int:
    """获取美团城市ID，支持模糊匹配"""
    if not city:
        return 0
    # 精确匹配
    if city in MEITUAN_CITY_IDS:
        return MEITUAN_CITY_IDS[city]
    # 模糊匹配（去掉"市"字）
    city_short = city.replace('市', '').replace('区', '')
    for name, cid in MEITUAN_CITY_IDS.items():
        if city_short in name or name in city_short:
            return cid
    return 0


# 搜索URL模板（{ci}为城市ID占位，为0时不加城市参数）
MEITUAN_SEARCH_URLS = {
    'food':   'https://i.meituan.com/search?keyword={keyword}&type=deal&ci={ci}&mt_app_version=9999',
    'hotel':  'https://i.meituan.com/hotel/search?keyword={keyword}&ci={ci}',
    'ticket': 'https://i.meituan.com/search?keyword={keyword}%20门票&type=deal&ci={ci}',
    'feizhu': 'https://h5.fliggy.com/hotel/search?q={keyword}',
}


@relay_bp.route('/relay/meituan')
def relay_meituan():
    """
    美团中转页

    参数:
      keyword: 搜索关键词（餐厅/酒店名）
      type: food | hotel | ticket（默认 food）
      city: 城市名（可选，和关键词组合搜索）
    """
    keyword = request.args.get('keyword', '').strip()
    poi_type = request.args.get('type', 'food')
    city = request.args.get('city', '').strip()

    # 获取城市ID（直接定位城市，不依赖GPS）
    city_id = get_city_id(city)

    # 关键词只用店名（城市已通过ci参数指定，搜索更精准）
    search_keyword = keyword if keyword else '团购'

    # 获取目标搜索URL
    search_url_tpl = MEITUAN_SEARCH_URLS.get(poi_type, MEITUAN_SEARCH_URLS['food'])
    if city_id:
        search_url = search_url_tpl.format(keyword=quote(search_keyword), ci=city_id)
    else:
        # 没有城市ID时退回到城市+店名拼接搜索
        fallback_keyword = f"{city} {keyword}".strip() if city else keyword
        search_url = search_url_tpl.format(keyword=quote(fallback_keyword), ci=0).replace('&ci=0', '')

    # 直跳模式：直接 302 重定向到搜索页（给小程序 webview 用）
    if request.args.get('direct') == '1':
        from flask import redirect
        return redirect(search_url, 302)

    # 获取CPS追踪链接（从聚推客API动态获取）
    cps_url = _get_cps_url(poi_type)

    # 显示名称
    display_name = keyword or '团购'
    icon = {'food': '🍜', 'hotel': '🏨', 'ticket': '🎫'}.get(poi_type, '🔗')

    html = _build_relay_html(
        cps_url=cps_url,
        search_url=search_url,
        display_name=display_name,
        icon=icon
    )

    resp = make_response(html)
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    resp.headers['Cache-Control'] = 'no-cache'
    return resp


def _get_cps_url(poi_type: str) -> str:
    """获取聚推客CPS追踪链接"""
    try:
        from services.jutuike_api import get_jutuike_api
        api = get_jutuike_api()

        if poi_type == 'feizhu':
            link = api.get_feizhu_link()
        elif poi_type == 'hotel':
            link = api.get_hotel_link()
        else:
            link = api.get_food_link()

        if link and link.get('h5'):
            return link['h5']
    except Exception:
        pass

    # 备用链接
    return 'http://dpurl.cn/8bOw5ETz'


def _build_relay_html(cps_url: str, search_url: str, display_name: str, icon: str) -> str:
    """生成中转页HTML"""
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
  <title>正在跳转...</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      display: flex; flex-direction: column; align-items: center;
      justify-content: center; min-height: 100vh;
      background: linear-gradient(135deg, #ff6b35, #f7c59f);
      font-family: -apple-system, 'PingFang SC', sans-serif;
    }}
    .card {{
      background: white; border-radius: 20px; padding: 40px 32px;
      text-align: center; box-shadow: 0 20px 60px rgba(0,0,0,0.15);
      max-width: 320px; width: 90%;
    }}
    .icon {{ font-size: 56px; margin-bottom: 16px; }}
    .title {{ font-size: 20px; font-weight: 700; color: #1a1a1a; margin-bottom: 8px; }}
    .subtitle {{ font-size: 14px; color: #888; margin-bottom: 28px; line-height: 1.5; }}
    .spinner {{
      width: 40px; height: 40px; border: 4px solid #f0f0f0;
      border-top-color: #ff6b35; border-radius: 50%;
      animation: spin 0.8s linear infinite; margin: 0 auto 20px;
    }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    .manual-btn {{
      display: inline-block; margin-top: 20px;
      padding: 12px 28px; background: #ff6b35; color: white;
      text-decoration: none; border-radius: 24px;
      font-size: 15px; font-weight: 600;
    }}
    .tip {{ font-size: 12px; color: #bbb; margin-top: 16px; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">{icon}</div>
    <div class="title">正在搜索「{display_name}」</div>
    <div class="subtitle">即将跳转到美团<br>为您找到最优惠的团购</div>
    <div class="spinner"></div>
    <a href="{search_url}" class="manual-btn">立即前往 →</a>
    <div class="tip">若未自动跳转，请点击上方按钮</div>
  </div>

  <script>
    // 步骤1：静默触发CPS追踪（设置返佣cookie）
    var cpsUrl = {repr(cps_url)};
    var searchUrl = {repr(search_url)};

    function goToSearch() {{
      window.location.href = searchUrl;
    }}

    // 用 fetch no-cors 触发CPS追踪，不等待响应直接跳转
    if (typeof fetch !== 'undefined') {{
      fetch(cpsUrl, {{ mode: 'no-cors', credentials: 'include' }})
        .catch(function() {{}});  // 忽略错误
    }} else {{
      // 降级：用Image pixel
      var img = new Image(1, 1);
      img.src = cpsUrl;
    }}

    // 步骤2：500ms后跳转搜索页（足够触发追踪请求）
    setTimeout(goToSearch, 500);
  </script>
</body>
</html>'''
