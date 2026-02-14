# 分享海报组件使用指南

## 📦 组件说明

`share-poster` 组件用于生成攻略分享海报，支持：
- ✅ 自动绘制精美海报
- ✅ 保存到相册
- ✅ 显示攻略关键信息
- ✅ 可添加二维码/小程序码

---

## 🚀 快速使用

### 1. 在攻略详情页引入组件

**pages/guide-detail/guide-detail.json**
```json
{
  "usingComponents": {
    "share-poster": "/components/share-poster/share-poster"
  }
}
```

### 2. 在 WXML 中添加组件

**pages/guide-detail/guide-detail.wxml**
```xml
<!-- 攻略页面 -->
<view class="guide-page">
  <!-- 攻略内容 -->
  <view class="guide-content">
    <rich-text nodes="{{guideContent}}"></rich-text>
  </view>
  
  <!-- 底部操作按钮 -->
  <view class="action-bar">
    <button class="btn-copy" bindtap="onCopy">📋 复制攻略</button>
    <button class="btn-share" bindtap="onShare">✈️ 分享</button>
  </view>
</view>

<!-- 分享海报组件 -->
<share-poster 
  visible="{{showPoster}}"
  guideData="{{posterData}}"
  bind:close="onClosePoster"
/>
```

### 3. 在 JS 中处理逻辑

**pages/guide-detail/guide-detail.js**
```javascript
Page({
  data: {
    showPoster: false,
    posterData: {},
    guideContent: '',
    guideInfo: {}
  },

  onLoad(options) {
    const guideId = options.id;
    this.loadGuide(guideId);
  },

  // 加载攻略
  async loadGuide(guideId) {
    const res = await wx.request({
      url: 'https://api.wildtrip.com.cn/api/guide/' + guideId,
      method: 'GET'
    });
    
    this.setData({
      guideContent: res.data.content,
      guideInfo: res.data
    });
  },

  // 点击分享按钮
  onShare() {
    // 准备海报数据
    const posterData = {
      id: this.data.guideInfo.id,
      title: this.data.guideInfo.title || '丝绸之路15天野路子攻略',
      destination: this.data.guideInfo.destination || '西安→敦煌→乌鲁木齐',
      days: this.data.guideInfo.days || 15,
      budget: this.data.guideInfo.budget || '6800-9200',
      userName: wx.getStorageSync('userInfo')?.nickName || '野游记用户',
      createdAt: new Date().toLocaleDateString('zh-CN')
    };
    
    this.setData({
      showPoster: true,
      posterData: posterData
    });
  },

  // 关闭海报
  onClosePoster() {
    this.setData({ showPoster: false });
  },

  // 复制攻略
  onCopy() {
    wx.setClipboardData({
      data: this.data.guideContent,
      success: () => {
        wx.showToast({ title: '已复制到剪贴板', icon: 'success' });
      }
    });
  }
});
```

### 4. 添加样式

**pages/guide-detail/guide-detail.wxss**
```css
.guide-page {
  padding-bottom: 120rpx;
}

.guide-content {
  padding: 40rpx;
}

/* 底部操作栏 */
.action-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  padding: 20rpx 40rpx;
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
  display: flex;
  gap: 20rpx;
}

.btn-copy,
.btn-share {
  flex: 1;
  height: 80rpx;
  border-radius: 40rpx;
  font-size: 28rpx;
  font-weight: 600;
  border: none;
}

.btn-copy {
  background: #F5F5F5;
  color: #666666;
}

.btn-share {
  background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
  color: white;
}
```

---

## 🎨 自定义海报

### 修改海报样式

在 `share-poster.js` 的 `generatePoster()` 方法中修改：

**1. 修改配色**
```javascript
// 修改顶部背景色
ctx.fillStyle = '#你的颜色';

// 修改渐变
const gradient = ctx.createLinearGradient(0, 0, 0, 1334);
gradient.addColorStop(0, '#起始色');
gradient.addColorStop(1, '#结束色');
```

**2. 添加封面图**
```javascript
// 在海报中添加攻略封面图
const coverImage = canvas.createImage();
coverImage.src = this.properties.guideData.coverUrl;
coverImage.onload = () => {
  ctx.drawImage(coverImage, 80, 500, 590, 300);
};
```

**3. 修改字体大小**
```javascript
ctx.font = 'bold 48px sans-serif';  // 标题
ctx.font = '28px sans-serif';       // 正文
ctx.font = '24px sans-serif';       // 小字
```

