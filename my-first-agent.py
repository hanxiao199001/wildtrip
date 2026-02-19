"""
我的第一个Claude Agent
功能：让AI回答问题
"""
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    # 1️⃣ 配置Agent的行为
    options = ClaudeAgentOptions(
        system_prompt="你是一个友好的助手，用中文回答。",  # AI的角色设定
        max_turns=3,  # 最多对话3轮
        permission_mode="acceptEdits",  # 自动接受编辑（学习用）
    )

    # 2️⃣ 向AI提问
    print("🤖 正在询问AI...\n")
    
    async for message in query(
        prompt="用一句话解释什么是Claude Agent SDK",
        options=options
    ):
        # 3️⃣ 处理AI的回复
        if message["type"] == "assistant":
            print(f"💬 AI说：{message['message']}")
        
        elif message["type"] == "result":
            if message["subtype"] == "success":
                print(f"\n✅ 完成！花费: ${message.get('total_cost_usd', 0):.4f}")
            else:
                print(f"\n❌ 错误：{message.get('errors', [])}")

# 运行Agent
if __name__ == "__main__":
    asyncio.run(main())
