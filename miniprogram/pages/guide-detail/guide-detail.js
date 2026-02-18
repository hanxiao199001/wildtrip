// 攻略详情页 - 完整攻略原生渲染（使用towxml）
const app = getApp()
const api = require('../../utils/api')

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
        this.setData({ loading: false, error: guide?.error || '攻略不存在' })
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
          article = towxml.toJson(markdownContent, 'markdown', {
            events: {
              tap: (e) => {
                const nodeData = e.currentTarget.dataset.data
                const href = (nodeData && nodeData.attr && nodeData.attr.href) || ''
                if (!href) return
                const isMeituanLink = href.includes('/api/relay/') || href.includes('dpurl') || href.includes('meituan')
                if (isMeituanLink) {
                  const qs = href.split('?')[1] || ''
                  const qparams = {}
                  qs.split('&').forEach(p => { const [k,v] = p.split('='); if(k) qparams[k] = decodeURIComponent(v||'') })
                  const keyword = qparams.keyword || ''
                  const city = qparams.city || ''
                  // 支持 q= 格式（直接美团搜索URL）和 keyword+city 格式（relay URL）
                  const searchText = qparams.q || (city ? `${city} ${keyword}` : keyword)
                  wx.showModal({
                    title: '跳转美团搜索',
                    content: `搜索词已复制：\n"${searchText || '未找到搜索词'}"\n\n跳转后在美团搜索框长按粘贴`,
                    confirmText: '去美团',
                    cancelText: '取消',
                    success: (res) => {
                      if (!res.confirm) return
                      if (searchText) wx.setClipboardData({ data: searchText, fail: ()=>{} })
                      wx.navigateToMiniProgram({
                        appId: 'wxde8ac0a21135c07d',
                        fail: () => {
                          wx.navigateTo({ url: `/pages/webview/webview?url=${encodeURIComponent(href)}&title=美团团购` })
                        }
                      })
                    }
                  })
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
    const content = guide?.markdown_content || guide?.title || ''
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
