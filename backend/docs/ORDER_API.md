# 订单系统 API 文档

## 数据库表结构

### orders 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| order_no | VARCHAR(32) | 订单号(唯一)，格式: WT+时间戳+随机码 |
| openid | VARCHAR(64) | 用户openid |
| product_type | VARCHAR(32) | 商品类型: vip_month, vip_year |
| product_name | VARCHAR(128) | 商品名称 |
| amount | INTEGER | 订单金额(分) |
| payment_method | VARCHAR(32) | 支付方式: wechat |
| transaction_id | VARCHAR(64) | 微信支付交易号 |
| prepay_id | VARCHAR(128) | 微信预支付ID |
| status | VARCHAR(32) | 订单状态 |
| created_at | DATETIME | 创建时间 |
| paid_at | DATETIME | 支付时间 |
| expired_at | DATETIME | 过期时间 |
| refunded_at | DATETIME | 退款时间 |
| client_ip | VARCHAR(64) | 客户端IP |
| user_agent | VARCHAR(512) | 用户代理 |
| remark | TEXT | 备注 |

### 订单状态

- `pending` - 待支付
- `paid` - 已支付
- `refunding` - 退款中
- `refunded` - 已退款
- `expired` - 已过期
- `cancelled` - 已取消

### 索引

- `order_no` - 唯一索引
- `openid` - 普通索引
- `transaction_id` - 普通索引
- `status` - 普通索引
- `(openid, status)` - 复合索引
- `created_at` - 普通索引

## OrderService 类

### 方法

#### create_order()

创建新订单

```python
order = OrderService.create_order(
    openid='oxxx',           # 用户openid
    product_type='vip_month', # 商品类型
    product_name='野游记会员-1个月',
    amount=2900,             # 金额(分)
    client_ip='127.0.0.1',   # 可选
    user_agent='xxx',        # 可选
    expire_minutes=30        # 可选，默认30分钟
)
```

#### get_order()

获取订单详情

```python
order = OrderService.get_order(order_no)
```

#### update_order_status()

更新订单状态

```python
success = OrderService.update_order_status(
    order_no='WT20260225xxx',
    status=OrderStatus.PAID,
    transaction_id='wx_xxx',  # 可选
    remark='xxx'              # 可选
)
```

#### get_user_orders()

获取用户订单列表

```python
orders = OrderService.get_user_orders(
    openid='oxxx',
    limit=20  # 可选，默认20
)
```

#### get_pending_orders()

获取待支付订单（未过期）

```python
orders = OrderService.get_pending_orders(openid='oxxx')
```

#### cancel_expired_orders()

取消过期订单（定时任务）

```python
count = OrderService.cancel_expired_orders()
```

#### get_stats()

获取订单统计

```python
stats = OrderService.get_stats(
    start_date=None,  # 可选
    end_date=None     # 可选
)
# 返回: {
#   'total': 10,      # 总订单数
#   'paid': 8,        # 已支付数
#   'amount': 23200,  # 总金额(分)
#   'pending': 2      # 待支付数
# }
```

## 使用示例

### 1. 初始化数据库

```bash
cd /root/clawd/backend
python3 init_db.py
```

### 2. 创建订单（在Flask应用中）

```python
from flask import Flask
from models import db
from services.order_service import OrderService

with app.app_context():
    order = OrderService.create_order(
        openid=user_openid,
        product_type='vip_month',
        product_name='野游记会员 - 1个月',
        amount=2900,
        client_ip=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
```

### 3. 支付回调处理

```python
# 支付成功后
OrderService.update_order_status(
    order_no=order_no,
    status=OrderStatus.PAID,
    transaction_id=wechat_transaction_id
)
```

### 4. 查询用户订单

```python
orders = OrderService.get_user_orders(openid)
return jsonify({
    'orders': [order.to_dict() for order in orders]
})
```

## 测试

运行测试脚本:

```bash
cd /root/clawd/backend
python3 test_order.py
```

## 文件位置

- 数据库: `/root/clawd/wildtrip/data/orders.db`
- Model定义: `/root/clawd/backend/models/order.py`
- 服务类: `/root/clawd/backend/services/order_service.py`
- 初始化脚本: `/root/clawd/backend/init_db.py`
- 测试脚本: `/root/clawd/backend/test_order.py`

## 下一步

1. 在 `api/payment.py` 中集成 OrderService
2. 创建订单时生成微信支付预支付单
3. 处理支付回调，更新订单状态
4. 支付成功后激活用户VIP
