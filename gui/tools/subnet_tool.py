#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络工具窗口 - 子网计算器
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTextEdit, QGroupBox,
                             QComboBox, QSpinBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QTabWidget, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.network_tools import SubnetCalculator
from gui.tool_styles import (
    TOOL_LABEL_STYLE, TOOL_LABEL_SECONDARY,
    TOOL_BUTTON_PRIMARY, TOOL_BUTTON_GHOST,
    TOOL_STATUS_SUCCESS, TOOL_STATUS_ERROR,
    apply_tool_style
)


class SubnetCalculatorWidget(QWidget):
    """子网计算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        apply_tool_style(self)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel("🧮 子网计算器")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976D2; padding: 5px 0;")
        layout.addWidget(title_label)
        
        input_group = QGroupBox("子网计算")
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(10)
        
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        
        ip_label = QLabel("IP 地址:")
        ip_label.setStyleSheet(TOOL_LABEL_STYLE)
        row1.addWidget(ip_label)
        
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("例如: 192.168.1.100")
        self.ip_input.setText("192.168.1.100")
        row1.addWidget(self.ip_input)
        
        mask_label = QLabel("掩码/前缀:")
        mask_label.setStyleSheet(TOOL_LABEL_STYLE)
        row1.addWidget(mask_label)
        
        self.mask_input = QLineEdit()
        self.mask_input.setPlaceholderText("如: 255.255.255.0 或 24")
        self.mask_input.setText("24")
        self.mask_input.setMaximumWidth(150)
        row1.addWidget(self.mask_input)
        
        self.calc_btn = QPushButton("🔢 计算")
        self.calc_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.calc_btn.clicked.connect(self.calculate)
        row1.addWidget(self.calc_btn)
        
        input_layout.addLayout(row1)
        layout.addWidget(input_group)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Consolas", 10))
        self.result_text.setMinimumHeight(280)
        self.result_text.setPlaceholderText("子网计算结果将显示在这里...")
        layout.addWidget(self.result_text)
        
        tabs = QTabWidget()
        
        split_widget = QWidget()
        split_layout = QVBoxLayout(split_widget)
        split_layout.setSpacing(10)
        
        split_row = QHBoxLayout()
        split_row.setSpacing(8)
        
        split_net_label = QLabel("网络地址:")
        split_net_label.setStyleSheet(TOOL_LABEL_STYLE)
        split_row.addWidget(split_net_label)
        
        self.split_network = QLineEdit("192.168.1.0")
        split_row.addWidget(self.split_network)
        
        orig_prefix_label = QLabel("原前缀:")
        orig_prefix_label.setStyleSheet(TOOL_LABEL_STYLE)
        split_row.addWidget(orig_prefix_label)
        
        self.split_orig_prefix = QSpinBox()
        self.split_orig_prefix.setRange(0, 31)
        self.split_orig_prefix.setValue(24)
        self.split_orig_prefix.setMinimumWidth(70)
        split_row.addWidget(self.split_orig_prefix)
        
        new_prefix_label = QLabel("新前缀:")
        new_prefix_label.setStyleSheet(TOOL_LABEL_STYLE)
        split_row.addWidget(new_prefix_label)
        
        self.split_new_prefix = QSpinBox()
        self.split_new_prefix.setRange(1, 32)
        self.split_new_prefix.setValue(26)
        self.split_new_prefix.setMinimumWidth(70)
        split_row.addWidget(self.split_new_prefix)
        
        self.split_btn = QPushButton("📐 划分子网")
        self.split_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.split_btn.clicked.connect(self.split_subnet)
        split_row.addWidget(self.split_btn)
        
        split_layout.addLayout(split_row)
        
        self.split_table = QTableWidget()
        self.split_table.setColumnCount(6)
        self.split_table.setHorizontalHeaderLabels(["子网", "掩码", "首主机", "末主机", "广播地址", "主机数"])
        self.split_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.split_table.setMinimumHeight(200)
        split_layout.addWidget(self.split_table)
        
        tabs.addTab(split_widget, "📐 子网划分")
        
        cidr_widget = QWidget()
        cidr_layout = QVBoxLayout(cidr_widget)
        cidr_layout.setSpacing(10)
        
        cidr_row = QHBoxLayout()
        cidr_row.setSpacing(8)
        
        cidr_start_label = QLabel("起始 IP:")
        cidr_start_label.setStyleSheet(TOOL_LABEL_STYLE)
        cidr_row.addWidget(cidr_start_label)
        
        self.cidr_start = QLineEdit("192.168.1.1")
        cidr_row.addWidget(self.cidr_start)
        
        cidr_end_label = QLabel("结束 IP:")
        cidr_end_label.setStyleSheet(TOOL_LABEL_STYLE)
        cidr_row.addWidget(cidr_end_label)
        
        self.cidr_end = QLineEdit("192.168.1.100")
        cidr_row.addWidget(self.cidr_end)
        
        self.cidr_btn = QPushButton("🔄 转换为 CIDR")
        self.cidr_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.cidr_btn.clicked.connect(self.convert_to_cidr)
        cidr_row.addWidget(self.cidr_btn)
        
        cidr_layout.addLayout(cidr_row)
        
        self.cidr_table = QTableWidget()
        self.cidr_table.setColumnCount(5)
        self.cidr_table.setHorizontalHeaderLabels(["CIDR", "网络地址", "掩码", "广播地址", "前缀"])
        self.cidr_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cidr_table.setMinimumHeight(200)
        cidr_layout.addWidget(self.cidr_table)
        
        tabs.addTab(cidr_widget, "🔄 IP 范围转 CIDR")
        
        masks_widget = QWidget()
        masks_layout = QVBoxLayout(masks_widget)
        masks_layout.setSpacing(10)
        
        masks_header = QHBoxLayout()
        self.masks_btn = QPushButton("📋 显示所有子网掩码")
        self.masks_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.masks_btn.clicked.connect(self.show_all_masks)
        masks_header.addWidget(self.masks_btn)
        masks_header.addStretch()
        masks_layout.addLayout(masks_header)
        
        self.masks_table = QTableWidget()
        self.masks_table.setColumnCount(4)
        self.masks_table.setHorizontalHeaderLabels(["前缀", "掩码", "总主机数", "可用主机数"])
        self.masks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.masks_table.setMinimumHeight(200)
        masks_layout.addWidget(self.masks_table)
        
        tabs.addTab(masks_widget, "📋 掩码速查表")
        
        layout.addWidget(tabs)
        
        self.status_bar = QLabel("就绪")
        self.status_bar.setStyleSheet("color: #666666; padding: 5px; font-size: 12px;")
        layout.addWidget(self.status_bar)
    
    def calculate(self):
        ip = self.ip_input.text().strip()
        mask = self.mask_input.text().strip()
        
        if not ip or not mask:
            QMessageBox.warning(self, "警告", "请输入IP地址和掩码")
            return
        
        result = SubnetCalculator.calculate(ip, mask)
        
        if result["success"]:
            prefix_str = '/' + str(result['prefix_length'])
            private_str = '是' if result['is_private'] else '否'
            binary_ip = result['binary_ip']
            binary_mask = result['binary_mask']
            
            txt = f"""
{'═' * 50}
🧮 子网计算结果
{'═' * 50}
📡 IP 地址:        {result['ip_address']}
🔲 子网掩码:      {result['subnet_mask']}
📏 前缀长度:      {prefix_str}
{'─' * 50}
🌐 网络地址:      {result['network_address']}
📢 广播地址:      {result['broadcast_address']}
🎯 首个可用 IP:   {result['first_usable']}
🏁 最后可用 IP:   {result['last_usable']}
{'─' * 50}
📊 总主机数:      {result['total_hosts']:,}
✅ 可用主机数:    {result['usable_hosts']:,}
🎯 通配符掩码:    {result['wildcard_mask']}
{'─' * 50}
🏷️ IP 类别:       {result['ip_class']}
📝 IP 类型:       {result['ip_type']}
🔒 私有地址:      {private_str}
{'─' * 50}
进制 二IP:    {binary_ip[:16]}
              {binary_ip[16:]}
