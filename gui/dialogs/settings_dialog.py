#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
设置对话框
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGroupBox, QComboBox, QSpinBox,
                             QCheckBox, QTabWidget, QWidget, QLineEdit,
                             QListWidget, QMessageBox)
from PyQt5.QtCore import Qt

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gui.styles import MODERN_STYLE, DIALOG_STYLE
from utils.settings import Settings


class SettingsDialog(QDialog):
    """系统设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("系统设置")
        self.setMinimumSize(500, 450)
        self.setStyleSheet(MODERN_STYLE + DIALOG_STYLE)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        tabs = QTabWidget()
        
        general_widget = QWidget()
        general_layout = QVBoxLayout(general_widget)
        general_layout.setSpacing(12)
        
        theme_group = QGroupBox("外观设置")
        theme_layout = QVBoxLayout(theme_group)
        
        theme_row = QHBoxLayout()
        theme_label = QLabel("界面主题:")
        theme_label.setStyleSheet("font-weight: bold;")
        theme_row.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["浅色模式", "深色模式", "跟随系统"])
        current_theme = self.settings.get('theme', 'light')
        theme_index = {'light': 0, 'dark': 1, 'system': 2}.get(current_theme, 0)
        self.theme_combo.setCurrentIndex(theme_index)
        theme_row.addWidget(self.theme_combo)
        theme_row.addStretch()
        theme_layout.addLayout(theme_row)
        
        toolbar_row = QHBoxLayout()
        self.show_toolbar_cb = QCheckBox("显示工具栏")
        self.show_toolbar_cb.setChecked(self.settings.get('show_toolbar', True))
        toolbar_row.addWidget(self.show_toolbar_cb)
        toolbar_row.addStretch()
        theme_layout.addLayout(toolbar_row)
        
        general_layout.addWidget(theme_group)
        
        device_group = QGroupBox("默认设备")
        device_layout = QVBoxLayout(device_group)
        
        device_row = QHBoxLayout()
        device_label = QLabel("默认设备类型:")
        device_label.setStyleSheet("font-weight: bold;")
        device_row.addWidget(device_label)
        
        self.device_combo = QComboBox()
        self.device_combo.addItems(["华为 (Huawei)", "H3C (华三)"])
        current_device = self.settings.get('default_device', 'huawei')
        self.device_combo.setCurrentIndex(0 if current_device == 'huawei' else 1)
        device_row.addWidget(self.device_combo)
        device_row.addStretch()
        device_layout.addLayout(device_row)
        
        general_layout.addWidget(device_group)
        
        auto_save_row = QHBoxLayout()
        self.auto_save_cb = QCheckBox("自动保存配置")
        self.auto_save_cb.setChecked(self.settings.get('auto_save', True))
        auto_save_row.addWidget(self.auto_save_cb)
        auto_save_row.addStretch()
        general_layout.addLayout(auto_save_row)
        
        general_layout.addStretch()
        tabs.addTab(general_widget, "⚙️ 常规")
        
        network_widget = QWidget()
        network_layout = QVBoxLayout(network_widget)
        network_layout.setSpacing(12)
        
        timeout_group = QGroupBox("超时设置")
        timeout_layout = QVBoxLayout(timeout_group)
        
        ping_row = QHBoxLayout()
        ping_label = QLabel("Ping 次数:")
        ping_label.setStyleSheet("font-weight: bold;")
        ping_row.addWidget(ping_label)
        
        self.ping_count_spin = QSpinBox()
        self.ping_count_spin.setRange(1, 20)
        self.ping_count_spin.setValue(self.settings.get('default_ping_count', 4))
        ping_row.addWidget(self.ping_count_spin)
        ping_row.addStretch()
        timeout_layout.addLayout(ping_row)
        
        timeout_row = QHBoxLayout()
        timeout_label = QLabel("默认超时(秒):")
        timeout_label.setStyleSheet("font-weight: bold;")
        timeout_row.addWidget(timeout_label)
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 30)
        self.timeout_spin.setValue(self.settings.get('default_timeout', 2))
        timeout_row.addWidget(self.timeout_spin)
        timeout_row.addStretch()
        timeout_layout.addLayout(timeout_row)
        
        port_row = QHBoxLayout()
        port_label = QLabel("端口扫描超时(秒):")
        port_label.setStyleSheet("font-weight: bold;")
        port_row.addWidget(port_label)
        
        self.port_timeout_spin = QSpinBox()
        self.port_timeout_spin.setRange(1, 10)
        self.port_timeout_spin.setValue(self.settings.get('default_port_timeout', 1))
        port_row.addWidget(self.port_timeout_spin)
        port_row.addStretch()
        timeout_layout.addLayout(port_row)
        
        network_layout.addWidget(timeout_group)
        network_layout.addStretch()
        
        tabs.addTab(network_widget, "🌐 网络")
        
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        
        recent_group = QGroupBox("最近主机")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_list = QListWidget()
        self.recent_list.addItems(self.settings.get_recent_hosts())
        self.recent_list.setMaximumHeight(150)
        recent_layout.addWidget(self.recent_list)
        
        clear_recent_btn = QPushButton("清空历史")
        clear_recent_btn.clicked.connect(self.clear_recent_hosts)
        recent_layout.addWidget(clear_recent_btn)
        
        history_layout.addWidget(recent_group)
        history_layout.addStretch()
        
        tabs.addTab(history_widget, "📋 历史")
        
        layout.addWidget(tabs)
        
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        reset_btn = QPushButton("恢复默认")
        reset_btn.setObjectName("ghostButton")
        reset_btn.clicked.connect(self.reset_settings)
        btn_row.addWidget(reset_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("ghostButton")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self.save_settings)
        btn_row.addWidget(save_btn)
        
        layout.addLayout(btn_row)
    
    def save_settings(self):
        theme_map = {0: 'light', 1: 'dark', 2: 'system'}
        self.settings.set('theme', theme_map[self.theme_combo.currentIndex()])
        self.settings.set('show_toolbar', self.show_toolbar_cb.isChecked())
        self.settings.set('default_device', 'huawei' if self.device_combo.currentIndex() == 0 else 'h3c')
        self.settings.set('auto_save', self.auto_save_cb.isChecked())
        self.settings.set('default_ping_count', self.ping_count_spin.value())
        self.settings.set('default_timeout', self.timeout_spin.value())
        self.settings.set('default_port_timeout', self.port_timeout_spin.value())
        
        QMessageBox.information(self, "成功", "设置已保存，部分设置需要重启生效")
        self.accept()
    
    def reset_settings(self):
        reply = QMessageBox.question(self, "确认", "确定恢复默认设置？", 
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.settings.reset()
            QMessageBox.information(self, "成功", "已恢复默认设置")
            self.reject()
    
    def clear_recent_hosts(self):
        reply = QMessageBox.question(self, "确认", "确定清空最近主机历史？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.settings.set('recent_hosts', [])
            self.recent_list.clear()
            QMessageBox.information(self, "成功", "历史已清空")
