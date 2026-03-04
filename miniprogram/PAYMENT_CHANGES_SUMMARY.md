# 📝 攻略解锁支付 - 修改内容总结

## 🎯 修改的文件

```
/root/clawd/miniprogram/pages/guide-detail/
├── guide-detail.js      ✅ 已修改（添加支付逻辑）
├── guide-detail.wxml    ✅ 已修改（添加解锁UI）
├── guide-detail.wxss    ✅ 已修改（添加样式）
└── unlock-payment.js    ✅ 新增（支付模块）
```

## 📋 代码修改详情

### 1. guide-detail.js 的修改

#### 添加的引入（第3行）
```javascript
const unlockPayment = require('./unlock-payment.js')
```

#### 添加的数据字段（data对象中）
```javascript
// 支付解锁相关
isUnlocked: false,     // 是否已解锁
checkingUnlock: true,  // 正在检查解锁状态
guideType: 'travel'    // 攻略类型 travel/history
```

#### 修改的 onLoad 方法
```javascript
if (slug) {
  // ✨ 新增：检查解锁状态
  this.checkUnlockStatus()
  // 加载攻略
  this.loadGuideDetail()
}
```

#### 修改的 loadGuideDetail 方法（末尾添加）
```javascript
// ✨ 新增：判断攻略类型
let guideType = 'travel'
if (guide.category && (guide.category.includes('历史') || 
    guide.category.includes('文化') || guide.category.includes('人文'))) {
  guideType = 'history'
}
this.setData({ guideType })
```

#### 新增的方法（3个）
```javascript
// 1. 检查攻略解锁状态
async checkUnlockStatus() { ... }

// 2. 点击解锁按钮
onUnlockGuide() { ... }
```

### 2. guide-detail.wxml 的修改

#### 在"行程亮点"后添加（约30行）
```xml
<!-- 🔐 解锁状态提示 -->
<view class="unlock-status" wx:if="{{!checkingUnlock}}">
  <!-- 未解锁状态 -->
  <view class="unlock-prompt" wx:if="{{!isUnlocked}}">
    <view class="lock-icon">🔒</view>
    <view class="unlock-title">完整攻略需要解锁</view>
    <view class="unlock-desc">解锁后可查看完整行程、推荐酒店、美食餐厅等</view>
    <view class="unlock-price">
      <text class="price-label">{{guideType === 'history' ? '人文历史路线' : '旅行攻略'}}</text>
      <text class="price-value">¥{{guideType === 'history' ? '9.80' : '4.80'}}</text>
    </view>
    <button class="unlock-btn" bindtap="onUnlockGuide">
      <text class="btn-icon">🔓</text>
      <text>立即解锁</text>
    </button>
  </view>
  
  <!-- 已解锁状态 -->
  <view class="unlocked-badge" wx:else>
    <text class="badge-icon">✅</text>
    <text>已解锁完整攻略</text>
  </view>
</view>
```

#### 修改"完整攻略内容"的条件
```xml
<!-- 原来 -->
<view class="section-card content-section" wx:if="{{article}}">

<!-- 修改为 -->
<view class="section-card content-section" wx:if="{{article && isUnlocked}}">
```

### 3. guide-detail.wxss 的修改

#### 在文件末尾添加（约120行）
```css
/* ========== 解锁状态区域 ========== */

/* 未解锁提示卡片 */
.unlock-prompt {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 24rpx;
  padding: 48rpx 32rpx;
  text-align: center;
  color: white;
  box-shadow: 0 8rpx 32rpx rgba(102, 126, 234, 0.3);
}

/* 锁图标（带摇晃动画） */
.lock-icon {
  font-size: 80rpx;
  margin-bottom: 16rpx;
  animation: shake 2s ease-in-out infinite;
}

/* 立即解锁按钮 */
.unlock-btn {
  background: white !important;
  color: #667eea !important;
  border-radius: 48rpx !important;
  /* ... 更多样式 */
}

/* 已解锁徽章 */
.unlocked-badge {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  /* ... 更多样式 */
}
```

### 4. unlock-payment.js（新文件）

