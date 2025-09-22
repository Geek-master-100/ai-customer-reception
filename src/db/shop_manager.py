# -*- coding: utf-8 -*-
"""
店铺数据管理类
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from .entities import PlatformShop, ShopType

class ShopManager:
    """店铺数据管理器"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.shops_file = data_dir / "shops.json"
        self._shops_cache: Dict[str, List[PlatformShop]] = {}
        self._load_shops()
    
    def _load_shops(self):
        """从文件加载店铺数据"""
        if not self.shops_file.exists():
            return
        
        try:
            with open(self.shops_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for platform, shops_list in data.items():
                self._shops_cache[platform] = [
                    PlatformShop.from_dict(shop_data) for shop_data in shops_list
                ]
        except Exception as e:
            print(f"加载店铺数据失败: {e}")
    
    def _save_shops(self):
        """保存店铺数据到文件"""
        try:
            data = {}
            for platform, shops in self._shops_cache.items():
                data[platform] = [shop.to_dict() for shop in shops]
            
            with open(self.shops_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存店铺数据失败: {e}")
    
    def get_platform_shops(self, platform: str) -> List[PlatformShop]:
        """获取指定平台的店铺列表"""
        return self._shops_cache.get(platform, [])
    
    def add_shop(self, platform: str, shop: PlatformShop):
        """添加新店铺"""
        if platform not in self._shops_cache:
            self._shops_cache[platform] = []
        
        # 检查是否已存在
        existing = self.find_shop(platform, shop.webview_id)
        if existing is None:
            shop.platform = platform
            self._shops_cache[platform].append(shop)
            self._save_shops()
    
    def update_shop(self, platform: str, shop: PlatformShop):
        """更新店铺信息"""
        shops = self._shops_cache.get(platform, [])
        for i, existing_shop in enumerate(shops):
            if existing_shop.webview_id == shop.webview_id:
                shop.platform = platform
                shops[i] = shop
                self._save_shops()
                return True
        return False
    
    def remove_shop(self, platform: str, webview_id: str):
        """删除店铺"""
        shops = self._shops_cache.get(platform, [])
        for i, shop in enumerate(shops):
            if shop.webview_id == webview_id:
                shops.pop(i)
                self._save_shops()
                return True
        return False
    
    def find_shop(self, platform: str, webview_id: str) -> Optional[PlatformShop]:
        """查找指定的店铺"""
        shops = self._shops_cache.get(platform, [])
        for shop in shops:
            if shop.webview_id == webview_id:
                return shop
        return None
    
    def get_all_shops(self) -> Dict[str, List[PlatformShop]]:
        """获取所有店铺数据"""
        return self._shops_cache.copy() 