"""
JSON 存储统一封装模块

背景：项目目前用 JSON / JSONL 文件当轻量数据库（用户攻略历史、点击日志、
攻略元数据等），读写逻辑散落在各个 api/service 中。本模块把这些读写收敛到
一处，提供：

- 原子写入（临时文件 + os.replace，避免写一半崩溃产生坏文件）
- 进程内线程锁（Flask threading 模式下防并发写坏）
- 统一的容错策略（读失败返回 default，不抛异常炸掉请求）

注意：这只是"收敛"，不是数据库。多进程部署（gunicorn 多 worker）下文件锁
不跨进程，正式上线前请按 docs/UPGRADE_NOTES.md 迁移到 SQLite/Supabase。
"""
import json
import os
import tempfile
from pathlib import Path
from threading import Lock
from typing import Any, Iterator, List, Optional, Union

from loguru import logger

PathLike = Union[str, Path]

# 进程内全局写锁（简单粗暴但安全；JSON 文件量小，不构成瓶颈）
_write_lock = Lock()


def read_json(path: PathLike, default: Any = None) -> Any:
    """读取 JSON 文件。文件不存在或解析失败时返回 default（不抛异常）。"""
    p = Path(path)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:
        logger.warning(f"读取JSON失败 {p}: {e}")
        return default


def write_json(path: PathLike, data: Any, indent: int = 2) -> bool:
    """原子写入 JSON 文件（临时文件 + rename）。返回是否成功。"""
    p = Path(path)
    try:
        with _write_lock:
            p.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=str(p.parent), suffix='.tmp')
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=indent)
                os.replace(tmp, str(p))
            finally:
                if os.path.exists(tmp):
                    os.unlink(tmp)
        return True
    except Exception as e:
        logger.error(f"写入JSON失败 {p}: {e}")
        return False


def append_jsonl(path: PathLike, record: dict) -> bool:
    """向 JSONL 文件追加一行记录（append 模式，天然近似原子）。"""
    p = Path(path)
    try:
        with _write_lock:
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, 'a', encoding='utf-8') as f:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        return True
    except Exception as e:
        logger.error(f"追加JSONL失败 {p}: {e}")
        return False


def iter_jsonl(path: PathLike) -> Iterator[dict]:
    """逐行迭代 JSONL 文件，坏行跳过。文件不存在则不产出任何行。"""
    p = Path(path)
    if not p.exists():
        return
    with open(p, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                logger.warning(f"JSONL坏行已跳过 {p}")


def read_jsonl(path: PathLike) -> List[dict]:
    """读取整个 JSONL 文件为列表。"""
    return list(iter_jsonl(path))
