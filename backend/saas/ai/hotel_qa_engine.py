"""
重构后的酒店 AI 客服问答引擎 (B端销冠版)
"""
import logging
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class HotelQAEngine:
    """
    摆脱底层复杂依赖的、极其轻量级的 MVP 销冠引擎
    """

    def __init__(self, hotel_id="hotel_001", hotel_name="海边小筑民宿"):
        self.hotel_id = hotel_id
        self.hotel_name = hotel_name
        self.hotel_kb = self._get_default_kb()

    def _get_default_kb(self) -> Dict[str, Any]:
        """内置的 B端私域知识库 (也就是你的卖点和底价)"""
        return {
            "name": "海口隐逸海岛精品民宿",
            "features": "庭院极具私密性，有超大公区适合男孩子拼装遥控积木，自带适合练习憋气和蛙泳的恒温亲子池。",
            "surroundings": [
                {"tag": "带娃赶海", "desc": "下午4点光线柔和时，步行15分钟有一处未被开发的野海滩，极品出片机位，适合用 DJI Pocket 记录。"},
                {"tag": "本地美食", "desc": "骑小电驴5分钟，有一家本地人扎堆的无名老爸茶，绝不踩雷网红店。"}
            ],
            "inventory": {
                "周末": {"status": "余量紧张", "direct_price": 580, "ota_price": 699}
            }
        }

    def answer_question(self, question: str, context: str = "", intent: str = None, hotel_kb: dict = None) -> str:
        """
        核心回复逻辑：不再调用容易失败的外部大模型 API，直接使用本地规则引擎进行高转化回复。
        """
        logger.info(f"[{self.hotel_id}] 收到咨询: {question}")

        # 意图 1：询价与预订 (最高优先级，直接抛出底价诱饵)
        if any(word in question for word in ["钱", "价格", "多少", "订房", "周末", "房"]):
            return (
                f"这周末我们刚好还有房！在携程上大概要 {self.hotel_kb['inventory']['周末']['ota_price']}，"
                f"但您直接在我这下订单，免了平台抽成，内部底价是 {self.hotel_kb['inventory']['周末']['direct_price']} 元。\n"
                f"我们院子特别大，带孩子来的话，在公区玩遥控积木完全施展得开，晚上还能在恒温池教教孩子游泳。确定要的话我给您发专属直销链接！"
            )

        # 意图 2：周边玩法与带娃痛点 (情绪价值拉满)
        if any(word in question for word in ["玩", "带娃", "去哪", "攻略", "附近", "好玩"]):
            return (
                f"完全不用您自己做攻略！下午气温合适的时候，我推荐您去旁边步行 15 分钟的野海滩，避开人流，那个时候光线绝佳，如果有 DJI Pocket 之类的设备拍家庭 VLOG 特别出片。晚上再骑个车去吃我们本地人常去的老爸茶。\n"
                f"如果您订我们这儿，我会把完整的避坑打卡地图发给您，保证孩子玩得开心您还不累。"
            )

        # 意图 3：设施与细节咨询 (如：宠物、早餐)
        if "宠物" in question:
            return "我们是可以带宠物的哦！带上毛孩子一起在草坪上跑，特别出片。不过为了维护卫生，会收取一点点清洁费。您是带狗狗还是猫咪呢？"

        if "早餐" in question:
            return "我们的早餐是阿姨每天早上现做的本地特色，绝对比外面的网红店地道。您如果直接在我这定，我私人给您把双早免了！"

        # 兜底回复
        return f"您好！我是{self.hotel_name}的智能掌柜。不管是了解房型、比对价格，还是想知道周边怎么带娃玩得与众不同，您随便问我！"


# ==========================================
# 测试代码：直接运行本文件即可看到效果
# ==========================================
if __name__ == '__main__':
    # 极简配置日志，避免满屏乱码
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    engine = HotelQAEngine()

    print("\n" + "="*50)
    print("🏨 AI 金牌主理人已上线 (MVP 无依赖版)...")
    print("="*50 + "\n")

    test_questions = [
        "你们能带宠物吗？",
        "周末带孩子去你们那有什么好玩的？",
        "多少钱一晚？",
        "早餐几点？"
    ]

    for q in test_questions:
        print(f"👤 散客咨询: {q}")
        reply = engine.answer_question(question=q)
        print(f"🤖 掌柜回复: {reply}\n")
        print("-" * 50 + "\n")
