#!/usr/bin/env python3
import chromadb

# 检查两个数据库
dbs = [
    "/root/clawd/wildtrip-existing/backend/data/chroma_db",
    "/root/clawd/wildtrip-existing/data/chroma_db"
]

for db_path in dbs:
    print(f"\n📁 检查: {db_path}")
    try:
        client = chromadb.PersistentClient(path=db_path)
        colls = client.list_collections()
        print(f"  Collections数量: {len(colls)}")
        for coll in colls:
            print(f"    - {coll.name}: {coll.count()}条数据")
    except Exception as e:
        print(f"  ❌ 错误: {e}")
