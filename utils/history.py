#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置历史记录管理
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional

HISTORY_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'history')


class ConfigHistory:
    """配置历史记录管理"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.history_dir = HISTORY_DIR
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir)
    
    def save_config(self, name: str, device_type: str, config_content: str, 
                    description: str = "") -> str:
        """保存配置到历史"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{device_type}_{timestamp}.json"
        filepath = os.path.join(self.history_dir, filename)
        
        record = {
            "id": timestamp,
            "name": name,
            "device_type": device_type,
            "description": description,
            "config": config_content,
            "created_at": datetime.now().isoformat(),
            "file_path": filepath
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(record, f, indent=2, ensure_ascii=False)
            return filepath
        except Exception as e:
            print(f"保存历史记录失败: {e}")
            return ""
    
    def list_history(self, device_type: str = None, limit: int = 50) -> List[Dict]:
        """列出历史记录"""
        records = []
        
        try:
            files = [f for f in os.listdir(self.history_dir) if f.endswith('.json')]
            files.sort(reverse=True)
            
            for filename in files[:limit]:
                filepath = os.path.join(self.history_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        record = json.load(f)
                    
                    if device_type is None or record.get('device_type') == device_type:
                        records.append({
                            "id": record.get('id'),
                            "name": record.get('name'),
                            "device_type": record.get('device_type'),
                            "description": record.get('description', ''),
                            "created_at": record.get('created_at'),
                            "file_path": filepath
                        })
                except:
                    continue
        except Exception as e:
            print(f"读取历史记录失败: {e}")
        
        return records
    
    def load_config(self, record_id: str) -> Optional[Dict]:
        """加载配置"""
        try:
            for filename in os.listdir(self.history_dir):
                if record_id in filename:
                    filepath = os.path.join(self.history_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
        return None
    
    def delete_config(self, record_id: str) -> bool:
        """删除历史记录"""
        try:
            for filename in os.listdir(self.history_dir):
                if record_id in filename:
                    filepath = os.path.join(self.history_dir, filename)
                    os.remove(filepath)
                    return True
        except Exception as e:
            print(f"删除记录失败: {e}")
        return False
    
    def clear_old_history(self, days: int = 30) -> int:
        """清理旧历史记录"""
        from datetime import timedelta
        count = 0
        cutoff = datetime.now() - timedelta(days=days)
        
        try:
            for filename in os.listdir(self.history_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.history_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            record = json.load(f)
                        created = datetime.fromisoformat(record.get('created_at', ''))
                        if created < cutoff:
                            os.remove(filepath)
                            count += 1
                    except:
                        continue
        except Exception as e:
            print(f"清理历史记录失败: {e}")
        
        return count
