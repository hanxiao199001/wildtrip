# 小程序部署与测试指南

## ✅ 前置条件已完成

- ✅ 微信商户号JSAPI权限已开通
- ✅ 后端支付API已部署
- ✅ 小程序代码已准备

## 📦 第一步: 部署小程序代码

### 1. 复制文件到小程序项目

将以下文件复制到你的小程序项目目录:

```bash
# 攻略详情页
pages/guide/detail.js
pages/guide/detail.wxml
pages/guide/detail.wxss
pages/guide/detail.json

# 已解锁列表页
pages/user/unlocked.js
pages/user/unlocked.wxml
pages/user/unlocked.wxss
pages/user/unlocked.json
```

**创建页面配置文件:**

`pages/guide/detail.json`:
```json
{
  "navigationBarTitleText": "攻略详情",
  "enablePullDownRefresh": false,
  "backgroundColor": "#f5f5f5"
}
```

`pages/user/unlocked.json`:
```json
{
  "navigationBarTitleText": "我的已解锁",
  "enablePullDownRefresh": true,
  "backgroundColor": "#f5f5f5"
}
```

### 2. 修改 app.json

在 `app.json` 中添加页面路径:

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
    "navigationBarTextStyle": "white",
    "backgroundColor": "#f5f5f5"
  },
  "tabBar": {
    "color": "#999",
    "selectedColor": "#667eea",
    "backgroundColor": "#ffffff",
    "list": [
      {
        "pagePath": "pages/index/index",
        "text": "首页",
        "iconPath": "images/tab/home.png",
        "selectedIconPath": "images/tab/home-active.png"
      },
      {
        "pagePath": "pages/user/unlocked",
        "text": "我的",
        "iconPath": "images/tab/user.png",
        "selectedIconPath": "images/tab/user-active.png"
      }
    ]
  }
}
```

### 3. 修改 app.js

在 `app.js` 中添加全局配置:

```javascript
App({
  globalData: {
    openid: '',
    userInfo: null,
    apiBase: 'https://api.wildtrip.com.cn'
  },

  onLaunch() {
    console.log('野游记小程序启动');
    this.autoLogin();
  },

  // 自动登录
  async autoLogin() {
    try {
      // 1. 调用wx.login获取code
      const loginRes = await this.wxLogin();
      
      // 2. 调用后端登录接口
      const res = await this.request({
        url: '/api/user/login',
        method: 'POST',
        data: { code: loginRes.code }
      });

      if (res.success) {
        this.globalData.openid = res.openid;
        console.log('✅ 登录成功:', res.openid);
      } else {
        console.error('❌ 登录失败:', res.error);
      }

    } catch (err) {
      console.error('❌ 自动登录失败:', err);
    }
  },

  // 封装wx.login
  wxLogin() {
    return new Promise((resolve, reject) => {
      wx.login({
        success: resolve,
        fail: reject
      });
    });
  },

  // 封装request
  request(options) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: this.globalData.apiBase + options.url,
        method: options.method || 'GET',
        data: options.data || {},
        header: options.header || {},
        success: (res) => {
          resolve(res.data);
        },
        fail: reject
      });
    });
  }
});
```

### 4. 准备图片资源

在 `images/` 目录准备以下图片:

```
images/
  ├── lock.png          # 锁图标 (200x200)
  ├── check.png         # 对勾图标 (60x60)
  ├── empty.png         # 空状态图标 (400x400)
  └── tab/
      ├── home.png
      ├── home-active.png
      ├── user.png
      └── user-active.png
```

**快速创建占位图片 (临时用):**
可以先用纯色图片占位,后续替换。

## 🔧 第二步: 配置小程序后台

### 1. 配置服务器域名

登录小程序后台: https://mp.weixin.qq.com

```
开发 → 开发管理 → 开发设置 → 服务器域名
```

添加以下域名:

**request合法域名:**
```
https://api.wildtrip.com.cn
```

**uploadFile合法域名:**
```
https://api.wildtrip.com.cn
```

**downloadFile合法域名:**
```
https://api.wildtrip.com.cn
```

⚠️ 注意: 必须是HTTPS,且已备案

### 2. 配置业务域名

```
开发 → 开发管理 → 开发设置 → 业务域名
```

添加:
```
https://api.wildtrip.com.cn
https://wildtrip.com.cn
```

### 3. 检查微信支付配置

```
功能 → 微信支付
```

确认:
- ✅ 微信支付已开通
- ✅ 商户号: 1106656739
- ✅ 状态: 正常

## 📱 第三步: 真机测试

### 测试前准备

1. **打开开发者工具**
   - 使用微信开发者工具打开项目
   - 点击"编译" 确保没有错误

2. **预览二维码**
   - 点击"预览"
   - 用微信扫描二维码

3. **检查控制台**
   - 查看是否有错误信息
   - 确认登录成功

### 测试流程

#### Test 1: 登录测试

```
预期结果:
✅ 小程序启动自动登录
✅ 控制台输出: "✅ 登录成功: oxxx"
✅ app.globalData.openid 有值
```

#### Test 2: 攻略解锁状态检查

```
操作步骤:
1. 进入攻略详情页
2. 传入测试参数: id=guide_test_001&type=travel

