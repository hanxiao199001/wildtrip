// 野游记 WildTrip - 小程序入口
const towxmlFn = require('./towxml/index')  // 🔥 引入towxml

App({
  globalData: {
    // API配置
    apiBaseUrl: 'https://api.wildtrip.com.cn/api',  // 线上环境
    // apiBaseUrl: 'http://192.168.1.76:5000/api',  // 本地开发（局域网IP，真机调试用）

    // 用户信息
    userInfo: null,

    // 返现比例
    cashbackRate: 0.5,  // 50%返现

    // 🔥 towxml（包装为对象，提供toJson方法供页面调用）
    towxml: {
      toJson: (str, type, option) => towxmlFn(str, type, option)
    }
  },

  onLaunch() {
    console.log('🔥 野游记启动')
    
    // 检查更新
    this.checkUpdate()
  },

  checkUpdate() {
    const updateManager = wx.getUpdateManager()
    
    updateManager.onCheckForUpdate((res) => {
      if (res.hasUpdate) {
        updateManager.onUpdateReady(() => {
          wx.showModal({
            title: '更新提示',
            content: '新版本已准备好，是否重启应用？',
            success: (res) => {
              if (res.confirm) {
                updateManager.applyUpdate()
              }
            }
          })
        })
      }
    })
  }
})
