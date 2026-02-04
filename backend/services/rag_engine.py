"""
RAG引擎 - 检索增强生成
基于Chroma向量数据库 + DeepSeek Embedding
"""

import chromadb
from chromadb.config import Settings
from loguru import logger
from typing import List, Dict, Optional
import os
from pathlib import Path


class RAGEngine:
    """RAG检索增强生成引擎"""
    
    def __init__(self, db_path: str = "./data/chroma_db"):
        """
        初始化RAG引擎
        
        Args:
            db_path: Chroma数据库路径
        """
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化Chroma客户端
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # 创建或获取collection
        self.travel_guides = self._get_or_create_collection("travel_guides")
        
        logger.info(f"✅ RAG引擎初始化完成 | 数据库: {self.db_path}")
        logger.info(f"📊 当前攻略数量: {self.travel_guides.count()}")
    
    def _get_or_create_collection(self, name: str):
        """获取或创建collection"""
        try:
            return self.client.get_collection(name)
        except:
            return self.client.create_collection(
                name=name,
                metadata={"description": "旅游攻略向量数据库"}
            )
    
    def add_guide(self, 
                  guide_id: str,
                  content: str,
                  metadata: Dict):
        """
        添加攻略到数据库
        
        Args:
            guide_id: 攻略唯一ID
            content: 攻略内容（自动向量化）
            metadata: 元数据 {
                "city": "上海",
                "type": "food|hotel|attraction",
                "source": "xiaohongshu|dianping|ctrip",
                "author": "用户名",
                "rating": 4.5,
                "tags": ["美食", "本地推荐"],
                "url": "原始链接"
            }
        """
        try:
            self.travel_guides.add(
                documents=[content],
                metadatas=[metadata],
                ids=[guide_id]
            )
            logger.info(f"✅ 添加攻略: {guide_id} | 城市: {metadata.get('city')} | 类型: {metadata.get('type')}")
        except Exception as e:
            logger.error(f"❌ 添加攻略失败: {guide_id} | 错误: {e}")
    
    def batch_add_guides(self, guides: List[Dict]):
        """
        批量添加攻略
        
        Args:
            guides: 攻略列表 [{
                "id": "xhs_12345",
                "content": "上海南翔馒头店超级好吃...",
                "metadata": {...}
            }]
        """
        if not guides:
            return
        
        ids = [g["id"] for g in guides]
        documents = [g["content"] for g in guides]
        metadatas = [g["metadata"] for g in guides]
        
        try:
            self.travel_guides.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"✅ 批量添加攻略: {len(guides)}条")
        except Exception as e:
            logger.error(f"❌ 批量添加失败: {e}")
    
    def search(self,
               query: str,
               n_results: int = 10,
               city: Optional[str] = None,
               guide_type: Optional[str] = None) -> List[Dict]:
        """
        检索相关攻略
        
        Args:
            query: 查询文本（如"上海好吃的小笼包"）
            n_results: 返回结果数量
            city: 筛选城市
            guide_type: 筛选类型（food/hotel/attraction）
            
        Returns:
            [{
                "id": "xhs_12345",
                "content": "...",
                "metadata": {...},
                "distance": 0.23  # 相似度（越小越相关）
            }]
        """
        # 构建过滤条件（Chroma语法：$and操作符）
        where = None
        if city and guide_type:
            # 多条件：需要$and
            where = {
                "$and": [
                    {"city": city},
                    {"type": guide_type}
                ]
            }
        elif city:
            # 单条件
            where = {"city": city}
        elif guide_type:
            # 单条件
            where = {"type": guide_type}
        
        try:
            results = self.travel_guides.query(
                query_texts=[query],
                n_results=n_results,
                where=where if where else None
            )
            
            # 格式化结果
            guides = []
            for i in range(len(results['ids'][0])):
                guides.append({
                    "id": results['ids'][0][i],
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else 0
                })
            
            logger.info(f"🔍 检索完成: {query} | 结果: {len(guides)}条 | 城市: {city or '全部'}")
            return guides
            
        except Exception as e:
            logger.error(f"❌ 检索失败: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """获取数据库统计信息"""
        total = self.travel_guides.count()
        
        # TODO: 统计各城市、各类型的数量
        return {
            "total_guides": total,
            "db_path": str(self.db_path)
        }
    
    def clear_all(self):
        """清空数据库（谨慎使用）"""
        logger.warning("⚠️ 清空数据库...")
        self.client.delete_collection("travel_guides")
        self.travel_guides = self._get_or_create_collection("travel_guides")
        logger.info("✅ 数据库已清空")


# 单例
_rag_instance = None


def get_rag_engine() -> RAGEngine:
    """获取RAG引擎实例（单例）"""
    global _rag_instance
    
    if _rag_instance is None:
        db_path = os.getenv('CHROMA_DB_PATH', './data/chroma_db')
        _rag_instance = RAGEngine(db_path)
    
    return _rag_instance


# 示例用法
if __name__ == "__main__":
    # 初始化
    rag = RAGEngine("./test_chroma_db")
    
    # 添加测试数据
    rag.add_guide(
        guide_id="test_001",
        content="上海南翔馒头店的小笼包超级好吃，皮薄汁多，排队2小时值得！本地人都去城隍庙那家老店。",
        metadata={
            "city": "上海",
            "type": "food",
            "source": "xiaohongshu",
            "author": "@上海吃货小王",
            "rating": 4.8,
            "tags": ["小笼包", "本地推荐", "排队"],
            "url": "https://www.xiaohongshu.com/xxx"
        }
    )
    
    rag.add_guide(
        guide_id="test_002",
        content="上海外滩W酒店，无边泳池view绝了！房间能看到东方明珠，早餐自助也很棒。",
        metadata={
            "city": "上海",
            "type": "hotel",
            "source": "xiaohongshu",
            "author": "@旅行达人",
            "rating": 4.7,
            "tags": ["奢华", "泳池", "外滩"],
            "url": "https://www.xiaohongshu.com/yyy"
        }
    )
    
    # 检索
    results = rag.search(
        query="上海好吃的小笼包",
        n_results=5,
        city="上海",
        guide_type="food"
    )
    
    print("\n检索结果:")
    for r in results:
        print(f"\n📝 {r['id']}")
        print(f"内容: {r['content'][:100]}...")
        print(f"相似度: {r['distance']:.3f}")
        print(f"元数据: {r['metadata']}")
    
    # 统计
    print(f"\n数据库统计: {rag.get_stats()}")
