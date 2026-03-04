// pages/guide/detail.js
// 攻略详情页 - 支持解锁支付

const app = getApp();
const API_BASE = 'https://api.wildtrip.com.cn';

Page({
  data: {
    guideId: '',           // 攻略ID
    guideType: 'travel',   // travel 或 history
    guideData: null,       // 攻略数据
    unlocked: true,        // 免费开放，所有攻略均可查看
    price: 0,              // 免费
    loading: true,
    paying: false
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
      // 1. 检查登录状态
      if (!app.globalData.openid) {
        await this.login();
      }

      // 2. 当前免费开放，跳过解锁检查
      // await this.checkUnlock();

      // 3. 加载攻略数据
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

  // 检查攻略是否已解锁
  async checkUnlock() {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${API_BASE}/api/vip/check_unlock`,
        data: {
          openid: app.globalData.openid,
          guide_id: this.data.guideId
        },
        success: (res) => {
          if (res.data.success) {
            this.setData({ unlocked: res.data.unlocked });
            console.log('解锁状态:', res.data.unlocked);
            resolve(res.data.unlocked);
          } else {
            reject(new Error('检查解锁状态失败'));
          }
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

  // 点击解锁按钮
  onUnlockTap() {
    if (this.data.paying) return;

    wx.showModal({
      title: '解锁攻略',
      content: `确认支付 ¥${this.data.price} 解锁完整攻略?`,
      confirmText: '立即支付',
      success: (res) => {
        if (res.confirm) {
          this.createOrder();
        }
      }
    });
  },

  // 创建订单
  async createOrder() {
    this.setData({ paying: true });

    wx.showLoading({ title: '创建订单中...' });

    try {
      const productId = this.data.guideType === 'history' 
        ? 'guide_history' 
        : 'guide_travel';

      const res = await this.request({
        url: `${API_BASE}/api/vip/create_order`,
        method: 'POST',
        data: {
          openid: app.globalData.openid,
          product_id: productId,
          guide_id: this.data.guideId
        }
      });

      wx.hideLoading();

      if (!res.success) {
        throw new Error(res.error || '创建订单失败');
      }

      // 调起微信支付
      await this.requestPayment(res.pay_params, res.order.order_no);

    } catch (err) {
      wx.hideLoading();
      console.error('创建订单失败:', err);
      wx.showToast({ 
        title: err.message || '创建订单失败', 
        icon: 'error' 
      });
    } finally {
      this.setData({ paying: false });
    }
  },

  // 调起微信支付
  async requestPayment(payParams, orderNo) {
    return new Promise((resolve, reject) => {
      wx.requestPayment({
        ...payParams,
        success: () => {
          console.log('支付成功');
          wx.showToast({ title: '支付成功', icon: 'success' });
          
          // 轮询查询订单状态
          this.checkPaymentStatus(orderNo);
          resolve();
        },
        fail: (err) => {
          console.error('支付失败:', err);
          
          if (err.errMsg.includes('cancel')) {
            wx.showToast({ title: '支付已取消', icon: 'none' });
          } else {
            wx.showToast({ title: '支付失败', icon: 'error' });
          }
          
          reject(err);
        }
      });
    });
  },

  // 轮询查询订单状态
  async checkPaymentStatus(orderNo, count = 0) {
    if (count > 15) {
      wx.showModal({
        title: '提示',
        content: '支付结果查询超时,请刷新页面查看',
        showCancel: false
      });
      return;
    }

    try {
      const res = await this.request({
        url: `${API_BASE}/api/payment/query_order`,
        data: { order_id: orderNo }
      });

      if (res.order.status === 'paid') {
        // 支付成功,标记为已解锁
        this.setData({ unlocked: true });
        
        wx.showModal({
          title: '解锁成功',
          content: '攻略已解锁,即将刷新页面',
          showCancel: false,
          success: () => {
            this.init(); // 重新加载
          }
        });
      } else {
        // 继续轮询
        setTimeout(() => {
          this.checkPaymentStatus(orderNo, count + 1);
        }, 2000);
      }

    } catch (err) {
      console.error('查询订单状态失败:', err);
      setTimeout(() => {
        this.checkPaymentStatus(orderNo, count + 1);
      }, 2000);
    }
  },

  // 封装request
  request(options) {
    return new Promise((resolve, reject) => {
      wx.request({
        ...options,
        success: (res) => {
          resolve(res.data);
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
