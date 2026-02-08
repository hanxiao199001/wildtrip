// WildTrip Web App - Frontend Logic

// 自动检测API地址：本地开发用localhost，生产环境用当前域名
const API_BASE = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000/api'
    : `http://${window.location.hostname}:5000/api`;

const WS_BASE = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000'
    : `http://${window.location.hostname}:5000`;

let currentTaskId = null;
let pollInterval = null;
let socket = null;

// Markdown to HTML converter (enhanced version with Meituan button styling)
function markdownToHtml(markdown) {
    let html = markdown
        // Headers
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        // 🔥 Images (before links!) - 统一尺寸，居中显示
        .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<div style="text-align: center; margin: 24px 0; padding: 0;"><img src="$2" alt="$1" style="max-width: 90%; max-height: 500px; height: auto; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.12); display: inline-block;" loading="lazy" /></div>')
        // Bold
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        // 🔥 美团链接渲染为醒目按钮
        .replace(/\[([^\]]*?(?:美团|团购|预订|查看详情|门票)[^\]]*?)\]\(([^)]+(?:meituan|i\.meituan)[^)]*)\)/gi, function(match, text, url) {
            // 判断类型
            let icon = '🍽️';
            let btnText = '团购';

            if (text.includes('预订') || text.includes('酒店') || text.includes('住宿')) {
                icon = '🏨';
                btnText = '预订';
            } else if (text.includes('门票') || text.includes('景点')) {
                icon = '🎫';
                btnText = '门票';
            }

            // 清理文字中的emoji和"有返现"字样
            let cleanText = text.replace(/💰\s*有返现/gi, '').replace(/💰/g, '').trim();

            return `<a href="${url}" target="_blank" rel="noopener" class="meituan-button">
                ${icon} ${cleanText}
            </a>`;
        })
        // 普通链接（排除图片，图片是 ![...](...)）
        .replace(/(?<!!)\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener" class="normal-link">$1</a>')
        // Lists
        .replace(/^\- (.+)$/gim, '<li>$1</li>')
        .replace(/^(\d+)\. (.+)$/gim, '<li>$2</li>')
        // Line breaks
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');
    
    // Wrap lists
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    
    // Wrap paragraphs
    if (!html.startsWith('<h') && !html.startsWith('<ul')) {
        html = '<p>' + html + '</p>';
    }
    
    return html;
}

// Generate guide
document.getElementById('generateForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const query = document.getElementById('queryInput').value.trim();
    const mode = document.querySelector('input[name="mode"]:checked').value;
    
    if (!query) {
        alert('请输入你的旅行需求 🧳');
        return;
    }
    
    // Show loading, hide input
    document.getElementById('inputSection').classList.add('hidden');
    document.getElementById('loadingSection').classList.remove('hidden');
    document.getElementById('resultSection').classList.add('hidden');
    
    try {
        // Create generation task
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                mode: mode,
                options: {}
            })
        });
        
        if (!response.ok) {
            throw new Error('生成请求失败');
        }
        
        const data = await response.json();
        currentTaskId = data.task_id;
        
        console.log('✅ 任务创建成功:', currentTaskId);
        
        // 订阅WebSocket实时更新
        const socket = initSocket();
        socket.emit('subscribe', { task_id: currentTaskId });
        
        // 同时启动轮询作为兜底（防止WebSocket失败）
        pollTaskStatus();
        
    } catch (error) {
        console.error('❌ 生成失败:', error);
        alert('生成失败，请稍后重试 😢\n' + error.message);
        location.reload();
    }
});

