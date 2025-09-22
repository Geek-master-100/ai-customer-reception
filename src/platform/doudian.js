// 抖店平台消息监控脚本
(function() {
    // 获取用户信息
    function getCurrentUser() {
        // 抖店的用户信息API可能需要根据实际页面调整
        try {
            // 这里需要根据抖店实际的API或页面元素来获取用户信息
            const userInfo = {
                userName: "抖店用户",
                mallName: "抖店店铺",
                userId: "doudian_user_id",
                mallId: "doudian_mall_id",
                avatar: ""
            };
            
            window.pywebview.api.post_message({
                type: 'currentuser',
                response: JSON.stringify(userInfo)
            });
        } catch (e) {
            console.error('获取抖店用户信息失败:', e);
        }
    }
    
    // 监控新消息
    function checkNewMessages() {
        try {
            // 根据抖店页面的实际消息提示元素来检测新消息
            const messageIndicators = document.querySelectorAll('.message-notify, .unread-count, [class*="unread"]');
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
            console.error('检查抖店新消息失败:', e);
        }
    }
    
    // 初始化
    setTimeout(getCurrentUser, 2000);
    setInterval(checkNewMessages, 1000);
})();