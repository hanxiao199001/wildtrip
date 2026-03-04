# 野游记小程序 - 攻略解锁支付

## 📦 已创建的文件

### 1. 攻略详情页 (支付解锁)
```
pages/guide/detail.js      - 页面逻辑
pages/guide/detail.wxml    - 页面结构
pages/guide/detail.wxss    - 页面样式
pages/guide/detail.json    - 页面配置
```

### 2. 我的已解锁页面
```
pages/user/unlocked.js     - 页面逻辑
pages/user/unlocked.wxml   - 页面结构
pages/user/unlocked.wxss   - 页面样式
pages/user/unlocked.json   - 页面配置
```

## 🚀 使用方法

### 第一步: 配置app.js

在小程序根目录的 `app.js` 中添加:

```javascript
App({
  globalData: {
    openid: '',  // 用户openid
    userInfo: null
  },

  onLaunch() {
    // 自动登录
    this.autoLogin();
  },

  async autoLogin() {
    try {
      const res = await wx.login();
      
      const loginRes = await wx.request({
        url: 'https://api.wildtrip.com.cn/api/user/login',
        method: 'POST',
        data: { code: res.code }
      });

      if (loginRes.data.success) {
        this.globalData.openid = loginRes.data.openid;
        console.log('登录成功:', loginRes.data.openid);
      }
    } catch (err) {
      console.error('自动登录失败:', err);
    }
  }
});
```

### 第二步: 配置app.json

添加页面路径:

```json
{
  "pages": [
    "pages/index/index",
    "pages/guide/detail",
    "pages/user/unlocked"
  ],
  "window": {
    "navigationBarTitleText": "野游记",
    "navigationBarBackgroundColor": "#667eea",
    "navigationBarTextStyle": "white"
  }
}
```

### 第三步: 跳转到攻略详情

从任何页面跳转到攻略详情:

```javascript
// 旅行攻略
wx.navigateTo({
  url: '/pages/guide/detail?id=guide_beijing_3days&type=travel'
});

// 人文历史
wx.navigateTo({
  url: '/pages/guide/detail?id=guide_xian_history&type=history'
});
```

### 第四步: 跳转到已解锁列表

```javascript
wx.navigateTo({
  url: '/pages/user/unlocked'
});
```

## 🎨 界面功能

### 攻略详情页
- ✅ 自动检测解锁状态
- ✅ 未解锁: 显示预览 + 支付按钮
- ✅ 已解锁: 显示完整内容
- ✅ 支付流程: 创建订单 → 调起微信支付 → 轮询状态
- ✅ 价格显示: 旅行攻略 ¥4.80, 人文历史 ¥9.80

### 已解锁列表页
- ✅ 统计卡片: 显示已解锁数量和累计消费
- ✅ 攻略列表: 展示所有已解锁攻略
- ✅ 点击跳转: 直接查看攻略详情
- ✅ 空状态: 没有解锁时显示引导

## 📝 页面配置文件

### pages/guide/detail.json
```json
{
  "navigationBarTitleText": "攻略详情",
  "enablePullDownRefresh": false
}
```

### pages/user/unlocked.json
```json
{
  "navigationBarTitleText": "我的已解锁",
  "enablePullDownRefresh": true,
  "backgroundColor": "#f5f5f5"
}
```

## 🖼️ 所需图片资源

需要准备以下图片,放在 `images/` 目录:

```
images/
  ├── lock.png      - 锁图标 (解锁按钮)
  ├── check.png     - 对勾图标 (已解锁标记)
  └── empty.png     - 空状态图标
```

建议尺寸:
- lock.png: 200x200 px
- check.png: 60x60 px
- empty.png: 400x400 px

## 🔌 API集成

小程序会调用以下后端API:

```
# 用户登录
POST /api/user/login
{ "code": "wx.login获取的code" }

# 检查解锁状态
GET /api/vip/check_unlock?openid=xxx&guide_id=xxx

# 创建订单
POST /api/vip/create_order
{ "openid": "xxx", "product_id": "guide_travel", "guide_id": "xxx" }

# 查询订单状态
GET /api/payment/query_order?order_id=xxx

# 已解锁列表
GET /api/vip/my_unlocked?openid=xxx
```

## 🧪 测试步骤

### 1. 未解锁状态测试
1. 打开攻略详情页
2. 应显示预览内容 + 解锁卡片
3. 点击"立即解锁"
4. 调起微信支付

### 2. 支付流程测试
1. 完成支付
2. 自动轮询订单状态
3. 支付成功后显示"解锁成功"
4. 刷新页面显示完整内容

### 3. 已解锁状态测试
1. 再次打开同一攻略
2. 应直接显示完整内容
3. 不显示支付按钮

### 4. 已解锁列表测试
1. 打开"我的已解锁"
2. 应显示所有已支付的攻略
3. 统计数据正确
4. 点击可跳转详情

## ⚠️ 注意事项

### 1. 微信支付域名配置

在小程序后台配置:
```
开发 → 开发设置 → 服务器域名
request合法域名: https://api.wildtrip.com.cn
```

### 2. 支付权限

确保小程序已开通微信支付功能:
```
小程序后台 → 功能 → 微信支付
```

### 3. 商户号关联

确保商户号已关联小程序AppID:
```
商户平台 → 产品中心 → AppID账号管理
```

### 4. 真机调试

支付功能必须在真机上测试,模拟器不支持微信支付。

## 🎯 完整流程

```
用户生成攻略
    ↓
进入攻略详情页
    ↓
自动检查解锁状态
    ↓ (未解锁)
显示预览 + 支付按钮
    ↓
点击"立即解锁"
    ↓
调用后端创建订单
    ↓
调起微信支付
    ↓
用户完成支付
    ↓
轮询查询订单状态
    ↓
状态变为