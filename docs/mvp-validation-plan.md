# 野游记 MVP 验证计划（务实版）

## 🎯 核心问题

**Gemini的问题：** 太乐观，忽略了冷启动难题  
**Claude的洞察：** 先验证C端付费意愿，再谈B端合作

**结论：** 分阶段验证，先做最小可用产品（MVP），用数据说话

---

## 📊 三阶段执行路线图

### 阶段一：验证付费意愿（2周，不写代码）

**目标：** 证明有人愿意为这种内容付费

#### 1.1 手动制作 5 篇高质量攻略

**周末游攻略 × 3：**
1. 《海口周末带7岁男孩：恒温泳池民宿 + 野海滩赶海方案》
2. 《海口周末遛娃避坑指南：不去假日海滩，去这3个本地宝藏地》
3. 《海口48小时亲子游：大草坪民宿 + DJI拍摄攻略》

**历史人文攻略 × 2：**
1. 《泉州5天文化深度游：海上丝绸之路遗迹考察》（12000字）
2. 《西安6天历史人文游：跟着唐诗走丝绸之路》（12000字）

#### 1.2 内容结构设计

**周末游（目标¥9.9）：**

```markdown
# 免费部分（30%，约800字）

## 痛点共鸣
你是不是也遇到这些问题：
- 周末不知道带孩子去哪
- 网红景点人太多，孩子玩不开
- OTA订酒店贵，还不知道适不适合带娃

## 方案概览
我为你找到了一个方案：
- 一家有恒温泳池和大草坪的民宿（具体名称付费后可见）
- 步行15分钟到野海滩，下午4点光线最美
- 完整时间表，精确到小时

## 价值承诺
这个方案帮你：
- 省下3小时做攻略的时间
- 避开网红店，省下约¥300冤枉钱
- 获得黄昏海滩的最佳拍摄时间和设备建议

---

💰 **支付 ¥9.9 解锁完整方案**

包含：
- 民宿具体名称和管家微信（直销价比OTA便宜¥150）
- 详细时间表（精确到小时）
- 3家本地人才去的餐厅
- 避坑指南
- 装备清单

---

# 付费部分（70%，约1800字）

（民宿名称、联系方式、详细行程、餐厅推荐...）
```

**历史人文（目标¥99）：**

```markdown
# 免费部分（30%，约3600字）

## 为什么要去泉州？
（历史背景300字 + 行程概览）

## 历史脉络
（宋元时期海上丝绸之路的兴衰史，1000字）

## Day 1 预览
（开元寺的历史故事，500字）

---

💰 **支付 ¥99 解锁完整深度游方案**

还包含：
- 5天完整实地考察路线
- 每个景点的深度历史解读（8000字）
- 推荐书单和纪录片
- 语音讲解词（可在现场边走边听）
- 隐藏古迹地图

---

# 付费部分（70%，约8400字）

（Day 2-5 详细路线 + 深度解读 + 推荐阅读...）
```

#### 1.3 测试渠道

**社群投放：**
- 海口本地亲子群（3-5个，总人数约2000人）
- 小红书（发前30%，引导私信获取完整版）
- 朋友圈（个人号 + 企业微信）

**定价测试：**
- A组：周末游 ¥9.9，历史人文 ¥99
- B组：周末游 ¥6.9，历史人文 ¥69
- C组：周末游 ¥12.9，历史人文 ¥129

**收集数据：**
```
阅读量：X
付费转化：Y
转化率：Y/X
单篇收入：价格 × Y
用户反馈：为什么买/为什么不买
```

#### 1.4 成功标准

**最低验证标准：**
- 周末游转化率 >5%（100人看，5人付费）
- 历史人文转化率 >3%

**理想标准：**
- 周末游转化率 >10%
- 历史人文转化率 >5%

**如果达不到最低标准：**
→ 停止，重新调整内容/定价  
**如果达到标准：**
→ 进入阶段二，开发技术系统

