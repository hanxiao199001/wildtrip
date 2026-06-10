# 野游记后端文档

## 📚 文档索引

### 核心系统文档

1. **[PAYMENT_SYSTEM_FINAL.md](./PAYMENT_SYSTEM_FINAL.md)** - 🎯 **主文档**
   - 攻略解锁支付系统
   - 业务模式说明
   - 完整技术方案
   - 小程序集成示例

2. **[GUIDE_UNLOCK_API.md](./GUIDE_UNLOCK_API.md)** - 📚 **API详细文档**
   - 攻略商品配置
   - 完整API接口
   - 支付流程说明
   - 代码示例

3. **[ORDER_API.md](./ORDER_API.md)** - 订单系统API
   - 数据库表结构
   - OrderService类方法
   - 使用示例

### 历史文档 (已废弃)

4. **[COMPLETE_PAYMENT_SYSTEM.md](./COMPLETE_PAYMENT_SYSTEM.md)** - ~~VIP会员系统~~
   - 已改为攻略解锁模式
   - 仅供参考

5. **[VIP_PAYMENT_API.md](./VIP_PAYMENT_API.md)** - ~~VIP API~~
   - 已废弃
   
6. **[ORDER_SETUP_COMPLETE.md](./ORDER_SETUP_COMPLETE.md)** - 搭建记录
   - 创建的文件列表
   - 数据库信息
   - 常用命令

## 🗂️ 项目结构

```
backend/
├── models/              # 数据模型
│   ├── order.py        # 订单模型
│   └── user.py         # 用户模型
│
├── services/            # 业务逻辑
│   ├── order_service.py    # 订单服务
│   ├── user_service.py     # 用户服务
│   └── wechat_payment.py   # 微信支付
│
├── api/                 # API路由
│   ├── payment.py      # 支付API
│   ├── vip.py          # VIP API
│   ├── generate.py     # 攻略生成
│   ├── guides.py       # 攻略列表
│   └── user.py         # 用户API
│
├── docs/               # 📚 文档目录 (当前)
│
├── tests/              # 测试脚本
│   ├── test_order.py
│   ├── test_vip_api.py
│   └── test_complete_flow.py
│
└── app.py             # 主应用
```

## 🚀 快速开始

### 1. 初始化数据库
```bash
cd /root/clawd/backend
python3 init_db.py
```

### 2. 运行测试
```bash
# 测试订单系统
python3 test_order.py

# 测试VIP API
python3 test_vip_api.py

# 测试完整流程
python3 test_complete_flow.py
```

### 3. 查看数据
```bash
# 查看所有订单
python3 view_orders.py

# 查看数据库
sqlite3 /root/clawd/wildtrip/data/orders.db "SELECT * FROM orders;"
sqlite3 /root/clawd/wildtrip/data/orders.db "SELECT * FROM users;"
```

### 4. 启动服务
```bash
systemctl start wildtrip-backend
systemctl status wildtrip-backend
```

## 📊 数据库位置

```
/root/clawd/wildtrip/data/orders.db
```

包含两张表:
- **orders** - 订单表
- **users** - 用户表

## 🔌 API 端点

### 攻略解锁
- `GET  /api/vip/products` - 获取攻略商品 (¥4.8/¥9.8)
- `POST /api/vip/create_order` - 创建解锁订单
- `GET  /api/vip/check_unlock` - 检查攻略解锁状态
- `GET  /api/vip/my_unlocked` - 我的已解锁攻略

### 订单相关
- `GET  /api/payment/query_order` - 查询订单
- `GET  /api/payment/my_orders` - 我的订单
- `POST /api/payment/cancel_order` - 取消订单
- `GET  /api/payment/stats` - 订单统计
- `POST /api/payment/notify` - 支付回调 (微信)

### 攻略相关
- `POST /api/generate` - 生成攻略
- `GET  /api/guides` - 攻略列表
- `GET  /api/task/:id` - 任务状态

## 🧪 测试结果

当前测试数据:
- ✅ 总订单: 7个
- ✅ 已支付: 4个 (¥72.60)
- ✅ 待支付: 3个
- ✅ 旅行攻略: 1个 (¥4.80)
- ✅ 人文历史: 1个 (¥9.80)

## 📝 配置检查

### .env 必需配置
```bash
# 微信小程序
WECHAT_APPID=<YOUR_APPID>
WECHAT_SECRET=<YOUR_WECHAT_SECRET>

# 微信商户号
WECHAT_MCHID=1106656739
WECHAT_API_KEY=<YOUR_WECHAT_PAY_API_KEY>

# 回调地址
PAYMENT_NOTIFY_URL=https://api.wildtrip.com.cn/api/payment/notify

# 数据库
DB_DIR=/root/clawd/wildtrip/data
```

## ⚠️ 待完成事项

### 微信商户平台
- [ ] 开通JSAPI支付权限
- [ ] 配置支付回调URL白名单
- [ ] 测试支付流程

### 小程序端
- [ ] 攻略详情页UI
- [ ] 支付流程集成
- [ ] 解锁状态检查
- [ ] 已解锁攻略列表

### 后续功能
- [ ] 订单管理后台
- [ ] 退款功能
- [ ] 优惠券系统

## 📞 支持

- 微信商户平台: https://pay.weixin.qq.com
- 小程序文档: https://developers.weixin.qq.com/miniprogram/dev/

## 📅 更新日志

### 2026-02-25 v2.0 - 攻略解锁模式
- ✅ 移除VIP会员制度
- ✅ 改为单篇攻略解锁
- ✅ 旅行攻略: ¥4.80
- ✅ 人文历史: ¥9.80
- ✅ 支持攻略ID记录
- ✅ 解锁状态检查
- ✅ 完整测试通过

### 2026-02-25 v1.0 - 订单系统搭建
- ✅ 创建订单数据库表
- ✅ 创建用户数据库表
- ✅ 实现订单服务 (OrderService)
- ✅ 实现用户服务 (UserService)
- ✅ 集成支付API

---

最后更新: 2026-02-25 00:34
