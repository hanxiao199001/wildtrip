# 野游记攻略解锁支付API

## 🎯 业务模式

**单篇攻略解锁,无会员制度**

- 用户生成攻略后,需要支付解锁才能查看完整内容
- 每个攻略独立付费,一次购买永久有效
- 不同类型攻略价格不同

## 💰 商品配置

| 商品ID | 名称 | 价格 | 类型 |
|--------|------|------|------|
| guide_travel | 旅行攻略解锁 | ¥4.80 | travel |
| guide_history | 人文历史路线解锁 | ¥9.80 | history |

配置文件: `/root/clawd/backend/api/vip.py` → `GUIDE_PRODUCTS`

## 🔌 API 接口

### 1. 获取攻略商品列表

**请求:**
```
GET /api/vip/products
```

**响应:**
```json
{
  "success": true,
  "products": [
    {
      "id": "guide_travel",
      "name": "旅行攻略解锁",
      "amount": 480,
      "price": "4.80",
      "type": "travel"
    },
    {
      "id": "guide_history",
      "name": "人文历史路线解锁",
      "amount": 980,
      "price": "9.80",
      "type": "history"
    }
  ]
}
```

### 2. 创建攻略解锁订单

**请求:**
```
POST /api/vip/create_order
Content-Type: application/json

{
  "openid": "用户openid",
  "product_id": "guide_travel",
  "guide_id": "guide_beijing_3days"
}
```

**响应:**
```json
{
  "success": true,
  "order": {
    "order_no": "WT20260225003402A8E932",
    "product_name": "旅行攻略解锁 - guide_beijing_3days",
    "amount": 480,
    "status": "pending",
    "created_at": "2026-02-25 00:34:02",
    "expired_at": "2026-02-25 01:04:02",
    "remark": "guide_id:guide_beijing_3days"
  },
  "pay_params": {
    "appId": "<YOUR_APPID>",
    "timeStamp": "1740414842",
    "nonceStr": "abc123",
    "package": "prepay_id=wx25003402...",
    "signType": "MD5",
    "paySign": "..."
  },
  "guide_id": "guide_beijing_3days"
}
```

### 3. 检查攻略是否已解锁

**请求:**
```
GET /api/vip/check_unlock?openid=xxx&guide_id=guide_beijing_3days
```

**响应 - 已解锁:**
```json
{
  "success": true,
  "unlocked": true,
  "order_no": "WT20260225003402A8E932",
  "paid_at": "2026-02-25T00:34:02.441000",
  "amount": 480
}
```

**响应 - 未解锁:**
```json
{
  "success": true,
  "unlocked": false
}
```

### 4. 我的已解锁攻略列表

**请求:**
```
GET /api/vip/my_unlocked?openid=xxx
```

**响应:**
```json
{
  "success": true,
  "guides": [
    {
      "guide_id": "guide_beijing_3days",
      "product_name": "旅行攻略解锁 - guide_beijing_3days",
      "product_type": "guide_travel",
      "amount": 480,
      "order_no": "WT20260225003402A8E932",
      "paid_at": "2026-02-25T00:34:02.441000"
    },
    {
      "guide_id": "guide_xian_history",
      "product_name": "人文历史路线解锁 - guide_xian_history",
      "product_type": "guide_history",
      "amount": 980,
      "order_no": "WT20260225003402957B8D",
      "paid_at": "2026-02-25T00:34:02.446000"
    }
  ],
  "total": 2
}
```

## 🔄 支付流程

### 小程序端完整流程:

```javascript
// 1. 用户生成攻略后,显示"解锁完整内容"按钮
//    根据攻略类型(travel/history)选择对应的product_id

const guideType = 'travel'; // 或 'history'
const guideId = 'guide_beijing_3days';
const productId = guideType === 'travel' ? 'guide_travel' : 'guide_history';

// 2. 创建订单
wx.request({
  url: 'https://api.wildtrip.com.cn/api/vip/create_order',
  method: 'POST',
  data: {
    openid: app.globalData.openid,
    product_id: productId,
    guide_id: guideId
  },
  success: (res) => {
    if (res.data.success) {
      const { pay_params } = res.data;
      
      // 3. 调起微信支付
      wx.requestPayment({
        ...pay_params,
        success: () => {
          console.log('支付成功');
          
          // 4. 轮询查询订单状态
          checkPaymentStatus(res.data.order.order_no);
        },
        fail: () => {
          console.log('支付取消');
        }
      });
    }
  }
});

// 5. 查询支付结果
function checkPaymentStatus(orderNo) {
  wx.request({
    url: `https://api.wildtrip.com.cn/api/payment/query_order?order_id=${orderNo}`,
    success: (res) => {
      if (res.data.order.status === 'paid') {
        // 支付成功,刷新页面显示完整攻略
        console.log('攻略已解锁');
        loadFullGuide(guideId);
      } else {
        // 继续轮询
        setTimeout(() => checkPaymentStatus(orderNo), 2000);
      }
    }
  });
}

