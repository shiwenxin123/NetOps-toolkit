#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络工具窗口 - 路由跟踪
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTextEdit, QGroupBox,
                             QSpinBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.network_tools import TraceRoute
from gui.tool_styles import (
    TOOL_LABEL_STYLE, TOOL_LABEL_SECONDARY,
    TOOL_BUTTON_PRIMARY, TOOL_BUTTON_DANGER, TOOL_BUTTON_GHOST,
    TOOL_STATUS_SUCCESS, TOOL_STATUS_ERROR, TOOL_STATUS_WARNING,
    apply_tool_style
)


class TraceWorker(QThread):
    """路由跟踪工作线程"""
    result_ready = pyqtSignal(dict)
    progress_update = pyqtSignal(str)
    
    def __init__(self, host, max_hops=30, timeout=2):
        super().__init__()
        self.host = host
        self.max_hops = max_hops
        self.timeout = timeout
    
    def run(self):
        self.progress_update.emit(f"🔍 正在追踪到 {self.host} 的路由...")
        result = TraceRoute.traceroute(self.host, self.max_hops, self.timeout)
        self.result_ready.emit(result)


class TraceRouteWidget(QWidget):
    """路由跟踪工具"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.initUI()
    
    def initUI(self):
        apply_tool_style(self)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel("🛤️ 路由跟踪工具")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976D2; padding: 5px 0;")
        layout.addWidget(title_label)
        
        input_group = QGroupBox("追踪设置")
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(10)
        
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        
        host_label = QLabel("目标主机:")
        host_label.setStyleSheet(TOOL_LABEL_STYLE)
        row1.addWidget(host_label)
        
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("IP 地址或域名")
        self.host_input.setText("www.baidu.com")
        row1.addWidget(self.host_input)
        
        hops_label = QLabel("最大跳数:")
        hops_label.setStyleSheet(TOOL_LABEL_STYLE)
        row1.addWidget(hops_label)
        
        self.max_hops = QSpinBox()
        self.max_hops.setRange(1, 64)
        self.max_hops.setValue(30)
        self.max_hops.setMinimumWidth(70)
        row1.addWidget(self.max_hops)
        
        timeout_label = QLabel("超时(s):")
        timeout_label.setStyleSheet(TOOL_LABEL_STYLE)
        row1.addWidget(timeout_label)
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 30)
        self.timeout_spin.setValue(2)
        self.timeout_spin.setMinimumWidth(70)
        row1.addWidget(self.timeout_spin)
        
        self.trace_btn = QPushButton("🚀 开始追踪")
        self.trace_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.trace_btn.clicked.connect(self.start_trace)
        row1.addWidget(self.trace_btn)
        
        self.stop_btn = QPushButton("⏹ 停止")
        self.stop_btn.setStyleSheet(TOOL_BUTTON_DANGER)
        self.stop_btn.clicked.connect(self.stop_trace)
        self.stop_btn.setEnabled(False)
        row1.addWidget(self.stop_btn)
        
        input_layout.addLayout(row1)
        layout.addWidget(input_group)
        
        self.status_label = QLabel("等待追踪...")
        self.status_label.setStyleSheet("color: #666666; padding: 8px; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(["跳数", "IP 地址", "主机名", "平均延迟", "状态"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.result_table.setMinimumHeight(300)
        layout.addWidget(self.result_table)
        
        self.raw_output = QTextEdit()
        self.raw_output.setReadOnly(True)
        self.raw_output.setFont(QFont("Consolas", 9))
        self.raw_output.setMinimumHeight(120)
        self.raw_output.setVisible(False)
        layout.addWidget(self.raw_output)
        
        btn_row = QHBoxLayout()
        self.toggle_raw_btn = QPushButton("📄 显示原始输出")
        self.toggle_raw_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.toggle_raw_btn.clicked.connect(self.toggle_raw_output)
        btn_row.addWidget(self.toggle_raw_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
    
    def start_trace(self):
        host = self.host_input.text().strip()
        
        if not host:
            QMessageBox.warning(self, "警告", "请输入目标主机")
            return
        
        self.trace_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.result_table.setRowCount(0)
        self.status_label.setStyleSheet(TOOL_STATUS_WARNING)
        self.status_label.setText(f"🔍 正在追踪到 {host} 的路由...")
        self.raw_output.clear()
        
        self.worker = TraceWorker(host, self.max_hops.value(), self.timeout_spin.value())
        self.worker.result_ready.connect(self.on_trace_result)
        self.worker.progress_update.connect(self.on_progress)
        self.worker.finished.connect(self.on_trace_finished)
        self.worker.start()
    
    def on_progress(self, msg):
        self.status_label.setText(msg)
    
    def on_trace_result(self, result):
        if result.get("success") or result.get("hops"):
            hops = result["hops"]
            
            if result.get("reached_destination"):
                status = "✅ 已到达目标"
            else:
                status = "❌ 未到达目标"
            
            self.status_label.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_label.setText(
                f"✅ 追踪完成 | 目标: {result['host']} ({result.get('ip_address', 'N/A')}) | "
                f"总跳数: {result['total_hops']} | {status}"
            )
            
            self.result_table.setRowCount(len(hops))
            
            for i, hop in enumerate(hops):
                hop_item = QTableWidgetItem(str(hop.get("hop_number", i+1)))
                self.result_table.setItem(i, 0, hop_item)
                
                ip = hop.get("ip", "")
                if hop.get("timeout"):
                    ip_item = QTableWidgetItem("* * * 超时 * * *")
                    ip_item.setForeground(QColor("#fbbf24"))
                else:
                    ip_item = QTableWidgetItem(ip)
                    if ip:
                        ip_item.setForeground(QColor("#4ade80"))
                self.result_table.setItem(i, 1, ip_item)
                
                self.result_table.setItem(i, 2, QTableWidgetItem(hop.get("hostname", "-")))
                self.result_table.setItem(i, 3, QTableWidgetItem(f"{hop.get('avg_rtt', 0):.1f}ms"))
                
                if hop.get("reached"):
                    status_item = QTableWidgetItem("✅ 到达")
                    status_item.setForeground(QColor("#4ade80"))
                elif hop.get("timeout"):
                    status_item = QTableWidgetItem("⏱️ 超时")
                    status_item.setForeground(QColor("#fbbf24"))
                else:
                    status_item = QTableWidgetItem("正常")
                self.result_table.setItem(i, 4, status_item)
            
            if result.get("raw_output"):
                self.raw_output.setPlainText(result["raw_output"])
        else:
            self.status_label.setStyleSheet(TOOL_STATUS_ERROR)
            self.status_label.setText(f"❌ 追踪失败: {result.get('error', '未知错误')}")
    
    def on_trace_finished(self):
        self.trace_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def stop_trace(self):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        self.on_trace_finished()
        self.status_label.setStyleSheet(TOOL_STATUS_WARNING)
        self.status_label.setText("⚠️ 已取消追踪")
    
    def toggle_raw_output(self):
        if self.raw_output.isVisible():
            self.raw_output.setVisible(False)
            self.toggle_raw_btn.setText("📄 显示原始输出")
        else:
            self.raw_output.setVisible(True)
            self.toggle_raw_btn.setText("📄 隐藏原始输出")
