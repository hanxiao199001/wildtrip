"""
AI生成引擎
支持DeepSeek/Claude/OpenAI等模型
"""

from loguru import logger
import os


class AIEngine:
    """AI内容生成引擎"""
    
    def __init__(self):
        """初始化AI引擎"""
        self.api_key = os.getenv('AI_API_KEY', '')
        self.base_url = os.getenv('AI_BASE_URL', 'https://api.deepseek.com')
        self.model = os.getenv('AI_MODEL', 'deepseek-chat')
        
        if not self.api_key:
            logger.warning("⚠️ AI_API_KEY未配置，将使用Mock数据")
            self.use_mock = True
        else:
            self.use_mock = False
            logger.info(f"✅ AI引擎初始化完成 | 模型: {self.model}")
    
    def generate(self, prompt: str, query: str, mode: str = 'full') -> str:
        """
        生成攻略内容
        
        Args:
            prompt: 完整的prompt（包含system + user）
            query: 用户原始查询
            mode: 生成模式
            
        Returns:
            生成的攻略内容（Markdown格式）
        """
        if self.use_mock:
            logger.info(f"🔧 使用Mock数据生成（mode={mode}）")
            return self._generate_mock(query, mode)
        
        try:
            import openai
            
            # 分离system和user prompt
            parts = prompt.split('\n\n', 1)
            system_prompt = parts[0] if len(parts) > 1 else ""
            user_prompt = parts[1] if len(parts) > 1 else prompt
            
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            logger.info(f"🤖 调用AI模型: {self.model}")
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            logger.info(f"✅ AI生成完成 | 字数: {len(content)}")
            
            return content
            
        except Exception as e:
            logger.error(f"❌ AI生成失败: {e}")
            logger.info("🔧 回退到Mock数据")
            return self._generate_mock(query, mode)

    def _get_city_data(self, city: str) -> dict:
        """
        获取不同城市的特色数据，用于生成个性化Mock攻略
        """
        # 城市特色数据库
        city_database = {
            "海口": {
                "breakfast_name": "海南粉老店",
                "breakfast_dish1": "海南粉",
                "breakfast_desc1": "汤底鲜美，配料10+种",
                "breakfast_dish2": "清补凉",
                "breakfast_desc2": "椰奶底，料足，冰冰凉凉",
                "breakfast_comment": "粉汤是骨头汤熬的，配料有花生、酸菜、豆芽、牛肉干",
                "dessert": "清补凉",
                "high_end_restaurant": "老渔港海鲜酒楼",
                "high_end_feature": "活海鲜现捞现做，明码标价不宰客",
                "high_end_dish1": "清蒸石斑鱼",
                "high_end_price1": "120/斤",
                "high_end_desc1": "肉质鲜嫩，原汁原味",
                "high_end_dish2": "椒盐濑尿虾",
                "high_end_price2": "80/份",
                "high_end_desc2": "个头大，肉饱满",
                "high_end_dish3": "椰子饭",
                "high_end_price3": "38",
                "high_end_desc3": "必点配菜，椰香浓郁",
                "high_end_comment": "老板自己有渔船，海鲜都是当天打捞的",
                "mid_restaurant": "文昌鸡饭老店",
                "mid_feature": "海南四大名菜之首，本地人都说正宗",
                "mid_dish1": "白切文昌鸡",
                "mid_price1": "68/半只",
                "mid_desc1": "皮脆肉滑，蘸料绝了",
                "mid_dish2": "鸡油饭",
                "mid_price2": "5/碗",
                "mid_desc2": "用鸡汤和鸡油煮的饭，粒粒分明",
                "mid_comment": "鸡肉滑嫩，鸡皮爽脆，蘸料是秘制的",
                "snack1": "清补凉",
                "snack1_price": "8-12",
                "snack1_desc": "10多种配料，椰奶冰沙底",
                "snack2": "煎饺",
                "snack2_price": "8/份",
                "snack2_desc": "皮薄馅大，外焦里嫩",
                "snack3": "炒冰",
                "nightmarket_comment": "清补凉有7-8家，都好吃，随便选",
                "cuisine_type": "海鲜",
                "landmark1": "骑楼老街",
                "attraction1": "骑楼老街",
                "attraction1_price": "0",
                "attraction1_desc": "拍照打卡，感受南洋风情",
                "attraction2": "火山口地质公园",
                "attraction2_price": "60",
                "attraction2_price_orig": "80",
                "attraction2_highlight": "万年火山口、热带植物、熔岩隧道",
                "attraction2_comment": "爬到火山口顶能看全景，拍照超震撼",
                "attraction3": "热带野生动植物园",
                "attraction3_price": "80",
                "attraction3_price_orig": "120",
                "attraction3_highlight": "看老虎狮子、喂长颈鹿、热带植物",
                "attraction3_comment": "亲子游必去！孩子超喜欢，动物种类多",
                "dinner_restaurant": "椰子鸡火锅",
                "dinner_feature": "用椰子水煮鸡，清甜养生",
                "dinner_comment": "椰子水做汤底，鸡肉嫩滑，不辣不油",
                "souvenirs": "椰子糖、咖啡、黄辣椒酱",
                "best_season": "11月-次年4月（避开台风季）",
                "weather_tips": "7-9月台风多，航班易取消；带伞防阵雨"
            },
            "三亚": {
                "breakfast_name": "港门粉店",
                "breakfast_dish1": "港门粉",
                "breakfast_desc1": "海鲜汤底，鲜美无比",
                "breakfast_dish2": "椰子饭",
                "breakfast_desc2": "椰香浓郁，软糯可口",
                "breakfast_comment": "用海鲜熬的汤底，加虾仁、蟹肉，鲜得掉眉毛",
                "dessert": "椰奶冻",
                "high_end_restaurant": "第一市场海鲜加工",
                "high_end_feature": "自己买海鲜，加工费便宜",
                "high_end_dish1": "龙虾刺身",
                "high_end_price1": "180/斤",
                "high_end_desc1": "新鲜得还在动",
                "high_end_dish2": "和乐蟹",
                "high_end_price2": "120/斤",
                "high_end_desc2": "三亚四大名菜之一，膏肥肉厚",
                "high_end_dish3": "蒜蓉粉丝蒸扇贝",
                "high_end_price3": "5/只",
                "high_end_desc3": "蒜香十足，肉质鲜嫩",
                "high_end_comment": "自己去市场挑海鲜，找靠谱的店加工",
                "mid_restaurant": "抱罗粉老店",
                "mid_feature": "海南特色粉，汤底清甜",
                "mid_dish1": "抱罗粉",
                "mid_price1": "15/碗",
                "mid_desc1": "粉滑汤鲜，配料丰富",
                "mid_dish2": "陵水酸粉",
                "mid_price2": "12/碗",
                "mid_desc2": "酸辣开胃，夏天首选",
                "mid_comment": "粉是手工做的，汤底用大骨熬了8小时",
                "snack1": "椰子冻",
                "snack1_price": "15",
                "snack1_desc": "整个椰子挖空，里面是椰奶冻",
                "snack2": "芒果肠粉",
                "snack2_price": "12/份",
                "snack2_desc": "甜品创新，芒果配肠粉皮",
                "snack3": "椰子鸡",
                "nightmarket_comment": "海鲜大排档一条街，价格透明",
                "cuisine_type": "海鲜",
                "landmark1": "亚龙湾",
                "attraction1": "亚龙湾海滩",
                "attraction1_price": "0",
                "attraction1_desc": "天下第一湾，沙滩细腻",
                "attraction2": "蜈支洲岛",
                "attraction2_price": "144",
                "attraction2_price_orig": "168",
                "attraction2_highlight": "潜水天堂、情人桥、海上项目",
                "attraction2_comment": "水质超清，潜水能看到珊瑚和鱼群",
                "attraction3": "天涯海角",
                "attraction3_price": "68",
                "attraction3_price_orig": "95",
                "attraction3_highlight": "天涯石、海角石、历史文化",
                "attraction3_comment": "打卡胜地，拍照留念必去",
                "dinner_restaurant": "海南四大名菜餐厅",
                "dinner_feature": "一次吃齐文昌鸡、和乐蟹、东山羊、加积鸭",
                "dinner_comment": "四大名菜都能尝到，适合游客打卡",
                "souvenirs": "椰子制品、珍珠饰品、热带水果干",
                "best_season": "10月-次年3月（避开台风季）",
                "weather_tips": "夏天很晒，防晒必备；7-9月台风季慎行"
            },
            "成都": {
                "breakfast_name": "红油抄手店",
                "breakfast_dish1": "红油抄手",
                "breakfast_desc1": "皮薄馅嫩，红油香辣",
                "breakfast_dish2": "担担面",
                "breakfast_desc2": "麻辣鲜香，芝麻酱底",
                "breakfast_comment": "抄手皮是现包的，红油是店家秘制",
                "dessert": "冰粉",
                "high_end_restaurant": "川菜馆子",
                "high_end_feature": "正宗川菜，麻辣鲜香",
                "high_end_dish1": "水煮牛肉",
                "high_end_price1": "68",
                "high_end_desc1": "麻辣鲜香，牛肉嫩滑",
                "high_end_dish2": "宫保鸡丁",
                "high_end_price2": "48",
                "high_end_desc2": "花生酥脆，鸡丁入味",
                "high_end_dish3": "麻婆豆腐",
                "high_end_price3": "28",
                "high_end_desc3": "麻辣烫香，下饭神器",
                "high_end_comment": "川菜必吃，辣得过瘾但不是干辣",
                "mid_restaurant": "老妈蹄花店",
                "mid_feature": "成都名小吃，软糯入味",
                "mid_dish1": "老妈蹄花",
                "mid_price1": "38/份",
                "mid_desc1": "炖得软烂，胶原蛋白满满",
                "mid_dish2": "钟水饺",
                "mid_price2": "15/份",
                "mid_desc2": "甜辣口，皮薄馅鲜",
                "mid_comment": "蹄花炖了6小时，筷子一夹就散",
                "snack1": "串串香",
                "snack1_price": "0.5-2/串",
                "snack1_desc": "自己选菜涮着吃",
                "snack2": "龙抄手",
                "snack2_price": "12/碗",
                "snack2_desc": "清汤底，鲜美爽口",
                "snack3": "冰粉",
                "nightmarket_comment": "串串香一条街，随便选都好吃",
                "cuisine_type": "川菜",
                "landmark1": "宽窄巷子",
                "attraction1": "宽窄巷子",
                "attraction1_price": "0",
                "attraction1_desc": "体验老成都生活，喝茶掏耳朵",
                "attraction2": "大熊猫繁育研究基地",
                "attraction2_price": "52",
                "attraction2_price_orig": "55",
                "attraction2_highlight": "看大熊猫、小熊猫、熊猫幼崽",
                "attraction2_comment": "早上8点去最好，熊猫活跃，还能看到吃竹子",
                "attraction3": "都江堰",
                "attraction3_price": "80",
                "attraction3_price_orig": "90",
                "attraction3_highlight": "世界文化遗产、两千年水利工程",
                "attraction3_comment": "感受古人智慧，景色也很美",
                "dinner_restaurant": "火锅店",
                "dinner_feature": "正宗成都火锅，麻辣底料",
                "dinner_comment": "九宫格必点，鸳鸯锅适合不能吃辣的",
                "souvenirs": "火锅底料、郫县豆瓣酱、蜀绣",
                "best_season": "3-6月、9-11月（春秋最佳）",
                "weather_tips": "夏天热冬天阴，带一件薄外套"
            },
            "西安": {
                "breakfast_name": "肉夹馍老店",
                "breakfast_dish1": "肉夹馍",
                "breakfast_desc1": "馍酥肉烂，汁水丰富",
                "breakfast_dish2": "凉皮",
                "breakfast_desc2": "爽滑筋道，辣香开胃",
                "breakfast_comment": "馍是现打的，肉是炖了一夜的腊汁肉",
                "dessert": "甑糕",
                "high_end_restaurant": "羊肉泡馍馆",
                "high_end_feature": "西安名吃，掰馍自己动手",
                "high_end_dish1": "羊肉泡馍",
                "high_end_price1": "38/碗",
                "high_end_desc1": "羊汤鲜美，肉烂馍筋",
                "high_end_dish2": "葫芦头泡馍",
                "high_end_price2": "32/碗",
                "high_end_desc2": "肥肠爱好者必点",
                "high_end_dish3": "biangbiang面",
                "high_end_price3": "18",
                "high_end_desc3": "宽如裤带，劲道十足",
                "high_end_comment": "馍要自己掰，越碎越入味",
                "mid_restaurant": "老孙家泡馍",
                "mid_feature": "百年老店，汤底醇厚",
                "mid_dish1": "优质羊肉泡",
                "mid_price1": "48/碗",
                "mid_desc1": "肉量足，汤鲜美",
                "mid_dish2": "酸汤水饺",
                "mid_price2": "22/份",
                "mid_desc2": "酸辣开胃",
                "mid_comment": "老字号，味道稳定，不踩雷",
                "snack1": "肉夹馍",
                "snack1_price": "12-18",
                "snack1_desc": "腊汁肉+白吉馍，绝配",
                "snack2": "臊子面",
                "snack2_price": "15/碗",
                "snack2_desc": "酸辣鲜香，面条劲道",
                "snack3": "镜糕",
                "nightmarket_comment": "回民街虽然游客多但小吃全",
                "cuisine_type": "陕菜",
                "landmark1": "回民街",
                "attraction1": "回民街",
                "attraction1_price": "0",
                "attraction1_desc": "小吃天堂，边走边吃",
                "attraction2": "兵马俑",
                "attraction2_price": "120",
                "attraction2_price_orig": "150",
                "attraction2_highlight": "世界第八大奇迹、秦始皇陵",
                "attraction2_comment": "震撼！一定要请讲解，不然看不懂",
                "attraction3": "华清宫",
                "attraction3_price": "110",
                "attraction3_price_orig": "120",
                "attraction3_highlight": "杨贵妃洗澡的地方、长恨歌演出",
                "attraction3_comment": "晚上看长恨歌演出超震撼",
                "dinner_restaurant": "陕西菜馆",
                "dinner_feature": "葫芦鸡、红烧牛尾等陕菜",
                "dinner_comment": "葫芦鸡外酥里嫩，必点",
                "souvenirs": "肉夹馍底料、臊子面调料、兵马俑纪念品",
                "best_season": "3-5月、9-11月（春秋最佳）",
                "weather_tips": "冬天冷夏天热，春秋舒适"
            },
            "杭州": {
                "breakfast_name": "片儿川面馆",
                "breakfast_dish1": "片儿川",
                "breakfast_desc1": "笋片肉片，鲜美清淡",
                "breakfast_dish2": "小笼包",
                "breakfast_desc2": "皮薄汁多，鲜香可口",
                "breakfast_comment": "杭州特色面，笋片是灵魂",
                "dessert": "桂花糕",
                "high_end_restaurant": "楼外楼",
                "high_end_feature": "百年老店，正宗杭帮菜",
                "high_end_dish1": "西湖醋鱼",
                "high_end_price1": "88",
                "high_end_desc1": "酸甜适口，鱼肉鲜嫩",
                "high_end_dish2": "东坡肉",
                "high_end_price2": "68",
                "high_end_desc2": "肥而不腻，入口即化",
                "high_end_dish3": "龙井虾仁",
                "high_end_price3": "128",
                "high_end_desc3": "茶香虾鲜，清爽可口",
                "high_end_comment": "西湖边吃饭，景色绝美",
                "mid_restaurant": "知味观",
                "mid_feature": "杭州老字号，小吃齐全",
                "mid_dish1": "猫耳朵",
                "mid_price1": "22/份",
                "mid_desc1": "形似猫耳，软糯可口",
                "mid_dish2": "虾爆鳝面",
                "mid_price2": "38/碗",
                "mid_desc2": "虾仁鳝丝，鲜美无比",
                "mid_comment": "老字号品质稳定，游客本地人都爱",
                "snack1": "葱包桧",
                "snack1_price": "5",
                "snack1_desc": "油条夹葱，甜面酱蘸着吃",
                "snack2": "定胜糕",
                "snack2_price": "3/个",
                "snack2_desc": "软糯香甜，寓意吉祥",
                "snack3": "桂花糕",
                "nightmarket_comment": "河坊街小吃多，但价格偏贵",
                "cuisine_type": "杭帮菜",
                "landmark1": "西湖",
                "attraction1": "西湖",
                "attraction1_price": "0",
                "attraction1_desc": "断桥残雪、苏堤春晓",
                "attraction2": "灵隐寺",
                "attraction2_price": "45",
                "attraction2_price_orig": "75",
                "attraction2_highlight": "千年古刹、飞来峰石刻",
                "attraction2_comment": "求签很灵，虔诚的可以去",
                "attraction3": "西溪湿地",
                "attraction3_price": "60",
                "attraction3_price_orig": "80",
                "attraction3_highlight": "城市湿地、坐船游览",
                "attraction3_comment": "远离喧嚣，坐船看芦苇荡很惬意",
                "dinner_restaurant": "杭帮菜私房菜",
                "dinner_feature": "精致杭帮菜，清淡为主",
                "dinner_comment": "不辣不油，适合老人小孩",
                "souvenirs": "龙井茶、丝绸、藕粉",
                "best_season": "3-5月、9-11月（春秋最佳）",
                "weather_tips": "夏天闷热冬天湿冷，春秋最舒适"
            },
            "重庆": {
                "breakfast_name": "小面馆",
                "breakfast_dish1": "重庆小面",
                "breakfast_desc1": "麻辣鲜香，辣得过瘾",
                "breakfast_dish2": "酸辣粉",
                "breakfast_desc2": "酸辣开胃，粉条劲道",
                "breakfast_comment": "小面是重庆人的灵魂早餐",
                "dessert": "冰粉",
                "high_end_restaurant": "江湖菜馆",
                "high_end_feature": "重庆江湖菜，重口味",
                "high_end_dish1": "毛血旺",
                "high_end_price1": "68",
                "high_end_desc1": "麻辣鲜香，配菜丰富",
                "high_end_dish2": "辣子鸡",
                "high_end_price2": "58",
                "high_end_desc2": "从辣椒堆里找鸡丁",
                "high_end_dish3": "水煮鱼",
                "high_end_price3": "78",
                "high_end_desc3": "鱼片嫩滑，麻辣够味",
                "high_end_comment": "重口味爱好者天堂，不能吃辣的慎点",
                "mid_restaurant": "老火锅店",
                "mid_feature": "九宫格火锅，正宗牛油底",
                "mid_dish1": "九宫格火锅",
                "mid_price1": "人均80",
                "mid_desc1": "九个格子涮不同食材",
                "mid_dish2": "毛肚",
                "mid_price2": "38/份",
                "mid_desc2": "七上八下，口感脆嫩",
                "mid_comment": "牛油底料才是正宗重庆味",
                "snack1": "小面",
                "snack1_price": "8-12",
                "snack1_desc": "麻辣鲜香，辣得爽",
                "snack2": "抄手",
                "snack2_price": "12/碗",
                "snack2_desc": "红油飘香，馅大皮薄",
                "snack3": "冰粉",
                "nightmarket_comment": "解放碑附近小吃街，晚上热闹",
                "cuisine_type": "火锅",
                "landmark1": "解放碑",
                "attraction1": "解放碑步行街",
                "attraction1_price": "0",
                "attraction1_desc": "重庆地标，繁华商圈",
                "attraction2": "洪崖洞",
                "attraction2_price": "0",
                "attraction2_price_orig": "0",
                "attraction2_highlight": "千与千寻同款夜景、吊脚楼建筑",
                "attraction2_comment": "晚上去拍照最美，像动画片里走出来的",
                "attraction3": "磁器口古镇",
                "attraction3_price": "0",
                "attraction3_price_orig": "0",
                "attraction3_highlight": "千年古镇、陈麻花、火锅底料",
                "attraction3_comment": "逛吃逛吃，买特产的好地方",
                "dinner_restaurant": "老火锅",
                "dinner_feature": "牛油九宫格，越涮越香",
                "dinner_comment": "来重庆不吃火锅等于白来",
                "souvenirs": "火锅底料、陈麻花、合川桃片",
                "best_season": "3-5月、9-11月（春秋最佳）",
                "weather_tips": "夏天巨热（火炉），冬天湿冷"
            },
            "北京": {
                "breakfast_name": "豆汁店",
                "breakfast_dish1": "豆汁焦圈",
                "breakfast_desc1": "老北京特色，酸中带甜",
                "breakfast_dish2": "炒肝",
                "breakfast_desc2": "浓稠鲜香，配包子绝了",
                "breakfast_comment": "豆汁有人爱有人恨，敢尝试的都是勇士",
                "dessert": "驴打滚",
                "high_end_restaurant": "全聚德/便宜坊",
                "high_end_feature": "正宗北京烤鸭，百年老字号",
                "high_end_dish1": "北京烤鸭",
                "high_end_price1": "198/只",
                "high_end_desc1": "皮脆肉嫩，蘸酱卷饼",
                "high_end_dish2": "芥末鸭掌",
                "high_end_price2": "48",
                "high_end_desc2": "冲鼻子但越吃越上头",
                "high_end_dish3": "火燎鸭心",
                "high_end_price3": "58",
                "high_end_desc3": "脆嫩可口",
                "high_end_comment": "来北京必吃烤鸭，一只鸭三吃",
                "mid_restaurant": "护国寺小吃",
                "mid_feature": "老北京小吃合集",
                "mid_dish1": "豌豆黄",
                "mid_price1": "8/份",
                "mid_desc1": "细腻甜糯",
                "mid_dish2": "艾窝窝",
                "mid_price2": "6/个",
                "mid_desc2": "糯米皮包馅，软糯香甜",
                "mid_comment": "各种老北京小吃都有，一站式体验",
                "snack1": "卤煮",
                "snack1_price": "25",
                "snack1_desc": "火烧、肺头、肠子，重口味",
                "snack2": "爆肚",
                "snack2_price": "30/份",
                "snack2_desc": "脆嫩爽口，蘸麻酱",
                "snack3": "糖葫芦",
                "nightmarket_comment": "簋街是吃夜宵的好地方",
                "cuisine_type": "京菜",
                "landmark1": "天安门广场",
                "attraction1": "故宫",
                "attraction1_price": "60",
                "attraction1_desc": "紫禁城，明清皇宫",
                "attraction2": "长城（八达岭）",
                "attraction2_price": "40",
                "attraction2_price_orig": "45",
                "attraction2_highlight": "不到长城非好汉",
                "attraction2_comment": "选八达岭（最方便）或慕田峪（人少）",
                "attraction3": "颐和园",
                "attraction3_price": "30",
                "attraction3_price_orig": "50",
                "attraction3_highlight": "皇家园林、昆明湖、长廊",
                "attraction3_comment": "景色优美，慢慢逛需要半天",
                "dinner_restaurant": "涮羊肉老店",
                "dinner_feature": "铜锅涮肉，清水锅底",
                "dinner_comment": "羊肉蘸麻酱，越涮越香",
                "souvenirs": "稻香村点心、果脯、京剧脸谱",
                "best_season": "4-5月、9-10月（春秋最佳）",
                "weather_tips": "冬天干冷，夏天闷热，春秋舒适但有沙尘"
            },
            "上海": {
                "breakfast_name": "生煎馒头店",
                "breakfast_dish1": "生煎馒头",
                "breakfast_desc1": "底脆汁多，鲜香可口",
                "breakfast_dish2": "小馄饨",
                "breakfast_desc2": "皮薄馅鲜，汤底清甜",
                "breakfast_comment": "生煎底要焦脆，汁水要烫嘴才正宗",
                "dessert": "蟹壳黄",
                "high_end_restaurant": "本帮菜馆",
                "high_end_feature": "浓油赤酱，甜中带咸",
                "high_end_dish1": "红烧肉",
                "high_end_price1": "68",
                "high_end_desc1": "肥而不腻，入口即化",
                "high_end_dish2": "清炒河虾仁",
                "high_end_price2": "88",
                "high_end_desc2": "鲜嫩弹牙，原汁原味",
                "high_end_dish3": "腌笃鲜",
                "high_end_price3": "58",
                "high_end_desc3": "咸肉鲜肉笋，汤鲜味美",
                "high_end_comment": "浓油赤酱是本帮菜特色，偏甜",
                "mid_restaurant": "小杨生煎",
                "mid_feature": "连锁品牌，品质稳定",
                "mid_dish1": "鲜肉生煎",
                "mid_price1": "8/4个",
                "mid_desc1": "经典款，汁水足",
                "mid_dish2": "蟹粉生煎",
                "mid_price2": "15/4个",
                "mid_desc2": "蟹黄蟹肉，鲜得掉眉毛",
                "mid_comment": "性价比高，排队也值得",
                "snack1": "生煎",
                "snack1_price": "8-15",
                "snack1_desc": "底脆汁多，小心烫嘴",
                "snack2": "锅贴",
                "snack2_price": "10/份",
                "snack2_desc": "焦脆鲜香",
                "snack3": "排骨年糕",
                "nightmarket_comment": "城隍庙小吃虽然游客多但种类全",
                "cuisine_type": "本帮菜",
                "landmark1": "外滩",
                "attraction1": "外滩",
                "attraction1_price": "0",
                "attraction1_desc": "万国建筑博览群，夜景绝美",
                "attraction2": "东方明珠/上海中心",
                "attraction2_price": "120",
                "attraction2_price_orig": "180",
                "attraction2_highlight": "俯瞰上海全景",
                "attraction2_comment": "选上海中心（更高）或东方明珠（经典）",
                "attraction3": "迪士尼乐园",
                "attraction3_price": "399",
                "attraction3_price_orig": "475",
                "attraction3_highlight": "全球最大迪士尼城堡",
                "attraction3_comment": "亲子必去！提前下载APP抢快速通行",
                "dinner_restaurant": "上海老饭店",
                "dinner_feature": "百年老店，正宗本帮菜",
                "dinner_comment": "偏甜，不能接受甜口菜的慎点",
                "souvenirs": "大白兔奶糖、城隍庙五香豆、蝴蝶酥",
                "best_season": "3-5月、9-11月（春秋最佳）",
                "weather_tips": "夏天闷热（黄梅天），冬天湿冷"
            }
        }

        # 默认数据（适用于未知城市）
        default_data = {
            "breakfast_name": "特色早餐店",
            "breakfast_dish1": "本地特色粉面",
            "breakfast_desc1": "汤底鲜美，配料丰富",
            "breakfast_dish2": "特色小吃",
            "breakfast_desc2": "本地风味，值得一试",
            "breakfast_comment": "本地人从小吃到大的味道",
            "dessert": "本地甜品",
            "high_end_restaurant": "本地特色餐厅",
            "high_end_feature": "本地招牌菜，口味正宗",
            "high_end_dish1": "招牌菜一",
            "high_end_price1": "88",
            "high_end_desc1": "本店招牌，必点",
            "high_end_dish2": "招牌菜二",
            "high_end_price2": "68",
            "high_end_desc2": "人气菜品",
            "high_end_dish3": "招牌菜三",
            "high_end_price3": "48",
            "high_end_desc3": "性价比之选",
            "high_end_comment": "本地人请客都来这，味道正宗",
            "mid_restaurant": "老字号小吃店",
            "mid_feature": "传承多年，味道稳定",
            "mid_dish1": "特色主食",
            "mid_price1": "25",
            "mid_desc1": "分量足，味道好",
            "mid_dish2": "配菜小吃",
            "mid_price2": "15",
            "mid_desc2": "搭配主食一起吃",
            "mid_comment": "老字号，本地人都认可",
            "snack1": "本地小吃",
            "snack1_price": "10",
            "snack1_desc": "街边美食，接地气",
            "snack2": "特色点心",
            "snack2_price": "8",
            "snack2_desc": "本地风味",
            "snack3": "夜市小吃",
            "nightmarket_comment": "夜市人多的摊位，味道不会差",
            "cuisine_type": "本地菜",
            "landmark1": "市中心广场",
            "attraction1": "老城区",
            "attraction1_price": "0",
            "attraction1_desc": "体验本地生活",
            "attraction2": "知名景点A",
            "attraction2_price": "60",
            "attraction2_price_orig": "80",
            "attraction2_highlight": "本地必去景点",
            "attraction2_comment": "值得一去，拍照好看",
            "attraction3": "知名景点B",
            "attraction3_price": "80",
            "attraction3_price_orig": "120",
            "attraction3_highlight": "适合全家游玩",
            "attraction3_comment": "性价比高，体验好",
            "dinner_restaurant": "本地特色餐厅",
            "dinner_feature": "晚餐首选，氛围好",
            "dinner_comment": "适合朋友聚餐",
            "souvenirs": "本地特产、手工艺品、零食小吃",
            "best_season": "春秋两季（气温舒适）",
            "weather_tips": "出行前查看天气预报，带好雨具"
        }

        return city_database.get(city, default_data)

    def _generate_mock(self, query: str, mode: str) -> str:
        """
        生成Mock攻略（当AI不可用时）- 优化版
        根据用户查询的城市，生成对应城市的通用攻略模板
        """
        # 提取城市名称
        from prompts.wildtrip_prompt import extract_city_name
        city = extract_city_name(query)

        # 获取城市特色数据
        city_data = self._get_city_data(city)

        if mode == 'hotel':
            return f"""
# 🏨 {city}酒店推荐 - 野游记精选

## 💰 3个价位，总有一款适合你

### 1. 高端之选：{city}希尔顿逸林酒店 ⭐⭐⭐⭐⭐
- **价格：** ¥680-980/晚（淡季¥680，旺季¥980）
- **位置：** {city}CBD核心区，步行3分钟到地铁站
- **设施：** 
  - 🏊 25米恒温泳池（顶楼无边泳池，城市景观一流）
  - 🍽️ 行政酒廊含早晚餐（中西式自助，品种100+）
  - 🧒 儿童乐园 + 儿童泳池（亲子游首选）
  - 💪 24h健身房 + SPA（设备齐全）
  - 🅿️ 免费停车（地下车库，充电桩）
- **适合：** 蜜月度假、商务出差、亲子游、高端享受
- **野导游说：** 
  贵是贵了点，但确实物有所值。早餐种类超多（粤式早茶、日式料理、西式煎蛋都有），泳池view绝了，适合拍照打卡。房间隔音好，床垫舒服，一夜睡到天亮。前台服务态度超好，有啥问题分分钟给你解决。如果预算够，闭眼入。
- **💰 省钱tip：** 提前7天订便宜15%，工作日入住再省10%
- **预订：** [查看详情](占位)

---

### 2. 舒适之选：{city}亚朵酒店 ⭐⭐⭐⭐
- **价格：** ¥280-380/晚（淡季¥280，旺季¥380）
- **位置：** 近地铁2号线，距离老城区3公里
- **设施：**
  - 🛏️ 大床房/双床房（床品舒适，乳胶枕）
  - 🍜 免费早餐（粥粉面饭，中式为主）
  - 💪 健身房（跑步机、哑铃）
  - 📚 图书角（竹居·流动图书馆）
  - 🅿️ 停车¥20/天
- **适合：** 情侣游、家庭游、商务差旅、性价比之选
- **野导游说：**
  性价比之王！本地人出差首选。房间干净整洁，装修简约但不简陋，插座够多（6个），床垫软硬适中。早餐虽然不如五星丰富，但够吃（粥粉面饭都有）。前台效率高，check-in只要2分钟。没有五星的奢华，但该有的都有，省下的钱拿去吃好的更香。
- **💰 省钱tip：** 成为会员再打9折，平均¥250/晚
- **预订：** [查看详情](占位)

---

### 3. 经济之选：{city}锦江之星快捷酒店 ⭐⭐⭐
- **价格：** ¥120-180/晚（淡季¥120，周末¥180）
- **位置：** 老城区中心，楼下菜市场+小吃街
- **设施：**
  - 🛏️ 标准间（干净卫生，空调热水齐全）
  - 🚿 24h热水（水压足，温度稳定）
  - 📶 免费WiFi（网速6-8Mbps）
  - 🍜 早餐¥15另购（豆浆油条、粥粉面）
  - 🅿️ 路边停车（免费，但车位紧张）
- **适合：** 学生党、背包客、预算有限、本地生活体验
- **野导游说：**
  别看便宜，性价比杠杠的。房间虽小（15㎡左右），但五脏俱全。床单一客一换，打扫阿姨很负责。楼下就是菜市场和小吃街，早上6点起来吃本地早餐，晚上逛夜市，满满的烟火气。唯一缺点是隔音一般（能听到隔壁看电视），睡眠浅的慎选。但这个价位还要啥自行车？
- **💰 省钱tip：** 连住3晚送1晚，平均¥90/晚
- **预订：** [查看详情](占位)

---

## 🎯 野游记选择建议

| 你的情况 | 推荐酒店 | 理由 |
|---------|---------|------|
| 💰 预算充足（>¥600/晚） | #1 希尔顿逸林 | 享受假期，一分钱一分货 |
| 🎯 追求性价比（¥250-400/晚） | #2 亚朵酒店 | **最佳选择**，90%的人都选这个 |
| 💸 预算有限（<¥200/晚） | #3 锦江之星 | 实惠够用，省钱吃好吃的 |
| 👨‍👩‍👧 亲子家庭 | #1 希尔顿逸林 | 儿童设施全，早餐孩子爱吃 |
| 💼 商务出差 | #2 亚朵酒店 | 位置方便，效率高 |
| 🎒 背包穷游 | #3 锦江之星 | 性价比最高，体验本地生活 |

---

## 💡 订酒店省钱秘籍

1. **提前订** - 提前7天订便宜10-20%，提前30天更便宜
2. **工作日入住** - 周一到周四比周五到周日便宜30%
3. **会员卡** - 各大连锁酒店会员打9折，还能积分
4. **比价** - 美团/携程/飞猪三平台对比，选最便宜的
5. **联系前台** - 有时直接电话酒店比OTA便宜（前台有优惠权）

---

## ⚠️ 避坑指南

- ❌ **别信"豪华海景房"** - 有些酒店挂着"海景"，实际只能看到一条缝
- ❌ **远离景区附近酒店** - 价格贵2倍，周边吵闹，性价比极低
- ❌ **别被"网红民宿"骗** - 拍照好看，实际体验差（隔音差、设施旧）
- ✅ **认准连锁品牌** - 锦江、亚朵、维也纳、汉庭，品质稳定不踩雷

---

**🔥 野游记碎碎念：**

酒店只是睡觉的地方，别把太多预算花在这。除非你是来度假享受的，否则选个干净舒适、位置方便的就够了。把省下来的钱拿去吃当地美食、玩真正值得玩的项目，这才是旅行的意义！

记住野游记的slogan：**不走寻常路，就走野路子** 😎
"""
        
        elif mode == 'food':
            return f"""
# 🍜 {city}美食地图 - 野游记本地人推荐

> 网红店都是坑，跟着本地人吃才不会错

---

## ☀️ 早餐篇（06:00-10:00）

### 1. {city}{city_data['breakfast_name']}（开了30年）¥12-20/人 ⭐4.8

- **地址：** {city}XX路菜市场旁边（导航：XX菜市场）
- **营业时间：** 06:00-10:00（卖完就关门，去晚了吃不到）
- **招牌菜：**
  - 🍜 **{city_data['breakfast_dish1']}**（¥12）- {city_data['breakfast_desc1']}
  - 🥤 **{city_data['breakfast_dish2']}**（¥8）- {city_data['breakfast_desc2']}
  - 🥞 **煎饼/包子**（¥5）- 现做现卖，外酥里嫩
- **人均消费：** ¥15-20吃到撑
- **野导游说：**
  早上6点就开始排队，全是本地人（游客根本不知道这地方）。老板娘做了30年，手艺没得说。{city_data['breakfast_comment']}。别被破旧的店面吓到，真正的美食都藏在这种"苍蝇馆子"里。
- **💡 Tips：**
  - 早点去（7点前），晚了要排队20分钟
  - 点餐的时候说"加料"，多给你配菜
  - 吃完记得来碗{city_data['dessert']}解腻
- **团购：** [美团团购](占位)

---

## 🍖 午餐/晚餐篇

### 💰 高端档（人均¥150-300）

#### 1. {city}{city_data['high_end_restaurant']} ¥200-300/人 ⭐4.7

- **地址：** {city}XX路18号（市中心）
- **营业时间：** 11:00-14:00, 17:00-22:00
- **特色：** {city_data['high_end_feature']}
- **招牌菜：**
  - 🍖 **{city_data['high_end_dish1']}**（¥{city_data['high_end_price1']}）- {city_data['high_end_desc1']}
  - 🍲 **{city_data['high_end_dish2']}**（¥{city_data['high_end_price2']}）- {city_data['high_end_desc2']}
  - 🥘 **{city_data['high_end_dish3']}**（¥{city_data['high_end_price3']}）- {city_data['high_end_desc3']}
- **人均消费：** ¥200-300
- **野导游说：**
  本地人请客都来这！{city_data['high_end_comment']}。价格明码标价，不像景区附近那些坑货。服务员态度好，会推荐当季最好的菜品。缺点是晚餐时间人多，建议提前订位。
- **💡 Tips：**
  - 避开周末晚餐高峰（17:30-19:00），要等位1小时
  - 招牌菜必点，其他菜可以让服务员推荐
- **团购：** [美团团购](占位)

---

### 🎯 中档档（人均¥50-100）- **性价比之王**

#### 1. {city}{city_data['mid_restaurant']} ¥50-80/人 ⭐4.9

- **地址：** {city}XX路XX号（老城区）
- **营业时间：** 10:30-14:00, 17:00-21:00
- **特色：** {city_data['mid_feature']}
- **招牌菜：**
  - 🍖 **{city_data['mid_dish1']}**（¥{city_data['mid_price1']}）- {city_data['mid_desc1']}
  - 🍚 **{city_data['mid_dish2']}**（¥{city_data['mid_price2']}）- {city_data['mid_desc2']}
  - 🥬 **时令蔬菜**（¥18）- 清淡爽口
- **人均消费：** ¥50-80
- **野导游说：**
  别去那些网红店了，都是坑！这家才是本地人认可的。{city_data['mid_comment']}。环境一般（老店嘛），但味道绝对正宗。两个人点招牌菜+2碗饭+1个菜，60块钱吃饱。
- **💡 Tips：**
  - 午餐11:30前去，晚了招牌菜卖完了
  - 米饭可以续（免费）
- **团购：** [美团团购](占位)

---

### 💸 经济档（人均¥20-50）

#### 1. {city}夜市小吃街 ¥20-40/人 ⭐4.6

- **地址：** {city}XX路夜市（晚上9点后最热闹）
- **营业时间：** 18:00-02:00
- **特色：** 接地气，地道，便宜
- **必吃清单：**
  - 🍜 **{city_data['snack1']}**（¥{city_data['snack1_price']}）- {city_data['snack1_desc']}
  - 🍢 **烧烤**（¥1-5/串）- 烤串、烤鱿鱼、烤羊肉
  - 🥟 **{city_data['snack2']}**（¥{city_data['snack2_price']}）- {city_data['snack2_desc']}
  - 🍨 **{city_data['snack3']}**（¥10）- 本地特色小吃
- **人均消费：** ¥30左右
- **野导游说：**
  晚上9点后最热闹，全是本地人（游客很少）。卫生条件一般，但味道绝了。{city_data['nightmarket_comment']}。烧烤要去人最多的那摊（排队就对了）。30块钱吃10样小吃，爽！
- **💡 Tips：**
  - 准备现金（有些摊位不收微信）
  - 别吃太饱，要留肚子多尝几家
  - 肠胃不好的慎吃烧烤（偶尔有拉肚子的）
- **团购：** [美团搜索](占位)

---

## ⚠️ 避坑指南（血泪教训）

| ❌ 别去 | 理由 | ✅ 去哪 |
|---------|------|--------|
| XX网红餐厅 | 宰客严重，性价比极低 | {city}{city_data['high_end_restaurant']} |
| XX网红店 | 徒有虚名，游客店，本地人都不去 | {city_data['mid_restaurant']} |
| XX景区美食街 | 价格贵3倍，味道还不行，全是游客 | 本地夜市小吃街 |

---

## 💡 吃货省钱秘籍

1. **跟着本地人走** - 人多的店，味道不会差
2. **避开景区** - 景区附近餐厅价格贵2-3倍
3. **美团团购** - 餐饮类平均省30%
4. **午餐代替晚餐** - 同一家店，午市比晚市便宜20%
5. **问当地人** - 打车时问司机，保洁阿姨都是美食雷达

---

**🔥 野游记碎碎念：**

好吃的店往往藏在犄角旮旯，别怕远，别怕破。那些装修豪华、网红打卡的店，90%都是坑。真正的美食，都是本地人从小吃到大的"苍蝇馆子"。记住：**人多的店，味道不会差**。别怕排队，排队就对了！ 🍖
"""
        
        else:  # full mode
            return f"""
# 🔥 {city}3天2晚完整攻略 - 野游记出品

> **不走寻常路，就走野路子**
> 用本地人的方式玩{city}，省钱又好玩

---

## 📋 行程概览卡片

| 项目 | 内容 |
|------|------|
| 🗓️ **天数** | 3天2晚（适合周末+请1天假） |
| 💰 **预算** | ¥1500-2500/人（含吃住行门票） |
| 👨‍👩‍👧 **适合** | 亲子家庭、情侣、闺蜜、朋友结伴 |
| 🌤️ **最佳时节** | {city_data['best_season']} |
| ✨ **核心亮点** | ① 本地人美食清单<br>② 避开网红景点找真宝藏<br>③ 全程团购省30%+ |

---

## 🗓️ 详细行程（复制就能用）

### 📅 Day 1：抵达 + 老城深度游（周五）

> **主题：** 慢节奏，感受本地生活烟火气

| 时间 | 地点/活动 | 费用 | 备注 |
|------|----------|------|------|
| 09:00 | ✈️ 抵达{city} | - | 机场/高铁打车到市区约¥50，30分钟 |
| 10:00 | 🏨 入住酒店 | ¥300/晚 | 推荐亚朵酒店（见下方住宿推荐） |
| 11:00 | 🏛️ {city_data['landmark1']} | 免费 | 拍照打卡，感受{city}风情 |
| 12:30 | 🍜 午餐：{city_data['breakfast_name']} | ¥15/人 | 本地人从小吃到大（见美食推荐） |
| 14:00 | 🛒 菜市场闲逛 | 免费 | 体验本地生活，买水果便宜 |
| 16:00 | ☕ 咖啡馆休息 | ¥30/人 | 老街里的精品咖啡馆，歇歇脚 |
| 18:30 | 🍲 晚餐：{city_data['high_end_restaurant']} | ¥150/人 | 重头戏！{city_data['cuisine_type']}美食（见美食推荐） |
| 20:30 | 🌃 夜市小吃街 | ¥30/人 | 烧烤、小吃，吃10样 |
| 22:00 | 🏨 回酒店休息 | - | 养精蓄锐，明天继续 |

**💡 Day 1 Tips：**
- ✅ 别赶时间，老街慢慢逛才有味道
- ✅ 菜市场买水果（比景区便宜一半）
- ✅ 晚餐别吃太饱，留肚子逛夜市

---

#### 🍽️ Day 1 美食详解

**午餐：{city}{city_data['breakfast_name']}**
- **地址：** {city}XX路菜市场旁
- **人均：** ¥15
- **必点：** {city_data['breakfast_dish1']}（¥12）+ {city_data['dessert']}（¥8）
- **野导游说：** {city_data['breakfast_comment']}。15块钱吃到撑。
- **团购：** [美团团购](占位)

**晚餐：{city}{city_data['high_end_restaurant']}**
- **地址：** {city}XX路18号
- **人均：** ¥150-200
- **必点：**
  - {city_data['high_end_dish1']}（¥{city_data['high_end_price1']}）
  - {city_data['high_end_dish2']}（¥{city_data['high_end_price2']}）
  - {city_data['high_end_dish3']}（¥{city_data['high_end_price3']}）
- **野导游说：** 本地人请客都来这，明码标价不宰客。{city_data['high_end_comment']}
- **团购：** [美团团购](占位)

**夜市小吃：**
- {city_data['snack1']}（¥{city_data['snack1_price']}）、烧烤（¥30）、{city_data['snack3']}（¥10）
- **野导游说：** 晚上9点后最热闹，全是本地人。30块钱吃10样。
- **团购：** [美团搜索](占位)

---

### 📅 Day 2：{city_data['attraction1']} + {city_data['attraction2']}（周六）

> **主题：** 上午游玩，下午探索，晚上美食

| 时间 | 地点/活动 | 费用 | 备注 |
|------|----------|------|------|
| 08:00 | 🥞 早餐：{city_data['breakfast_name']} | ¥15/人 | 再吃一次，太香了 |
| 09:00 | 🏛️ {city_data['attraction1']} | ¥{city_data['attraction1_price']}/人 | {city_data['attraction1_desc']} |
| 12:00 | 🍜 午餐：{city_data['mid_restaurant']} | ¥50/人 | {city_data['mid_dish1']} |
| 14:00 | 🌄 {city_data['attraction2']} | ¥{city_data['attraction2_price']}/人 | 美团订票省钱（见门票推荐） |
| 17:00 | 🚗 返回市区 | 打车¥40 | 约30分钟 |
| 18:30 | 🍲 晚餐：{city_data['dinner_restaurant']} | ¥80/人 | 本地特色 |
| 20:00 | 🛍️ 商场逛街 | - | 买特产 |
| 22:00 | 🏨 回酒店休息 | - | - |

**💡 Day 2 Tips：**
- ✅ 景点10点前去（人少，拍照好看）
- ✅ 穿运动鞋，方便游玩
- ✅ 带防晒霜（SPF50+）

---

#### 🎫 Day 2 门票详解

**{city_data['attraction2']}**
- **原价：** ¥{city_data['attraction2_price_orig']}/人
- **美团价：** ¥{city_data['attraction2_price']}/人（省¥20）
- **游玩时间：** 2-3小时
- **亮点：** {city_data['attraction2_highlight']}
- **野导游说：** {city}值得去的景点！{city_data['attraction2_comment']}。别去那些网红景点，这里才是真宝藏。
- **💡 Tips：**
  - 美团提前1天订票，便宜¥20
  - 带运动鞋（要走路）
- **订票：** [美团门票](占位)

---

#### 🍽️ Day 2 美食详解

**午餐：{city}{city_data['mid_restaurant']}**
- **人均：** ¥50
- **团购：** [美团团购](占位)

**晚餐：{city_data['dinner_restaurant']}**
- **地址：** {city}XX路XX号
- **人均：** ¥80
- **特色：** {city_data['dinner_feature']}
- **野导游说：** {city}特色吃法，{city_data['dinner_comment']}。适合老人小孩。
- **团购：** [美团团购](占位)

---

### 📅 Day 3：{city_data['attraction3']} + 返程（周日）

> **主题：** 深度游玩，下午返程

| 时间 | 地点/活动 | 费用 | 备注 |
|------|----------|------|------|
| 08:30 | 🥞 早餐：酒店附近 | ¥20/人 | 粥粉面饭 |
| 09:00 | 🦁 {city_data['attraction3']} | ¥{city_data['attraction3_price']}/人 | 美团订票（见门票推荐） |
| 12:00 | 🍜 午餐：园内/附近 | ¥50/人 | 快餐 |
| 14:00 | 🛍️ 买特产 | ¥100 | {city_data['souvenirs']} |
| 15:30 | ✈️ 前往机场/车站 | 打车¥50 | 留足时间，别误机 |
| 17:00 | 🏠 返程 | - | 带着美好回忆回家 |

**💡 Day 3 Tips：**
- ✅ 景点要玩3-4小时，别赶时间
- ✅ 特产去超市买（比机场便宜30%）
- ✅ 预留2小时到机场（路上可能堵车）

---

#### 🎫 Day 3 门票详解

**{city_data['attraction3']}**
- **原价：** ¥{city_data['attraction3_price_orig']}/人
- **美团价：** ¥{city_data['attraction3_price']}/人（省¥40）
- **游玩时间：** 3-4小时
- **亮点：** {city_data['attraction3_highlight']}
- **野导游说：** {city_data['attraction3_comment']}。性价比高。
- **💡 Tips：**
  - 美团提前1天订票
  - 穿舒适鞋子（要走很多路）
- **订票：** [美团门票](占位)

---

## 🏨 住宿推荐（2晚）

### ⭐ 推荐：{city}亚朵酒店（性价比之王）

- **价格：** ¥280-380/晚 × 2晚 = ¥600
- **位置：** 市中心，近地铁，交通方便
- **设施：** 大床房、免费早餐、健身房、图书角
- **适合：** 90%的人都选这个
- **野导游说：** 本地人出差首选！房间干净舒适，早餐够吃，位置方便。没有五星的奢华，但该有的都有。省下的钱拿去吃好的更香。
- **💰 省钱tip：** 成为会员打9折，平均¥250/晚
- **预订：** [查看详情](占位)

### 备选方案：

| 酒店 | 价格 | 适合人群 |
|------|------|----------|
| 希尔顿逸林 | ¥680-980/晚 | 预算充足、享受型 |
| 锦江之星 | ¥120-180/晚 | 预算有限、学生党 |

---

## 💰 费用明细（人均预算）

| 项目 | 明细 | 金额 |
|------|------|------|
| 🏨 **住宿** | 亚朵酒店 ¥300/晚 × 2晚 | **¥600** |
| 🍽️ **餐饮** | 早¥15 + 午¥50 + 晚¥100 × 3天 | **¥500** |
| 🎫 **门票** | {city_data['attraction2']}¥{city_data['attraction2_price']} + {city_data['attraction3']}¥{city_data['attraction3_price']} | **¥140** |
| 🚗 **交通** | 打车 + 公交 | **¥150** |
| 🛍️ **购物** | 特产、纪念品 | **¥100** |
| 💡 **预留** | 应急费用 | **¥100** |
| **💰 总计** |  | **¥1590** |

**💡 如果用美团团购：** 最终费用约 **¥1300-1500/人**（省15-20%）

---

## 💡 省钱秘籍（帮你省¥300+）

| 省钱方法 | 能省多少 | 操作 |
|---------|---------|------|
| 🏨 工作日入住 | 省¥120 | 周一到周四住宿便宜30% |
| 🍽️ 美团团购 | 省¥150 | 餐饮类平均省30% |
| 🎫 提前订票 | 省¥60 | 门票提前1天订便宜¥20/张 |
| ✈️ 提前订机票 | 省¥200+ | 提前30天订机票便宜50% |
| 🛍️ 超市买特产 | 省¥50 | 比机场便宜30% |
| **💰 总共** | **省¥580** | **省出一顿大餐！** |

---

## ⚠️ 避坑指南（血泪教训）

| ❌ 别去/别做 | 理由 | ✅ 正确做法 |
|------------|------|------------|
| ❌ XX网红餐厅 | 宰客严重，性价比低 | ✅ 去{city}{city_data['high_end_restaurant']} |
| ❌ 住景区附近 | 价格贵2倍，吵闹 | ✅ 住市中心，交通方便 |
| ❌ 参加低价团 | 全程购物，景点走马观花 | ✅ 自由行，按这份攻略走 |
| ❌ 在景区买特产 | 价格虚高 | ✅ 去{city}本地超市买特产 |

---

## 🎒 行前准备清单

### ✅ 必带物品
- 🧴 **防晒霜**（SPF50+）
- 👟 **运动鞋**（景点要走路）
- 🕶️ **墨镜 + 帽子**（防晒必备）
- 💊 **肠胃药**（吃当地美食以防万一）
- 🔋 **充电宝**（拍照耗电快）

### 📱 APP下载
- 美团（订酒店、餐厅团购、门票）
- 高德地图（导航）
- 大众点评（找美食）

### 🌤️ 天气建议
- **最佳时节：** {city_data['best_season']}
- **注意事项：** {city_data['weather_tips']}

---

## 🔥 野游记碎碎念

这份攻略是我（野游记AI导游）根据本地人的真实经验整理的，**不是千篇一律的旅游团线路**。

我们的理念很简单：
1. **别去网红景点排队** - 那些都是坑，去真正值得去的地方
2. **跟着本地人吃** - 最好吃的店都藏在犄角旮旯
3. **用美团省钱** - 团购能省30%，省下的钱吃好的

记住野游记的slogan：**不走寻常路，就走野路子** 😎

祝你在{city}玩得开心！有问题随时问我 🔥

---

**📌 最后提醒：**
- 这份攻略可以直接复制粘贴到备忘录
- 所有团购链接点击即可跳转美团

**🎁 福利：** 把这份攻略分享给3个好友，返现¥10！（具体规则见野游记小程序）
"""
