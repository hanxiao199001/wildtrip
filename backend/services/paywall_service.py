"""
付费墙服务
为web端个性化生成的攻略添加付费墙
"""

def add_paywall_to_content(content: str, query: str) -> dict:
    """
    给生成的内容添加付费墙
    
    Args:
        content: 完整的攻略内容
        query: 用户的查询需求
        
    Returns:
        {
            'preview': '预览内容（前30%）',
            'full_content': '完整内容',
            'price': 4.9,
            'locked': True
        }
    """
    
    # 分段显示：前30%免费预览
    lines = content.split('\n')
    preview_line_count = max(10, int(len(lines) * 0.3))
    
    preview_lines = lines[:preview_line_count]
    preview_content = '\n'.join(preview_lines)
    
    # 添加预览提示
    preview_hint = f"""

---

### 🔒 解锁完整攻略

以上是根据你的需求「{query}」定制的攻略预览。

**完整版包含:**
- ✅ 精选酒店/民宿名称 + 直订联系方式（省OTA抽佣）
- ✅ 餐厅名称、详细地址、推荐菜品
- ✅ 景点门票购买渠道和最新优惠
- ✅ 可直接使用的"时间表"（精确到小时）
- ✅ 雨天/意外情况备选方案

**价格：** ¥4.9（一次性付费，永久有效）

<button class="unlock-btn" onclick="handleUnlock()">¥4.9 解锁完整攻略</button>

<p style="font-size: 12px; color: #999; text-align: center;">24小时内不满意全额退款</p>
"""
    
    return {
        'preview': preview_content + preview_hint,
        'full_content': content,
        'price': 4.9,
        'locked': True,
        'unlock_includes': [
            '精选酒店/民宿名称 + 直订联系方式（省OTA抽佣）',
            '餐厅名称、详细地址、推荐菜品',
            '景点门票购买渠道和最新优惠',
            '可直接使用的"时间表"（精确到小时）',
            '雨天/意外情况备选方案'
        ]
    }


def verify_payment(task_id: str, payment_proof: str) -> bool:
    """
    验证支付
    
    Args:
        task_id: 任务ID
        payment_proof: 支付凭证（微信支付订单号等）
        
    Returns:
        True if payment is valid
    """
    # TODO: 接入真实的微信支付验证
    # 目前返回True用于测试
    return True


def unlock_content(task_id: str) -> dict:
    """
    解锁完整内容
    
    Args:
        task_id: 任务ID
        
    Returns:
        {
            'success': True,
            'full_content': '完整内容'
        }
    """
    # TODO: 从数据库或缓存中获取完整内容
    return {
        'success': True,
        'message': '解锁成功'
    }
