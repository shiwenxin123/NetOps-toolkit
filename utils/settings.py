#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
系统设置模块
"""

import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'settings.json')

DEFAULT_SETTINGS = {
    "theme": "light",
    "language": "zh_CN",
    "default_device": "huawei",
    "default_timeout": 2,
    "default_ping_count": 4,
    "default_port_timeout": 1,
    "auto_save": True,
    "show_toolbar": True,
    "window_geometry": None,
    "recent_files": [],
    "recent_hosts": []
}


class Settings:
    """系统设置管理"""
    
    _instance = None
    _settings = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance
    
    def _load(self):
        """加载设置"""
        try:
            config_dir = os.path.dirname(SETTINGS_FILE)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    self._settings = json.load(f)
            else:
                self._settings = DEFAULT_SETTINGS.copy()
                self._save()
        except Exception as e:
            print(f"加载设置失败: {e}")
            self._settings = DEFAULT_SETTINGS.copy()
    
    def _save(self):
        """保存设置"""
        try:
            config_dir = os.path.dirname(SETTINGS_FILE)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存设置失败: {e}")
    
    def get(self, key, default=None):
        """获取设置项"""
        return self._settings.get(key, default)
    
    def set(self, key, value):
        """设置项"""
        self._settings[key] = value
        self._save()
    
    def get_all(self):
        """获取所有设置"""
        return self._settings.copy()
    
    def reset(self):
        """重置为默认设置"""
        self._settings = DEFAULT_SETTINGS.copy()
        self._save()
    
    def add_recent_file(self, filepath):
        """添加最近文件"""
        recent = self._settings.get('recent_files', [])
        if filepath in recent:
            recent.remove(filepath)
        recent.insert(0, filepath)
        self._settings['recent_files'] = recent[:10]
        self._save()
    
    def add_recent_host(self, host):
        """添加最近主机"""
        recent = self._settings.get('recent_hosts', [])
        if host in recent:
            recent.remove(host)
        recent.insert(0, host)
        self._settings['recent_hosts'] = recent[:20]
        self._save()
    
    def get_recent_hosts(self):
        """获取最近主机列表"""
        return self._settings.get('recent_hosts', [])
    
    def get_recent_files(self):
        """获取最近文件列表"""
        return self._settings.get('recent_files', [])
