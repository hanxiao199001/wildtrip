"""
野游记 WildTrip - 后端主应用
Flask API Server + WebSocket实时进度
"""

from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from loguru import logger
import sys
from pathlib import Path

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
app.register_blueprint(generate_bp, url_prefix='/api')
register_socketio_events(socketio)

logger.info("野游记 WildTrip API已注册")


@app.route('/')
def index():
    """首页"""
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
