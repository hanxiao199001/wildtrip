# 🚀 攻略解锁支付功能 - 部署说明

## 📦 已修改的文件

### 后端（服务器）
```
/root/clawd/backend/api/vip.py
```
- ✅ 价格已改为 ¥0.01（测试）
- ✅ 服务已重启
- ✅ API测试通过

### 小程序（需要同步到本地）
```
/root/clawd/miniprogram/pages/guide-detail/
├── guide-detail.js      (已修改 - 添加支付逻辑)
├── guide-detail.wxml    (已修改 - 添加解锁UI)
├── guide-detail.wxss    (已修改 - 添加样式)
└── unlock-payment.js    (新增 - 支付模块)
```

---

## 🔄 同步方式

### 方式1: 使用打包文件（最简单）

#### 步骤1: 下载打包文件
```bash
# 文件位置（服务器上）
/root/clawd/guide-detail-payment-update.tar.gz

# 使用 scp 下载到本地
scp root@你的服务器IP:/root/clawd/guide-detail-payment-update.tar.gz ~/Downloads/
```

#### 步骤2: 解压并覆盖
```bash
# 在本地小程序项目目录
cd /path/to/your/miniprogram/pages/guide-detail/

# 解压（会覆盖现有文件）
tar -xzf ~/Downloads/guide-detail-payment-update.tar.gz
```

#### 步骤3: 验证文件
```bash
ls -la
# 应该看到:
# - guide-detail.js
# - guide-detail.wxml  
# - guide-detail.wxss
# - unlock-payment.js (新文件)
```

---

### 方式2: 手动复制文件内容

如果你不想用命令行，可以手动复制：

#### 1. guide-detail.js
- 位置: `/root/clawd/miniprogram/pages/guide-detail/guide-detail.js`
- 复制整个文件内容
- 粘贴到本地同名文件

#### 2. guide-detail.wxml
- 位置: `/root/clawd/miniprogram/pages/guide-detail/guide-detail.wxml`
- 复制整个文件内容
- 粘贴到本地同名文件

#### 3. guide-detail.wxss
- 位置: `/root/clawd/miniprogram/pages/guide-detail/guide-detail.wxss`
- 复制整个文件内容
- 粘贴到本地同名文件

#### 4. unlock-payment.js (新文件)
- 位置: `/root/clawd/miniprogram/pages/guide-detail/unlock-payment.js`
- 在本地创建新文件
- 复制内容并保存

---

### 方式3: 使用 Git（推荐，如果你用Git管理代码）

```bash
# 在服务器上
cd /root/clawd
git add .
git commit -m "feat: 添加攻略解锁支付功能"
git push origin main  # 或你的分支名

# 在本地
cd /path/to/your/local/project
git pull origin main
```

---

## ✅ 同步后的检查清单

在微信开发者工具中：

### 1. 检查文件是否存在
- [ ] `pages/guide-detail/guide-detail.js` 已更新
- [ ] `pages/guide-detail/guide-detail.wxml` 已更新
- [ ] `pages/guide-detail/guide-detail.wxss` 已更新
- [ ] `pages/guide-detail/unlock-payment.js` 已创建（新文件）

### 2. 检查代码是否正确
打开 `guide-detail.js`，找到：
```javascript
const unlockPayment = require('./unlock-payment.js')
```
如果有这行代码，说明引入正确 ✅

### 3. 检查UI是否显示
- 编译小程序
- 进入任意攻略详情页
- 应该看到紫色的解锁提示卡片
- 价格显示为 **¥0.01（测试价格）**

### 4. 检查控制台
打开控制台，应该看到：
```
📖 攻略详情页加载, slug: xxx
🔓 解锁状态: 未解锁  (或 已解锁)
```

---

## 🧪 测试步骤

### 测试1: UI显示测试
1. ✅ 打开任意攻略详情页
2. ✅ 看到行程亮点
3. ✅ 看到紫色解锁提示卡片
4. ✅ 看到 "¥0.01（测试价格）"
5. ✅ 看到 "立即解锁" 按钮

