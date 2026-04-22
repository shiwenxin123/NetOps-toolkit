#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络工具窗口 - Ping测试
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTextEdit, QGroupBox,
                             QSpinBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QCheckBox, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.network_tools import PingTool
from gui.tool_styles import (
    TOOL_LABEL_STYLE, TOOL_LABEL_SECONDARY,
    TOOL_BUTTON_PRIMARY, TOOL_BUTTON_DANGER, TOOL_BUTTON_GHOST,
    TOOL_STATUS_SUCCESS, TOOL_STATUS_ERROR, TOOL_STATUS_INFO,
    RESULT_HEADER, RESULT_FOOTER,
    apply_tool_style
)


class PingWorker(QThread):
    """Ping工作线程"""
    result_ready = pyqtSignal(dict)
    batch_result_ready = pyqtSignal(list)
    
    def __init__(self, host, count=4, timeout=2):
        super().__init__()
        self.host = host
        self.count = count
        self.timeout = timeout
        self.batch_hosts = []
        self.is_batch = False
    
    def set_batch(self, hosts, count=2, timeout=2):
        self.batch_hosts = hosts
        self.count = count
        self.timeout = timeout
        self.is_batch = True
    
    def run(self):
        if self.is_batch:
            results = PingTool.ping_list(self.batch_hosts, self.count, self.timeout)
            self.batch_result_ready.emit(results)
        else:
            result = PingTool.ping(self.host, self.count, self.timeout)
            self.result_ready.emit(result)


