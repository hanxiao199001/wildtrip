"""pytest 配置：把 backend 加入 sys.path，保持与运行时一致的导入方式。"""
import sys
from pathlib import Path

BACKEND = Path(__file__).parent.parent / 'backend'
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))
