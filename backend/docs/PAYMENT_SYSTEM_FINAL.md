# ✅ 野游记支付系统 - 最终版

## 🎯 业务模式

**攻略解锁支付 (非会员制)**

- 用户生成攻略后,需要支付解锁查看完整内容
- 每个攻略独立付费,一次购买永久有效
- 旅行攻略: ¥4.80
- 人文历史路线: ¥9.80

## 💰 商品配置

| 商品ID | 名称 | 价格 | 适用类型 |
|--------|------|------|----------|
| guide_travel | 旅行攻略解锁 | ¥4.80 | 普通旅行攻略 |
| guide_history | 人文历史路线解锁 | ¥9.80 | 人文历史主题 |

## 📊 数据库设计

### orders 表 - 订单记录

| 字段 | 类型 | 说明 |
|------|------|------|
| order_no | VARCHAR(32) | 订单号 (WT+时间戳+随机码) |
| openid | VARCHAR(64) | 用户openid |
| product_type | VARCHAR(32) | guide_travel / guide_history |
| product_name | VARCHAR(128) | 包含攻略ID,如 "旅行攻略解锁 - guide_beijing_3days" |
| amount | INTEGER | 金额(分): 480 或 980 |
| status | VARCHAR(32) | pending / paid / expired / cancelled |
| remark | TEXT | 存储 "guide_id:攻略ID" |
| transaction_id | VARCHAR(64) | 微信交易号 |
| created_at | DATETIME | 创建时间 |
| paid_at | DATETIME | 支付时间 |
| expired_at | DATETIME | 过期时间(30分钟) |

**数据库位置:** `/root/clawd/wildtrip/data/orders.db`

## 🔌 核心API

### 1. 获取商品列表
```
GET /api/vip/products
```

### 2. 创建解锁订单
```
POST /api/vip/create_order
Body: {
  "openid": "xxx",
  "product_id": "guide_travel",
  "guide_id": "guide_beijing_3days"
}
```

### 3. 检查攻略解锁
```
GET /api/vip/check_unlock?openid=xxx&guide_id=guide_beijing_3days
```

### 4. 我的已解锁攻略
```
GET /api/vip/my_unlocked?openid=xxx
```

### 5. 支付回调 (微信)
```
POST /api/payment/notify
```

完整API文档: [GUIDE_UNLOCK_API.md](./GUIDE_UNLOCK_API.md)

## 🔄 支付流程

### 用户视角:

```
1. 生成攻略 → 看到预览内容
2. 点击"解锁完整攻略" → 显示价格(¥4.8 或 ¥9.8)
3. 点击"立即支付" → 调起微信支付
4. 完成支付 → 自动跳转,显示完整攻略
5. 下次进入 → 自动识别已解锁,直接显示
```

### 技术流程:

```javascript
// 1. 页面加载,检查是否已解锁
checkUnlock(guideId) → {
  if (unlocked) {
    显示完整内容
  } else {
    显示预览 + 支付按钮
  }
}

// 2. 用户点击支付
createOrder({guideId, productId}) → {
  获取 pay_params
  wx.requestPayment(pay_params) → {
    支付成功 → 轮询订单状态 → 刷新页面
  }
}

// 3. 微信支付回调
/api/payment/notify ← 微信服务器 → {
  更新订单状态: pending → paid
  记录交易号和支付时间
}
```

## 📁 项目文件

```
/root/clawd/backend/
├── models/
│   ├── order.py              # 订单模型
│   └── user.py               # 用户模型
├── services/
│   ├── order_service.py      # 订单服务
│   └── wechat_payment.py     # 微信支付
├── api/
│   ├── vip.py                # 攻略解锁API ⭐
│   └── payment.py            # 支付API
├── docs/
│   ├── GUIDE_UNLOCK_API.md   # 📚 API详细文档
│   └── PAYMENT_SYSTEM_FINAL.md # 本文档
├── test_guide_complete.py    # 完整流程测试
├── test_guide_payment.py     # API测试
└── view_orders.py            # 查看订单

/root/clawd/wildtrip/data/
└── orders.db                 # SQLite数据库
```

## 🧪 测试结果

### 完整流程测试
```bash
cd /root/clawd/backend
python3 test_guide_complete.py
```

**输出:**
```
✅ 旅行攻略解锁: ¥4.8
✅ 人文历史路线解锁: ¥9.8

✅ 订单创建成功: WT20260225003402A8E932
✅ 订单已支付
✅ 攻略已解锁: guide_beijing_3days

已解锁 2 个攻略:
  - guide_beijing_3days: 旅行攻略 (¥4.80)
  - guide_xian_history: 人文历史 (¥9.80)

总订单: 7
已支付: 4 (¥72.60)
```

### 当前订单数据

```
📊 订单数据库 (7 条记录)

订单号                    商品                             金额      状态
WT20260225003402957B8D   人文历史路线解锁                  ¥9.80    ✅已支付
WT20260225003402A8E932   旅行攻略解锁                     ¥4.80    ✅已支付

📈 统计:
   总订单: 7
   已支付: 4 (¥72.60)
   待支付: 3
   
   旅行攻略: 1 个 (¥4.80)
   人文历史: 1 个 (¥9.80)
```

