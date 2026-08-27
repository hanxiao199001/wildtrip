"""
冒烟测试：核心模块能 import、关键纯函数跑通。
运行：pytest tests/test_smoke.py -v
"""
import importlib

import pytest


# ---------- 1. 核心模块 import 不炸 ----------

@pytest.mark.parametrize("module", [
    "services.json_storage",
    "services.guide_history_service",
    "services.affiliate_manager",
    "services.taobao_affiliate",
    "services.content_parser",
    "services.ai_engine",
    "services.rag_engine",
    "api.track",
    "api.guides",
])
def test_import(module):
    importlib.import_module(module)


def test_third_party_versions():
    """依赖升级后版本符合钉版本要求"""
    import chromadb
    import openai
    assert chromadb.__version__.startswith("1."), chromadb.__version__
    assert int(openai.__version__.split(".")[0]) >= 2, openai.__version__


# ---------- 2. json_storage 纯函数 ----------

def test_json_storage_roundtrip(tmp_path):
    from services.json_storage import read_json, write_json
    f = tmp_path / "a" / "b.json"
    assert read_json(f, default=[]) == []
    assert write_json(f, {"x": 1, "中文": "好"})
    assert read_json(f) == {"x": 1, "中文": "好"}


def test_jsonl_append_and_read(tmp_path):
    from services.json_storage import append_jsonl, read_jsonl
    f = tmp_path / "clicks.jsonl"
    append_jsonl(f, {"n": 1})
    append_jsonl(f, {"n": 2})
    # 混入一条坏行，应被跳过
    with open(f, "a", encoding="utf-8") as fp:
        fp.write("{bad json}\n")
    append_jsonl(f, {"n": 3})
    assert [r["n"] for r in read_jsonl(f)] == [1, 2, 3]


# ---------- 3. 用户攻略历史（JSON 存储收敛后行为不变） ----------

def test_guide_history_service(tmp_path):
    from services.guide_history_service import GuideHistoryService
    svc = GuideHistoryService(data_dir=tmp_path)
    gid = svc.save_user_guide("user_1", {"query": "成都3天", "content": "第一天..."})
    guides = svc.get_user_guides("user_1")
    assert len(guides) == 1 and guides[0]["guide_id"] == gid
    assert svc.get_guide_by_id("user_1", gid)["query"] == "成都3天"
    assert svc.toggle_favorite("user_1", gid) is True
    assert svc.delete_guide("user_1", gid) is True
    assert svc.get_user_guides("user_1") == []


def test_guide_history_path_traversal_safe(tmp_path):
    from services.guide_history_service import GuideHistoryService
    svc = GuideHistoryService(data_dir=tmp_path)
    f = svc._user_file("../../etc/passwd")
    assert tmp_path in f.parents


# ---------- 4. 内容解析纯函数 ----------

def test_content_parser_runs():
    from services.content_parser import parse_itinerary, extract_wild_tips
    md = "## Day 1 抵达成都\n- 上午：宽窄巷子\n\n省钱贴士：早点订票"
    assert isinstance(parse_itinerary(md), list)
    assert isinstance(extract_wild_tips(md), list)
