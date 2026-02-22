#!/usr/bin/env python3
"""
给攻略页面添加付费墙
"""
import re
import sys
from pathlib import Path

PAYWALL_CSS = """
        /* ===== 付费墙样式 ===== */
        .paywall-fade {
            position: relative;
            margin-top: 40px;
            height: 120px;
            overflow: hidden;
        }
        .paywall-fade::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 80px;
            background: linear-gradient(to bottom, rgba(250,250,250,0) 0%, rgba(250,250,250,1) 100%);
        }
        .paywall-fade .prose p {
            filter: blur(3px);
        }
        .paywall {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            padding: 40px 24px;
            border-radius: 16px;
            text-align: center;
            margin: 24px 0 40px;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        .paywall-lock {
            font-size: 48px;
            margin-bottom: 16px;
        }
        .paywall-title {
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        .paywall-desc {
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 24px;
        }
        .paywall-includes {
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            text-align: left;
        }
        .paywall-includes-title {
            font-size: 15px;
            font-weight: 600;
            margin-bottom: 12px;
            text-align: center;
        }
        .paywall-includes-item {
            font-size: 13px;
            margin: 8px 0;
            padding-left: 20px;
            position: relative;
        }
        .paywall-includes-item::before {
            content: '✓';
            position: absolute;
            left: 0;
            font-weight: bold;
        }
        .paywall-btn {
            background: #fff;
            color: #667eea;
            border: none;
            padding: 16px 40px;
            border-radius: 30px;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            margin-top: 20px;
            transition: transform 0.2s;
        }
        .paywall-btn:active {
            transform: scale(0.98);
        }
        .paywall-price {
            font-size: 24px;
        }
        .paywall-price-small {
            font-size: 14px;
        }
        .paywall-guarantee {
            font-size: 12px;
            opacity: 0.8;
            margin-top: 12px;
        }
        .paid-content {
            display: none;
        }
"""

PAYWALL_HTML = """
    <!-- 渐隐效果 -->
    <div class="paywall-fade">
        <p style="filter: blur(3px); color: #999;">具体的民宿名称、餐厅地址、时间节点等详细信息需要解锁完整方案...</p>
    </div>

    <!-- 付费墙 -->
    <div class="paywall" id="paywall">
        <div class="paywall-lock">🔒</div>
        <div class="paywall-title">解锁完整攻略方案</div>
        <div class="paywall-desc">包含所有具体地名、联系方式、时间节点和省钱技巧</div>

        <div class="paywall-includes">
            <div class="paywall-includes-title">完整版包含</div>
            <div class="paywall-includes-item">精选民宿/酒店名称 + 直订联系方式（省OTA抽佣）</div>
            <div class="paywall-includes-item">餐厅名称、位置、推荐菜品和人均价格</div>
            <div class="paywall-includes-item">景点门票购买渠道和优惠方式</div>
            <div class="paywall-includes-item">可直接转发的"时间表"（精确到每个小时）</div>
            <div class="paywall-includes-item">天气变化备选方案</div>
        </div>

        <button class="paywall-btn" onclick="handlePayment()">
            <span class="paywall-price">¥9.9</span>
            <span class="paywall-price-small"> 解锁完整方案</span>
        </button>
        <div class="paywall-guarantee">不满意 24 小时内全额退款 · 微信支付</div>
    </div>

    <!-- 付费内容（隐藏） -->
    <div class="paid-content" id="paid-content">
        <h2>完整行程方案</h2>
        <p>此处为完整的攻略内容，包含所有具体信息...</p>
    </div>

    <script>
    function handlePayment() {
        alert('付费功能开发中...\n\n实际部署时会接入微信支付。\n点击后会跳转到支付页面，支付成功后解锁完整内容。');
        // 测试：直接解锁
        // document.getElementById('paywall').style.display = 'none';
        // document.querySelector('.paywall-fade').style.display = 'none';
        // document.getElementById('paid-content').style.display = 'block';
    }
    </script>
"""

def add_paywall_to_html(file_path):
    """给HTML文件添加付费墙"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经有付费墙
    if 'paywall' in content or '付费墙' in content:
        print(f"⚠️  {file_path.name} 已经有付费墙，跳过")
        return False
    
    # 1. 在 </style> 前插入 CSS
    content = content.replace('</style>', f'{PAYWALL_CSS}\n    </style>')
    
    # 2. 在 </body> 前插入付费墙 HTML
    # 找到最后一个 </div> 之前（通常是 main 容器的结束）
    # 更安全的方式：在 </body> 之前插入
    content = content.replace('</body>', f'\n{PAYWALL_HTML}\n</body>')
    
    # 3. 写回文件
    backup_path = file_path.with_suffix('.html.backup')
    file_path.rename(backup_path)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ {file_path.name} 已添加付费墙 (备份: {backup_path.name})")
    return True

def main():
    if len(sys.argv) < 2:
        print("用法: python add_paywall_to_guides.py <html文件1> <html文件2> ...")
        sys.exit(1)
    
    files = [Path(f) for f in sys.argv[1:]]
    
    success_count = 0
    for file_path in files:
        if not file_path.exists():
            print(f"❌ 文件不存在: {file_path}")
            continue
        
        if add_paywall_to_html(file_path):
            success_count += 1
    
    print(f"\n完成! 成功处理 {success_count}/{len(files)} 个文件")

if __name__ == '__main__':
    main()
