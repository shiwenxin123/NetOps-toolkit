#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模板管理对话框
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QListWidget, QListWidgetItem,
                              QTextEdit, QLineEdit, QComboBox, QTabWidget,
                              QWidget, QMessageBox, QFileDialog, QGroupBox,
                              QCheckBox, QInputDialog, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gui.styles import MODERN_STYLE, DIALOG_STYLE
from utils.template_manager import TemplateManager, Template


class TemplateManagerDialog(QDialog):
    """模板管理对话框"""
    
    template_selected = pyqtSignal(dict)
    
    def __init__(self, parent=None, device_type: str = "huawei"):
        super().__init__(parent)
        self.device_type = device_type
        self.template_manager = TemplateManager()
        self.current_template = None
        self.initUI()
        self.load_templates()
    
    def initUI(self):
        self.setWindowTitle("模板管理器")
        self.setMinimumSize(900, 600)
        self.setStyleSheet(MODERN_STYLE + DIALOG_STYLE)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        header = QLabel("📚 模板管理器")
        header.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #1976D2;
            padding: 10px;
        """)
        layout.addWidget(header)
        
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("设备类型:"))
        self.device_combo = QComboBox()
        self.device_combo.addItems(["全部", "华为", "H3C"])
        self.device_combo.currentIndexChanged.connect(self.on_device_filter_changed)
        filter_layout.addWidget(self.device_combo)
        
        filter_layout.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索模板...")
        self.search_input.textChanged.connect(self.on_search_changed)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        list_header = QLabel("模板列表")
        list_header.setStyleSheet("font-weight: bold; color: #333;")
        left_layout.addWidget(list_header)
        
        self.template_list = QListWidget()
        self.template_list.setAlternatingRowColors(True)
        self.template_list.currentItemChanged.connect(self.on_template_selected)
        self.template_list.itemDoubleClicked.connect(self.on_template_double_clicked)
        left_layout.addWidget(self.template_list)
        
        list_btn_layout = QHBoxLayout()
        self.new_btn = QPushButton("新建")
        self.new_btn.clicked.connect(self.create_template)
        list_btn_layout.addWidget(self.new_btn)
        
        self.delete_btn = QPushButton("删除")
        self.delete_btn.clicked.connect(self.delete_template)
        list_btn_layout.addWidget(self.delete_btn)
        
        left_layout.addLayout(list_btn_layout)
        splitter.addWidget(left_widget)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        tabs = QTabWidget()
        
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        
        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("名称:"))
        self.name_input = QLineEdit()
        self.name_input.setReadOnly(True)
        form_layout.addWidget(self.name_input)
        
        form_layout.addWidget(QLabel("设备:"))
        self.device_label = QLabel()
        self.device_label.setStyleSheet("color: #1976D2; font-weight: bold;")
        form_layout.addWidget(self.device_label)
        form_layout.addStretch()
        info_layout.addLayout(form_layout)
        
        info_layout.addWidget(QLabel("描述:"))
        self.desc_input = QTextEdit()
        self.desc_input.setReadOnly(True)
        self.desc_input.setMaximumHeight(80)
        info_layout.addWidget(self.desc_input)
        
        info_layout.addWidget(QLabel("标签:"))
        self.tags_label = QLabel()
        self.tags_label.setStyleSheet("color: #666;")
        info_layout.addWidget(self.tags_label)
        
        info_layout.addWidget(QLabel("配置预览:"))
        self.config_preview = QTextEdit()
        self.config_preview.setReadOnly(True)
        self.config_preview.setStyleSheet("font-family: Consolas, monospace; font-size: 11px;")
        info_layout.addWidget(self.config_preview)
        
        meta_layout = QHBoxLayout()
        self.author_label = QLabel()
        self.author_label.setStyleSheet("color: #999;")
        meta_layout.addWidget(self.author_label)
        meta_layout.addStretch()
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: #999;")
        meta_layout.addWidget(self.time_label)
        info_layout.addLayout(meta_layout)
        
        tabs.addTab(info_widget, "📝 详情")
        
        edit_widget = QWidget()
        edit_layout = QVBoxLayout(edit_widget)
        
        edit_form = QHBoxLayout()
        edit_form.addWidget(QLabel("名称:"))
        self.edit_name = QLineEdit()
        edit_form.addWidget(self.edit_name)
        edit_form.addStretch()
        edit_layout.addLayout(edit_form)
        
        edit_layout.addWidget(QLabel("描述:"))
        self.edit_desc = QTextEdit()
        self.edit_desc.setMaximumHeight(80)
        edit_layout.addWidget(self.edit_desc)
        
        edit_layout.addWidget(QLabel("作者:"))
        self.edit_author = QLineEdit()
        edit_layout.addWidget(self.edit_author)
        
        edit_layout.addWidget(QLabel("标签 (逗号分隔):"))
        self.edit_tags = QLineEdit()
        edit_layout.addWidget(self.edit_tags)
        
        edit_layout.addWidget(QLabel("配置 (JSON):"))
        self.edit_config = QTextEdit()
        self.edit_config.setStyleSheet("font-family: Consolas, monospace;")
        edit_layout.addWidget(self.edit_config)
        
        edit_btn_layout = QHBoxLayout()
        self.save_edit_btn = QPushButton("💾 保存")
        self.save_edit_btn.setObjectName("primaryButton")
        self.save_edit_btn.clicked.connect(self.save_edited_template)
        edit_btn_layout.addWidget(self.save_edit_btn)
        
        self.cancel_edit_btn = QPushButton("取消")
        self.cancel_edit_btn.clicked.connect(self.cancel_edit)
        edit_btn_layout.addWidget(self.cancel_edit_btn)
        edit_btn_layout.addStretch()
        edit_layout.addLayout(edit_btn_layout)
        
        tabs.addTab(edit_widget, "✏️ 编辑")
        
        right_layout.addWidget(tabs)
        
        btn_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("📥 导入")
        self.import_btn.clicked.connect(self.import_template)
        btn_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("📤 导出")
        self.export_btn.clicked.connect(self.export_template)
        btn_layout.addWidget(self.export_btn)
        
        self.duplicate_btn = QPushButton("📋 复制")
        self.duplicate_btn.clicked.connect(self.duplicate_template)
        btn_layout.addWidget(self.duplicate_btn)
        
        btn_layout.addStretch()
        
        self.use_btn = QPushButton("✅ 使用模板")
        self.use_btn.setObjectName("primaryButton")
        self.use_btn.clicked.connect(self.use_template)
        btn_layout.addWidget(self.use_btn)
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.close_btn)
        
        right_layout.addLayout(btn_layout)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 600])
        
        layout.addWidget(splitter)
    
    def load_templates(self):
        self.template_list.clear()
        
        device_type = None
        if self.device_combo.currentText() != "全部":
            device_map = {"华为": "huawei", "H3C": "h3c"}
            device_type = device_map.get(self.device_combo.currentText())
        
        keyword = self.search_input.text().strip()
        
        if keyword:
            templates = self.template_manager.search_templates(keyword, device_type)
        else:
            templates = self.template_manager.get_templates(device_type)
        
        for template in templates:
            item = QListWidgetItem(f"{'🔒 ' if template.is_builtin else '📝 '}{template.name}")
            item.setData(Qt.UserRole, f"{template.device_type}_{template.name}")
            
            if template.device_type == "huawei":
                item.setForeground(Qt.darkBlue)
            else:
                item.setForeground(Qt.darkGreen)
            
            self.template_list.addItem(item)
    
    def on_device_filter_changed(self):
        self.load_templates()
    
    def on_search_changed(self):
        self.load_templates()
    
    def on_template_selected(self, current, previous):
        if not current:
            return
        
        key = current.data(Qt.UserRole)
        device_type, name = key.split("_", 1)
        
        self.current_template = self.template_manager.get_template(name, device_type)
        
        if self.current_template:
            self.name_input.setText(self.current_template.name)
            self.device_label.setText("华为" if self.current_template.device_type == "huawei" else "H3C")
            self.desc_input.setPlainText(self.current_template.description)
            self.tags_label.setText(", ".join(self.current_template.tags))
            
            import json
            self.config_preview.setPlainText(json.dumps(self.current_template.config, ensure_ascii=False, indent=2))
            
            self.author_label.setText(f"作者: {self.current_template.author or '未知'}")
            self.time_label.setText(f"创建: {self.current_template.created_time}")
            
            self.delete_btn.setEnabled(not self.current_template.is_builtin)
    
    def on_template_double_clicked(self, item):
        self.use_template()
    
    def create_template(self):
        name, ok = QInputDialog.getText(self, "新建模板", "请输入模板名称:")
        if ok and name:
            template = Template(
                name=name,
                device_type=self.device_type,
                description="新建模板",
                config={"basic": {}},
                tags=["自定义"]
            )
            
            if self.template_manager.save_template(template):
                QMessageBox.information(self, "成功", f"模板 '{name}' 创建成功！")
                self.load_templates()
            else:
                QMessageBox.warning(self, "失败", "创建模板失败，名称可能已存在。")
    
    def delete_template(self):
        if not self.current_template:
            return
        
        if self.current_template.is_builtin:
            QMessageBox.warning(self, "无法删除", "内置模板不能删除！")
            return
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除模板 '{self.current_template.name}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.template_manager.delete_template(self.current_template.name, self.current_template.device_type):
                QMessageBox.information(self, "成功", "模板已删除！")
                self.load_templates()
    
    def duplicate_template(self):
        if not self.current_template:
            return
        
        new_name, ok = QInputDialog.getText(
            self, "复制模板",
            "请输入新模板名称:",
            text=f"{self.current_template.name}_副本"
        )
        
        if ok and new_name:
            if self.template_manager.duplicate_template(
                self.current_template.name, self.current_template.device_type, new_name
            ):
                QMessageBox.information(self, "成功", f"模板已复制为 '{new_name}'！")
                self.load_templates()
    
    def import_template(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入模板", "", "JSON文件 (*.json)"
        )
        
        if file_path:
            if self.template_manager.import_template(file_path):
                QMessageBox.information(self, "成功", "模板导入成功！")
                self.load_templates()
            else:
                QMessageBox.warning(self, "失败", "导入模板失败，请检查文件格式。")
    
    def export_template(self):
        if not self.current_template:
            QMessageBox.warning(self, "提示", "请先选择一个模板！")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出模板",
            f"{self.current_template.name}.json",
            "JSON文件 (*.json)"
        )
        
        if file_path:
            if self.template_manager.export_template(
                self.current_template.name, self.current_template.device_type, file_path
            ):
                QMessageBox.information(self, "成功", "模板导出成功！")
    
    def save_edited_template(self):
        if not self.current_template:
            return
        
        import json
        
        try:
            config = json.loads(self.edit_config.toPlainText())
        except json.JSONDecodeError:
            QMessageBox.warning(self, "错误", "配置JSON格式错误！")
            return
        
        new_name = self.edit_name.text().strip()
        if new_name and new_name != self.current_template.name:
            self.template_manager.rename_template(
                self.current_template.name, new_name, self.current_template.device_type
            )
            self.current_template.name = new_name
        
        self.current_template.description = self.edit_desc.toPlainText()
        self.current_template.author = self.edit_author.text()
        self.current_template.config = config
        self.current_template.tags = [t.strip() for t in self.edit_tags.text().split(",") if t.strip()]
        
        if self.template_manager.save_template(self.current_template):
            QMessageBox.information(self, "成功", "模板保存成功！")
            self.load_templates()
    
    def cancel_edit(self):
        if self.current_template:
            self.edit_name.setText(self.current_template.name)
            self.edit_desc.setPlainText(self.current_template.description)
            self.edit_author.setText(self.current_template.author)
            self.edit_tags.setText(", ".join(self.current_template.tags))
            import json
            self.edit_config.setPlainText(json.dumps(self.current_template.config, ensure_ascii=False, indent=2))
    
    def use_template(self):
        if not self.current_template:
            QMessageBox.warning(self, "提示", "请先选择一个模板！")
            return
        
        self.template_selected.emit({
            "name": self.current_template.name,
            "device_type": self.current_template.device_type,
            "config": self.current_template.config
        })
        self.close()


class SaveTemplateDialog(QDialog):
    """保存配置为模板对话框"""
    
    def __init__(self, parent=None, config: dict = None, device_type: str = "huawei"):
        super().__init__(parent)
        self.config = config or {}
        self.device_type = device_type
        self.template_manager = TemplateManager()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("保存为模板")
        self.setFixedSize(450, 350)
        self.setStyleSheet(MODERN_STYLE + DIALOG_STYLE)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        header = QLabel("💾 保存配置为模板")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976D2;")
        layout.addWidget(header)
        
        form_layout = QVBoxLayout()
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("模板名称:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("输入模板名称")
        name_layout.addWidget(self.name_input)
        form_layout.addLayout(name_layout)
        
        form_layout.addWidget(QLabel("描述:"))
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("输入模板描述...")
        self.desc_input.setMaximumHeight(80)
        form_layout.addWidget(self.desc_input)
        
        author_layout = QHBoxLayout()
        author_layout.addWidget(QLabel("作者:"))
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("可选")
        author_layout.addWidget(self.author_input)
        form_layout.addLayout(author_layout)
        
        tags_layout = QHBoxLayout()
        tags_layout.addWidget(QLabel("标签:"))
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("标签1, 标签2, ...")
        tags_layout.addWidget(self.tags_input)
        form_layout.addLayout(tags_layout)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("保存")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self.save_template)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def save_template(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "错误", "请输入模板名称！")
            return
        
        template = Template(
            name=name,
            device_type=self.device_type,
            description=self.desc_input.toPlainText(),
            config=self.config,
            author=self.author_input.text(),
            tags=[t.strip() for t in self.tags_input.text().split(",") if t.strip()]
        )
        
        if self.template_manager.save_template(template):
            QMessageBox.information(self, "成功", f"模板 '{name}' 保存成功！")
            self.accept()
        else:
            QMessageBox.warning(self, "失败", "保存模板失败，名称可能已存在。")
