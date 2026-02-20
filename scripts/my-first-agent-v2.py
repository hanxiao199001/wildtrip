"""
我的第一个Claude Agent (v2)
功能：让AI回答问题
"""
import asyncio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
)

async def main():
    # 1️⃣ 配置Agent的行为
    options = ClaudeAgentOptions(
        system_prompt="你是一个友好的助手，用中文回答。",
        max_turns=3,
        permission_mode="acceptEdits",
    )

    # 2️⃣ 向AI提问
    print("🤖 正在询问AI...\n")
    
    async for message in query(
        prompt="用一句话解释什么是Claude Agent SDK",
        options=options
    ):
        # 3️⃣ 处理AI的回复（使用类型检查，不是字典）
        if isinstance(message, AssistantMessage):
            # AI的回复
            if isinstance(message.content, str):
                print(f"💬 AI说：{message.content}")
            else:
                # content是列表，遍历所有内容块
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(f"💬 AI说：{block.text}")
        
        elif isinstance(message, ResultMessage):
            # 最终结果
            if message.result_type == "success":
                print(f"\n✅ 完成！")
                if hasattr(message, 'cost_usd'):
                    print(f"花费: ${message.cost_usd:.4f}")
            else:
                print(f"\n❌ 错误：{message}")

# 运行Agent
if __name__ == "__main__":
    asyncio.run(main())