// Poll task status
function pollTaskStatus() {
    let attempts = 0;
    const maxAttempts = 150; // 🔥 延长到150次，每2秒一次 = 5分钟
    
    pollInterval = setInterval(async () => {
        attempts++;
        
        if (attempts > maxAttempts) {
            clearInterval(pollInterval);
            alert('生成超时，AI可能太忙了 ⏰\n请稍后重试或简化查询');
            location.reload();
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE}/task/${currentTaskId}`);
            
            if (!response.ok) {
                throw new Error('获取状态失败');
            }
            
            const data = await response.json();
            
            console.log('📊 任务状态:', data.status, '进度:', data.progress + '%', '耗时:', attempts * 2 + '秒');
            
            // 🔥 更友好的进度提示
            let progressText = `进度: ${data.progress}%`;
            let tipText = 'AI正在为你挖掘野路子干货 🔍';
            
            if (data.progress === 0) {
                tipText = '正在准备...' + (attempts > 5 ? ' 请稍候 ☕' : '');
            } else if (data.progress === 30) {
                tipText = 'AI正在生成中...' + (attempts > 30 ? ' 内容越丰富，时间越长 📝' : '');
            } else if (data.progress === 70) {
                tipText = '正在添加返现链接... 马上就好！🔗';
            } else if (attempts > 60) {
                tipText = `已等待${Math.floor(attempts * 2 / 60)}分钟... AI正在深度思考 🤔`;
            }
            
            // Update progress
            document.getElementById('loadingProgress').textContent = progressText + 
                (data.status === 'running' ? ' 🔥' : '');
            document.querySelector('#loadingSection p:last-child').textContent = tipText;
            
            // Check if completed
            if (data.status === 'completed') {
                clearInterval(pollInterval);
                displayResult(data);
            } else if (data.status === 'failed') {
                clearInterval(pollInterval);
                alert('生成失败 😢\n可能原因：\n1. AI服务暂时不可用\n2. 查询过于复杂\n\n请稍后重试或简化查询');
                location.reload();
            }
            
        } catch (error) {
            console.error('❌ 轮询失败:', error);
            // 🔥 不要因为单次失败就停止，继续轮询
        }
        
    }, 2000); // Poll every 2 seconds
}

// Display result
function displayResult(data) {
    console.log('✨ 攻略生成完成!');
    
    // Hide loading
    document.getElementById('loadingSection').classList.add('hidden');
    
    // Get result data
    const result = data.result || {};
    const content = result.content || '暂无内容';
    const stats = result.stats || {};
    
    // 🔥 调试：检查是否有图片
    const imageMatches = content.match(/!\[[^\]]*\]\([^)]+\)/g);
    console.log(`📸 检测到 ${imageMatches ? imageMatches.length : 0} 张图片`);
    if (imageMatches && imageMatches.length > 0) {
        console.log('图片示例:', imageMatches.slice(0, 3));
    }
    
    // Update stats
    const statsHtml = `
        <span>📝 ${stats.word_count || 0} 字</span>
        ${stats.hotels_count > 0 ? `<span>• 🏨 ${stats.hotels_count} 家酒店</span>` : ''}
        ${stats.restaurants_count > 0 ? `<span>• 🍜 ${stats.restaurants_count} 家餐厅</span>` : ''}
        ${stats.tickets_count > 0 ? `<span>• 🎫 ${stats.tickets_count} 个景点</span>` : ''}
    `;
    document.getElementById('resultStats').innerHTML = statsHtml;
    
    // Convert markdown to HTML
    let htmlContent = markdownToHtml(content);
    
    // 🔥 提取推荐的酒店/餐厅信息（用于预订卡片）
    const bookingItems = extractBookingItems(content, stats);
    
    // 🔥 在攻略中插入预订卡片
    if (bookingItems.length > 0) {
        htmlContent = insertBookingCards(htmlContent, bookingItems);
        
        // 🔥 计算总返现金额
        const totalCashback = bookingItems.reduce((sum, item) => sum + Math.round(item.price * 0.5), 0);
        
        // 在攻略顶部插入返现总览
        const cashbackSummary = createCashbackSummary(totalCashback, Math.floor(Math.random() * 200) + 50);
        htmlContent = htmlContent.replace(/(<h2>)/i, cashbackSummary + '$1');
    }
    
    document.getElementById('resultContent').innerHTML = htmlContent;
    
    // Show result
    document.getElementById('resultSection').classList.remove('hidden');
    
    // Scroll to result
    document.getElementById('resultSection').scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
    });
    
    // 🔥 显示引导预订弹窗（2秒后）
    if (bookingItems.length > 0) {
        setTimeout(() => {
            const totalCashback = bookingItems.reduce((sum, item) => sum + Math.round(item.price * 0.5), 0);
            showBookingModal(bookingItems, totalCashback);
        }, 2000);
    }
}

// Copy to clipboard (full guide)
function copyToClipboard() {
    const content = document.getElementById('resultContent').innerText;
    
    navigator.clipboard.writeText(content).then(() => {
        alert('✅ 攻略已复制到剪贴板！');
    }).catch(() => {
        alert('❌ 复制失败，请手动选择复制');
    });
}

// 🔥 Share guide
let currentShareUrl = '';

function shareGuide() {
    // 如果已有分享链接，直接分享
    if (currentShareUrl) {
        shareLink(currentShareUrl);
        return;
    }
    
    // 否则生成分享链接（使用当前URL + hash）
    const shareUrl = window.location.href;
    shareLink(shareUrl);
}

function shareLink(url) {
    // 尝试使用Web Share API（移动端）
    if (navigator.share) {
        navigator.share({
            title: '野游记 - 我的旅游攻略',
            text: '我用野游记生成了一份超实用的旅游攻略！',
            url: url
        }).then(() => {
            console.log('✅ 分享成功');
        }).catch((error) => {
            console.log('分享取消或失败:', error);
            // 降级到复制链接
            copyShareLink(url);
        });
    } else {
        // 桌面端：复制链接
        copyShareLink(url);
    }
}

function copyShareLink(url) {
    navigator.clipboard.writeText(url).then(() => {
        alert('✅ 链接已复制！\n\n' + url + '\n\n可以分享给朋友了 🎉');
    }).catch(() => {
        // 降级方案：显示链接让用户手动复制
        const modal = document.createElement('div');
        modal.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 9999;';
        modal.innerHTML = `
            <div style="background: white; padding: 24px; border-radius: 16px; max-width: 500px; width: 90%;">
                <h3 style="font-size: 20px; font-weight: bold; margin-bottom: 16px;">📋 分享链接</h3>
                <input type="text" value="${url}" readonly style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 14px;" onclick="this.select()">
                <p style="margin-top: 12px; font-size: 14px; color: #666;">点击输入框选中，然后复制（Ctrl+C / Cmd+C）</p>
                <button onclick="this.parentElement.parentElement.remove()" style="margin-top: 16px; width: 100%; padding: 12px; background: linear-gradient(135deg, #FF6B6B, #FF5252); color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer;">关闭</button>
            </div>
        `;
        document.body.appendChild(modal);
    });
}

// Copy keyword to clipboard (for Meituan search)
function copyToClipboard(keyword, element) {
    navigator.clipboard.writeText(keyword).then(() => {
        // 修改提示文字
        const originalHTML = element.innerHTML;
        element.innerHTML = element.innerHTML.replace('👆点击复制', '✅已复制');
        element.style.background = 'linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%)';
        element.style.color = '#fff';
        
        // 2秒后恢复
        setTimeout(() => {
            element.innerHTML = originalHTML;
            element.style.background = '';
            element.style.color = '';
        }, 2000);
    }).catch(() => {
        alert('❌ 复制失败，请手动复制关键词：' + keyword);
    });
}

// Initialize Socket.IO connection
function initSocket() {
    if (socket && socket.connected) {
        return socket;
    }
    
    socket = io(WS_BASE, {
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionAttempts: 5
    });
    
    socket.on('connect', () => {
        console.log('🔌 WebSocket已连接');
    });
    
    socket.on('disconnect', () => {
        console.log('🔌 WebSocket已断开');
    });
    
    socket.on('error', (error) => {
        console.error('❌ WebSocket错误:', error);
    });
    
    // 监听实时进度更新
    socket.on('wildtrip_progress', (data) => {
        console.log('📊 实时进度:', data.progress + '%', data.message);
        updateProgress(data.progress, data.message, data.type);
        
        // 如果完成，自动获取结果
        if (data.type === 'done' && currentTaskId) {
            setTimeout(() => {
                fetchTaskResult();
            }, 500);
        }
    });
    
    socket.on('subscribed', (data) => {
        console.log('✅ 已订阅任务:', data.task_id);
    });
    
    return socket;
}

// Update progress display
function updateProgress(progress, message, type) {
    const progressElement = document.getElementById('loadingProgress');
    const messageElement = document.querySelector('#loadingSection p:last-child');
    
    if (progressElement) {
        // 添加动画效果
        progressElement.textContent = `进度: ${progress}% 🔥`;
        
        // 根据类型添加不同的图标
        const icons = {
            'parsing': '📍',
            'building_prompt': '🧠',
            'rag_search': '🔍',
            'generating': '✍️',
            'ai_done': '✅',
            'affiliate_start': '🔗',
            'affiliate_hotels': '🏨',
            'affiliate_food': '🍜',
            'affiliate_tickets': '🎫',
            'affiliate_done': '💰',
            'stats': '📊',
            'done': '🎉'
        };
        
        const icon = icons[type] || '⚡';
        progressElement.textContent = `${icon} ${progress}%`;
    }
    
    if (messageElement && message) {
        messageElement.textContent = message;
        
        // 添加淡入效果
        messageElement.style.animation = 'fadeIn 0.3s ease-in';
    }
}

// Fetch task result when completed
async function fetchTaskResult() {
    if (!currentTaskId) return;
    
    try {
        const response = await fetch(`${API_BASE}/task/${currentTaskId}`);
        
        if (!response.ok) {
            throw new Error('获取结果失败');
        }
        
        const data = await response.json();
        
        if (data.status === 'completed') {
            clearInterval(pollInterval);
            displayResult(data);
        }
        
    } catch (error) {
        console.error('❌ 获取结果失败:', error);
    }
}

// Load example on page load (optional)
window.addEventListener('DOMContentLoaded', () => {
    console.log('🌴 野游记 WildTrip 已加载');
    console.log('🤖 API地址:', API_BASE);
    console.log('🔌 WebSocket地址:', WS_BASE);
    
    // 初始化Socket.IO
    initSocket();
});

// ========== 预订卡片功能 ==========

// 从攻略内容中提取推荐的酒店/餐厅信息
function extractBookingItems(content, stats) {
    const items = [];
    
    // 简单提取：查找提到的酒店名称
    // 正则匹配：酒店名、价格区间
    const hotelRegex = /(?:入住|推荐|酒店[:：]\s*)([^\n,，。]+?)(?:酒店|宾馆|民宿|客栈)/gi;
    const matches = content.matchAll(hotelRegex);
    
    let hotelCount = 0;
    for (const match of matches) {
        if (hotelCount >= 3) break; // 最多3个
        
        const name = match[1].trim() + '酒店';
        const price = 200 + Math.floor(Math.random() * 300); // 200-500元
        
        items.push({
            id: `hotel_${hotelCount}`,
            name: name,
            type: '酒店',
            icon: '🏨',
            price: price,
            rating: (4.5 + Math.random() * 0.4).toFixed(1),
            url: `https://www.meituan.com/search?q=${encodeURIComponent(name)}`
        });
        
        hotelCount++;
    }
    
    // 如果没提取到，使用stats中的统计数据生成示例
    if (items.length === 0 && stats.hotels_count > 0) {
        items.push({
            id: 'hotel_default',
            name: '精选酒店',
            type: '酒店',
            icon: '🏨',
            price: 299,
            rating: '4.8',
            url: 'https://www.meituan.com/hotel'
        });
    }
    
    return items;
}

