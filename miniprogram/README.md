# 野游记小程序

> 懒人旅游AI，预订返现50%

## 📁 项目结构

```
miniprogram/
├── pages/              # 页面
│   ├── index/         # 首页
│   ├── generate/      # 生成页
│   ├── result/        # 结果页
│   └── cashback/      # 返现说明页
├── utils/             # 工具函数
│   └── api.js        # API封装
├── app.js             # 小程序入口
├── app.json           # 全局配置
└── app.wxss           # 全局样式
```

## 🎨 页面说明

### 1. 首页 (pages/index)
- 输入框
- 热门案例
- 返现横幅
- 核心卖点展示

### 2. 生成页 (pages/generate)
- 实时进度条
- 进度消息
- 速度对比（vs马蜂窝）
- 返现提示

### 3. 结果页 (pages/result)
- 返现横幅（显示预估金额）
- 统计信息
- 攻略内容
- 复制/分享按钮

### 4. 返现说明页 (pages/cashback)
- vs马蜂窝对比
- 返现案例
- 返现规则
- FAQ

## 🚀 快速开始

### 1. 配置后端地址

编辑 `app.js` 中的 `apiBaseUrl`：
```javascript
globalData: {
  apiBaseUrl: 'http://47.82.159.93:5000/api'
}
```

### 2. 微信开发者工具

1. 打开微信开发者工具
2. 导入项目，选择 `miniprogram` 目录
3. 填写AppID（或使用测试号）
4. 编译运行

### 3. 测试流程

1. 首页输入需求："海口3天亲子游"
2. 点击"30秒生成攻略"
3. 查看生成进度
4. 查看结果和返现金额

## 🎨 设计规范

### 颜色
- 主色：`#20B2AA` (薄荷绿)
- 辅色：`#5FCCC4` (浅薄荷绿)
- 文字：`#333333` (主文字)
- 提示：`#999999` (辅助文字)

### 字号
- 标题：48rpx
- 正文：28rpx
- 小字：24rpx

### 圆角
- 小：8rpx
- 中：16rpx
- 大：24rpx

## 📝 待优化

- [ ] Markdown渲染（当前为纯文本）
- [ ] WebSocket实时进度（当前为轮询）
- [ ] 图片资源（icon占位）
- [ ] 骨架屏loading
- [ ] 分享海报生成

## 🔗 后端API

详见 `/root/clawd/wildtrip/backend/README.md`

---

**开发时间：** 2026-02-04  
**版本：** v1.0 MVP
