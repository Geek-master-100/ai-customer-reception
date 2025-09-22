#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PdkBot - 电商客服聚合接待工具
支持拼多多、抖店、快手、京东等平台的客服管理
"""

import sys
import os
import json
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QDir
from PyQt6.QtGui import QIcon

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.windows.main_window import MainWindow
from src.core.application import PdkBotApplication

def main():
    """主入口函数"""
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("PdkBot")
    app.setApplicationDisplayName("电商客服聚合接待工具")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("PdkBot")
    
    # 设置应用图标
    icon_path = project_root / "assets" / "pdkbot.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # 创建应用程序实例
    pdk_app = PdkBotApplication()
    
    # 创建主窗口
    main_window = MainWindow()
    main_window.show()
    
    # 运行应用程序
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 