---

### 阶段二：最小可用产品（4周，写代码）

**前提：** 阶段一验证通过

#### 2.1 改造 SEO 静态页面

**技术任务：**

1. **创建内容截断脚本**

```python
# backend/services/content_splitter.py

def split_content(full_markdown: str, content_type: str) -> dict:
    """
    切分内容为免费和付费部分
    
    Args:
        full_markdown: 完整的Markdown内容
        content_type: 'weekend' | 'history'
    
    Returns:
        {
            'free_part': str,     # 30%
            'paid_part': str,     # 70%
            'free_word_count': int,
            'paid_word_count': int
        }
    """
    # 按章节切分
    sections = full_markdown.split('\n## ')
    total_sections = len(sections)
    
    if content_type == 'weekend':
        # 周末游：前3个section免费（概览+住宿推荐+第一个活动）
        free_count = 3
    else:  # history
        # 历史人文：前4个section免费（概览+历史背景+Day1）
        free_count = 4
    
    free_sections = sections[:free_count]
    paid_sections = sections[free_count:]
    
    return {
        'free_part': '\n## '.join(free_sections),
        'paid_part': '\n## '.join(paid_sections),
        'free_word_count': len(''.join(free_sections)),
        'paid_word_count': len(''.join(paid_sections))
    }
```

2. **修改 HTML 模板**

```html
<!-- web/templates/paywall-guide.html -->

<div class="content-free">
    {{ free_content | markdown }}
</div>

<!-- Paywall 付费墙 -->
<div class="paywall">
    <div class="paywall-box">
        <h3>🔒 解锁完整攻略</h3>
        <p>还有 {{ paid_word_count }} 字精彩内容</p>
        
        <div class="price">¥{{ price }}</div>
        
        <!-- 小程序二维码 -->
        <img src="{{ qrcode_url }}" alt="扫码解锁">
        <p>微信扫码打开小程序支付解锁</p>
    </div>
</div>
```

3. **生成小程序二维码**

```python
# backend/services/qrcode_generator.py

def generate_miniprogram_qrcode(guide_id: str) -> str:
    """
    调用微信API生成小程序码
    
    Args:
        guide_id: 攻略ID
    
    Returns:
        二维码图片URL
    """
    # 调用微信接口
    access_token = get_wechat_access_token()
    
    response = requests.post(
        f'https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={access_token}',
        json={
            'scene': f'gid={guide_id}',  # 最多32字符
            'page': 'pages/guide/guide',
            'width': 280
        }
    )
    
    # 保存图片
    qrcode_path = f'/public/qrcodes/{guide_id}.jpg'
    with open(qrcode_path, 'wb') as f:
        f.write(response.content)
    
    return f'https://api.wildtrip.com.cn{qrcode_path}'
```

#### 2.2 小程序支付功能

**文件：** `miniprogram/pages/guide/guide.wxml`

```xml
<view class="guide-container">
  <!-- 免费内容 -->
  <view class="free-content">
    <rich-text nodes="{{ guide.freeContent }}"></rich-text>
  </view>
  
  <!-- 付费内容（已解锁才显示） -->
  <view wx:if="{{ isPaid }}" class="paid-content">
    <rich-text nodes="{{ guide.paidContent }}"></rich-text>
  </view>
  
  <!-- 未解锁显示付费按钮 -->
  <view wx:else class="unlock-box">
    <text class="price">¥{{ guide.price }}</text>
    <button bindtap="onUnlock" type="primary">解锁完整攻略</button>
  </view>
</view>
```

**文件：** `miniprogram/pages/guide/guide.js`

