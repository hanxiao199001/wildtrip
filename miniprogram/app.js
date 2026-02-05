// 野游记 WildTrip - 小程序入口
const Towxml = require('./towxml/index')  // 🔥 引入towxml

App({
  globalData: {
    // API配置
    apiBaseUrl: 'http://47.82.159.93:5000/api',
    
    // 用户信息
    userInfo: null,
    
    // 返现比例
    cashbackRate: 0.5,  // 50%返现
    
    // 🔥 towxml实例
    towxml: new Towxml()
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
