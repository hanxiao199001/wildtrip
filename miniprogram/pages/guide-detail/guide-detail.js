// 攻略详情页 - 完整攻略原生渲染（使用towxml）
const app = getApp()
const api = require('../../utils/api')

// 美团城市ID映射（ci参数，用于精准定位城市）
const MEITUAN_CITY_IDS = {
  '北京': 1, '上海': 2, '广州': 3, '深圳': 4, '天津': 5,
  '杭州': 6, '南京': 7, '武汉': 8, '西安': 9, '沈阳': 10,
  '青岛': 11, '大连': 12, '苏州': 13, '重庆': 14, '成都': 15,
  '长沙': 16, '郑州': 17, '厦门': 18, '福州': 20, '济南': 21,
  '哈尔滨': 22, '昆明': 23, '合肥': 26, '南昌': 28, '南宁': 29,
  '贵阳': 30, '太原': 35, '兰州': 37, '长春': 38, '乌鲁木齐': 40,
  '宁波': 54, '无锡': 55, '温州': 57, '东莞': 58, '佛山': 59,
  '石家庄': 70, '呼和浩特': 80, '银川': 93, '西宁': 108,
  '海口': 196, '三亚': 252,
  '黄州': 8,  // 黄州属于湖北黄冈，近武汉，共用武汉ID
}

// 获取美团城市ID（支持模糊匹配）
function getMeituanCityId(city) {
  if (!city) return 0
  // 精确匹配
  if (MEITUAN_CITY_IDS[city]) return MEITUAN_CITY_IDS[city]
  // 模糊匹配（去掉"市"/"区"）
  const cityShort = city.replace(/[市区]/g, '')
  for (const name in MEITUAN_CITY_IDS) {
    if (cityShort.includes(name) || name.includes(cityShort)) {
      return MEITUAN_CITY_IDS[name]
    }
  }
  return 0
}

// 解析relay URL参数
function parseRelayUrl(url) {
  const params = {}
  const qs = url.split('?')[1] || ''
  qs.split('&').forEach(p => {
    const [k, v] = p.split('=')
    if (k) params[k] = decodeURIComponent(v || '')
  })
  return params
}

// 构建美团最终搜索URL
function buildMeituanSearchUrl(keyword, city, type = 'food') {
  const cityId = getMeituanCityId(city)
  const encodedKeyword = encodeURIComponent(keyword || '团购')
  
  const templates = {
    'food': 'https://i.meituan.com/search?keyword={keyword}&type=deal&ci={ci}&mt_app_version=9999',
    'hotel': 'https://i.meituan.com/hotel/search?keyword={keyword}&ci={ci}',
    'ticket': 'https://i.meituan.com/search?keyword={keyword}%20门票&type=deal&ci={ci}',
  }
  
  const template = templates[type] || templates['food']
  
  if (cityId) {
    return template.replace('{keyword}', encodedKeyword).replace('{ci}', cityId)
  } else {
    // 没有城市ID时，关键词拼接城市名
    const fallbackKeyword = city ? `${city} ${keyword}`.trim() : keyword
    return template
      .replace('{keyword}', encodeURIComponent(fallbackKeyword))
      .replace('&ci={ci}', '')
  }
}

// 城市渐变色映射
const CITY_GRADIENTS = {
  '深圳': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  '上海': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  '北京': 'linear-gradient(135deg, #E44D26 0%, #F16529 100%)',
  '成都': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
  '重庆': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  '杭州': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  '西安': 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)',
  '海口': 'linear-gradient(135deg, #0093E9 0%, #80D0C7 100%)',
  '三亚': 'linear-gradient(135deg, #0093E9 0%, #80D0C7 100%)',
  '厦门': 'linear-gradient(135deg, #FBAB7E 0%, #F7CE68 100%)',
  '广州': 'linear-gradient(135deg, #FFE985 0%, #FA742B 100%)',
  '长沙': 'linear-gradient(135deg, #FA8BFF 0%, #2BD2FF 50%, #2BFF88 100%)',
  '大理': 'linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%)',
  '南京': 'linear-gradient(135deg, #c471f5 0%, #fa71cd 100%)',
  '昆明': 'linear-gradient(135deg, #f5576c 0%, #ff6f91 100%)',
}
const DEFAULT_GRADIENT = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'

