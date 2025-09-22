# -*- coding: utf-8 -*-
"""
WebView控件，用于嵌入电商平台网页
"""

import json
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, Callable

from PyQt6.QtCore import QUrl, pyqtSignal, QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineScript, QWebEngineProfile, QWebEnginePage

from ..db.entities import PlatformShop, NewMessage, PlatformResponse


class PlatformWebView(QWebEngineView):
    """平台WebView控件"""
    
    # 信号
    user_info_received = pyqtSignal(PlatformShop)  # 用户信息接收
    new_message_received = pyqtSignal(NewMessage)  # 新消息接收
    message_received = pyqtSignal(dict)  # 普通消息接收
    
    def __init__(self, platform: str, webview_id: str = None, parent=None):
        super().__init__(parent)
        
        self.platform = platform
        self.webview_id = webview_id or str(uuid.uuid4()).replace("-", "")
        self._script_injected = False
        
        # 设置WebEngine配置文件
        self._setup_profile()
        
        # 设置页面
        self._setup_page()
        
        # 连接信号
        self.page().loadFinished.connect(self._on_load_finished)
    
    def _setup_profile(self):
        """设置WebEngine配置文件"""
        # 为每个WebView创建独立的配置文件
        profile_path = Path.cwd() / "webview_profiles" / self.webview_id
        profile_path.mkdir(parents=True, exist_ok=True)
        
        # 创建配置文件
        profile = QWebEngineProfile(str(profile_path), self)
        page = QWebEnginePage(profile, self)
        self.setPage(page)
    
    def _setup_page(self):
        """设置页面"""
        # 添加JavaScript桥接对象
        self.page().runJavaScript("""
            window.pywebview = {
                api: {
                    post_message: function(data) {
                        // 通过控制台输出消息，然后在Python中捕获
                        console.log('PYWEBVIEW_MESSAGE:' + JSON.stringify(data));
                    }
                }
            };
        """)
        
        # 监听控制台消息
        self.page().javaScriptConsoleMessage = self._handle_console_message
    
    def _handle_console_message(self, level, message, line, source):
        """处理控制台消息"""
        if message.startswith('PYWEBVIEW_MESSAGE:'):
            try:
                data_json = message[18:]  # 去除前缀
                data = json.loads(data_json)
                self._handle_platform_message(data)
            except Exception as e:
                print(f"处理平台消息失败: {e}")
    
    def _handle_platform_message(self, data: Dict[str, Any]):
        """处理平台消息"""
        try:
            message_type = data.get('type', '')
            response_str = data.get('response', '{}')
            response_data = json.loads(response_str) if isinstance(response_str, str) else response_str
            
            if message_type == 'currentuser':
                # 用户信息
                shop = PlatformShop(
                    user_name=response_data.get('userName', ''),
                    mall_name=response_data.get('mallName', ''),
                    user_id=response_data.get('userId', ''),
                    mall_id=response_data.get('mallId', ''),
                    avatar=response_data.get('avatar', ''),
                    webview_id=self.webview_id,
                    platform=self.platform
                )
                self.user_info_received.emit(shop)
                
            elif message_type == 'newmessage':
                # 新消息
                new_msg = NewMessage(
                    has_new_message=response_data.get('hasNewMessage', False),
                    new_message_count=response_data.get('newMessageCount', 0)
                )
                self.new_message_received.emit(new_msg)
                
            elif message_type == 'receiveMessage':
                # 接收消息
                self.message_received.emit(response_data)
                
        except Exception as e:
            print(f"处理平台消息失败: {e}")
    
    def _on_load_finished(self, success: bool):
        """页面加载完成"""
        if success and not self._script_injected:
            self._inject_platform_script()
    
    def _inject_platform_script(self):
        """注入平台脚本"""
        script_path = Path(__file__).parent.parent / "platform" / f"{self.platform}.js"
        if not script_path.exists():
            print(f"平台脚本不存在: {script_path}")
            return
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            # 延迟注入脚本
            QTimer.singleShot(2000, lambda: self._do_inject_script(script_content))
            
        except Exception as e:
            print(f"读取平台脚本失败: {e}")
    
    def _do_inject_script(self, script_content: str):
        """执行脚本注入"""
        try:
            self.page().runJavaScript(script_content)
            self._script_injected = True
            print(f"已注入{self.platform}平台脚本")
        except Exception as e:
            print(f"注入平台脚本失败: {e}")
    
    def load_platform_url(self, url: str):
        """加载平台URL"""
        self.load(QUrl(url))
    
    def execute_script(self, script: str, callback: Callable = None):
        """执行JavaScript脚本"""
        if callback:
            self.page().runJavaScript(script, callback)
        else:
            self.page().runJavaScript(script) 