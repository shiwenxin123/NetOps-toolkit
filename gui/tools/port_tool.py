#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络工具窗口 - 端口扫描
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTextEdit, QGroupBox,
                             QSpinBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QCheckBox, QComboBox,
                             QTabWidget, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.network_tools import PortScanner
from gui.tool_styles import (
    TOOL_LABEL_STYLE, TOOL_LABEL_SECONDARY,
    TOOL_BUTTON_PRIMARY, TOOL_BUTTON_DANGER, TOOL_BUTTON_GHOST,
    TOOL_STATUS_SUCCESS, TOOL_STATUS_ERROR, TOOL_STATUS_WARNING, TOOL_STATUS_INFO,
    apply_tool_style
)


class PortScanWorker(QThread):
    """端口扫描工作线程"""
    result_ready = pyqtSignal(dict)
    progress_update = pyqtSignal(str, int)
    
    def __init__(self, host, scan_type="common", start_port=1, end_port=1024, timeout=1.0):
        super().__init__()
        self.host = host
        self.scan_type = scan_type
        self.start_port = start_port
        self.end_port = end_port
        self.timeout = timeout
    
    def run(self):
        self.progress_update.emit(f"🔍 正在扫描 {self.host}...", 0)
        
        def progress_callback(current, total, open_count):
            percent = int((current / total) * 100) if total > 0 else 0
            self.progress_update.emit(
                f"🔍 扫描中... {current}/{total} ({percent}%) | 已发现 {open_count} 个开放端口",
                percent
            )
        
        if self.scan_type == "common":
            result = PortScanner.scan_common_ports(self.host, self.timeout)
        elif self.scan_type == "quick":
            result = PortScanner.scan_port_range(self.host, 1, 1024, self.timeout, 200, progress_callback)
        elif self.scan_type == "full":
            result = PortScanner.scan_full_range(self.host, self.timeout, 500, progress_callback)
        else:
            result = PortScanner.scan_port_range(self.host, self.start_port, self.end_port, self.timeout, 200, progress_callback)
        
        self.progress_update.emit("扫描完成", 100)
        self.result_ready.emit(result)