```javascript
Page({
  data: {
    guideId: '',
    guide: null,
    isPaid: false
  },
  
  onLoad(options) {
    // 从二维码 scene 参数获取 guide_id
    const scene = decodeURIComponent(options.scene || '')
    const guideId = scene.split('gid=')[1]
    
    this.setData({ guideId })
    this.loadGuide()
  },
  
  async loadGuide() {
    const res = await wx.request({
      url: `${app.globalData.apiBaseUrl}/guide/${this.data.guideId}`,
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`
      }
    })
    
    this.setData({
      guide: res.data.guide,
      isPaid: res.data.isPaid  // 后端检查用户是否已购买
    })
  },
  
  async onUnlock() {
    // 创建订单
    const orderRes = await wx.request({
      url: `${app.globalData.apiBaseUrl}/order/create`,
      method: 'POST',
      data: {
        guideId: this.data.guideId,
        price: this.data.guide.price
      }
    })
    
    // 调起微信支付
    wx.requestPayment({
      timeStamp: orderRes.data.timeStamp,
      nonceStr: orderRes.data.nonceStr,
      package: orderRes.data.package,
      signType: 'RSA',
      paySign: orderRes.data.paySign,
      success: (res) => {
        wx.showToast({ title: '解锁成功！' })
        this.setData({ isPaid: true })
        this.loadGuide()  // 重新加载，获取付费内容
      }
    })
  }
})
```

#### 2.3 后端支付接口

**文件：** `backend/api/payment.py`

```python
from flask import Blueprint, request, jsonify
from wechatpayv3 import WeChatPay, WeChatPayType
import os

payment_bp = Blueprint('payment', __name__)

# 初始化微信支付
wxpay = WeChatPay(
    wechatpay_type=WeChatPayType.MINIPROG,
    mchid=os.getenv('WECHAT_MCHID'),
    private_key=open(os.getenv('WECHAT_PRIVATE_KEY_PATH')).read(),
    cert_serial_no=os.getenv('WECHAT_CERT_SERIAL_NO'),
    apiv3_key=os.getenv('WECHAT_APIV3_KEY'),
    appid=os.getenv('WECHAT_APPID')
)

@payment_bp.route('/order/create', methods=['POST'])
def create_order():
    """创建支付订单"""
    guide_id = request.json.get('guideId')
    price = request.json.get('price')
    user_id = get_current_user_id()  # 从token获取
    
    # 创建订单记录
    order = Order.create({
        'user_id': user_id,
        'guide_id': guide_id,
        'amount': price,
        'status': 'pending'
    })
    
    # 调用微信支付
    out_trade_no = f'WT{order.id}'
    total = int(price * 100)  # 转为分
    
    result = wxpay.pay(
        description=f'野游记攻略-{guide_id}',
        out_trade_no=out_trade_no,
        amount={'total': total},
        payer={'openid': get_user_openid(user_id)}
    )
    
    return jsonify(result)

@payment_bp.route('/order/callback', methods=['POST'])
def payment_callback():
    """微信支付回调"""
    # 验证签名
    # ...
    
    # 解析通知
    result = wxpay.callback(request.headers, request.data)
    
    # 更新订单状态
    out_trade_no = result.get('out_trade_no')
    order_id = int(out_trade_no[2:])  # 去掉 WT 前缀
    
    Order.update(order_id, {'status': 'paid'})
    
    # 解锁攻略
    UserGuide.create({
        'user_id': Order.get(order_id).user_id,
        'guide_id': Order.get(order_id).guide_id,
        'unlocked_at': datetime.now()
    })
    
    return jsonify({'code': 'SUCCESS'})
```

#### 2.4 数据库设计

```sql
-- 订单表
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(64),
    guide_id VARCHAR(64),
    amount DECIMAL(10,2),
    status ENUM('pending', 'paid', 'refunded'),
    created_at TIMESTAMP,
    paid_at TIMESTAMP
);

-- 用户已解锁攻略表
CREATE TABLE user_guides (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(64),
    guide_id VARCHAR(64),
    unlocked_at TIMESTAMP,
    UNIQUE KEY(user_id, guide_id)
);

