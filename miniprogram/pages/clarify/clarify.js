// 需求澄清页面
const app = getApp()
const api = require('../../utils/api')

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

  // 调用后端分析需求
  async analyzeNeed(query) {
    try {
      const result = await api.analyzeNeed(query)

      if (!result.need_clarify || !result.questions || result.questions.length === 0) {
        // 不需要澄清，直接跳转生成
        this.goGenerate(query)
        return
      }

      // 计算必填问题数量
      const requiredCount = result.questions.filter(q => q.required).length

      this.setData({
        questions: result.questions,
        requiredCount: requiredCount,
        loading: false
      })
    } catch (error) {
      console.error('需求分析失败:', error)
      // 分析失败，直接跳转生成
      this.goGenerate(query)
    }
  },

  // 选择选项
  onSelectOption(e) {
    const { questionId, value } = e.currentTarget.dataset
    const selectedAnswers = { ...this.data.selectedAnswers }

    // 如果点击已选中的选项，取消选中
    if (selectedAnswers[questionId] === value) {
      delete selectedAnswers[questionId]
    } else {
      selectedAnswers[questionId] = value
    }

    // 计算已回答的必填问题数
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

  // 确认，带答案生成
  async onConfirm() {
    const { originalQuery, selectedAnswers, allAnswered } = this.data

    if (!allAnswered) {
      wx.showToast({
        title: '请先完成必选项',
        icon: 'none'
      })
      return
    }

    wx.showLoading({ title: '正在优化需求...' })

    try {
      // 调用后端增强查询
      const result = await api.enhanceQuery(originalQuery, selectedAnswers)
      wx.hideLoading()

      // 跳转到生成页
      this.goGenerate(result.enhanced_query)
    } catch (error) {
      wx.hideLoading()
      console.error('查询增强失败:', error)
      // 失败时用原始查询
      this.goGenerate(originalQuery)
    }
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
