// 野游记首页
const app = getApp()

Page({
  data: {
    query: '',
    mode: 'full',
    isGenerating: false,
    modes: [
      { id: 'full', name: '完整攻略', icon: '🎯' },
      { id: 'history', name: '人文历史', icon: '🏛️' },
      { id: 'food', name: '美食探店', icon: '🍜' },
      { id: 'hotel', name: '酒店推荐', icon: '🏨' }
    ],
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

  // 切换模式
  onModeChange(e) {
    const mode = e.currentTarget.dataset.mode
    this.setData({ mode })
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
    const { query, mode } = this.data
    
    if (!query.trim()) {
      wx.showToast({
        title: '请输入您的需求',
        icon: 'none'
      })
      return
    }

    // 跳转到生成页
    wx.navigateTo({
      url: `/pages/generate/generate?query=${encodeURIComponent(query)}&mode=${mode}`
    })
  },

  // 查看返现说明
  onCashbackInfo() {
    wx.switchTab({
      url: '/pages/cashback/cashback'
    })
  }
})
