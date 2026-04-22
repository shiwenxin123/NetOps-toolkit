#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络工具窗口 - 编码转换器
"""

import base64
import urllib.parse
import binascii
import hashlib
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTextEdit, QGroupBox,
                             QComboBox, QTabWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gui.tool_styles import (
    TOOL_LABEL_STYLE, TOOL_LABEL_SECONDARY,
    TOOL_BUTTON_PRIMARY, TOOL_BUTTON_DANGER, TOOL_BUTTON_GHOST,
    TOOL_STATUS_SUCCESS, TOOL_STATUS_ERROR, TOOL_STATUS_INFO,
    apply_tool_style
)


class EncoderToolWidget(QWidget):
    """编码转换工具"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        apply_tool_style(self)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel("🔄 编码转换器")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976D2; padding: 5px 0;")
        layout.addWidget(title_label)
        
        tabs = QTabWidget()
        
        base64_widget = QWidget()
        base64_layout = QVBoxLayout(base64_widget)
        base64_layout.setSpacing(10)
        
        input_group = QGroupBox("输入文本")
        input_layout = QVBoxLayout(input_group)
        
        self.base64_input = QTextEdit()
        self.base64_input.setFont(QFont("Consolas", 10))
        self.base64_input.setPlaceholderText("输入要编码/解码的文本...")
        self.base64_input.setMaximumHeight(100)
        input_layout.addWidget(self.base64_input)
        
        base64_layout.addWidget(input_group)
        
        btn_row = QHBoxLayout()
        
        self.base64_encode_btn = QPushButton("🔒 Base64 编码")
        self.base64_encode_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.base64_encode_btn.clicked.connect(self.base64_encode)
        btn_row.addWidget(self.base64_encode_btn)
        
        self.base64_decode_btn = QPushButton("🔓 Base64 解码")
        self.base64_decode_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.base64_decode_btn.clicked.connect(self.base64_decode)
        btn_row.addWidget(self.base64_decode_btn)
        
        btn_row.addStretch()
        base64_layout.addLayout(btn_row)
        
        result_group = QGroupBox("结果")
        result_layout = QVBoxLayout(result_group)
        
        self.base64_result = QTextEdit()
        self.base64_result.setFont(QFont("Consolas", 10))
        self.base64_result.setReadOnly(True)
        self.base64_result.setMaximumHeight(100)
        result_layout.addWidget(self.base64_result)
        
        copy_btn = QPushButton("📋 复制结果")
        copy_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        copy_btn.clicked.connect(lambda: self.copy_result(self.base64_result))
        result_layout.addWidget(copy_btn)
        
        base64_layout.addWidget(result_group)
        tabs.addTab(base64_widget, "📝 Base64")
        
        url_widget = QWidget()
        url_layout = QVBoxLayout(url_widget)
        url_layout.setSpacing(10)
        
        url_input_group = QGroupBox("URL文本")
        url_input_layout = QVBoxLayout(url_input_group)
        
        self.url_input = QTextEdit()
        self.url_input.setFont(QFont("Consolas", 10))
        self.url_input.setPlaceholderText("输入URL或参数...")
        self.url_input.setMaximumHeight(100)
        url_input_layout.addWidget(self.url_input)
        
        url_layout.addWidget(url_input_group)
        
        url_btn_row = QHBoxLayout()
        
        self.url_encode_btn = QPushButton("🔒 URL 编码")
        self.url_encode_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.url_encode_btn.clicked.connect(self.url_encode)
        url_btn_row.addWidget(self.url_encode_btn)
        
        self.url_decode_btn = QPushButton("🔓 URL 解码")
        self.url_decode_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.url_decode_btn.clicked.connect(self.url_decode)
        url_btn_row.addWidget(self.url_decode_btn)
        
        self.url_full_encode_btn = QPushButton("🔒 全编码")
        self.url_full_encode_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.url_full_encode_btn.clicked.connect(self.url_full_encode)
        url_btn_row.addWidget(self.url_full_encode_btn)
        
        url_btn_row.addStretch()
        url_layout.addLayout(url_btn_row)
        
        url_result_group = QGroupBox("结果")
        url_result_layout = QVBoxLayout(url_result_group)
        
        self.url_result = QTextEdit()
        self.url_result.setFont(QFont("Consolas", 10))
        self.url_result.setReadOnly(True)
        self.url_result.setMaximumHeight(100)
        url_result_layout.addWidget(self.url_result)
        
        url_copy_btn = QPushButton("📋 复制结果")
        url_copy_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        url_copy_btn.clicked.connect(lambda: self.copy_result(self.url_result))
        url_result_layout.addWidget(url_copy_btn)
        
        url_layout.addWidget(url_result_group)
        tabs.addTab(url_widget, "🔗 URL")
        
        hex_widget = QWidget()
        hex_layout = QVBoxLayout(hex_widget)
        hex_layout.setSpacing(10)
        
        hex_input_group = QGroupBox("输入")
        hex_input_layout = QVBoxLayout(hex_input_group)
        
        self.hex_input = QTextEdit()
        self.hex_input.setFont(QFont("Consolas", 10))
        self.hex_input.setPlaceholderText("输入文本或十六进制字符串...")
        self.hex_input.setMaximumHeight(100)
        hex_input_layout.addWidget(self.hex_input)
        
        hex_layout.addWidget(hex_input_group)
        
        hex_btn_row = QHBoxLayout()
        
        self.str_to_hex_btn = QPushButton("文本 → Hex")
        self.str_to_hex_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.str_to_hex_btn.clicked.connect(self.str_to_hex)
        hex_btn_row.addWidget(self.str_to_hex_btn)
        
        self.hex_to_str_btn = QPushButton("Hex → 文本")
        self.hex_to_str_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.hex_to_str_btn.clicked.connect(self.hex_to_str)
        hex_btn_row.addWidget(self.hex_to_str_btn)
        
        hex_btn_row.addStretch()
        hex_layout.addLayout(hex_btn_row)
        
        hex_result_group = QGroupBox("结果")
        hex_result_layout = QVBoxLayout(hex_result_group)
        
        self.hex_result = QTextEdit()
        self.hex_result.setFont(QFont("Consolas", 10))
        self.hex_result.setReadOnly(True)
        self.hex_result.setMaximumHeight(100)
        hex_result_layout.addWidget(self.hex_result)
        
        hex_copy_btn = QPushButton("📋 复制结果")
        hex_copy_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        hex_copy_btn.clicked.connect(lambda: self.copy_result(self.hex_result))
        hex_result_layout.addWidget(hex_copy_btn)
        
        hex_layout.addWidget(hex_result_group)
        tabs.addTab(hex_widget, "🔢 Hex")
        
        json_widget = QWidget()
        json_layout = QVBoxLayout(json_widget)
        json_layout.setSpacing(10)
        
        json_input_group = QGroupBox("JSON输入")
        json_input_layout = QVBoxLayout(json_input_group)
        
        self.json_input = QTextEdit()
        self.json_input.setFont(QFont("Consolas", 10))
        self.json_input.setPlaceholderText('{"key": "value"}')
        self.json_input.setMaximumHeight(150)
        json_input_layout.addWidget(self.json_input)
        
        json_layout.addWidget(json_input_group)
        
        json_btn_row = QHBoxLayout()
        
        self.json_format_btn = QPushButton("✨ 格式化")
        self.json_format_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.json_format_btn.clicked.connect(self.json_format)
        json_btn_row.addWidget(self.json_format_btn)
        
        self.json_compress_btn = QPushButton("📦 压缩")
        self.json_compress_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.json_compress_btn.clicked.connect(self.json_compress)
        json_btn_row.addWidget(self.json_compress_btn)
        
        self.json_escape_btn = QPushButton("🔒 转义")
        self.json_escape_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.json_escape_btn.clicked.connect(self.json_escape)
        json_btn_row.addWidget(self.json_escape_btn)
        
        self.json_unescape_btn = QPushButton("🔓 去转义")
        self.json_unescape_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.json_unescape_btn.clicked.connect(self.json_unescape)
        json_btn_row.addWidget(self.json_unescape_btn)
        
        json_btn_row.addStretch()
        json_layout.addLayout(json_btn_row)
        
        json_result_group = QGroupBox("结果")
        json_result_layout = QVBoxLayout(json_result_group)
        
        self.json_result = QTextEdit()
        self.json_result.setFont(QFont("Consolas", 10))
        self.json_result.setReadOnly(True)
        self.json_result.setMaximumHeight(150)
        json_result_layout.addWidget(self.json_result)
        
        json_copy_btn = QPushButton("📋 复制结果")
        json_copy_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        json_copy_btn.clicked.connect(lambda: self.copy_result(self.json_result))
        json_result_layout.addWidget(json_copy_btn)
        
        json_layout.addWidget(json_result_group)
        tabs.addTab(json_widget, "📄 JSON")
        
        hash_widget = QWidget()
        hash_layout = QVBoxLayout(hash_widget)
        hash_layout.setSpacing(10)
        
        hash_input_group = QGroupBox("输入文本")
        hash_input_layout = QVBoxLayout(hash_input_group)
        
        self.hash_input = QTextEdit()
        self.hash_input.setFont(QFont("Consolas", 10))
        self.hash_input.setPlaceholderText("输入要计算哈希的文本...")
        self.hash_input.setMaximumHeight(80)
        hash_input_layout.addWidget(self.hash_input)
        
        hash_layout.addWidget(hash_input_group)
        
        hash_btn_row = QHBoxLayout()
        
        self.hash_calc_btn = QPushButton("🔍 计算哈希")
        self.hash_calc_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.hash_calc_btn.clicked.connect(self.calculate_hashes)
        hash_btn_row.addWidget(self.hash_calc_btn)
        
        hash_btn_row.addStretch()
        hash_layout.addLayout(hash_btn_row)
        
        hash_result_group = QGroupBox("哈希值")
        hash_result_layout = QVBoxLayout(hash_result_group)
        
        self.hash_result = QTextEdit()
        self.hash_result.setFont(QFont("Consolas", 10))
        self.hash_result.setReadOnly(True)
        hash_result_layout.addWidget(self.hash_result)
        
        hash_layout.addWidget(hash_result_group)
        tabs.addTab(hash_widget, "#️⃣ Hash")
        
        layout.addWidget(tabs)
        
        self.status_bar = QLabel("就绪")
        self.status_bar.setStyleSheet("color: #666666; padding: 5px; font-size: 12px;")
        layout.addWidget(self.status_bar)
    
    def base64_encode(self):
        try:
            text = self.base64_input.toPlainText()
            encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
            self.base64_result.setPlainText(encoded)
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText("✅ Base64 编码成功")
        except Exception as e:
            self.base64_result.setPlainText(f"编码失败: {str(e)}")
            self.status_bar.setStyleSheet(TOOL_STATUS_ERROR)
            self.status_bar.setText("❌ 编码失败")
    
    def base64_decode(self):
        try:
            text = self.base64_input.toPlainText().strip()
            decoded = base64.b64decode(text).decode('utf-8')
            self.base64_result.setPlainText(decoded)
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText("✅ Base64 解码成功")
        except Exception as e:
            self.base64_result.setPlainText(f"解码失败: {str(e)}")
            self.status_bar.setStyleSheet(TOOL_STATUS_ERROR)
            self.status_bar.setText("❌ 解码失败")
    
    def url_encode(self):
        try:
            text = self.url_input.toPlainText()
            encoded = urllib.parse.quote(text)
            self.url_result.setPlainText(encoded)
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText("✅ URL 编码成功")
        except Exception as e:
            self.url_result.setPlainText(f"编码失败: {str(e)}")
    
    def url_decode(self):
        try:
            text = self.url_input.toPlainText()
            decoded = urllib.parse.unquote(text)
            self.url_result.setPlainText(decoded)
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText("✅ URL 解码成功")
        except Exception as e:
            self.url_result.setPlainText(f"解码失败: {str(e)}")
    
    def url_full_encode(self):
        try:
            text = self.url_input.toPlainText()
            encoded = ''.join(f'%{ord(c):02X}' for c in text)
            self.url_result.setPlainText(encoded)
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText("✅ URL 全编码成功")
        except Exception as e:
            self.url_result.setPlainText(f"编码失败: {str(e)}")
    
    def str_to_hex(self):
        try:
            text = self.hex_input.toPlainText()
            hex_str = text.encode('utf-8').hex()
            self.hex_result.setPlainText(hex_str)
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText("✅ 转 Hex 成功")
        except Exception as e:
            self.hex_result.setPlainText(f"转换失败: {str(e)}")
    
    def hex_to_str(self):
        try:
            hex_str = self.hex_input.toPlainText().strip().replace(' ', '').replace('0x', '').replace('\\x', '')
            text = bytes.fromhex(hex_str).decode('utf-8')
            self.hex_result.setPlainText(text)
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText("✅ Hex 转文本成功")
        except Exception as e:
            self.hex_result.setPlainText(f"转换失败: {str(e)}")
    
    def json_format(self):
        try:
            text = self.json_input.toPlainText()
            data = json.loads(text)
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            self.json_result.setPlainText(formatted)
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText("✅ JSON 格式化成功")
        except Exception as e:
            self.json_result.setPlainText(f"格式化失败: {str(e)}")
    
    def json_compress(self):
        try:
            text = self.json_input.toPlainText()
            data = json.loads(text)
            compressed = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
            self.json_result.setPlainText(compressed)
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText("✅ JSON 压缩成功")
        except Exception as e:
            self.json_result.setPlainText(f"压缩失败: {str(e)}")
    
    def json_escape(self):
        try:
            text = self.json_input.toPlainText()
            escaped = json.dumps(text, ensure_ascii=False)
            self.json_result.setPlainText(escaped)
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText("✅ JSON 转义成功")
        except Exception as e:
            self.json_result.setPlainText(f"转义失败: {str(e)}")
    
    def json_unescape(self):
        try:
            text = self.json_input.toPlainText()
            unescaped = json.loads(text)
            if isinstance(unescaped, str):
                self.json_result.setPlainText(unescaped)
            else:
                self.json_result.setPlainText(json.dumps(unescaped, indent=2, ensure_ascii=False))
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText("✅ JSON 去转义成功")
        except Exception as e:
            self.json_result.setPlainText(f"去转义失败: {str(e)}")
    
    def calculate_hashes(self):
        try:
            text = self.hash_input.toPlainText()
            data = text.encode('utf-8')
            
            md5 = hashlib.md5(data).hexdigest()
            sha1 = hashlib.sha1(data).hexdigest()
            sha256 = hashlib.sha256(data).hexdigest()
            sha512 = hashlib.sha512(data).hexdigest()
            
            result = f"""
{'─' * 50}
📝 输入长度: {len(text)} 字符
{'─' * 50}

MD5:     {md5}
SHA1:    {sha1}
SHA256:  {sha256}
SHA512:  {sha512}
"""
            self.hash_result.setPlainText(result)
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText("✅ 哈希计算完成")
        except Exception as e:
            self.hash_result.setPlainText(f"计算失败: {str(e)}")
    
    def copy_result(self, text_edit):
        from PyQt5.QtWidgets import QApplication
        QApplication.clipboard().setText(text_edit.toPlainText())
        self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
        self.status_bar.setText("✅ 已复制到剪贴板")
