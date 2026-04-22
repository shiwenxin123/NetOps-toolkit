#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络工具窗口 - DNS查询和其他工具
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTextEdit, QGroupBox,
                             QComboBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QTabWidget, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.network_tools import DNSTool, WhoisTool, NetworkInfo, IPAddressConverter
from gui.tool_styles import (
    TOOL_LABEL_STYLE, TOOL_LABEL_SECONDARY,
    TOOL_BUTTON_PRIMARY, TOOL_BUTTON_GHOST,
    TOOL_STATUS_SUCCESS, TOOL_STATUS_ERROR,
    apply_tool_style
)


class DNSToolWidget(QWidget):
    """DNS查询工具"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        apply_tool_style(self)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel("🌐 DNS 查询工具集")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976D2; padding: 5px 0;")
        layout.addWidget(title_label)
        
        tabs = QTabWidget()
        
        lookup_widget = QWidget()
        lookup_layout = QVBoxLayout(lookup_widget)
        lookup_layout.setSpacing(10)
        
        input_row = QHBoxLayout()
        input_row.setSpacing(8)
        
        domain_label = QLabel("域名:")
        domain_label.setStyleSheet(TOOL_LABEL_STYLE)
        input_row.addWidget(domain_label)
        
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("例如: baidu.com")
        self.domain_input.setText("baidu.com")
        input_row.addWidget(self.domain_input)
        
        type_label = QLabel("记录类型:")
        type_label.setStyleSheet(TOOL_LABEL_STYLE)
        input_row.addWidget(type_label)
        
        self.record_type = QComboBox()
        self.record_type.addItems(["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"])
        input_row.addWidget(self.record_type)
        
        self.lookup_btn = QPushButton("🔍 查询")
        self.lookup_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.lookup_btn.clicked.connect(self.do_lookup)
        input_row.addWidget(self.lookup_btn)
        
        self.lookup_all_btn = QPushButton("📋 查询所有")
        self.lookup_all_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.lookup_all_btn.clicked.connect(self.do_lookup_all)
        input_row.addWidget(self.lookup_all_btn)
        
        lookup_layout.addLayout(input_row)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Consolas", 10))
        self.result_text.setMinimumHeight(250)
        self.result_text.setPlaceholderText("查询结果将显示在这里...")
        lookup_layout.addWidget(self.result_text)
        
        tabs.addTab(lookup_widget, "DNS 查询")
        
        reverse_widget = QWidget()
        reverse_layout = QVBoxLayout(reverse_widget)
        reverse_layout.setSpacing(10)
        
        rev_row = QHBoxLayout()
        rev_row.setSpacing(8)
        
        reverse_ip_label = QLabel("IP地址:")
        reverse_ip_label.setStyleSheet(TOOL_LABEL_STYLE)
        rev_row.addWidget(reverse_ip_label)
        
        self.reverse_ip = QLineEdit()
        self.reverse_ip.setPlaceholderText("例如: 8.8.8.8")
        self.reverse_ip.setText("8.8.8.8")
        rev_row.addWidget(self.reverse_ip)
        
        self.reverse_btn = QPushButton("🔄 反向查询")
        self.reverse_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.reverse_btn.clicked.connect(self.do_reverse_lookup)
        rev_row.addWidget(self.reverse_btn)
        
        reverse_layout.addLayout(rev_row)
        
        self.reverse_result = QTextEdit()
        self.reverse_result.setReadOnly(True)
        self.reverse_result.setFont(QFont("Consolas", 10))
        self.reverse_result.setMinimumHeight(250)
        self.reverse_result.setPlaceholderText("反向DNS查询结果将显示在这里...")
        reverse_layout.addWidget(self.reverse_result)
        
        tabs.addTab(reverse_widget, "反向 DNS")
        
        whois_widget = QWidget()
        whois_layout = QVBoxLayout(whois_widget)
        whois_layout.setSpacing(10)
        
        whois_row = QHBoxLayout()
        whois_row.setSpacing(8)
        
        whois_label = QLabel("域名:")
        whois_label.setStyleSheet(TOOL_LABEL_STYLE)
        whois_row.addWidget(whois_label)
        
        self.whois_domain = QLineEdit()
        self.whois_domain.setPlaceholderText("例如: google.com")
        whois_row.addWidget(self.whois_domain)
        
        self.whois_btn = QPushButton("📋 Whois 查询")
        self.whois_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.whois_btn.clicked.connect(self.do_whois)
        whois_row.addWidget(self.whois_btn)
        
        whois_layout.addLayout(whois_row)
        
        self.whois_result = QTextEdit()
        self.whois_result.setReadOnly(True)
        self.whois_result.setFont(QFont("Consolas", 9))
        self.whois_result.setMinimumHeight(250)
        self.whois_result.setPlaceholderText("Whois 域名注册信息将显示在这里...")
        whois_layout.addWidget(self.whois_result)
        
        tabs.addTab(whois_widget, "Whois 查询")
        
        layout.addWidget(tabs)
        
        self.status_bar = QLabel("就绪")
        self.status_bar.setStyleSheet("color: #666666; padding: 5px; font-size: 12px;")
        layout.addWidget(self.status_bar)
    
    def do_lookup(self):
        domain = self.domain_input.text().strip()
        record_type = self.record_type.currentText()
        
        if not domain:
            QMessageBox.warning(self, "警告", "请输入域名")
            return
        
        result = DNSTool.lookup(domain, record_type)
        
        if result["success"]:
            txt = f"""
{'─' * 50}
📡 DNS 查询结果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 域名: {domain}
📝 记录类型: {record_type}
🕐 查询时间: {result['query_time']}
{'─' * 50}
"""
            if isinstance(result["records"], list):
                for record in result["records"]:
                    if isinstance(record, dict):
                        txt += f"  优先级: {record.get('priority', '-')}  服务器: {record.get('server', record)}\n"
                    else:
                        txt += f"  📍 {record}\n"
            else:
                txt += f"  {result['records']}"
            
            self.result_text.setPlainText(txt)
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText(f"✅ 查询成功")
        else:
            self.result_text.setPlainText(f"❌ 查询失败: {result['error']}")
            self.status_bar.setStyleSheet(TOOL_STATUS_ERROR)
            self.status_bar.setText(f"❌ 查询失败")
    
    def do_lookup_all(self):
        domain = self.domain_input.text().strip()
        
        if not domain:
            QMessageBox.warning(self, "警告", "请输入域名")
            return
        
        result = DNSTool.lookup_all(domain)
        
        txt = f"""
{'─' * 50}
📡 DNS 完整查询结果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 域名: {domain}
"""
        
        if result["A"]:
            txt += f"\n📍 A 记录 (IPv4):\n"
            for ip in result["A"]:
                txt += f"   {ip}\n"
        
        if result["AAAA"]:
            txt += f"\n📍 AAAA 记录 (IPv6):\n"
            for ip in result["AAAA"]:
                txt += f"   {ip}\n"
        
        if result["MX"]:
            txt += f"\n📧 MX 记录 (邮件服务器):\n"
            for mx in result["MX"]:
                txt += f"   优先级 {mx['priority']}: {mx['server']}\n"
        
        if result["NS"]:
            txt += f"\n🖥️ NS 记录 (域名服务器):\n"
            for ns in result["NS"]:
                txt += f"   {ns}\n"
        
        if result["TXT"]:
            txt += f"\n📄 TXT 记录:\n"
            for txt_record in result["TXT"]:
                txt += f"   {txt_record}\n"
        
        if result["CNAME"]:
            txt += f"\n🔗 CNAME 记录: {result['CNAME']}\n"
        
        if result["errors"]:
            txt += f"\n⚠️ 错误信息:\n"
            for error in result["errors"]:
                txt += f"   {error}\n"
        
        self.result_text.setPlainText(txt)
        self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
        self.status_bar.setText(f"✅ 完整查询成功")
    
    def do_reverse_lookup(self):
        ip = self.reverse_ip.text().strip()
        
        if not ip:
            QMessageBox.warning(self, "警告", "请输入IP地址")
            return
        
        result = DNSTool.reverse_lookup(ip)
        
        if result["success"]:
            from datetime import datetime
            txt = f"""
{'─' * 50}
🔄 反向 DNS 查询结果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📡 IP 地址: {ip}
🕐 查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'─' * 50}

