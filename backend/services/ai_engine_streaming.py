"""
AI生成引擎 - 流式版本（优化进度反馈）
支持Qwen/DeepSeek/Claude/OpenAI等模型的流式输出
"""

from loguru import logger
import os
import time


class StreamingAIEngine:
    """流式AI内容生成引擎（优化版）"""
    
    def __init__(self):
        """初始化AI引擎"""
        self.api_key = os.getenv('AI_API_KEY', '')
        self.base_url = os.getenv('AI_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        self.model = os.getenv('AI_MODEL', 'qwen3-max')
        
        if not self.api_key:
            logger.warning("⚠️ AI_API_KEY未配置，将使用Mock数据")
            self.use_mock = True
        else:
            self.use_mock = False
            logger.info(f"✅ AI引擎初始化完成 | 模型: {self.model}")
    
    def generate_stream(self, prompt: str, query: str, mode: str = 'full', progress_callback=None):
        """
        流式生成攻略内容（RAG增强）
        
        Args:
            prompt: 完整的prompt（包含system + user）
            query: 用户原始查询
            mode: 生成模式
            progress_callback: 进度回调函数（接收 progress, message, chunk）
            
        Returns:
            生成的攻略内容（Markdown格式）
        """
        if self.use_mock:
            logger.info(f"🔧 使用Mock数据生成（mode={mode}）")
            # Mock也模拟流式输出
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from services.ai_engine import AIEngine
            mock_engine = AIEngine()
            content = mock_engine._generate_mock(query, mode)
            
            # 模拟流式输出（分批发送）
            chunk_size = 200
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i+chunk_size]
                progress = min(30 + int((i / len(content)) * 50), 80)
                if progress_callback:
                    progress_callback(progress, "AI正在生成内容...", chunk)
                time.sleep(0.1)  # 模拟延迟
            
            return content
        
        try:
            import openai
            
            # 🔥 RAG步骤1：检索相关攻略
            if progress_callback:
                progress_callback(15, "🔍 正在搜索本地攻略数据库...", "")
            
            rag_context = self._retrieve_relevant_guides(query, mode)
            
            # 分离system和user prompt
            parts = prompt.split('\n\n', 1)
            system_prompt = parts[0] if len(parts) > 1 else ""
            user_prompt = parts[1] if len(parts) > 1 else prompt
            
            # 🔥 RAG步骤2：将检索结果加入prompt
            if rag_context:
                user_prompt = f"""{user_prompt}

---

## 📚 参考真实攻略（来自小红书/大众点评）

{rag_context}

---

请结合以上真实攻略，生成更本地化、更新鲜的推荐内容。
"""
            
            if progress_callback:
                progress_callback(25, "✍️ AI开始生成...", "")
            
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=180.0  # 🔥 提高超时到180秒
            )
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            logger.info(f"🤖 调用AI模型: {self.model} | RAG增强: {'是' if rag_context else '否'} | 流式: 是")
            
            # 🔥 流式生成
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,  # 降回0.7，减少幻觉，提高真实性
                max_tokens=4000,
                timeout=180,
                stream=True,  # 🔥 启用流式输出
            )
            
            # 接收流式输出
            full_content = ""
            chunk_count = 0
            start_time = time.time()
            last_progress_update = 0
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content_chunk = chunk.choices[0].delta.content
                    full_content += content_chunk
                    chunk_count += 1
                    
                    # 每接收10个chunk更新一次进度（避免过于频繁）
                    if chunk_count % 10 == 0 and progress_callback:
                        # 估算进度：30% -> 80%（根据已生成字数）
                        estimated_total_chars = 3000  # 预估总字数
                        progress = min(30 + int((len(full_content) / estimated_total_chars) * 50), 80)
                        
                        # 避免进度倒退
                        if progress > last_progress_update:
                            last_progress_update = progress
                            
                            # 根据字数显示不同的提示
                            if len(full_content) < 500:
                                msg = "💭 AI正在分析景点信息..."
                            elif len(full_content) < 1000:
                                msg = "🍜 AI正在挖掘本地美食..."
                            elif len(full_content) < 1500:
                                msg = "🏨 AI正在筛选优质酒店..."
                            elif len(full_content) < 2000:
                                msg = "📝 AI正在组织攻略结构..."
                            elif len(full_content) < 2500:
                                msg = "✨ AI正在润色文字..."
                            else:
                                msg = "🔥 内容即将生成完成..."
                            
                            progress_callback(progress, msg, content_chunk)
            
            elapsed = time.time() - start_time
            logger.info(f"✅ AI生成完成 | 字数: {len(full_content)} | 耗时: {elapsed:.2f}秒 | chunks: {chunk_count}")
            
            if progress_callback:
                progress_callback(80, "✅ 攻略生成完成！", "")
            
            return full_content
            
        except Exception as e:
            logger.error(f"❌ AI生成失败: {e}")
            logger.info("🔧 回退到Mock数据")
            
            # 回退到Mock
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from services.ai_engine import AIEngine
            mock_engine = AIEngine()
            return mock_engine._generate_mock(query, mode)
    
    def _retrieve_relevant_guides(self, query: str, mode: str) -> str:
        """
        从RAG数据库检索相关攻略
        
        Args:
            query: 用户查询
            mode: 模式（full/hotel/food）
            
        Returns:
            格式化的参考攻略文本
        """
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from services.rag_engine import get_rag_engine
            from prompts.wildtrip_prompt import extract_city_name
            
            # 提取城市
            city = extract_city_name(query)
            
            # 确定检索类型
            guide_type = None
            if mode == 'hotel':
                guide_type = 'hotel'
            elif mode == 'food':
                guide_type = 'food'
            # full模式不限制类型
            
            # 检索
            rag = get_rag_engine()
            results = rag.search(
                query=query,
                n_results=5,  # 最多5条
                city=city,
                guide_type=guide_type
            )
            
            if not results:
                logger.info("📚 RAG数据库为空，跳过检索")
                return ""
            
            # 格式化结果
            context_parts = []
            for i, r in enumerate(results, 1):
                metadata = r.get('metadata', {})
                context_parts.append(f"""
### 参考{i}：{metadata.get('title', '攻略')}
**来源：** {metadata.get('source', '未知')} | **作者：** {metadata.get('author', '匿名')} | **点赞：** {metadata.get('likes', 0)}
**标签：** {', '.join(metadata.get('tags', []))}

{r['content'][:500]}...
""")
            
            logger.info(f"📚 RAG检索完成: {len(results)}条参考攻略")
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.warning(f"⚠️ RAG检索失败: {e}")
            return ""


# 单例模式
_streaming_engine_instance = None

def get_streaming_ai_engine():
    """获取流式AI引擎实例"""
    global _streaming_engine_instance
    if _streaming_engine_instance is None:
        _streaming_engine_instance = StreamingAIEngine()
    return _streaming_engine_instance