// 6. 页面加载时检查是否已解锁
wx.request({
  url: `https://api.wildtrip.com.cn/api/vip/check_unlock`,
  data: {
    openid: app.globalData.openid,
    guide_id: guideId
  },
  success: (res) => {
    if (res.data.unlocked) {
      // 已解锁,直接显示完整内容
      loadFullGuide(guideId);
    } else {
      // 未解锁,显示预览+解锁按钮
      showPreview(guideId);
    }
  }
});
```

## 📝 业务逻辑说明

### 订单创建

1. **根据攻略类型自动选择商品:**
   - 旅行攻略 → `guide_travel` (¥4.80)
   - 人文历史 → `guide_history` (¥9.80)

2. **订单信息记录:**
   - `product_name`: 包含攻略ID,如 "旅行攻略解锁 - guide_beijing_3days"
   - `remark`: 存储 "guide_id:攻略ID",用于后续解锁检查

3. **订单有效期:**
   - 30分钟内未支付自动过期

### 解锁检查

1. **检查逻辑:**
   - 查询用户所有已支付订单
   - 匹配订单的 `remark` 字段中的 `guide_id`
   - 如果匹配到,则该攻略已解锁

2. **返回信息:**
   - 已解锁: 返回订单号、支付时间、金额
   - 未解锁: 返回 `unlocked: false`

### 支付回调

微信支付成功后,回调 `/api/payment/notify`:
1. 更新订单状态为 `paid`
2. 记录微信交易号
3. 记录支付时间
4. 日志输出解锁信息

## 🧪 测试

### 完整流程测试
```bash
cd /root/clawd/backend
python3 test_guide_complete.py
```

**测试结果:**
```
✅ 旅行攻略: 1 个 (¥4.80)
✅ 人文历史: 1 个 (¥9.80)
✅ 已解锁 2 个攻略
✅ 总订单: 7
✅ 已支付: 4 (¥72.60)
```

### API测试
```bash
cd /root/clawd/backend
python3 test_guide_payment.py
```

## 📊 当前数据

```
订单号                    商品                             金额      状态
WT20260225003402957B8D   人文历史路线解锁                  ¥9.80    ✅已支付
WT20260225003402A8E932   旅行攻略解锁                     ¥4.80    ✅已支付

统计:
  总订单: 7
  已支付: 4 (¥72.60)
  旅行攻略: 1 个 (¥4.80)
  人文历史: 1 个 (¥9.80)
```

## ⚠️ 注意事项

### 1. 攻略ID命名规范

建议使用清晰的命名:
- `guide_{city}_{days}days` - 旅行攻略,如 `guide_beijing_3days`
- `guide_{city}_history` - 人文历史,如 `guide_xian_history`

### 2. 类型判断

在生成攻略时,需要标记攻略类型(travel/history),用于:
- 选择正确的商品(4.8元 或 9.8元)
- 显示对应的价格

### 3. 防重复购买

检查逻辑应在前端实现:
```javascript
// 先检查是否已解锁
const unlockResult = await checkUnlock(guideId);
if (unlockResult.unlocked) {
  // 已解锁,直接显示
  showFullGuide();
} else {
  // 未解锁,显示支付按钮
  showPayButton();
}
```

### 4. 支付状态轮询

建议轮询参数:
- 间隔: 2秒
- 最多轮询: 15次 (30秒)
- 超时后提示用户刷新页面

## 🚀 下一步

1. ✅ 订单数据库 - 已完成
2. ✅ 攻略解锁API - 已完成
3. ⏳ 微信商户号开通JSAPI支付
4. ⏳ 小程序支付UI
5. ⏳ 攻略详情页集成解锁检查

---
更新时间: 2026-02-25 00:34
文档版本: v1.0
