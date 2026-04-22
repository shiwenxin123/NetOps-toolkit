#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NetOps Toolkit v4.0
网络运维工具集 - 交换机配置生成 + 11个网络工具
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from gui.main_window import MainWindow
from gui.tools_window import NetworkToolsWindow
from gui.splash import SplashManager

APP_NAME = "NetOps Toolkit"
APP_VERSION = "4.0"


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    
    font = QFont("Microsoft YaHei UI", 9)
    app.setFont(font)
    
    splash_manager = SplashManager(app)
    
    def on_splash_complete():
        window = MainWindow()
        window.show()
    
    splash_manager.start_loading(on_splash_complete)
    
    sys.exit(app.exec_())


def run_tools():
    """运行网络工具箱"""
    app = QApplication(sys.argv)
    
    app.setApplicationName("网络工具箱")
    app.setApplicationVersion("1.0")
    
    font = QFont("Microsoft YaHei UI", 9)
    app.setFont(font)
    
    splash_manager = SplashManager(app)
    
    def on_splash_complete():
        window = NetworkToolsWindow()
        window.show()
    
    splash_manager.start_loading(on_splash_complete)
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
