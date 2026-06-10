// pages/user/unlocked.js
// 我的攻略（生成历史）

const app = getApp();
const { API_BASE } = require('../../utils/config.js');

Page({
  data: {
    guides: [],
    loading: true,
    totalCount: 0
  },

  onShow() {
    this.loadMyGuides();
  },

  onPullDownRefresh() {
    this.loadMyGuides().then(() => {
      wx.stopPullDownRefresh();
    });
  },

  async loadMyGuides() {
    this.setData({ loading: true });

    try {
      if (!app.globalData.openid) {
        await this.login();
      }

      const guides = await this.request({
        url: `${API_BASE}/api/user/${app.globalData.openid}/guides`
      });

      const list = Array.isArray(guides) ? guides : [];
      this.setData({
        guides: list.map(g => ({
          ...g,
          // 从 seo_url 提取 slug，供详情页使用
          slug: g.seo_url ? g.seo_url.split('/').pop().replace('.html', '') : '',
          date: (g.created_at || '').slice(0, 10),
          typeLabel: g.mode === 'history' ? '人文历史' : '旅行攻略'
        })),
        totalCount: list.length
      });
    } catch (err) {
      console.error('加载失败:', err);
      wx.showToast({ title: '加载失败', icon: 'error' });
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
    const { slug, title } = e.currentTarget.dataset;
    if (!slug) {
      wx.showToast({ title: '该攻略暂不支持查看', icon: 'none' });
      return;
    }
    wx.navigateTo({
      url: `/pages/guide-detail/guide-detail?slug=${encodeURIComponent(slug)}&title=${encodeURIComponent(title || '攻略详情')}`
    });
  },

  onExplore() {
    wx.switchTab({ url: '/pages/index/index' });
  }
});
