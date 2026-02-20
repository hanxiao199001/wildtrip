# 野游记 B端 SaaS 产品方案

## 🎯 产品定位

**AI 智能掌柜 - 精品民宿/单体酒店的私域直销工具**

**核心价值主张:**
- 不收佣金,只收 SaaS 订阅费(¥299/月)
- 7x24 小时 AI 客服,自动回答 90% 常见问题
- 自动生成周边"野路子"攻略,提升情绪价值
- 引导客人直接在官方小程序/企微预订

---

## 📋 功能模块

### 1. AI 客服核心引擎

**接入方式:**
- 嵌入酒店公众号自动回复
- 嵌入酒店企微客服号
- 嵌入酒店小程序客服

**技术架构:**
```python
# backend/services/hotel_ai_assistant.py

class HotelAIAssistant:
    """酒店 AI 助手"""
    
    def __init__(self, hotel_id: str):
        self.hotel_id = hotel_id
        self.hotel_info = self.load_hotel_info(hotel_id)
    
    async def chat(self, user_message: str, context: dict = None) -> dict:
        """
        处理用户咨询
        
        Returns:
            {
                'reply': 'AI 回复文本',
                'action': 'book' | 'recommend' | 'info',
                'data': {...}  # 额外数据(如预订链接)
            }
        """
        # 1. 意图识别
        intent = self.classify_intent(user_message)
        
        # 2. 根据意图生成回复
        if intent == 'faq':
            # 常见问题(能带宠物吗/有儿童拖鞋吗)
            return self.answer_faq(user_message)
        
        elif intent == '周边玩法':
            # 🔥 核心卖点:生成野路子攻略
            return self.generate_local_guide(user_message)
        
        elif intent == '预订咨询':
            # 引导到直销渠道
            return self.guide_to_booking(user_message)
    
    def answer_faq(self, question: str) -> dict:
        """回答常见问题"""
        # 从酒店信息库匹配答案
        faq_db = {
            '能带宠物': f"{self.hotel_info['pet_friendly']}",
            '儿童拖鞋': f"有的,{self.hotel_info['amenities']['kids']}",
            '早餐时间': f"{self.hotel_info['breakfast_time']}",
            '停车位': f"{self.hotel_info['parking']}",
            # ... 更多
        }
        
        # 关键词匹配
        for keyword, answer in faq_db.items():
            if keyword in question:
                return {
                    'reply': answer,
                    'action': 'info'
                }
        
        # 未匹配到,调用 AI 生成
        return self.ai_generate_answer(question)
    
    def generate_local_guide(self, query: str) -> dict:
        """
        🔥 核心功能:生成周边野路子攻略
        
        这是促单的关键!
        """
        from services.ai_engine import AIEngine
        
        prompt = f"""
你是 {self.hotel_info['name']} 的本地向导。

用户问: {query}

请生成一份情绪价值极高的周末行程建议:

【要求】
1. 避开网红打卡点,推荐本地人才知道的地方
2. 结合酒店的特色(如: {self.hotel_info['features']})
3. 给出具体的时间安排和交通方式
4. 语气要像朋友聊天,不要官方腔

【参考信息】
- 酒店位置: {self.hotel_info['location']}
- 周边 5km 内的宝藏地点: {self.hotel_info['nearby_wild_places']}
- 适合人群: {query中提取的人群(如亲子/情侣)}
"""
        
        ai = AIEngine()
        guide_content = ai.generate(prompt, query, mode='local_guide')
        
        return {
            'reply': guide_content + f"\n\n💡 预订我们酒店可享受:\n{self.hotel_info['vip_benefits']}",
            'action': 'recommend',
            'data': {
                'guide': guide_content,
                'booking_link': self.hotel_info['wechat_miniprogram']
            }
        }
    
    def guide_to_booking(self, message: str) -> dict:
        """引导到直销渠道"""
        return {
            'reply': f"您可以直接在我们的官方小程序预订,价格比 OTA 更优惠!\n\n" +
                     f"🎁 野游记专属福利:\n" +
                     f"- 免费升级房型(视空房情况)\n" +
                     f"- 延迟退房至下午 2 点\n" +
                     f"- 赠送儿童欢迎礼\n\n" +
                     f"[点击预订]({self.hotel_info['booking_link']})",
            'action': 'book',
            'data': {
                'booking_link': self.hotel_info['booking_link']
            }
        }
```

