#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NetOps Toolkit - 接口配置标签页
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QSpinBox, QCheckBox, QGroupBox,
                             QComboBox, QPushButton, QListWidget, QLabel,
                             QMessageBox, QScrollArea, QFrame)
from PyQt5.QtCore import Qt
from modules.interface_config import InterfaceConfigGenerator


class InterfaceConfigTab(QWidget):
    """接口配置标签页"""
    
    def __init__(self):
        super().__init__()
        self.eth_trunks = []
        self.lldp_interfaces = []
        self.poe_interfaces = []
        self.rate_limits = []
        self.initUI()
    
    def initUI(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        container = QWidget()
        layout = QHBoxLayout(container)
        
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)
        
        trunk_group = QGroupBox("端口聚合 (Eth-Trunk)")
        trunk_layout = QVBoxLayout()
        trunk_layout.setSpacing(10)
        
        trunk_form = QFormLayout()
        trunk_form.setSpacing(8)
        
        self.trunk_id = QSpinBox()
        self.trunk_id.setRange(1, 64)
        trunk_form.addRow("Trunk ID:", self.trunk_id)
        
        self.trunk_mode = QComboBox()
        self.trunk_mode.addItems(["lacp-static", "lacp-dynamic", "manual"])
        trunk_form.addRow("聚合模式:", self.trunk_mode)
        
        self.trunk_desc = QLineEdit()
        self.trunk_desc.setPlaceholderText("描述信息(可选)")
        trunk_form.addRow("描述:", self.trunk_desc)
        
        self.trunk_members = QLineEdit()
        self.trunk_members.setPlaceholderText("成员端口，逗号分隔 例: GE0/0/1,GE0/0/2")
        trunk_form.addRow("成员端口:", self.trunk_members)
        
        self.trunk_link_type = QComboBox()
        self.trunk_link_type.addItems(["trunk", "access"])
        self.trunk_link_type.currentTextChanged.connect(self.on_trunk_type_changed)
        trunk_form.addRow("链路类型:", self.trunk_link_type)
        
        self.trunk_vlans = QLineEdit()
        self.trunk_vlans.setPlaceholderText("允许VLAN，空格分隔")
        trunk_form.addRow("Trunk VLANs:", self.trunk_vlans)
        
        self.trunk_native_vlan = QSpinBox()
        self.trunk_native_vlan.setRange(1, 4094)
        trunk_form.addRow("Native VLAN:", self.trunk_native_vlan)
        
        trunk_layout.addLayout(trunk_form)
        
        add_trunk_btn = QPushButton("添加聚合")
        add_trunk_btn.setObjectName("primaryButton")
        add_trunk_btn.clicked.connect(self.add_eth_trunk)
        trunk_layout.addWidget(add_trunk_btn)
        
        self.trunk_list = QListWidget()
        self.trunk_list.setMaximumHeight(120)
        trunk_layout.addWidget(self.trunk_list)
        
        del_trunk_btn = QPushButton("删除选中")
        del_trunk_btn.setObjectName("dangerButton")
        del_trunk_btn.clicked.connect(self.del_eth_trunk)
        trunk_layout.addWidget(del_trunk_btn)
        
        trunk_group.setLayout(trunk_layout)
        left_panel.addWidget(trunk_group)
        
        lldp_group = QGroupBox("LLDP链路发现")
        lldp_layout = QFormLayout()
        lldp_layout.setSpacing(8)
        
        self.lldp_enable = QCheckBox("全局启用LLDP")
        self.lldp_enable.setChecked(True)
        lldp_layout.addRow("", self.lldp_enable)
        
        self.lldp_mode = QComboBox()
        self.lldp_mode.addItems(["both", "tx", "rx"])
        lldp_layout.addRow("工作模式:", self.lldp_mode)
        
        self.lldp_interval = QSpinBox()
        self.lldp_interval.setRange(5, 300)
        self.lldp_interval.setValue(30)
        self.lldp_interval.setSuffix(" 秒")
        lldp_layout.addRow("发送间隔:", self.lldp_interval)
        
        self.lldp_holdtime = QSpinBox()
        self.lldp_holdtime.setRange(60, 1200)
        self.lldp_holdtime.setValue(120)
        self.lldp_holdtime.setSuffix(" 秒")
        lldp_layout.addRow("存活时间:", self.lldp_holdtime)
        
        lldp_group.setLayout(lldp_layout)
        left_panel.addWidget(lldp_group)
        
        loop_group = QGroupBox("环路检测")
        loop_layout = QFormLayout()
        loop_layout.setSpacing(8)
        
        self.loop_detect_enable = QCheckBox("启用环路检测")
        loop_layout.addRow("", self.loop_detect_enable)
        
        self.loop_interval = QSpinBox()
        self.loop_interval.setRange(1, 300)
        self.loop_interval.setValue(5)
        self.loop_interval.setSuffix(" 秒")
        loop_layout.addRow("检测间隔:", self.loop_interval)
        
        self.loop_action = QComboBox()
        self.loop_action.addItems(["block", "shutdown", "trap"])
        loop_layout.addRow("检测动作:", self.loop_action)
        
        self.loop_vlans = QLineEdit()
        self.loop_vlans.setPlaceholderText("VLAN列表，空格分隔")
        loop_layout.addRow("检测VLAN:", self.loop_vlans)
        
        loop_group.setLayout(loop_layout)
        left_panel.addWidget(loop_group)
        
        left_panel.addStretch()
        layout.addLayout(left_panel, 1)
        
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)
        
        poe_group = QGroupBox("PoE供电配置")
        poe_layout = QVBoxLayout()
        poe_layout.setSpacing(10)
        
        poe_form = QFormLayout()
        poe_form.setSpacing(8)
        
        self.poe_global_enable = QCheckBox("全局启用PoE")
        self.poe_global_enable.setChecked(True)
        poe_form.addRow("", self.poe_global_enable)
        
        self.poe_global_power = QSpinBox()
        self.poe_global_power.setRange(1000, 100000)
        self.poe_global_power.setValue(74000)
        self.poe_global_power.setSuffix(" mW")
        poe_form.addRow("最大功率:", self.poe_global_power)
        
        poe_layout.addLayout(poe_form)
        
        poe_iface_form = QFormLayout()
        poe_iface_form.setSpacing(8)
        
        self.poe_interface = QLineEdit()
        self.poe_interface.setPlaceholderText("接口名，例: GE0/0/1")
        poe_iface_form.addRow("接口:", self.poe_interface)
        
        self.poe_mode = QComboBox()
        self.poe_mode.addItems(["auto", "force"])
        poe_iface_form.addRow("供电模式:", self.poe_mode)
        
        self.poe_priority = QComboBox()
        self.poe_priority.addItems(["critical", "high", "low"])
        poe_iface_form.addRow("优先级:", self.poe_priority)
        
        self.poe_iface_power = QSpinBox()
        self.poe_iface_power.setRange(1000, 30000)
        self.poe_iface_power.setValue(15400)
        self.poe_iface_power.setSuffix(" mW")
        poe_iface_form.addRow("端口功率:", self.poe_iface_power)
        
        poe_layout.addLayout(poe_iface_form)
        
        add_poe_btn = QPushButton("添加接口PoE配置")
        add_poe_btn.setObjectName("primaryButton")
        add_poe_btn.clicked.connect(self.add_poe_interface)
        poe_layout.addWidget(add_poe_btn)
        
        self.poe_list = QListWidget()
        self.poe_list.setMaximumHeight(100)
        poe_layout.addWidget(self.poe_list)
        
        del_poe_btn = QPushButton("删除选中")
        del_poe_btn.setObjectName("dangerButton")
        del_poe_btn.clicked.connect(self.del_poe_interface)
        poe_layout.addWidget(del_poe_btn)
        
        poe_group.setLayout(poe_layout)
        right_panel.addWidget(poe_group)
        
        rate_group = QGroupBox("接口限速")
        rate_layout = QVBoxLayout()
        rate_layout.setSpacing(10)
        
        rate_form = QFormLayout()
        rate_form.setSpacing(8)
        
        self.rate_interface = QLineEdit()
        self.rate_interface.setPlaceholderText("接口名，例: GE0/0/1")
        rate_form.addRow("接口:", self.rate_interface)
        
        self.rate_in = QSpinBox()
        self.rate_in.setRange(100, 10000000)
        self.rate_in.setValue(10000)
        self.rate_in.setSuffix(" kbps")
        rate_form.addRow("入方向限速:", self.rate_in)
        
        self.rate_out = QSpinBox()
        self.rate_out.setRange(100, 10000000)
        self.rate_out.setValue(10000)
        self.rate_out.setSuffix(" kbps")
        rate_form.addRow("出方向限速:", self.rate_out)
        
        rate_layout.addLayout(rate_form)
        
        add_rate_btn = QPushButton("添加限速配置")
        add_rate_btn.setObjectName("primaryButton")
        add_rate_btn.clicked.connect(self.add_rate_limit)
        rate_layout.addWidget(add_rate_btn)
        
        self.rate_list = QListWidget()
        self.rate_list.setMaximumHeight(100)
        rate_layout.addWidget(self.rate_list)
        
        del_rate_btn = QPushButton("删除选中")
        del_rate_btn.setObjectName("dangerButton")
        del_rate_btn.clicked.connect(self.del_rate_limit)
        rate_layout.addWidget(del_rate_btn)
        
        rate_group.setLayout(rate_layout)
        right_panel.addWidget(rate_group)
        
        right_panel.addStretch()
        layout.addLayout(right_panel, 1)
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def on_trunk_type_changed(self, trunk_type):
        self.trunk_vlans.setEnabled(trunk_type == "trunk")
        self.trunk_native_vlan.setEnabled(trunk_type == "access")
    
    def add_eth_trunk(self):
        trunk_id = self.trunk_id.value()
        members_str = self.trunk_members.text().strip()
        
        if not members_str:
            QMessageBox.warning(self, "警告", "请输入成员端口！")
            return
        
        for t in self.eth_trunks:
            if t["trunk_id"] == trunk_id:
                QMessageBox.warning(self, "警告", f"Eth-Trunk{trunk_id} 已存在！")
                return
        
        members = [m.strip() for m in members_str.split(",")]
        
        trunk_data = {
            "trunk_id": trunk_id,
            "mode": self.trunk_mode.currentText(),
            "description": self.trunk_desc.text().strip() or None,
            "member_ports": members,
            "port_link_type": self.trunk_link_type.currentText()
        }
        
        if trunk_data["port_link_type"] == "trunk":
            vlans_str = self.trunk_vlans.text().strip()
            if vlans_str:
                trunk_data["trunk_vlans"] = [int(v) for v in vlans_str.split()]
        else:
            trunk_data["native_vlan"] = self.trunk_native_vlan.value()
        
        self.eth_trunks.append(trunk_data)
        
        display = f"Eth-Trunk{trunk_id} ({trunk_data['mode']}) - {', '.join(members[:2])}"
        if len(members) > 2:
            display += f"... 共{len(members)}个端口"
        self.trunk_list.addItem(display)
        
        self.trunk_id.setValue(self.trunk_id.value() + 1)
        self.trunk_members.clear()
        self.trunk_desc.clear()
    
    def del_eth_trunk(self):
        row = self.trunk_list.currentRow()
        if row >= 0:
            self.trunk_list.takeItem(row)
            del self.eth_trunks[row]
    
    def add_poe_interface(self):
        interface = self.poe_interface.text().strip()
        if not interface:
            QMessageBox.warning(self, "警告", "请输入接口名称！")
            return
        
        poe_data = {
            "interface": interface,
            "enable": True,
            "mode": self.poe_mode.currentText(),
            "priority": self.poe_priority.currentText(),
            "max_power": self.poe_iface_power.value()
        }
        
        self.poe_interfaces.append(poe_data)
        self.poe_list.addItem(f"{interface} - {poe_data['mode']} - {poe_data['priority']}")
        self.poe_interface.clear()
    
    def del_poe_interface(self):
        row = self.poe_list.currentRow()
        if row >= 0:
            self.poe_list.takeItem(row)
            del self.poe_interfaces[row]
    
    def add_rate_limit(self):
        interface = self.rate_interface.text().strip()
        if not interface:
            QMessageBox.warning(self, "警告", "请输入接口名称！")
            return
        
        rate_data = {
            "interface": interface,
            "cir_in": self.rate_in.value() if self.rate_in.value() > 0 else None,
            "cir_out": self.rate_out.value() if self.rate_out.value() > 0 else None
        }
        
        self.rate_limits.append(rate_data)
        self.rate_list.addItem(f"{interface} - 入:{rate_data['cir_in']}kbps 出:{rate_data['cir_out']}kbps")
        self.rate_interface.clear()
    
    def del_rate_limit(self):
        row = self.rate_list.currentRow()
        if row >= 0:
            self.rate_list.takeItem(row)
            del self.rate_limits[row]
    
    def get_config(self):
        config = {}
        
        if self.eth_trunks:
            config["eth_trunks"] = self.eth_trunks
        
        if self.lldp_enable.isChecked():
            config["lldp"] = {
                "enable": True,
                "mode": self.lldp_mode.currentText(),
                "interval": self.lldp_interval.value(),
                "holdtime": self.lldp_holdtime.value()
            }
        
        if self.loop_detect_enable.isChecked():
            vlans_str = self.loop_vlans.text().strip()
            config["loopback_detection"] = {
                "enable": True,
                "interval": self.loop_interval.value(),
                "action": self.loop_action.currentText(),
                "vlan_ids": [int(v) for v in vlans_str.split()] if vlans_str else None
            }
        
        if self.poe_global_enable.isChecked() or self.poe_interfaces:
            config["poe"] = {
                "enable": self.poe_global_enable.isChecked(),
                "max_power": self.poe_global_power.value(),
                "interfaces": self.poe_interfaces
            }
        
        if self.rate_limits:
            config["rate_limits"] = self.rate_limits
        
        if config:
            return InterfaceConfigGenerator.generate_interface_all(config)
        return ""
    
    def clear_config(self):
        self.eth_trunks.clear()
        self.poe_interfaces.clear()
        self.rate_limits.clear()
        
        self.trunk_list.clear()
        self.poe_list.clear()
        self.rate_list.clear()
        
        self.trunk_id.setValue(1)
        self.trunk_mode.setCurrentIndex(0)
        self.trunk_desc.clear()
        self.trunk_members.clear()
        self.trunk_link_type.setCurrentIndex(0)
        self.trunk_vlans.clear()
        self.trunk_native_vlan.setValue(1)
        
        self.lldp_enable.setChecked(True)
        self.lldp_mode.setCurrentIndex(0)
        self.lldp_interval.setValue(30)
        self.lldp_holdtime.setValue(120)
        
        self.loop_detect_enable.setChecked(False)
        self.loop_interval.setValue(5)
        self.loop_action.setCurrentIndex(0)
        self.loop_vlans.clear()
        
        self.poe_global_enable.setChecked(True)
        self.poe_global_power.setValue(74000)
        self.poe_interface.clear()
        self.poe_mode.setCurrentIndex(0)
        self.poe_priority.setCurrentIndex(2)
        self.poe_iface_power.setValue(15400)
        
        self.rate_interface.clear()
        self.rate_in.setValue(10000)
        self.rate_out.setValue(10000)
    
    def get_config_data(self):
        """获取配置数据字典"""
        return {
            "eth_trunks": self.eth_trunks.copy(),
            "poe_interfaces": self.poe_interfaces.copy(),
            "rate_limits": self.rate_limits.copy(),
            "lldp": {
                "enable": self.lldp_enable.isChecked(),
                "mode": self.lldp_mode.currentText(),
                "interval": self.lldp_interval.value()
            },
            "loop_detect": {
                "enable": self.loop_detect_enable.isChecked(),
                "interval": self.loop_interval.value()
            }
        }
    
    def load_config(self, config):
        """从配置字典加载配置"""
        if not config:
            return
        
        if "eth_trunks" in config:
            self.eth_trunks = config["eth_trunks"].copy()
            for trunk in self.eth_trunks:
                self.trunk_list.addItem(f"Eth-Trunk{trunk['id']}: {trunk.get('mode', '')}")
        
        if "poe_interfaces" in config:
            self.poe_interfaces = config["poe_interfaces"].copy()
        
        if "rate_limits" in config:
            self.rate_limits = config["rate_limits"].copy()
        
        if "lldp" in config:
            lldp = config["lldp"]
            self.lldp_enable.setChecked(lldp.get("enable", True))
            if "mode" in lldp:
                self.lldp_mode.setCurrentText(lldp["mode"])
        
        if "loop_detect" in config:
            loop = config["loop_detect"]
            self.loop_detect_enable.setChecked(loop.get("enable", False))