// 生成预订卡片HTML（按新设计重构）
function createBookingCard(item) {
    const cashbackAmount = Math.round(item.price * 0.5); // 50%返现
    const discountedPrice = item.price - cashbackAmount;
    const bookedToday = Math.floor(Math.random() * 20) + 5; // 5-25人
    const stockLeft = Math.floor(Math.random() * 5) + 2; // 2-7间
    
    return `
        <div class="booking-card">
            <!-- 商品信息 -->
            <div class="booking-card-header">
                <div class="booking-card-image">
                    ${item.icon}
                </div>
                <div class="booking-card-info">
                    <h4 class="booking-card-name">${item.name}</h4>
                    <div class="booking-card-rating">
                        ⭐ ${item.rating} <span style="color: #9CA3AF;">(${Math.floor(Math.random() * 5000) + 1000}条评价)</span>
                    </div>
                    <div class="booking-card-location">
                        📍 距${item.location || '市中心'}步行5分钟
                    </div>
                </div>
            </div>
            
            <!-- 标签 -->
            <div class="booking-card-tags">
                <span class="booking-tag">网红设计</span>
                <span class="booking-tag">早餐丰富</span>
                <span class="booking-tag">位置绝佳</span>
            </div>
            
            <!-- 价格区（核心）-->
            <div class="booking-card-price-section">
                <div class="booking-price-original">原价 ¥${item.price}</div>
                <div class="booking-price-main">
                    <div>
                        <span class="booking-price-discounted">返现后仅</span>
                        <span class="booking-price-amount">¥${discountedPrice}</span>
                        <span class="booking-price-unit">/晚</span>
                    </div>
                    <div class="booking-cashback-badge">返 ¥${cashbackAmount}</div>
                </div>
                <div class="booking-cashback-rate">返现率 50%</div>
            </div>
            
            <!-- 紧迫感 -->
            <div class="booking-urgency">
                <span class="booking-urgency-left">🔥 今日已有 ${bookedToday} 人预订</span>
                <span class="booking-urgency-right">仅剩 ${stockLeft} 间！</span>
            </div>
            
            <!-- CTA按钮 -->
            <button onclick="window.open('${item.url}', '_blank')" class="booking-btn-cta">
                立即预订，返现 ¥${cashbackAmount}
            </button>
            
            <!-- 信任标签 -->
            <div class="booking-trust-tags">
                <span>✓ 随时可退</span>
                <span>✓ 价格保障</span>
                <span>✓ 返现秒到</span>
            </div>
        </div>
    `;
}

