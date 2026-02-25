#!/usr/bin/env python3
"""
初始化数据库
创建所有表结构
"""
from flask import Flask
from models import db, Order, User
from pathlib import Path
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)

# 数据库配置
DB_DIR = os.getenv('DB_DIR', '/root/clawd/wildtrip/data')
Path(DB_DIR).mkdir(parents=True, exist_ok=True)

DB_PATH = Path(DB_DIR) / 'orders.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        # 创建所有表
        db.create_all()
        print(f"✅ 数据库初始化成功!")
        print(f"📁 数据库路径: {DB_PATH}")
        print(f"📋 已创建表:")
        print(f"   - orders (订单表)")
        print(f"   - users (用户表)")
        
        # 显示表结构
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        for table_name in inspector.get_table_names():
            print(f"\n📊 表: {table_name}")
            for column in inspector.get_columns(table_name):
                print(f"   - {column['name']}: {column['type']}")
