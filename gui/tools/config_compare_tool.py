#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置比较工具 - 华为/H3C配置对比
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTextEdit, QPushButton, QSplitter, QComboBox,
                             QGroupBox, QMessageBox, QTabWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextCharFormat, QColor, QBrush
import difflib

from gui.tool_styles import (
    TOOL_LABEL_STYLE, TOOL_LABEL_SECONDARY,
    TOOL_BUTTON_PRIMARY, TOOL_BUTTON_GHOST,
    TOOL_STATUS_SUCCESS, TOOL_STATUS_ERROR,
    apply_tool_style
)


class ConfigCompareWidget(QWidget):
    """配置比较工具"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        apply_tool_style(self)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel("⚖️ 配置比较工具")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ff9500; padding: 5px 0;")
        layout.addWidget(title_label)
        
        header = QHBoxLayout()
        header.setSpacing(8)
        
        header.addWidget(QLabel(""))
        
        self.compare_type = QComboBox()
        self.compare_type.addItems(["📋 配置对比 (差异高亮)", "🔄 华为 vs H3C 命令转换"])
        self.compare_type.currentIndexChanged.connect(self.on_compare_type_changed)
        header.addWidget(self.compare_type)
        
        header.addStretch()
        
        layout.addLayout(header)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_group = QGroupBox("原始配置")
        left_group_layout = QVBoxLayout(left_group)
        self.left_text = QTextEdit()
        self.left_text.setFont(QFont("Consolas", 10))
        self.left_text.setPlaceholderText("粘贴原始配置...")
        left_group_layout.addWidget(self.left_text)
        left_layout.addWidget(left_group)
        
        splitter.addWidget(left_widget)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        right_group = QGroupBox("目标配置")
        right_group_layout = QVBoxLayout(right_group)
        self.right_text = QTextEdit()
        self.right_text.setFont(QFont("Consolas", 10))
        self.right_text.setPlaceholderText("粘贴目标配置...")
        right_group_layout.addWidget(self.right_text)
        right_layout.addWidget(right_group)
        
        splitter.addWidget(right_widget)
        
        splitter.setSizes([400, 400])
        layout.addWidget(splitter)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.compare_btn = QPushButton("🔍 比较配置")
        self.compare_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.compare_btn.clicked.connect(self.compare_configs)
        btn_layout.addWidget(self.compare_btn)
        
        self.swap_btn = QPushButton("🔄 交换配置")
        self.swap_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.swap_btn.clicked.connect(self.swap_configs)
        btn_layout.addWidget(self.swap_btn)
        
        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.clear_btn.clicked.connect(self.clear_all)
        btn_layout.addWidget(self.clear_btn)
        
        btn_layout.addStretch()
        
        self.copy_result_btn = QPushButton("📋 复制结果")
        self.copy_result_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.copy_result_btn.clicked.connect(self.copy_result)
        btn_layout.addWidget(self.copy_result_btn)
        
        layout.addLayout(btn_layout)
        
        result_group = QGroupBox("比较结果")
        result_layout = QVBoxLayout(result_group)
        
        self.result_text = QTextEdit()
        self.result_text.setFont(QFont("Consolas", 10))
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(200)
        self.result_text.setPlaceholderText("比较结果将显示在这里...")
        result_layout.addWidget(self.result_text)
        
        layout.addWidget(result_group)
        
        self.status_bar = QLabel("就绪")
        self.status_bar.setStyleSheet("color: #8a8580; padding: 5px; font-size: 12px;")
        layout.addWidget(self.status_bar)
        
        self.load_example_configs()
    
    def on_compare_type_changed(self, index):
        if index == 1:
            self.left_text.setPlaceholderText("粘贴华为配置...")
            self.right_text.setPlaceholderText("将自动转换为 H3C 配置...")
            self.compare_btn.setText("🔄 转换配置")
        else:
            self.left_text.setPlaceholderText("粘贴原始配置...")
            self.right_text.setPlaceholderText("粘贴目标配置...")
            self.compare_btn.setText("🔍 比较配置")
    
    def compare_configs(self):
        if self.compare_type.currentIndex() == 1:
            self.convert_config()
        else:
            self.diff_configs()
    
    def diff_configs(self):
        left_text = self.left_text.toPlainText()
        right_text = self.right_text.toPlainText()
        
        if not left_text and not right_text:
            QMessageBox.warning(self, "警告", "请输入配置内容")
            return
        
        left_lines = left_text.splitlines()
        right_lines = right_text.splitlines()
        
        diff = difflib.unified_diff(
            left_lines, right_lines,
            fromfile='原始配置', tofile='目标配置',
            lineterm=''
        )
        
        diff_text = '\n'.join(diff)
        
        self.result_text.setPlainText(diff_text)
        
        additions = diff_text.count('+') - diff_text.count('+++')
        deletions = diff_text.count('-') - diff_text.count('---')
        
        self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
        self.status_bar.setText(f"✅ 比较完成 | +{additions} 行 -{deletions} 行")
    
    def convert_config(self):
        from utils.config_parser import ConfigConverter
        
        huawei_config = self.left_text.toPlainText()
        
        if not huawei_config:
            QMessageBox.warning(self, "警告", "请输入华为配置")
            return
        
        h3c_config = ConfigConverter.huawei_to_h3c(huawei_config)
        
        self.right_text.setPlainText(h3c_config)
        self.result_text.setPlainText(f"✅ 转换完成\n\n华为配置行数: {len(huawei_config.splitlines())}\nH3C 配置行数: {len(h3c_config.splitlines())}")
        
        self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
        self.status_bar.setText("✅ 配置转换完成")
    
    def swap_configs(self):
        left = self.left_text.toPlainText()
        right = self.right_text.toPlainText()
        self.left_text.setPlainText(right)
        self.right_text.setPlainText(left)
        self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
        self.status_bar.setText("✅ 已交换配置")
    
    def clear_all(self):
        self.left_text.clear()
        self.right_text.clear()
        self.result_text.clear()
        self.status_bar.setStyleSheet("color: #8a8580;")
        self.status_bar.setText("已清空")
    
    def copy_result(self):
        from PyQt5.QtWidgets import QApplication
        QApplication.clipboard().setText(self.result_text.toPlainText())
        self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
        self.status_bar.setText("✅ 已复制到剪贴板")
    
    def load_example_configs(self):
        self.left_text.setPlainText("""# 华为交换机配置示例
sysname SW-Core
#
vlan batch 10 20 30
#
interface Vlanif10
 ip address 192.168.10.1 255.255.255.0
#
interface GigabitEthernet0/0/1
 port link-type access
 port default vlan 10
#""")
        self.right_text.setPlainText("""# H3C交换机配置示例
sysname SW-Core
#
vlan 10 20 30
#
interface Vlan-interface10
 ip address 192.168.10.1 255.255.255.0
#
interface GigabitEthernet1/0/1
 port link-mode bridge
 port access vlan 10
#""")
