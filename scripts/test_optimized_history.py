#!/usr/bin/env python3
"""测试优化后的历史路线Prompt"""

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
query = "给我规划一个苏东坡被贬路线，重走黄州到惠州这两站，7天时间，预算有限想省钱"

print(f"📝 用户查询: {query}\n")
print("="*80)

# 步骤1：RAG检索
print("\n🔍 步骤1：检索历史数据...\n")
rag = get_rag_engine()
results = rag.search(query, n_results=10, guide_type="history")

print(f"检索到 {len(results)} 条历史数据")

# 格式化RAG上下文
rag_context_parts = []
for i, r in enumerate(results, 1):
    rag_context_parts.append(f"### 参考{i}：{r['id']}\n\n{r['content']}\n")
rag_context = "\n".join(rag_context_parts)

print(f"RAG上下文长度: {len(rag_context)} 字符\n")
print("="*80)

# 步骤2：生成Prompt
print("\n🎯 步骤2：生成优化后的Prompt...\n")
prompt = build_wildtrip_prompt(query, mode='history', rag_context=rag_context)

print("📋 Prompt预览（前1000字）:")
print("-"*80)
print(prompt[:1000])
print("\n[...省略中间部分...]\n")
print(prompt[-500:])
print("-"*80)

# 步骤3：AI生成
print("\n🤖 步骤3：调用AI生成攻略...\n")
print("⏳ 生成中，请稍候（预计30-60秒）...\n")

ai_engine = AIEngine()
result = ai_engine.generate(prompt, query, mode='history')

print("\n✅ 生成完成！\n")
print("="*80)
print("📄 生成的优化版攻略:\n")
print(result)

# 保存到文件
output_file = '/root/clawd/wildtrip-existing/test_optimized_sudongpo.md'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"# 用户查询\n\n{query}\n\n")
    f.write("---\n\n")
    f.write("# 优化版历史路线攻略\n\n")
    f.write(result)

print(f"\n💾 结果已保存到: {output_file}")

# 统计信息
word_count = len(result)
has_food = "午餐推荐" in result or "晚餐推荐" in result
has_hotel = "住宿推荐" in result
has_meituan = "美团" in result
has_history = "参考：sudongpo" in result

print("\n📊 生成质量检查:")
print(f"  ✅ 字数: {word_count}")
print(f"  {'✅' if has_food else '❌'} 包含餐厅推荐")
print(f"  {'✅' if has_hotel else '❌'} 包含住宿推荐")
print(f"  {'✅' if has_meituan else '❌'} 包含美团链接")
print(f"  {'✅' if has_history else '❌'} 包含史料引用")

print("\n✨ 测试完成！")
