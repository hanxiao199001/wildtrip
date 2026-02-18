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
    shareUrl: '',  // 🔥 分享链接
    meituanMiniprogram: null,  // 🔥 美团小程序跳转参数（聚推客联盟）
    relatedGuides: [],  // 相关推荐攻略
    destination: '',  // 当前攻略目的地
    showPoster: false,  // 分享海报弹窗
    posterData: {}  // 海报数据
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
        const article = towxml.toJson(result.content || '', 'markdown', {
          events: {
            tap: (e) => {
              const nodeData = e.currentTarget.dataset.data
              const href = (nodeData && nodeData.attr && nodeData.attr.href) || ''
              if (!href) return
              wx.showToast({ title: '跳转中...', icon: 'loading', duration: 1500 })
              const isMeituanLink = href.includes('/api/relay/') || href.includes('dpurl') || href.includes('navi.sankuai')
              if (isMeituanLink) {
                // 从 relay URL 提取参数，直接构建美团搜索 URL
                const urlObj = href.split('?')[1] || ''
                const params = {}
                urlObj.split('&').forEach(p => {
                  const [k, v] = p.split('=')
                  if (k) params[k] = decodeURIComponent(v || '')
                })
                const keyword = params.keyword || ''
                const city = params.city || ''
                const poiType = params.type || 'food'
                // 城市ID映射
                const CITY_IDS = {
                  '北京':1,'上海':2,'广州':3,'深圳':4,'天津':5,
                  '杭州':6,'南京':7,'武汉':8,'西安':9,'成都':15,
                  '长沙':16,'郑州':17,'厦门':18,'福州':20,'济南':21,
                  '昆明':23,'合肥':26,'南昌':28,'南宁':29,'重庆':14,
                  '苏州':13,'宁波':54,'无锡':55,'青岛':11,'大连':12,
                  '沈阳':10,'哈尔滨':22,'长春':38,'贵阳':30,'太原':35,
                  '石家庄':70,'东莞':58,'佛山':59,'温州':57,
                  '海口':196,'三亚':252,
                }
                const cityShort = city.replace('市','').replace('区','')
                let ci = CITY_IDS[city] || CITY_IDS[cityShort] || 0
                // 模糊匹配
                if (!ci) {
                  for (const [name, id] of Object.entries(CITY_IDS)) {
                    if (cityShort.includes(name) || name.includes(cityShort)) { ci = id; break }
                  }
                }
                // 构建搜索 URL
                let searchUrl
                if (poiType === 'hotel') {
                  searchUrl = `https://i.meituan.com/hotel/search?keyword=${encodeURIComponent(keyword)}${ci ? '&ci=' + ci : ''}`
                } else {
                  searchUrl = `https://i.meituan.com/search?keyword=${encodeURIComponent(keyword)}&type=deal${ci ? '&ci=' + ci : ''}&mt_app_version=9999`
                }
                wx.navigateToMiniProgram({
                  appId: 'wxde8ac0a21135c07d',
                  path: `/index/pages/h5/h5?weburl=${encodeURIComponent(searchUrl)}`,
                  fail: () => {
                    wx.navigateTo({
                      url: `/pages/webview/webview?url=${encodeURIComponent(href)}&title=美团团购`
                    })
                  }
                })
              } else if (href.startsWith('http')) {
                wx.navigateTo({
                  url: `/pages/webview/webview?url=${encodeURIComponent(href)}&title=链接`
                })
              }
            }
          }
        })

        // 🔥 获取美团小程序跳转信息（聚推客联盟）
        const meituanMiniprogram = result.meituan_miniprogram || null

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
          ticketLinks,  // 门票链接
          meituanMiniprogram  // 🔥 美团小程序跳转参数
        })

        // 🔥 提取目的地（从content或result中）
        const destination = result.destination || this.extractDestination(result.content || '')
        this.setData({ destination })

        // 🔥 如果有slug，加载收藏状态
        if (slug) {
          this.loadFavoriteStatus()
        }

        // 加载相关推荐
        this.loadRelatedGuides(destination, slug)
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

  // 从内容中提取目的地城市
  extractDestination(content) {
    const cities = ['海口', '三亚', '成都', '重庆', '上海', '北京', '西安', '杭州',
      '厦门', '大理', '丽江', '桂林', '青岛', '南京', '长沙', '武汉',
      '广州', '深圳', '昆明', '拉萨']
    for (const city of cities) {
      if (content.includes(city)) {
        return city
      }
    }
    return ''
  },

  // 加载相关推荐
  async loadRelatedGuides(destination, slug) {
    try {
      const guides = await api.getRelatedGuides(destination || '', slug || '', 3)
      this.setData({ relatedGuides: guides || [] })
      console.log('🔗 相关推荐加载成功:', (guides || []).length, '篇')
    } catch (error) {
      console.log('相关推荐加载失败:', error)
      // 静默失败，不影响主流程
    }
  },

  // 点击相关推荐卡片
  onRelatedTap(e) {
    const item = e.currentTarget.dataset.item

    // 如果是预设攻略（有query字段），跳转到首页并填充
    if (item.query) {
      wx.switchTab({
        url: '/pages/index/index'
      })
      // 通过全局变量传递查询
      app.globalData._pendingQuery = item.query
      return
    }

    // 如果是真实攻略，跳转到攻略详情页
    if (item.slug && !item.slug.startsWith('_preset')) {
      app.globalData._guideItem = item
      wx.navigateTo({
        url: '/pages/guide-detail/guide-detail'
      })
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

  // 显示分享海报
  showSharePoster() {
    const { content, destination, taskId } = this.data

    // 🔥 优化：从多个来源提取信息

    // 1. 提取标题（优先从HTML <h1>，其次从Markdown标题）
    let title = '我的旅行攻略'
    const h1Match = content.match(/<h1[^>]*>([^<]+)<\/h1>/)
    if (h1Match) {
      title = h1Match[1].replace(/【.*?】|#/g, '').trim().substring(0, 30)
    } else {
      const titleMatch = content.match(/^#+\s*(.+)/m)
      if (titleMatch) {
        title = titleMatch[1].replace(/[🔥🌴✈️🏨🍜💰📋🗓️⚠️💡🎒]/g, '').trim().substring(0, 30)
      }
    }

    // 2. 提取天数（多种模式匹配 + 过滤异常值）
    let days = 0
    const daysPatterns = [
      /(\d+)天\d*晚/,           // "3天2晚" 最精确
      /(\d+)\s*天深度/,          // "3天深度游"
      /行程[：:]\s*(\d+)天/,     // "行程：3天"
      /天数[：:]\s*(\d+)/,       // "天数：3"
      /(\d+)\s*天/               // 通用但可能误匹配
    ]
    for (const pattern of daysPatterns) {
      const match = content.match(pattern)
      if (match) {
        const d = parseInt(match[1])
        if (d > 0 && d <= 30) {  // 过滤异常值（超过30天不合理）
          days = d
          break
        }
      }
    }

    // 3. 提取目的地（如果页面没有从API获取到）
    let dest = destination || ''
    if (!dest) {
      const destPatterns = [
        /目的地[：:]\s*([^\n<]+)/,
        /📍\s*([^\n<]+)/,
        /(北京|上海|广州|深圳|成都|重庆|杭州|西安|三亚|海口|厦门|苏州|南京|武汉|长沙|青岛|大连|昆明|桂林|丽江|大理|哈尔滨|拉萨|太原|沈阳)/
      ]
      for (const pattern of destPatterns) {
        const match = content.match(pattern)
        if (match) {
          dest = match[1].trim()
          break
        }
      }
    }

    // 4. 提取预算（多种格式）
    let budget = ''
    const budgetPatterns = [
      /预算[：:]\s*[¥￥]?(\d+[-~～]?\d*)/,
      /人均[：:]\s*[¥￥]?(\d+[-~～]?\d*)/,
      /[¥￥](\d{3,5})[-~～/]?/
    ]
    for (const pattern of budgetPatterns) {
      const match = content.match(pattern)
      if (match) {
        budget = match[1]
        break
      }
    }

    this.setData({
      showPoster: true,
      posterData: {
        id: taskId || 'demo',
        title: title,
        destination: dest,
        days: days || 3,
        budget: budget,
        userName: wx.getStorageSync('userInfo')?.nickName || '野游记用户',
        createdAt: new Date().toLocaleDateString('zh-CN')
      }
    })
  },

  // 关闭海报
  onClosePoster() {
    this.setData({ showPoster: false })
  },

  // 分享（微信转发）
  onShare() {
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    })
  },

  onShareAppMessage() {
    return {
      title: '我用野游记生成了旅游攻略，预订立省50%！',
      path: '/pages/index/index'
    }
  },

  onShareTimeline() {
    return {
      title: '野游记 - AI旅游助手，预订立省50%'
    }
  },

  // 🔥 跳转美团小程序（聚推客联盟 CPS）
  onJumpMeituan(e) {
    const { meituanMiniprogram } = this.data
    const linkName = e.currentTarget.dataset.name || '美团'

    // 优先使用小程序跳转（带返佣追踪）
    if (meituanMiniprogram && meituanMiniprogram.enabled && meituanMiniprogram.page_path) {
      wx.navigateToMiniProgram({
        appId: meituanMiniprogram.app_id,
        path: meituanMiniprogram.page_path,
        success: () => {
          console.log('跳转美团小程序成功:', linkName)
        },
        fail: (err) => {
          console.error('跳转美团小程序失败:', err)
          // 失败时尝试 H5 备用链接
          this.openH5Fallback(e)
        }
      })
    } else {
      // 聚推客未配置，用 H5 链接
      this.openH5Fallback(e)
    }
  },

  // H5 备用打开方式
  openH5Fallback(e) {
    const url = e.currentTarget.dataset.url || ''
    const name = e.currentTarget.dataset.name || '美团'
    if (url) {
      wx.navigateTo({
        url: `/pages/webview/webview?url=${encodeURIComponent(url)}&title=${encodeURIComponent(name)}`
      })
    } else {
      wx.showToast({
        title: '链接暂不可用',
        icon: 'none'
      })
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
