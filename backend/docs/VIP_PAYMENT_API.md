# VIP会员支付系统 API 文档

## 🎯 功能概述

完整的VIP会员支付系统,包括:
- ✅ 订单数据库管理
- ✅ VIP商品配置
- ✅ 订单创建与查询
- ✅ 支付回调处理
- ✅ 自动激活VIP
- ✅ 订单统计分析

## 📦 VIP商品配置

| 商品ID | 名称 | 价格 | 时长 |
|--------|------|------|------|
| vip_month | 野游记会员-1个月 | ¥29 | 30天 |
| vip_season | 野游记会员-3个月 | ¥69 | 90天 |
| vip_year | 野游记会员-1年 | ¥199 | 365天 |

## 🔌 API 接口

### 1. 获取VIP商品列表

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
      "id": "vip_month",
      "name": "野游记会员 - 1个月",
      "amount": 2900,
      "price": "29.00",
      "duration_days": 30
    },
    ...
  ]
}
```

### 2. 创建VIP订单

**请求:**
```
POST /api/vip/create_order
Content-Type: application/json

{
  "openid": "用户openid",
  "product_id": "vip_month"
}
```

**响应:**
```json
{
  "success": true,
  "order": {
    "order_no": "WT20260225002048B62542",
    "product_name": "野游记会员 - 1个月",
    "amount": 2900,
    "status": "pending",
    "created_at": "2026-02-25 00:20:48",
    "expired_at": "2026-02-25 00:50:48"
  },
  "pay_params": {
    "appId": "wxb5430a06dd7fa579",
    "timeStamp": "1740414048",
    "nonceStr": "abc123",
    "package": "prepay_id=wx25002048...",
    "signType": "MD5",
    "paySign": "..."
  },
  "is_existing": false
}
```

**特性:**
- 如果有未支付订单,自动返回已有订单
- 自动过滤已过期订单
- 支持订单重复提交检测

### 3. 查询订单状态

**请求:**
```
GET /api/payment/query_order?order_id=WT20260225002048B62542
```

**响应:**
```json
{
  "success": true,
  "order": {
    "id": 1,
    "order_no": "WT20260225002048B62542",
    "openid": "oxxx",
    "product_type": "vip_month",
    "product_name": "野游记会员 - 1个月",
    "amount": 2900,
    "status": "paid",
    "transaction_id": "wx_123456",
    "created_at": "2026-02-25 00:20:48",
    "paid_at": "2026-02-25 00:21:30"
  }
}
```

### 4. 获取我的订单列表

**请求:**
```
GET /api/payment/my_orders?openid=oxxx&limit=20
```

**响应:**
```json
{
  "success": true,
  "orders": [
    {
      "order_no": "WT20260225002048B62542",
      "product_name": "野游记会员 - 1个月",
      "amount": 2900,
      "status": "paid",
      "created_at": "2026-02-25 00:20:48"
    },
    ...
  ],
  "total": 5
}
```

### 5. 取消订单

**请求:**
```
POST /api/payment/cancel_order
Content-Type: application/json

{
  "order_id": "WT20260225002048B62542"
}
```

**响应:**
```json
{
  "success": true,
  "message": "订单已取消"
}
```

**限制:**
- 只能取消状态为 `pending` 的订单
- 已支付/已过期订单无法取消

### 6. 订单统计 (管理员)

**请求:**
```
GET /api/payment/stats?start_date=2026-02-01&end_date=2026-02-28
```

**响应:**
```json
{
  "success": true,
  "stats": {
    "total": 100,
    "paid": 80,
    "amount": 232000,
    "pending": 15
  }
}
```

### 7. 支付回调 (微信回调)

**请求:**
```
POST /api/payment/notify
Content-Type: application/xml

