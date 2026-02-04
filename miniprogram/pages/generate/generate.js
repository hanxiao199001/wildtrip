// 攻略生成页面
const app = getApp()

Page({
  data: {
    query: '',
    taskId: '',
    progress: 0,
    statusText: '正在生成攻略...',
    statusIcon: '⏳',
    messages: [],
    isCompleted: false
  },

  timer: null,

  onLoad(options) {
    const query = decodeURIComponent(options.query || '')
    this.setData({ query })
    
    if (query) {
      this.startGenerate()
    }
  },

  onUnload() {
    if (this.timer) {
      clearInterval(this.timer)
    }
  },

  // 开始生成
  async startGenerate() {
    const { query } = this.data

    this.addMessage('🔥 野游记开始工作...')
    
    try {
      // 调用后端API
      const res = await this.callAPI('/generate', {
        query,
        mode: 'full'
      })

      if (res.task_id) {
        this.setData({ taskId: res.task_id })
        this.addMessage('✅ 任务创建成功')
        
        // 开始轮询状态
        this.pollTaskStatus()
      } else {
        throw new Error('创建任务失败')
      }
    } catch (error) {
      console.error('生成失败:', error)
      this.setData({
        statusText: '生成失败',
        statusIcon: '❌'
      })
      this.addMessage(`❌ ${error.message || '生成失败'}`)
      
      wx.showModal({
        title: '生成失败',
        content: error.message || '请检查网络后重试',
        showCancel: false
      })
    }
  },

  // 轮询任务状态
  async pollTaskStatus() {
    const { taskId } = this.data
    
    this.timer = setInterval(async () => {
      try {
        const status = await this.callAPI(`/task/${taskId}`, {}, 'GET')
        
        // 更新进度
        this.setData({
          progress: status.progress || 0
        })

        // 根据状态更新UI
        if (status.status === 'completed') {
          clearInterval(this.timer)
          this.onGenerateComplete(status.result)
        } else if (status.status === 'failed') {
          clearInterval(this.timer)
          this.setData({
            statusText: '生成失败',
            statusIcon: '❌'
          })
          this.addMessage(`❌ ${status.error || '生成失败'}`)
        } else {
          // 正在运行
          if (status.progress > this.data.progress) {
            this.addMessage(`⏳ 进度 ${status.progress}%`)
          }
        }
      } catch (error) {
        console.error('查询状态失败:', error)
      }
    }, 2000)  // 每2秒查询一次
  },

  // 生成完成
  onGenerateComplete(result) {
    this.setData({
      progress: 100,
      statusText: '生成完成',
      statusIcon: '🎉',
      isCompleted: true
    })
    this.addMessage('🎉 攻略生成完成！')

    // 延迟跳转到结果页
    setTimeout(() => {
      wx.redirectTo({
        url: `/pages/result/result?taskId=${this.data.taskId}`
      })
    }, 1000)
  },

  // 添加进度消息
  addMessage(text) {
    const now = new Date()
    const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
    
    const messages = this.data.messages.concat({
      text,
      time
    })

    this.setData({ messages })
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
