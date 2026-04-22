#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络工具窗口 - MAC地址查询
"""

import re
from urllib.request import urlopen
from urllib.error import URLError
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTextEdit, QGroupBox,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gui.tool_styles import (
    TOOL_LABEL_STYLE, TOOL_LABEL_SECONDARY,
    TOOL_BUTTON_PRIMARY, TOOL_BUTTON_GHOST,
    TOOL_STATUS_SUCCESS, TOOL_STATUS_ERROR, TOOL_STATUS_INFO,
    apply_tool_style
)


class MACLookupWorker(QThread):
    """MAC地址查询工作线程"""
    result_ready = pyqtSignal(dict)
    
    def __init__(self, mac):
        super().__init__()
        self.mac = mac
    
    def run(self):
        result = {
            "success": False,
            "mac": self.mac,
            "vendor": "",
            "address": "",
            "country": "",
            "error": ""
        }
        
        try:
            clean_mac = self.clean_mac(self.mac)
            oui = clean_mac[:6].upper()
            
            local_oui_db = {
                "001A2C": {"vendor": "Huawei", "country": "China"},
                "001A2D": {"vendor": "Huawei", "country": "China"},
                "002568": {"vendor": "Huawei", "country": "China"},
                "00E0FC": {"vendor": "Huawei", "country": "China"},
                "001E10": {"vendor": "H3C", "country": "China"},
                "000FE2": {"vendor": "H3C", "country": "China"},
                "001FC6": {"vendor": "H3C", "country": "China"},
                "00000C": {"vendor": "Cisco", "country": "USA"},
                "001007": {"vendor": "Cisco", "country": "USA"},
                "0018BA": {"vendor": "Cisco", "country": "USA"},
                "001C0D": {"vendor": "Cisco", "country": "USA"},
                "00234E": {"vendor": "Cisco", "country": "USA"},
                "002414": {"vendor": "Cisco", "country": "USA"},
                "001B2B": {"vendor": "Dell", "country": "USA"},
                "001C23": {"vendor": "Dell", "country": "USA"},
                "0023AE": {"vendor": "Dell", "country": "USA"},
                "000BCD": {"vendor": "Dell", "country": "USA"},
                "0050B6": {"vendor": "Dell", "country": "USA"},
                "001FF3": {"vendor": "Dell", "country": "USA"},
                "000393": {"vendor": "Apple", "country": "USA"},
                "000502": {"vendor": "Apple", "country": "USA"},
                "001124": {"vendor": "Apple", "country": "USA"},
                "0017F2": {"vendor": "Apple", "country": "USA"},
                "001E52": {"vendor": "Apple", "country": "USA"},
                "0021E9": {"vendor": "Apple", "country": "USA"},
                "002312": {"vendor": "Apple", "country": "USA"},
                "002436": {"vendor": "Apple", "country": "USA"},
                "002500": {"vendor": "Apple", "country": "USA"},
                "002608": {"vendor": "Apple", "country": "USA"},
                "00264A": {"vendor": "Apple", "country": "USA"},
                "14E6E4": {"vendor": "Apple", "country": "USA"},
                "98E0D9": {"vendor": "Apple", "country": "USA"},
                "000BB4": {"vendor": "Intel", "country": "USA"},
                "000CD5": {"vendor": "Intel", "country": "USA"},
                "001111": {"vendor": "Intel", "country": "USA"},
                "0012F0": {"vendor": "Intel", "country": "USA"},
                "001302": {"vendor": "Intel", "country": "USA"},
                "001676": {"vendor": "Intel", "country": "USA"},
                "001AE8": {"vendor": "Intel", "country": "USA"},
                "001B21": {"vendor": "Intel", "country": "USA"},
                "001CBE": {"vendor": "Intel", "country": "USA"},
                "001E64": {"vendor": "Intel", "country": "USA"},
                "001FF0": {"vendor": "Intel", "country": "USA"},
                "0020F3": {"vendor": "Intel", "country": "USA"},
                "00248C": {"vendor": "Intel", "country": "USA"},
                "00265C": {"vendor": "Intel", "country": "USA"},
                "E8611F": {"vendor": "Intel", "country": "USA"},
                "000AF7": {"vendor": "HP", "country": "USA"},
                "001083": {"vendor": "HP", "country": "USA"},
                "0011FB": {"vendor": "HP", "country": "USA"},
                "0014C2": {"vendor": "HP", "country": "USA"},
                "001635": {"vendor": "HP", "country": "USA"},
                "001702": {"vendor": "HP", "country": "USA"},
                "0018FE": {"vendor": "HP", "country": "USA"},
                "001BB9": {"vendor": "HP", "country": "USA"},
                "001E0B": {"vendor": "HP", "country": "USA"},
                "0021CC": {"vendor": "HP", "country": "USA"},
                "002324": {"vendor": "HP", "country": "USA"},
                "0024E8": {"vendor": "HP", "country": "USA"},
                "0025B3": {"vendor": "HP", "country": "USA"},
                "00268A": {"vendor": "HP", "country": "USA"},
                "948BB6": {"vendor": "HP", "country": "USA"},
                "001D09": {"vendor": "Juniper", "country": "USA"},
                "001F12": {"vendor": "Juniper", "country": "USA"},
                "00226F": {"vendor": "Juniper", "country": "USA"},
                "002283": {"vendor": "Juniper", "country": "USA"},
                "002319": {"vendor": "Juniper", "country": "USA"},
                "0026BB": {"vendor": "Juniper", "country": "USA"},
                "020008": {"vendor": "Juniper", "country": "USA"},
                "002423": {"vendor": "D-Link", "country": "Taiwan"},
                "00055B": {"vendor": "D-Link", "country": "Taiwan"},
                "000D88": {"vendor": "D-Link", "country": "Taiwan"},
                "001195": {"vendor": "D-Link", "country": "Taiwan"},
                "001346": {"vendor": "D-Link", "country": "Taiwan"},
                "0015E9": {"vendor": "D-Link", "country": "Taiwan"},
                "00179A": {"vendor": "D-Link", "country": "Taiwan"},
                "001B11": {"vendor": "D-Link", "country": "Taiwan"},
                "001CF6": {"vendor": "D-Link", "country": "Taiwan"},
                "001E58": {"vendor": "D-Link", "country": "Taiwan"},
                "0011FB": {"vendor": "TP-Link", "country": "China"},
                "001E58": {"vendor": "TP-Link", "country": "China"},
                "002275": {"vendor": "TP-Link", "country": "China"},
                "0023CD": {"vendor": "TP-Link", "country": "China"},
                "002522": {"vendor": "TP-Link", "country": "China"},
                "0026C6": {"vendor": "TP-Link", "country": "China"},
                "00310E": {"vendor": "TP-Link", "country": "China"},
                "0050DA": {"vendor": "TP-Link", "country": "China"},
                "00B0D0": {"vendor": "Microsoft", "country": "USA"},
                "0014A5": {"vendor": "Microsoft", "country": "USA"},
                "0017FA": {"vendor": "Microsoft", "country": "USA"},
                "001DD8": {"vendor": "Microsoft", "country": "USA"},
                "00215C": {"vendor": "Microsoft", "country": "USA"},
                "0023A4": {"vendor": "Microsoft", "country": "USA"},
                "00260B": {"vendor": "Microsoft", "country": "USA"},
                "7C1E52": {"vendor": "Microsoft", "country": "USA"},
                "001B63": {"vendor": "Netgear", "country": "USA"},
                "000FB5": {"vendor": "Netgear", "country": "USA"},
                "00146C": {"vendor": "Netgear", "country": "USA"},
                "00184D": {"vendor": "Netgear", "country": "USA"},
                "001E2A": {"vendor": "Netgear", "country": "USA"},
                "001F33": {"vendor": "Netgear", "country": "USA"},
                "00223F": {"vendor": "Netgear", "country": "USA"},
                "0024B2": {"vendor": "Netgear", "country": "USA"},
                "008EF2": {"vendor": "Netgear", "country": "USA"},
                "A021B7": {"vendor": "Netgear", "country": "USA"},
                "E0469A": {"vendor": "Netgear", "country": "USA"},
                "00268C": {"vendor": "ZTE", "country": "China"},
                "002719": {"vendor": "ZTE", "country": "China"},
                "002902": {"vendor": "ZTE", "country": "China"},
                "001E10": {"vendor": "ZTE", "country": "China"},
                "0023EB": {"vendor": "ZTE", "country": "China"},
                "001C44": {"vendor": "ZTE", "country": "China"},
                "000DE9": {"vendor": "Samsung", "country": "Korea"},
                "0011F6": {"vendor": "Samsung", "country": "Korea"},
                "0014A8": {"vendor": "Samsung", "country": "Korea"},
                "0017C9": {"vendor": "Samsung", "country": "Korea"},
                "001A8A": {"vendor": "Samsung", "country": "Korea"},
                "001CB3": {"vendor": "Samsung", "country": "Korea"},
                "001E7D": {"vendor": "Samsung", "country": "Korea"},
                "0021A4": {"vendor": "Samsung", "country": "Korea"},
                "0023D8": {"vendor": "Samsung", "country": "Korea"},
                "002538": {"vendor": "Samsung", "country": "Korea"},
                "002673": {"vendor": "Samsung", "country": "Korea"},
            }
            
            if oui in local_oui_db:
                result["success"] = True
                result["vendor"] = local_oui_db[oui]["vendor"]
                result["country"] = local_oui_db[oui]["country"]
                result["address"] = f"{local_oui_db[oui]['vendor']} ({local_oui_db[oui]['country']})"
            else:
                result["success"] = True
                result["vendor"] = "未知厂商"
                result["country"] = "未知"
                result["error"] = "OUI不在本地数据库中"
            
        except Exception as e:
            result["error"] = str(e)
        
        self.result_ready.emit(result)
    
    def clean_mac(self, mac):
        return re.sub(r'[^A-Fa-f0-9]', '', mac.upper())


class MACToolWidget(QWidget):
    """MAC地址工具"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.initUI()
    
    def initUI(self):
        apply_tool_style(self)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel("📀 MAC地址查询")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976D2; padding: 5px 0;")
        layout.addWidget(title_label)
        
        input_group = QGroupBox("MAC地址查询")
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(10)
        
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        
        mac_label = QLabel("MAC地址:")
        mac_label.setStyleSheet(TOOL_LABEL_STYLE)
        row1.addWidget(mac_label)
        
        self.mac_input = QLineEdit()
        self.mac_input.setPlaceholderText("支持多种格式: 00:1A:2B:3C:4D:5E / 00-1A-2B-3C-4D-5E / 001A2B3C4D5E")
        row1.addWidget(self.mac_input)
        
        self.lookup_btn = QPushButton("🔍 查询厂商")
        self.lookup_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.lookup_btn.clicked.connect(self.lookup_mac)
        row1.addWidget(self.lookup_btn)
        
        input_layout.addLayout(row1)
        layout.addWidget(input_group)
        
        format_group = QGroupBox("MAC格式转换")
        format_layout = QVBoxLayout(format_group)
        
        self.format_result = QTextEdit()
        self.format_result.setFont(QFont("Consolas", 10))
        self.format_result.setReadOnly(True)
        self.format_result.setMaximumHeight(150)
        format_layout.addWidget(self.format_result)
        
        format_btn_row = QHBoxLayout()
        
        self.format_colon_btn = QPushButton("冒号格式")
        self.format_colon_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.format_colon_btn.clicked.connect(lambda: self.format_mac(':'))
        format_btn_row.addWidget(self.format_colon_btn)
        
        self.format_hyphen_btn = QPushButton("短横格式")
        self.format_hyphen_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.format_hyphen_btn.clicked.connect(lambda: self.format_mac('-'))
        format_btn_row.addWidget(self.format_hyphen_btn)
        
        self.format_dot_btn = QPushButton("点格式")
        self.format_dot_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.format_dot_btn.clicked.connect(lambda: self.format_mac('.'))
        format_btn_row.addWidget(self.format_dot_btn)
        
        self.format_none_btn = QPushButton("无分隔符")
        self.format_none_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.format_none_btn.clicked.connect(lambda: self.format_mac(''))
        format_btn_row.addWidget(self.format_none_btn)
        
        format_btn_row.addStretch()
        
        format_layout.addLayout(format_btn_row)
        layout.addWidget(format_group)
        
        result_group = QGroupBox("查询结果")
        result_layout = QVBoxLayout(result_group)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["MAC地址", "厂商", "国家", "状态"])
        self.result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.result_table.setMinimumHeight(200)
        result_layout.addWidget(self.result_table)
        
        layout.addWidget(result_group)
        
        self.status_bar = QLabel("就绪")
        self.status_bar.setStyleSheet("color: #666666; padding: 5px; font-size: 12px;")
        layout.addWidget(self.status_bar)
    
    def lookup_mac(self):
        mac = self.mac_input.text().strip()
        
        if not mac:
            return
        
        self.lookup_btn.setEnabled(False)
        self.status_bar.setStyleSheet(TOOL_STATUS_INFO)
        self.status_bar.setText("正在查询...")
        
        self.worker = MACLookupWorker(mac)
        self.worker.result_ready.connect(self.on_result)
        self.worker.finished.connect(lambda: self.lookup_btn.setEnabled(True))
        self.worker.start()
    
    def on_result(self, result):
        row = self.result_table.rowCount()
        self.result_table.insertRow(row)
        
        mac_item = QTableWidgetItem(result["mac"])
        self.result_table.setItem(row, 0, mac_item)
        
        vendor_item = QTableWidgetItem(result.get("vendor", "-"))
        if result["success"]:
            vendor_item.setForeground(QColor("#4ade80"))
        else:
            vendor_item.setForeground(QColor("#f87171"))
        self.result_table.setItem(row, 1, vendor_item)
        
        country_item = QTableWidgetItem(result.get("country", "-"))
        self.result_table.setItem(row, 2, country_item)
        
        status_text = "✅ 已识别" if result["success"] else "❌ 未识别"
        status_item = QTableWidgetItem(status_text)
        status_item.setForeground(QColor("#4ade80") if result["success"] else QColor("#fbbf24"))
        self.result_table.setItem(row, 3, status_item)
        
        if result["success"]:
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText(f"✅ 厂商: {result['vendor']}")
        else:
            self.status_bar.setStyleSheet(TOOL_STATUS_ERROR)
            self.status_bar.setText(f"❌ 未找到厂商信息")
    
    def format_mac(self, separator):
        mac = self.mac_input.text().strip()
        
        if not mac:
            return
        
        clean = re.sub(r'[^A-Fa-f0-9]', '', mac.upper())
        
        if len(clean) < 12:
            self.format_result.setPlainText("❌ MAC地址格式无效")
            return
        
        clean = clean[:12]
        
        if separator == ':':
            formatted = ':'.join(clean[i:i+2] for i in range(0, 12, 2))
        elif separator == '-':
            formatted = '-'.join(clean[i:i+2] for i in range(0, 12, 2))
        elif separator == '.':
            formatted = '.'.join(clean[i:i+4] for i in range(0, 12, 4))
        else:
            formatted = clean
        
        result_text = f"""
{'─' * 50}
📝 MAC地址格式转换
{'─' * 50}
原始输入: {mac}

冒号格式: {':'.join(clean[i:i+2] for i in range(0, 12, 2))}
短横格式: {'-'.join(clean[i:i+2] for i in range(0, 12, 2))}
点格式:   {'.'.join(clean[i:i+4] for i in range(0, 12, 4))}
无分隔符: {clean}

OUI (前3字节): {clean[:6]}
{'─' * 50}
"""
        self.format_result.setPlainText(result_text)
        self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
        self.status_bar.setText("✅ 格式转换完成")