---

## 🔧 添加小程序码

### 方案1：使用第三方库（推荐）

**安装 weapp-qrcode：**
```bash
npm install --save weapp-qrcode
```

**在组件中使用：**
```javascript
import QRCode from 'weapp-qrcode';

// 在 drawQRCode 方法中
drawQRCode(ctx, x, y) {
  const qrcode = new QRCode('canvas', {
    text: `https://api.wildtrip.com.cn/guide/${this.properties.guideData.id}`,
    width: 200,
    height: 200,
    colorDark: '#000000',
    colorLight: '#ffffff',
    correctLevel: QRCode.CorrectLevel.H
  });
  
  // 将二维码绘制到海报 canvas
  const qrCanvas = qrcode._oCanvas;
  ctx.drawImage(qrCanvas, x, y, 200, 200);
}
```

### 方案2：调用后端接口获取小程序码

**后端接口（Python + Flask）：**
```python
# /api/qrcode/generate
@app.route('/api/qrcode/generate', methods=['POST'])
def generate_qrcode():
    guide_id = request.json.get('guide_id')
    
    # 调用微信小程序码接口
    access_token = get_access_token()
    url = f'https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={access_token}'
    
    data = {
        'scene': guide_id,
        'page': 'pages/guide-detail/guide-detail',
        'width': 200
    }
    
    response = requests.post(url, json=data)
    
    # 保存图片
    filename = f'qrcode_{guide_id}.png'
    with open(f'/tmp/{filename}', 'wb') as f:
        f.write(response.content)
    
    return jsonify({'url': f'https://api.wildtrip.com.cn/qrcodes/{filename}'})
```

**小程序端调用：**
```javascript
async drawQRCode(ctx, x, y) {
  const res = await wx.request({
    url: 'https://api.wildtrip.com.cn/api/qrcode/generate',
    method: 'POST',
    data: { guide_id: this.properties.guideData.id }
  });
  
  const qrImage = canvas.createImage();
  qrImage.src = res.data.url;
  qrImage.onload = () => {
    ctx.drawImage(qrImage, x, y, 200, 200);
  };
}
```

---

## 📋 海报数据格式

```javascript
{
  id: 'guide_123',              // 攻略ID
  title: '丝绸之路15天野路子攻略',  // 攻略标题
  destination: '西安→敦煌',      // 目的地
  days: 15,                     // 天数
  budget: '6800-9200',          // 预算
  userName: '张三',             // 用户昵称
  createdAt: '2026/2/14',       // 生成日期
  coverUrl: 'https://...'       // 封面图（可选）
}
```

---

## ⚠️ 注意事项

1. **Canvas 2D API**  
   使用 `type="2d"` 的新版 Canvas，需要微信基础库 2.9.0+

2. **相册权限**  
   首次保存需要用户授权相册权限

3. **图片大小**  
   默认海报尺寸 750×1334px，生成的图片大约 200-500KB

4. **性能优化**  
   - 只在需要时生成海报（避免每次打开都生成）
   - 可以缓存已生成的海报 URL

5. **字体支持**  
   小程序 Canvas 支持的字体有限，自定义字体需要额外处理

---

## 🎯 效果预览

生成的海报包含：
```
┌─────────────────────────────┐
│   🌴 野游记 WildTrip        │ ← 橙色顶部
│   不走寻常路，就走野路子    │
├─────────────────────────────┤
│                              │
│  【丝绸之路15天野路子攻略】  │ ← 白色卡片
│                              │
│  📍 西安→敦煌→乌鲁木齐       │
│  ⏰ 15天深度游               │
│  💰 ¥6800-9200/人            │
│                              │
│  [避坑指南] [省钱秘籍] [返现]│ ← 标签
│                              │
│  @张三 · 2026/2/14          │
├─────────────────────────────┤
│       [小程序码]             │
│    长按识别查看攻略          │
│                              │
│  Powered by 野游记          │
└─────────────────────────────┘
```

---

## 🚀 下一步优化

1. **添加封面图**：支持攻略封面图展示
2. **动态样式**：根据目的地类型切换配色
3. **分享统计**：记录分享次数和来源
4. **水印保护**：添加防盗用水印
5. **多尺寸**：适配朋友圈/微博等不同尺寸

---

**🎉 部署完成，现在可以生成精美分享海报了！**
