// 野游记首页
const app = getApp()
const api = require('../../utils/api')

// 🔀 Fisher-Yates 随机洗牌
function shuffleArray(arr) {
  var a = arr.slice()
  for (var i = a.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1))
    var t = a[i]; a[i] = a[j]; a[j] = t
  }
  return a
}

// 🏙️ 从标题/slug中猜测城市名
function guessCity(item) {
  var t = (item.title || '') + (item.slug || '')
  var m = t.match(/[\u4e00-\u9fa5]{2,4}(?=[0-9\-\u5929\u65e5])/)
  return m ? m[0] : (item.destination || '')
}

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

  // 加载精选攻略（含过滤、去重、验证）
  async loadFeaturedGuides() {
    try {
      var raw = await api.getFeaturedGuides(20)
      var list = raw || []

      // ① 过滤低质量标题 + 清除假数据
      var badTitles = ['旅行攻略', '旅游攻略', '出行攻略', '游玩攻略', '攻略详情']
      var tooSimpleRe = /^.{2,4}\d+[日天][a-zA-Z\u4e00-\u9fa5]{0,3}游$/
      list = list.filter(function (g) {
        var t = (g.title || '').trim()
        if (t.length <= 7) return false
        if (badTitles.indexOf(t) >= 0) return false
        if (tooSimpleRe.test(t)) return false
        return true
      })

      // 清除假数据：unsplash占位图、虚假浏览/点赞数
      list.forEach(function (g) {
        // 去掉unsplash占位图
        if (g.cover_image && g.cover_image.indexOf('unsplash.com') >= 0) {
          g.cover_image = ''
        }
        // 清零虚假的views/likes
        g.views = 0
        g.likes = 0
      })

      // ② 标题去重
      var seenTitle = {}
      list = list.filter(function (g) {
        var k = (g.title || '').trim()
        if (seenTitle[k]) return false
        seenTitle[k] = true
        return true
      })

      // ③ 城市去重（每城最多1条）
      var seenCity = {}
      list = list.filter(function (g) {
        var c = guessCity(g)
        if (!c) return true
        if (seenCity[c]) return false
        seenCity[c] = true
        return true
      })

      // 缓存全部有效攻略，供"换一批"使用
      this._allValidGuides = list

      // ④ 洗牌取6条
      var picked = shuffleArray(list).slice(0, 6)
      this.setData({ featuredGuides: picked })
      console.log('🌟 精选攻略加载成功:', picked.length, '/', list.length, '条有效')
    } catch (error) {
      console.log('精选攻略加载失败:', error)
      this.setData({ featuredGuides: [] })
    }
  },

  // 🔄 换一批精选攻略
  onRefreshGuides() {
    var all = this._allValidGuides || []
    if (all.length <= 6) {
      wx.showToast({ title: '暂无更多攻略', icon: 'none' })
      return
    }
    var picked = shuffleArray(all).slice(0, 6)
    this.setData({ featuredGuides: picked })
    wx.showToast({ title: '已刷新', icon: 'none', duration: 800 })
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

  // 点击精选攻略卡片 → 跳转到攻略详情页（免费查看）
  onFeaturedTap(e) {
    var item = e.currentTarget.dataset.item
    if (!item || !item.slug) return

    // 传递攻略数据给详情页
    app.globalData._guideItem = item
    wx.navigateTo({
      url: '/pages/guide-detail/guide-detail?slug=' + item.slug + '&title=' + encodeURIComponent(item.title || '攻略详情')
    })
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