class PingTestWidget(QWidget):
    """Ping测试工具"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.initUI()
    
    def initUI(self):
        apply_tool_style(self)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel("🔔 Ping 网络连通性测试")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976D2; padding: 5px 0;")
        layout.addWidget(title_label)
        
        single_group = QGroupBox("单主机 Ping 测试")
        single_layout = QVBoxLayout(single_group)
        single_layout.setSpacing(10)
        
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        
        host_label = QLabel("目标主机:")
        host_label.setStyleSheet(TOOL_LABEL_STYLE)
        row1.addWidget(host_label)
        
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("输入 IP 地址或域名，如: 8.8.8.8 或 baidu.com")
        self.host_input.setText("8.8.8.8")
        row1.addWidget(self.host_input)
        
        count_label = QLabel("次数:")
        count_label.setStyleSheet(TOOL_LABEL_STYLE)
        row1.addWidget(count_label)
        
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 100)
        self.count_spin.setValue(4)
        self.count_spin.setMinimumWidth(70)
        row1.addWidget(self.count_spin)
        
        timeout_label = QLabel("超时(s):")
        timeout_label.setStyleSheet(TOOL_LABEL_STYLE)
        row1.addWidget(timeout_label)
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 30)
        self.timeout_spin.setValue(2)
        self.timeout_spin.setMinimumWidth(70)
        row1.addWidget(self.timeout_spin)
        
        self.ping_btn = QPushButton("▶ 开始 Ping")
        self.ping_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.ping_btn.clicked.connect(self.start_ping)
        row1.addWidget(self.ping_btn)
        
        single_layout.addLayout(row1)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Consolas", 10))
        self.result_text.setMinimumHeight(180)
        self.result_text.setPlaceholderText("Ping 测试结果将显示在这里...")
        single_layout.addWidget(self.result_text)
        
        layout.addWidget(single_group)
        
        batch_group = QGroupBox("批量 Ping 测试")
        batch_layout = QVBoxLayout(batch_group)
        batch_layout.setSpacing(10)
        
        batch_row = QHBoxLayout()
        batch_row.setSpacing(8)
        
        batch_label = QLabel("主机列表:")
        batch_label.setStyleSheet(TOOL_LABEL_STYLE)
        batch_row.addWidget(batch_label)
        
        self.batch_input = QLineEdit()
        self.batch_input.setPlaceholderText("多个 IP/域名用逗号分隔，如: 192.168.1.1, google.com, 1.1.1.1")
        self.batch_input.setText("8.8.8.8, 8.8.4.4, 1.1.1.1")
        batch_row.addWidget(self.batch_input)
        
        self.batch_btn = QPushButton("📋 批量测试")
        self.batch_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.batch_btn.clicked.connect(self.start_batch_ping)
        batch_row.addWidget(self.batch_btn)
        
        self.stop_btn = QPushButton("⏹ 停止")
        self.stop_btn.setStyleSheet(TOOL_BUTTON_DANGER)
        self.stop_btn.clicked.connect(self.stop_ping)
        self.stop_btn.setEnabled(False)
        batch_row.addWidget(self.stop_btn)
        
        batch_layout.addLayout(batch_row)
        
        self.batch_table = QTableWidget()
        self.batch_table.setColumnCount(6)
        self.batch_table.setHorizontalHeaderLabels(["主机", "状态", "发送", "接收", "丢失率", "平均延迟"])
        self.batch_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.batch_table.setMinimumHeight(200)
        batch_layout.addWidget(self.batch_table)
        
        layout.addWidget(batch_group)
        
        self.status_bar = QLabel("就绪")
        self.status_bar.setStyleSheet("color: #666666; padding: 5px; font-size: 12px;")
        layout.addWidget(self.status_bar)
    
    def start_ping(self):
        host = self.host_input.text().strip()
        
        if not host:
            QMessageBox.warning(self, "警告", "请输入目标主机")
            return
        
        self.ping_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_bar.setStyleSheet(TOOL_STATUS_INFO)
        self.status_bar.setText(f"正在 Ping {host}...")
        self.result_text.setPlainText(f"正在 Ping {host}...\n")
        
        self.worker = PingWorker(host, self.count_spin.value(), self.timeout_spin.value())
        self.worker.result_ready.connect(self.on_ping_result)
        self.worker.finished.connect(self.on_ping_finished)
        self.worker.start()
    
    def start_batch_ping(self):
        hosts_text = self.batch_input.text().strip()
        
        if not hosts_text:
            QMessageBox.warning(self, "警告", "请输入主机列表")
            return
        
        hosts = [h.strip() for h in hosts_text.split(',') if h.strip()]
        
        if not hosts:
            QMessageBox.warning(self, "警告", "请输入有效的主机列表")
            return
        
        self.batch_btn.setEnabled(False)
        self.ping_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_bar.setStyleSheet(TOOL_STATUS_INFO)
        self.status_bar.setText(f"正在批量测试 {len(hosts)} 个主机...")
        
        self.batch_table.setRowCount(len(hosts))
        for i, host in enumerate(hosts):
            self.batch_table.setItem(i, 0, QTableWidgetItem(host))
            item = QTableWidgetItem("⏳ 测试中...")
            item.setForeground(QColor("#fbbf24"))
            self.batch_table.setItem(i, 1, item)
            for j in range(2, 6):
                self.batch_table.setItem(i, j, QTableWidgetItem("-"))
        
        self.worker = PingWorker()
        self.worker.set_batch(hosts, 2, self.timeout_spin.value())
        self.worker.batch_result_ready.connect(self.on_batch_result)
        self.worker.finished.connect(self.on_ping_finished)
        self.worker.start()
    
    def on_ping_result(self, result):
        host = result["host"]
        
        if result["success"]:
            txt = f"""
{' RESULT ':-^50}
📡 Ping 测试结果: {host}
{'─' * 50}
🎯 目标 IP:     {result.get('ip_address', host)}
📦 发送包数:   {result['packets_sent']}
📬 接收包数:   {result['packets_received']}
📉 丢包率:      {result['loss_rate']:.1f}%
⚡ 最小延迟:    {result['min_time']:.1f} ms
🚀 最大延迟:    {result['max_time']:.1f} ms
📊 平均延迟:    {result['avg_time']:.1f} ms
{'─' * 50}
✅ 状态: 主机可达
"""
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText(f"✅ {host} 可达，平均延迟: {result['avg_time']:.1f}ms")
        else:
            txt = f"""
{' RESULT ':-^50}
📡 Ping 测试结果: {host}
{'─' * 50}
❌ 状态: 主机不可达
⚠️ 错误: {result.get('error', '未知错误')}
{'─' * 50}
"""
            self.status_bar.setStyleSheet(TOOL_STATUS_ERROR)
            self.status_bar.setText(f"❌ {host} 不可达")
        
        self.result_text.setPlainText(txt)
    
    def on_batch_result(self, results):
        for i, result in enumerate(results):
            host = result["host"]
            
            self.batch_table.setItem(i, 0, QTableWidgetItem(host))
            
            if result["success"]:
                status_item = QTableWidgetItem("✅ 可达")
                status_item.setForeground(QColor("#4ade80"))
                self.batch_table.setItem(i, 1, status_item)
                self.batch_table.setItem(i, 2, QTableWidgetItem(str(result['packets_sent'])))
                self.batch_table.setItem(i, 3, QTableWidgetItem(str(result['packets_received'])))
                self.batch_table.setItem(i, 4, QTableWidgetItem(f"{result['loss_rate']:.1f}%"))
                self.batch_table.setItem(i, 5, QTableWidgetItem(f"{result['avg_time']:.1f}ms"))
            else:
                status_item = QTableWidgetItem("❌ 不可达")
                status_item.setForeground(QColor("#f87171"))
                self.batch_table.setItem(i, 1, status_item)
                for j in range(2, 6):
                    self.batch_table.setItem(i, j, QTableWidgetItem("-"))
        
        self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
        self.status_bar.setText(f"✅ 批量测试完成，共 {len(results)} 个主机")
    
    def on_ping_finished(self):
        self.ping_btn.setEnabled(True)
        self.batch_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def stop_ping(self):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            self.status_bar.setStyleSheet(TOOL_STATUS_WARNING)
            self.status_bar.setText("⚠️ 已停止测试")
        self.on_ping_finished()