🌐 主机名: {result.get('hostname', '未找到')}
"""
            if result.get("aliases"):
                txt += f"\n📎 别名:\n"
                for alias in result["aliases"]:
                    txt += f"   {alias}\n"
            
            self.reverse_result.setPlainText(txt)
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText(f"✅ 反向查询成功")
        else:
            self.reverse_result.setPlainText(f"❌ 查询失败: {result['error']}")
            self.status_bar.setStyleSheet(TOOL_STATUS_ERROR)
            self.status_bar.setText(f"❌ 查询失败")
    
    def do_whois(self):
        domain = self.whois_domain.text().strip()
        
        if not domain:
            QMessageBox.warning(self, "警告", "请输入域名")
            return
        
        result = WhoisTool.query(domain)
        
        if result["success"]:
            self.whois_result.setPlainText(str(result.get("raw_output", "")))
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText(f"✅ Whois 查询成功")
        else:
            self.whois_result.setPlainText(f"❌ 查询失败: {result.get('error', '未知错误')}")
            self.status_bar.setStyleSheet(TOOL_STATUS_ERROR)
            self.status_bar.setText(f"❌ 查询失败")


class NetworkInfoWidget(QWidget):
    """网络信息工具"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        apply_tool_style(self)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel("🖥️ 网络信息")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976D2; padding: 5px 0;")
        layout.addWidget(title_label)
        
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        
        self.refresh_btn = QPushButton("🔄 刷新信息")
        self.refresh_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.refresh_btn.clicked.connect(self.refresh_info)
        btn_row.addWidget(self.refresh_btn)
        
        btn_row.addStretch()
        layout.addLayout(btn_row)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setFont(QFont("Consolas", 10))
        self.info_text.setMinimumHeight(400)
        self.info_text.setPlaceholderText("点击刷新获取网络信息...")
        layout.addWidget(self.info_text)
        
        self.status_bar = QLabel("就绪")
        self.status_bar.setStyleSheet("color: #666666; padding: 5px; font-size: 12px;")
        layout.addWidget(self.status_bar)
        
        self.refresh_info()
    
    def refresh_info(self):
        """刷新网络信息"""
        import socket
        import platform
        
        info = f"""
{'═' * 50}
🖥️ 网络信息
{'═' * 50}

📍 系统信息:
   操作系统: {platform.system()} {platform.release()}
   主机名: {socket.gethostname()}
   
📡 网络配置:
"""
        
        try:
            hostname = socket.gethostname()
            local_ips = socket.gethostbyname_ex(hostname)[2]
            for ip in local_ips:
                info += f"   本地 IP: {ip}\n"
        except Exception as e:
            info += f"   获取失败: {e}\n"
        
        info += f"""
{'─' * 50}
   公网 IP: 请通过网络服务获取
{'═' * 50}
"""
        
        self.info_text.setPlainText(info)
        self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
        self.status_bar.setText("✅ 信息已刷新")


