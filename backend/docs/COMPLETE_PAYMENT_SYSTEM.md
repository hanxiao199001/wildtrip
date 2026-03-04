# ✅ 野游记VIP支付系统 - 完整版

## 🎯 系统概述

一个完整的VIP会员支付系统,包含:
- ✅ 订单管理系统
- ✅ 用户VIP管理
- ✅ 微信支付集成
- ✅ 自动激活VIP
- ✅ 数据统计分析

## 📊 数据库设计

### 1. 订单表 (orders)

存储所有订单记录,包括VIP订单和攻略付费订单。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| order_no | VARCHAR(32) | 订单号(WT+时间戳+随机码) |
| openid | VARCHAR(64) | 用户openid |
| product_type | VARCHAR(32) | vip_month/vip_season/vip_year/guide |
| product_name | VARCHAR(128) | 商品名称 |
| amount | INTEGER | 金额(分) |
| status | VARCHAR(32) | pending/paid/expired/cancelled/refunded |
| transaction_id | VARCHAR(64) | 微信交易号 |
| created_at | DATETIME | 创建时间 |
| paid_at | DATETIME | 支付时间 |
| expired_at | DATETIME | 过期时间(默认30分钟) |

**索引:**
- order_no (唯一)
- openid
- (openid, status)
- created_at

### 2. 用户表 (users)

存储用户信息和VIP状态。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| openid | VARCHAR(64) | 微信openid(唯一) |
| nickname | VARCHAR(128) | 昵称 |
| avatar | VARCHAR(512) | 头像URL |
| is_vip | BOOLEAN | 是否VIP |
| vip_expire_at | DATETIME | VIP到期时间 |
| vip_activated_at | DATETIME | 首次激活时间 |
| generate_count | INTEGER | 生成攻略次数 |
| order_count | INTEGER | 订单数量 |
| total_paid | INTEGER | 累计消费(分) |
| created_at | DATETIME | 注册时间 |
| last_login_at | DATETIME | 最后登录 |

**索引:**
- openid (唯一)
- (is_vip, vip_expire_at)

## 💰 VIP商品配置

| ID | 名称 | 价格 | 时长 |
|----|------|------|------|
| vip_month | 野游记会员-1个月 | ¥29 | 30天 |
| vip_season | 野游记会员-3个月 | ¥69 | 90天 |
| vip_year | 野游记会员-1年 | ¥199 | 365天 |

配置文件: `/root/clawd/backend/api/vip.py` 的 `VIP_PRODUCTS`

## 🔌 API 接口文档

### VIP 相关

#### 1. 获取VIP商品列表
```
GET /api/vip/products
```

#### 2. 创建VIP订单
```
POST /api/vip/create_order
Body: {
  "openid": "oxxx",
  "product_id": "vip_month"
}
```

#### 3. 查询VIP状态
```
GET /api/vip/check_status?openid=oxxx
```

### 订单相关

#### 4. 查询订单详情
```
GET /api/payment/query_order?order_id=WT123
```

#### 5. 我的订单列表
```
GET /api/payment/my_orders?openid=oxxx&limit=20
```

#### 6. 取消订单
```
POST /api/payment/cancel_order
Body: {
  "order_id": "WT123"
}
```

#### 7. 订单统计
```
GET /api/payment/stats
```

### 支付回调

#### 8. 微信支付回调 (内部)
```
POST /api/payment/notify
```

## 🔄 支付流程

### 用户端流程:

```
1. 用户打开VIP页面
   ↓
2. 选择VIP套餐 (月/季/年)
   ↓
3. 点击"立即购买"
   ↓
4. 调用 /api/vip/create_order 创建订单
   ↓
5. 获取支付参数 pay_params
   ↓
6. 调起微信支付 wx.requestPayment(pay_params)
   ↓
7. 用户完成支付
   ↓
8. 微信回调 /api/payment/notify
   ↓
9. 订单状态更新为 paid
   ↓
10. 自动激活VIP
   ↓
11. 小程序轮询查询订单状态
   ↓
12. 显示"支付成功,VIP已激活"
```

### 服务端流程:

