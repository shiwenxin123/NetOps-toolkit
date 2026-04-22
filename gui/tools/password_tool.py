#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络工具窗口 - 密码生成器
"""

import random
import string
import secrets
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTextEdit, QGroupBox,
                             QSpinBox, QCheckBox, QSlider, QComboBox, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gui.tool_styles import (
    TOOL_LABEL_STYLE, TOOL_LABEL_SECONDARY,
    TOOL_BUTTON_PRIMARY, TOOL_BUTTON_DANGER, TOOL_BUTTON_GHOST,
    TOOL_STATUS_SUCCESS, TOOL_STATUS_ERROR, TOOL_STATUS_WARNING, TOOL_STATUS_INFO,
    apply_tool_style
)


class PasswordGeneratorWidget(QWidget):
    """密码生成器工具"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        apply_tool_style(self)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel("🔐 密码生成器")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976D2; padding: 5px 0;")
        layout.addWidget(title_label)
        
        result_group = QGroupBox("生成的密码")
        result_layout = QVBoxLayout(result_group)
        
        self.password_display = QLineEdit()
        self.password_display.setFont(QFont("Consolas", 16))
        self.password_display.setAlignment(Qt.AlignCenter)
        self.password_display.setMinimumHeight(50)
        result_layout.addWidget(self.password_display)
        
        btn_row = QHBoxLayout()
        
        self.generate_btn = QPushButton("🎲 生成新密码")
        self.generate_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.generate_btn.setMinimumHeight(40)
        self.generate_btn.clicked.connect(self.generate_password)
        btn_row.addWidget(self.generate_btn)
        
        self.copy_btn = QPushButton("📋 复制")
        self.copy_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.copy_btn.setMinimumHeight(40)
        self.copy_btn.clicked.connect(self.copy_password)
        btn_row.addWidget(self.copy_btn)
        
        result_layout.addLayout(btn_row)
        layout.addWidget(result_group)
        
        settings_group = QGroupBox("密码设置")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(12)
        
        len_row = QHBoxLayout()
        len_row.setSpacing(10)
        
        len_label = QLabel("密码长度:")
        len_label.setStyleSheet(TOOL_LABEL_STYLE)
        len_row.addWidget(len_label)
        
        self.length_slider = QSlider(Qt.Horizontal)
        self.length_slider.setRange(8, 64)
        self.length_slider.setValue(16)
        self.length_slider.valueChanged.connect(self.on_length_changed)
        len_row.addWidget(self.length_slider)
        
        self.length_display = QLabel("16")
        self.length_display.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976D2; min-width: 30px;")
        len_row.addWidget(self.length_display)
        
        settings_layout.addLayout(len_row)
        
        count_row = QHBoxLayout()
        count_row.setSpacing(10)
        
        count_label = QLabel("生成数量:")
        count_label.setStyleSheet(TOOL_LABEL_STYLE)
        count_row.addWidget(count_label)
        
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 50)
        self.count_spin.setValue(5)
        self.count_spin.setMinimumWidth(80)
        count_row.addWidget(self.count_spin)
        
        count_row.addStretch()
        
        preset_label = QLabel("预设方案:")
        preset_label.setStyleSheet(TOOL_LABEL_STYLE)
        count_row.addWidget(preset_label)
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "自定义",
            "简单密码 (8位纯数字)",
            "普通密码 (12位字母数字)",
            "强密码 (16位混合)",
            "高安全 (24位全字符)",
            "WIFI密钥 (32位)"
        ])
        self.preset_combo.currentIndexChanged.connect(self.on_preset_changed)
        count_row.addWidget(self.preset_combo)
        
        settings_layout.addLayout(count_row)
        
        options_group = QGroupBox("字符类型")
        options_layout = QHBoxLayout(options_group)
        options_layout.setSpacing(20)
        
        self.upper_cb = QCheckBox("大写字母 (A-Z)")
        self.upper_cb.setChecked(True)
        options_layout.addWidget(self.upper_cb)
        
        self.lower_cb = QCheckBox("小写字母 (a-z)")
        self.lower_cb.setChecked(True)
        options_layout.addWidget(self.lower_cb)
        
        self.digits_cb = QCheckBox("数字 (0-9)")
        self.digits_cb.setChecked(True)
        options_layout.addWidget(self.digits_cb)
        
        self.symbols_cb = QCheckBox("特殊字符 (!@#$%)")
        self.symbols_cb.setChecked(True)
        options_layout.addWidget(self.symbols_cb)
        
        settings_layout.addWidget(options_group)
        
        exclude_row = QHBoxLayout()
        
        exclude_label = QLabel("排除字符:")
        exclude_label.setStyleSheet(TOOL_LABEL_STYLE)
        exclude_row.addWidget(exclude_label)
        
        self.exclude_input = QLineEdit()
        self.exclude_input.setPlaceholderText("输入要排除的字符，如: 0O1lI")
        exclude_row.addWidget(self.exclude_input)
        
        settings_layout.addLayout(exclude_row)
        
        layout.addWidget(settings_group)
        
        batch_group = QGroupBox("批量密码")
        batch_layout = QVBoxLayout(batch_group)
        
        self.batch_result = QTextEdit()
        self.batch_result.setFont(QFont("Consolas", 11))
        self.batch_result.setMinimumHeight(200)
        self.batch_result.setReadOnly(True)
        batch_layout.addWidget(self.batch_result)
        
        batch_btn_row = QHBoxLayout()
        batch_btn_row.addStretch()
        
        self.generate_batch_btn = QPushButton("📋 批量生成")
        self.generate_batch_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.generate_batch_btn.clicked.connect(self.generate_batch_passwords)
        batch_btn_row.addWidget(self.generate_batch_btn)
        
        self.copy_all_btn = QPushButton("📋 复制全部")
        self.copy_all_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.copy_all_btn.clicked.connect(self.copy_all_passwords)
        batch_btn_row.addWidget(self.copy_all_btn)
        
        batch_layout.addLayout(batch_btn_row)
        layout.addWidget(batch_group)
        
        self.strength_label = QLabel("强度: -")
        self.strength_label.setStyleSheet("padding: 5px; font-size: 12px;")
        layout.addWidget(self.strength_label)
        
        self.status_bar = QLabel("就绪")
        self.status_bar.setStyleSheet("color: #666666; padding: 5px; font-size: 12px;")
        layout.addWidget(self.status_bar)
        
        self.generate_password()
    
    def on_length_changed(self, value):
        self.length_display.setText(str(value))
    
    def on_preset_changed(self, index):
        presets = {
            0: None,
            1: {"length": 8, "upper": False, "lower": False, "digits": True, "symbols": False},
            2: {"length": 12, "upper": True, "lower": True, "digits": True, "symbols": False},
            3: {"length": 16, "upper": True, "lower": True, "digits": True, "symbols": True},
            4: {"length": 24, "upper": True, "lower": True, "digits": True, "symbols": True},
            5: {"length": 32, "upper": True, "lower": True, "digits": True, "symbols": True},
        }
        
        if presets[index]:
            preset = presets[index]
            self.length_slider.setValue(preset["length"])
            self.upper_cb.setChecked(preset["upper"])
            self.lower_cb.setChecked(preset["lower"])
            self.digits_cb.setChecked(preset["digits"])
            self.symbols_cb.setChecked(preset["symbols"])
    
    def generate_password(self):
        length = self.length_slider.value()
        
        chars = ""
        if self.upper_cb.isChecked():
            chars += string.ascii_uppercase
        if self.lower_cb.isChecked():
            chars += string.ascii_lowercase
        if self.digits_cb.isChecked():
            chars += string.digits
        if self.symbols_cb.isChecked():
            chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"
        
        exclude = self.exclude_input.text()
        for c in exclude:
            chars = chars.replace(c, "")
        
        if not chars:
            self.password_display.setText("请选择至少一种字符类型")
            self.strength_label.setStyleSheet("color: #f87171; padding: 5px; font-size: 12px;")
            self.strength_label.setText("强度: ❌ 无效")
            return
        
        password = ''.join(secrets.choice(chars) for _ in range(length))
        self.password_display.setText(password)
        
        self.update_strength(password)
        
        self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
        self.status_bar.setText("✅ 已生成新密码")
    
    def update_strength(self, password):
        score = 0
        
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        
        if any(c.isupper() for c in password):
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in password):
            score += 2
        
        if score <= 3:
            strength_text = "⚠️ 弱"
            color = "#f87171"
        elif score <= 5:
            strength_text = "🔶 中等"
            color = "#fbbf24"
        elif score <= 7:
            strength_text = "✅ 强"
            color = "#4ade80"
        else:
            strength_text = "🔒 高安全"
            color = "#22c55e"
        
        entropy = len(set(password)) * len(password)
        self.strength_label.setStyleSheet(f"color: {color}; padding: 5px; font-size: 12px;")
        self.strength_label.setText(f"强度: {strength_text} | 熵值: {entropy} bits")
    
    def generate_batch_passwords(self):
        count = self.count_spin.value()
        passwords = []
        
        for _ in range(count):
            self.generate_password()
            passwords.append(self.password_display.text())
        
        self.batch_result.setPlainText('\n'.join(passwords))
        
        self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
        self.status_bar.setText(f"✅ 已生成 {count} 个密码")
    
    def copy_password(self):
        from PyQt5.QtWidgets import QApplication
        QApplication.clipboard().setText(self.password_display.text())
        
        self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
        self.status_bar.setText("✅ 已复制到剪贴板")
    
    def copy_all_passwords(self):
        from PyQt5.QtWidgets import QApplication
        QApplication.clipboard().setText(self.batch_result.toPlainText())
        
        self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
        self.status_bar.setText("✅ 已复制全部密码到剪贴板")
