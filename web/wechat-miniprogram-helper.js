/**
 * 微信小程序跳转辅助脚本
 * 检测微信环境，支持小程序跳转
 */

// 检测是否在微信环境
function isWeChat() {
    return /MicroMessenger/i.test(navigator.userAgent);
}

// 检测是否支持小程序跳转
function supportMiniProgram() {
    return isWeChat() && window.WeixinJSBridge;
}

/**
 * 跳转到美团小程序
 * @param {string} appId - 小程序AppID
 * @param {string} path - 小程序页面路径
 * @param {string} fallbackUrl - 降级H5链接
 */
function navigateToMiniProgram(appId, path, fallbackUrl) {
    if (!isWeChat()) {
        // 非微信环境，直接跳转H5
        window.location.href = fallbackUrl;
        return;
    }

    // 微信环境，尝试跳转小程序
    if (window.WeixinJSBridge) {
        window.WeixinJSBridge.invoke('launchMiniProgram', {
            userName: 'gh_870576f3c6f9',  // 小程序原始ID
            path: path,
            type: 0  // 0-正式版 1-开发版 2-体验版
        }, function(res) {
            if (res.err_msg !== 'launch_mini_program:ok') {
                // 跳转失败，降级到H5
                console.log('小程序跳转失败，降级到H5', res);
                window.location.href = fallbackUrl;
            }
        });
    } else {
        // WeixinJSBridge未加载，等待或降级
        if (document.addEventListener) {
            document.addEventListener('WeixinJSBridgeReady', function() {
                navigateToMiniProgram(appId, path, fallbackUrl);
            }, false);
        } else {
            // 等待超时，降级到H5
            window.location.href = fallbackUrl;
        }
    }
}

/**
 * 增强所有美团链接，支持小程序跳转
 */
function enhanceMeituanLinks() {
    const links = document.querySelectorAll('a[data-mp-appid]');
    
    links.forEach(link => {
        const appId = link.getAttribute('data-mp-appid');
        const path = link.getAttribute('data-mp-path');
        const fallbackUrl = link.getAttribute('href');
        
        if (appId && path) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                navigateToMiniProgram(appId, path, fallbackUrl);
            });
        }
    });
    
    console.log(`✅ 已增强 ${links.length} 个美团链接，支持小程序跳转`);
}

// 页面加载完成后自动增强链接
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', enhanceMeituanLinks);
} else {
    enhanceMeituanLinks();
}

// 导出函数（如果需要手动调用）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        isWeChat,
        supportMiniProgram,
        navigateToMiniProgram,
        enhanceMeituanLinks
    };
}
