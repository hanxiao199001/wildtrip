// 野游记首页
const app = getApp()
const api = require('../../utils/api')

Page({
  data: {
    query: '',
    isGenerating: false,
    featuredGuides: []  // 精选攻略
  },

  onLoad() {
    console.log('🏠 首页加载')
    this.loadFeaturedGuides()
  },

  onShow() {
    // 每次显示页面时刷新精选（可能有新攻略生成）
    this.loadFeaturedGuides()
  },

  // 加载精选攻略
  async loadFeaturedGuides() {
    try {
      const guides = await api.getFeaturedGuides(6)
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
            cover_image: 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=800&h=600&fit=crop',
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
            cover_image: 'https://images.unsplash.com/photo-1590559899731-a382839e5549?w=800&h=600&fit=crop',
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
            cover_image: 'https://images.unsplash.com/photo-1537531383496-f4749b67fd74?w=800&h=600&fit=crop',
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
            cover_image: 'https://images.unsplash.com/photo-1603366445787-09714680cbf1?w=800&h=600&fit=crop',
            views: 932,
            likes: 85,
            query: '西安4天穷游，预算800'
          }
        ]
      })
    }
  },

  // 输入变化
  onQueryInput(e) {
    this.setData({
      query: e.detail.value
    })
  },

  // 点击精选攻略卡片
  onFeaturedTap(e) {
    const item = e.currentTarget.dataset.item

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

    // 如果是真实攻略（有slug且非预设），跳转到详情
    if (item.slug && !item.slug.startsWith('_preset') && !item.slug.startsWith('_fallback')) {
      wx.navigateTo({
        url: `/pages/webview/webview?url=${encodeURIComponent(item.url)}&title=${encodeURIComponent(item.title)}`
      })
    }
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

    // 跳转到需求澄清页（澄清后自动跳转生成页）
    wx.navigateTo({
      url: `/pages/clarify/clarify?query=${encodeURIComponent(query)}`
    })
  },

  // 查看返现说明
  onCashbackInfo() {
    wx.switchTab({
      url: '/pages/cashback/cashback'
    })
  }
})
