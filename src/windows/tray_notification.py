# -*- coding: utf-8 -*-
"""
托盘通知窗口
"""

from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                           QFrame, QPushButton, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QPixmap, QIcon

class TrayNotification(QWidget):
    """托盘通知窗口"""
    
    clicked = pyqtSignal()
    
    def __init__(self, title: str, message: str, duration: int = 3000, parent=None):
        super().__init__(parent)
        
        self.title = title
        self.message = message
        self.duration = duration
        
        self.setup_ui()
        self.setup_animation()
        
        # 自动关闭定时器
        if duration > 0:
            QTimer.singleShot(duration, self.hide_notification)
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 设置窗口大小和位置
        self.setFixedSize(300, 100)
        self.move_to_bottom_right()
        
        # 主容器
        main_frame = QFrame()
        main_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(50, 50, 50, 240);
                border-radius: 10px;
                border: 1px solid rgba(70, 70, 70, 200);
            }
        """)
        
        layout = QVBoxLayout(main_frame)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # 标题
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 14px;
                background: transparent;
            }
        """)
        title_label.setWordWrap(True)
        
        # 消息内容
        message_label = QLabel(self.message)
        message_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 12px;
                background: transparent;
            }
        """)
        message_label.setWordWrap(True)
        
        # 关闭按钮
        close_button = QPushButton("×")
        close_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #999;
                font-size: 18px;
                font-weight: bold;
                min-width: 20px;
                max-width: 20px;
                min-height: 20px;
                max-height: 20px;
            }
            QPushButton:hover {
                color: white;
                background-color: rgba(255, 255, 255, 50);
                border-radius: 10px;
            }
        """)
        close_button.clicked.connect(self.hide_notification)
        
        # 顶部布局（标题和关闭按钮）
        top_layout = QHBoxLayout()
        top_layout.addWidget(title_label)
        top_layout.addStretch()
        top_layout.addWidget(close_button)
        
        layout.addLayout(top_layout)
        layout.addWidget(message_label)
        layout.addStretch()
        
        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(main_frame)
        
        # 点击事件
        self.mousePressEvent = self._on_click
        
    def setup_animation(self):
        """设置动画"""
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        # 淡入动画
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 淡出动画
        self.fade_out_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_animation.setDuration(300)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_out_animation.finished.connect(self.close)
        
    def move_to_bottom_right(self):
        """移动到屏幕右下角"""
        screen = self.screen().availableGeometry()
        self.move(screen.width() - self.width() - 20, screen.height() - self.height() - 20)
        
    def show_notification(self):
        """显示通知"""
        self.show()
        self.fade_in_animation.start()
        
    def hide_notification(self):
        """隐藏通知"""
        self.fade_out_animation.start()
        
    def _on_click(self, event):
        """点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
            self.hide_notification()


class NotificationManager:
    """通知管理器"""
    
    def __init__(self):
        self.notifications = []
        self.max_notifications = 5
        
    def show_notification(self, title: str, message: str, duration: int = 3000) -> TrayNotification:
        """显示通知"""
        # 限制同时显示的通知数量
        if len(self.notifications) >= self.max_notifications:
            # 移除最旧的通知
            old_notification = self.notifications.pop(0)
            old_notification.hide_notification()
            
        # 创建新通知
        notification = TrayNotification(title, message, duration)
        
        # 调整位置（避免重叠）
        self._adjust_notification_positions()
        
        # 添加到列表
        self.notifications.append(notification)
        
        # 显示通知
        notification.show_notification()
        
        # 监听关闭事件
        notification.destroyed.connect(lambda: self._remove_notification(notification))
        
        return notification
        
    def _adjust_notification_positions(self):
        """调整通知位置，避免重叠"""
        for i, notification in enumerate(self.notifications):
            if notification.isVisible():
                screen = notification.screen().availableGeometry()
                y_offset = (notification.height() + 10) * i
                notification.move(
                    screen.width() - notification.width() - 20,
                    screen.height() - notification.height() - 20 - y_offset
                )
                
    def _remove_notification(self, notification):
        """从列表中移除通知"""
        if notification in self.notifications:
            self.notifications.remove(notification)
            
    def clear_all(self):
        """清除所有通知"""
        for notification in self.notifications:
            notification.hide_notification()
        self.notifications.clear() 