/**
 * 攻略解锁支付功能模块
 * 包含支付流程、解锁检查、支付状态查询
 */

const API_BASE = 'https://api.wildtrip.com.cn'

/**
 * 检查攻略是否已解锁
 * @param {string} guideId - 攻略ID
 * @param {string} openid - 用户openid
 * @returns {Promise<{unlocked: boolean, orderNo?: string}>}
 */
async function checkUnlockStatus(guideId, openid) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API_BASE}/api/vip/check_unlock`,
      method: 'GET',
      data: { guide_id: guideId, openid },
      success: (res) => {
        if (res.data && res.data.success) {
          resolve({
            unlocked: res.data.unlocked || false,
            orderNo: res.data.order_no,
            paidAt: res.data.paid_at
          })
        } else {
          resolve({ unlocked: false })
        }
      },
      fail: (err) => {
        console.error('检查解锁状态失败:', err)
        resolve({ unlocked: false })
      }
    })
  })
}

/**
 * 创建支付订单
 * @param {object} params
 * @param {string} params.guideId - 攻略ID
 * @param {string} params.openid - 用户openid
 * @param {string} params.productId - 商品ID (guide_travel/guide_history)
 * @param {string} params.guideTitle - 攻略标题
 * @returns {Promise<object>} 订单信息和支付参数
 */
async function createPaymentOrder({ guideId, openid, productId, guideTitle }) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API_BASE}/api/vip/create_order`,
      method: 'POST',
      data: {
        openid,
        product_id: productId,
        guide_id: guideId
      },
      success: (res) => {
        if (res.data && res.data.success) {
          resolve(res.data)
        } else {
          reject(new Error(res.data?.error || '创建订单失败'))
        }
      },
      fail: (err) => {
        console.error('创建订单失败:', err)
        reject(new Error('网络错误，请重试'))
      }
    })
  })
}

/**
 * 调起微信支付
 * @param {object} payParams - 微信支付参数
 * @returns {Promise<boolean>} 支付是否成功
 */
async function requestWxPayment(payParams) {
  return new Promise((resolve, reject) => {
    wx.requestPayment({
      ...payParams,
      success: () => {
        console.log('支付成功')
        resolve(true)
      },
      fail: (err) => {
        console.error('支付失败:', err)
        if (err.errMsg.includes('cancel')) {
          reject(new Error('用户取消支付'))
        } else {
          reject(new Error('支付失败: ' + err.errMsg))
        }
      }
    })
  })
}

/**
 * 完整的解锁支付流程
 * @param {object} params
 * @param {string} params.guideId - 攻略ID
 * @param {string} params.guideTitle - 攻略标题
 * @param {string} params.guideType - 攻略类型 (travel/history)
 * @param {Function} params.onSuccess - 成功回调
 * @param {Function} params.onFail - 失败回调
 */
async function startUnlockPayment({ guideId, guideTitle, guideType, onSuccess, onFail }) {
  try {
    // 1. 获取用户openid
    const app = getApp()
    const openid = app.globalData.openid
    
    if (!openid) {
      wx.showModal({
        title: '提示',
        content: '请先登录',
        success: (res) => {
          if (res.confirm) {
            wx.switchTab({ url: '/pages/user/user' })
          }
        }
      })
      onFail && onFail(new Error('未登录'))
      return
    }

    // 2. 确定商品类型
    const productId = guideType === 'history' ? 'guide_history' : 'guide_travel'
    const productName = guideType === 'history' ? '人文历史路线' : '旅行攻略'
    const price = '0.01'  // 测试价格（正式环境改为 guideType === 'history' ? '9.80' : '4.80'）

    // 3. 显示支付确认对话框
    const confirmed = await new Promise((resolve) => {
      wx.showModal({
        title: '解锁完整攻略',
        content: `${productName}解锁\n${guideTitle}\n\n价格: ¥${price}`,
        confirmText: '立即支付',
        cancelText: '取消',
        success: (res) => resolve(res.confirm)
      })
    })

    if (!confirmed) {
      onFail && onFail(new Error('用户取消'))
      return
    }

    // 4. 显示加载提示
    wx.showLoading({ title: '创建订单中...', mask: true })

    // 5. 创建支付订单
    const orderData = await createPaymentOrder({
      guideId,
      openid,
      productId,
      guideTitle
    })

    wx.hideLoading()

    // 6. 调起微信支付
    const paySuccess = await requestWxPayment(orderData.pay_params)

    if (paySuccess) {
      // 7. 支付成功
      wx.showToast({
        title: '支付成功',
        icon: 'success',
        duration: 2000
      })

      // 等待一秒让用户看到提示
      await new Promise(resolve => setTimeout(resolve, 1000))

      onSuccess && onSuccess(orderData.order)
    }

  } catch (error) {
    wx.hideLoading()
    
    console.error('解锁支付流程失败:', error)
    
    wx.showModal({
      title: '支付失败',
      content: error.message || '未知错误',
      showCancel: false
    })

    onFail && onFail(error)
  }
}

/**
 * 获取我已解锁的攻略列表
 * @param {string} openid - 用户openid
 * @returns {Promise<Array>} 已解锁攻略列表
 */
async function getMyUnlockedGuides(openid) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API_BASE}/api/vip/my_unlocked`,
      method: 'GET',
      data: { openid },
      success: (res) => {
        if (res.data && res.data.success) {
          resolve(res.data.guides || [])
        } else {
          resolve([])
        }
      },
      fail: (err) => {
        console.error('获取已解锁列表失败:', err)
        resolve([])
      }
    })
  })
}

module.exports = {
  checkUnlockStatus,
  createPaymentOrder,
  requestWxPayment,
  startUnlockPayment,
  getMyUnlockedGuides
}