// 生成攻略顶部返现总览（新设计：利益前置）
function createCashbackSummary(totalCashback, bookingCount) {
    return `
        <div class="cashback-summary">
            <div class="cashback-summary-left">
                <div class="cashback-summary-icon">💰</div>
                <div>
                    <div class="cashback-summary-text">本攻略预估可返现</div>
                    <div class="cashback-summary-amount">¥${totalCashback}</div>
                </div>
            </div>
            <div class="cashback-summary-right">
                已为 ${bookingCount} 人<br>省下 ¥${(totalCashback * bookingCount).toLocaleString()}
            </div>
        </div>
    `;
}

// 在攻略内容中插入预订卡片
function insertBookingCards(guideHtml, bookingItems) {
    let result = guideHtml;
    
    // 🔥 新逻辑：解析Markdown中的餐厅/酒店信息，直接替换为预订卡片
    
    // 1. 识别并替换餐厅推荐区域
    result = result.replace(/(<h3>.*?[午晚早]餐推荐.*?<\/h3>)([\s\S]*?)(?=<h[23]|$)/gi, function(match, header, content) {
        // 提取餐厅信息
        const restaurants = extractRestaurantsFromContent(content);
        
        if (restaurants.length > 0) {
            let restaurantCards = header;
            restaurants.forEach(restaurant => {
                restaurantCards += createRestaurantCard(restaurant);
            });
            return restaurantCards;
        }
        return match;
    });
    
    // 2. 识别并替换酒店推荐区域
    result = result.replace(/(<h2>.*?住宿推荐.*?<\/h2>)([\s\S]*?)(?=<h2|$)/gi, function(match, header, content) {
        // 提取酒店信息
        const hotels = extractHotelsFromContent(content);
        
        if (hotels.length > 0) {
            let hotelCards = header;
            hotels.forEach(hotel => {
                hotelCards += createHotelCard(hotel);
            });
            return hotelCards;
        }
        return match;
    });
    
    // 3. 在攻略末尾插入打包预订卡片
    const bundleCard = createBundleCard(bookingItems);
    result = result + bundleCard;
    
    return result;
}

