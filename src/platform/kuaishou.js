// 快手平台消息监控脚本
(function() {
    // 获取用户信息
    function getCurrentUser() {
        try {
            // 快手的用户信息获取，需要根据实际页面调整
            const userInfo = {
                userName: "快手用户",
                mallName: "快手店铺",
                userId: "kuaishou_user_id", 
                mallId: "kuaishou_mall_id",
                avatar: ""
            };
            
            window.pywebview.api.post_message({
                type: 'currentuser',
                response: JSON.stringify(userInfo)
            });
        } catch (e) {
            console.error('获取快手用户信息失败:', e);
        }
    }
    
    // 监控新消息
    function checkNewMessages() {
        try {
            // 根据快手页面的实际消息提示元素来检测新消息
            const messageIndicators = document.querySelectorAll('.new-message, .unread-badge, [class*="unread"], [class*="new-msg"]');
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
            console.error('检查快手新消息失败:', e);
        }
    }
    
    // 初始化
    setTimeout(getCurrentUser, 2000);
    setInterval(checkNewMessages, 1000);
})(); 