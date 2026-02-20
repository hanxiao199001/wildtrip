#!/usr/bin/env python3
"""检查ChromaDB中的数据"""

import sys
sys.path.insert(0, '/root/clawd/wildtrip-existing/backend')

from services.rag_engine import get_rag_engine

# 获取RAG引擎
rag = get_rag_engine()

# 获取统计信息
stats = rag.get_stats()
print(f"\n📊 数据库统计:")
print(f"总数据量: {stats['total_guides']}")
print(f"数据库路径: {stats['db_path']}")

# 尝试检索历史相关数据
print("\n🔍 检索'苏东坡'相关数据:")
results = rag.search(query="苏东坡", n_results=10)

if results:
    print(f"找到 {len(results)} 条结果:\n")
    for i, r in enumerate(results, 1):
        print(f"\n--- 结果 {i} ---")
        print(f"ID: {r['id']}")
        print(f"内容预览: {r['content'][:200]}...")
        print(f"元数据: {r['metadata']}")
        print(f"相似度: {r.get('distance', 'N/A')}")
else:
    print("❌ 未找到相关数据")

# 检索历史类型的数据
print("\n🔍 检索 type='history' 的数据:")
results_history = rag.search(query="历史", n_results=10, guide_type="history")
if results_history:
    print(f"找到 {len(results_history)} 条历史数据")
    for i, r in enumerate(results_history, 1):
        print(f"\n{i}. {r['id']}")
        print(f"   {r['content'][:150]}...")
else:
    print("❌ 未找到 type='history' 的数据")
