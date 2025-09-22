# -*- coding: utf-8 -*-
"""
店铺列表控件
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QScrollArea, QFrame, QGridLayout, QSizePolicy)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap, QIcon
from typing import List, Callable, Optional
import requests
from io import BytesIO

from ..db.entities import PlatformShop


class ShopCard(QFrame):
    """店铺卡片"""
    
    clicked = pyqtSignal()
    
    def __init__(self, shop: PlatformShop, parent=None):
        super().__init__(parent)
        self.shop = shop
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            ShopCard {
                border: 1px solid #d2d2d7;
                border-radius: 12px;
                padding: 12px;
                margin: 8px;
                background-color: #ffffff;
            }
            ShopCard:hover {
                border-color: #007acc;
                background-color: #f0f8ff;
                transform: scale(1.02);
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 头像
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(60, 60)
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ccc;
                border-radius: 30px;
                background-color: #f5f5f5;
            }
        """)
        self._load_avatar()
        
        # 用户名
        self.username_label = QLabel(self.shop.user_name or "未知用户")
        self.username_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.username_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #333;")
        
        # 店铺名
        self.mallname_label = QLabel(self.shop.mall_name or "未知店铺")
        self.mallname_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mallname_label.setStyleSheet("color: #666; font-size: 14px;")
        self.mallname_label.setWordWrap(True)
        
        layout.addWidget(self.avatar_label)
        layout.addWidget(self.username_label)
        layout.addWidget(self.mallname_label)
        
        self.setFixedSize(150, 180)
        
    def _load_avatar(self):
        """加载头像"""
        if self.shop.avatar:
            try:
                response = requests.get(self.shop.avatar, timeout=5)
                if response.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    scaled_pixmap = pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, 
                                                Qt.TransformationMode.SmoothTransformation)
                    self.avatar_label.setPixmap(scaled_pixmap)
                    return
            except Exception as e:
                print(f"加载头像失败: {e}")
        
        # 默认头像
        self.avatar_label.setText("👤")
        self.avatar_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ccc;
                border-radius: 30px;
                background-color: #f5f5f5;
                font-size: 24px;
            }
        """)
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class AddNewCard(QFrame):
    """添加新店铺卡片"""
    
    clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            AddNewCard {
                border: 2px dashed #d2d2d7;
                border-radius: 12px;
                background-color: #ffffff;
            }
            AddNewCard:hover {
                border-color: #007acc;
                background-color: #f0f8ff;
                transform: scale(1.02);
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 加号图标
        icon_label = QLabel("+")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; color: #007acc; font-weight: bold;")
        
        # 文本
        text_label = QLabel("添加新店铺")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("color: #007acc; font-size: 14px; font-weight: bold;")
        
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        
        self.setFixedSize(150, 180)
        
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class ShopListWidget(QWidget):
    """店铺列表控件"""
    
    shop_selected = pyqtSignal(PlatformShop)
    add_new_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.shops: List[PlatformShop] = []
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 标题
        title_label = QLabel("选择店铺账号")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 15px; color: #333;")
        layout.addWidget(title_label)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 内容容器
        self.content_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.content_widget.setLayout(self.grid_layout)
        scroll_area.setWidget(self.content_widget)
        
        layout.addWidget(scroll_area)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        self.load_all_btn = QPushButton("加载所有店铺")
        self.load_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #005c99;
            }
            QPushButton:pressed {
                background-color: #004080;
            }
        """)
        self.load_all_btn.clicked.connect(self._load_all_shops)
        
        button_layout.addStretch()
        button_layout.addWidget(self.load_all_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
    def set_shops(self, shops: List[PlatformShop]):
        """设置店铺列表"""
        self.shops = shops
        self._refresh_ui()
        
    def _refresh_ui(self):
        """刷新UI"""
        # 清空现有内容
        for i in reversed(range(self.grid_layout.count())):
            child = self.grid_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 添加店铺卡片
        row, col = 0, 0
        cols = 4  # 每行4个卡片
        
        for shop in self.shops:
            card = ShopCard(shop)
            card.clicked.connect(lambda s=shop: self.shop_selected.emit(s))
            self.grid_layout.addWidget(card, row, col)
            
            col += 1
            if col >= cols:
                col = 0
                row += 1
        
        # 添加"添加新店铺"卡片
        add_card = AddNewCard()
        add_card.clicked.connect(self.add_new_requested.emit)
        self.grid_layout.addWidget(add_card, row, col)
        
        # 调整内容大小
        self.content_widget.adjustSize()
        
    def _load_all_shops(self):
        """加载所有店铺"""
        for shop in self.shops:
            self.shop_selected.emit(shop) 