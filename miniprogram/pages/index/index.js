// 野游记首页
const app = getApp()
const api = require('../../utils/api')

// 📜 人文历史路线推荐主题
var HISTORY_THEMES = [
  {
    icon: '📝',
    title: '苏东坡被贬路线',
    desc: '黄州→惠州→儋州，诗酒人生',
    query: '苏东坡被贬路线15天，追寻东坡足迹'
  },
  {
    icon: '⚔️',
    title: '三国古战场巡礼',
    desc: '赤壁→荆州→成都，英雄往事',
    query: '三国古战场巡礼10天，赤壁荆州成都'
  },
  {
    icon: '🏯',
    title: '千年古都文化游',
    desc: '西安→洛阳→开封→南京',
    query: '四大古都历史文化游12天'
  },
  {
    icon: '🍵',
    title: '茶马古道探秘',
    desc: '从普洱到拉萨的千年茶路',
    query: '茶马古道历史文化游10天'
  },
  {
    icon: '🎭',
    title: '李白游历路线',
    desc: '蜀道→长安→金陵→庐山',
    query: '李白游历路线12天，追寻诗仙足迹'
  },
  {
    icon: '🏮',
    title: '丝绸之路文化游',
    desc: '西安→敦煌→嘉峪关',
    query: '丝绸之路文化游8天，从长安到敦煌'
  }
]

Page({
  data: {
    query: '',
    isGenerating: false,
    currentMode: 'full',                // 🔥 当前模式：full / history
    placeholderText: '说一句话，30秒生成攻略\n例如：海口3天亲子游，预算5000',
    btnText: '🚀 生成攻略',
    historyThemes: HISTORY_THEMES,      // 📜 人文历史路线推荐主题
    featuredGuides: []                  // 精选攻略
  },

  onLoad() {
    console.log('🏠 首页加载')
    this.loadFeaturedGuides()
  },

  onShow() {
    // 每次显示页面时刷新精选（可能有新攻略生成）
    this.loadFeaturedGuides()

    // 🔥 处理从其他页面传来的查询（如"生成同款"）
    if (app.globalData._pendingQuery) {
      this.setData({ query: app.globalData._pendingQuery })
      app.globalData._pendingQuery = null
      wx.showToast({
        title: '已填充，点击生成',
        icon: 'none',
        duration: 1500
      })
      wx.pageScrollTo({ scrollTop: 0, duration: 300 })
    }
  },

  // 🔥 切换模式
  onModeChange(e) {
    var mode = e.currentTarget.dataset.mode
    if (mode === this.data.currentMode) return

    var isHistory = mode === 'history'
    this.setData({
      currentMode: mode,
      query: '',
      placeholderText: isHistory
        ? '输入人文历史主题\n例如：苏东坡被贬路线15天'
        : '说一句话，30秒生成攻略\n例如：海口3天亲子游，预算5000',
      btnText: isHistory ? '📜 生成人文历史路线' : '🚀 生成攻略'
    })

    console.log('🔄 切换模式:', mode)
  },

  // 📜 点击历史人文推荐主题
  onHistoryThemeTap(e) {
    var query = e.currentTarget.dataset.query
    this.setData({ query: query })
    wx.showToast({
      title: '已填充，点击生成',
      icon: 'none',
      duration: 1500
    })
    wx.pageScrollTo({ scrollTop: 0, duration: 300 })
  },

  // 加载精选攻略
  async loadFeaturedGuides() {
    try {
      var guides = await api.getFeaturedGuides(6)
      this.setData({ featuredGuides: guides || [] })
      console.log('🌟 精选攻略加载成功:', (guides || []).length, '篇')
    } catch (error) {
      console.log('精选攻略加载失败，使用默认数据:', error)
      // API失败时使用前端fallback数据
      this.setData({
        featuredGuides: [
          {
            slug: '_fallback_haikou',
            title: '海口3天亲子游攻略',
            destination: '海口',
            days: 3,
            category: '亲子游',
            budget: 5000,
            views: 856,
            likes: 72,
            query: '海口3天亲子游，预算5000'
          },
          {
            slug: '_fallback_chengdu',
            title: '成都2天美食之旅',
            destination: '成都',
            days: 2,
            category: '美食游',
            budget: 2000,
            views: 1203,
            likes: 98,
            query: '成都2天美食游，预算2000'
          },
          {
            slug: '_fallback_shanghai',
            title: '上海周末轻松游',
            destination: '上海',
            days: 2,
            category: '周末游',
            budget: 1000,
            views: 645,
            likes: 51,
            query: '上海周末游，预算1000'
          },
          {
            slug: '_fallback_xian',
            title: '西安4天深度穷游',
            destination: '西安',
            days: 4,
            category: '穷游',
            budget: 800,
            views: 932,
            likes: 85,
            query: '西安4天穷游，预算800'
          }
        ]
      })
    }
  },

  // 封面图加载失败时标记，显示渐变色底
  onCoverImageError(e) {
    var index = e.currentTarget.dataset.index
    this.setData({
      ['featuredGuides[' + index + ']._imgFailed']: true
    })
  },

  // 输入变化
  onQueryInput(e) {
    this.setData({
      query: e.detail.value
    })
  },

  // 点击精选攻略卡片
  onFeaturedTap(e) {
    var item = e.currentTarget.dataset.item

    // 如果是预设/fallback攻略（有query字段），填充搜索框
    if (item.query) {
      this.setData({ query: item.query })
      wx.showToast({
        title: '已填充，点击生成',
        icon: 'none',
        duration: 1500
      })
      // 滚动到顶部搜索区域
      wx.pageScrollTo({
        scrollTop: 0,
        duration: 300
      })
      return
    }

    // 如果是真实攻略（有slug且非预设），跳转到攻略详情页
    if (item.slug && !item.slug.startsWith('_preset') && !item.slug.startsWith('_fallback')) {
      // 🔥 通过全局变量传递攻略数据（避免URL参数过长被截断）
      app.globalData._guideItem = item
      wx.navigateTo({
        url: '/pages/guide-detail/guide-detail'
      })
    }
  },

  // 生成攻略
  onGenerate() {
    var query = this.data.query
    var mode = this.data.currentMode

    if (!query.trim()) {
      wx.showToast({
        title: mode === 'history' ? '请输入人文历史主题' : '请输入您的需求',
        icon: 'none'
      })
      return
    }

    // 🔥 将当前模式传递给后续页面
    app.globalData._generateMode = mode

    // 跳转到需求澄清页（澄清后自动跳转生成页）
    wx.navigateTo({
      url: '/pages/clarify/clarify?query=' + encodeURIComponent(query) + '&mode=' + mode
    })
  },

  // 查看返现说明
  onCashbackInfo() {
    wx.switchTab({
      url: '/pages/cashback/cashback'
    })
  }
})
