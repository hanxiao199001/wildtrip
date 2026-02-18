# 快速集成分享海报 - 3步搞定

## 第1步：复制组件文件

将以下文件复制到你的小程序项目：
```
miniprogram/
  components/
    share-poster/
      ├── share-poster.js      ← 组件逻辑
      ├── share-poster.wxml    ← 组件模板
      ├── share-poster.wxss    ← 组件样式
      └── share-poster.json    ← 组件配置
```

---

## 第2步：修改攻略详情页

### 2.1 引入组件

**pages/guide/guide.json**
```json
{
  "navigationBarTitleText": "攻略详情",
  "usingComponents": {
    "share-poster": "/components/share-poster/share-poster"
  }
}
```

### 2.2 修改页面模板

**pages/guide/guide.wxml**

在攻略内容下方添加分享按钮：

```xml
<!-- 原有的攻略内容 -->
<view class="guide-container">
  <rich-text nodes="{{guideContent}}"></rich-text>
</view>

<!-- ✅ 新增：底部操作栏 -->
<view class="bottom-bar">
  <button class="btn-copy" bindtap="copyGuide">
    📋 复制
  </button>
  <button class="btn-share" bindtap="shareGuide">
    ✈️ 分享
  </button>
</view>

<!-- ✅ 新增：分享海报组件 -->
<share-poster 
  visible="{{showSharePoster}}"
  guideData="{{shareData}}"
  bind:close="onClosePoster"
/>
```

### 2.3 修改页面逻辑

**pages/guide/guide.js**

在 `data` 中添加：
```javascript
data: {
  guideContent: '',
  showSharePoster: false,  // ← 新增
  shareData: {}            // ← 新增
}
```

在 `methods` 中添加：
```javascript
// ✅ 分享按钮点击
shareGuide() {
  const guideInfo = this.data.currentGuide || {};
  
  this.setData({
    showSharePoster: true,
    shareData: {
      id: guideInfo.taskId || 'demo',
      title: this.extractTitle(this.data.guideContent),
      destination: this.extractDestination(this.data.guideContent),
      days: this.extractDays(this.data.guideContent),
      budget: this.extractBudget(this.data.guideContent),
      userName: wx.getStorageSync('userNickname') || '野游记用户',
      createdAt: new Date().toLocaleDateString('zh-CN')
    }
  });
},

// ✅ 关闭海报
onClosePoster() {
  this.setData({ showSharePoster: false });
},

// 辅助函数：从攻略内容提取信息
extractTitle(content) {
  const match = content.match(/<h1[^>]*>(.*?)<\/h1>/);
  return match ? match[1].replace(/<[^>]*>/g, '') : '我的旅行攻略';
},

extractDestination(content) {
  const match = content.match(/目的地[：:]\s*([^\n<]+)/);
  return match ? match[1].trim() : '';
},

extractDays(content) {
  const match = content.match(/(\d+)天/);
  return match ? parseInt(match[1]) : 0;
},

extractBudget(content) {
  const match = content.match(/预算[：:]\s*[¥￥]?(\d+[-~]?\d*)/);
  return match ? match[1] : '';
}
```

### 2.4 添加样式

**pages/guide/guide.wxss**

```css
/* 底部操作栏 */
.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  padding: 20rpx 40rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
  display: flex;
  gap: 20rpx;
  z-index: 100;
}

.btn-copy,
.btn-share {
  flex: 1;
  height: 80rpx;
  border-radius: 40rpx;
  font-size: 28rpx;
  font-weight: 600;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-copy {
  background: #F5F5F5;
  color: #666666;
}

.btn-share {
  background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
  color: white;
}

/* 攻略容器底部留空 */
.guide-container {
  padding-bottom: 140rpx;
}
```

---

## 第3步：测试

1. **编译小程序**
   ```bash
   微信开发者工具 → 编译
   ```

2. **点击"分享"按钮**
   - 应该弹出海报生成弹窗
   - 显示"正在生成海报..."

3. **查看生成的海报**
   - 海报应包含攻略标题、目的地、天数、预算
   - 有野游记 Logo 和二维码

4. **保存到相册**
   - 点击"保存到相册"
   - 首次需要授权相册权限
   - 成功后提示"已保存到相册"

---

## 🎯 完整示例代码

如果你的攻略页面结构不同，参考这个完整示例：

**pages/guide/guide.js**
```javascript
Page({
  data: {
    taskId: '',
    guideContent: '',
    generating: false,
    showSharePoster: false,
    shareData: {}
  },

  onLoad(options) {
    this.setData({ taskId: options.taskId });
    this.loadGuide();
  },

  // 加载攻略
  async loadGuide() {
    const res = await wx.request({
      url: `https://api.wildtrip.com.cn/api/task/${this.data.taskId}`,
      method: 'GET'
    });

    if (res.data.status === 'completed') {
      this.setData({ guideContent: res.data.result });
    }
  },

  // 复制攻略
  copyGuide() {
    wx.setClipboardData({
      data: this.data.guideContent.replace(/<[^>]*>/g, ''),
      success: () => {
        wx.showToast({ title: '已复制', icon: 'success' });
      }
    });
  },

  // 分享攻略
  shareGuide() {
    const content = this.data.guideContent;
    
    // 从内容中提取关键信息
    const titleMatch = content.match(/<h1[^>]*>(.*?)<\/h1>/);
    const title = titleMatch ? titleMatch[1].replace(/<[^>]*>/g, '') : '我的旅行攻略';
    
    const daysMatch = content.match(/(\d+)天/);
    const days = daysMatch ? parseInt(daysMatch[1]) : 0;
    
    const budgetMatch = content.match(/[¥￥](\d+[-~]?\d*)/);
    const budget = budgetMatch ? budgetMatch[1] : '';

    this.setData({
      showSharePoster: true,
      shareData: {
        id: this.data.taskId,
        title: title,
        destination: '',  // 根据实际情况提取
        days: days,
        budget: budget,
        userName: wx.getStorageSync('userInfo')?.nickName || '野游记用户',
        createdAt: new Date().toLocaleDateString('zh-CN')
      }
    });
  },

  // 关闭海报
  onClosePoster() {
    this.setData({ showSharePoster: false });
  }
});
```

---

## ⚠️ 常见问题

### Q1: 海报生成失败？
**A:** 检查 Canvas 是否正确初始化
```javascript
// 在 share-poster.js 中添加错误处理
query.select('#posterCanvas')
  .fields({ node: true, size: true })
  .exec((res) => {
    if (!res || !res[0]) {
      console.error('Canvas 节点未找到');
      return;
    }
    // 继续绘制...
  });
```

### Q2: 保存到相册失败？
**A:** 检查权限设置
```javascript
// 在 share-poster.js 的 saveToAlbum 方法中
wx.getSetting({
  success: (res) => {
    if (!res.authSetting['scope.writePhotosAlbum']) {
      wx.authorize({
        scope: 'scope.writePhotosAlbum',
        success: () => {
          this.doSaveImage();
        }
      });
    }
  }
});
```

### Q3: 二维码不显示？
**A:** 暂时先用文字占位，后续可以：
1. 使用 weapp-qrcode 库
2. 或调用后端接口获取小程序码

---

## 🎉 完成！

现在点击"分享"按钮，应该能看到精美的分享海报了！

**效果：**
- ✅ 点击分享 → 弹出海报生成中
- ✅ 自动绘制海报（包含攻略信息）
- ✅ 显示预览 + 保存按钮
- ✅ 保存到相册成功

**下一步优化：**
- 添加真实的小程序码
- 优化海报样式
- 添加封面图支持
- 统计分享数据
