# -*- coding: utf-8 -*-
"""
主窗口
"""

import sys
from pathlib import Path
from typing import Dict, Optional

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QTabWidget, QSplitter, QTreeWidget, QTreeWidgetItem,
                           QSystemTrayIcon, QMenu, QMessageBox, QStatusBar,
                           QPushButton, QLabel, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QAction, QPixmap, QFont

from ..core.application import PdkBotApplication
from ..pages.platform_page import PlatformPage
from ..db.shop_manager import ShopManager
from ..db.entities import NewMessage, PlatformShop
from .tray_notification import NotificationManager


class NavigationTree(QTreeWidget):
    """导航树控件"""
    
    platform_selected = pyqtSignal(str)  # 平台名
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setHeaderHidden(True)
        self.setRootIsDecorated(True)
        self.setIndentation(20)
        
        # 设置样式
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #ffffff;
                border: 1px solid #d2d2d7;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }
            QTreeWidget::item {
                height: 40px;
                padding: 8px 12px;
                border: none;
                font-size: 14px;
                color: #1d1d1f;
            }
            QTreeWidget::item:hover {
                background-color: #f5f5f7;
            }
            QTreeWidget::item:selected {
                background-color: #007acc;
                color: white;
                font-weight: bold;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                image: url(none);
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                image: url(none);
            }
        """)
        
        self.setup_items()
        
        # 连接信号
        self.itemClicked.connect(self.on_item_clicked)
        
    def setup_items(self):
        """设置导航项目"""
        # 首页
        home_item = QTreeWidgetItem(["🏠 首页"])
        home_item.setData(0, Qt.ItemDataRole.UserRole, "home")
        self.addTopLevelItem(home_item)
        
        # 平台列表
        platforms = [
            ("pdd", "拼多多", "🛍️"),
            ("doudian", "抖店", "📱"),
            ("kuaishou", "快手", "⚡"),
            ("jd", "京东", "🛒")
        ]
        
        for platform_id, platform_name, icon in platforms:
            item = QTreeWidgetItem([f"{icon} {platform_name}"])
            item.setData(0, Qt.ItemDataRole.UserRole, platform_id)
            self.addTopLevelItem(item)
            
        # 设置
        settings_item = QTreeWidgetItem(["⚙️ 设置"])
        settings_item.setData(0, Qt.ItemDataRole.UserRole, "settings")
        self.addTopLevelItem(settings_item)
        
        # 关于
        about_item = QTreeWidgetItem(["ℹ️ 关于"])
        about_item.setData(0, Qt.ItemDataRole.UserRole, "about")
        self.addTopLevelItem(about_item)
        
        # 默认选中首页
        self.setCurrentItem(home_item)
        
    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """导航项点击事件"""
        item_type = item.data(0, Qt.ItemDataRole.UserRole)
        if item_type:
            self.platform_selected.emit(item_type)
            
    def update_badge(self, platform: str, count: int):
        """更新消息徽章"""
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item.data(0, Qt.ItemDataRole.UserRole) == platform:
                text = item.text(0)
                # 移除现有的徽章
                if "(" in text:
                    text = text[:text.rfind("(")].strip()
                
                # 添加新徽章
                if count > 0:
                    text = f"{text} ({count})"
                    
                item.setText(0, text)
                break


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        
        self.app = PdkBotApplication()
        self.shop_manager = ShopManager(self.app.data_dir)
        self.notification_manager = NotificationManager()
        
        # 平台页面
        self.platform_pages: Dict[str, PlatformPage] = {}
        
        # 消息计数
        self.message_counts: Dict[str, int] = {}
        
        self.setup_ui()
        self.setup_system_tray()
        self.setup_platform_pages()
        self.setup_signals()
        
        # 应用全局样式
        self.apply_styles()
        
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("PdkBot - 电商客服聚合接待工具")
        self.setGeometry(100, 100, 1200, 800)
        
        # 中央控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧导航
        self.navigation_tree = NavigationTree()
        self.navigation_tree.setMaximumWidth(200)
        splitter.addWidget(self.navigation_tree)
        
        # 右侧内容区域
        self.content_widget = QTabWidget()
        self.content_widget.setTabsClosable(False)
        self.content_widget.setMovable(False)
        self.content_widget.tabBar().hide()  # 隐藏标签页栏，通过导航控制
        splitter.addWidget(self.content_widget)
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 0)  # 导航固定宽度
        splitter.setStretchFactor(1, 1)  # 内容区域自适应
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪", 2000)
        
    def setup_system_tray(self):
        """设置系统托盘"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(self, "系统托盘", "系统不支持系统托盘功能")
            return
            
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        
        # 设置图标
        icon_path = Path(__file__).parent.parent.parent / "assets" / "pdkbot.ico"
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        else:
            # 使用默认图标
            self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        # 显示/隐藏窗口
        show_action = QAction("显示窗口", self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("隐藏窗口", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        # 退出
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        
        # 托盘图标双击事件
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # 显示托盘图标
        self.tray_icon.show()
        
    def setup_platform_pages(self):
        """设置平台页面"""
        # 平台配置
        platforms_config = {
            "pdd": {
                "name": "拼多多",
                "url": "https://mms.pinduoduo.com/chat-merchant/index.html#/"
            },
            "doudian": {
                "name": "抖店", 
                "url": "https://fxg.jinritemai.com/ffa/mshop/shopIndex"
            },
            "kuaishou": {
                "name": "快手",
                "url": "https://s.kwaixiaodian.com/zone/settles/chat"
            },
            "jd": {
                "name": "京东",
                "url": "https://dongdong.jd.com/"
            }
        }
        
        # 添加首页
        home_page = self.create_home_page()
        self.content_widget.addTab(home_page, "首页")
        
        # 创建平台页面
        for platform_id, config in platforms_config.items():
            page = PlatformPage(
                platform=platform_id,
                platform_name=config["name"],
                chat_url=config["url"],
                shop_manager=self.shop_manager
            )
            
            self.platform_pages[platform_id] = page
            self.content_widget.addTab(page, config["name"])
            
        # 添加设置页面
        settings_page = self.create_settings_page()
        self.content_widget.addTab(settings_page, "设置")
        
        # 添加关于页面
        about_page = self.create_about_page()
        self.content_widget.addTab(about_page, "关于")
        
    def setup_signals(self):
        """设置信号连接"""
        # 导航选择
        self.navigation_tree.platform_selected.connect(self.on_navigation_selected)
        
        # 平台页面信号
        for platform_id, page in self.platform_pages.items():
            page.new_message_received.connect(self.on_new_message_received)
            page.shop_updated.connect(self.on_shop_updated)
            page.tab_changed.connect(self.on_tab_changed)
            
    def create_home_page(self) -> QWidget:
        """创建首页"""
        page = QWidget()
        page.setStyleSheet("background-color: #f5f5f7;")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 标题
        title = QLabel("PdkBot 电商客服聚合接待工具")
        title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #007bff;
                margin: 20px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 描述
        description = QLabel("""
        支持拼多多、抖店、快手、京东等平台的客服管理
        
        功能特色：
        • 多平台统一管理
        • 无限账号登录
        • 实时消息提醒
        • 现代化界面设计
        
        请从左侧导航栏选择要使用的平台
        """)
        description.setStyleSheet("""
            QLabel {
                font-size: 16px;
                line-height: 1.6;
                color: #1d1d1f;
                background-color: #ffffff;
                border: 1px solid #d2d2d7;
                border-radius: 12px;
                padding: 25px;
                margin: 20px;
            }
        """)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title)
        layout.addWidget(description)
        
        return page
        
    def create_settings_page(self) -> QWidget:
        """创建设置页面"""
        page = QWidget()
        page.setStyleSheet("background-color: #f5f5f7;")
        layout = QVBoxLayout(page)
        
        title = QLabel("设置")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 15px; color: #1d1d1f;")
        
        content = QLabel("设置功能开发中...")
        content.setStyleSheet("font-size: 16px; color: #86868b; margin: 15px;")
        
        layout.addWidget(title)
        layout.addWidget(content)
        layout.addStretch()
        
        return page
        
    def create_about_page(self) -> QWidget:
        """创建关于页面"""
        page = QWidget()
        page.setStyleSheet("background-color: #f5f5f7;")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("关于 PdkBot")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #007acc;
                margin: 15px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        info = QLabel("""
        版本：1.0.0
        
        PdkBot 是一款用Python开发的电商客服聚合接待工具
        
        ⚠️ 注意：本项目仅供学习与交流使用
        """)
        info.setStyleSheet("""
            QLabel {
                font-size: 16px;
                line-height: 1.6;
                color: #1d1d1f;
                background-color: #ffffff;
                border: 1px solid #d2d2d7;
                border-radius: 12px;
                padding: 25px;
                margin: 20px;
            }
        """)
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title)
        layout.addWidget(info)
        
        return page
        
    def apply_styles(self):
        """应用全局样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f7;
                font-family: "Helvetica Neue", "Arial", sans-serif;
                font-size: 14px;
            }
            QTabWidget::pane {
                border: none;
                background-color: #f5f5f7;
            }
            QTabWidget QWidget {
                background-color: #f5f5f7;
            }
            QLabel {
                color: #1d1d1f;
            }
            QPushButton {
                font-family: "Helvetica Neue", "Arial", sans-serif;
            }
            QWidget {
                background-color: #f5f5f7;
            }
        """)
        
    def on_navigation_selected(self, item_type: str):
        """导航选择事件"""
        if item_type == "home":
            self.content_widget.setCurrentIndex(0)
        elif item_type in self.platform_pages:
            # 找到对应的标签页索引
            for i in range(self.content_widget.count()):
                widget = self.content_widget.widget(i)
                if widget == self.platform_pages[item_type]:
                    self.content_widget.setCurrentIndex(i)
                    break
        elif item_type == "settings":
            self.content_widget.setCurrentIndex(self.content_widget.count() - 2)
        elif item_type == "about":
            self.content_widget.setCurrentIndex(self.content_widget.count() - 1)
            
    def on_new_message_received(self, platform: str, new_msg: NewMessage):
        """处理新消息"""
        if new_msg.has_new_message and new_msg.new_message_count > 0:
            # 更新消息计数
            self.message_counts[platform] = new_msg.new_message_count
            
            # 更新导航徽章
            self.navigation_tree.update_badge(platform, new_msg.new_message_count)
            
            # 显示系统通知
            platform_names = {
                "pdd": "拼多多",
                "doudian": "抖店", 
                "kuaishou": "快手",
                "jd": "京东"
            }
            platform_name = platform_names.get(platform, platform)
            
            notification = self.notification_manager.show_notification(
                f"{platform_name} 新消息",
                f"您有 {new_msg.new_message_count} 条新消息",
                duration=5000
            )
            notification.clicked.connect(lambda: self.on_notification_clicked(platform))
            
        else:
            # 清除消息计数
            self.message_counts.pop(platform, None)
            self.navigation_tree.update_badge(platform, 0)
            
    def on_notification_clicked(self, platform: str):
        """通知点击事件"""
        # 显示窗口并切换到对应平台
        self.show_window()
        self.on_navigation_selected(platform)
        
    def on_shop_updated(self, platform: str, shop: PlatformShop):
        """店铺更新事件"""
        self.status_bar.showMessage(f"{platform} 店铺信息已更新：{shop.user_name}", 3000)
        
    def on_tab_changed(self, platform: str, tab_title: str):
        """标签页改变事件"""
        self.status_bar.showMessage(f"当前：{platform} - {tab_title}", 5000)
        
    def show_window(self):
        """显示窗口"""
        self.show()
        self.raise_()
        self.activateWindow()
        
    def tray_icon_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show_window()
                
    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            self.quit_application()
            
    def quit_application(self):
        """退出应用程序"""
        self.notification_manager.clear_all()
        self.app.save_config()
        sys.exit(0) 