```python
# 1. 创建订单
order = OrderService.create_order(
    openid=openid,
    product_type='vip_month',
    product_name='野游记会员-1个月',
    amount=2900
)

# 2. 调用微信支付
from services.wechat_payment import get_payment_service
payment = get_payment_service()
pay_params = payment.create_order(
    user_openid=openid,
    order_id=order.order_no,
    total_fee=2900,
    description='野游记会员-1个月'
)

# 3. 支付成功回调处理
OrderService.update_order_status(
    order_no=order_no,
    status=OrderStatus.PAID,
    transaction_id=wechat_transaction_id
)

# 4. 自动激活VIP
UserService.activate_vip(openid, 30)  # 30天

# 5. 更新用户统计
UserService.add_paid_amount(openid, 2900)
```

## 📁 文件结构

```
/root/clawd/backend/
├── models/
│   ├── __init__.py
│   ├── order.py          # 订单模型
│   └── user.py           # 用户模型
├── services/
│   ├── order_service.py  # 订单服务
│   ├── user_service.py   # 用户服务
│   └── wechat_payment.py # 微信支付
├── api/
│   ├── payment.py        # 支付API
│   └── vip.py            # VIP API
├── docs/
│   ├── ORDER_API.md
│   ├── VIP_PAYMENT_API.md
│   └── COMPLETE_PAYMENT_SYSTEM.md
├── init_db.py            # 初始化数据库
├── test_order.py         # 测试订单系统
├── test_vip_api.py       # 测试VIP API
├── test_complete_flow.py # 测试完整流程
└── view_orders.py        # 查看订单数据
```

## 🧪 测试

### 1. 初始化数据库
```bash
cd /root/clawd/backend
python3 init_db.py
```

### 2. 测试订单系统
```bash
python3 test_order.py
```

### 3. 测试VIP API
```bash
python3 test_vip_api.py
```

### 4. 测试完整流程
```bash
python3 test_complete_flow.py
```

### 5. 查看订单数据
```bash
python3 view_orders.py
```

## 📊 当前状态

运行测试后的数据:
- ✅ 总订单: 3个
- ✅ 已支付: 2个 (¥58.00)
- ✅ VIP用户: 1人
- ✅ 数据库: /root/clawd/wildtrip/data/orders.db

## 🚀 部署检查

### 1. 环境变量配置
```bash
# .env 文件必须配置:
WECHAT_APPID=wxb5430a06dd7fa579
WECHAT_SECRET=***REMOVED***
WECHAT_MCHID=1106656739
WECHAT_API_KEY=***REMOVED***
PAYMENT_NOTIFY_URL=https://api.wildtrip.com.cn/api/payment/notify
```

### 2. 微信商户平台
- ✅ 已配置商户号: 1106656739
- ⚠️  需开通JSAPI支付权限
- ⚠️  需配置支付回调URL白名单

### 3. 服务状态
```bash
systemctl status wildtrip-backend
```

### 4. 日志查看
```bash
tail -f /root/clawd/backend/logs/wildtrip.log
```

## 🔧 常用维护命令

### 查看订单
```bash
cd /root/clawd/backend
python3 view_orders.py
```

### 清理过期订单 (定时任务)
```python
from services.order_service import OrderService
OrderService.cancel_expired_orders()
```

### 清理过期VIP (定时任务)
```python
from services.user_service import UserService
UserService.expire_vip_users()
```

### 数据库备份
```bash
cp /root/clawd/wildtrip/data/orders.db \
   /root/clawd/wildtrip/data/orders.db.backup.$(date +%Y%m%d)
```

## 📝 下一步开发

### 短期 (1-2周)
1. ✅ 订单数据库 ← 已完成
2. ✅ VIP用户管理 ← 已完成
3. ✅ 支付API集成 ← 已完成
4. ⏳ 小程序VIP页面UI
5. ⏳ 微信商户号JSAPI权限开通
6. ⏳ 支付测试与调试

### 中期 (2-4周)
7. VIP权益系统 (生成次数限制、无广告等)
8. 订单管理后台
9. 退款功能
10. 优惠券系统

### 长期 (1-2月)
11. 分销系统
12. 会员等级
13. 积分系统
14. 发票系统

## 🎉 总结

完整的VIP支付系统已部署完成!

✅ **已完成:**
- 订单数据库表 (orders)
- 用户数据库表 (users)
- 订单服务 (OrderService)
- 用户服务 (UserService)
- VIP API (/api/vip/*)
- 支付API (/api/payment/*)
- 自动激活VIP
- 完整测试套件

⚠️ **待配置:**
- 微信商户号JSAPI支付权限
- 小程序支付UI

📞 **联系方式:**
- 微信商户平台: pay.weixin.qq.com
- 问题咨询: 微信商户客服

---
完成时间: 2026-02-25 00:27
系统状态: ✅ 运行中
