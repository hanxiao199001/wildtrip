#!/usr/bin/env python3
"""测试生成苏东坡历史路线攻略"""

import sys
import os
sys.path.insert(0, '/root/clawd/wildtrip-existing/backend')

# 确保加载.env文件
from dotenv import load_dotenv
load_dotenv('/root/clawd/wildtrip-existing/backend/.env')

from services.ai_engine import AIEngine
from prompts.wildtrip_prompt import build_wildtrip_prompt

# 用户查询
query = "给我规划一个苏东坡被贬路线攻略，重走他的贬谪之路，从杭州到黄州到惠州到儋州，时间15天"

print(f"📝 用户查询: {query}\n")
print("="*80)
print("🚀 开始生成攻略...\n")

# 生成Prompt (先用full模式，因为还没有history模式)
prompt = build_wildtrip_prompt(query, mode='full')

print("📋 生成的Prompt预览:")
print("-"*80)
print(prompt[:800] + "\n...\n")
print("-"*80)

# 调用AI生成
print("\n🤖 调用AI引擎生成攻略...")
ai_engine = AIEngine()
result = ai_engine.generate(prompt, query, mode='full')

print("\n✅ 生成完成！\n")
print("="*80)
print("📄 生成的攻略:\n")
print(result)

# 保存到文件
output_file = '/root/clawd/wildtrip-existing/test_sudongpo_output.md'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"# 用户查询\n{query}\n\n")
    f.write("# 生成的攻略\n\n")
    f.write(result)

print(f"\n💾 结果已保存到: {output_file}")
