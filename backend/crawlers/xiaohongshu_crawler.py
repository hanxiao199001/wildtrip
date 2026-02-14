"""
小红书爬虫 - 爬取旅游攻略/美食推荐
反爬策略：IP代理 + UA轮换 + 请求频控
"""

import requests
from typing import List, Dict
from loguru import logger
import time
import random
import hashlib
from datetime import datetime


class XiaoHongShuCrawler:
    """小红书爬虫"""
    
    def __init__(self):
        """初始化爬虫"""
        self.session = requests.Session()
        
        # User-Agent池（避免被ban）
        self.user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
            'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        ]
        
        logger.info("✅ 小红书爬虫初始化完成")
    
    def _get_headers(self) -> Dict:
        """生成请求头（随机UA）"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://www.xiaohongshu.com/'
        }
    
    def search_notes(self, keyword: str, count: int = 20) -> List[Dict]:
        """
        搜索笔记
        
        Args:
            keyword: 关键词（如"上海美食"）
            count: 爬取数量
            
        Returns:
            [{
                "note_id": "xxx",
                "title": "标题",
                "content": "内容",
                "author": "作者",
                "likes": 1234,
                "tags": ["标签1", "标签2"],
                "images": ["图片URL"]
            }]
        """
        logger.info(f"🔍 开始搜索: {keyword}")
        
        # TODO: 实现真实的小红书API调用
        # 由于小红书反爬严格，这里先返回Mock数据
        # 实际使用时需要：
        # 1. 获取小红书Cookie（登录后）
        # 2. 解析小红书搜索接口
        # 3. 处理加密参数
        
        logger.warning("⚠️ 当前使用Mock数据，真实爬虫待实现")
        
        return self._generate_mock_data(keyword, count)
    
    def _generate_mock_data(self, keyword: str, count: int) -> List[Dict]:
        """生成Mock数据（开发测试用）- 优化版，更真实"""
        
        # 根据关键词生成相关数据
        city = self._extract_city(keyword)
        guide_type = self._extract_type(keyword)
        
        mock_data = []
        
        if "美食" in keyword or "吃" in keyword:
            # 美食类 - 更真实的店名和内容
            food_spots = {
                "上海": [
                    ("南翔馒头店", "城隍庙的小笼包王者！皮薄汁多，一口下去满嘴鲜美。排队2小时很正常，但真的值！本地人都去老店，游客太多的分店别去。早上9点前去人少。", ["小笼包", "老字号", "排队美食"]),
                    ("阿大葱油饼", "火了20年的葱油饼！外酥里嫩，葱香四溢。下午3点后去，早上卖完就关门。只收现金，记得带零钱。", ["网红", "街头小吃", "必吃"]),
                    ("佳家汤包", "本地人的早餐首选！汤包个头大、汤汁足，比南翔便宜一半。环境一般但味道绝了，6块钱4个汤包超值。", ["本地推荐", "性价比", "早餐"]),
                    ("老盛昌汤包", "24小时营业的深夜食堂！夜宵来这吃汤包+牛肉粉丝汤，完美。凌晨2点还在排队的店，靠谱！", ["24小时", "夜宵", "汤包"]),
                    ("大壶春", "生煎包天花板！底部焦脆，上面松软，一口爆汁。推荐虾仁生煎，鲜得眉毛掉下来。", ["生煎", "老字号", "必吃"])
                ],
                "北京": [
                    ("护国寺小吃", "老北京小吃集合地！豆汁儿、焦圈、卤煮火烧、驴打滚...一次吃遍北京味。豆汁儿第一次喝可能不习惯，但喝惯了就上瘾。", ["老北京", "传统小吃", "特色"]),
                    ("全聚德烤鸭", "百年老店，外酥里嫩的烤鸭配甜面酱、黄瓜丝、葱丝，经典！但价格偏贵，人均200+。本地人更推荐四季民福。", ["烤鸭", "老字号", "必吃"]),
                    ("姚记炒肝", "炒肝不是炒的，是煮的！配包子吃，地道北京味。外地人可能吃不习惯，但值得尝试。", ["炒肝", "传统", "早餐"]),
                    ("庆丰包子铺", "习大大都来吃的包子铺！猪肉大葱包子、炒肝、豆腐脑，15块钱吃饱。", ["包子", "平民美食", "性价比"]),
                    ("海底捞", "火锅界的服务天花板！等位有小吃、美甲、擦鞋，吃完送水果。虽然哪都有，但北京的服务更好。", ["火锅", "服务好", "网红"])
                ],
                "成都": [
                    ("龙抄手", "成都必吃！红油抄手、钟水饺、担担面...川味小吃一网打尽。推荐红油抄手，麻辣鲜香。", ["小吃", "老字号", "必吃"]),
                    ("蜀九香火锅", "本地人都去的火锅店！比海底捞便宜，味道更正宗。鸳鸯锅底，不能吃辣的也能享受。", ["火锅", "本地推荐", "性价比"]),
                    ("陈麻婆豆腐", "麻婆豆腐发源地！麻辣鲜香嫩烫，配米饭能吃三碗。招牌陈麻婆豆腐必点。", ["川菜", "老字号", "经典"]),
                    ("小龙坎火锅", "网红火锅！装修好看，适合拍照。味道也不错，就是人多要排队。建议工作日去。", ["火锅", "网红", "适合拍照"]),
                    ("冒椒火辣", "冒菜天花板！比火锅方便，一人食也OK。麻辣鲜香，配料丰富，人均40块吃撑。", ["冒菜", "快餐", "性价比"])
                ]
            }
            
            spots = food_spots.get(city, food_spots["上海"])
            mock_data = [
                {
                    "note_id": f"xhs_food_{hashlib.md5(f'{city}_{spot[0]}'.encode()).hexdigest()[:8]}",
                    "title": f"{city}{spot[0]} - 本地人强推！",
                    "content": spot[1],
                    "author": f"@{city}吃货小{random.choice(['王', '李', '张', '刘', '陈'])}",
                    "likes": random.randint(1000, 8000),
                    "tags": spot[2] + [city, "美食"],
                    "images": [],
                    "create_time": datetime.now().isoformat()
                }
                for spot in spots[:min(count, len(spots))]
            ]
        
        elif "酒店" in keyword or "住宿" in keyword:
            # 酒店类 - 真实酒店名称
            hotels = {
                "上海": [
                    ("上海外滩W酒店", "奢华五星！无边泳池俯瞰外滩，房间能看东方明珠。早餐自助很棒，服务一流。就是贵，1500+/晚。适合蜜月、纪念日。", ["奢华", "泳池", "外滩景观"]),
                    ("上海亚朵酒店", "性价比之王！房间干净舒适，床品超级软。免费早餐够吃，位置方便。本地人出差首选，300-400/晚。", ["性价比", "商务", "连锁"]),
                    ("上海锦江之星", "经济实惠！虽然老旧但干净，交通方便。适合学生党、背包客。120-180/晚，省钱首选。", ["经济型", "背包客", "便宜"]),
                    ("上海璞丽酒店", "顶级奢华！苏州河畔，设计感满分。米其林餐厅、SPA一流。土豪专属，2000+/晚。", ["顶奢", "设计酒店", "米其林"]),
                    ("上海民宿（老洋房）", "特色住宿！老上海风情，适合文艺青年。价格200-500/晚，体验当地生活。", ["民宿", "特色", "文艺"])
                ],
                "北京": [
                    ("北京王府井希尔顿", "地理位置绝佳！王府井步行街旁，逛街吃饭超方便。房间大，服务好。800-1200/晚。", ["市中心", "购物方便", "商务"]),
                    ("北京如家快捷", "连锁经济酒店，胜在稳定。哪家都差不多，干净卫生。100-150/晚，适合短途。", ["经济型", "连锁", "稳定"]),
                    ("北京四合院民宿", "老北京特色！住四合院，体验胡同文化。老板热情，早餐有豆汁儿焦圈。300-600/晚。", ["民宿", "四合院", "特色"]),
                    ("北京三里屯CHAO酒店", "潮流设计酒店！三里屯核心区，夜生活丰富。适合年轻人，600-1000/晚。", ["潮流", "夜生活", "年轻"]),
                    ("北京7天连锁", "便宜！就是便宜！80-120/晚，穷游首选。卫生达标，别要求太高。", ["便宜", "穷游", "经济"])
                ],
                "成都": [
                    ("成都博舍酒店", "太古里旁的设计酒店！川西风格，很有味道。屋顶酒吧view绝了，1200+/晚。", ["设计酒店", "太古里", "奢华"]),
                    ("成都亚朵酒店", "连锁品牌，稳定靠谱！位置方便，性价比高。300-400/晚，商务首选。", ["性价比", "商务", "连锁"]),
                    ("成都宽窄巷子民宿", "住宽窄巷子里面！早上起来吃龙抄手，晚上逛锦里。200-400/晚，体验当地。", ["民宿", "宽窄巷子", "特色"]),
                    ("成都7天连锁", "经济实惠，连锁品质。100-150/晚，适合学生党。", ["经济型", "便宜", "学生"]),
                    ("成都熊猫主题酒店", "亲子首选！满屋熊猫元素，孩子超爱。300-500/晚，适合家庭游。", ["亲子", "主题", "特色"])
                ]
            }
            
            hotel_list = hotels.get(city, hotels["上海"])
            mock_data = [
                {
                    "note_id": f"xhs_hotel_{hashlib.md5(f'{city}_{h[0]}'.encode()).hexdigest()[:8]}",
                    "title": f"{h[0]} 住宿体验分享",
                    "content": h[1],
                    "author": f"@旅行达人{random.choice(['小美', '阿华', '老李', '晓雯'])}",
                    "likes": random.randint(500, 5000),
                    "tags": h[2] + [city, "酒店"],
                    "images": [],
                    "create_time": datetime.now().isoformat()
                }
                for h in hotel_list[:min(count, len(hotel_list))]
            ]
        
        else:
            # 景点类
            attractions = {
                "上海": [
                    ("外滩", "上海必去！夜景无敌，东方明珠、上海中心尽收眼底。晚上7-9点最美，拍照圣地。免费！", ["夜景", "必去", "免费"]),
                    ("迪士尼", "亚洲最大迪士尼！刺激项目多，排队也多。建议买快速通行证，工作日去。门票399起。", ["主题乐园", "亲子", "刺激"]),
                    ("田子坊", "文艺小资！小店、咖啡馆、创意市集。适合拍照、淘宝。下午去人少。", ["文艺", "拍照", "小资"]),
                    ("南京路步行街", "购物天堂！各种品牌都有，但人多挤。晚上霓虹灯亮起来很漂亮。", ["购物", "夜景", "繁华"]),
                    ("豫园", "老上海风情！古色古香，小笼包、南翔馒头店在这。门票30元。", ["古迹", "传统", "美食"])
                ],
                "北京": [
                    ("故宫", "必去！世界最大宫殿群，震撼！一定要提前网上订票，现场不卖。门票60元。", ["必去", "古迹", "震撼"]),
                    ("长城", "不到长城非好汉！建议去慕田峪或八达岭。爬上去很累但值得，门票40元。", ["必去", "长城", "爬山"]),
                    ("颐和园", "皇家园林！昆明湖泛舟、佛香阁登高，半天时间。门票30元。", ["园林", "泛舟", "休闲"]),
                    ("天安门", "升国旗震撼！早上5点多去占位置。广场免费，拍照打卡必去。", ["必去", "升旗", "免费"]),
                    ("南锣鼓巷", "文艺胡同！小店、咖啡馆、创意市集。人多，周内去。", ["文艺", "胡同", "拍照"])
                ],
                "成都": [
                    ("宽窄巷子", "成都名片！老街、小吃、茶馆。晚上最热闹，但人挤人。免费。", ["必去", "老街", "免费"]),
                    ("熊猫基地", "看国宝！早上8-10点熊猫最活跃。门票55元，建议早去。", ["熊猫", "亲子", "必去"]),
                    ("锦里", "古街夜市！小吃、特产、酒吧。晚上去感受成都夜生活。免费。", ["夜市", "小吃", "免费"]),
                    ("武侯祠", "三国迷必去！刘备墓、诸葛亮殿。门票60元，历史氛围浓厚。", ["古迹", "三国", "历史"]),
                    ("太古里", "潮流地标！奢侈品、网红店、美食。适合拍照、逛街。", ["购物", "潮流", "拍照"])
                ]
            }
            
            attr_list = attractions.get(city, attractions["上海"])
            mock_data = [
                {
                    "note_id": f"xhs_attr_{hashlib.md5(f'{city}_{a[0]}'.encode()).hexdigest()[:8]}",
                    "title": f"{city}{a[0]} - 超详细攻略",
                    "content": a[1],
                    "author": f"@{city}旅游博主{random.choice(['小月', '阿杰', '大鹏', '晓晓'])}",
                    "likes": random.randint(2000, 10000),
                    "tags": a[2] + [city, "景点"],
                    "images": [],
                    "create_time": datetime.now().isoformat()
                }
                for a in attr_list[:min(count, len(attr_list))]
            ]
        
        logger.info(f"✅ Mock数据生成完成: {len(mock_data)}条 | {city} | {guide_type}")
        return mock_data
    
    def _extract_city(self, keyword: str) -> str:
        """从关键词提取城市"""
        cities = ["北京", "上海", "广州", "深圳", "杭州", "成都", "西安", "重庆", "海口", "三亚"]
        for city in cities:
            if city in keyword:
                return city
        return "上海"  # 默认
    
    def _extract_type(self, keyword: str) -> str:
        """从关键词提取类型"""
        if "美食" in keyword or "吃" in keyword:
            return "美食"
        elif "酒店" in keyword or "住" in keyword:
            return "酒店"
        elif "景点" in keyword or "门票" in keyword:
            return "景点"
        else:
            return "攻略"
    
    def rate_limit(self, delay: float = 1.0):
        """请求频控（避免被ban）"""
        time.sleep(delay + random.random())


# 全局实例
_crawler_instance = None


def get_xiaohongshu_crawler() -> XiaoHongShuCrawler:
    """获取小红书爬虫实例（单例）"""
    global _crawler_instance
    
    if _crawler_instance is None:
        _crawler_instance = XiaoHongShuCrawler()
    
    return _crawler_instance


# 示例用法
if __name__ == "__main__":
    crawler = XiaoHongShuCrawler()
    
    # 搜索美食
    results = crawler.search_notes("上海美食", count=10)
    
    print(f"\n搜索结果: {len(results)}条\n")
    for r in results:
        print(f"📝 {r['title']}")
        print(f"   作者: {r['author']} | 点赞: {r['likes']}")
        print(f"   内容: {r['content'][:100]}...")
        print(f"   标签: {', '.join(r['tags'])}\n")