进制 二掩码:  {binary_mask[:16]}
              {binary_mask[16:]}
{'═' * 50}
"""
            self.result_text.setPlainText(txt)
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText("✅ 计算完成")
        else:
            self.result_text.setPlainText(f"❌ 计算失败: {result['error']}")
            self.status_bar.setStyleSheet(TOOL_STATUS_ERROR)
            self.status_bar.setText(f"❌ 计算失败")
    
    def split_subnet(self):
        network = self.split_network.text().strip()
        orig_prefix = self.split_orig_prefix.value()
        new_prefix = self.split_new_prefix.value()
        
        if new_prefix <= orig_prefix:
            QMessageBox.warning(self, "警告", "新前缀必须大于原前缀")
            return
        
        result = SubnetCalculator.split_subnet(network, orig_prefix, new_prefix)
        
        if result:
            subnets = result
            self.split_table.setRowCount(len(subnets))
            
            for i, subnet in enumerate(subnets):
                self.split_table.setItem(i, 0, QTableWidgetItem(subnet['subnet']))
                self.split_table.setItem(i, 1, QTableWidgetItem(subnet['mask']))
                self.split_table.setItem(i, 2, QTableWidgetItem(subnet.get('first_host', '-')))
                self.split_table.setItem(i, 3, QTableWidgetItem(subnet.get('last_host', '-')))
                self.split_table.setItem(i, 4, QTableWidgetItem(subnet.get('broadcast', '-')))
                self.split_table.setItem(i, 5, QTableWidgetItem(str(subnet.get('hosts', 0))))
            
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText(f"✅ 已划分为 {len(subnets)} 个子网")
        else:
            self.status_bar.setStyleSheet(TOOL_STATUS_ERROR)
            self.status_bar.setText(f"❌ 划分失败: 请检查网络地址和前缀")
    
    def convert_to_cidr(self):
        start_ip = self.cidr_start.text().strip()
        end_ip = self.cidr_end.text().strip()
        
        result = SubnetCalculator.ip_range_to_cidr(start_ip, end_ip)
        
        if result:
            cidrs = result
            self.cidr_table.setRowCount(len(cidrs))
            
            for i, cidr in enumerate(cidrs):
                self.cidr_table.setItem(i, 0, QTableWidgetItem(cidr.get('cidr', '-')))
                self.cidr_table.setItem(i, 1, QTableWidgetItem(cidr.get('network', '-')))
                self.cidr_table.setItem(i, 2, QTableWidgetItem(cidr.get('mask', '-')))
                self.cidr_table.setItem(i, 3, QTableWidgetItem(cidr.get('broadcast', '-')))
                self.cidr_table.setItem(i, 4, QTableWidgetItem(f"/{cidr.get('prefix', 0)}"))
            
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText(f"✅ 转换完成，共 {len(cidrs)} 个 CIDR 块")
        else:
            self.status_bar.setStyleSheet(TOOL_STATUS_ERROR)
            self.status_bar.setText(f"❌ 转换失败: 请检查IP范围")
    
    def show_all_masks(self):
        masks = SubnetCalculator.get_all_masks()
        
        self.masks_table.setRowCount(len(masks))
        
        for i, mask in enumerate(masks):
            prefix_item = QTableWidgetItem(f"/{mask['prefix']}")
            self.masks_table.setItem(i, 0, prefix_item)
            
            self.masks_table.setItem(i, 1, QTableWidgetItem(mask['mask']))
            self.masks_table.setItem(i, 2, QTableWidgetItem(f"{mask['total_hosts']:,}"))
            self.masks_table.setItem(i, 3, QTableWidgetItem(f"{mask['usable_hosts']:,}"))
        
        self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
        self.status_bar.setText(f"✅ 已显示所有 {len(masks)} 个子网掩码")