### 测试2: 支付流程测试（需要真实用户）
1. ✅ 点击 "立即解锁" 按钮
2. ✅ 弹出确认对话框
3. ✅ 显示商品信息和价格
4. ✅ 点击 "立即支付"
5. ⚠️ 调起微信支付（需要真实openid）

### 测试3: 已解锁状态测试
1. 完成支付后
2. ✅ 显示绿色 "已解锁完整攻略" 徽章
3. ✅ 显示完整攻略内容
4. ✅ 退出并重新进入，仍然显示已解锁

---

## ⚙️ API域名配置

确保在小程序后台配置了服务器域名：

### 开发 > 开发管理 > 开发设置 > 服务器域名

#### request合法域名
```
https://api.wildtrip.com.cn
```

#### uploadFile合法域名
```
https://api.wildtrip.com.cn
```

#### downloadFile合法域名
```
https://api.wildtrip.com.cn
```

---

## 🔑 openid 获取

小程序需要先获取用户的openid才能完整测试支付流程。

### 在 app.js 中添加登录逻辑

```javascript
App({
  globalData: {
    openid: null
  },
  
  onLaunch() {
    // 获取 openid
    wx.login({
      success: (res) => {
        if (res.code) {
          // 发送到后端换取 openid
          wx.request({
            url: 'https://api.wildtrip.com.cn/api/auth/login',
            method: 'POST',
            data: { code: res.code },
            success: (result) => {
              if (result.data && result.data.openid) {
                this.globalData.openid = result.data.openid
                console.log('✅ 用户登录成功, openid:', result.data.openid)
              }
            }
          })
        }
      }
    })
  }
})
```

---

## 💰 价格说明

### 当前配置（测试）
- 旅行攻略: **¥0.01**
- 人文历史: **¥0.01**

### 正式环境价格
上线前需要改回：
- 旅行攻略: **¥4.80**
- 人文历史: **¥9.80**

#### 修改位置

**后端**: `/root/clawd/backend/api/vip.py`
```python
GUIDE_PRODUCTS = {
    'guide_travel': {
        'name': '旅行攻略解锁',
        'amount': 480,  # 改回 4.8元
        'type': 'travel'
    },
    'guide_history': {
        'name': '人文历史路线解锁',
        'amount': 980,  # 改回 9.8元
        'type': 'history'
    }
}
```

**小程序**: `/root/clawd/miniprogram/pages/guide-detail/`
- `guide-detail.wxml` - 删除测试价格标记
- `unlock-payment.js` - 改回正式价格

---

## 🐛 常见问题

### Q1: 点击解锁按钮没反应
**检查**:
- 控制台是否有错误
- `unlock-payment.js` 是否存在
- 是否正确引入

### Q2: 显示 "请先登录"
**原因**: `app.globalData.openid` 为空
**解决**: 添加登录逻辑获取 openid

### Q3: 创建订单失败
**检查**:
- 后端服务是否运行
- API域名是否配置
- openid 是否有效

### Q4: 支付后未解锁
**检查**:
- 支付回调是否成功（查看后端日志）
- 订单状态是否更新为 paid
- 刷新页面后是否解锁

---

## 📊 查看后端日志

```bash
# SSH 登录服务器后
tail -f /root/clawd/backend/flask.log

# 查找支付相关日志
grep "攻略解锁\|payment" /root/clawd/backend/flask.log | tail -20
```

---

## 🎉 部署完成后

完成以上步骤后：
1. ✅ 在微信开发者工具中编译小程序
2. ✅ 测试UI显示
3. ✅ 测试解锁流程
4. ✅ 小额支付测试（¥0.01）

测试通过后，即可提交审核或继续开发其他功能！

---

如有问题，查看文档：
- `PAYMENT_INTEGRATION_GUIDE.md` - 集成指南
- `PAYMENT_TEST_GUIDE.md` - 测试指南
- `API_TEST_REPORT.md` - API测试报告
