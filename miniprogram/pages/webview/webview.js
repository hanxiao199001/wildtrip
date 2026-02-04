// WebView页面 - 打开美团链接
Page({
  data: {
    url: ''
  },

  onLoad(options) {
    const url = decodeURIComponent(options.url || '')
    const title = decodeURIComponent(options.title || '美团')

    // 设置导航栏标题
    wx.setNavigationBarTitle({
      title: title.substring(0, 20)  // 最多20字符
    })

    this.setData({ url })
  },

  onMessage(e) {
    console.log('WebView message:', e.detail.data)
  },

  onError(e) {
    console.error('WebView error:', e.detail)
    
    wx.showModal({
      title: '无法打开链接',
      content: '请稍后重试或复制链接到浏览器打开',
      confirmText: '复制链接',
      success: (res) => {
        if (res.confirm) {
          wx.setClipboardData({
            data: this.data.url,
            success: () => {
              wx.showToast({
                title: '链接已复制',
                icon: 'success'
              })
            }
          })
        }
      }
    })
  }
})