// 从HTML内容中提取餐厅信息（HTML格式）
function extractRestaurantsFromContent(content) {
    const restaurants = [];
    
    // 正则匹配HTML格式：<strong>餐厅名</strong> ¥XX/人 ⭐X.X
    const pattern = /<strong>([^<]+)<\/strong>\s*[¥￥](\d+)\/人\s*⭐([\d.]+)/gi;
    let match;
    
    while ((match = pattern.exec(content)) !== null) {
        const name = match[1].trim();
        const price = parseInt(match[2]);
        const rating = match[3];
        
        // 提取特色菜
        const specialtyMatch = content.match(new RegExp(`${name}[\\s\\S]{0,300}<strong>特色菜[：:]?<\/strong>[\\s]*(.*?)(?:<br|<\/li|<p)`, 'i'));
        const specialties = specialtyMatch ? specialtyMatch[1].replace(/<[^>]+>/g, '').trim() : '特色美食';
        
        // 提取美团链接关键词
        const searchKeyword = name;
        
        restaurants.push({
            name: name,
            price: price,
            rating: rating,
            specialties: specialties.substring(0, 50),  // 限制长度
            searchKeyword: searchKeyword,
            type: 'restaurant'
        });
    }
    
    console.log(`📝 提取到 ${restaurants.length} 家餐厅`);
    return restaurants;
}

