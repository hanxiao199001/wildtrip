// components/share-poster/share-poster.js
Component({
  properties: {
    visible: {
      type: Boolean,
      value: false
    },
    guideData: {
      type: Object,
      value: {}
    }
  },

  data: {
    posterUrl: '',
    generating: false
  },

  methods: {
    // 生成海报
    async generatePoster() {
      this.setData({ generating: true });
      
      const { title, destination, days, budget, userName, createdAt } = this.properties.guideData;
      
      // 创建 canvas 上下文
      const query = this.createSelectorQuery();
      query.select('#posterCanvas')
        .fields({ node: true, size: true })
        .exec(async (res) => {
          const canvas = res[0].node;
          const ctx = canvas.getContext('2d');
          
          const dpr = wx.getSystemInfoSync().pixelRatio;
          canvas.width = 750 * dpr;
          canvas.height = 1334 * dpr;
          ctx.scale(dpr, dpr);
          
          // 绘制背景渐变
          const gradient = ctx.createLinearGradient(0, 0, 0, 1334);
          gradient.addColorStop(0, '#FFF5EB');
          gradient.addColorStop(1, '#FFE8D6');
          ctx.fillStyle = gradient;
          ctx.fillRect(0, 0, 750, 1334);
          
          // 绘制顶部装饰
          ctx.fillStyle = '#FF6B35';
          ctx.fillRect(0, 0, 750, 200);
          
          // 绘制 Logo 和标题
          ctx.fillStyle = '#FFFFFF';
          ctx.font = 'bold 48px sans-serif';
          ctx.fillText('🌴 野游记 WildTrip', 50, 90);
          
          ctx.font = '28px sans-serif';
          ctx.fillText('不走寻常路，就走野路子', 50, 140);
          
          // 绘制攻略卡片
          this.drawRoundRect(ctx, 40, 240, 670, 600, 20, '#FFFFFF');
          ctx.shadowColor = 'rgba(0,0,0,0.1)';
          ctx.shadowBlur = 20;
          ctx.shadowOffsetY = 10;
          ctx.fill();
          
          // 攻略标题
          ctx.fillStyle = '#333333';
          ctx.font = 'bold 36px sans-serif';
          this.drawText(ctx, title, 80, 310, 590, 50);
          
          // 攻略信息
          ctx.font = '28px sans-serif';
          ctx.fillStyle = '#666666';
          
          const info = [
            `📍 ${destination || '丝绸之路'}`,
            `⏰ ${days || 15}天深度游`,
            `💰 ¥${budget || '6800-9200'}/人`
          ];
          
          info.forEach((text, index) => {
            ctx.fillText(text, 80, 420 + index * 60);
          });
          
          // 绘制亮点标签
          const tags = ['避坑指南', '省钱秘籍', '返现福利'];
          tags.forEach((tag, index) => {
            const x = 80 + index * 140;
            const y = 650;
            
            // 标签背景
            ctx.fillStyle = '#FFF3E0';
            ctx.fillRect(x, y, 120, 50);
            
            // 标签文字
            ctx.fillStyle = '#FF6B35';
            ctx.font = '24px sans-serif';
            ctx.fillText(tag, x + 10, y + 32);
          });
          
          // 底部用户信息
          ctx.fillStyle = '#999999';
          ctx.font = '24px sans-serif';
          ctx.fillText(`@${userName || '野游记用户'}`, 80, 760);
          ctx.fillText(createdAt || new Date().toLocaleDateString(), 500, 760);
          
          // 绘制分割线
          ctx.strokeStyle = '#E0E0E0';
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.moveTo(80, 810);
          ctx.lineTo(670, 810);
          ctx.stroke();
          
          // 生成二维码
          await this.drawQRCode(ctx, 275, 900);
          
          // 二维码说明
          ctx.fillStyle = '#666666';
          ctx.font = '28px sans-serif';
          ctx.textAlign = 'center';
          ctx.fillText('长按识别查看攻略', 375, 1150);
          
          // 底部 slogan
          ctx.fillStyle = '#CCCCCC';
          ctx.font = '20px sans-serif';
          ctx.fillText('Powered by 野游记 · AI驱动的旅行攻略', 375, 1250);
          
          // 导出图片
          wx.canvasToTempFilePath({
            canvas: canvas,
            success: (res) => {
              this.setData({
                posterUrl: res.tempFilePath,
                generating: false
              });
            },
            fail: (err) => {
              console.error('生成海报失败', err);
              wx.showToast({ title: '生成失败，请重试', icon: 'none' });
              this.setData({ generating: false });
            }
          });
        });
    },
    
    // 绘制圆角矩形
    drawRoundRect(ctx, x, y, w, h, r, fillColor) {
      ctx.beginPath();
      ctx.arc(x + r, y + r, r, Math.PI, Math.PI * 1.5);
      ctx.arc(x + w - r, y + r, r, Math.PI * 1.5, Math.PI * 2);
      ctx.arc(x + w - r, y + h - r, r, 0, Math.PI * 0.5);
      ctx.arc(x + r, y + h - r, r, Math.PI * 0.5, Math.PI);
      ctx.closePath();
      ctx.fillStyle = fillColor;
    },
    
    // 绘制多行文字（自动换行）
    drawText(ctx, text, x, y, maxWidth, lineHeight) {
      let line = '';
      let currentY = y;
      
      for (let i = 0; i < text.length; i++) {
        const testLine = line + text[i];
        const metrics = ctx.measureText(testLine);
        
        if (metrics.width > maxWidth && i > 0) {
          ctx.fillText(line, x, currentY);
          line = text[i];
          currentY += lineHeight;
        } else {
          line = testLine;
        }
      }
      ctx.fillText(line, x, currentY);
    },
    
    // 生成二维码
    async drawQRCode(ctx, x, y) {
      // 这里用简单的链接二维码（实际可以调后端生成小程序码）
      const guideId = this.properties.guideData.id || 'demo';
      const qrUrl = `https://api.wildtrip.com.cn/guide/${guideId}`;
      
      // 使用小程序的 qrcode 库生成二维码
      // 这里简化处理，绘制一个占位框
      ctx.fillStyle = '#FFFFFF';
      ctx.fillRect(x, y, 200, 200);
      
      ctx.strokeStyle = '#CCCCCC';
      ctx.lineWidth = 2;
      ctx.strokeRect(x, y, 200, 200);
      
      ctx.fillStyle = '#666666';
      ctx.font = '20px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('小程序码', x + 100, y + 100);
      
      // TODO: 实际项目中可以：
      // 1. 使用 weapp-qrcode 库生成二维码
      // 2. 或调用后端接口获取小程序码
    },
    
    // 保存到相册
    saveToAlbum() {
      wx.saveImageToPhotosAlbum({
        filePath: this.data.posterUrl,
        success: () => {
          wx.showToast({ title: '已保存到相册', icon: 'success' });
          this.close();
        },
        fail: (err) => {
          if (err.errMsg.includes('auth deny')) {
            wx.showModal({
              title: '需要相册权限',
              content: '请在设置中开启相册权限',
              success: (res) => {
                if (res.confirm) {
                  wx.openSetting();
                }
              }
            });
          }
        }
      });
    },
    
    // 关闭弹窗
    close() {
      this.triggerEvent('close');
      this.setData({ posterUrl: '' });
    },
    
    // 组件显示时生成海报
    onShow() {
      if (this.properties.visible && !this.data.posterUrl) {
        setTimeout(() => {
          this.generatePoster();
        }, 100);
      }
    }
  },
  
  lifetimes: {
    attached() {
      this.onShow();
    }
  },
  
  observers: {
    'visible': function(visible) {
      if (visible) {
        this.onShow();
      }
    }
  }
});
