// 攻略结果页面
const app = getApp()
const api = require('../../utils/api')

Page({
  data: {
    taskId: '',
    slug: '',  // 🔥 攻略slug（用于收藏、分享等）
    loading: true,
    error: '',
    content: '',
    article: {},  // 🔥 towxml渲染后的数据
    result: null,
    stats: {
      hotels_count: 0,
      restaurants_count: 0,
      tickets_count: 0
    },
    estimatedCashback: 0,
    links: [],  // 🔥 所有可点击链接
    hotelLinks: [],  // 酒店链接
    restaurantLinks: [],  // 餐厅链接
    ticketLinks: [],  // 门票链接
    isFavorited: false,  // 🔥 是否已收藏
    shareUrl: ''  // 🔥 分享链接
  },

  onLoad(options) {
    const taskId = options.taskId || ''
    this.setData({ taskId })
    
    if (taskId) {
      this.loadResult()
    } else {
      this.setData({
        loading: false,
        error: '任务ID不存在'
      })
    }
  },

  // 加载结果
  async loadResult() {
    const { taskId } = this.data

    try {
      const res = await this.callAPI(`/task/${taskId}`, {}, 'GET')

      if (res.status === 'completed' && res.result) {
        const result = res.result
        
        // 计算预估返现
        const cashback = this.calculateCashback(result.stats || {})

        // 🔥 处理链接数据，分类
        const links = result.links || []
        const hotelLinks = links.filter(link => link.type === 'hotel')
        const restaurantLinks = links.filter(link => link.type === 'restaurant')
        const ticketLinks = links.filter(link => link.type === 'ticket')

        // 🔥 获取slug（从result中）
        const slug = result.slug || ''
        
        // 🔥 使用towxml渲染Markdown（支持图片）
        const towxml = app.globalData.towxml
        const article = towxml.toJson(result.content || '', 'markdown')

        this.setData({
          loading: false,
          result,
          slug,  // 🔥 保存slug
          content: result.content || '',
          article,  // 🔥 渲染后的数据
          stats: result.stats || {},
          estimatedCashback: cashback,
          links,  // 🔥 所有链接
          hotelLinks,  // 酒店链接
          restaurantLinks,  // 餐厅链接
          ticketLinks  // 门票链接
        })

        // 🔥 如果有slug，加载收藏状态
        if (slug) {
          this.loadFavoriteStatus()
        }
      } else if (res.status === 'failed') {
        this.setData({
          loading: false,
          error: res.error || '生成失败'
        })
      } else {
        // 还在生成中，继续等待
        setTimeout(() => {
          this.loadResult()
        }, 2000)
      }
    } catch (error) {
      console.error('加载结果失败:', error)
      this.setData({
        loading: false,
        error: error.message || '加载失败'
      })
    }
  },

  // 计算预估返现（优化版）
  calculateCashback(stats) {
    // 更准确的计算：基于典型消费金额 × 返佣率 × 50%返现
    
    // 酒店：假设¥300/晚，返佣5%=¥15，返现50%=¥7.5
    // 但推荐多家，按平均每家¥12计算（考虑用户可能选便宜的）
    const hotelCashback = (stats.hotels_count || 0) * 12
    
    // 餐厅：假设¥80/顿，返佣8%=¥6.4，返现50%=¥3.2
    // 按每家¥8计算（考虑可能多次消费）
    const foodCashback = (stats.restaurants_count || 0) * 8
    
    // 景点：假设¥60/张，返佣10%=¥6，返现50%=¥3
    // 按每个¥5计算
    const ticketCashback = (stats.tickets_count || 0) * 5
    
    const total = hotelCashback + foodCashback + ticketCashback
    
    // 返回整数（向上取整，给用户更好的预期）
    return Math.ceil(total)
  },

  // 🔥 加载收藏状态
  async loadFavoriteStatus() {
    const { slug } = this.data
    if (!slug) return

    try {
      const detail = await api.getGuideDetail(slug)
      this.setData({
        isFavorited: detail.is_favorited || false
      })
    } catch (error) {
      console.log('加载收藏状态失败:', error)
    }
  },

  // 🔥 切换收藏
  async onToggleFavorite() {
    const { slug, isFavorited } = this.data
    if (!slug) {
      wx.showToast({
        title: '攻略未保存',
        icon: 'none'
      })
      return
    }

    try {
      if (isFavorited) {
        await api.unfavoriteGuide(slug)
        this.setData({ isFavorited: false })
        wx.showToast({
          title: '已取消收藏',
          icon: 'success'
        })
      } else {
        await api.favoriteGuide(slug)
        this.setData({ isFavorited: true })
        wx.showToast({
          title: '收藏成功',
          icon: 'success'
        })
      }
    } catch (error) {
      wx.showToast({
        title: error.message || '操作失败',
        icon: 'none'
      })
    }
  },

  // 🔥 生成分享链接
  async onGenerateShareLink() {
    const { slug, shareUrl } = this.data
    
    if (!slug) {
      wx.showToast({
        title: '攻略未保存',
        icon: 'none'
      })
      return
    }

    // 如果已生成，直接复制
    if (shareUrl) {
      wx.setClipboardData({
        data: shareUrl,
        success: () => {
          wx.showToast({
            title: '链接已复制',
            icon: 'success'
          })
        }
      })
      return
    }

    try {
      wx.showLoading({ title: '生成中...' })
      const result = await api.shareGuide(slug)
      const url = result.share_url
      
      this.setData({ shareUrl: url })
      
      wx.hideLoading()
      wx.setClipboardData({
        data: url,
        success: () => {
          wx.showToast({
            title: '链接已复制',
            icon: 'success'
          })
        }
      })
    } catch (error) {
      wx.hideLoading()
      wx.showToast({
        title: error.message || '生成失败',
        icon: 'none'
      })
    }
  },

  // 🔥 删除攻略
  onDelete() {
    const { slug } = this.data
    
    if (!slug) {
      wx.showToast({
        title: '攻略未保存',
        icon: 'none'
      })
      return
    }

    wx.showModal({
      title: '确认删除',
      content: '删除后无法恢复，确定要删除这篇攻略吗？',
      confirmText: '删除',
      confirmColor: '#FF3B30',
      success: async (res) => {
        if (res.confirm) {
          try {
            wx.showLoading({ title: '删除中...' })
            await api.deleteGuide(slug)
            wx.hideLoading()
            wx.showToast({
              title: '已删除',
              icon: 'success',
              duration: 1500
            })
            // 返回上一页
            setTimeout(() => {
              wx.navigateBack()
            }, 1500)
          } catch (error) {
            wx.hideLoading()
            wx.showToast({
              title: error.message || '删除失败',
              icon: 'none'
            })
          }
        }
      }
    })
  },

  // 复制攻略
  onCopy() {
    const { content } = this.data
    
    wx.setClipboardData({
      data: content,
      success: () => {
        wx.showToast({
          title: '复制成功',
          icon: 'success'
        })
      }
    })
  },

  // 分享
  onShare() {
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    })
  },

  onShareAppMessage() {
    return {
      title: '我用野游记生成了旅游攻略，预订还能返现50%！',
      path: '/pages/index/index'
    }
  },

  onShareTimeline() {
    return {
      title: '野游记 - 懒人旅游AI，预订返现50%'
    }
  },

  // 重试
  onRetry() {
    wx.navigateBack()
  },

  // 调用API
  async callAPI(url, data = {}, method = 'POST') {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${app.globalData.apiBaseUrl}${url}`,
        method,
        data,
        header: {
          'Content-Type': 'application/json'
        },
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.data)
          } else {
            reject(new Error(res.data.error || '请求失败'))
          }
        },
        fail: (err) => {
          reject(new Error('网络请求失败'))
        }
      })
    })
  }
})
