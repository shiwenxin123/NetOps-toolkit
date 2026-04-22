#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置导入导出工具
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTextEdit, QPushButton, QGroupBox, QMessageBox,
                             QFileDialog, QComboBox, QCheckBox, QLineEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import json
import os

from gui.tool_styles import (
    TOOL_LABEL_STYLE, TOOL_LABEL_SECONDARY,
    TOOL_BUTTON_PRIMARY, TOOL_BUTTON_GHOST,
    TOOL_STATUS_SUCCESS, TOOL_STATUS_ERROR, TOOL_STATUS_WARNING,
    apply_tool_style
)


class ConfigIOWidget(QWidget):
    """配置导入导出工具"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_data = {}
        self.initUI()
    
    def initUI(self):
        apply_tool_style(self)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel("📦 配置导入导出工具")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ff9500; padding: 5px 0;")
        layout.addWidget(title_label)
        
        export_group = QGroupBox("📤 导出配置")
        export_layout = QVBoxLayout(export_group)
        export_layout.setSpacing(10)
        
        format_row = QHBoxLayout()
        format_row.setSpacing(8)
        
        format_label = QLabel("导出格式:")
        format_label.setStyleSheet(TOOL_LABEL_STYLE)
        format_row.addWidget(format_label)
        
        self.export_format = QComboBox()
        self.export_format.addItems(["📋 JSON 格式", "📄 文本格式", "📜 批量脚本"])
        format_row.addWidget(self.export_format)
        format_row.addStretch()
        export_layout.addLayout(format_row)
        
        options_row = QHBoxLayout()
        options_row.setSpacing(15)
        
        self.include_comments = QCheckBox("包含注释说明")
        self.include_comments.setChecked(True)
        options_row.addWidget(self.include_comments)
        
        self.include_timestamp = QCheckBox("包含时间戳")
        self.include_timestamp.setChecked(True)
        options_row.addWidget(self.include_timestamp)
        
        self.include_device_info = QCheckBox("包含设备信息")
        self.include_device_info.setChecked(True)
        options_row.addWidget(self.include_device_info)
        
        options_row.addStretch()
        export_layout.addLayout(options_row)
        
        export_btn_row = QHBoxLayout()
        export_btn_row.setSpacing(8)
        
        self.export_btn = QPushButton("💾 导出到文件")
        self.export_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.export_btn.clicked.connect(self.export_config)
        export_btn_row.addWidget(self.export_btn)
        
        self.copy_btn = QPushButton("📋 复制到剪贴板")
        self.copy_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.copy_btn.clicked.connect(self.copy_config)
        export_btn_row.addWidget(self.copy_btn)
        
        export_btn_row.addStretch()
        export_layout.addLayout(export_btn_row)
        
        layout.addWidget(export_group)
        
        import_group = QGroupBox("📥 导入配置")
        import_layout = QVBoxLayout(import_group)
        import_layout.setSpacing(10)
        
        import_format_row = QHBoxLayout()
        import_format_row.setSpacing(8)
        
        import_label = QLabel("导入来源:")
        import_label.setStyleSheet(TOOL_LABEL_STYLE)
        import_format_row.addWidget(import_label)
        
        self.import_source = QComboBox()
        self.import_source.addItems(["📁 从文件导入", "📋 从剪贴板导入", "🔍 从文本解析"])
        import_format_row.addWidget(self.import_source)
        import_format_row.addStretch()
        import_layout.addLayout(import_format_row)
        
        import_btn_row = QHBoxLayout()
        import_btn_row.setSpacing(8)
        
        self.import_btn = QPushButton("📂 导入配置")
        self.import_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.import_btn.clicked.connect(self.import_config)
        import_btn_row.addWidget(self.import_btn)
        
        self.paste_btn = QPushButton("📋 从剪贴板粘贴")
        self.paste_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.paste_btn.clicked.connect(self.paste_from_clipboard)
        import_btn_row.addWidget(self.paste_btn)
        
        self.parse_btn = QPushButton("🔍 解析配置")
        self.parse_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.parse_btn.clicked.connect(self.parse_config)
        import_btn_row.addWidget(self.parse_btn)
        
        import_btn_row.addStretch()
        import_layout.addLayout(import_btn_row)
        
        layout.addWidget(import_group)
        
        preview_group = QGroupBox("👁️ 配置预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.config_text = QTextEdit()
        self.config_text.setFont(QFont("Consolas", 10))
        self.config_text.setPlaceholderText("配置内容将显示在这里...\n\n可以手动编辑或从外部导入配置")
        self.config_text.setMinimumHeight(200)
        preview_layout.addWidget(self.config_text)
        
        preview_btn_row = QHBoxLayout()
        preview_btn_row.setSpacing(8)
        
        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.clear_btn.clicked.connect(self.clear_config)
        preview_btn_row.addWidget(self.clear_btn)
        
        preview_btn_row.addStretch()
        
        self.copy_preview_btn = QPushButton("📋 复制预览")
        self.copy_preview_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.copy_preview_btn.clicked.connect(self.copy_preview)
        preview_btn_row.addWidget(self.copy_preview_btn)
        
        preview_layout.addLayout(preview_btn_row)
        
        layout.addWidget(preview_group)
        
        self.status_bar = QLabel("就绪")
        self.status_bar.setStyleSheet("color: #8a8580; padding: 5px; font-size: 12px;")
        layout.addWidget(self.status_bar)
    
    def set_config_data(self, data):
        """设置配置数据"""
        self.config_data = data
        self.update_preview()
    
    def update_preview(self):
        """更新预览"""
        format_idx = self.export_format.currentIndex()
        
        if format_idx == 0:  # JSON
            self.config_text.setPlainText(json.dumps(self.config_data, indent=2, ensure_ascii=False))
        elif format_idx == 1:  # Text
            text = self.format_as_text(self.config_data)
            self.config_text.setPlainText(text)
        else:  # Script
            script = self.format_as_script(self.config_data)
            self.config_text.setPlainText(script)
    
    def format_as_text(self, data):
        """格式化为文本"""
        lines = []
        
        if self.include_timestamp.isChecked():
            from datetime import datetime
            lines.append(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.include_device_info.isChecked() and 'device_info' in data:
            lines.append(f"# 设备: {data['device_info'].get('name', 'Unknown')}")
        
        lines.append("")
        
        for section, content in data.items():
            if section == 'device_info':
                continue
            if self.include_comments.isChecked():
                lines.append(f"# {section}")
            lines.append(str(content))
            lines.append("")
        
        return '\n'.join(lines)
    
    def format_as_script(self, data):
        """格式化为脚本"""
        lines = ["#!/bin/bash", "# 配置部署脚本", ""]
        
        if self.include_timestamp.isChecked():
            from datetime import datetime
            lines.append(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        lines.append("")
        lines.append("echo '开始配置...'")
        lines.append("")
        
        for section, content in data.items():
            if section == 'device_info':
                continue
            if self.include_comments.isChecked():
                lines.append(f"# {section}")
            lines.append(f"echo '{section}'")
            for line in str(content).split('\n'):
                if line.strip():
                    lines.append(f"echo '  {line}'")
            lines.append("")
        
        lines.append("echo '配置完成!'")
        
        return '\n'.join(lines)
    
    def export_config(self):
        """导出配置到文件"""
        if not self.config_text.toPlainText():
            QMessageBox.warning(self, "警告", "没有可导出的配置")
            return
        
        format_idx = self.export_format.currentIndex()
        extensions = ["JSON 文件 (*.json)", "文本文件 (*.txt)", "Shell 脚本 (*.sh)"]
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出配置", "", extensions[format_idx]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.config_text.toPlainText())
                QMessageBox.information(self, "成功", f"配置已导出到:\n{file_path}")
                self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
                self.status_bar.setText(f"✅ 已导出到: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
                self.status_bar.setStyleSheet(TOOL_STATUS_ERROR)
                self.status_bar.setText(f"❌ 导出失败")
    
    def copy_config(self):
        """复制配置到剪贴板"""
        from PyQt5.QtWidgets import QApplication
        text = self.config_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText("✅ 已复制到剪贴板")
        else:
            self.status_bar.setStyleSheet(TOOL_STATUS_WARNING)
            self.status_bar.setText("⚠️ 没有可复制的内容")
    
    def import_config(self):
        """从文件导入配置"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入配置", "", "JSON 文件 (*.json);;文本文件 (*.txt);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if file_path.endswith('.json'):
                    self.config_data = json.loads(content)
                    self.update_preview()
                else:
                    self.config_text.setPlainText(content)
                
                QMessageBox.information(self, "成功", "配置导入成功")
                self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
                self.status_bar.setText(f"✅ 已导入: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导入失败: {str(e)}")
                self.status_bar.setStyleSheet(TOOL_STATUS_ERROR)
                self.status_bar.setText(f"❌ 导入失败")
    
    def paste_from_clipboard(self):
        """从剪贴板粘贴"""
        from PyQt5.QtWidgets import QApplication
        text = QApplication.clipboard().text()
        
        if text:
            self.config_text.setPlainText(text)
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText("✅ 已从剪贴板导入")
        else:
            QMessageBox.warning(self, "警告", "剪贴板为空")
            self.status_bar.setStyleSheet(TOOL_STATUS_WARNING)
            self.status_bar.setText("⚠️ 剪贴板为空")
    
    def parse_config(self):
        """解析配置"""
        text = self.config_text.toPlainText()
        
        if not text:
            QMessageBox.warning(self, "警告", "请先输入或导入配置")
            return
        
        result = f"""配置分析结果:
{'─' * 40}
总行数: {len(text.splitlines())}
字符数: {len(text)}
{'─' * 40}
主要配置项:
"""
        
        lines = text.splitlines()
        keywords = ['vlan', 'interface', 'ip address', 'acl', 'route', 'snmp', 'ntp']
        found = {k: 0 for k in keywords}
        
        for line in lines:
            line_lower = line.lower()
            for kw in keywords:
                if kw in line_lower:
                    found[kw] += 1
        
        for kw, count in found.items():
            if count > 0:
                result += f"  • {kw}: {count} 处\n"
        
        self.config_text.setPlainText(result)
        self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
        self.status_bar.setText("✅ 解析完成")
    
    def clear_config(self):
        """清空配置"""
        self.config_text.clear()
        self.config_data = {}
        self.status_bar.setStyleSheet("color: #8a8580;")
        self.status_bar.setText("已清空")
    
    def copy_preview(self):
        """复制预览内容"""
        from PyQt5.QtWidgets import QApplication
        text = self.config_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText("✅ 已复制到剪贴板")
