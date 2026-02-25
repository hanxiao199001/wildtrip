// app.js
App({
  globalData: {
    openid: '',
    userInfo: null,
    apiBase: 'https://api.wildtrip.com.cn'
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
      const res = await this.request({
        url: '/api/user/login',
        method: 'POST',
        data: { code: loginRes.code }
      });

      if (res.success) {
        this.globalData.openid = res.openid;
        console.log('✅ 登录成功, openid:', res.openid);
        
        // 触发登录成功事件
        if (this.loginCallback) {
          this.loginCallback(res.openid);
        }
      } else {
        console.error('❌ 登录失败:', res.error);
        wx.showToast({
          title: '登录失败',
          icon: 'error'
        });
      }

    } catch (err) {
      console.error('❌ 自动登录异常:', err);
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

    // 等待登录完成
    return new Promise((resolve) => {
      this.loginCallback = resolve;
      
      // 如果5秒后还没登录,重新触发登录
      setTimeout(() => {
        if (!this.globalData.openid) {
          this.autoLogin();
        }
      }, 5000);
    });
  }
});
