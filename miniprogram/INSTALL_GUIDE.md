# 小程序代码部署指南

## 📦 文件清单

已准备好的文件:

```
miniprogram/
├── app.js                    # 全局配置
├── app.json                  # 页面路由
├── app.wxss                  # 全局样式
├── pages/
│   ├── guide/
│   │   ├── detail.js        # 攻略详情页逻辑
│   │   ├── detail.wxml      # 攻略详情页结构
│   │   ├── detail.wxss      # 攻略详情页样式
│   │   └── detail.json      # 攻略详情页配置
│   └── user/
│       ├── unlocked.js      # 已解锁列表逻辑
│       ├── unlocked.wxml    # 已解锁列表结构
│       ├── unlocked.wxss    # 已解锁列表样式
│       └── unlocked.json    # 已解锁列表配置
└── images/                  # 图片资源 (需要准备)
    ├── lock.png
    ├── check.png
    ├── empty.png
    └── tab/
        ├── home.png
        ├── home-active.png
        ├── user.png
        └── user-active.png
```

## 🚀 部署步骤

### 方法1: 通过服务器下载 (推荐)

如果你的电脑可以访问服务器:

```bash
# 1. 打包文件
cd /root/clawd
tar -czf miniprogram.tar.gz miniprogram/

# 2. 下载到本地
# 使用SFTP或SCP工具下载 miniprogram.tar.gz
# 例如: scp root@your-server:/root/clawd/miniprogram.tar.gz ~/Downloads/

# 3. 解压到小程序项目目录
tar -xzf miniprogram.tar.gz
```

### 方法2: 手动复制粘贴

**步骤1: 在小程序项目中创建文件夹**

在微信开发者工具中:
1. 右键项目根目录 → 新建文件夹 → `pages`
2. 在`pages`下新建 → `guide` 文件夹
3. 在`pages`下新建 → `user` 文件夹

**步骤2: 创建页面**

在开发者工具中:
1. 右键 `pages/guide` → 新建Page → 输入 `detail`
2. 右键 `pages/user` → 新建Page → 输入 `unlocked`

这会自动生成4个文件 (.js, .wxml, .wxss, .json)

**步骤3: 复制代码内容**

从服务器文件复制内容到对应的小程序文件:

```bash
# 查看文件内容 (在服务器上执行)

# app.js
cat /root/clawd/miniprogram/app.js

# app.json
cat /root/clawd/miniprogram/app.json

# app.wxss
cat /root/clawd/miniprogram/app.wxss

# 攻略详情页
cat /root/clawd/miniprogram/pages/guide/detail.js
cat /root/clawd/miniprogram/pages/guide/detail.wxml
cat /root/clawd/miniprogram/pages/guide/detail.wxss
cat /root/clawd/miniprogram/pages/guide/detail.json

# 已解锁列表
cat /root/clawd/miniprogram/pages/user/unlocked.js
cat /root/clawd/miniprogram/pages/user/unlocked.wxml
cat /root/clawd/miniprogram/pages/user/unlocked.wxss
cat /root/clawd/miniprogram/pages/user/unlocked.json
```

然后复制内容粘贴到开发者工具对应文件中。

## 🖼️ 图片资源准备

### 方法1: 临时占位图片

暂时不添加图片,代码中先注释掉图片相关部分:

在 `detail.wxml` 中:
```xml
<!-- 暂时注释掉图片 -->
<!-- <image class="lock-icon" src="/images/lock.png"></image> -->
<view class="lock-icon-placeholder">🔒</view>
```

### 方法2: 准备真实图片

需要的图片:
1. **lock.png** (200x200) - 锁图标
2. **check.png** (60x60) - 对勾图标
3. **empty.png** (400x400) - 空状态图标
4. **tab/home.png** (81x81) - 首页图标
5. **tab/home-active.png** (81x81) - 首页激活图标
6. **tab/user.png** (81x81) - 我的图标
7. **tab/user-active.png** (81x81) - 我的激活图标

可以从这些网站下载免费图标:
- https://www.iconfont.cn/
- https://www.flaticon.com/
- https://icons8.com/

## ⚙️ 配置服务器域名

在小程序后台配置:

1. 登录: https://mp.weixin.qq.com
2. 开发 → 开发管理 → 开发设置 → 服务器域名
3. 添加以下域名:

```
request合法域名:
https://api.wildtrip.com.cn

uploadFile合法域名:
https://api.wildtrip.com.cn

downloadFile合法域名:
https://api.wildtrip.com.cn
```

4. 点击"保存并提交"
5. 等待5-10分钟生效

## 🧪 开发者工具调试

### 1. 不校验合法域名 (开发时)

在开发者工具中:
- 点击右上角"详情"
- 勾选"不校验合法域名、web-view (业务域名)、TLS版本以及HTTPS证书"

⚠️ 这个选项**仅用于开发调试**,真机测试和上线前必须取消勾选!

### 2. 编译并预览

1. 点击"编译" - 检查是否有错误
2. 控制台应该显示:
   ```
   🚀 野游记小程序启动
   开始自动登录...
   wx.login success, code: ...
   ✅ 登录成功, openid: ...
   ```

### 3. 模拟器测试

在模拟器中测试基本功能:
- 页面能否正常打开
- 样式是否正确
- 控制台有无错误

⚠️ 注意: **微信支付无法在模拟器中测试**,必须真机测试!

## 📱 真机预览

### 1. 生成预览二维码

- 点击开发者工具顶部的"预览"按钮
- 会生成一个二维码

### 2. 扫码预览

- 用微信扫描二维码
- 小程序会在手机上打开

### 3. 真机调试

如果需要查看手机上的日志:
- 点击"真机调试"
- 扫码后可以在电脑上看到手机的控制台输出

## ✅ 检查清单

部署完成后检查:

- [ ] 所有文件已创建
- [ ] app.js/app.json/app.wxss 已配置
- [ ] 攻略详情页4个文件已创建
- [ ] 已解锁列表4个文件已创建
- [ ] 服务器域名已配置
- [ ] 开发者工具编译通过
- [ ] 控制台显示登录成功
- [ ] 真机可以扫码预览

## 🐛 常见问题

### Q1: 编译报错 "pages/index/index 不存在"

**解决:** 
创建一个简单的首页:
1. 右键 pages → 新建Page → index
2. 或者在 app.json 中删除 "pages/index/index" 这行

### Q2: 登录失败

**解决:**
1. 检查后端服务是否运行: `systemctl status wildtrip-backend`
2. 检查服务器域名是否配置
3. 检查开发者工具是否勾选"不校验域名"

### Q3: 图片不显示

**解决:**
1. 临时方案: 用emoji替代图标
2. 长期方案: 准备图片资源

### Q4: tabBar图标不显示

**解决:**
临时注释掉tabBar配置,部署时再添加:

```json
// app.json 中暂时注释
/*
"tabBar": {
  ...
}
*/
```

## 📞 需要帮助?

遇到问题可以:
1. 查看开发者工具控制台错误信息
2. 截图发给我帮你看
3. 查看小程序官方文档: https://developers.weixin.qq.com/miniprogram/dev/

---

部署完成后告诉我,我们继续进行真机支付测试! 🚀
