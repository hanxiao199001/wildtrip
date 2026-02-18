#!/usr/bin/env python3
"""直接测试ChromaDB"""

import chromadb
from pathlib import Path

db_path = Path('/root/clawd/wildtrip-existing/backend/data/chroma_db')
client = chromadb.PersistentClient(path=str(db_path))

# 获取collection
coll = client.get_collection("travel_guides")
print(f"Collection: {coll.name}")
print(f"总数: {coll.count()}")

# 测试检索
results = coll.query(
    query_texts=["苏东坡黄州赤壁"],
    n_results=5
)

print(f"\n检索结果数量: {len(results['ids'][0])}")
for i in range(len(results['ids'][0])):
    print(f"\n{i+1}. {results['ids'][0][i]}")
    print(f"   距离: {results['distances'][0][i]:.3f}")
    print(f"   内容: {results['documents'][0][i][:200]}...")
    print(f"   元数据: {results['metadatas'][0][i]}")