-- 攻略表
CREATE TABLE guides (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255),
    content_type ENUM('weekend', 'history'),
    free_content TEXT,
    paid_content TEXT,
    price DECIMAL(10,2),
    view_count INT DEFAULT 0,
    paid_count INT DEFAULT 0,
    created_at TIMESTAMP
);
```

#### 2.5 成功标准

**技术目标（2周内完成）：**
- [x] 静态页面支持 Paywall
- [x] 小程序支付流程跑通
- [x] 后端订单系统上线

**业务目标（上线后2周）：**
- 生成 50 篇 SEO 攻略
- 获得 500 PV
- 完成 10 笔付费（转化率 2%）
- 收入 ¥100

---

### 阶段三：B端SaaS（8周，有C端数据后）

**前提：** C端月收入稳定在 ¥3000+ 以上

#### 3.1 准备谈判筹码

**数据看板：**
```
过去30天数据：
- 攻略曝光：50,000 次
- 付费用户：500 人
- 付费金额：¥5,000
- 转化率：1%

针对海口周边游的攻略：
- 曝光：15,000 次
- 付费：150 人
- 其中咨询民宿：45 人（30%）
```

**话术：**
> "张老板，我们每个月有 1.5万 次海口周末游的搜索流量，其中 30% 的用户会咨询民宿。
> 如果接入我们的系统，这些用户会直接看到您民宿的差异化卖点（比如恒温泳池、步行到野海滩）。
> 我们帮您对接的都是精准客户，比OTA的流量质量高得多。
> 年费 ¥2499，算下来一天不到 ¥7，只要带来 2 个直销订单就回本了。"

#### 3.2 B端功能开发

**最简化版本：**
1. 酒店后台（填写差异化特征表单）
2. 数据看板（展示流量和咨询数）
3. 客户管理（查看咨询记录）

**不做：**
- AI自动访谈（太复杂，改成表单填写）
- 自动匹配（手动审核后再上线）

#### 3.3 冷启动策略

**第一批签约目标：** 海口 5 家民宿

**方式：**
1. 先免费试用 3 个月
2. 证明效果后再收费
3. 签约后给予"首批合作伙伴"标识

**成功标准：**
- 3个月内帮每家民宿带来至少 10 个咨询
- 至少 3 家愿意续费

---

## 📊 关键指标监控

### 阶段一指标
- 手工攻略阅读量
- 付费转化率
- 用户反馈

### 阶段二指标
- SEO流量（PV/UV）
- 付费转化率
- 月收入
- 用户留存

### 阶段三指标
- B端签约数
- B端续费率
- B端客户带来的直销订单数

---

## ⚠️ 风险与应对

### 风险1：C端转化率不达标

**应对：**
- 调整定价（降到 ¥6.9 / ¥69）
- 优化内容质量
- 增加"7天无理由退款"

### 风险2：SEO流量起不来

**应对：**
- 加大长尾词数量（从100篇到500篇）
- 优化页面SEO（标题、描述、结构化数据）
- 投放小红书引流

### 风险3：B端不愿付费

**应对：**
- 延长免费试用期
- 降价到 ¥999/年
- 改成"按效果付费"（每带来一个订单抽成）

---

## 💡 核心原则

1. **先验证，再开发**  
   不要为没验证的想法写代码

2. **数据驱动决策**  
   每个阶段都有清晰的成功标准

3. **聚焦单点突破**  
   同一时间只做一件事

4. **保持灵活调整**  
   如果数据不好，立刻pivot

---

## ⚡ 本周行动（2.20-2.26）

**Day 1-3：** 手写 3 篇周末游攻略  
**Day 4-5：** 手写 2 篇历史人文攻略  
**Day 6-7：** 投放到社群，收集数据

**下周回顾：**
- 如果转化率 >5%，启动阶段二开发
- 如果转化率 <5%，调整内容/定价再测试
