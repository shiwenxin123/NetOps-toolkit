#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络工具箱主窗口
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QLabel, QMessageBox, QStatusBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gui.tools.subnet_tool import SubnetCalculatorWidget
from gui.tools.ping_tool import PingTestWidget
from gui.tools.port_tool import PortScanWidget
from gui.tools.trace_tool import TraceRouteWidget
from gui.tools.dns_tool import DNSToolWidget, NetworkInfoWidget, IPConverterWidget
from gui.tools.http_tool import HTTPStatusWidget
from gui.tools.password_tool import PasswordGeneratorWidget
from gui.tools.encoder_tool import EncoderToolWidget
from gui.tools.mac_tool import MACToolWidget
from gui.styles import MODERN_STYLE


class NetworkToolsWindow(QMainWindow):
    """网络工具箱主窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("NetOps Toolkit - 网络工具箱")
        self.setGeometry(200, 200, 1000, 800)
        self.setStyleSheet(MODERN_STYLE)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)
        
        header = QLabel("🧰 网络工具箱")
        header.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #1976D2;
            padding: 10px;
            background: transparent;
        """)
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        
        tabs.addTab(SubnetCalculatorWidget(), "🧮 子网计算器")
        tabs.addTab(PingTestWidget(), "🔔 Ping 测试")
        tabs.addTab(PortScanWidget(), "🔍 端口扫描")
        tabs.addTab(TraceRouteWidget(), "🛤️ 路由跟踪")
        tabs.addTab(DNSToolWidget(), "🌐 DNS/Whois")
        tabs.addTab(HTTPStatusWidget(), "🌐 HTTP检测")
        tabs.addTab(MACToolWidget(), "📀 MAC查询")
        tabs.addTab(PasswordGeneratorWidget(), "🔐 密码生成")
        tabs.addTab(EncoderToolWidget(), "🔄 编码转换")
        tabs.addTab(NetworkInfoWidget(), "🖥️ 网络信息")
        tabs.addTab(IPConverterWidget(), "🔄 IP 转换")
        
        main_layout.addWidget(tabs)
        
        self.statusBar().showMessage("就绪")
        self.statusBar().setStyleSheet("color: #1976D2;")
