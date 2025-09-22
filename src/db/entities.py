# -*- coding: utf-8 -*-
"""
数据库实体类
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from enum import Enum
import json

class ShopType(Enum):
    """店铺类型枚举"""
    PINDUODUO = "pdd"
    DOUDIAN = "doudian"
    KUAISHOU = "kuaishou"
    JD = "jd"

@dataclass
class PlatformShop:
    """平台店铺信息"""
    user_name: str = ""
    mall_name: str = ""
    user_id: str = ""
    mall_id: str = ""
    avatar: str = ""
    webview_id: str = ""
    platform: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlatformShop':
        return cls(**data)

@dataclass
class NewMessage:
    """新消息数据"""
    has_new_message: bool = False
    new_message_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NewMessage':
        return cls(**data)

@dataclass
class PlatformResponse:
    """平台响应数据"""
    type: str
    response: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlatformResponse':
        return cls(**data)

@dataclass
class ReceiveMessageResponse:
    """接收消息响应"""
    pdd_message: Optional[Dict] = None
    payload: Optional[Dict] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReceiveMessageResponse':
        return cls(**data) 