#!/usr/bin/env python3
"""检查ChromaDB中的所有collections"""

import sys
sys.path.insert(0, '/root/clawd/wildtrip-existing/backend')

import chromadb
from pathlib import Path

db_path = Path('/root/clawd/wildtrip-existing/backend/data/chroma_db')
print(f"数据库路径: {db_path}")
print(f"路径存在: {db_path.exists()}")

client = chromadb.PersistentClient(path=str(db_path))

# 列出所有collections
collections = client.list_collections()
print(f"\n📁 Collections总数: {len(collections)}")

for coll in collections:
    print(f"\n  - {coll.name}")
    print(f"    数量: {coll.count()}")
    print(f"    元数据: {coll.metadata}")
    
    # 查看前3条数据
    if coll.count() > 0:
        sample = coll.get(limit=3)
        print(f"    示例ID: {sample['ids'][:3]}")
