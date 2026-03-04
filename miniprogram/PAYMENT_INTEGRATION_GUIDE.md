# 攻略解锁支付集成指南

## 📋 概述

本指南说明如何在野游记小程序中集成攻略解锁支付功能。

## ✅ 后端已完成

- ✅ 支付API接口 (`/api/vip/*`)
- ✅ 订单管理系统
- ✅ 微信支付回调
- ✅ 数据库设计

## 📱 小程序端需要修改的地方

### 1. 在 guide-detail 页面添加支付功能

#### 步骤1: 引入支付模块

在 `pages/guide-detail/guide-detail.js` 开头添加:

```javascript
const unlockPayment = require('./unlock-payment.js')
```

#### 步骤2: 在 data 中添加解锁状态

```javascript
Page({
  data: {
    // ... 现有数据
    isUnlocked: false,  // 是否已解锁
    checkingUnlock: true,  // 正在检查解锁状态
    guideType: 'travel',  // 攻略类型 travel/history
  },
  
  // ...
})
```

#### 步骤3: 在 onLoad 中检查解锁状态

```javascript
async onLoad(options) {
  const { slug } = options
  this.setData({ slug })
  
  // 检查解锁状态
  this.checkUnlockStatus()
  
  // 加载攻略
  this.loadGuideDetail()
},

// 检查解锁状态
async checkUnlockStatus() {
  const app = getApp()
  const openid = app.globalData.openid
  const { slug } = this.data
  
  if (!openid || !slug) {
    this.setData({ checkingUnlock: false, isUnlocked: false })
    return
  }
  
  try {
    const result = await unlockPayment.checkUnlockStatus(slug, openid)
    this.setData({
      isUnlocked: result.unlocked,
      checkingUnlock: false
    })
  } catch (error) {
    console.error('检查解锁状态失败:', error)
    this.setData({ checkingUnlock: false, isUnlocked: false })
  }
},
```

#### 步骤4: 添加解锁支付方法

```javascript
// 点击解锁按钮
onUnlockGuide() {
  const { slug, guide, guideType } = this.data
  
  if (!slug || !guide) {
    wx.showToast({ title: '攻略加载中', icon: 'none' })
    return
  }
  
  // 调用支付流程
  unlockPayment.startUnlockPayment({
    guideId: slug,
    guideTitle: guide.title,
    guideType: guideType,
    onSuccess: (order) => {
      console.log('支付成功:', order)
      // 更新解锁状态
      this.setData({ isUnlocked: true })
      // 重新加载攻略详情
      this.loadGuideDetail()
    },
    onFail: (error) => {
      console.error('支付失败:', error)
    }
  })
},
```

### 2. 在 WXML 中添加解锁按钮

在 `pages/guide-detail/guide-detail.wxml` 的完整攻略内容前添加:

```xml
<!-- 解锁状态提示 -->
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

<!-- 完整攻略内容（只有解锁后才显示） -->
<view wx:if="{{isUnlocked && !showContent}}" class="preview-placeholder">
  <!-- 现有的攻略内容 -->
</view>
```

### 3. 在 WXSS 中添加样式

在 `pages/guide-detail/guide-detail.wxss` 中添加:

```css
/* 解锁状态区域 */
.unlock-status {
  margin: 20rpx;
}

/* 未解锁提示卡片 */
.unlock-prompt {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 24rpx;
  padding: 48rpx 32rpx;
  text-align: center;
  color: white;
  box-shadow: 0 8rpx 32rpx rgba(102, 126, 234, 0.3);
}

.lock-icon {
  font-size: 80rpx;
  margin-bottom: 16rpx;
}

.unlock-title {
  font-size: 36rpx;
  font-weight: bold;
  margin-bottom: 16rpx;
}

.unlock-desc {
  font-size: 28rpx;
  opacity: 0.9;
  margin-bottom: 32rpx;
  line-height: 1.6;
}

.unlock-price {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  margin-bottom: 32rpx;
}

.price-label {
  font-size: 28rpx;
  opacity: 0.9;
}

.price-value {
  font-size: 48rpx;
  font-weight: bold;
}

.unlock-btn {
  background: white;
  color: #667eea;
  border-radius: 48rpx;
  padding: 24rpx 64rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 12rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
}

.btn-icon {
  font-size: 32rpx;
}

/* 已解锁徽章 */
.unlocked-badge {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  border-radius: 16rpx;
  padding: 24rpx 32rpx;
  text-align: center;
  color: white;
  font-size: 28rpx;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
}

.badge-icon {
  font-size: 32rpx;
}
```

## 🔧 判断攻略类型

在加载攻略时，根据攻略内容判断类型:

```javascript
loadGuideDetail() {
  // ... 加载攻略
  
  // 判断是否是人文历史类攻略
  let guideType = 'travel'  // 默认旅行攻略
  
  if (guide.category && 
      (guide.category.includes('历史') || 
       guide.category.includes('文化') ||
       guide.category.includes('人文'))) {
    guideType = 'history'
  }
  
  this.setData({ guide, guideType })
}
```

## 📊 测试流程

### 1. 开发环境测试

```bash
# 在服务器上查看订单
cd /root/clawd/backend
python3 view_orders.py
```

### 2. 小程序测试步骤

1. 打开攻略详情页
2. 看到"解锁提示"卡片
3. 点击"立即解锁"按钮
4. 确认支付对话框
5. 完成微信支付
6. 支付成功后自动显示完整攻略

### 3. 查看支付日志

```bash
# 查看Flask日志
tail -f /root/clawd/backend/flask.log

# 查看支付回调日志
grep "payment/notify" /root/clawd/backend/flask.log
```

## ⚠️ 重要配置

### 1. 确保小程序有支付权限

在微信公众平台:
1. 开发管理 → 开发设置 → 服务器域名
2. 添加 `https://api.wildtrip.com.cn`
3. request合法域名、uploadFile合法域名都要配置

### 2. 微信商户平台配置

1. 产品中心 → JSAPI支付 → 已开通
2. 账户中心 → API安全 → 设置API密钥
3. 支付配置 → 支付回调URL: `https://api.wildtrip.com.cn/api/payment/notify`

## 📁 相关文件

```
/root/clawd/
├── backend/
│   ├── api/vip.py                 # 攻略支付API
│   ├── api/payment.py             # 支付回调
│   └── services/order_service.py  # 订单服务
├── miniprogram/
│   └── pages/guide-detail/
│       ├── guide-detail.js        # 需要修改
│       ├── guide-detail.wxml      # 需要修改
│       ├── guide-detail.wxss      # 需要修改
│       └── unlock-payment.js      # 新增支付模块
```

## 🚀 上线前检查清单

- [ ] 微信支付已开通并测试通过
- [ ] 支付回调URL已配置
- [ ] 小程序request域名已添加
- [ ] 解锁状态检查正常
- [ ] 支付流程测试通过
- [ ] 已支付订单能正常解锁
- [ ] 日志记录完整

## 💡 后续优化

1. **支付成功动画** - 添加庆祝动画
2. **我的订单页面** - 显示购买记录
3. **分享解锁** - 分享给好友也能解锁
4. **优惠券系统** - 首单优惠等
5. **退款功能** - 7天内可退

---

完成以上步骤后，攻略解锁支付功能就集成完毕了! 🎉
