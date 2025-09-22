// 京东平台消息监控脚本
(function() {
    // 获取用户信息
    function getCurrentUser() {
        try {
            // 京东的用户信息获取，需要根据实际页面调整
            const userInfo = {
                userName: "京东用户",
                mallName: "京东店铺", 
                userId: "jd_user_id",
                mallId: "jd_mall_id",
                avatar: ""
            };
            
            window.pywebview.api.post_message({
                type: 'currentuser',
                response: JSON.stringify(userInfo)
            });
        } catch (e) {
            console.error('获取京东用户信息失败:', e);
        }
    }
    
    // 监控新消息
    function checkNewMessages() {
        try {
            // 根据京东页面的实际消息提示元素来检测新消息
            const messageIndicators = document.querySelectorAll('.new-msg, .msg-count, [class*="new"], [class*="unread"]');
            let newMessageCount = 0;
            
            messageIndicators.forEach(indicator => {
                const text = indicator.textContent.trim();
                const count = parseInt(text) || 0;
                newMessageCount += count;
            });
            
            window.pywebview.api.post_message({
                type: 'newmessage',
                response: JSON.stringify({
                    hasNewMessage: newMessageCount > 0,
                    newMessageCount: newMessageCount
                })
            });
        } catch (e) {
            console.error('检查京东新消息失败:', e);
        }
    }
    
    // 初始化
    setTimeout(getCurrentUser, 2000);
    setInterval(checkNewMessages, 1000);
})();