## 🚀 部署状态

### ✅ 已完成

1. **数据库系统**
   - orders 表设计完成
   - 支持攻略ID存储 (remark字段)
   - 订单过期机制 (30分钟)

2. **服务层**
   - OrderService: 订单CRUD + 统计
   - 支持remark参数存储guide_id

3. **API接口**
   - 攻略商品列表 ✅
   - 创建解锁订单 ✅
   - 检查解锁状态 ✅
   - 已解锁列表 ✅
   - 支付回调处理 ✅

4. **测试验证**
   - 完整流程测试通过 ✅
   - API测试通过 ✅
   - 数据库测试通过 ✅

### ⏳ 待完成

1. **微信商户平台**
   - [ ] 开通JSAPI支付权限
   - [ ] 配置支付回调URL: `https://api.wildtrip.com.cn/api/payment/notify`
   - [ ] 测试沙箱支付

2. **小程序端**
   - [ ] 攻略详情页UI
   - [ ] 支付按钮集成
   - [ ] 解锁状态检查
   - [ ] 支付成功处理

3. **可选功能**
   - [ ] 订单管理后台
   - [ ] 支付统计图表
   - [ ] 退款功能

## 💡 小程序集成示例

### 1. 攻略详情页

```javascript
// pages/guide/detail.js
Page({
  data: {
    guideId: '',
    guideType: 'travel', // 或 'history'
    unlocked: false,
    price: 4.80
  },

  async onLoad(options) {
    this.setData({
      guideId: options.id,
      guideType: options.type
    });
    
    // 检查是否已解锁
    await this.checkUnlock();
  },

  async checkUnlock() {
    const res = await wx.request({
      url: 'https://api.wildtrip.com.cn/api/vip/check_unlock',
      data: {
        openid: getApp().globalData.openid,
        guide_id: this.data.guideId
      }
    });
    
    this.setData({
      unlocked: res.data.unlocked
    });
    
    if (res.data.unlocked) {
      this.loadFullGuide();
    } else {
      this.loadPreview();
    }
  },

  async onPayTap() {
    const productId = this.data.guideType === 'travel' 
      ? 'guide_travel' 
      : 'guide_history';
    
    // 创建订单
    const orderRes = await wx.request({
      url: 'https://api.wildtrip.com.cn/api/vip/create_order',
      method: 'POST',
      data: {
        openid: getApp().globalData.openid,
        product_id: productId,
        guide_id: this.data.guideId
      }
    });
    
    if (!orderRes.data.success) {
      wx.showToast({ title: '订单创建失败', icon: 'none' });
      return;
    }
    
    // 调起支付
    wx.requestPayment({
      ...orderRes.data.pay_params,
      success: () => {
        this.checkPaymentStatus(orderRes.data.order.order_no);
      },
      fail: () => {
        wx.showToast({ title: '支付取消', icon: 'none' });
      }
    });
  },

  async checkPaymentStatus(orderNo) {
    const res = await wx.request({
      url: `https://api.wildtrip.com.cn/api/payment/query_order?order_id=${orderNo}`
    });
    
    if (res.data.order.status === 'paid') {
      wx.showToast({ title: '支付成功!', icon: 'success' });
      this.setData({ unlocked: true });
      this.loadFullGuide();
    } else {
      // 继续轮询
      setTimeout(() => this.checkPaymentStatus(orderNo), 2000);
    }
  }
});
```

### 2. 我的已解锁攻略

```javascript
// pages/user/unlocked.js
Page({
  data: {
    guides: []
  },

  async onLoad() {
    const res = await wx.request({
      url: 'https://api.wildtrip.com.cn/api/vip/my_unlocked',
      data: {
        openid: getApp().globalData.openid
      }
    });
    
    this.setData({
      guides: res.data.guides
    });
  }
});
```

## 🔧 运维命令

### 查看订单
```bash
cd /root/clawd/backend
python3 view_orders.py
```

### 重启服务
```bash
systemctl restart wildtrip-backend
systemctl status wildtrip-backend
```

### 查看日志
```bash
tail -f /root/clawd/backend/logs/wildtrip.log
```

### 数据库备份
```bash
cp /root/clawd/wildtrip/data/orders.db \
   /root/clawd/wildtrip/data/orders.db.$(date +%Y%m%d).bak
```

## 📞 支持

- 微信商户平台: https://pay.weixin.qq.com
- 小程序文档: https://developers.weixin.qq.com/miniprogram/dev/

## 📝 更新日志

### 2026-02-25 v1.0
- ✅ 移除VIP会员制度
- ✅ 改为单篇攻略解锁模式
- ✅ 旅行攻略: ¥4.80
- ✅ 人文历史: ¥9.80
- ✅ 支持攻略ID记录和解锁检查
- ✅ 完整测试通过

---

**系统状态:** ✅ 运行中  
**服务地址:** https://api.wildtrip.com.cn  
**数据库:** /root/clawd/wildtrip/data/orders.db  
**文档版本:** v1.0 (2026-02-25 00:34)
