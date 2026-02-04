// API工具函数
const app = getApp()

/**
 * 统一API调用
 */
function request(url, data = {}, method = 'POST') {
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

/**
 * 生成攻略
 */
function generateItinerary(query, mode = 'full') {
  return request('/generate', { query, mode })
}

/**
 * 查询任务状态
 */
function getTaskStatus(taskId) {
  return request(`/task/${taskId}`, {}, 'GET')
}

module.exports = {
  request,
  generateItinerary,
  getTaskStatus
}
