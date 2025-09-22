#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PdkBot Python版启动脚本
提供依赖检查和友好的错误提示
"""

import sys
import subprocess
import os
from pathlib import Path


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print(f"   当前版本: {sys.version}")
        print("   请升级Python版本后重试")
        return False
    else:
        print(f"✅ Python版本检查通过: {sys.version.split()[0]}")
        return True


def check_dependencies():
    """检查依赖包"""
    required_packages = ['PyQt6', 'PyQt6-WebEngine', 'requests', 'beautifulsoup4', 'plyer']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PyQt6':
                import PyQt6
            elif package == 'PyQt6-WebEngine':
                import PyQt6.QtWebEngineWidgets
            elif package == 'requests':
                import requests
            elif package == 'beautifulsoup4':
                import bs4
            elif package == 'plyer':
                import plyer
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\n📦 请运行以下命令安装依赖:")
        print("   pip install -r requirements.txt")
        return False
    else:
        print("✅ 依赖包检查通过")
        return True


def main():
    """主函数"""
    print("🚀 PdkBot Python版启动器")
    print("=" * 40)
    
    # 检查是否在正确的目录
    if not Path("main.py").exists():
        print("❌ 错误: 请在pdkbot-python目录中运行此脚本")
        print("   正确用法:")
        print("   cd pdkbot-python")
        print("   python run.py")
        sys.exit(1)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    print("=" * 40)
    print("🎯 启动PdkBot应用程序...")
    
    try:
        # 导入并运行主程序
        from main import main as app_main
        sys.exit(app_main())
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("   请确保所有文件都在正确的位置")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 