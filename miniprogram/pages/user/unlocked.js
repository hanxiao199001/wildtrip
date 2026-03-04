// pages/user/unlocked.js
// 我的已解锁攻略

const app = getApp();
const API_BASE = 'https://api.wildtrip.com.cn';

Page({
  data: {
    guides: [],
    loading: true,
    totalAmount: 0,
    totalCount: 0
  },

  onLoad() {
    this.loadUnlockedGuides();
  },

  onPullDownRefresh() {
    this.loadUnlockedGuides().then(() => {
      wx.stopPullDownRefresh();
    });
  },

  async loadUnlockedGuides() {
    this.setData({ loading: true });

    try {
      // 确保已登录
      if (!app.globalData.openid) {
        await this.login();
      }

      const res = await this.request({
        url: `${API_BASE}/api/vip/my_unlocked`,
        data: {
          openid: app.globalData.openid
        }
      });

      if (res.success) {
        const guides = res.guides || [];
        const totalAmount = guides.reduce((sum, g) => sum + (g.amount || 0), 0);
        
        this.setData({
          guides: guides,
          totalCount: res.total || 0,
          totalAmount: totalAmount / 100 // 分转元
        });
      } else {
        throw new Error(res.error || '加载失败');
      }

    } catch (err) {
      console.error('加载失败:', err);
      wx.showToast({ 
        title: '加载失败', 
        icon: 'error' 
      });
    } finally {
      this.setData({ loading: false });
    }
  },

  async login() {
    return new Promise((resolve, reject) => {
      wx.login({
        success: (res) => {
          wx.request({
            url: `${API_BASE}/api/user/login`,
            method: 'POST',
            data: { code: res.code },
            success: (res) => {
              if (res.data.success) {
                app.globalData.openid = res.data.openid;
                resolve(res.data.openid);
              } else {
                reject(new Error('登录失败'));
              }
            },
            fail: reject
          });
        },
        fail: reject
      });
    });
  },

  request(options) {
    return new Promise((resolve, reject) => {
      wx.request({
        ...options,
        success: (res) => resolve(res.data),
        fail: reject
      });
    });
  },

  onGuideTap(e) {
    const { id, type } = e.currentTarget.dataset;
    wx.navigateTo({
      url: `/pages/guide/detail?id=${id}&type=${type}`
    });
  }
});