// 从HTML内容中提取酒店信息（HTML格式）
function extractHotelsFromContent(content) {
    const hotels = [];
    
    // 正则匹配HTML格式：<h3>1. 高端选择：酒店名</h3>
    const h3Pattern = /<h3>\s*\d+\.\s*[^：:]+[：:]([^<]+)<\/h3>/gi;
    const names = [...content.matchAll(h3Pattern)].map(m => m[1].trim());
    
    // 为每个酒店名提取详情
    for (const name of names) {
        // 找到这个酒店名所在的section
        const sectionMatch = content.match(new RegExp(`<h3>[^<]*${name}[^<]*<\/h3>([\\s\\S]{0,800}?)(?:<h3>|<h2>|$)`, 'i'));
        if (!sectionMatch) continue;
        
        const section = sectionMatch[1];
        
        // 提取价格
        const priceMatch = section.match(/[¥￥](\d+)\/晚/);
        const price = priceMatch ? parseInt(priceMatch[1]) : 300;
        
        // 提取评分
        const ratingMatch = section.match(/⭐([\d.]+)/);
        const rating = ratingMatch ? ratingMatch[1] : '4.7';
        
        // 提取特色
        const featureMatch = section.match(/<strong>特色[：:]?<\/strong>[\\s]*(.*?)(?:<br|<\/li|<strong)/i);
        const features = featureMatch ? featureMatch[1].replace(/<[^>]+>/g, '').trim().substring(0, 50) : '位置优越，设计独特';
        
        // 提取美团链接关键词
        const searchKeyword = name;
        
        hotels.push({
            name: name,
            price: price,
            rating: rating,
            features: features,
            searchKeyword: searchKeyword,
            type: 'hotel'
        });
    }
    
    console.log(`📝 提取到 ${hotels.length} 家酒店`);
    return hotels;
}

// 生成餐厅预订卡片
function createRestaurantCard(restaurant) {
    const cashbackAmount = Math.round(restaurant.price * 0.15); // 餐饮15%返现
    const discountedPrice = restaurant.price - cashbackAmount;
    const bookedToday = Math.floor(Math.random() * 30) + 10; // 10-40人
    
    const meituan_url = `https://i.meituan.com/search?q=${encodeURIComponent(restaurant.searchKeyword)}`;
    
    return `
        <div class="booking-card" style="margin: 20px 0;">
            <div class="booking-card-header">
                <div class="booking-card-image">🍜</div>
                <div class="booking-card-info">
                    <h4 class="booking-card-name">${restaurant.name}</h4>
                    <div class="booking-card-rating">
                        ⭐ ${restaurant.rating} <span style="color: #9CA3AF;">(${Math.floor(Math.random() * 2000) + 500}条评价)</span>
                    </div>
                    <div class="booking-card-location">
                        🍴 ${restaurant.specialties}
                    </div>
                </div>
            </div>
            
            <div class="booking-card-tags">
                <span class="booking-tag">本地特色</span>
                <span class="booking-tag">人气餐厅</span>
            </div>
            
            <div class="booking-card-price-section">
                <div class="booking-price-original">人均 ¥${restaurant.price}</div>
                <div class="booking-price-main">
                    <div>
                        <span class="booking-price-discounted">团购后</span>
                        <span class="booking-price-amount">¥${discountedPrice}</span>
                        <span class="booking-price-unit">/人</span>
                    </div>
                    <div class="booking-cashback-badge">返 ¥${cashbackAmount}</div>
                </div>
                <div class="booking-cashback-rate">返现率 15%</div>
            </div>
            
            <div class="booking-urgency">
                <span class="booking-urgency-left">🔥 今日已有 ${bookedToday} 人预订</span>
            </div>
            
            <button onclick="window.open('${meituan_url}', '_blank')" class="booking-btn-cta">
                美团团购，返现 ¥${cashbackAmount}
            </button>
            
            <div class="booking-trust-tags">
                <span>✓ 支持退款</span>
                <span>✓ 过期退</span>
                <span>✓ 返现秒到</span>
            </div>
        </div>
    `;
}