完整的支付流程封装模块，包含：
- `checkUnlockStatus()` - 检查解锁状态
- `createPaymentOrder()` - 创建支付订单
- `requestWxPayment()` - 调起微信支付
- `startUnlockPayment()` - 完整支付流程
- `getMyUnlockedGuides()` - 获取已解锁列表

## 🔄 页面流程

```
用户进入攻略详情
    ↓
检查解锁状态 (checkUnlockStatus)
    ↓
┌─────────────────────┬──────────────────┐
│    未解锁           │     已解锁        │
├─────────────────────┼──────────────────┤
│ 显示：              │ 显示：            │
│ • 行程亮点          │ • 行程亮点         │
│ • 🔒 解锁提示卡片   │ • ✅ 已解锁徽章    │
│ • 立即解锁按钮      │ • 📖 完整攻略内容  │
│                     │                  │
│ 点击解锁按钮        │                  │
│     ↓              │                  │
│ 支付确认对话框      │                  │
│     ↓              │                  │
│ 调起微信支付        │                  │
│     ↓              │                  │
│ 支付成功            │                  │
│     ↓              │                  │
│ 更新为已解锁 ───────→                  │
└─────────────────────┴──────────────────┘
```

## 💰 商品定价

| 类型 | 判断条件 | 价格 | product_id |
|------|---------|------|------------|
| 旅行攻略 | 默认 | ¥4.80 | guide_travel |
| 人文历史 | category包含"历史"/"文化"/"人文" | ¥9.80 | guide_history |

## 🎨 UI 样式特点

- **未解锁卡片**：紫色渐变背景，白色文字，摇晃的锁图标
- **解锁按钮**：白色按钮，紫色文字，点击缩放效果
- **已解锁徽章**：绿色渐变背景，简洁的勾选图标

## 📊 API调用流程

```
小程序 → 后端 API
  ↓
1. GET /api/vip/check_unlock?guide_id=xxx&openid=xxx
   检查是否已解锁
  ↓
2. POST /api/vip/create_order
   {
     "openid": "xxx",
     "product_id": "guide_travel",
     "guide_id": "xxx"
   }
   创建支付订单
  ↓
3. wx.requestPayment(pay_params)
   调起微信支付
  ↓
4. 微信支付回调 → POST /api/payment/notify
   更新订单状态为 paid
  ↓
5. 支付成功回调
   setData({ isUnlocked: true })
```

## ✅ 快速检查清单

在提交代码或测试前，确认：

- [ ] `unlock-payment.js` 文件已创建
- [ ] `guide-detail.js` 引入了 `unlock-payment.js`
- [ ] `guide-detail.js` 的 data 包含解锁状态字段
- [ ] `guide-detail.js` 的 onLoad 调用了 checkUnlockStatus
- [ ] `guide-detail.js` 添加了 onUnlockGuide 方法
- [ ] `guide-detail.wxml` 添加了解锁提示UI
- [ ] `guide-detail.wxml` 修改了完整内容的显示条件
- [ ] `guide-detail.wxss` 添加了所有样式
- [ ] 后端 API 正常运行
- [ ] request 域名已配置

## 🔧 调试技巧

### 控制台查看状态
```javascript
// 在 checkUnlockStatus 方法中添加
console.log('🔓 解锁状态:', result.unlocked ? '已解锁' : '未解锁')

// 在 onUnlockGuide 方法中添加
console.log('💰 开始支付流程:', { guideId, guideTitle, guideType })
```

### 强制设置为已解锁（测试用）
```javascript
// 在控制台执行
this.setData({ isUnlocked: true })
```

### 查看后端日志
```bash
# 实时查看
tail -f /root/clawd/backend/flask.log

# 查找支付日志
grep "攻略解锁\|payment" /root/clawd/backend/flask.log
```

---

## 🎉 完成！

所有修改已完成，现在可以在微信开发者工具中测试支付功能了！

有任何问题，参考：
- `/root/clawd/miniprogram/PAYMENT_TEST_GUIDE.md` - 测试指南
- `/root/clawd/miniprogram/PAYMENT_INTEGRATION_GUIDE.md` - 集成指南
