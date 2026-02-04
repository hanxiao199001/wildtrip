// 攻略结果页面
const app = getApp()

Page({
  data: {
    taskId: '',
    loading: true,
    error: '',
    content: '',
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
    ticketLinks: []  // 门票链接
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

        this.setData({
          loading: false,
          result,
          content: result.content || '',
          stats: result.stats || {},
          estimatedCashback: cashback,
          links,  // 🔥 所有链接
          hotelLinks,  // 酒店链接
          restaurantLinks,  // 餐厅链接
          ticketLinks  // 门票链接
        })
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

  // 计算预估返现
  calculateCashback(stats) {
    // 简化计算：每家酒店¥15，每家餐厅¥5，每个景点¥10
    const hotelCashback = (stats.hotels_count || 0) * 15
    const foodCashback = (stats.restaurants_count || 0) * 5
    const ticketCashback = (stats.tickets_count || 0) * 10
    
    return hotelCashback + foodCashback + ticketCashback
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
