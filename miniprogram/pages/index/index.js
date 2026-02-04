// 野游记首页
const app = getApp()

Page({
  data: {
    query: '',
    isGenerating: false,
    examples: [
      { query: '海口3天亲子游，预算5000', tag: '亲子游' },
      { query: '成都2天美食游，预算2000', tag: '美食游' },
      { query: '上海周末游，预算1000', tag: '周末游' },
      { query: '西安4天穷游，预算800', tag: '穷游' }
    ]
  },

  onLoad() {
    console.log('🏠 首页加载')
  },

  // 输入变化
  onQueryInput(e) {
    this.setData({
      query: e.detail.value
    })
  },

  // 点击案例
  onExampleTap(e) {
    const query = e.currentTarget.dataset.query
    this.setData({ query })
  },

  // 生成攻略
  onGenerate() {
    const { query } = this.data
    
    if (!query.trim()) {
      wx.showToast({
        title: '请输入您的需求',
        icon: 'none'
      })
      return
    }

    // 跳转到生成页
    wx.navigateTo({
      url: `/pages/generate/generate?query=${encodeURIComponent(query)}`
    })
  },

  // 查看返现说明
  onCashbackInfo() {
    wx.switchTab({
      url: '/pages/cashback/cashback'
    })
  }
})
