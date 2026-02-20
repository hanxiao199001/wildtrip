// 订阅页面
const app = getApp()
const api = require('../../utils/api')

Page({
  data: {
    // 订阅消息模板 ID(需要在公众平台申请后填入)
    tmplIds: [
      process.env.WECHAT_SUBSCRIBE_TEMPLATE_WEEKEND || '',  // 周末计划推送
    ],
    
    // 订阅权益展示
    benefits: [
      { icon: '📅', title: '每周四推送', desc: '周末野游计划准时送达' },
      { icon: '💰', title: '独家底价', desc: 'B端酒店直销价,比OTA便宜' },
      { icon: '🎯', title: '个性化推荐', desc: '根据你的偏好定制行程' },
      { icon: '🎁', title: '会员福利', desc: '延迟退房、房型升级' }
    ],
    
    subscribed: false,  // 是否已订阅
    loading: false
  },

  onLoad(options) {
    // 检查是否已订阅
    this.checkSubscriptionStatus()
  },

  /**
   * 检查订阅状态
   */
  async checkSubscriptionStatus() {
    try {
      const openid = wx.getStorageSync('openid')
      if (!openid) {
        console.log('用户未登录,无法查询订阅状态')
        return
      }
      
      const res = await api.get('/user/subscription/status', { openid })
      
      this.setData({
        subscribed: res.subscribed || false
      })
      
    } catch (e) {
      console.error('查询订阅状态失败', e)
    }
  },

  /**
   * 🔥 核心:引导用户订阅
   */
  async requestSubscribe() {
    const { tmplIds } = this.data
    
    // 检查模板 ID
    if (!tmplIds[0]) {
      wx.showModal({
        title: '配置错误',
        content: '订阅消息模板 ID 未配置,请联系客服',
        showCancel: false
      })
      return
    }
    
    this.setData({ loading: true })
    
    try {
      // 🔥 调用微信订阅接口
      const res = await wx.requestSubscribeMessage({
        tmplIds: tmplIds,
        success: (res) => {
          console.log('订阅弹窗返回:', res)
          
          // 检查订阅结果
          const templateId = tmplIds[0]
          const status = res[templateId]  // 'accept' | 'reject' | 'ban'
          
          if (status === 'accept') {
            // ✅ 用户同意订阅
            this.onSubscribeSuccess(res)
          } else if (status === 'reject') {
            // ❌ 用户拒绝
            this.onSubscribeReject()
          } else if (status === 'ban') {
            // ⚠️ 用户已永久拒绝
            this.onSubscribeBan()
          }
        },
        fail: (err) => {
          console.error('订阅失败', err)
          wx.showToast({
            title: '订阅失败,请重试',
            icon: 'none'
          })
        }
      })
      
    } catch (e) {
      console.error('请求订阅失败', e)
    } finally {
      this.setData({ loading: false })
    }
  },

  /**
   * 订阅成功
   */
  async onSubscribeSuccess(result) {
    console.log('✅ 用户订阅成功', result)
    
    // 1. 同步到后端
    try {
      const openid = wx.getStorageSync('openid')
      
      await api.post('/user/subscription/sync', {
        openid,
        subscriptions: result,
        timestamp: Date.now()
      })
      
      this.setData({ subscribed: true })
      
      // 2. 提示用户
      wx.showModal({
        title: '订阅成功 🎉',
        content: '每周四晚 8 点,我们会为您推送周末野游计划。\n\n第一次推送预计本周四送达!',
        showCancel: false,
        confirmText: '好的',
        success: () => {
          // 返回上一页或跳转到首页
          wx.navigateBack({
            delta: 1,
            fail: () => {
              wx.switchTab({ url: '/pages/index/index' })
            }
          })
        }
      })
      
    } catch (e) {
      console.error('同步订阅状态失败', e)
    }
  },

  /**
   * 用户拒绝订阅
   */
  onSubscribeReject() {
    wx.showModal({
      title: '提示',
      content: '您拒绝了订阅。如果以后想订阅,可以在"我的-设置"里重新开启。',
      showCancel: false
    })
  },

  /**
   * 用户永久拒绝
   */
  onSubscribeBan() {
    wx.showModal({
      title: '提示',
      content: '您已关闭此消息订阅。\n\n如需开启,请前往:\n微信 → 我 → 设置 → 通知管理 → 订阅消息',
      showCancel: false
    })
  },

  /**
   * 稍后订阅
   */
  onSkip() {
    wx.navigateBack({
      delta: 1,
      fail: () => {
        wx.switchTab({ url: '/pages/index/index' })
      }
    })
  }
})
