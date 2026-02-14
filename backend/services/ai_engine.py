"""
AI生成引擎
支持Qwen/DeepSeek/Claude/OpenAI等模型
"""

from loguru import logger
import os


class AIEngine:
    """AI内容生成引擎"""

    def __init__(self):
        """初始化AI引擎"""
        self.api_key = os.getenv('AI_API_KEY', '')
        self.base_url = os.getenv('AI_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        self.model = os.getenv('AI_MODEL', 'qwen3-max')

        if not self.api_key:
            logger.warning("⚠️ AI_API_KEY未配置，将使用离线数据")
            self.use_mock = True
        else:
            self.use_mock = False
            logger.info(f"✅ AI引擎初始化完成 | 模型: {self.model}")

    def generate(self, prompt: str, query: str, mode: str = 'full') -> str:
        """生成攻略内容（RAG增强）"""
        if self.use_mock:
            logger.info(f"🔧 使用离线数据生成（mode={mode}）")
            return self._generate_mock(query, mode)

        try:
            import openai

            rag_context = self._retrieve_relevant_guides(query, mode)

            parts = prompt.split('\n\n', 1)
            system_prompt = parts[0] if len(parts) > 1 else ""
            user_prompt = parts[1] if len(parts) > 1 else prompt

            if rag_context:
                user_prompt = f"""{user_prompt}

---

## 参考真实攻略（来自小红书/大众点评）

{rag_context}

---

请结合以上真实攻略，生成更本地化、更新鲜的推荐内容。
"""

            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=120.0
            )

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            logger.info(f"🤖 调用AI模型: {self.model} | RAG增强: {'是' if rag_context else '否'}")

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=4000,
                timeout=120,
            )

            content = response.choices[0].message.content
            logger.info(f"✅ AI生成完成 | 字数: {len(content)}")
            return content

        except Exception as e:
            logger.error(f"❌ AI生成失败: {e}")
            logger.info("🔧 回退到离线数据")
            return self._generate_mock(query, mode)

    def _retrieve_relevant_guides(self, query: str, mode: str) -> str:
        """从RAG数据库检索相关攻略"""
        try:
            from services.rag_engine import get_rag_engine
            from prompts.wildtrip_prompt import extract_city_name

            city = extract_city_name(query)
            guide_type = None
            if mode == 'hotel':
                guide_type = 'hotel'
            elif mode == 'food':
                guide_type = 'food'

            rag = get_rag_engine()
            results = rag.search(query=query, n_results=5, city=city, guide_type=guide_type)

            if not results:
                return ""

            context_parts = []
            for i, r in enumerate(results, 1):
                metadata = r.get('metadata', {})
                context_parts.append(f"""
### 参考{i}：{metadata.get('title', '攻略')}
**来源：** {metadata.get('source', '未知')} | **点赞：** {metadata.get('likes', 0)}

{r['content'][:500]}...
""")
            return "\n".join(context_parts)

        except Exception as e:
            logger.warning(f"⚠️ RAG检索失败: {e}")
            return ""

    def _get_city_data(self, city: str) -> dict:
        """获取城市真实商家数据（所有商家均为真实存在、可在美团/大众点评搜到的）"""
        city_database = {
            "海口": {
                "breakfast_name": "老彭记海南粉",
                "breakfast_dish1": "海南腌粉",
                "breakfast_desc1": "酸甜口味，配花生酸菜牛肉干",
                "breakfast_dish2": "清补凉",
                "breakfast_desc2": "椰奶+10多种配料，海口夏天续命水",
                "breakfast_comment": "海口本地人从小吃到大的粉店，料足味正",
                "dessert": "清补凉",
                "high_end_restaurant": "丁村万人海鲜广场",
                "high_end_feature": "自己买海鲜选加工店做，明码标价",
                "high_end_dish1": "清蒸石斑鱼",
                "high_end_price1": "时价/斤",
                "high_end_desc1": "原汁原味，肉质鲜嫩",
                "high_end_dish2": "椒盐皮皮虾",
                "high_end_price2": "50-80/斤",
                "high_end_desc2": "个大肉满，椒盐味香",
                "high_end_dish3": "蒜蓉蒸扇贝",
                "high_end_price3": "5-8/只",
                "high_end_desc3": "蒜香浓郁肉嫩鲜甜",
                "high_end_comment": "海鲜广场百家加工店，挑人多的那家准没错",
                "mid_restaurant": "龙泉人文昌鸡饭店",
                "mid_feature": "海南四大名菜之首文昌鸡，本地口碑老店",
                "mid_dish1": "白切文昌鸡",
                "mid_price1": "半只60-80",
                "mid_desc1": "皮脆肉滑，蘸秘制调料绝了",
                "mid_dish2": "鸡油饭",
                "mid_price2": "5/碗",
                "mid_desc2": "鸡汤鸡油煮的饭，粒粒分明",
                "mid_comment": "本地人认可度高，文昌鸡嫩滑，鸡油饭必配",
                "snack1": "清补凉",
                "snack1_price": "8-15",
                "snack1_desc": "椰奶+10多种配料，海口解暑神器",
                "snack2": "抱罗粉",
                "snack2_price": "12-18",
                "snack2_desc": "粗粉配猪骨汤底，鲜美爽口",
                "snack3": "椰子鸡",
                "nightmarket_comment": "海大南门夜市品种多价格实惠，本地大学生最爱",
                "cuisine_type": "海鲜",
                "landmark1": "骑楼老街",
                "attraction1": "骑楼老街",
                "attraction1_price": "0",
                "attraction1_desc": "百年南洋建筑风情，拍照打卡必去",
                "attraction2": "海口火山口国家地质公园",
                "attraction2_price": "50",
                "attraction2_price_orig": "60",
                "attraction2_highlight": "万年火山口、热带植物、熔岩隧道",
                "attraction2_comment": "爬到火山口顶能看海口全景，拍照绝佳",
                "attraction3": "海南热带野生动植物园",
                "attraction3_price": "100",
                "attraction3_price_orig": "128",
                "attraction3_highlight": "喂长颈鹿、坐小火车穿猛兽区",
                "attraction3_comment": "亲子游必去！小朋友最喜欢喂长颈鹿",
                "dinner_restaurant": "嗲嗲的椰子鸡",
                "dinner_feature": "新鲜椰子水煮文昌鸡，清甜养生",
                "dinner_comment": "先喝汤再涮鸡，清甜不油腻，老人小孩都爱",
                "souvenirs": "春光椰子糖、南国椰子粉、黄灯笼辣椒酱",
                "best_season": "11月-次年4月",
                "weather_tips": "7-9月台风多；出门带伞防阵雨"
            },
            "三亚": {
                "breakfast_name": "林姐香味海鲜",
                "breakfast_dish1": "港门粉",
                "breakfast_desc1": "海鲜汤底细粉，加虾仁蟹肉",
                "breakfast_dish2": "椰子饭",
                "breakfast_desc2": "糯米塞椰子里蒸，椰香浓郁",
                "breakfast_comment": "港门粉是三亚特色早餐，海鲜汤底鲜味十足",
                "dessert": "芒果肠粉",
                "high_end_restaurant": "第一市场海鲜加工",
                "high_end_feature": "三亚最大海鲜市场，买海鲜找店加工",
                "high_end_dish1": "龙虾（蒜蓉/刺身）",
                "high_end_price1": "150-250/只",
                "high_end_desc1": "鲜活龙虾现杀现做",
                "high_end_dish2": "和乐蟹",
                "high_end_price2": "80-120/斤",
                "high_end_desc2": "海南四大名菜，膏满黄肥",
                "high_end_dish3": "蒜蓉粉丝蒸扇贝",
                "high_end_price3": "5-8/只",
                "high_end_desc3": "蒜香配扇贝鲜甜可口",
                "high_end_comment": "买海鲜看清秤，找人多的加工店不容易被宰",
                "mid_restaurant": "海南粉小吃街",
                "mid_feature": "本地粉面品种齐全价格实惠",
                "mid_dish1": "抱罗粉",
                "mid_price1": "15/碗",
                "mid_desc1": "粉滑汤鲜，猪骨汤底",
                "mid_dish2": "陵水酸粉",
                "mid_price2": "12/碗",
                "mid_desc2": "酸辣开胃，夏天最爽",
                "mid_comment": "来三亚别只吃海鲜，本地粉面便宜好吃",
                "snack1": "椰子冻",
                "snack1_price": "15-20",
                "snack1_desc": "椰壳装椰奶冻，冰凉爽口",
                "snack2": "清补凉",
                "snack2_price": "10-15",
                "snack2_desc": "椰奶+芒果+红豆，三亚解暑标配",
                "snack3": "炸炸",
                "nightmarket_comment": "第一市场夜市种类多价格合理",
                "cuisine_type": "海鲜",
                "landmark1": "亚龙湾",
                "attraction1": "亚龙湾海滩",
                "attraction1_price": "0",
                "attraction1_desc": "三亚最好海滩，沙细水清",
                "attraction2": "蜈支洲岛",
                "attraction2_price": "136",
                "attraction2_price_orig": "168",
                "attraction2_highlight": "潜水天堂、情人桥、海上项目",
                "attraction2_comment": "水质超清，潜水能看珊瑚和热带鱼",
                "attraction3": "南山文化旅游区",
                "attraction3_price": "108",
                "attraction3_price_orig": "129",
                "attraction3_highlight": "108米南海观音、南山寺",
                "attraction3_comment": "海上观音像非常壮观，景区很大逛半天",
                "dinner_restaurant": "阿浪海鲜连锁",
                "dinner_feature": "明码标价不宰客的海鲜连锁品牌",
                "dinner_comment": "价格透明菜品新鲜，适合怕被宰的游客",
                "souvenirs": "椰子制品、热带水果干、珍珠饰品",
                "best_season": "10月-次年3月",
                "weather_tips": "全年防晒必备；7-9月台风季航班易取消"
            },
            "成都": {
                "breakfast_name": "甘食记肥肠粉",
                "breakfast_dish1": "肥肠粉",
                "breakfast_desc1": "红薯粉+肥肠+酸辣汤底",
                "breakfast_dish2": "红油抄手",
                "breakfast_desc2": "皮薄馅嫩，红油麻辣鲜香",
                "breakfast_comment": "成都人早上不吃清淡的，一碗肥肠粉辣醒一整天",
                "dessert": "冰粉",
                "high_end_restaurant": "大龙燚火锅",
                "high_end_feature": "成都人气火锅品牌，牛油锅底醇厚",
                "high_end_dish1": "鲜毛肚",
                "high_end_price1": "58-68/份",
                "high_end_desc1": "七上八下15秒，脆嫩爽口",
                "high_end_dish2": "极品鲜鸭肠",
                "high_end_price2": "38-48/份",
                "high_end_desc2": "涮10秒，脆弹有嚼劲",
                "high_end_dish3": "手工黑豆腐",
                "high_end_price3": "20-28/份",
                "high_end_desc3": "吸满汤汁嫩滑入味",
                "high_end_comment": "成都火锅必选牛油锅底，不能吃辣点鸳鸯锅",
                "mid_restaurant": "陈麻婆豆腐（总店）",
                "mid_feature": "川菜百年老字号，麻婆豆腐发源地",
                "mid_dish1": "陈麻婆豆腐",
                "mid_price1": "28-38/份",
                "mid_desc1": "麻辣烫香嫩，正宗成都味",
                "mid_dish2": "宫保鸡丁",
                "mid_price2": "38-48/份",
                "mid_desc2": "花生酥脆，鸡丁入味",
                "mid_comment": "来成都必吃正宗麻婆豆腐，这家是发源地老店",
                "snack1": "串串香",
                "snack1_price": "0.5-3/串",
                "snack1_desc": "自己选菜涮着吃",
                "snack2": "龙抄手",
                "snack2_price": "12-18/碗",
                "snack2_desc": "清汤配薄皮抄手",
                "snack3": "冰粉",
                "nightmarket_comment": "建设路小吃街是成都年轻人最爱逛的",
                "cuisine_type": "川菜/火锅",
                "landmark1": "春熙路/太古里",
                "attraction1": "宽窄巷子",
                "attraction1_price": "0",
                "attraction1_desc": "老成都慢生活，喝茶采耳逛小店",
                "attraction2": "成都大熊猫繁育研究基地",
                "attraction2_price": "52",
                "attraction2_price_orig": "55",
                "attraction2_highlight": "看大熊猫、小熊猫、熊猫幼崽",
                "attraction2_comment": "早上8点前到最好，熊猫活跃在吃竹子",
                "attraction3": "都江堰景区",
                "attraction3_price": "80",
                "attraction3_price_orig": "90",
                "attraction3_highlight": "两千年世界文化遗产水利工程",
                "attraction3_comment": "高铁30分钟到，景区不大但很值得",
                "dinner_restaurant": "蜀大侠火锅",
                "dinner_feature": "主打花千骨大骨头特色，拍照好看味道正",
                "dinner_comment": "招牌花千骨端上来很震撼",
                "souvenirs": "张飞牛肉、火锅底料、蜀绣",
                "best_season": "3-6月、9-11月",
                "weather_tips": "夏天闷热冬天阴冷，春秋最舒适"
            },
            "西安": {
                "breakfast_name": "贾三灌汤包子馆",
                "breakfast_dish1": "牛肉灌汤包",
                "breakfast_desc1": "皮薄汤多，先戳破吸汤再吃馅",
                "breakfast_dish2": "八宝稀饭",
                "breakfast_desc2": "配灌汤包一起喝，甜而不腻",
                "breakfast_comment": "回民街上最有名的灌汤包老店",
                "dessert": "甑糕",
                "high_end_restaurant": "老孙家饭庄",
                "high_end_feature": "百年老字号，羊肉泡馍招牌",
                "high_end_dish1": "优质羊肉泡馍",
                "high_end_price1": "45-58/碗",
                "high_end_desc1": "羊汤醇厚，自己掰馍越碎越入味",
                "high_end_dish2": "葫芦头泡馍",
                "high_end_price2": "35-45/碗",
                "high_end_desc2": "肥肠爱好者必点",
                "high_end_dish3": "biangbiang面",
                "high_end_price3": "18-25/碗",
                "high_end_desc3": "宽如裤带，油泼辣子香气扑鼻",
                "high_end_comment": "馍自己掰，越碎越入味，别嫌麻烦",
                "mid_restaurant": "魏家凉皮",
                "mid_feature": "西安连锁凉皮品牌，品质稳定价格实惠",
                "mid_dish1": "秘制凉皮",
                "mid_price1": "12-16/份",
                "mid_desc1": "爽滑筋道，辣油香醋调味绝",
                "mid_dish2": "肉夹馍",
                "mid_price2": "10-15/个",
                "mid_desc2": "腊汁肉+现打白吉馍，香酥多汁",
                "mid_comment": "凉皮+肉夹馍是西安经典组合，20块管饱",
                "snack1": "腊汁肉夹馍",
                "snack1_price": "10-18",
                "snack1_desc": "西安美食名片",
                "snack2": "羊肉串",
                "snack2_price": "5-10/串",
                "snack2_desc": "炭火现烤，孜然辣椒香",
                "snack3": "镜糕",
                "nightmarket_comment": "回民街小吃全，永兴坊更适合本地人口味",
                "cuisine_type": "陕菜/小吃",
                "landmark1": "钟鼓楼",
                "attraction1": "回民街",
                "attraction1_price": "0",
                "attraction1_desc": "美食一条街，边走边吃不重样",
                "attraction2": "秦始皇兵马俑博物馆",
                "attraction2_price": "120",
                "attraction2_price_orig": "150",
                "attraction2_highlight": "世界第八大奇迹",
                "attraction2_comment": "一定要请讲解员，不然只是看泥人",
                "attraction3": "华清宫",
                "attraction3_price": "110",
                "attraction3_price_orig": "120",
                "attraction3_highlight": "杨贵妃沐浴温泉，晚上看《长恨歌》",
                "attraction3_comment": "《长恨歌》演出是精华，提前一周订票",
                "dinner_restaurant": "长安大排档",
                "dinner_feature": "陕西菜合集连锁，古长安风格装修",
                "dinner_comment": "葫芦鸡外酥里嫩是必点招牌",
                "souvenirs": "绿豆糕、狗头枣、兵马俑摆件",
                "best_season": "3-5月、9-11月",
                "weather_tips": "冬天干冷夏天酷热，春秋温差大带外套"
            },
            "杭州": {
                "breakfast_name": "知味观（总店）",
                "breakfast_dish1": "猫耳朵",
                "breakfast_desc1": "软糯Q弹配火腿笋丁",
                "breakfast_dish2": "小笼包",
                "breakfast_desc2": "皮薄汁多，蘸醋吃鲜美",
                "breakfast_comment": "百年老字号，本地人办喜事都来这",
                "dessert": "桂花糕",
                "high_end_restaurant": "楼外楼（孤山路总店）",
                "high_end_feature": "西湖边百年老店，正宗杭帮菜代表",
                "high_end_dish1": "西湖醋鱼",
                "high_end_price1": "88-128",
                "high_end_desc1": "酸甜适口，西湖草鱼现做",
                "high_end_dish2": "东坡肉",
                "high_end_price2": "58-78/份",
                "high_end_desc2": "肥而不腻入口即化",
                "high_end_dish3": "龙井虾仁",
                "high_end_price3": "108-138",
                "high_end_desc3": "西湖龙井+鲜河虾仁",
                "high_end_comment": "西湖边吃饭景色一绝，建议提前排号",
                "mid_restaurant": "外婆家（湖滨店）",
                "mid_feature": "杭帮菜人气连锁，性价比超高",
                "mid_dish1": "茶香鸡",
                "mid_price1": "38-48/份",
                "mid_desc1": "龙井茶熏制鸡肉，清香扑鼻",
                "mid_dish2": "麻婆豆腐",
                "mid_price2": "15-20/份",
                "mid_desc2": "3块钱的豆腐不输大店",
                "mid_comment": "菜价良心到不敢信是景区店",
                "snack1": "葱包桧",
                "snack1_price": "5-8",
                "snack1_desc": "油条裹葱卷饼蘸甜面酱",
                "snack2": "定胜糕",
                "snack2_price": "3-5/个",
                "snack2_desc": "软糯米糕豆沙馅",
                "snack3": "吴山酥油饼",
                "nightmarket_comment": "胜利河美食街适合本地人口味",
                "cuisine_type": "杭帮菜",
                "landmark1": "西湖",
                "attraction1": "西湖景区",
                "attraction1_price": "0",
                "attraction1_desc": "断桥残雪、苏堤春晓，免费天花板",
                "attraction2": "灵隐寺",
                "attraction2_price": "45",
                "attraction2_price_orig": "75",
                "attraction2_highlight": "千年古刹，飞来峰石刻",
                "attraction2_comment": "早上去人少清静",
                "attraction3": "西溪国家湿地公园",
                "attraction3_price": "60",
                "attraction3_price_orig": "80",
                "attraction3_highlight": "坐摇橹船穿芦苇荡",
                "attraction3_comment": "远离喧嚣，适合放空发呆",
                "dinner_restaurant": "新白鹿餐厅",
                "dinner_feature": "杭州排队王，杭帮菜性价比天花板",
                "dinner_comment": "糖醋排条和蛋黄鸡翅必点",
                "souvenirs": "西湖龙井茶、丝绸、藕粉",
                "best_season": "3-5月、9-11月",
                "weather_tips": "夏天闷热梅雨，冬天湿冷"
            },
            "重庆": {
                "breakfast_name": "花市豌杂面",
                "breakfast_dish1": "豌杂面",
                "breakfast_desc1": "豌豆+杂酱+面条，重庆人灵魂早餐",
                "breakfast_dish2": "小面",
                "breakfast_desc2": "麻辣鲜香，一碗面辣醒一天",
                "breakfast_comment": "重庆人早上就吃辣，小面是续命神器",
                "dessert": "冰粉",
                "high_end_restaurant": "珮姐老火锅",
                "high_end_feature": "重庆排名第一老火锅，牛油锅底醇厚",
                "high_end_dish1": "鲜毛肚",
                "high_end_price1": "58-68/份",
                "high_end_desc1": "七上八下15秒，脆嫩爽口",
                "high_end_dish2": "麻辣牛肉",
                "high_end_price2": "48-58/份",
                "high_end_desc2": "腌制入味，涮完更香",
                "high_end_dish3": "手工虾滑",
                "high_end_price3": "38-48/份",
                "high_end_desc3": "虾肉含量高，Q弹鲜甜",
                "high_end_comment": "九宫格中间温度最高涮毛肚，不能吃辣点鸳鸯",
                "mid_restaurant": "好又来酸辣粉",
                "mid_feature": "重庆老牌酸辣粉，排队排到马路上",
                "mid_dish1": "酸辣粉",
                "mid_price1": "12-18/碗",
                "mid_desc1": "酸辣开胃，红薯粉Q弹",
                "mid_dish2": "凉糕",
                "mid_price2": "5-8/份",
                "mid_desc2": "吃完辣来碗凉糕解辣",
                "mid_comment": "酸辣粉配凉糕，一辣一甜绝了",
                "snack1": "小面",
                "snack1_price": "8-15",
                "snack1_desc": "不加浇头的麻辣面，越简单越见功夫",
                "snack2": "烤脑花",
                "snack2_price": "15-25",
                "snack2_desc": "蒜蓉辣酱烤猪脑花，嫩滑入味",
                "snack3": "糍粑",
                "nightmarket_comment": "九街是重庆年轻人夜生活聚集地",
                "cuisine_type": "火锅/江湖菜",
                "landmark1": "解放碑",
                "attraction1": "洪崖洞",
                "attraction1_price": "0",
                "attraction1_desc": "千与千寻同款夜景，11层吊脚楼",
                "attraction2": "武隆天生三桥",
                "attraction2_price": "95",
                "attraction2_price_orig": "125",
                "attraction2_highlight": "变形金刚取景地，天然石桥",
                "attraction2_comment": "景色壮观震撼，穿运动鞋",
                "attraction3": "磁器口古镇",
                "attraction3_price": "0",
                "attraction3_price_orig": "0",
                "attraction3_highlight": "千年古镇，陈麻花必买",
                "attraction3_comment": "工作日去体验好，周末人太多",
                "dinner_restaurant": "纸盐河码头火锅",
                "dinner_feature": "洪崖洞旁，边看江景边吃火锅",
                "dinner_comment": "嘉陵江夜景+火锅，氛围绝了",
                "souvenirs": "火锅底料、陈麻花、合川桃片",
                "best_season": "3-5月、9-11月",
                "weather_tips": "夏天火炉40°C，冬天湿冷"
            },
            "北京": {
                "breakfast_name": "护国寺小吃",
                "breakfast_dish1": "豆汁配焦圈",
                "breakfast_desc1": "老北京特色，酸中带臭配焦圈绝了",
                "breakfast_dish2": "炒肝",
                "breakfast_desc2": "浓稠勾芡配大蒜，用碗沿转着喝",
                "breakfast_comment": "豆汁有人爱有人恨，但来北京不尝就白来了",
                "dessert": "驴打滚",
                "high_end_restaurant": "四季民福（故宫店）",
                "high_end_feature": "一边看故宫角楼一边吃烤鸭，人气第一",
                "high_end_dish1": "北京烤鸭",
                "high_end_price1": "238-298/只",
                "high_end_desc1": "果木挂炉烤制，皮脆肉嫩",
                "high_end_dish2": "芥末鸭掌",
                "high_end_price2": "48-58/份",
                "high_end_desc2": "冲鼻子但越吃越上头",
                "high_end_dish3": "火燎鸭心",
                "high_end_price3": "48-58/份",
                "high_end_desc3": "烤鸭副产品精品，脆嫩可口",
                "high_end_comment": "烤鸭配蒜泥甜面酱葱丝卷饼。故宫店要排队2小时+",
                "mid_restaurant": "南门涮肉",
                "mid_feature": "老北京铜锅涮肉代表，清水锅底+芝麻酱",
                "mid_dish1": "手切鲜羊肉",
                "mid_price1": "58-78/盘",
                "mid_desc1": "肉质鲜嫩，蘸芝麻酱入口即化",
                "mid_dish2": "烧饼",
                "mid_price2": "3-5/个",
                "mid_desc2": "配涮肉吃，外酥里软",
                "mid_comment": "北京冬天的仪式感就是铜锅涮肉配二锅头",
                "snack1": "卤煮火烧",
                "snack1_price": "25-35",
                "snack1_desc": "火烧+猪肺+肥肠，老北京平民美食",
                "snack2": "爆肚",
                "snack2_price": "30-40",
                "snack2_desc": "毛肚焯水蘸芝麻酱，脆嫩爽口",
                "snack3": "糖葫芦",
                "nightmarket_comment": "簋街是北京夜宵街，麻小和烤串为主",
                "cuisine_type": "京菜",
                "landmark1": "天安门广场",
                "attraction1": "故宫博物院",
                "attraction1_price": "60",
                "attraction1_desc": "明清皇宫，世界五大宫殿之首",
                "attraction2": "八达岭长城",
                "attraction2_price": "40",
                "attraction2_price_orig": "45",
                "attraction2_highlight": "不到长城非好汉",
                "attraction2_comment": "坐S2线火车去最方便",
                "attraction3": "颐和园",
                "attraction3_price": "30",
                "attraction3_price_orig": "50",
                "attraction3_highlight": "皇家园林、昆明湖、长廊",
                "attraction3_comment": "逛半天，昆明湖边散步很惬意",
                "dinner_restaurant": "大董烤鸭店",
                "dinner_feature": "高端烤鸭，酥不腻是招牌",
                "dinner_comment": "比四季民福贵但更精致",
                "souvenirs": "稻香村糕点、果脯、北京酥糖",
                "best_season": "4-5月、9-10月",
                "weather_tips": "冬天干冷零下10度，夏天闷热35度+"
            },
            "上海": {
                "breakfast_name": "大壶春（四川中路店）",
                "breakfast_dish1": "生煎馒头",
                "breakfast_desc1": "底焦脆金黄，咬一口汁水四溅",
                "breakfast_dish2": "咖喱牛肉汤",
                "breakfast_desc2": "配生煎一起喝，上海早餐标配",
                "breakfast_comment": "百年老店，生煎底脆汁烫才正宗",
                "dessert": "蟹壳黄",
                "high_end_restaurant": "南京大牌档",
                "high_end_feature": "民国风复古装修，菜品全面量大",
                "high_end_dish1": "盐水鸭",
                "high_end_price1": "38-58/份",
                "high_end_desc1": "皮白肉嫩咸香适中",
                "high_end_dish2": "狮子头",
                "high_end_price2": "28-38/份",
                "high_end_desc2": "入口即化，红烧汤汁浓郁",
                "high_end_dish3": "美龄粥",
                "high_end_price3": "15-22/碗",
                "high_end_desc3": "豆浆山药粥，甜糯养胃",
                "high_end_comment": "民国复古风，菜量大价格合理",
                "mid_restaurant": "小杨生煎（吴江路总店）",
                "mid_feature": "上海最火生煎品牌",
                "mid_dish1": "鲜肉生煎",
                "mid_price1": "8-12/4个",
                "mid_desc1": "经典款，汁水足底脆香",
                "mid_dish2": "虾仁生煎",
                "mid_price2": "15-20/4个",
                "mid_desc2": "整颗虾仁包里面，鲜上加鲜",
                "mid_comment": "来上海必吃小杨生煎，便宜好吃管饱",
                "snack1": "生煎馒头",
                "snack1_price": "8-15",
                "snack1_desc": "底脆汁多小心烫嘴",
                "snack2": "葱油拌面",
                "snack2_price": "10-15",
                "snack2_desc": "葱油焦香，每根面裹着酱汁",
                "snack3": "排骨年糕",
                "nightmarket_comment": "云南南路小吃街种类多",
                "cuisine_type": "本帮菜",
                "landmark1": "外滩",
                "attraction1": "外滩",
                "attraction1_price": "0",
                "attraction1_desc": "万国建筑+浦东天际线，上海名片",
                "attraction2": "上海迪士尼乐园",
                "attraction2_price": "399",
                "attraction2_price_orig": "475",
                "attraction2_highlight": "全球最大奇幻童话城堡",
                "attraction2_comment": "提前下载APP抢快速通行证，周二三人最少",
                "attraction3": "豫园/城隍庙",
                "attraction3_price": "30",
                "attraction3_price_orig": "40",
                "attraction3_highlight": "明代古典园林、九曲桥",
                "attraction3_comment": "园林精致值得看，城隍庙小吃偏贵",
                "dinner_restaurant": "老吉士酒家",
                "dinner_feature": "本帮菜老牌，浓油赤酱特色",
                "dinner_comment": "红烧肉和草头圈子是本帮精髓，偏甜",
                "souvenirs": "大白兔奶糖、国际饭店蝴蝶酥、城隍庙五香豆",
                "best_season": "3-5月、9-11月",
                "weather_tips": "夏天闷热黄梅天，冬天湿冷"
            },
            "长沙": {
                "breakfast_name": "文和友",
                "breakfast_dish1": "长沙米粉",
                "breakfast_desc1": "扁粉圆粉任选，浇头丰富",
                "breakfast_dish2": "糖油粑粑",
                "breakfast_desc2": "糯米炸到金黄，外脆里糯",
                "breakfast_comment": "长沙人嗦粉嗦出了文化",
                "dessert": "茶颜悦色",
                "high_end_restaurant": "炊烟小炒黄牛肉",
                "high_end_feature": "长沙湘菜头牌，排队2-3小时",
                "high_end_dish1": "小炒黄牛肉",
                "high_end_price1": "68-88/份",
                "high_end_desc1": "鲜嫩牛肉配小米辣爆炒",
                "high_end_dish2": "剁椒鱼头",
                "high_end_price2": "88-108/份",
                "high_end_desc2": "大花鲢鱼头配剁椒蒸制",
                "high_end_dish3": "农家小炒肉",
                "high_end_price3": "48-58/份",
                "high_end_desc3": "辣椒炒五花肉，湖南人白月光",
                "high_end_comment": "排队常态，建议美团提前取号",
                "mid_restaurant": "黑色经典臭豆腐",
                "mid_feature": "长沙臭豆腐连锁品牌",
                "mid_dish1": "经典臭豆腐",
                "mid_price1": "15-20/份",
                "mid_desc1": "外焦里嫩，闻着臭吃着香",
                "mid_dish2": "烤肠",
                "mid_price2": "10-15/份",
                "mid_desc2": "配臭豆腐一起吃",
                "mid_comment": "臭豆腐趁热吃，凉了就不好吃了",
                "snack1": "臭豆腐",
                "snack1_price": "15-20",
                "snack1_desc": "闻着臭吃着香",
                "snack2": "糖油粑粑",
                "snack2_price": "5-10",
                "snack2_desc": "外酥里软甜而不腻",
                "snack3": "茶颜悦色",
                "nightmarket_comment": "太平街和坡子街最热闹",
                "cuisine_type": "湘菜",
                "landmark1": "太平街",
                "attraction1": "橘子洲头",
                "attraction1_price": "0",
                "attraction1_desc": "毛主席青年雕塑，湘江中央绿洲",
                "attraction2": "岳麓山",
                "attraction2_price": "0",
                "attraction2_price_orig": "0",
                "attraction2_highlight": "爱晚亭、岳麓书院、俯瞰全城",
                "attraction2_comment": "秋天枫叶红了最美",
                "attraction3": "湖南省博物馆",
                "attraction3_price": "0",
                "attraction3_price_orig": "0",
                "attraction3_highlight": "辛追夫人（马王堆汉墓）",
                "attraction3_comment": "免费但提前预约，周一闭馆",
                "dinner_restaurant": "费大厨辣椒炒肉",
                "dinner_feature": "辣椒炒肉专门店，全国出名",
                "dinner_comment": "辣椒炒肉看着简单，这家是天花板",
                "souvenirs": "灯芯糕、酱板鸭、茶颜悦色周边",
                "best_season": "3-5月、9-11月",
                "weather_tips": "夏天闷热（火炉），冬天湿冷"
            },
        }

        # 默认数据：使用全国连锁品牌+通用真实建议
        default_data = {
            "breakfast_name": "当地评分最高的早餐店",
            "breakfast_dish1": "当地特色早餐",
            "breakfast_desc1": "到了先问酒店前台推荐",
            "breakfast_dish2": "包子/粉面/粥",
            "breakfast_desc2": "中式早餐经典组合",
            "breakfast_comment": "打开大众点评搜'早餐'按评分排序，选4.5分以上的",
            "dessert": "当地甜品",
            "high_end_restaurant": "大众点评排名第一的当地菜",
            "high_end_feature": "大众点评搜本地菜按口味排序选前3",
            "high_end_dish1": "当地招牌菜",
            "high_end_price1": "时价",
            "high_end_desc1": "到店问服务员推荐",
            "high_end_dish2": "当地特色菜",
            "high_end_price2": "时价",
            "high_end_desc2": "点评收藏数最高的菜品",
            "high_end_dish3": "时令推荐",
            "high_end_price3": "时价",
            "high_end_desc3": "问服务员当季推荐",
            "high_end_comment": "大众点评搜目的地+菜系，按口味排序选前3名",
            "mid_restaurant": "酒店附近评分最高的餐厅",
            "mid_feature": "本地人常去的老店",
            "mid_dish1": "当地主食",
            "mid_price1": "20-40",
            "mid_desc1": "分量足味道正",
            "mid_dish2": "特色小菜",
            "mid_price2": "15-25",
            "mid_desc2": "搭配主食一起吃",
            "mid_comment": "选大众点评4.0分以上、评价500+条的店",
            "snack1": "当地小吃",
            "snack1_price": "10-20",
            "snack1_desc": "到夜市问摊主什么最受欢迎",
            "snack2": "烧烤/串串",
            "snack2_price": "2-5/串",
            "snack2_desc": "人多的摊位去排队",
            "snack3": "当地饮品",
            "nightmarket_comment": "搜'目的地+夜市'，选本地人推荐的",
            "cuisine_type": "当地菜",
            "landmark1": "市中心地标",
            "attraction1": "当地最知名景点",
            "attraction1_price": "0-50",
            "attraction1_desc": "美团门票提前一天订更便宜",
            "attraction2": "当地必去景点",
            "attraction2_price": "50-100",
            "attraction2_price_orig": "80-120",
            "attraction2_highlight": "美团提前订票省20-30%",
            "attraction2_comment": "小红书搜'目的地+攻略'看真实评价",
            "attraction3": "当地特色体验",
            "attraction3_price": "50-100",
            "attraction3_price_orig": "80-150",
            "attraction3_highlight": "体验当地文化特色",
            "attraction3_comment": "提前做功课，避开节假日",
            "dinner_restaurant": "当地口碑餐厅",
            "dinner_feature": "大众点评搜'晚餐'选评分最高",
            "dinner_comment": "晚餐选人多的店，排队说明味道好",
            "souvenirs": "当地特产（去超市买比景区便宜一半）",
            "best_season": "春秋两季",
            "weather_tips": "出行前查天气预报，带好雨具和防晒"
        }

        return city_database.get(city, default_data)

    def _generate_mock(self, query: str, mode: str) -> str:
        """生成离线攻略（AI不可用时的备用方案）"""
        from prompts.wildtrip_prompt import extract_city_name
        city = extract_city_name(query)
        city_data = self._get_city_data(city)

        offline_notice = ""
        if city == "目的地":
            offline_notice = "\n> ⚠️ **提示：** 当前为离线模式，无法识别具体城市。以下为通用旅行建议，请用大众点评搜索当地美食和景点。\n\n---\n\n"

        if mode == 'hotel':
            return self._mock_hotel(city, city_data, offline_notice)
        elif mode == 'food':
            return self._mock_food(city, city_data, offline_notice)
        else:
            return self._mock_full(city, city_data, offline_notice)

    def _mock_hotel(self, city, d, notice):
        return f"""# 🏨 {city}住宿推荐 - 野游记精选

{notice}### 1. 品质之选：亚朵酒店 ⭐⭐⭐⭐
- **价格：** ¥350-500/晚
- **位置：** {city}市中心交通便利地段
- **设施：** 大床房、丰富早餐、健身房、竹居图书馆
- **野导游说：** 亚朵品控国内顶级，床品舒服，早餐丰富，服务态度好
- **预订：** [美团预订](占位)

### 2. 性价比之选：全季酒店 ⭐⭐⭐⭐
- **价格：** ¥200-350/晚
- **位置：** {city}市区交通方便
- **设施：** 标准房、含早餐、WiFi
- **野导游说：** 90%的人选全季不会错，干净整洁隔音好
- **预订：** [美团预订](占位)

### 3. 经济之选：汉庭酒店 ⭐⭐⭐
- **价格：** ¥120-200/晚
- **位置：** {city}市区
- **设施：** 标准间、24h热水、WiFi
- **野导游说：** 3.0版升级后品质提升不少，省钱吃好的更香
- **预订：** [美团预订](占位)

---
## 💡 省钱秘籍
1. 提前7天订便宜10-20%
2. 工作日比周末便宜20-30%
3. 华住/亚朵会员打9折起
"""

    def _mock_food(self, city, d, notice):
        return f"""# 🍜 {city}美食地图 - 野游记推荐

{notice}## ☀️ 早餐

### {d['breakfast_name']} ⭐4.8
- **区域：** {city}老城区一带
- **招牌：** {d['breakfast_dish1']}（¥12-18）、{d['breakfast_dish2']}（¥8-12）
- **野导游说：** {d['breakfast_comment']}
- **团购：** [美团搜索](占位)

## 🍖 正餐

### 品质之选：{d['high_end_restaurant']} ⭐4.7
- **区域：** {city}市中心一带
- **特色：** {d['high_end_feature']}
- **招牌：** {d['high_end_dish1']}（¥{d['high_end_price1']}）、{d['high_end_dish2']}（¥{d['high_end_price2']}）
- **野导游说：** {d['high_end_comment']}
- **团购：** [美团团购](占位)

### 性价比之选：{d['mid_restaurant']} ⭐4.9
- **特色：** {d['mid_feature']}
- **招牌：** {d['mid_dish1']}（¥{d['mid_price1']}）、{d['mid_dish2']}（¥{d['mid_price2']}）
- **野导游说：** {d['mid_comment']}
- **团购：** [美团团购](占位)

## 💸 小吃夜市
- {d['snack1']}（¥{d['snack1_price']}）- {d['snack1_desc']}
- {d['snack2']}（¥{d['snack2_price']}）- {d['snack2_desc']}
- {d['nightmarket_comment']}
"""

    def _mock_full(self, city, d, notice):
        return f"""# 🔥 {city}3天2晚攻略 - 野游记出品

{notice}> **不走寻常路，就走野路子**

## 📋 行程概览
| 项目 | 内容 |
|------|------|
| 🗓️ 天数 | 3天2晚 |
| 💰 预算 | ¥1500-2500/人 |
| 🌤️ 最佳时节 | {d['best_season']} |

---

## 🗓️ Day 1：抵达 + 市区探索

| 时间 | 活动 | 费用 |
|------|------|------|
| 09:00 | ✈️ 抵达{city} | - |
| 10:00 | 🏨 入住全季/亚朵酒店 | ¥250-400/晚 |
| 11:00 | 🏛️ {d['landmark1']} | 免费 |
| 12:30 | 🍜 午餐：{d['breakfast_name']} | ¥15-25/人 |
| 18:30 | 🍲 晚餐：{d['high_end_restaurant']} | ¥100-200/人 |
| 20:30 | 🌃 逛夜市 | ¥30/人 |

#### 🍽️ Day 1 美食

**午餐：{d['breakfast_name']}**
- **区域：** {city}老城区一带
- **人均：** ¥15-25
- **必点：** {d['breakfast_dish1']}、{d['dessert']}
- **野导游说：** {d['breakfast_comment']}
- **团购：** [美团搜索](占位)

**晚餐：{d['high_end_restaurant']}**
- **区域：** {city}市中心一带
- **人均：** ¥100-200
- **必点：** {d['high_end_dish1']}（¥{d['high_end_price1']}）、{d['high_end_dish2']}（¥{d['high_end_price2']}）
- **野导游说：** {d['high_end_comment']}
- **团购：** [美团团购](占位)

---

## 🗓️ Day 2：{d['attraction1']} + {d['attraction2']}

| 时间 | 活动 | 费用 |
|------|------|------|
| 09:00 | 🏛️ {d['attraction1']} | ¥{d['attraction1_price']}/人 |
| 12:00 | 🍜 {d['mid_restaurant']} | ¥30-60/人 |
| 14:00 | 🌄 {d['attraction2']} | ¥{d['attraction2_price']}/人 |
| 18:30 | 🍲 {d['dinner_restaurant']} | ¥60-100/人 |

**{d['attraction2']}**
- **美团价：** ¥{d['attraction2_price']}（原价¥{d['attraction2_price_orig']}）
- **亮点：** {d['attraction2_highlight']}
- **野导游说：** {d['attraction2_comment']}
- **订票：** [美团门票](占位)

**午餐：{d['mid_restaurant']}**
- **特色：** {d['mid_feature']}
- **必点：** {d['mid_dish1']}（¥{d['mid_price1']}）
- **野导游说：** {d['mid_comment']}
- **团购：** [美团团购](占位)

**晚餐：{d['dinner_restaurant']}**
- **特色：** {d['dinner_feature']}
- **野导游说：** {d['dinner_comment']}
- **团购：** [美团团购](占位)

---

## 🗓️ Day 3：{d['attraction3']} + 返程

| 时间 | 活动 | 费用 |
|------|------|------|
| 09:00 | {d['attraction3']} | ¥{d['attraction3_price']}/人 |
| 14:00 | 🛍️ 买特产 | ¥100 |
| 16:00 | ✈️ 返程 | - |

**{d['attraction3']}**
- **美团价：** ¥{d['attraction3_price']}（原价¥{d['attraction3_price_orig']}）
- **亮点：** {d['attraction3_highlight']}
- **野导游说：** {d['attraction3_comment']}
- **订票：** [美团门票](占位)

---

## 🏨 住宿推荐

### 推荐：全季酒店 ⭐⭐⭐⭐
- **价格：** ¥200-350/晚 × 2晚
- **位置：** {city}市中心，交通方便
- **野导游说：** 性价比最高，干净舒适，90%的人选这个不会错
- **预订：** [美团预订](占位)

---

## 💰 费用明细（人均）
| 项目 | 金额 |
|------|------|
| 🏨 住宿 | ¥500-700 |
| 🍽️ 餐饮 | ¥400-600 |
| 🎫 门票 | ¥150-300 |
| 🚗 交通 | ¥150-200 |
| **💰 总计** | **¥1300-2000** |

## 💡 省钱秘籍
1. 美团团购餐饮省30%，门票提前订省20%
2. 工作日入住酒店便宜20-30%
3. 特产去超市买，比景区便宜一半

## 🎒 行前清单
防晒霜、运动鞋、肠胃药、充电宝、美团/大众点评/高德地图

**🌤️ 天气：** {d['best_season']} | {d['weather_tips']}

**🎁 特产推荐：** {d['souvenirs']}（去超市买）

---
**🔥 不走寻常路，就走野路子 😎**
"""
