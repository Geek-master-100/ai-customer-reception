# -*- coding: utf-8 -*-
"""
应用程序核心类，管理全局状态和配置
"""

import os
import json
from pathlib import Path
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from typing import Dict, List, Optional

class PdkBotApplication(QObject):
    """PdkBot应用程序核心类"""
    
    # 信号
    new_message_received = pyqtSignal(str, dict)  # 平台名, 消息数据
    shop_updated = pyqtSignal(str, dict)  # 平台名, 店铺数据
    
    def __init__(self):
        super().__init__()
        self.app_dir = Path(__file__).parent.parent.parent
        self.data_dir = self.app_dir / "data"
        self.profiles_dir = self.app_dir / "webview_profiles"
        self.platform_dir = self.app_dir / "src" / "platform"
        
        # 确保目录存在
        self.data_dir.mkdir(exist_ok=True)
        self.profiles_dir.mkdir(exist_ok=True)
        
        # 初始化配置
        self.config = self._load_config()
        
    def _load_config(self) -> dict:
        """加载应用配置"""
        config_file = self.data_dir / "config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置失败: {e}")
        
        # 默认配置
        return {
            "auto_reply": False,
            "notification": True,
            "theme": "light",
            "platforms": {
                "pdd": {"enabled": True, "name": "拼多多"},
                "doudian": {"enabled": True, "name": "抖店"},
                "kuaishou": {"enabled": True, "name": "快手"},
                "jd": {"enabled": True, "name": "京东"}
            }
        }
    
    def save_config(self):
        """保存应用配置"""
        config_file = self.data_dir / "config.json"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def get_platform_script_path(self, platform: str) -> Optional[Path]:
        """获取平台脚本路径"""
        script_path = self.platform_dir / f"{platform}.js"
        return script_path if script_path.exists() else None
    
    def get_webview_profile_path(self, profile_id: str) -> Path:
        """获取WebView配置文件路径"""
        return self.profiles_dir / profile_id
    
    def emit_new_message(self, platform: str, message_data: dict):
        """发出新消息信号"""
        self.new_message_received.emit(platform, message_data)
    
    def emit_shop_updated(self, platform: str, shop_data: dict):
        """发出店铺更新信号"""
        self.shop_updated.emit(platform, shop_data) 