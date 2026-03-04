# 🎉 攻略解锁支付 - 测试指南

## ✅ 已完成的修改

### 1. guide-detail.js
- ✅ 引入支付模块 `unlock-payment.js`
- ✅ 添加解锁状态数据 (`isUnlocked`, `checkingUnlock`, `guideType`)
- ✅ 添加 `checkUnlockStatus()` 方法 - 检查是否已解锁
- ✅ 添加 `onUnlockGuide()` 方法 - 触发支付流程
- ✅ 在 `onLoad` 中自动检查解锁状态
- ✅ 在 `loadGuideDetail` 中判断攻略类型

### 2. guide-detail.wxml
- ✅ 添加解锁提示卡片（未解锁时显示）
- ✅ 添加已解锁徽章（已解锁时显示）
- ✅ 修改完整攻略内容只在解锁后显示 (`wx:if="{{article && isUnlocked}}"`)

### 3. guide-detail.wxss
- ✅ 添加解锁提示卡片样式（紫色渐变背景）
- ✅ 添加立即解锁按钮样式（白色按钮）
- ✅ 添加已解锁徽章样式（绿色渐变）
- ✅ 添加锁图标摇晃动画

## 📱 测试流程

### 第一步：在微信开发者工具中打开小程序

```bash
# 小程序代码位置
/root/clawd/miniprogram/
```

### 第二步：测试未解锁状态

1. 打开任意攻略详情页
2. 应该看到：
   - ✨ 行程亮点（正常显示）
   - 🔒 紫色解锁提示卡片
   - 💰 价格显示（旅行攻略 ¥4.80 或 人文历史 ¥9.80）
   - 🔓 "立即解锁"按钮
   - ❌ **不显示**完整攻略内容

### 第三步：测试支付流程

1. 点击"立即解锁"按钮
2. 弹出支付确认对话框
3. 显示：
   - 攻略标题
   - 商品类型（旅行攻略/人文历史路线）
   - 价格
4. 点击"立即支付"
5. 调起微信支付界面
6. 完成支付

### 第四步：测试已解锁状态

支付成功后：
1. ✅ 显示绿色"已解锁完整攻略"徽章
2. 📖 显示完整攻略内容
3. 🔒 解锁提示消失

### 第五步：测试持久化

1. 退出攻略详情页
2. 重新进入同一攻略
3. 应该自动识别为已解锁状态
4. 直接显示完整内容

## 🔍 后台验证

### 查看订单记录

```bash
cd /root/clawd/backend
python3 view_orders.py
```

应该看到新创建的订单：
- 订单号：WT开头
- 商品：旅行攻略解锁 或 人文历史路线解锁
- 金额：¥4.80 或 ¥9.80
- 状态：✅已支付

### 查看支付日志

```bash
# 实时查看Flask日志
tail -f /root/clawd/backend/flask.log

# 查找支付相关日志
grep "攻略解锁\|payment" /root/clawd/backend/flask.log | tail -20
```

## 🎨 UI 效果预览

### 未解锁状态
```
┌─────────────────────────────────┐
│         行程亮点 ✨               │
│   D1 抵达北京 体验老北京          │
│   D2 故宫一日游                  │
│   D3 长城 + 颐和园               │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│            🔒                    │
│      完整攻略需要解锁              │
│  解锁后可查看完整行程、推荐酒店等   │
│                                 │
│  旅行攻略          ¥4.80         │
│                                 │
│    [ 🔓 立即解锁 ]               │
└─────────────────────────────────┘
```

### 已解锁状态
```
┌─────────────────────────────────┐
│  ✅  已解锁完整攻略                │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│      完整攻略 📖                  │
│                                 │
│  Day 1: 抵达北京                 │
│  上午：首都机场接机...            │
│  下午：入住酒店...               │
│  ...（完整内容）                 │
└─────────────────────────────────┘
```

## ⚠️ 常见问题

### 1. 支付失败：无效的openid
**原因**：用户未登录或 openid 未获取
**解决**：
```javascript
// 在 app.js 的 onLaunch 中确保已获取 openid
wx.login({
  success: (res) => {
    // 调用后端获取 openid
  }
})
```

### 2. 点击解锁按钮无反应
**检查**：
- 打开控制台查看错误信息
- 确认 `unlock-payment.js` 文件存在
- 确认后端 API 正常运行

### 3. 支付成功但未显示内容
**检查**：
- 支付回调是否成功（查看后端日志）
- 订单状态是否更新为 `paid`
- 刷新页面后是否显示

### 4. 测试环境如何模拟支付？

**方法1：直接修改数据库**
```bash
cd /root/clawd/backend
python3 << EOF
from services.order_service import OrderService
from models import OrderStatus

# 创建测试订单并标记为已支付
order = OrderService.create_order(
    openid='test_user_openid',
    product_type='guide_travel',
    product_name='旅行攻略解锁 - guide_test_001',
    amount=480,
    remark='guide_id:guide_test_001'
)
OrderService.update_order_status(order.order_no, OrderStatus.PAID)
print(f"✅ 测试订单已创建: {order.order_no}")
EOF
```

**方法2：小额真实支付测试**
- 使用 0.01 元测试（需要修改商品价格）
- 测试完成后退款

## 🚀 上线前检查清单

- [ ] 微信支付功能已开通
- [ ] request域名已配置：`https://api.wildtrip.com.cn`
- [ ] 所有测试场景通过
- [ ] 支付回调正常工作
- [ ] 解锁状态持久化正常
- [ ] 价格显示正确（¥4.80 / ¥9.80）
- [ ] UI/UX 符合预期
- [ ] 错误提示友好

## 📊 数据统计

上线后可以通过以下方式查看数据：

```bash
# 查看总订单数和销售额
cd /root/clawd/backend
python3 view_orders.py

# 按商品类型统计
sqlite3 /root/clawd/wildtrip/data/orders.db "
SELECT 
  product_type,
  COUNT(*) as count,
  SUM(amount)/100.0 as total_yuan
FROM orders 
WHERE status='paid'
GROUP BY product_type;
"
```

## 🎯 下一步优化

完成基础功能后，可以考虑：

1. **优惠活动**
   - 首单优惠（新用户首次解锁 8折）
   - 限时特价（节假日促销）

2. **分享解锁**
   - 分享给3个好友，免费解锁

3. **订单管理页**
   - 在用户中心显示购买记录
   - 支持查看已解锁的所有攻略

4. **退款功能**
   - 7天内可申请退款

5. **数据分析**
   - 统计最受欢迎的攻略
   - 转化率分析

---

🎉 所有功能已集成完毕！现在可以开始测试了！
