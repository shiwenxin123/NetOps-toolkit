#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动画面 - 现代设计风格
"""

from PyQt5.QtWidgets import QSplashScreen, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import (QPixmap, QPainter, QFont, QColor, QLinearGradient, 
                         QRadialGradient, QPen, QBrush, QPainterPath)

import os
import sys
import math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class ModernSplashScreen(QWidget):
    """现代风格启动画面"""
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_QuitOnClose, False)
        
        self.setFixedSize(600, 400)
        
        self._progress = 0
        self._loading_text = "正在初始化..."
        self._dot_count = 0
        self._animation_angle = 0
        
        self.dot_timer = QTimer()
        self.dot_timer.timeout.connect(self._update_dots)
        self.dot_timer.start(200)
    
    def _update_dots(self):
        self._dot_count = (self._dot_count + 1) % 4
        self._animation_angle = (self._animation_angle + 5) % 360
        self.update()
    
    def set_progress(self, value, text=None):
        self._progress = min(100, max(0, value))
        if text:
            self._loading_text = text
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        # 绘制背景
        self._draw_background(painter)
        
        # 绘制装饰元素
        self._draw_decorations(painter)
        
        # 绘制Logo区域
        self._draw_logo(painter)
        
        # 绘制标题
        self._draw_title(painter)
        
        # 绘制进度区域
        self._draw_progress(painter)
        
        # 绘制加载动画
        self._draw_loading_animation(painter)
        
        # 绘制版权信息
        self._draw_footer(painter)
    
    def _draw_background(self, painter):
        # 主背景渐变
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#ffffff"))
        gradient.setColorAt(0.5, QColor("#f8fafc"))
        gradient.setColorAt(1, QColor("#f1f5f9"))
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(self.rect(), 16, 16)
        
        # 添加边框
        painter.setPen(QPen(QColor(33, 150, 243, 50), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 16, 16)
    
    def _draw_decorations(self, painter):
        # 右上角装饰圆
        painter.setPen(Qt.NoPen)
        
        gradient1 = QRadialGradient(self.width() - 80, 80, 120)
        gradient1.setColorAt(0, QColor(33, 150, 243, 30))
        gradient1.setColorAt(1, QColor(33, 150, 243, 0))
        painter.setBrush(gradient1)
        painter.drawEllipse(self.width() - 200, -40, 240, 240)
        
        # 左下角装饰圆
        gradient2 = QRadialGradient(80, self.height() - 80, 100)
        gradient2.setColorAt(0, QColor(25, 118, 210, 25))
        gradient2.setColorAt(1, QColor(25, 118, 210, 0))
        painter.setBrush(gradient2)
        painter.drawEllipse(-50, self.height() - 180, 200, 200)
        
        # 绘制网格点
        painter.setPen(QPen(QColor(33, 150, 243, 20), 1))
        for x in range(0, self.width(), 30):
            for y in range(0, self.height(), 30):
                painter.drawPoint(x, y)
    
    def _draw_logo(self, painter):
        center_x = self.width() // 2
        center_y = 140
        
        # 绘制背景圆环
        painter.setPen(QPen(QColor(33, 150, 243, 30), 3))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center_x - 55, center_y - 55, 110, 110)
        
        # 绘制旋转动画圈
        pen = QPen(QColor(33, 150, 243), 3)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        path = QPainterPath()
        start_angle = self._animation_angle * 16
        path.arcMoveTo(center_x - 50, center_y - 50, 100, 100, self._animation_angle)
        path.arcTo(center_x - 50, center_y - 50, 100, 100, self._animation_angle, 270)
        painter.drawPath(path)
        
        # 绘制内部渐变圆
        inner_gradient = QRadialGradient(center_x, center_y, 45)
        inner_gradient.setColorAt(0, QColor(33, 150, 243, 15))
        inner_gradient.setColorAt(1, QColor(33, 150, 243, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(inner_gradient)
        painter.drawEllipse(center_x - 45, center_y - 45, 90, 90)
        
        # 绘制图标
        painter.setFont(QFont("Segoe UI Emoji", 40))
        painter.setPen(QColor(33, 150, 243))
        painter.drawText(center_x - 25, center_y + 18, "🔧")
    
    def _draw_title(self, painter):
        # 主标题
        painter.setFont(QFont("Microsoft YaHei UI", 26, QFont.Bold))
        painter.setPen(QColor(25, 118, 210))
        
        title = "NetOps Toolkit"
        title_width = painter.fontMetrics().horizontalAdvance(title)
        painter.drawText((self.width() - title_width) // 2, 240, title)
        
        # 副标题
        painter.setFont(QFont("Microsoft YaHei UI", 11))
        painter.setPen(QColor(100, 116, 139))
        
        subtitle = "网络运维工具集"
        subtitle_width = painter.fontMetrics().horizontalAdvance(subtitle)
        painter.drawText((self.width() - subtitle_width) // 2, 268, subtitle)
    
    def _draw_progress(self, painter):
        bar_x = 100
        bar_y = 300
        bar_width = self.width() - 200
        bar_height = 6
        
        # 背景条
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(226, 232, 240))
        painter.drawRoundedRect(bar_x, bar_y, bar_width, bar_height, 3, 3)
        
        # 进度条
        progress_width = int(bar_width * self._progress / 100)
        if progress_width > 0:
            progress_gradient = QLinearGradient(bar_x, 0, bar_x + progress_width, 0)
            progress_gradient.setColorAt(0, QColor(33, 150, 243))
            progress_gradient.setColorAt(0.5, QColor(59, 130, 246))
            progress_gradient.setColorAt(1, QColor(25, 118, 210))
            
            painter.setBrush(progress_gradient)
            painter.drawRoundedRect(bar_x, bar_y, progress_width, bar_height, 3, 3)
        
        # 进度百分比
        painter.setFont(QFont("Microsoft YaHei UI", 10, QFont.Bold))
        painter.setPen(QColor(33, 150, 243))
        percent_text = f"{self._progress}%"
        painter.drawText(bar_x + bar_width + 15, bar_y + 5, percent_text)
        
        # 加载文字
        dots = "." * self._dot_count
        painter.setFont(QFont("Microsoft YaHei UI", 10))
        painter.setPen(QColor(100, 116, 139))
        loading_text = f"{self._loading_text}{dots}"
        text_width = painter.fontMetrics().horizontalAdvance(loading_text)
        painter.drawText((self.width() - text_width) // 2, bar_y + 28, loading_text)
    
    def _draw_loading_animation(self, painter):
        center_x = self.width() - 70
        center_y = self.height() - 50
        
        for i in range(8):
            angle = (self._animation_angle + i * 45) * math.pi / 180
            x = center_x + 12 * math.cos(angle)
            y = center_y + 12 * math.sin(angle)
            
            alpha = 100 + int(155 * (1 - i / 8))
            color = QColor(33, 150, 243, alpha)
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawEllipse(int(x) - 2, int(y) - 2, 4, 4)
    
    def _draw_footer(self, painter):
        # 分隔线
        painter.setPen(QPen(QColor(226, 232, 240), 1))
        painter.drawLine(100, self.height() - 35, self.width() - 100, self.height() - 35)
        
        # 版本信息
        painter.setFont(QFont("Microsoft YaHei UI", 9))
        painter.setPen(QColor(148, 163, 184))
        
        version_text = "Version 4.0"
        painter.drawText(30, self.height() - 15, version_text)
        
        copyright_text = "by Dimples"
        copyright_width = painter.fontMetrics().horizontalAdvance(copyright_text)
        painter.drawText(self.width() - copyright_width - 30, self.height() - 15, copyright_text)
        
        # 功能标签
        features = ["华为/H3C 配置生成", "11个网络工具", "批量配置"]
        painter.setFont(QFont("Microsoft YaHei UI", 8))
        x_offset = (self.width() - sum(painter.fontMetrics().horizontalAdvance(f"• {f}") for f in features) - 40) // 2
        
        for feature in features:
            painter.setPen(QColor(59, 130, 246))
            painter.drawText(x_offset, self.height() - 15, "•")
            painter.setPen(QColor(148, 163, 184))
            painter.drawText(x_offset + 10, self.height() - 15, feature)
            x_offset += painter.fontMetrics().horizontalAdvance(f"• {feature}") + 20


class SplashManager:
    """启动画面管理器"""
    
    def __init__(self, app):
        self.app = app
        self.splash = ModernSplashScreen()
        
        # 居中显示
        screen = app.primaryScreen().geometry()
        x = (screen.width() - self.splash.width()) // 2
        y = (screen.height() - self.splash.height()) // 2
        self.splash.move(x, y)
        
        self.splash.show()
        
        self.load_steps = [
            (8, "加载系统配置"),
            (18, "初始化核心模块"),
            (28, "加载配置生成器"),
            (40, "加载网络工具箱"),
            (52, "初始化对话框组件"),
            (65, "加载样式资源"),
            (78, "准备用户界面"),
            (90, "应用主题设置"),
            (100, "启动完成"),
        ]
        self.current_step = 0
    
    def next_step(self):
        if self.current_step < len(self.load_steps):
            progress, text = self.load_steps[self.current_step]
            self.splash.set_progress(progress, text)
            self.current_step += 1
            return True
        return False
    
    def start_loading(self, callback):
        def process_step():
            if self.next_step():
                QTimer.singleShot(80, process_step)
            else:
                QTimer.singleShot(300, self.finish)
                QTimer.singleShot(600, callback)
        
        QTimer.singleShot(100, process_step)
    
    def finish(self):
        self.splash.dot_timer.stop()
        self.splash.close()
        
    def start_loading_async(self, callback):
        """异步加载"""
        QTimer.singleShot(100, lambda: self._run_steps(callback))
    
    def _run_steps(self, callback):
        def process():
            if self.next_step():
                QTimer.singleShot(60, process)
            else:
                QTimer.singleShot(200, self.finish)
                QTimer.singleShot(300, callback)
        process()
