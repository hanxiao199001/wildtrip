// pages/guide/detail.js
// 攻略详情页（免费开放）

const app = getApp();
const { API_BASE } = require('../../utils/config.js');

Page({
  data: {
    guideId: '',           // 攻略ID
    guideType: 'travel',   // travel 或 history
    guideData: null,       // 攻略数据
    loading: true
  },

  onLoad(options) {
    const { id, type } = options;

    if (!id) {
      wx.showToast({ title: '攻略ID缺失', icon: 'error' });
      setTimeout(() => wx.navigateBack(), 1500);
      return;
    }

    this.setData({
      guideId: id,
      guideType: type || 'travel'
    });

    this.init();
  },

  async init() {
    try {
      if (!app.globalData.openid) {
        await this.login();
      }
      await this.loadGuide();
    } catch (err) {
      console.error('初始化失败:', err);
      wx.showToast({ title: '加载失败', icon: 'error' });
    } finally {
      this.setData({ loading: false });
    }
  },

  // 登录获取openid
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

  // 加载攻略数据
  async loadGuide() {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${API_BASE}/api/guides/${this.data.guideId}`,
        success: (res) => {
          if (res.data.success) {
            this.setData({ guideData: res.data.guide });
            resolve(res.data.guide);
          } else {
            reject(new Error('加载攻略失败'));
          }
        },
        fail: reject
      });
    });
  },

  // 分享
  onShareAppMessage() {
    return {
      title: this.data.guideData?.title || '野游记攻略',
      path: `/pages/guide/detail?id=${this.data.guideId}&type=${this.data.guideType}`
    };
  }
});
