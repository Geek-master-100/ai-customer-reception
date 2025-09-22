# -*- coding: utf-8 -*-
"""
平台页面，管理特定平台的WebView标签页
"""

import uuid
from typing import Dict, List, Optional

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                           QStackedWidget, QMessageBox, QPushButton, QLabel)
from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QPixmap

from ..controls.webview_widget import PlatformWebView
from ..controls.shop_list_widget import ShopListWidget
from ..db.entities import PlatformShop, NewMessage
from ..db.shop_manager import ShopManager


class PlatformTabWidget(QTabWidget):
    """平台标签页控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.close_tab)
        
        # 设置样式
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                border: 1px solid #c0c0c0;
                border-bottom-color: #c2c7cb;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 120px;
                padding: 8px 12px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-color: #007acc;
                border-bottom-color: white;
            }
            QTabBar::tab:hover {
                background-color: #e0e0e0;
            }
        """)
    
    def close_tab(self, index: int):
        """关闭标签页"""
        if index >= 0:
            widget = self.widget(index)
            if widget:
                widget.deleteLater()
            self.removeTab(index)


class PlatformPage(QWidget):
    """平台页面"""
    
    # 信号
    new_message_received = pyqtSignal(str, NewMessage)  # 平台名, 新消息
    shop_updated = pyqtSignal(str, PlatformShop)  # 平台名, 店铺信息
    tab_changed = pyqtSignal(str, str)  # 平台名, 标签页标题
    
    def __init__(self, platform: str, platform_name: str, chat_url: str, shop_manager: ShopManager, parent=None):
        super().__init__(parent)
        
        self.platform = platform
        self.platform_name = platform_name
        self.chat_url = chat_url
        self.shop_manager = shop_manager
        
        # 存储WebView实例
        self.webviews: Dict[str, PlatformWebView] = {}
        self.webview_tabs: Dict[str, int] = {}  # webview_id -> tab_index
        
        self.setup_ui()
        self.load_saved_shops()
        
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 使用堆栈布局切换店铺选择和标签页
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # 店铺选择页面
        self.shop_list_widget = ShopListWidget()
        self.shop_list_widget.shop_selected.connect(self.load_shop)
        self.shop_list_widget.add_new_requested.connect(self.create_new_shop)
        self.stacked_widget.addWidget(self.shop_list_widget)
        
        # 标签页页面
        self.tab_widget = PlatformTabWidget()
        self.tab_widget.tabCloseRequested.connect(self.close_shop_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # 添加返回按钮到标签页
        tab_page = QWidget()
        tab_layout = QVBoxLayout(tab_page)
        
        # 顶部工具栏
        toolbar = QHBoxLayout()
        self.back_button = QPushButton("← 返回店铺选择")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                padding: 10px 16px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        self.back_button.clicked.connect(self.show_shop_list)
        
        toolbar.addWidget(self.back_button)
        toolbar.addStretch()
        
        tab_layout.addLayout(toolbar)
        tab_layout.addWidget(self.tab_widget)
        
        self.stacked_widget.addWidget(tab_page)
        
        # 默认显示店铺选择
        self.stacked_widget.setCurrentIndex(0)
        
    def load_saved_shops(self):
        """加载已保存的店铺"""
        shops = self.shop_manager.get_platform_shops(self.platform)
        self.shop_list_widget.set_shops(shops)
        
    def show_shop_list(self):
        """显示店铺选择页面"""
        self.stacked_widget.setCurrentIndex(0)
        self.load_saved_shops()  # 刷新店铺列表
        
    def show_tab_widget(self):
        """显示标签页页面"""
        self.stacked_widget.setCurrentIndex(1)
        
    def load_shop(self, shop: PlatformShop):
        """加载店铺"""
        # 检查是否已经打开
        if shop.webview_id in self.webviews:
            # 切换到对应标签页
            tab_index = self.webview_tabs[shop.webview_id]
            self.tab_widget.setCurrentIndex(tab_index)
            self.show_tab_widget()
            return
            
        # 创建新的WebView
        webview = PlatformWebView(self.platform, shop.webview_id)
        webview.user_info_received.connect(self.on_user_info_received)
        webview.new_message_received.connect(self.on_new_message_received)
        webview.message_received.connect(self.on_message_received)
        
        # 添加到标签页
        tab_title = shop.user_name or f"新{self.platform_name}账号"
        tab_index = self.tab_widget.addTab(webview, tab_title)
        
        # 存储引用
        self.webviews[shop.webview_id] = webview
        self.webview_tabs[shop.webview_id] = tab_index
        
        # 加载页面
        webview.load_platform_url(self.chat_url)
        
        # 切换到新标签页
        self.tab_widget.setCurrentIndex(tab_index)
        self.show_tab_widget()
        
    def create_new_shop(self):
        """创建新店铺"""
        # 生成新的webview_id
        webview_id = str(uuid.uuid4()).replace("-", "")
        
        # 创建临时店铺对象
        temp_shop = PlatformShop(
            webview_id=webview_id,
            platform=self.platform,
            user_name=f"新{self.platform_name}账号"
        )
        
        self.load_shop(temp_shop)
        
    def close_shop_tab(self, index: int):
        """关闭店铺标签页"""
        widget = self.tab_widget.widget(index)
        if isinstance(widget, PlatformWebView):
            webview_id = widget.webview_id
            
            # 从字典中移除
            if webview_id in self.webviews:
                del self.webviews[webview_id]
            if webview_id in self.webview_tabs:
                del self.webview_tabs[webview_id]
                
            # 更新其他标签页的索引
            for vid, idx in list(self.webview_tabs.items()):
                if idx > index:
                    self.webview_tabs[vid] = idx - 1
        
        # 关闭标签页
        self.tab_widget.removeTab(index)
        
        # 如果没有标签页了，返回店铺选择
        if self.tab_widget.count() == 0:
            self.show_shop_list()
            
    def on_tab_changed(self, index: int):
        """标签页改变事件"""
        if index >= 0:
            widget = self.tab_widget.widget(index)
            if isinstance(widget, PlatformWebView):
                tab_title = self.tab_widget.tabText(index)
                self.tab_changed.emit(self.platform, tab_title)
    
    def on_user_info_received(self, shop: PlatformShop):
        """接收到用户信息"""
        # 保存到数据库
        self.shop_manager.add_shop(self.platform, shop)
        
        # 更新标签页标题
        if shop.webview_id in self.webview_tabs:
            tab_index = self.webview_tabs[shop.webview_id]
            self.tab_widget.setTabText(tab_index, shop.user_name)
            
        # 发出信号
        self.shop_updated.emit(self.platform, shop)
        
    def on_new_message_received(self, new_msg: NewMessage):
        """接收到新消息"""
        # 查找发送消息的WebView
        sender = self.sender()
        if isinstance(sender, PlatformWebView):
            webview_id = sender.webview_id
            
            # 更新标签页显示（添加未读消息提示）
            if webview_id in self.webview_tabs:
                tab_index = self.webview_tabs[webview_id]
                tab_text = self.tab_widget.tabText(tab_index)
                
                if new_msg.has_new_message and new_msg.new_message_count > 0:
                    # 添加未读消息数量
                    if not tab_text.endswith(")"):
                        tab_text = f"{tab_text} ({new_msg.new_message_count})"
                    else:
                        # 更新数量
                        base_text = tab_text[:tab_text.rfind("(")].strip()
                        tab_text = f"{base_text} ({new_msg.new_message_count})"
                else:
                    # 移除未读消息提示
                    if "(" in tab_text:
                        tab_text = tab_text[:tab_text.rfind("(")].strip()
                        
                self.tab_widget.setTabText(tab_index, tab_text)
                
            # 发出信号
            self.new_message_received.emit(self.platform, new_msg)
    
    def on_message_received(self, message_data: dict):
        """接收到普通消息"""
        # 可以在这里处理具体的消息内容
        print(f"{self.platform} 收到消息: {message_data}")
        
    def get_current_webview(self) -> Optional[PlatformWebView]:
        """获取当前WebView"""
        current_widget = self.tab_widget.currentWidget()
        if isinstance(current_widget, PlatformWebView):
            return current_widget
        return None 