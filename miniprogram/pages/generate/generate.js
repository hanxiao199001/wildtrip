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

// 🔥 前端模拟进度时间轴（秒 → 进度%）
// 总预估 90 秒，4 个阶段均匀分配
var PROGRESS_TIMELINE = [
  { time: 0,  progress: 2 },
  { time: 3,  progress: 15 },    // 分析需求完成
  { time: 5,  progress: 22 },    // 进入规划行程
  { time: 15, progress: 35 },
  { time: 25, progress: 48 },
  { time: 30, progress: 55 },    // 进入比价推荐
  { time: 40, progress: 62 },
  { time: 50, progress: 70 },
  { time: 60, progress: 78 },
  { time: 65, progress: 82 },    // 进入生成攻略
  { time: 75, progress: 88 },
  { time: 85, progress: 92 },
  { time: 95, progress: 95 },    // 最多停在95%，等后端完成
]

Page({
  data: {
    query: '',
    mode: 'full',
    taskId: '',
    progress: 0,
    stages: STAGES,
    currentStage: 0,
    currentTip: TIPS[0],
    isCompleted: false,
    isFailed: false
  },

  timer: null,
  tipTimer: null,
  progressTimer: null,
  timeoutTimer: null,  // 🔥 超时定时器
  tipIndex: 0,
  startTime: 0,

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
    this.clearAllTimers()
  },

  // 启动贴士轮播
  startTipRotation() {
    this.tipTimer = setInterval(() => {
      this.tipIndex = (this.tipIndex + 1) % TIPS.length
      this.setData({ currentTip: TIPS[this.tipIndex] })
    }, 3000)
  },

  // 🔥 前端模拟进度（平滑推进）
  startSimulatedProgress() {
    this.startTime = Date.now()
    var self = this

    this.progressTimer = setInterval(function () {
      if (self.data.isCompleted || self.data.isFailed) {
        clearInterval(self.progressTimer)
        return
      }

      var elapsed = (Date.now() - self.startTime) / 1000
      var simProgress = 0

      // 根据时间轴插值计算进度
      for (var i = 0; i < PROGRESS_TIMELINE.length - 1; i++) {
        var cur = PROGRESS_TIMELINE[i]
        var next = PROGRESS_TIMELINE[i + 1]
        if (elapsed >= cur.time && elapsed < next.time) {
          var ratio = (elapsed - cur.time) / (next.time - cur.time)
          simProgress = cur.progress + ratio * (next.progress - cur.progress)
          break
        }
      }

      // 超过最后一个节点，停在95%
      if (elapsed >= PROGRESS_TIMELINE[PROGRESS_TIMELINE.length - 1].time) {
        simProgress = 95
      }

      simProgress = Math.round(simProgress)

      // 只向前推进，不回退
      if (simProgress > self.data.progress) {
        var stage = self.getStageFromProgress(simProgress)
        self.setData({
          progress: simProgress,
          currentStage: stage
        })
      }
    }, 500)
  },

  // 根据进度计算当前阶段 (0-3)
  getStageFromProgress(progress) {
    if (progress < 20) return 0       // 分析需求
    if (progress < 55) return 1       // 规划行程
    if (progress < 80) return 2       // 比价推荐
    return 3                          // 生成攻略
  },

  // 开始生成
  async startGenerate() {
    // 🔥 先设置初始进度，让用户立刻看到进度条在动
    this.setData({ progress: 3, currentStage: 0 })

    this.startTipRotation()
    this.startSimulatedProgress()

    // 🔥 设置总超时：180秒后自动失败
    this.timeoutTimer = setTimeout(() => {
      if (!this.data.isCompleted && !this.data.isFailed) {
        console.error('生成超时')
        this.clearAllTimers()
        this.setData({ isFailed: true })
        wx.showModal({
          title: '生成超时',
          content: '攻略生成时间过长，请稍后重试',
          showCancel: false
        })
      }
    }, 180000)

    try {
      var res = await this.callAPI('/generate', {
        query: this.data.query,
        mode: this.data.mode,
        user_id: getApp().globalData.openid || ''  // 用于保存到"我的攻略"
      })

      if (res.task_id) {
        this.setData({ taskId: res.task_id })
        this.pollTaskStatus()
      } else {
        throw new Error('创建任务失败')
      }
    } catch (error) {
      console.error('生成失败:', error)
      this.clearAllTimers()
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
    var pollCount = 0
    var maxPolls = 90  // 🔥 最多轮询90次（180秒）

    this.timer = setInterval(async function () {
      pollCount++

      // 🔥 超过最大轮询次数，视为超时
      if (pollCount > maxPolls) {
        self.clearAllTimers()
        self.setData({ isFailed: true })
        wx.showModal({
          title: '生成超时',
          content: '服务器响应时间过长，请稍后重试',
          showCancel: false
        })
        return
      }

      try {
        var status = await self.callAPI('/task/' + taskId, {}, 'GET')

        // 🔥 如果后端进度比前端模拟的大，用后端的
        var backendProgress = status.progress || 0
        if (backendProgress > self.data.progress) {
          var stage = self.getStageFromProgress(backendProgress)
          self.setData({
            progress: backendProgress,
            currentStage: stage
          })
        }

        if (status.status === 'completed') {
          self.clearAllTimers()
          self.onGenerateComplete(status.result)
        } else if (status.status === 'failed') {
          self.clearAllTimers()
          self.setData({ isFailed: true })
          wx.showModal({
            title: '生成失败',
            content: status.error || '攻略生成失败，请重试',
            showCancel: false
          })
        }
      } catch (error) {
        console.error('查询状态失败:', error)
        // 🔥 连续失败时不立刻放弃，但超过5次连续失败则停止
        if (pollCount > 5 && pollCount % 5 === 0) {
          // 每5次失败提醒一次，但继续轮询
          console.warn('连续轮询失败，继续重试...')
        }
      }
    }, 2000)
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

  // 清除所有定时器
  clearAllTimers() {
    if (this.timer) clearInterval(this.timer)
    if (this.tipTimer) clearInterval(this.tipTimer)
    if (this.progressTimer) clearInterval(this.progressTimer)
    if (this.timeoutTimer) clearTimeout(this.timeoutTimer)
  },

  // 调用API
  callAPI(url, data, method) {
    data = data || {}
    method = method || 'POST'
    return new Promise(function (resolve, reject) {
      wx.request({
        url: app.globalData.apiBase + '/api' + url,
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