class IPConverterWidget(QWidget):
    """IP 地址转换工具"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        apply_tool_style(self)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel("🔄 IP 地址转换")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976D2; padding: 5px 0;")
        layout.addWidget(title_label)
        
        decimal_group = QGroupBox("十进制转换")
        decimal_layout = QVBoxLayout(decimal_group)
        decimal_layout.setSpacing(8)
        
        dec_row = QHBoxLayout()
        dec_row.setSpacing(8)
        
        dec_label = QLabel("十进制数:")
        dec_label.setStyleSheet(TOOL_LABEL_STYLE)
        dec_row.addWidget(dec_label)
        
        self.dec_input = QLineEdit()
        self.dec_input.setPlaceholderText("输入十进制 IP 数，如: 3232235521")
        dec_row.addWidget(self.dec_input)
        
        self.dec_to_ip_btn = QPushButton("→ IP")
        self.dec_to_ip_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.dec_to_ip_btn.clicked.connect(self.dec_to_ip)
        dec_row.addWidget(self.dec_to_ip_btn)
        
        decimal_layout.addLayout(dec_row)
        layout.addWidget(decimal_group)
        
        hex_group = QGroupBox("十六进制转换")
        hex_layout = QVBoxLayout(hex_group)
        hex_layout.setSpacing(8)
        
        hex_row = QHBoxLayout()
        hex_row.setSpacing(8)
        
        hex_label = QLabel("十六进制:")
        hex_label.setStyleSheet(TOOL_LABEL_STYLE)
        hex_row.addWidget(hex_label)
        
        self.hex_input = QLineEdit()
        self.hex_input.setPlaceholderText("输入十六进制，如: C0A80001")
        hex_row.addWidget(self.hex_input)
        
        self.hex_to_ip_btn = QPushButton("→ IP")
        self.hex_to_ip_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.hex_to_ip_btn.clicked.connect(self.hex_to_ip)
        hex_row.addWidget(self.hex_input)
        
        hex_layout.addLayout(hex_row)
        layout.addWidget(hex_group)
        
        ip_group = QGroupBox("IP 地址转换")
        ip_layout = QVBoxLayout(ip_group)
        ip_layout.setSpacing(8)
        
        ip_row = QHBoxLayout()
        ip_row.setSpacing(8)
        
        ip_label = QLabel("IP 地址:")
        ip_label.setStyleSheet(TOOL_LABEL_STYLE)
        ip_row.addWidget(ip_label)
        
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("如: 192.168.0.1")
        ip_row.addWidget(self.ip_input)
        
        self.ip_to_dec_btn = QPushButton("→ 十进制")
        self.ip_to_dec_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.ip_to_dec_btn.clicked.connect(self.ip_to_dec)
        ip_row.addWidget(self.ip_to_dec_btn)
        
        self.ip_to_hex_btn = QPushButton("→ 十六进制")
        self.ip_to_hex_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.ip_to_hex_btn.clicked.connect(self.ip_to_hex)
        ip_row.addWidget(self.ip_to_hex_btn)
        
        ip_layout.addLayout(ip_row)
        layout.addWidget(ip_group)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Consolas", 10))
        self.result_text.setMinimumHeight(150)
        self.result_text.setPlaceholderText("转换结果将显示在这里...")
        layout.addWidget(self.result_text)
        
        self.status_bar = QLabel("就绪")
        self.status_bar.setStyleSheet("color: #666666; padding: 5px; font-size: 12px;")
        layout.addWidget(self.status_bar)
    
    def dec_to_ip(self):
        """十进制转IP"""
        try:
            num = int(self.dec_input.text().strip())
            ip = IPAddressConverter.decimal_to_ip(num)
            self.result_text.setPlainText(f"✅ 转换结果:\n   十进制: {num}\n   IP 地址: {ip}")
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText("✅ 转换成功")
        except Exception as e:
            QMessageBox.warning(self, "警告", f"请输入有效的十进制数")
    
    def hex_to_ip(self):
        """十六进制转IP"""
        hex_str = self.hex_input.text().strip()
        if not hex_str:
            QMessageBox.warning(self, "警告", "请输入十六进制数")
            return
        
        result = IPAddressConverter.hex_to_ip(hex_str)
        if result["success"]:
            self.result_text.setPlainText(f"✅ 转换结果:\n   十六进制: {hex_str}\n   IP 地址: {result['ip']}")
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText("✅ 转换成功")
        else:
            QMessageBox.warning(self, "警告", "请输入有效的十六进制数")
    
    def ip_to_dec(self):
        """IP转十进制"""
        ip = self.ip_input.text().strip()
        if not ip:
            QMessageBox.warning(self, "警告", "请输入IP地址")
            return
        
        result = IPAddressConverter.ip_to_decimal(ip)
        if result["success"]:
            self.result_text.setPlainText(f"✅ 转换结果:\n   IP 地址: {ip}\n   十进制: {result['decimal']}")
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText("✅ 转换成功")
        else:
            QMessageBox.warning(self, "警告", "请输入有效的IP地址")
    
    def ip_to_hex(self):
        """IP转十六进制"""
        ip = self.ip_input.text().strip()
        if not ip:
            QMessageBox.warning(self, "警告", "请输入IP地址")
            return
        
        result = IPAddressConverter.ip_to_hex(ip)
        if result["success"]:
            self.result_text.setPlainText(f"✅ 转换结果:\n   IP 地址: {ip}\n   十六进制: {result['hex'].upper()}")
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText("✅ 转换成功")
        else:
            QMessageBox.warning(self, "警告", "请输入有效的IP地址")
