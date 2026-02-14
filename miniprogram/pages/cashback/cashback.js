// 返现说明页面
Page({
  data: {},

  onLoad() {
    console.log('💰 返现说明页加载')
  },

  onStartUse() {
    wx.switchTab({
      url: '/pages/index/index'
    })
  }
})
