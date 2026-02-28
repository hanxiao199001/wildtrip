// components/share-poster/share-poster.js
// 🎨 优化版 - 更有分享欲望的海报设计
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
    // 🎨 生成海报（全新视觉设计）
    async generatePoster() {
      this.setData({ generating: true });

      const { title, destination, days, budget, userName, createdAt } = this.properties.guideData;

      const query = this.createSelectorQuery();
      query.select('#posterCanvas')
        .fields({ node: true, size: true })
        .exec(async (res) => {
          if (!res || !res[0]) {
            console.error('Canvas 节点未找到');
            wx.showToast({ title: '生成失败', icon: 'none' });
            this.setData({ generating: false });
            return;
          }

          const canvas = res[0].node;
          const ctx = canvas.getContext('2d');

          const dpr = wx.getSystemInfoSync().pixelRatio;
          canvas.width = 750 * dpr;
          canvas.height = 1334 * dpr;
          ctx.scale(dpr, dpr);

          // ========== 🎨 全新视觉设计 ==========

          // 1. 绘制渐变背景（橙粉渐变）
          const bgGradient = ctx.createLinearGradient(0, 0, 750, 1334);
          bgGradient.addColorStop(0, '#FF6B35');
          bgGradient.addColorStop(0.3, '#FF8C42');
          bgGradient.addColorStop(0.7, '#FFA07A');
          bgGradient.addColorStop(1, '#FFB88C');
          ctx.fillStyle = bgGradient;
          ctx.fillRect(0, 0, 750, 1334);

          // 2. 绘制装饰圆形（背景点缀）
          ctx.globalAlpha = 0.1;
          ctx.fillStyle = '#FFFFFF';
          ctx.beginPath();
          ctx.arc(600, 100, 150, 0, Math.PI * 2);
          ctx.fill();
          ctx.beginPath();
          ctx.arc(100, 1200, 120, 0, Math.PI * 2);
          ctx.fill();
          ctx.globalAlpha = 1;

          // 3. 绘制主卡片（白色圆角卡片）
          this.drawRoundRect(ctx, 30, 150, 690, 1000, 30, '#FFFFFF');
          ctx.shadowColor = 'rgba(0,0,0,0.15)';
          ctx.shadowBlur = 30;
          ctx.shadowOffsetY = 15;
          ctx.fill();
          ctx.shadowColor = 'transparent';
          ctx.shadowBlur = 0;
          ctx.shadowOffsetY = 0;

          // 4. 顶部 Logo 区（橙色圆角条）
          const logoGradient = ctx.createLinearGradient(60, 180, 690, 180);
          logoGradient.addColorStop(0, '#FF6B35');
          logoGradient.addColorStop(1, '#FF8C42');
          this.drawRoundRect(ctx, 60, 180, 630, 120, 20, logoGradient);
          ctx.fill();

          ctx.fillStyle = '#FFFFFF';
          ctx.font = 'bold 52px sans-serif';
          ctx.fillText('野游记', 90, 245);

          ctx.font = '28px sans-serif';
          ctx.fillText('不走寻常路 · 就走野路子', 90, 280);

          // 5. 攻略标题（大字加粗）
          ctx.fillStyle = '#1A1A1A';
          ctx.font = 'bold 44px sans-serif';
          this.drawText(ctx, title || '我的旅行攻略', 90, 360, 570, 60);

          // 6. 封面图区域（渐变占位）
          const coverGradient = ctx.createLinearGradient(90, 450, 660, 450);
          coverGradient.addColorStop(0, '#FFF4E6');
          coverGradient.addColorStop(1, '#FFE8D1');
          this.drawRoundRect(ctx, 90, 450, 570, 280, 16, coverGradient);
          ctx.fill();

          // 封面图中央 icon
          ctx.fillStyle = '#FF6B35';
          ctx.font = 'bold 80px sans-serif';
          ctx.textAlign = 'center';
          ctx.fillText('\uD83D\uDDFA\uFE0F', 375, 620);
          ctx.textAlign = 'left';

          // 7. 信息标签（圆角徽章样式）
          const infoItems = [
            { icon: '\uD83D\uDCCD', text: destination || '精彩旅程', color: '#FF6B35' },
            { icon: '\u23F0', text: (days || 3) + '天深度游', color: '#FF8C42' },
            { icon: '\uD83D\uDCB0', text: '\u00A5' + (budget || '待定') + '/人', color: '#FFA07A' }
          ];

          infoItems.forEach((item, index) => {
            const y = 770 + index * 70;

            // 徽章背景
            const badgeGradient = ctx.createLinearGradient(90, y, 260, y);
            badgeGradient.addColorStop(0, item.color);
            badgeGradient.addColorStop(1, item.color + 'CC');
            this.drawRoundRect(ctx, 90, y, 560, 55, 28, badgeGradient);
            ctx.fill();

            // icon + 文字
            ctx.fillStyle = '#FFFFFF';
            ctx.font = 'bold 32px sans-serif';
            ctx.fillText(item.icon, 110, y + 38);
            ctx.font = '30px sans-serif';
            ctx.fillText(item.text, 160, y + 38);
          });

          // 8. 分割线
          ctx.strokeStyle = '#F0F0F0';
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.moveTo(90, 995);
          ctx.lineTo(660, 995);
          ctx.stroke();

          // 9. 用户信息
          ctx.fillStyle = '#999999';
          ctx.font = '26px sans-serif';
          ctx.fillText('\uD83D\uDC64 ' + (userName || '野游记用户'), 90, 1040);
          ctx.textAlign = 'right';
          ctx.fillText('\uD83D\uDCC5 ' + (createdAt || new Date().toLocaleDateString()), 660, 1040);
          ctx.textAlign = 'left';

          // 10. 二维码区域（白色圆角框）
          this.drawRoundRect(ctx, 265, 1060, 220, 220, 16, '#FFFFFF');
          ctx.shadowColor = 'rgba(0,0,0,0.1)';
          ctx.shadowBlur = 10;
          ctx.fill();
          ctx.shadowColor = 'transparent';
          ctx.shadowBlur = 0;

          await this.drawQRCode(ctx, 275, 1070);

          // 11. 二维码说明
          ctx.fillStyle = '#666666';
          ctx.font = '24px sans-serif';
          ctx.textAlign = 'center';
          ctx.fillText('长按识别 · 查看攻略', 375, 1310);

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

    // 生成真实小程序码
    async drawQRCode(ctx, x, y) {
      const guideId = this.properties.guideData.id || 'demo';

      try {
        // 调用后端接口生成小程序码
        const app = getApp();
        const apiBase = app.globalData.apiBase + '/api';

        const res = await new Promise((resolve, reject) => {
          wx.request({
            url: apiBase + '/qrcode/generate',
            method: 'POST',
            data: {
              guide_id: guideId,
              page: 'pages/result/result'
            },
            responseType: 'arraybuffer',
            success: (r) => resolve(r),
            fail: (e) => reject(e)
          });
        });

        if (res.statusCode === 200 && res.data) {
          // 将二进制数据写入临时文件
          const fs = wx.getFileSystemManager();
          const qrPath = wx.env.USER_DATA_PATH + '/qrcode_' + guideId.substring(0, 20) + '.png';

          fs.writeFileSync(qrPath, res.data, 'binary');

          // 创建图片对象并绘制
          const canvas = ctx.canvas;
          const qrImage = canvas.createImage();
          qrImage.src = qrPath;

          await new Promise((resolve) => {
            qrImage.onload = () => {
              ctx.drawImage(qrImage, x, y, 200, 200);
              resolve();
            };
            qrImage.onerror = () => {
              console.error('二维码图片加载失败');
              this.drawQRCodePlaceholder(ctx, x, y);
              resolve();
            };
          });
        } else {
          // 接口返回非200，使用占位
          this.drawQRCodePlaceholder(ctx, x, y);
        }
      } catch (err) {
        console.error('生成小程序码失败:', err);
        this.drawQRCodePlaceholder(ctx, x, y);
      }
    },

    // 占位二维码（后备方案）
    drawQRCodePlaceholder(ctx, x, y) {
      ctx.fillStyle = '#F8F8F8';
      ctx.fillRect(x, y, 200, 200);

      ctx.strokeStyle = '#E0E0E0';
      ctx.lineWidth = 2;
      ctx.strokeRect(x, y, 200, 200);

      ctx.fillStyle = '#999999';
      ctx.font = '24px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('扫码查看', x + 100, y + 100);
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
