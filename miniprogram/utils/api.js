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

/**
 * 获取攻略列表
 */
function getGuidesList() {
  return request('/guides', {}, 'GET')
}

/**
 * 获取攻略详情
 */
function getGuideDetail(slug) {
  return request(`/guides/${encodeURIComponent(slug)}`, {}, 'GET')
}

/**
 * 收藏攻略
 */
function favoriteGuide(slug) {
  return request(`/guides/${encodeURIComponent(slug)}/favorite`, {}, 'POST')
}

/**
 * 取消收藏攻略
 */
function unfavoriteGuide(slug) {
  return request(`/guides/${encodeURIComponent(slug)}/favorite`, {}, 'DELETE')
}

/**
 * 删除攻略
 */
function deleteGuide(slug) {
  return request(`/guides/${encodeURIComponent(slug)}`, {}, 'DELETE')
}

/**
 * 分享攻略（生成分享链接）
 */
function shareGuide(slug) {
  return request(`/guides/${encodeURIComponent(slug)}/share`, {}, 'POST')
}

/**
 * 获取精选攻略（首页展示）
 */
function getFeaturedGuides(limit = 6) {
  return request(`/guides/featured?limit=${limit}`, {}, 'GET')
}

/**
 * 获取相关推荐攻略（结果页展示）
 */
function getRelatedGuides(destination, slug, limit = 3) {
  const params = `destination=${encodeURIComponent(destination)}&slug=${encodeURIComponent(slug)}&limit=${limit}`
  return request(`/guides/related?${params}`, {}, 'GET')
}

module.exports = {
  request,
  generateItinerary,
  getTaskStatus,
  getGuidesList,
  getGuideDetail,
  favoriteGuide,
  unfavoriteGuide,
  deleteGuide,
  shareGuide,
  getFeaturedGuides,
  getRelatedGuides
}