预期结果:
✅ 页面正常加载
✅ 显示"未解锁"状态
✅ 显示价格: ¥4.80
✅ 显示"立即解锁"按钮
```

#### Test 3: 支付流程测试 (小额测试)

```
操作步骤:
1. 点击"立即解锁"
2. 确认支付弹窗
3. 点击"立即支付"
4. 输入微信支付密码
5. 完成支付

预期结果:
✅ 调起微信支付成功
✅ 支付完成后显示"支付成功"
✅ 自动轮询订单状态
✅ 订单状态变为"已支付"
✅ 页面刷新显示完整内容
✅ 显示"已解锁"标记
```

#### Test 4: 已解锁状态验证

```
操作步骤:
1. 关闭小程序
2. 重新打开
3. 再次进入同一攻略

预期结果:
✅ 直接显示完整内容
✅ 不显示支付按钮
✅ 显示"已解锁"标记
```

#### Test 5: 已解锁列表

```
操作步骤:
1. 进入"我的已解锁"页面

预期结果:
✅ 显示统计卡片
✅ 显示已解锁攻略列表
✅ 统计数据正确
✅ 点击可跳转详情
```

## 🐛 常见问题排查

### Q1: 服务器域名配置失败

**问题:** 提示"不在合法域名列表中"

**解决:**
1. 检查域名是否添加到服务器域名列表
2. 确认域名是HTTPS
3. 等待5-10分钟生效
4. 开发者工具中勾选"不校验合法域名" (仅开发时)

### Q2: 登录失败

**问题:** 控制台显示 "❌ 登录失败"

**解决:**
1. 检查后端 `/api/user/login` 接口是否正常
2. 测试接口:
```bash
curl -X POST https://api.wildtrip.com.cn/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"code": "test"}'
```
3. 查看后端日志:
```bash
tail -f /root/clawd/backend/logs/wildtrip.log
```

### Q3: 支付调起失败

**问题:** 点击支付没有反应或报错

**可能原因:**
1. 商户号未关联小程序AppID
2. JSAPI支付未开通
3. 支付参数错误

**解决:**
1. 检查商户平台关联状态
2. 查看控制台错误信息
3. 检查后端返回的 pay_params

### Q4: 支付成功但未解锁

**问题:** 支付完成但内容仍然锁定

**解决:**
1. 检查支付回调是否收到:
```bash
tail -f /root/clawd/backend/logs/wildtrip.log | grep "支付回调"
```

2. 查询订单状态:
```bash
cd /root/clawd/backend
python3 view_orders.py
```

3. 手动触发解锁检查:
```
刷新页面 → 重新检查解锁状态
```

### Q5: 图片不显示

**问题:** 锁图标、空状态图标不显示

**解决:**
1. 检查图片路径是否正确
2. 确认图片文件存在
3. 临时解决: 用emoji替代图标

## 📊 测试数据记录

### 测试记录表

| 测试项 | 状态 | 备注 |
|--------|------|------|
| 登录功能 | ⬜ | openid: |
| 解锁状态检查 | ⬜ | |
| 支付调起 | ⬜ | |
| 支付完成 | ⬜ | 订单号: |
| 解锁验证 | ⬜ | |
| 已解锁列表 | ⬜ | |

### 测试订单记录

```
订单1:
- 攻略ID: guide_test_001
- 类型: travel
- 金额: ¥4.80
- 订单号: 
- 状态: 
- 测试时间: 

订单2:
- 攻略ID: guide_test_002
- 类型: history
- 金额: ¥9.80
- 订单号: 
- 状态: 
- 测试时间: 
```

## 🚀 上线前检查清单

部署到生产环境前,确认:

- [ ] 所有测试用例通过
- [ ] 真机测试支付成功
- [ ] 支付回调正常工作
- [ ] 订单数据正确记录
- [ ] 解锁状态正确更新
- [ ] 服务器域名配置完成
- [ ] 微信支付配置正确
- [ ] 后端日志正常
- [ ] 数据库备份完成
- [ ] 关闭开发者工具的"不校验域名"选项

## 📝 提交审核

测试完成后,提交小程序审核:

```
开发管理 → 版本管理 → 提交审核
```

**审核材料准备:**
1. 小程序截图 (包含支付页面)
2. 支付功能说明
3. 隐私政策链接
4. 用户协议链接

**审核周期:** 通常1-7个工作日

---
文档版本: v1.0  
创建时间: 2026-02-25 12:00  
测试负责人: 
