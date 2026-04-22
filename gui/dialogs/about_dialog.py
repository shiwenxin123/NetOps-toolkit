#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
关于对话框
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTabWidget, QWidget, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gui.styles import MODERN_STYLE, DIALOG_STYLE


class AboutDialog(QDialog):
    """关于对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("关于")
        self.setFixedSize(500, 400)
        self.setStyleSheet(MODERN_STYLE + DIALOG_STYLE)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        
        icon_label = QLabel("🔧")
        icon_label.setStyleSheet("font-size: 48px;")
        header_layout.addWidget(icon_label)
        
        info_layout = QVBoxLayout()
        
        title = QLabel("NetOps Toolkit")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1976D2;")
        info_layout.addWidget(title)
        
        version = QLabel("版本 4.0 - 网络运维工具集")
        version.setStyleSheet("color: #666666; font-size: 12px;")
        info_layout.addWidget(version)
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        tabs = QTabWidget()
        
        about_widget = QWidget()
        about_layout = QVBoxLayout(about_widget)
        
        about_text = QLabel("""
<p style='line-height: 1.8;'>
<strong>NetOps Toolkit</strong> 是一款专业的网络运维工具集，
支持华为和H3C设备的配置快速生成与管理。
</p>
<p style='line-height: 1.8;'>
集成了丰富的网络工具箱，包括：
</p>
<ul style='margin-left: 20px; line-height: 1.6;'>
<li>子网计算器</li>
<li>Ping测试 & 端口扫描</li>
<li>DNS/Whois查询</li>
<li>HTTP状态检测</li>
<li>MAC地址查询</li>
<li>密码生成器 & 编码转换</li>
</ul>
        """)
        about_text.setWordWrap(True)
        about_layout.addWidget(about_text)
        about_layout.addStretch()
        
        tabs.addTab(about_widget, "📝 关于")
        
        feature_widget = QWidget()
        feature_layout = QVBoxLayout(feature_widget)
        
        features_text = QTextEdit()
        features_text.setReadOnly(True)
        features_text.setHtml("""
<h4 style='color: #1976D2;'>🎯 核心功能</h4>
<ul style='line-height: 1.8;'>
<li>支持华为/H3C双平台配置生成</li>
<li>配置模板快速应用</li>
<li>配置导入导出与比较</li>
<li>命令速查手册</li>
</ul>

<h4 style='color: #1976D2;'>🛠️ 网络工具</h4>
<ul style='line-height: 1.8;'>
<li>11个实用网络诊断工具</li>
<li>支持批量操作</li>
<li>结果导出与复制</li>
</ul>

<h4 style='color: #1976D2;'>🎨 界面特色</h4>
<ul style='line-height: 1.8;'>
<li>Material Design风格</li>
<li>清爽明亮的蓝色主题</li>
<li>统一的设计语言</li>
</ul>
        """)
        feature_layout.addWidget(features_text)
        
        tabs.addTab(feature_widget, "✨ 功能")
        
        thanks_widget = QWidget()
        thanks_layout = QVBoxLayout(thanks_widget)
        
        thanks_text = QLabel("""
<p style='line-height: 2;'>
<b>开发框架:</b><br>
Python 3.12 + PyQt5
</p>
<p style='line-height: 2;'>
<b>开源库:</b><br>
requests, python-whois, dnspython
</p>
<p style='line-height: 2;'>
<b>设计参考:</b><br>
Google Material Design<br>
Microsoft Fluent Design
</p>
<p style='line-height: 2; margin-top: 20px; color: #1976D2;'>
Made with ❤️ by Dimples
</p>
<p style='line-height: 1.5; font-size: 16px; font-weight: bold; color: #2196F3;'>
QQ: 1367880198
</p>
        """)
        thanks_text.setWordWrap(True)
        thanks_layout.addWidget(thanks_text)
        thanks_layout.addStretch()
        
        tabs.addTab(thanks_widget, "🙏 致谢")
        
        layout.addWidget(tabs)
        
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        ok_btn = QPushButton("确定")
        ok_btn.setObjectName("primaryButton")
        ok_btn.clicked.connect(self.accept)
        btn_row.addWidget(ok_btn)
        
        layout.addLayout(btn_row)