---

### 2. 酒店信息管理后台

**功能:**
- 酒店老板可以自己配置:
  - 房型和价格
  - 周边野路子地点库
  - 常见问题答案
  - VIP 会员专属福利

**技术栈:**
- 前端: 简单的 Web 管理后台
- 后端: Flask + SQLite (MVP 阶段)

```python
# backend/models/hotel.py

class Hotel(BaseModel):
    id: str
    name: str
    location: str
    
    # 基础信息
    pet_friendly: str = "可以带宠物,需提前告知"
    parking: str = "免费停车位 10 个"
    breakfast_time: str = "7:30 - 10:00"
    
    # 设施
    amenities: dict = {
        'kids': '儿童拖鞋、儿童牙刷、积木玩具',
        'pool': '恒温泳池(1.2m 深,适合儿童)',
        'dining': '院子可 BBQ'
    }
    
    # 🔥 核心资产:周边野路子地点
    nearby_wild_places: List[dict] = [
        {
            'name': '后山野海滩',
            'distance': '步行 5 分钟',
            'description': '游客不知道,本地人周末去抓螃蟹的地方',
            'best_time': '下午 4-5 点退潮'
        },
        {
            'name': '镇上无名海鲜排档',
            'distance': '开车 10 分钟',
            'description': '没有招牌,但本地人都去,老板娘会教你挑海鲜'
        }
    ]
    
    # VIP 福利
    vip_benefits: str = "野游记会员专享:免费升级海景房 + 延迟退房"
    
    # 预订链接
    wechat_miniprogram: str = "weixin://dl/business/?t=xxx"
    booking_link: str = "https://hotel.com/book"
```

---

### 3. 微信公众号/企微集成

**接入流程:**

```python
# backend/api/wechat_bot.py

from flask import Blueprint, request
from services.hotel_ai_assistant import HotelAIAssistant

wechat_bp = Blueprint('wechat', __name__)

@wechat_bp.route('/wechat/callback/<hotel_id>', methods=['POST'])
def wechat_message_callback(hotel_id: str):
    """
    微信公众号消息回调
    
    酒店老板在公众号后台配置这个 URL:
    https://api.wildtrip.com.cn/wechat/callback/hotel_001
    """
    # 解析微信消息
    msg = parse_wechat_message(request.data)
    
    # 调用 AI 助手
    assistant = HotelAIAssistant(hotel_id)
    response = await assistant.chat(msg.content, context={
        'user_id': msg.from_user
    })
    
    # 回复微信消息
    return build_wechat_reply(
        to_user=msg.from_user,
        content=response['reply']
    )
```

---

## 💰 定价策略

### SaaS 订阅费

**定价:**
- 月付: ¥299/月
- 年付: ¥2999/年 (相当于 8.3 折)

**为什么定这个价?**
- 对比 OTA 抽成:一家年流水 100万 的民宿,携程抽 15% = ¥15万
- 我们只收 ¥3000/年,**省 99% 的成本**
- 酒店老板**秒懂**这笔账

**增值服务(可选):**
- 定制化周边攻略库: ¥1999 一次性
- 小红书引流代运营: ¥999/月

---

## 🎯 冷启动策略

### 第一步:海口周边 10 家试点酒店

**目标酒店画像:**
- 精品民宿/单体酒店
- 房间数 10-30 间
- 有亲子设施(泳池/沙池/院子)
- 老板有私域意识