// 生成酒店预订卡片（复用已有逻辑，增强版）
function createHotelCard(hotel) {
    const cashbackAmount = Math.round(hotel.price * 0.5); // 50%返现
    const discountedPrice = hotel.price - cashbackAmount;
    const bookedToday = Math.floor(Math.random() * 20) + 5; // 5-25人
    const stockLeft = Math.floor(Math.random() * 5) + 2; // 2-7间
    
    const meituan_url = `https://i.meituan.com/search?q=${encodeURIComponent(hotel.searchKeyword)}`;
    
    return `
        <div class="booking-card" style="margin: 20px 0;">
            <div class="booking-card-header">
                <div class="booking-card-image">🏨</div>
                <div class="booking-card-info">
                    <h4 class="booking-card-name">${hotel.name}</h4>
                    <div class="booking-card-rating">
                        ⭐ ${hotel.rating} <span style="color: #9CA3AF;">(${Math.floor(Math.random() * 3000) + 1000}条评价)</span>
                    </div>
                    <div class="booking-card-location">
                        📍 ${hotel.features}
                    </div>
                </div>
            </div>
            
            <div class="booking-card-tags">
                <span class="booking-tag">设计独特</span>
                <span class="booking-tag">位置优越</span>
                <span class="booking-tag">性价比高</span>
            </div>
            
            <div class="booking-card-price-section">
                <div class="booking-price-original">原价 ¥${hotel.price}</div>
                <div class="booking-price-main">
                    <div>
                        <span class="booking-price-discounted">返现后仅</span>
                        <span class="booking-price-amount">¥${discountedPrice}</span>
                        <span class="booking-price-unit">/晚</span>
                    </div>
                    <div class="booking-cashback-badge">返 ¥${cashbackAmount}</div>
                </div>
                <div class="booking-cashback-rate">返现率 50%</div>
            </div>
            
            <div class="booking-urgency">
                <span class="booking-urgency-left">🔥 今日已有 ${bookedToday} 人预订</span>
                <span class="booking-urgency-right">仅剩 ${stockLeft} 间！</span>
            </div>
            
            <button onclick="window.open('${meituan_url}', '_blank')" class="booking-btn-cta">
                立即预订，返现 ¥${cashbackAmount}
            </button>
            
            <div class="booking-trust-tags">
                <span>✓ 随时可退</span>
                <span>✓ 价格保障</span>
                <span>✓ 返现秒到</span>
            </div>
        </div>
    `;
}

