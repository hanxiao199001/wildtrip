"""
野游记 WildTrip - 后端主应用
Flask API Server + WebSocket实时进度
"""

from flask import Flask, jsonify, send_from_directory, send_file, request
from flask_socketio import SocketIO
from flask_cors import CORS
from loguru import logger
import sys
from pathlib import Path
import os

# 🔥 加载.env配置文件（必须在最前面）
from dotenv import load_dotenv
load_dotenv()

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'wildtrip-2026-no-ordinary-path'

# CORS配置（允许小程序跨域）
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# SocketIO配置
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/wildtrip.log",
    rotation="00:00",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
    level="DEBUG"
)

# 注册API路由
from api.generate import generate_bp, register_socketio_events
from api.guides import guides_bp
from api.user import user_bp
from api.relay import relay_bp
from api.clarify import clarify_bp
from api.qrcode import qrcode_bp
from api.subscription import subscription_bp  # 🔥 新增:订阅消息
from routes.track import track_bp  # 🔥 新增:点击追踪

app.register_blueprint(generate_bp, url_prefix='/api')
app.register_blueprint(guides_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(relay_bp, url_prefix='/api')
app.register_blueprint(clarify_bp, url_prefix='/api')
app.register_blueprint(qrcode_bp, url_prefix='/api')
app.register_blueprint(subscription_bp, url_prefix='/api')  # 🔥 新增
app.register_blueprint(track_bp)  # 🔥 新增:点击追踪
register_socketio_events(socketio)

logger.info("野游记 WildTrip API已注册（生成 + 攻略列表 + 用户系统 + 需求澄清 + 小程序码 + 中转页 + 订阅消息 + 点击追踪）")

# 🔥 启动周末推送服务
try:
    from services.weekend_push_service import get_weekend_push_service
    push_service = get_weekend_push_service()
    push_service.start()
    logger.info("✅ 周末推送服务已启动(每周四 20:00)")
except Exception as e:
    logger.warning(f"⚠️ 周末推送服务启动失败(可能缺少配置): {e}")


@app.route('/')
def index():
    """首页 - 返回Web界面"""
    web_dir = Path(__file__).parent.parent / 'web'
    index_file = web_dir / 'index.html'
    
    if index_file.exists():
        return send_file(str(index_file))
    else:
        # 找不到HTML，返回API信息
        return jsonify({
            'name': '野游记 WildTrip',
            'slogan': '不走寻常路，就走野路子',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'generate': '/api/generate',
                'task': '/api/task/<task_id>',
                'health': '/api/health'
            }
        })


@app.route('/app.js')
@app.route('/analytics.html')
@app.route('/sitemap.xml')
@app.route('/robots.txt')
def serve_web_files():
    """Web静态文件"""
    web_dir = Path(__file__).parent.parent / 'web'
    filename = request.path.lstrip('/')
    return send_from_directory(str(web_dir), filename)


@app.route('/public/<path:filename>')
def serve_public(filename):
    """静态资源 - 图片等"""
    web_dir = Path(__file__).parent.parent / 'web' / 'public'
    return send_from_directory(str(web_dir), filename)


@app.route('/guides/<path:filename>')
def serve_guides(filename):
    """攻略静态页面"""
    web_dir = Path(__file__).parent.parent / 'web' / 'guides'
    return send_from_directory(str(web_dir), filename)


@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'service': 'wildtrip-backend'
    })


if __name__ == '__main__':
    import os
    
    # 创建日志目录
    Path('logs').mkdir(exist_ok=True)
    
    # 启动服务
    port = int(os.getenv('PORT', 5000))
    logger.info(f"🔥 野游记 WildTrip 启动中...")
    logger.info(f"📍 访问地址: http://0.0.0.0:{port}")
    logger.info(f"📡 WebSocket已启用")
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=False,
        allow_unsafe_werkzeug=True
    )
