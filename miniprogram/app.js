// app.js
const towxml = require('/towxml/index')
const { API_BASE } = require('./utils/config.js')

App({
  globalData: {
    openid: '',
    userInfo: null,
    apiBase: API_BASE,
    towxml: towxml
  },

  onLaunch() {
    console.log('🚀 野游记小程序启动');
    this.autoLogin();
  },

  // 自动登录获取openid
  async autoLogin() {
    try {
      console.log('开始自动登录...');

      // 1. 调用wx.login获取code
      const loginRes = await this.wxLogin();
      console.log('wx.login success, code:', loginRes.code);

      // 2. 调用后端登录接口
      let res
      try {
        res = await this.request({
          url: '/api/user/login',
          method: 'POST',
          data: { code: loginRes.code }
        });
      } catch (httpErr) {
        console.error('❌ 后端登录接口异常:', httpErr.message);
        // 🔥 后端不可用时，用wx.login的code生成临时标识，保证基本可用
        const fallbackId = 'wx_' + loginRes.code.substring(0, 16);
        console.warn('⚠️ 使用临时标识:', fallbackId);
        this.globalData.openid = fallbackId;
        if (this.loginCallback) {
          this.loginCallback(fallbackId);
          this.loginCallback = null;
        }
        return;
      }

      if (res.success && res.openid) {
        this.globalData.openid = res.openid;
        console.log('✅ 登录成功, openid:', res.openid);

        // 🔥 触发登录成功事件
        if (this.loginCallback) {
          this.loginCallback(res.openid);
          this.loginCallback = null;
        }
      } else {
        console.error('❌ 登录失败:', res.error);
        // 🔥 登录失败也要通知等待者，否则getOpenid永远挂起
        if (this.loginCallback) {
          this.loginCallback(null);
          this.loginCallback = null;
        }
      }

    } catch (err) {
      console.error('❌ 自动登录异常:', err);
      // 🔥 异常也要通知等待者
      if (this.loginCallback) {
        this.loginCallback(null);
        this.loginCallback = null;
      }
    }
  },

  // 封装wx.login
  wxLogin() {
    return new Promise((resolve, reject) => {
      wx.login({
        success: resolve,
        fail: reject
      });
    });
  },

  // 封装request
  request(options) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: this.globalData.apiBase + options.url,
        method: options.method || 'GET',
        data: options.data || {},
        header: options.header || {
          'Content-Type': 'application/json'
        },
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.data);
          } else {
            reject(new Error(`HTTP ${res.statusCode}`));
          }
        },
        fail: reject
      });
    });
  },

  // 获取openid (如果未登录会自动登录)
  async getOpenid() {
    if (this.globalData.openid) {
      return this.globalData.openid;
    }

    // 🔥 等待登录完成，设定超时保底
    return new Promise((resolve) => {
      this.loginCallback = (openid) => {
        resolve(openid || '');
      };

      // 如果3秒后还没登录，重新触发一次
      setTimeout(() => {
        if (!this.globalData.openid) {
          console.warn('⚠️ 等待3秒未登录，重新触发autoLogin');
          this.autoLogin();
        }
      }, 3000);

      // 🔥 10秒兜底：无论如何都resolve，防止永久挂起
      setTimeout(() => {
        if (!this.globalData.openid) {
          console.error('❌ 登录10秒超时，放弃等待');
          resolve('');
        }
      }, 10000);
    });
  }
});