**地推话术:**
```
老板您好,我是野游记的创始人。

我们是做 AI 旅游攻略的,现在想帮海口周边的精品民宿
做一个免费的 AI 客服系统。

【您的痛点我懂】
- 携程抽 15%-20%,一年几万块
- 客人总问"能带宠物吗""早餐几点",前台很烦
- 想做私域,但不知道怎么引导客人直接订

【我们能帮您什么】
1. 免费帮您接入 AI 客服,7x24 自动回答常见问题
2. 自动生成您周边的"野路子"攻略,提升情绪价值
3. 引导客人在您的小程序/企微直接预订,省佣金

【试用方案】
- 免费用 1 个月,看效果
- 如果转化了,按月付 299 元
- 如果没效果,您没损失

您看可以吗?
```

**预期转化:**
- 10 家试点,至少 6 家付费
- 月收入: 6 × ¥299 = ¥1794
- **关键不是钱,是拿到 6 家的独家房源和在地知识**

---

## 📱 C端周末订阅产品

### 产品形态

**名称:** "野游记黑卡"

**价格:**
- 月付: ¥9.9/月
- 年付: ¥99/年

**会员权益:**
1. 每周四推送本周末的"定制放电计划"
2. B端酒店的直销底价(比 OTA 便宜 10-20%)
3. 独家福利:延迟退房、房型升级、儿童礼包
4. 野路子攻略库无限查看

**推送示例:**
```
📅 本周末推荐 | 万宁玩水亲子游

🌤️ 天气:28°C,晴,适合玩水

🏨 住宿:万宁 XX 海景民宿
- 野游记专属价:¥380/晚(携程 ¥480)
- 赠送:儿童欢迎礼 + 延迟退房至 14:00

🗺️ 行程安排:
【周六】
14:00 办入住,院子里拼遥控积木
16:00 去民宿背后的野海滩抓螃蟹(退潮时间)
18:00 镇上无名海鲜排档(老板娘教你挑海鲜)

【周日】
09:00 睡到自然醒,在院子里玩水
12:00 退房,回海口

💡 野路子小贴士:
- 海滩抓螃蟹记得带小桶和手套
- 海鲜排档没招牌,认准"蓝色铁皮房"

[一键预订](link)
```

---

## 🔄 飞轮启动路径

### 第 1 个月:B端试点

- 地推 10 家酒店
- 免费试用 1 个月
- 收集反馈,优化产品

### 第 2 个月:C端冷启动

- 用 B端酒店的内容,生成 30 篇小红书图文
- 标题:"海口周边小众遛娃地,人均 300,孩子玩疯了"
- 引流到微信群:"海口周末野游群"

### 第 3 个月:飞轮启动

- 群里推送周末计划
- 引导订阅"野游记黑卡"(¥9.9/月)
- 用 C端需求,再谈 5 家 B端酒店

### 第 6 个月:飞轮加速

- B端:15 家付费酒店,月收入 ¥4500
- C端:500 付费会员,月收入 ¥5000
- 月营收:¥9500
- **关键:有了数据和案例,可以融资**

---

## 🚀 技术路线图

### Week 1-2:MVP 开发
- [ ] Hotel AI Assistant 核心引擎
- [ ] 微信公众号集成
- [ ] 简单的酒店信息管理后台

### Week 3-4:试点上线
- [ ] 接入 3 家试点酒店
- [ ] 测试 AI 客服效果
- [ ] 收集优化反馈

### Month 2:C端产品
- [ ] 小红书内容生成器
- [ ] 微信群推送系统
- [ ] 会员订阅支付

### Month 3:飞轮优化
- [ ] 数据分析Dashboard
- [ ] 自动化运营工具
- [ ] B/C 端打通

---

## 💡 关键成功因素

1. **B端内容质量** - 在地知识是护城河
2. **C端情绪价值** - 不只是便宜,更是省心
3. **运营节奏** - 每周四固定推送,养成习惯
4. **数据闭环** - 追踪转化,持续优化

---

**这个方案可以立即开始执行!** 🚀
