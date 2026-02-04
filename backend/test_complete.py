"""
完整流程测试 - API → RAG → AI生成
"""

import requests
import time
import json

API_BASE = "http://localhost:5000/api"

def test_complete_flow():
    """测试完整生成流程"""
    
    print("🧪 测试完整流程：API → RAG → AI生成\n")
    print("=" * 60)
    
    # 测试查询
    test_queries = [
        ("上海美食推荐", "food"),
        ("北京3天游", "full"),
        ("成都酒店", "hotel")
    ]
    
    for query, mode in test_queries:
        print(f"\n🔍 测试查询: {query} (模式: {mode})")
        print("-" * 60)
        
        # 1. 创建任务
        print("📤 步骤1：创建生成任务...")
        resp = requests.post(f"{API_BASE}/generate", json={
            "query": query,
            "mode": mode
        })
        
        if resp.status_code != 200:
            print(f"❌ 创建任务失败: {resp.text}")
            continue
        
        data = resp.json()
        task_id = data.get("task_id")
        print(f"✅ 任务ID: {task_id}")
        print(f"   预估时间: {data.get('estimated_time')}")
        
        # 2. 轮询任务状态
        print("\n⏳ 步骤2：等待生成完成...")
        max_wait = 60  # 最多等60秒
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            resp = requests.get(f"{API_BASE}/task/{task_id}")
            if resp.status_code != 200:
                print(f"❌ 查询任务失败: {resp.text}")
                break
            
            data = resp.json()
            status = data.get("status")
            progress = data.get("progress", 0)
            
            print(f"   进度: {progress}% | 状态: {status}")
            
            if status == "completed":
                result = data.get("result", {})
                content = result.get("content", "")
                stats = result.get("stats", {})
                links = result.get("links", [])
                
                print(f"\n✅ 生成完成！")
                print(f"   字数: {stats.get('word_count', 0)}")
                print(f"   酒店: {stats.get('hotels_count', 0)}家")
                print(f"   餐厅: {stats.get('restaurants_count', 0)}家")
                print(f"   景点: {stats.get('tickets_count', 0)}个")
                print(f"   链接: {len(links)}个")
                
                # 显示内容预览
                print(f"\n📝 内容预览（前500字）:")
                print(content[:500] + "...")
                
                # 显示链接
                if links:
                    print(f"\n🔗 可点击链接:")
                    for link in links[:3]:  # 只显示前3个
                        print(f"   - [{link['type']}] {link['name']}")
                        print(f"     {link['url'][:60]}...")
                
                break
            
            elif status == "failed":
                error = data.get("error", "未知错误")
                print(f"\n❌ 生成失败: {error}")
                break
            
            time.sleep(2)
        
        print("\n" + "=" * 60)
    
    print("\n🎉 测试完成！")
    print("\n💡 RAG系统已集成到AI生成流程")
    print("   搜索时会自动检索数据库，生成更本地化的攻略")


if __name__ == "__main__":
    try:
        test_complete_flow()
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