// 🔥 从HTML中提取可读的Markdown内容（独立函数，避免async中this丢失）
function extractMarkdownFromHtml(html, title) {
  if (!html) return ''

  const mdParts = []

  // 添加标题
  if (title) {
    mdParts.push('# ' + title + '\n')
  }

  // 方法1: 提取 day-section 块中的结构化内容
  const daySectionRegex = /class="[^"]*day-section[^"]*"[\s\S]*?(?=class="[^"]*day-section|<\/main|<footer|$)/gi
  const daySections = html.match(daySectionRegex)

  if (daySections && daySections.length > 0) {
    for (let s = 0; s < daySections.length; s++) {
      const section = daySections[s]
      // 提取Day编号
      const dayMatch = section.match(/Day\s*(\d+)/i)
      // 提取副标题
      const subtitleMatch = section.match(/day-subtitle[^>]*>([\s\S]*?)<\//i)

      if (dayMatch) {
        const dayNum = dayMatch[1]
        let subtitle = ''
        if (subtitleMatch) {
          subtitle = subtitleMatch[1].replace(/<[^>]+>/g, '').trim()
        }
        mdParts.push('\n## Day ' + dayNum + ' ' + subtitle + '\n')
      }

      // 提取时间点、活动名、活动描述
      const timePoints = []
      const tpRegex = /time-point[^>]*>([\s\S]*?)<\//gi
      let tpMatch
      while ((tpMatch = tpRegex.exec(section)) !== null) {
        timePoints.push(tpMatch[1].replace(/<[^>]+>/g, '').trim())
      }

      const actTitles = []
      const atRegex = /activity-title[^>]*>([\s\S]*?)<\//gi
      let atMatch
      while ((atMatch = atRegex.exec(section)) !== null) {
        actTitles.push(atMatch[1].replace(/<[^>]+>/g, '').trim())
      }

      const actDescs = []
      const adRegex = /activity-desc[^>]*>([\s\S]*?)<\//gi
      let adMatch
      while ((adMatch = adRegex.exec(section)) !== null) {
        actDescs.push(adMatch[1].replace(/<[^>]+>/g, '').trim())
      }

      const maxLen = Math.max(timePoints.length, actTitles.length)
      for (let i = 0; i < maxLen; i++) {
        const tp = timePoints[i] || ''
        const at = actTitles[i] || ''
        const ad = actDescs[i] || ''
        if (tp || at) {
          const line = tp ? ('**' + tp + '** ' + at) : ('**' + at + '**')
          mdParts.push(line)
          if (ad) {
            mdParts.push('> ' + ad + '\n')
          }
        }
      }
    }

    if (mdParts.length > 1) {
      return mdParts.join('\n')
    }
  }

  // 方法2: 提取 timeline-item 块
  const timelineRegex = /class="timeline-item"[\s\S]*?<\/div>\s*<\/div>\s*<\/div>/gi
  const timelineItems = html.match(timelineRegex)

  if (timelineItems && timelineItems.length > 0) {
    for (let t = 0; t < timelineItems.length; t++) {
      const item = timelineItems[t]
      const tp = (item.match(/time-point[^>]*>([\s\S]*?)<\//) || [])[1]
      const at = (item.match(/activity-title[^>]*>([\s\S]*?)<\//) || [])[1]
      const ad = (item.match(/activity-desc[^>]*>([\s\S]*?)<\//) || [])[1]

      const timeText = tp ? tp.replace(/<[^>]+>/g, '').trim() : ''
      const titleText = at ? at.replace(/<[^>]+>/g, '').trim() : ''
      const descText = ad ? ad.replace(/<[^>]+>/g, '').trim() : ''

      if (timeText || titleText) {
        mdParts.push(timeText ? ('**' + timeText + '** ' + titleText) : ('**' + titleText + '**'))
        if (descText) {
          mdParts.push('> ' + descText + '\n')
        }
      }
    }

    if (mdParts.length > 1) {
      return mdParts.join('\n')
    }
  }

  // 方法3: 最终回退 - 去除HTML标签，保留纯文本
  var text = html
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<head[\s\S]*?<\/head>/gi, '')
    .replace(/<nav[\s\S]*?<\/nav>/gi, '')
    .replace(/<footer[\s\S]*?<\/footer>/gi, '')
    .replace(/<[^>]+>/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim()

  // 截取合理长度
  if (text.length > 5000) {
    text = text.substring(0, 5000) + '\n\n...'
  }

  return text || ''
}

Page({
  data: {
    slug: '',
    loading: true,
    error: '',
    guide: null,           // API返回的攻略数据
    article: null,         // towxml渲染后的数据
    coverGradient: DEFAULT_GRADIENT,
    highlights: [],        // 从内容提取的亮点
    wordCountDisplay: '0',
    _coverFailed: false,
    showContent: false     // 是否展示完整内容
  },

  onLoad(options) {
    // 优先从全局变量获取攻略数据
    const guideItem = app.globalData._guideItem || {}
    app.globalData._guideItem = null

    const slug = guideItem.slug || decodeURIComponent(options.slug || '')
    const title = guideItem.title || decodeURIComponent(options.title || '攻略详情')

    console.log('📖 攻略详情页加载, slug:', slug)
    wx.setNavigationBarTitle({ title: title })

    // 选择城市对应渐变色
    const city = guideItem.destination || ''
    const coverGradient = CITY_GRADIENTS[city] || DEFAULT_GRADIENT

    this.setData({ slug, coverGradient })

    if (slug) {
      this.loadGuideDetail()
    } else {
      this.setData({ loading: false, error: '攻略ID不存在' })
    }
  },

  // 加载攻略详情 + 渲染内容
  async loadGuideDetail() {
    const { slug } = this.data
    try {
      const guide = await api.getGuideDetail(slug)
      if (!guide || guide.error) {
        this.setData({ loading: false, error: (guide && guide.error) || '攻略不存在' })
        return
      }

      if (guide.title) {
        wx.setNavigationBarTitle({ title: guide.title })
      }

      // 城市渐变色
      const city = guide.destination || ''
      const coverGradient = CITY_GRADIENTS[city] || DEFAULT_GRADIENT

      // 从HTML内容提取亮点（Day标题）
      const highlights = this._extractHighlights(guide.content || '')

      // 格式化字数显示
      const wc = guide.word_count || 0
      const wordCountDisplay = wc > 1000 ? (wc / 1000).toFixed(1) + 'k' : String(wc)

      // 🔥 使用towxml渲染内容
      let article = null
      const towxml = app.globalData.towxml

      // 优先使用后端返回的Markdown内容
      let markdownContent = guide.markdown_content || ''

      // 🔥 客户端回退：如果没有markdown_content，从HTML中提取可读内容
      if (!markdownContent && guide.content) {
        markdownContent = extractMarkdownFromHtml(guide.content, guide.title)
        console.log('📖 从HTML提取Markdown内容, 长度:', markdownContent.length)
      }

      if (markdownContent && towxml) {
        try {
          // 🔥 towxml 链接点击处理（通过 option.events 传入，toJson 内部会注册到 global._events）
          article = towxml.toJson(markdownContent, 'markdown', {
            events: {
              tap: (e) => {
                const nodeData = e.currentTarget.dataset.data
                const href = (nodeData && nodeData.attr && nodeData.attr.href) || ''
                if (!href) return
                console.log('🔥 链接被点击了!', '链接地址:', href)
                const isMeituanLink = href.includes('/api/relay/') || href.includes('dpurl') || href.includes('meituan') || href.includes('navi.sankuai')
                if (isMeituanLink) {
                  // 🔥 优化版：Toast提示 + 自动跳转
                  let finalSearchUrl = ''
                  let searchText = ''
                  
                  // 判断是relay URL还是直接美团URL
                  if (href.includes('/api/relay/meituan')) {
                    // relay URL → 解析参数构建最终搜索URL
                    const params = parseRelayUrl(href)
                    const keyword = params.keyword || ''
                    const city = params.city || (this.data.guide && this.data.guide.destination) || ''
                    const type = params.type || 'food'
                    finalSearchUrl = buildMeituanSearchUrl(keyword, city, type)
                    searchText = city ? `${city} ${keyword}` : keyword
                    
                    // 🔥 后台静默触发CPS追踪（设置返佣cookie）
                    wx.request({
                      url: href + (href.includes('?') ? '&' : '?') + 'direct=1',
                      method: 'GET',
                      header: { 'Content-Type': 'application/json' },
                      success: () => console.log('✅ CPS追踪已触发'),
                      fail: (err) => console.warn('⚠️ CPS追踪失败（不影响跳转）:', err)
                    })
                  } else {
                    // 直接美团URL，不处理
                    finalSearchUrl = href
                  }
                  
                  console.log('🔍 构建的美团URL:', finalSearchUrl)
                  console.log('🔍 搜索词:', searchText)
                  
                  // Toast提示 + 自动跳转
                  if (searchText) {
                    wx.setClipboardData({ 
                      data: searchText,
                      success: () => {
                        wx.showToast({
                          title: `已复制: ${searchText}\n\n① 即将跳转美团\n② 搜索框长按粘贴`,
                          icon: 'none',
                          duration: 2000
                        })
                        setTimeout(() => {
                          wx.navigateToMiniProgram({
                            appId: 'wxde8ac0a21135c07d',
                            fail: () => {
                              wx.navigateTo({ url: `/pages/webview/webview?url=${encodeURIComponent(finalSearchUrl)}&title=美团团购` })
                            }
                          })
                        }, 1500)
                      },
                      fail: () => {
                        // 复制失败则直接跳转
                        wx.navigateToMiniProgram({
                          appId: 'wxde8ac0a21135c07d',
                          fail: () => {
                            wx.navigateTo({ url: `/pages/webview/webview?url=${encodeURIComponent(finalSearchUrl)}&title=美团团购` })
                          }
                        })
                      }
                    })
                  } else {
                    // 没有搜索词则直接跳转
                    wx.navigateToMiniProgram({
                      appId: 'wxde8ac0a21135c07d',
                      fail: () => {
                        wx.navigateTo({ url: `/pages/webview/webview?url=${encodeURIComponent(finalSearchUrl)}&title=美团团购` })
                      }
                    })
                  }
                } else if (href.startsWith('http')) {
                  wx.navigateTo({ url: `/pages/webview/webview?url=${encodeURIComponent(href)}&title=链接` })
                }
              }
            }
          })
          console.log('📖 内容渲染成功')
        } catch (e) {
          console.error('towxml渲染失败:', e)
        }
      }

      this.setData({
        loading: false,
        guide,
        article,
        coverGradient,
        highlights,
        wordCountDisplay,
        showContent: !!article  // 如果有渲染内容则直接展示
      })

      console.log('📖 攻略详情加载成功:', slug, article ? '(含内容渲染)' : '(仅预览)')
    } catch (error) {
      console.error('加载攻略详情失败:', error)
      this.setData({ loading: false, error: error.message || '加载失败' })
    }
  },

  // 从HTML内容提取每天的亮点标题
  _extractHighlights(content) {
    const highlights = []

    // 提取 Day 标题和副标题
    const dayRegex = /Day\s*(\d+)[\s\S]*?<div class="day-subtitle">(.*?)<\/div>/gi
    let match
    while ((match = dayRegex.exec(content)) !== null) {
      highlights.push({
        day: match[1],
        text: match[2].replace(/<[^>]+>/g, '').trim()
      })
    }

    // 如果没匹配到，尝试简单的Day提取
    if (highlights.length === 0) {
      const simpleRegex = /Day\s*(\d+)[^<\n]*(.*?)(?:<|$)/gi
      while ((match = simpleRegex.exec(content)) !== null) {
        const text = match[2].replace(/<[^>]+>/g, '').trim()
        if (text) {
          highlights.push({ day: match[1], text })
        }
      }
    }

    return highlights.slice(0, 7)  // 最多7天
  },

  // 🔥 展开/收起完整攻略
  onToggleContent() {
    this.setData({ showContent: !this.data.showContent })
  },

  // 切换收藏
  async onToggleFavorite() {
    const { slug, guide } = this.data
    if (!slug || !guide) return
    try {
      if (guide.is_favorited) {
        await api.unfavoriteGuide(slug)
        guide.is_favorited = false
        wx.showToast({ title: '已取消收藏', icon: 'success' })
      } else {
        await api.favoriteGuide(slug)
        guide.is_favorited = true
        wx.showToast({ title: '收藏成功', icon: 'success' })
      }
      this.setData({ guide })
    } catch (error) {
      wx.showToast({ title: error.message || '操作失败', icon: 'none' })
    }
  },

  // 复制攻略文本
  onCopy() {
    const { guide } = this.data
    const content = (guide && guide.markdown_content) || (guide && guide.title) || ''
    if (!content) {
      wx.showToast({ title: '暂无内容', icon: 'none' })
      return
    }
    wx.setClipboardData({
      data: content,
      success: () => {
        wx.showToast({ title: '复制成功', icon: 'success' })
      }
    })
  },

  // 分享
  onShareAppMessage() {
    const { guide } = this.data
    return {
      title: guide ? `${guide.title} - 野游记攻略` : '野游记 - AI旅游助手',
      path: '/pages/index/index'
    }
  },

  onShareTimeline() {
    const { guide } = this.data
    return { title: guide ? guide.title : '野游记 - AI旅游助手' }
  },

  // 生成同款攻略
  onGenerateSimilar() {
    const { guide } = this.data
    if (!guide) return
    let query = guide.title || ''
    if (guide.destination && guide.days) {
      query = `${guide.destination}${guide.days}天`
      if (guide.category && guide.category !== '自由行') query += guide.category
      if (guide.budget) query += `，预算${guide.budget}`
    }
    app.globalData._pendingQuery = query
    wx.switchTab({ url: '/pages/index/index' })
  },

  // 封面图加载失败
  onCoverError() {
    this.setData({ _coverFailed: true })
  },

  // 重试
  onRetry() {
    this.setData({ loading: true, error: '' })
    this.loadGuideDetail()
  }
})
