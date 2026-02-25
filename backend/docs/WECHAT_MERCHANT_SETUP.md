# 微信商户平台配置指南

## 📋 前提条件

- ✅ 已有微信商户号: **1106656739**
- ✅ 已配置商户API密钥
- ⏳ 需要开通JSAPI支付功能

## 🔧 配置步骤

### 第一步: 登录商户平台

1. 访问: https://pay.weixin.qq.com
2. 使用管理员微信扫码登录
3. 商户号: **1106656739**

### 第二步: 开通JSAPI支付

#### 路径:
```
产品中心 → 我的产品 → JSAPI支付
```

#### 操作:
1. 点击 **"申请开通"**
2. 填写申请信息:
   - 产品名称: `野游记旅行攻略`
   - 产品类型: `数字内容`
   - 产品描述: `旅行攻略生成与解锁服务`
   - 预计月交易额: 根据实际情况填写

3. 提交资料:
   - 产品截图 (小程序页面)
   - 用户协议
   - 隐私政策

4. 等待审核 (通常1-2个工作日)

#### 审核通过后:
- 产品中心会显示 **"JSAPI支付 - 已开通"**

### 第三步: 配置支付回调URL

#### 路径:
```
产品中心 → 开发配置 → 支付配置 → 支付回调URL
```

#### 配置内容:
```
支付回调URL: https://api.wildtrip.com.cn/api/payment/notify
```

⚠️ **重要**: 必须是HTTPS域名

### 第四步: 配置JSAPI支付授权目录

#### 路径:
```
产品中心 → 开发配置 → JSAPI支付 → 支付授权目录
```

#### 添加授权目录:
```
https://api.wildtrip.com.cn/
```

⚠️ 目录必须精确到具体路径,末尾要加 `/`

### 第五步: 绑定小程序AppID

#### 路径:
```
产品中心 → AppID账号管理 → 关联AppID
```

#### 操作:
1. 点击 **"新增关联"**
2. 输入小程序AppID: **wxb5430a06dd7fa579**
3. 小程序管理员扫码确认
4. 等待审核通过

### 第六步: 验证API密钥

#### 路径:
```
账户中心 → API安全 → API密钥
```

#### 当前配置:
```
API密钥(32位): ***REMOVED***
```

✅ 已配置在 `.env` 文件中: `WECHAT_API_KEY`

### 第七步: 下载证书 (用于退款等高级功能)

#### 路径:
```
账户中心 → API安全 → API证书
```

#### 操作:
1. 点击 **"下载证书"**
2. 管理员扫码验证
3. 下载证书文件:
   - `apiclient_cert.pem` (证书)
   - `apiclient_key.pem` (密钥)
   - `apiclient_cert.p12` (证书+密钥)

4. 上传到服务器:
```bash
# 创建证书目录
mkdir -p /root/clawd/backend/certs

# 上传证书文件
# apiclient_cert.pem
# apiclient_key.pem
```

5. 更新 `.env`:
```bash
WECHAT_CERT_PATH=/root/clawd/backend/certs/apiclient_cert.pem
WECHAT_KEY_PATH=/root/clawd/backend/certs/apiclient_key.pem
```

## ✅ 配置检查清单

完成以上步骤后,检查:

- [ ] JSAPI支付已开通
- [ ] 支付回调URL已配置: `https://api.wildtrip.com.cn/api/payment/notify`
- [ ] 支付授权目录已添加: `https://api.wildtrip.com.cn/`
- [ ] 小程序AppID已关联: `wxb5430a06dd7fa579`
- [ ] API密钥已配置
- [ ] 证书已下载 (可选,用于退款)

## 🧪 测试支付

### 使用沙箱环境测试

微信支付提供沙箱环境用于测试:

#### 获取沙箱密钥:
```
开发配置 → 沙箱验收 → 获取沙箱密钥
```

#### 更新 `.env` 测试配置:
```bash
# 测试环境
PAYMENT_SANDBOX=true
WECHAT_API_KEY_SANDBOX=沙箱密钥
```

#### 测试步骤:
1. 小程序发起支付
2. 使用测试账号支付
3. 查看回调日志
4. 验证订单状态

### 真实环境小额测试

沙箱测试通过后,进行真实支付测试:

1. 创建订单 (¥0.01 测试订单)
2. 真实支付
3. 验证回调
4. 检查数据库订单状态
5. 测试退款 (可选)

## 📞 常见问题

### Q1: JSAPI支付开通需要多久?
A: 通常1-2个工作日,如遇节假日可能延长

### Q2: 回调URL配置不成功?
A: 检查:
- 域名必须是HTTPS
- 域名必须已备案
- 服务器防火墙开放443端口

### Q3: 小程序关联失败?
A: 确保:
- 小程序已认证
- 使用小程序管理员微信扫码
- 商户号状态正常

### Q4: 支付时提示"商户号该产品权限未开通"?
A: 说明JSAPI支付未开通或未审核通过,返回第二步重新检查

## 📚 相关文档

- 微信支付官方文档: https://pay.weixin.qq.com/wiki/doc/apiv3/index.shtml
- JSAPI支付文档: https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_5_1.shtml
- 小程序支付文档: https://developers.weixin.qq.com/miniprogram/dev/api/payment/wx.requestPayment.html

## 🔐 安全提醒

1. **API密钥**: 严格保密,不要提交到代码仓库
2. **证书文件**: 权限设置为 600,只允许root读取
3. **回调验签**: 必须验证微信签名,防止伪造
4. **订单幂等**: 处理重复回调通知

## 📝 配置完成后

完成所有配置后,更新 `.env`:

```bash
# 微信支付配置
WECHAT_APPID=wxb5430a06dd7fa579
WECHAT_SECRET=***REMOVED***
WECHAT_MCHID=1106656739
WECHAT_API_KEY=***REMOVED***

# 回调地址
PAYMENT_NOTIFY_URL=https://api.wildtrip.com.cn/api/payment/notify

# 生产环境
PAYMENT_SANDBOX=false

# 证书路径 (可选)
WECHAT_CERT_PATH=/root/clawd/backend/certs/apiclient_cert.pem
WECHAT_KEY_PATH=/root/clawd/backend/certs/apiclient_key.pem
```

重启服务:
```bash
systemctl restart wildtrip-backend
```

---
配置指南版本: v1.0  
更新时间: 2026-02-25
