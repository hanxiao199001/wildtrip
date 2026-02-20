#!/usr/bin/env python3
"""测试历史模式攻略生成"""

import sys
import os
sys.path.insert(0, '/root/clawd/wildtrip-existing/backend')

# 加载环境变量
from dotenv import load_dotenv
load_dotenv('/root/clawd/wildtrip-existing/backend/.env')

# 设置数据库路径
os.environ['CHROMA_DB_PATH'] = '/root/clawd/wildtrip-existing/backend/data/chroma_db'

from services.ai_engine import AIEngine
from services.rag_engine import get_rag_engine
from prompts.wildtrip_prompt import build_wildtrip_prompt

# 用户查询
query = "给我规划一个苏东坡被贬路线攻略，重走他的贬谪之路，从杭州到黄州到惠州到儋州，时间15天"

print(f"📝 用户查询: {query}\n")
print("="*80)

# 步骤1：RAG检索历史数据
print("\n🔍 步骤1：检索历史数据...\n")
rag = get_rag_engine()
results = rag.search(query, n_results=10, guide_type="history")

print(f"检索到 {len(results)} 条历史数据:")
for i, r in enumerate(results[:5], 1):
    print(f"  {i}. {r['id']}")
    print(f"     类别: {r['metadata'].get('category')}")
    print(f"     内容: {r['content'][:100]}...")

# 格式化RAG上下文
rag_context_parts = []
for i, r in enumerate(results, 1):
    rag_context_parts.append(f"### 参考{i}：{r['id']}\n\n{r['content']}\n")
rag_context = "\n".join(rag_context_parts)

print(f"\n📚 RAG上下文总长度: {len(rag_context)} 字符\n")
print("="*80)

# 步骤2：生成Prompt（使用history模式）
print("\n🎯 步骤2：生成历史路线Prompt...\n")
prompt = build_wildtrip_prompt(query, mode='history', rag_context=rag_context)

print("📋 Prompt预览:")
print("-"*80)
print(prompt[:1200] + "\n...\n")
print("-"*80)

# 步骤3：调用AI生成
print("\n🤖 步骤3：调用AI生成攻略...\n")
ai_engine = AIEngine()

# 注意：对于history模式，prompt已经包含了RAG上下文
result = ai_engine.generate(prompt, query, mode='history')

print("\n✅ 生成完成！\n")
print("="*80)
print("📄 生成的攻略:\n")
print(result)

# 保存到文件
output_file = '/root/clawd/wildtrip-existing/test_sudongpo_history.md'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"# 用户查询\n\n{query}\n\n")
    f.write("---\n\n")
    f.write("# 生成的历史路线攻略\n\n")
    f.write(result)

print(f"\n💾 结果已保存到: {output_file}")
print("\n✨ 测试完成！")
