"""
用户攻略历史服务
JSON 文件存储（每个用户一个文件），无需数据库迁移。
供 api/user.py 和 api/generate.py 使用。
"""
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from threading import Lock

from loguru import logger

from services.json_storage import read_json, write_json

_DATA_DIR = Path(os.getenv('DB_DIR', str(Path(__file__).parent.parent / 'data'))) / 'user_guides'
_lock = Lock()


class GuideHistoryService:
    """用户攻略历史（JSON 文件存储）"""

    def __init__(self, data_dir: Path = _DATA_DIR):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _user_file(self, user_id: str) -> Path:
        # 防路径穿越：只保留安全字符
        safe_id = ''.join(c for c in user_id if c.isalnum() or c in '-_')
        return self.data_dir / f'{safe_id}.json'

    def _load(self, user_id: str) -> list:
        return read_json(self._user_file(user_id), default=[])

    def _save(self, user_id: str, guides: list):
        write_json(self._user_file(user_id), guides)

    def save_user_guide(self, user_id: str, guide: dict) -> str:
        """保存一篇攻略到用户历史，返回 guide_id"""
        with _lock:
            guides = self._load(user_id)
            guide_id = uuid.uuid4().hex[:12]
            guides.insert(0, {
                'guide_id': guide_id,
                'query': guide.get('query', ''),
                'mode': guide.get('mode', ''),
                'content': guide.get('content', ''),
                'stats': guide.get('stats', {}),
                'seo_url': guide.get('seo_url'),
                'favorite': False,
                'created_at': datetime.now().isoformat(timespec='seconds'),
            })
            self._save(user_id, guides)
        return guide_id

    def get_user_guides(self, user_id: str, limit: int = 50) -> list:
        return self._load(user_id)[:limit]

    def get_guide_by_id(self, user_id: str, guide_id: str):
        for g in self._load(user_id):
            if g.get('guide_id') == guide_id:
                return g
        return None

    def delete_guide(self, user_id: str, guide_id: str) -> bool:
        with _lock:
            guides = self._load(user_id)
            remaining = [g for g in guides if g.get('guide_id') != guide_id]
            if len(remaining) == len(guides):
                return False
            self._save(user_id, remaining)
        return True

    def toggle_favorite(self, user_id: str, guide_id: str) -> bool:
        with _lock:
            guides = self._load(user_id)
            for g in guides:
                if g.get('guide_id') == guide_id:
                    g['favorite'] = not g.get('favorite', False)
                    self._save(user_id, guides)
                    return g['favorite']
        return False

    def get_stats(self) -> dict:
        files = list(self.data_dir.glob('*.json'))
        total_guides = 0
        for f in files:
            try:
                total_guides += len(read_json(f, default=[]))
            except Exception:
                pass
        return {'total_users': len(files), 'total_guides': total_guides}


_instance = None


def get_guide_history_service() -> GuideHistoryService:
    global _instance
    if _instance is None:
        _instance = GuideHistoryService()
    return _instance
