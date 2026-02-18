#!/usr/bin/env python3
"""测试历史数据RAG检索效果"""

import sys
sys.path.insert(0, '/root/clawd/wildtrip-existing/backend')

from services.rag_engine import get_rag_engine

# 获取RAG引擎
rag = get_rag_engine()

print("📊 数据库状态:", rag.get_stats())
print("\n" + "="*80 + "\n")

# 测试1：检索"苏东坡被贬路线"
print("🔍 测试1：检索 '苏东坡被贬路线'")
results = rag.search("苏东坡被贬路线", n_results=5, guide_type="history")
for i, r in enumerate(results, 1):
    print(f"\n{i}. {r['id']}")
    print(f"   相似度: {r.get('distance', 'N/A')}")
    print(f"   内容: {r['content'][:200]}...")
    print(f"   元数据: {r['metadata']}")

print("\n" + "="*80 + "\n")

# 测试2：检索"黄州东坡肉"
print("🔍 测试2：检索 '黄州东坡肉'")
results = rag.search("黄州东坡肉", n_results=3, guide_type="history")
for i, r in enumerate(results, 1):
    print(f"\n{i}. {r['id']}")
    print(f"   内容: {r['content'][:200]}...")

print("\n" + "="*80 + "\n")

# 测试3：检索诗词"念奴娇"
print("🔍 测试3：检索诗词 '念奴娇赤壁怀古'")
results = rag.search("念奴娇赤壁怀古", n_results=3, guide_type="history")
for i, r in enumerate(results, 1):
    print(f"\n{i}. {r['id']}")
    print(f"   标题: {r['metadata'].get('title', 'N/A')}")
    print(f"   内容: {r['content'][:200]}...")

print("\n" + "="*80 + "\n")

# 测试4：检索地点"惠州荔枝"
print("🔍 测试4：检索 '惠州荔枝'")
results = rag.search("惠州荔枝 日啖荔枝三百颗", n_results=3, guide_type="history")
for i, r in enumerate(results, 1):
    print(f"\n{i}. {r['id']}")
    print(f"   类别: {r['metadata'].get('category', 'N/A')}")
    print(f"   内容: {r['content'][:200]}...")

print("\n✅ 测试完成！")
