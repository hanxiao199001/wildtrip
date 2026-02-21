"""
点击追踪 API
记录用户点击 affiliate 链接的数据
"""

import json
import os
from datetime import datetime
from pathlib import Path
from flask import Blueprint, request, jsonify
from loguru import logger

# 创建 Blueprint
track_bp = Blueprint('track', __name__)

# 数据存储目录
TRACK_DATA_DIR = Path(__file__).parent.parent.parent / 'data' / 'clicks'
TRACK_DATA_DIR.mkdir(parents=True, exist_ok=True)


@track_bp.route('/api/track/click', methods=['POST', 'OPTIONS'])
def track_click():
    """
    记录 affiliate 链接点击
    
    请求格式：
    {
        "page": "/guides/haikou-3day.html",
        "poi_name": "柚庐民宿",
        "poi_type": "hotel",
        "url": "https://i.meituan.com/...",
        "timestamp": 1708491234567
    }
    """
    # 处理 CORS 预检请求
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    try:
        # 解析请求数据
        if request.content_type == 'application/json':
            data = request.json
        else:
            # 支持 sendBeacon 的 text/plain
            data = json.loads(request.data.decode('utf-8'))
        
        # 添加服务器时间戳
        data['server_timestamp'] = datetime.now().isoformat()
        data['user_agent'] = request.headers.get('User-Agent', '')
        data['referrer'] = request.headers.get('Referer', '')
        data['ip'] = request.headers.get('X-Real-IP', request.remote_addr)
        
        # 保存到 JSONL 文件（按日期分文件）
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = TRACK_DATA_DIR / f'{today}.jsonl'
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
        
        logger.info(f"🔗 点击追踪 | {data.get('poi_type')} | {data.get('poi_name')} | {data.get('page')}")
        
        response = jsonify({'ok': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        logger.error(f"❌ 点击追踪失败: {e}")
        response = jsonify({'ok': False, 'error': str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500


@track_bp.route('/api/track/stats', methods=['GET'])
def track_stats():
    """
    查看点击统计
    
    查询参数：
    - date: 日期（YYYY-MM-DD），默认今天
    - page: 页面路径（可选）
    """
    try:
        # 获取日期
        date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        page_filter = request.args.get('page')
        
        log_file = TRACK_DATA_DIR / f'{date_str}.jsonl'
        
        if not log_file.exists():
            return jsonify({
                'date': date_str,
                'total_clicks': 0,
                'clicks': []
            })
        
        # 读取数据
        clicks = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    click = json.loads(line)
                    if page_filter and click.get('page') != page_filter:
                        continue
                    clicks.append(click)
        
        # 统计
        stats = {
            'date': date_str,
            'total_clicks': len(clicks),
            'by_type': {},
            'by_page': {},
            'top_pois': {},
            'clicks': clicks[-100:]  # 只返回最近 100 条
        }
        
        # 按类型统计
        for click in clicks:
            poi_type = click.get('poi_type', 'unknown')
            stats['by_type'][poi_type] = stats['by_type'].get(poi_type, 0) + 1
            
            # 按页面统计
            page = click.get('page', 'unknown')
            stats['by_page'][page] = stats['by_page'].get(page, 0) + 1
            
            # 按 POI 统计
            poi_name = click.get('poi_name', 'unknown')
            stats['top_pois'][poi_name] = stats['top_pois'].get(poi_name, 0) + 1
        
        # 排序
        stats['top_pois'] = dict(sorted(stats['top_pois'].items(), key=lambda x: x[1], reverse=True)[:20])
        stats['by_page'] = dict(sorted(stats['by_page'].items(), key=lambda x: x[1], reverse=True)[:20])
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"❌ 统计查询失败: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@track_bp.route('/api/track/dashboard', methods=['GET'])
def track_dashboard():
    """
    简单的统计面板（HTML）
    """
    try:
        # 获取最近 7 天的数据
        stats_by_date = {}
        
        for i in range(7):
            date = datetime.now().date()
            from datetime import timedelta
            date = date - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            log_file = TRACK_DATA_DIR / f'{date_str}.jsonl'
            
            if log_file.exists():
                count = 0
                with open(log_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            count += 1
                stats_by_date[date_str] = count
            else:
                stats_by_date[date_str] = 0
        
        # 生成 HTML
        html = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>点击追踪 - 野游记</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            margin-bottom: 8px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 16px;
            margin-top: 20px;
        }}
        .stat-box {{
            background: linear-gradient(135deg, #4CAF50, #43A047);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 4px;
        }}
        .stat-label {{
            font-size: 14px;
            opacity: 0.9;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        th {{
            background: #f5f5f5;
            font-weight: 600;
        }}
        .refresh-btn {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
        }}
        .refresh-btn:hover {{
            background: #43A047;
        }}
    </style>
</head>
<body>
    <div class="card">
        <h1>📊 点击追踪统计</h1>
        <p style="color: #666;">野游记 Affiliate 链接点击数据</p>
        <button class="refresh-btn" onclick="location.reload()">🔄 刷新数据</button>
        
        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-value">{stats_by_date.get(datetime.now().strftime('%Y-%m-%d'), 0)}</div>
                <div class="stat-label">今日点击</div>
            </div>
            <div class="stat-box" style="background: linear-gradient(135deg, #FF9500, #FF8000);">
                <div class="stat-value">{sum(stats_by_date.values())}</div>
                <div class="stat-label">7日总计</div>
            </div>
            <div class="stat-box" style="background: linear-gradient(135deg, #2196F3, #1976D2);">
                <div class="stat-value">{round(sum(stats_by_date.values()) / 7, 1)}</div>
                <div class="stat-label">日均点击</div>
            </div>
        </div>
    </div>
    
    <div class="card">
        <h2>📅 最近 7 天趋势</h2>
        <table>
            <thead>
                <tr>
                    <th>日期</th>
                    <th>点击次数</th>
                </tr>
            </thead>
            <tbody>
                {"".join([f'<tr><td>{date}</td><td>{count}</td></tr>' for date, count in sorted(stats_by_date.items(), reverse=True)])}
            </tbody>
        </table>
    </div>
    
    <div class="card">
        <h2>🔗 查看详细数据</h2>
        <p>使用 API 查询：</p>
        <ul>
            <li><a href="/api/track/stats?date={datetime.now().strftime('%Y-%m-%d')}" target="_blank">今日统计（JSON）</a></li>
            <li><a href="/api/track/stats?date={datetime.now().strftime('%Y-%m-%d')}&page=/guides/haikou-3day.html" target="_blank">按页面过滤示例</a></li>
        </ul>
    </div>
</body>
</html>
'''
        
        return html
        
    except Exception as e:
        logger.error(f"❌ 面板生成失败: {e}")
        return f"<h1>错误</h1><p>{e}</p>", 500


# 导出 Blueprint
__all__ = ['track_bp']