class PortScanWidget(QWidget):
    """端口扫描工具"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.initUI()
    
    def initUI(self):
        apply_tool_style(self)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel("🔍 端口扫描工具")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976D2; padding: 5px 0;")
        layout.addWidget(title_label)
        
        tabs = QTabWidget()
        
        scan_widget = QWidget()
        scan_layout = QVBoxLayout(scan_widget)
        scan_layout.setSpacing(10)
        
        input_group = QGroupBox("扫描设置")
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(10)
        
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        
        host_label = QLabel("目标主机:")
        host_label.setStyleSheet(TOOL_LABEL_STYLE)
        row1.addWidget(host_label)
        
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("IP 地址或域名，如: 192.168.1.1 或 scanme.nmap.org")
        self.host_input.setText("127.0.0.1")
        row1.addWidget(self.host_input)
        
        input_layout.addLayout(row1)
        
        row2 = QHBoxLayout()
        row2.setSpacing(8)
        
        type_label = QLabel("扫描类型:")
        type_label.setStyleSheet(TOOL_LABEL_STYLE)
        row2.addWidget(type_label)
        
        self.scan_type = QComboBox()
        self.scan_type.addItems(["🚀 常用端口 (Top 100)", "⚡ 快速扫描 (1-1024)", "🎯 指定范围", "🌐 全端口 (1-65535)"])
        self.scan_type.currentIndexChanged.connect(self.on_scan_type_changed)
        row2.addWidget(self.scan_type)
        
        timeout_label = QLabel("超时(s):")
        timeout_label.setStyleSheet(TOOL_LABEL_STYLE)
        row2.addWidget(timeout_label)
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 10)
        self.timeout_spin.setValue(1)
        self.timeout_spin.setMinimumWidth(70)
        row2.addWidget(self.timeout_spin)
        
        input_layout.addLayout(row2)
        
        self.range_widget = QWidget()
        range_layout = QHBoxLayout(self.range_widget)
        range_layout.setContentsMargins(0, 0, 0, 0)
        range_layout.setSpacing(8)
        
        range_label = QLabel("端口范围:")
        range_label.setStyleSheet(TOOL_LABEL_STYLE)
        range_layout.addWidget(range_label)
        
        self.start_port = QSpinBox()
        self.start_port.setRange(1, 65535)
        self.start_port.setValue(1)
        self.start_port.setMinimumWidth(90)
        range_layout.addWidget(self.start_port)
        
        dash_label = QLabel("-")
        dash_label.setStyleSheet(TOOL_LABEL_STYLE)
        range_layout.addWidget(dash_label)
        
        self.end_port = QSpinBox()
        self.end_port.setRange(1, 65535)
        self.end_port.setValue(1024)
        self.end_port.setMinimumWidth(90)
        range_layout.addWidget(self.end_port)
        
        range_layout.addStretch()
        
        input_layout.addWidget(self.range_widget)
        self.range_widget.hide()
        
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        
        self.scan_btn = QPushButton("🚀 开始扫描")
        self.scan_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.scan_btn.setMinimumHeight(40)
        self.scan_btn.clicked.connect(self.start_scan)
        btn_row.addWidget(self.scan_btn)
        
        self.stop_btn = QPushButton("⏹ 停止")
        self.stop_btn.setStyleSheet(TOOL_BUTTON_DANGER)
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.clicked.connect(self.stop_scan)
        self.stop_btn.setEnabled(False)
        btn_row.addWidget(self.stop_btn)
        
        self.export_btn = QPushButton("📋 导出结果")
        self.export_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.export_btn.setMinimumHeight(40)
        self.export_btn.clicked.connect(self.export_results)
        btn_row.addWidget(self.export_btn)
        
        btn_row.addStretch()
        
        input_layout.addLayout(btn_row)
        scan_layout.addWidget(input_group)
        
        progress_row = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximumHeight(20)
        progress_row.addWidget(self.progress_bar)
        scan_layout.addLayout(progress_row)
        
        result_group = QGroupBox("扫描结果")
        result_layout = QVBoxLayout(result_group)
        result_layout.setSpacing(8)
        
        self.stats_label = QLabel("等待扫描...")
        self.stats_label.setStyleSheet("color: #666666; font-size: 12px;")
        result_layout.addWidget(self.stats_label)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["端口", "状态", "服务", "Banner"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.result_table.setMinimumHeight(250)
        result_layout.addWidget(self.result_table)
        
        scan_layout.addWidget(result_group)
        
        tabs.addTab(scan_widget, "🔍 端口扫描")
        
        quick_widget = QWidget()
        quick_layout = QVBoxLayout(quick_widget)
        quick_layout.setSpacing(10)
        
        quick_group = QGroupBox("快速端口测试")
        quick_inner_layout = QVBoxLayout(quick_group)
        quick_inner_layout.setSpacing(10)
        
        quick_row1 = QHBoxLayout()
        quick_row1.setSpacing(8)
        
        quick_host_label = QLabel("主机:")
        quick_host_label.setStyleSheet(TOOL_LABEL_STYLE)
        quick_row1.addWidget(quick_host_label)
        
        self.quick_host = QLineEdit()
        self.quick_host.setPlaceholderText("IP 地址或域名")
        self.quick_host.setText("127.0.0.1")
        quick_row1.addWidget(self.quick_host)
        
        quick_inner_layout.addLayout(quick_row1)
        
        quick_row2 = QHBoxLayout()
        quick_row2.setSpacing(8)
        
        quick_port_label = QLabel("端口:")
        quick_port_label.setStyleSheet(TOOL_LABEL_STYLE)
        quick_row2.addWidget(quick_port_label)
        
        self.quick_port = QSpinBox()
        self.quick_port.setRange(1, 65535)
        self.quick_port.setValue(80)
        self.quick_port.setMinimumWidth(90)
        quick_row2.addWidget(self.quick_port)
        
        common_ports_label = QLabel("常用端口:")
        common_ports_label.setStyleSheet(TOOL_LABEL_STYLE)
        quick_row2.addWidget(common_ports_label)
        
        self.common_ports_combo = QComboBox()
        self.common_ports_combo.addItems([
            "自定义", "HTTP (80)", "HTTPS (443)", "SSH (22)", 
            "FTP (21)", "Telnet (23)", "SMTP (25)", "DNS (53)",
            "POP3 (110)", "IMAP (143)", "RDP (3389)", "MySQL (3306)",
            "PostgreSQL (5432)", "Redis (6379)", "MongoDB (27017)"
        ])
        self.common_ports_combo.currentIndexChanged.connect(self.on_common_port_selected)
        quick_row2.addWidget(self.common_ports_combo)
        
        quick_row2.addStretch()
        
        self.quick_test_btn = QPushButton("⚡ 测试连接")
        self.quick_test_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.quick_test_btn.clicked.connect(self.quick_test)
        quick_row2.addWidget(self.quick_test_btn)
        
        quick_inner_layout.addLayout(quick_row2)
        
        quick_layout.addWidget(quick_group)
        
        self.quick_result = QTextEdit()
        self.quick_result.setReadOnly(True)
        self.quick_result.setFont(QFont("Consolas", 10))
        self.quick_result.setMinimumHeight(300)
        self.quick_result.setPlaceholderText("测试结果将显示在这里...")
        quick_layout.addWidget(self.quick_result)
        
        tabs.addTab(quick_widget, "⚡ 快速测试")
        
        batch_widget = QWidget()
        batch_layout = QVBoxLayout(batch_widget)
        batch_layout.setSpacing(10)
        
        batch_group = QGroupBox("批量端口检测")
        batch_inner = QVBoxLayout(batch_group)
        batch_inner.setSpacing(10)
        
        batch_row1 = QHBoxLayout()
        batch_row1.setSpacing(8)
        
        batch_host_label = QLabel("主机:")
        batch_host_label.setStyleSheet(TOOL_LABEL_STYLE)
        batch_row1.addWidget(batch_host_label)
        
        self.batch_host = QLineEdit()
        self.batch_host.setPlaceholderText("IP 地址或域名")
        self.batch_host.setText("127.0.0.1")
        batch_row1.addWidget(self.batch_host)
        
        batch_inner.addLayout(batch_row1)
        
        batch_row2 = QHBoxLayout()
        batch_row2.setSpacing(8)
        
        ports_label = QLabel("端口列表:")
        ports_label.setStyleSheet(TOOL_LABEL_STYLE)
        batch_row2.addWidget(ports_label)
        
        self.batch_ports = QLineEdit()
        self.batch_ports.setPlaceholderText("多个端口用逗号分隔，如: 22,80,443,3306")
        self.batch_ports.setText("22,80,443,3306,3389")
        batch_row2.addWidget(self.batch_ports)
        
        self.batch_test_btn = QPushButton("📋 批量检测")
        self.batch_test_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.batch_test_btn.clicked.connect(self.batch_test)
        batch_row2.addWidget(self.batch_test_btn)
        
        batch_inner.addLayout(batch_row2)
        
        batch_layout.addWidget(batch_group)
        
        self.batch_result = QTextEdit()
        self.batch_result.setReadOnly(True)
        self.batch_result.setFont(QFont("Consolas", 10))
        self.batch_result.setMinimumHeight(300)
        self.batch_result.setPlaceholderText("批量检测结果将显示在这里...")
        batch_layout.addWidget(self.batch_result)
        
        tabs.addTab(batch_widget, "📋 批量检测")
        
        layout.addWidget(tabs)
        
        self.status_bar = QLabel("就绪")
        self.status_bar.setStyleSheet("color: #666666; padding: 5px; font-size: 12px;")
        layout.addWidget(self.status_bar)
    
    def on_scan_type_changed(self, index):
        if index == 2:
            self.range_widget.show()
        else:
            self.range_widget.hide()
    
    def on_common_port_selected(self, index):
        port_map = {
            0: None, 1: 80, 2: 443, 3: 22, 4: 21, 5: 23, 6: 25, 7: 53,
            8: 110, 9: 143, 10: 3389, 11: 3306, 12: 5432, 13: 6379, 14: 27017
        }
        if index > 0:
            self.quick_port.setValue(port_map[index])
    
    def start_scan(self):
        host = self.host_input.text().strip()
        
        if not host:
            QMessageBox.warning(self, "警告", "请输入目标主机")
            return
        
        scan_types = ["common", "quick", "range", "full"]
        scan_type = scan_types[self.scan_type.currentIndex()]
        
        self.scan_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.result_table.setRowCount(0)
        self.progress_bar.setValue(0)
        self.stats_label.setStyleSheet(TOOL_STATUS_INFO)
        self.stats_label.setText("🔍 正在扫描...")
        self.status_bar.setStyleSheet(TOOL_STATUS_INFO)
        self.status_bar.setText(f"正在扫描 {host}...")
        
        self.worker = PortScanWorker(
            host, scan_type,
            self.start_port.value(),
            self.end_port.value(),
            float(self.timeout_spin.value())
        )
        self.worker.result_ready.connect(self.on_scan_result)
        self.worker.progress_update.connect(self.on_progress)
        self.worker.finished.connect(self.on_scan_finished)
        self.worker.start()
    
    def on_progress(self, msg, percent):
        self.stats_label.setText(msg)
        self.progress_bar.setValue(percent)
    
    def on_scan_result(self, result):
        if result["success"]:
            open_ports = result["ports"]
            
            self.stats_label.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.stats_label.setText(
                f"✅ 扫描完成 | 总端口: {result['total_ports']} | "
                f"开放: {result['open_ports']} | 关闭: {result['closed_ports']} | "
                f"过滤: {result['filtered_ports']}"
            )
            
            self.result_table.setRowCount(len(open_ports))
            
            for i, port in enumerate(open_ports):
                port_item = QTableWidgetItem(f"{port['port']}")
                self.result_table.setItem(i, 0, port_item)
                
                status_item = QTableWidgetItem("✅ 开放")
                status_item.setForeground(QColor("#4ade80"))
                self.result_table.setItem(i, 1, status_item)
                
                service_item = QTableWidgetItem(port.get('service', '未知'))
                self.result_table.setItem(i, 2, service_item)
                
                banner_item = QTableWidgetItem(port.get('banner', '-'))
                self.result_table.setItem(i, 3, banner_item)
            
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText(f"✅ 发现 {len(open_ports)} 个开放端口")
        else:
            self.stats_label.setStyleSheet(TOOL_STATUS_ERROR)
            self.stats_label.setText(f"❌ 扫描失败: {result.get('error', '未知错误')}")
            self.status_bar.setStyleSheet(TOOL_STATUS_ERROR)
            self.status_bar.setText(f"❌ 扫描失败")
    
    def on_scan_finished(self):
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def stop_scan(self):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            self.stats_label.setStyleSheet(TOOL_STATUS_WARNING)
            self.stats_label.setText("⚠️ 扫描已停止")
        self.on_scan_finished()
    
    def quick_test(self):
        host = self.quick_host.text().strip()
        port = self.quick_port.value()
        
        if not host:
            QMessageBox.warning(self, "警告", "请输入目标主机")
            return
        
        result = PortScanner.test_port(host, port, 2.0)
        
        if result["open"]:
            txt = f"""
{'─' * 50}
✅ 端口测试结果
{'─' * 50}
📡 主机: {host}
🔢 端口: {port}
📊 状态: 开放
🔧 服务: {result.get('service', '未知')}
{'─' * 50}
"""
            self.quick_result.setPlainText(txt)
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText(f"✅ 端口 {port} 开放")
        else:
            txt = f"""
{'─' * 50}
❌ 端口测试结果
{'─' * 50}
📡 主机: {host}
🔢 端口: {port}
📊 状态: 关闭或被过滤
{'─' * 50}
"""
            self.quick_result.setPlainText(txt)
            self.status_bar.setStyleSheet(TOOL_STATUS_ERROR)
            self.status_bar.setText(f"❌ 端口 {port} 关闭")
    
    def batch_test(self):
        host = self.batch_host.text().strip()
        ports_text = self.batch_ports.text().strip()
        
        if not host:
            QMessageBox.warning(self, "警告", "请输入目标主机")
            return
        
        if not ports_text:
            QMessageBox.warning(self, "警告", "请输入端口列表")
            return
        
        try:
            ports = [int(p.strip()) for p in ports_text.split(',') if p.strip()]
        except ValueError:
            QMessageBox.warning(self, "警告", "端口格式错误，请输入数字")
            return
        
        txt = f"{'─' * 50}\n📋 批量端口检测结果\n{'─' * 50}\n📡 主机: {host}\n{'─' * 50}\n\n"
        
        open_count = 0
        for port in ports:
            result = PortScanner.test_port(host, port, 2.0)
            if result["open"]:
                txt += f"✅ 端口 {port:5d} | 开放   | {result.get('service', '未知')}\n"
                open_count += 1
            else:
                txt += f"❌ 端口 {port:5d} | 关闭\n"
        
        txt += f"\n{'─' * 50}\n📊 统计: 开放 {open_count}/{len(ports)} 个端口\n{'─' * 50}"
        
        self.batch_result.setPlainText(txt)
        self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
        self.status_bar.setText(f"✅ 批量检测完成，开放 {open_count}/{len(ports)} 个端口")
    
    def export_results(self):
        if self.result_table.rowCount() == 0:
            QMessageBox.warning(self, "警告", "没有可导出的结果")
            return
        
        from PyQt5.QtWidgets import QApplication
        txt = f"端口扫描结果 - {self.host_input.text()}\n{'=' * 50}\n\n"
        
        for row in range(self.result_table.rowCount()):
            port = self.result_table.item(row, 0).text()
            status = self.result_table.item(row, 1).text()
            service = self.result_table.item(row, 2).text()
            banner = self.result_table.item(row, 3).text()
            txt += f"端口: {port}\t状态: {status}\t服务: {service}\tBanner: {banner}\n"
        
        QApplication.clipboard().setText(txt)
        self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
        self.status_bar.setText("✅ 结果已复制到剪贴板")
