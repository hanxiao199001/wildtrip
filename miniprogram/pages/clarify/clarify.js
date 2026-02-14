// 需求澄清页面
const app = getApp()
const api = require('../../utils/api')

// 前端本地问题模板（当后端不可用时使用）
const LOCAL_QUESTIONS = {
  budget: {
    id: 'budget',
    question: '预算范围？',
    type: 'single_choice',
    required: true,
    options: [
      { value: 'budget_low', label: '穷游省钱', icon: '💰', description: '人均¥500-1500' },
      { value: 'budget_mid', label: '舒适出行', icon: '💎', description: '人均¥1500-4000' },
      { value: 'budget_high', label: '品质享受', icon: '👑', description: '人均¥4000+' }
    ]
  },
  people: {
    id: 'people',
    question: '几个人出行？',
    type: 'single_choice',
    required: true,
    options: [
      { value: 'solo', label: '一个人', icon: '🧑', description: '独自旅行' },
      { value: 'couple', label: '两人同行', icon: '👫', description: '情侣/朋友' },
      { value: 'family', label: '家庭出游', icon: '👨‍👩‍👧‍👦', description: '3-5人带小孩' },
      { value: 'group', label: '多人团体', icon: '👥', description: '5人以上' }
    ]
  },
  accommodation: {
    id: 'accommodation',
    question: '住宿偏好？',
    type: 'single_choice',
    required: false,
    options: [
      { value: 'budget_hotel', label: '经济型', icon: '🏠', description: '快捷酒店/青旅' },
      { value: 'comfort_hotel', label: '舒适型', icon: '🏨', description: '品牌连锁酒店' },
      { value: 'luxury_hotel', label: '高端型', icon: '🏰', description: '五星级/度假酒店' },
      { value: 'homestay', label: '特色民宿', icon: '🏡', description: '体验当地生活' }
    ]
  },
  travel_style: {
    id: 'travel_style',
    question: '玩法偏好？',
    type: 'single_choice',
    required: false,
    options: [
      { value: 'culture', label: '人文历史', icon: '🏛️', description: '博物馆/古迹/文化' },
      { value: 'nature', label: '自然风光', icon: '🏔️', description: '山水/海滩/户外' },
      { value: 'food_tour', label: '美食探店', icon: '🍲', description: '以吃为主的旅行' },
      { value: 'relax', label: '休闲度假', icon: '🧘', description: '不赶行程，慢慢逛' }
    ]
  }
}

// 本地查询增强映射
const ENHANCE_MAP = {
  budget_low: '预算有限，穷游省钱，人均1000左右',
  budget_mid: '预算中等，追求舒适，人均3000左右',
  budget_high: '预算充足，追求品质，人均5000以上',
  solo: '一个人出行',
  couple: '两人同行',
  family: '家庭出游（带小孩）',
  group: '多人团体出行',
  budget_hotel: '住经济型酒店',
  comfort_hotel: '住舒适型品牌连锁酒店',
  luxury_hotel: '住高端五星级酒店',
  homestay: '住特色民宿',
  culture: '偏好人文历史、博物馆、古迹',
  nature: '偏好自然风光、山水、户外',
  food_tour: '以美食探店为主',
  relax: '休闲度假为主，不赶行程'
}

Page({
  data: {
    originalQuery: '',
    questions: [],
    selectedAnswers: {},
    answeredCount: 0,
    requiredCount: 0,
    allAnswered: false,
    loading: true
  },

  onLoad(options) {
    const query = decodeURIComponent(options.query || '')
    this.setData({ originalQuery: query })

    if (query) {
      this.analyzeNeed(query)
    }
  },

  // 分析需求：先尝试后端，失败则用本地模板
  async analyzeNeed(query) {
    try {
      const result = await api.analyzeNeed(query)

      if (result.need_clarify && result.questions && result.questions.length > 0) {
        const requiredCount = result.questions.filter(q => q.required).length
        this.setData({
          questions: result.questions,
          requiredCount: requiredCount,
          loading: false
        })
        return
      }
    } catch (error) {
      console.log('后端分析不可用，使用本地模板:', error)
    }

    // 后端不可用或不需要澄清时，使用本地智能分析
    this.useLocalQuestions(query)
  },

  // 使用本地问题模板
  useLocalQuestions(query) {
    const questions = []
    const queryLower = query.toLowerCase()

    // 检测是否已有预算信息
    const hasBudget = /预算|\d{3,}[块元]|穷游|豪华|经济/.test(query)
    if (!hasBudget) {
      questions.push(LOCAL_QUESTIONS.budget)
    }

    // 检测是否已有人群信息
    const hasPeople = /亲子|情侣|一个人|独|蜜月|家庭|朋友/.test(query)
    if (!hasPeople) {
      questions.push(LOCAL_QUESTIONS.people)
    }

    // 住宿偏好
    if (questions.length < 4) {
      questions.push(LOCAL_QUESTIONS.accommodation)
    }

    // 玩法偏好
    const hasStyle = /美食|文化|自然|休闲|户外|历史|海滩/.test(query)
    if (!hasStyle && questions.length < 4) {
      questions.push(LOCAL_QUESTIONS.travel_style)
    }

    const requiredCount = questions.filter(q => q.required).length

    this.setData({
      questions: questions,
      requiredCount: requiredCount,
      loading: false
    })
  },

  // 选择选项
  onSelectOption(e) {
    const { questionId, value } = e.currentTarget.dataset
    const selectedAnswers = { ...this.data.selectedAnswers }

    if (selectedAnswers[questionId] === value) {
      delete selectedAnswers[questionId]
    } else {
      selectedAnswers[questionId] = value
    }

    const requiredQuestions = this.data.questions.filter(q => q.required)
    const answeredRequired = requiredQuestions.filter(q => selectedAnswers[q.id]).length
    const answeredCount = Object.keys(selectedAnswers).length
    const allAnswered = answeredRequired >= this.data.requiredCount

    this.setData({
      selectedAnswers,
      answeredCount,
      allAnswered
    })
  },

  // 确认生成
  async onConfirm() {
    const { originalQuery, selectedAnswers, allAnswered } = this.data

    if (!allAnswered) {
      wx.showToast({ title: '请先完成必选项', icon: 'none' })
      return
    }

    // 先尝试后端增强，失败则本地增强
    let enhancedQuery = originalQuery
    try {
      const result = await api.enhanceQuery(originalQuery, selectedAnswers)
      enhancedQuery = result.enhanced_query
    } catch (error) {
      console.log('后端增强不可用，使用本地增强')
      enhancedQuery = this.localEnhance(originalQuery, selectedAnswers)
    }

    this.goGenerate(enhancedQuery)
  },

  // 本地增强查询
  localEnhance(query, answers) {
    const parts = [query]
    for (const key in answers) {
      const desc = ENHANCE_MAP[answers[key]]
      if (desc) {
        parts.push(desc)
      }
    }
    return parts.join('，')
  },

  // 跳过，直接生成
  onSkip() {
    this.goGenerate(this.data.originalQuery)
  },

  // 跳转到生成页
  goGenerate(query) {
    wx.redirectTo({
      url: `/pages/generate/generate?query=${encodeURIComponent(query)}`
    })
  }
})