// 生成打包预订卡片（提客单价）
function createBundleCard(bookingItems) {
    const totalOriginalPrice = bookingItems.reduce((sum, item) => sum + item.price, 0) * 2; // 假设住2晚
    const totalCashback = Math.round(totalOriginalPrice * 0.5);
    const finalPrice = totalOriginalPrice - totalCashback;
    
    // 组合套餐内容
    const bundleItems = [];
    bookingItems.forEach(item => {
        if (item.type === '酒店') bundleItems.push('酒店2晚');
    });
    bundleItems.push('熊猫基地门票');
    bundleItems.push('火锅代金券');
    
    return `
        <div class="booking-bundle-card">
            <div class="booking-bundle-header">
                <div class="booking-bundle-icon">📦</div>
                <h3 class="booking-bundle-title">一键打包本攻略全部推荐</h3>
            </div>
            
            <div class="booking-bundle-items">
                含：${bundleItems.join(' + ')}
            </div>
            
            <div class="booking-bundle-price">
                <span class="booking-bundle-price-old">¥${totalOriginalPrice}</span>
                <span class="booking-bundle-price-new">¥${finalPrice}</span>
                <span class="booking-bundle-price-save">省50%</span>
            </div>
            
            <button onclick="bundleBooking()" class="booking-bundle-btn">
                打包预订
            </button>
        </div>
    `;
}

// 打包预订功能
function bundleBooking() {
    alert('🎉 打包预订功能即将上线！\n一键预订，省时又省钱。');
}

// 显示引导预订弹窗（优化CTA文案）
function showBookingModal(items, totalCashback) {
    // 最多显示3个推荐
    const displayItems = items.slice(0, 3);
    const firstItemCashback = Math.round(displayItems[0].price * 0.5);
    
    const itemsHtml = displayItems.map(item => {
        const cashback = Math.round(item.price * 0.5);
        const discountedPrice = item.price - cashback;
        return `
            <div style="background: #f8f9fa; border-radius: 12px; padding: 16px; display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                <div style="font-size: 32px;">${item.icon}</div>
                <div style="flex: 1;">
                    <div style="font-size: 16px; font-weight: 600; margin-bottom: 4px;">${item.name}</div>
                    <div style="font-size: 14px; color: #666;">
                        <span style="text-decoration: line-through;">¥${item.price}</span>
                        → <span style="color: #DC2626; font-weight: 700;">¥${discountedPrice}/晚</span>
                    </div>
                </div>
                <div style="font-size: 18px; font-weight: 700; color: #EF4444;">返¥${cashback}</div>
            </div>
        `;
    }).join('');
    
    const modal = document.createElement('div');
    modal.className = 'booking-modal';
    modal.innerHTML = `
        <div class="booking-modal-content">
            <div style="text-align: center; margin-bottom: 24px;">
                <div style="font-size: 64px; margin-bottom: 16px;">🎉</div>
                <h3 style="font-size: 24px; font-weight: 700; margin: 0 0 8px 0;">攻略已生成！</h3>
                <p style="font-size: 16px; color: #666; margin: 0;">现在预订，最高返现50%</p>
            </div>
            
            <div style="margin-bottom: 24px;">
                ${itemsHtml}
            </div>
            
            <div style="text-align: center; margin-bottom: 16px; padding: 16px; background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%); border-radius: 12px;">
                <div style="font-size: 14px; color: #92400E; margin-bottom: 4px;">💰 预估返现总额</div>
                <div style="font-size: 32px; font-weight: 800; color: #DC2626;">¥${totalCashback}</div>
            </div>
            
            <div style="display: flex; flex-direction: column; gap: 12px;">
                <button onclick="bookFirstItem()" style="width: 100%; padding: 16px; background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: white; font-size: 18px; font-weight: 700; border: none; border-radius: 12px; cursor: pointer; box-shadow: 0 4px 16px rgba(16, 185, 129, 0.4);">
                    ¥${firstItemCashback} 即将到账 →
                </button>
                <button onclick="closeBookingModal()" style="width: 100%; padding: 14px; background: white; color: #666; font-size: 15px; font-weight: 600; border: 2px solid #E5E7EB; border-radius: 10px; cursor: pointer;">
                    先看攻略，稍后预订
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // 点击背景关闭
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeBookingModal();
        }
    });
    
    // 保存第一个预订项的URL
    window._firstBookingUrl = displayItems[0]?.url;
}

// 关闭预订弹窗
function closeBookingModal() {
    const modal = document.querySelector('.booking-modal');
    if (modal) {
        modal.remove();
    }
}

// 预订第一个推荐
function bookFirstItem() {
    if (window._firstBookingUrl) {
        window.open(window._firstBookingUrl, '_blank');
    }
    closeBookingModal();
}
