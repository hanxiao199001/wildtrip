#!/usr/bin/env python3
"""
修复 Pydantic V2 兼容性问题
将 .dict() 替换为 .model_dump()
"""

import os
import re

files_to_fix = [
    './services/user_profile.py',
    './core/agent_orchestrator.py',
    './core/trip_state.py',
    './test_orchestrator.py',
    './test_multi_agent.py'
]

for file_path in files_to_fix:
    if not os.path.exists(file_path):
        print(f"⚠️  跳过: {file_path} (文件不存在)")
        continue
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 统计修改次数
    count = len(re.findall(r'\.dict\(\)', content))
    
    if count == 0:
        print(f"✅ {file_path}: 已是最新版本")
        continue
    
    # 替换 .dict() 为 .model_dump()
    new_content = re.sub(r'\.dict\(\)', '.model_dump()', content)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ {file_path}: 修复了 {count} 处")

print("\n🎉 修复完成！")
