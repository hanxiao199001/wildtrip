// 攻略生成页面
const app = getApp()

// 4 个 Agent 阶段定义
var STAGES = [
  { key: 'profile',      icon: '📋', label: '分析需求',   desc: '理解你的旅行偏好' },
  { key: 'wild_routing', icon: '🗺️', label: '规划行程',   desc: 'AI 生成最佳路线' },
  { key: 'pricing',      icon: '💰', label: '比价推荐',   desc: '对比平台找底价' },
  { key: 'content',      icon: '✨', label: '生成攻略',   desc: '排版输出完整攻略' }
]

// 轮播小贴士
var TIPS = [
  '野游记的推荐来自本地人真实评价',
  'AI 正在从 1000+ 条点评中筛选精华',
  '每篇攻略平均为您节省 3 小时规划时间',
  '攻略内嵌预订链接，返现高达 50%',
  '不走寻常路，就走野路子',
  '30 秒搞定，比传统攻略快 10 倍',
  '已为 10000+ 旅客生成个性化攻略'
]

Page({
  data: {
    query: '',
    mode: 'full',
    taskId: '',
    progress: 0,
    stages: STAGES,
    currentStage: 0,           // 当前阶段 0-3
    currentTip: TIPS[0],       // 当前显示的贴士
    isCompleted: false,
    isFailed: false
  },

  timer: null,        // 轮询定时器
  tipTimer: null,     // 贴士轮播定时器
  tipIndex: 0,

  onLoad(options) {
    var query = decodeURIComponent(options.query || '')
    var mode = options.mode || app.globalData._generateMode || 'full'
    app.globalData._generateMode = null

    this.setData({ query: query, mode: mode })

    if (query) {
      this.startGenerate()
    }
  },

  onUnload() {
    if (this.timer) clearInterval(this.timer)
    if (this.tipTimer) clearInterval(this.tipTimer)
  },

  // 启动贴士轮播
  startTipRotation() {
    this.tipTimer = setInterval(() => {
      this.tipIndex = (this.tipIndex + 1) % TIPS.length
      this.setData({ currentTip: TIPS[this.tipIndex] })
    }, 3000)
  },

  // 根据进度计算当前阶段 (0-3)
  getStageFromProgress(progress) {
    if (progress < 20) return 0       // Profile Agent
    if (progress < 55) return 1       // Wild-Routing Agent
    if (progress < 80) return 2       // Pricing Agent
    return 3                          // Content Agent
  },

  // 开始生成
  async startGenerate() {
    this.startTipRotation()

    try {
      var res = await this.callAPI('/generate', {
        query: this.data.query,
        mode: this.data.mode
      })

      if (res.task_id) {
        this.setData({ taskId: res.task_id })
        this.pollTaskStatus()
      } else {
        throw new Error('创建任务失败')
      }
    } catch (error) {
      console.error('生成失败:', error)
      if (this.tipTimer) clearInterval(this.tipTimer)
      this.setData({ isFailed: true })
      wx.showModal({
        title: '生成失败',
        content: error.message || '请检查网络后重试',
        showCancel: false
      })
    }
  },

  // 轮询任务状态
  pollTaskStatus() {
    var self = this
    var taskId = this.data.taskId

    this.timer = setInterval(async function () {
      try {
        var status = await self.callAPI('/task/' + taskId, {}, 'GET')
        var currentProgress = status.progress || 0
        var stage = self.getStageFromProgress(currentProgress)

        self.setData({
          progress: currentProgress,
          currentStage: stage
        })

        if (status.status === 'completed') {
          clearInterval(self.timer)
          clearInterval(self.tipTimer)
          self.onGenerateComplete(status.result)
        } else if (status.status === 'failed') {
          clearInterval(self.timer)
          clearInterval(self.tipTimer)
          self.setData({ isFailed: true })
        }
      } catch (error) {
        console.error('查询状态失败:', error)
      }
    }, 1500)
  },

  // 生成完成
  onGenerateComplete(result) {
    this.setData({
      progress: 100,
      currentStage: 4,
      isCompleted: true
    })

    setTimeout(() => {
      wx.redirectTo({
        url: '/pages/result/result?taskId=' + this.data.taskId
      })
    }, 1200)
  },

  // 调用API
  callAPI(url, data, method) {
    data = data || {}
    method = method || 'POST'
    return new Promise(function (resolve, reject) {
      wx.request({
        url: app.globalData.apiBaseUrl + url,
        method: method,
        data: data,
        header: { 'Content-Type': 'application/json' },
        success: function (res) {
          if (res.statusCode === 200) {
            resolve(res.data)
          } else {
            reject(new Error((res.data && res.data.error) || '请求失败'))
          }
        },
        fail: function () {
          reject(new Error('网络请求失败'))
        }
      })
    })
  }
})