<xml>
  <return_code><![CDATA[SUCCESS]]></return_code>
  <result_code><![CDATA[SUCCESS]]></return_code>
  <out_trade_no><![CDATA[WT20260225002048B62542]]></out_trade_no>
  <transaction_id><![CDATA[4200001234567890]]></transaction_id>
  <total_fee>2900</total_fee>
  ...
</xml>
```

**响应:**
```xml
<xml>
  <return_code><![CDATA[SUCCESS]]></return_code>
  <return_msg><![CDATA[OK]]></return_msg>
</xml>
```

**处理流程:**
1. 验证微信签名
2. 更新订单状态为 `paid`
3. 如果是VIP订单,自动激活VIP
4. 发送支付成功通知

### 8. 查询VIP状态

**请求:**
```
GET /api/vip/check_status?openid=oxxx
```

**响应:**
```json
{
  "success": true,
  "is_vip": true,
  "expire_at": "2026-03-25 00:00:00",
  "days_left": 28
}
```

## 🔄 订单状态流转

```
pending (待支付)
    ↓ 用户支付成功
paid (已支付) ──→ 自动激活VIP (如果是VIP订单)
    ↓ 超时未支付
expired (已过期)
    ↓ 用户取消
cancelled (已取消)
    ↓ 申请退款
refunding (退款中)
    ↓
refunded (已退款)
```

## 💰 支付流程

### 小程序端:

1. **获取商品列表**
   ```javascript
   wx.request({
     url: 'https://api.wildtrip.com.cn/api/vip/products',
     success: (res) => {
       console.log(res.data.products)
     }
   })
   ```

2. **创建订单**
   ```javascript
   wx.request({
     url: 'https://api.wildtrip.com.cn/api/vip/create_order',
     method: 'POST',
     data: {
       openid: app.globalData.openid,
       product_id: 'vip_month'
     },
     success: (res) => {
       const { pay_params } = res.data
       // 调起微信支付
       wx.requestPayment({
         ...pay_params,
         success: () => {
           console.log('支付成功')
         }
       })
     }
   })
   ```

3. **查询订单状态**
   ```javascript
   wx.request({
     url: 'https://api.wildtrip.com.cn/api/payment/query_order',
     data: {
       order_id: order_no
     },
     success: (res) => {
       if (res.data.order.status === 'paid') {
         console.log('已支付')
       }
     }
   })
   ```

## 📝 开发注意事项

### 1. 微信支付配置

在 `.env` 中配置:
```bash
# 微信小程序
WECHAT_APPID=wxb5430a06dd7fa579
WECHAT_SECRET=***REMOVED***

# 微信商户号
WECHAT_MCHID=1106656739
WECHAT_API_KEY=***REMOVED***

# 支付回调地址
PAYMENT_NOTIFY_URL=https://api.wildtrip.com.cn/api/payment/notify
```

### 2. 商户平台配置

需要在微信商户平台开通:
- ✅ JSAPI支付 (小程序支付)
- ✅ 设置回调URL白名单
- ✅ 配置API密钥

### 3. 订单安全

- ✅ 订单30分钟自动过期
- ✅ 防止重复支付
- ✅ 支付回调验签
- ✅ 订单状态幂等更新

### 4. 数据库

订单数据存储在:
```
/root/clawd/wildtrip/data/orders.db
```

查看订单:
```bash
cd /root/clawd/backend
python3 view_orders.py
```

## 🧪 测试

运行完整测试:
```bash
cd /root/clawd/backend
python3 test_vip_api.py
```

## 📊 当前状态

✅ 已完成:
- 订单数据库设计
- VIP商品配置
- 订单创建API
- 订单查询API
- 支付回调处理
- 订单统计API

⏳ 待完成:
- 用户VIP状态管理
- VIP权益系统
- 退款处理
- 发票系统

## 🚀 下一步

1. 创建用户表,存储VIP状态
2. 实现VIP激活逻辑
3. 添加VIP权益检查
4. 小程序支付UI集成
5. 订单管理后台

---
更新时间: 2026-02-25 00:24
