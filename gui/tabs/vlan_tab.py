#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NetOps Toolkit - VLAN配置标签页
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QSpinBox, QCheckBox, QGroupBox,
                             QComboBox, QPushButton, QListWidget, QListWidgetItem,
                             QTextEdit, QMessageBox, QLabel)
from PyQt5.QtCore import Qt
from modules.vlan_config import VLANConfigGenerator


class VLANConfigTab(QWidget):
    """VLAN配置标签页"""
    
    def __init__(self):
        super().__init__()
        self.vlans = []
        self.interfaces = []
        self.vlanifs = []
        self.initUI()
    
    def initUI(self):
        layout = QHBoxLayout(self)
        
        left_panel = QVBoxLayout()
        
        vlan_group = QGroupBox("VLAN列表")
        vlan_layout = QVBoxLayout()
        
        vlan_input_layout = QHBoxLayout()
        vlan_input_layout.addWidget(QLabel("VLAN ID:"))
        self.vlan_id_input = QSpinBox()
        self.vlan_id_input.setRange(1, 4094)
        vlan_input_layout.addWidget(self.vlan_id_input)
        
        self.vlan_name_input = QLineEdit()
        self.vlan_name_input.setPlaceholderText("VLAN名称(可选)")
        vlan_input_layout.addWidget(self.vlan_name_input)
        
        add_vlan_btn = QPushButton("添加")
        add_vlan_btn.clicked.connect(self.add_vlan)
        vlan_input_layout.addWidget(add_vlan_btn)
        
        vlan_layout.addLayout(vlan_input_layout)
        
        self.vlan_list = QListWidget()
        self.vlan_list.setMaximumHeight(150)
        vlan_layout.addWidget(self.vlan_list)
        
        del_vlan_btn = QPushButton("删除选中")
        del_vlan_btn.clicked.connect(self.del_vlan)
        vlan_layout.addWidget(del_vlan_btn)
        
        vlan_group.setLayout(vlan_layout)
        left_panel.addWidget(vlan_group)
        
        interface_group = QGroupBox("接口VLAN配置")
        iface_layout = QVBoxLayout()
        
        iface_form = QFormLayout()
        
        self.interface_input = QLineEdit()
        self.interface_input.setPlaceholderText("例如: GigabitEthernet0/0/1")
        iface_form.addRow("接口:", self.interface_input)
        
        self.vlan_type_combo = QComboBox()
        self.vlan_type_combo.addItems(["access", "trunk", "hybrid"])
        self.vlan_type_combo.currentTextChanged.connect(self.on_vlan_type_changed)
        iface_form.addRow("类型:", self.vlan_type_combo)
        
        self.port_vlan_id = QSpinBox()
        self.port_vlan_id.setRange(1, 4094)
        iface_form.addRow("VLAN ID:", self.port_vlan_id)
        
        self.trunk_vlans_input = QLineEdit()
        self.trunk_vlans_input.setPlaceholderText("例如: 10 20 30")
        self.trunk_vlans_input.setEnabled(False)
        iface_form.addRow("Trunk VLANs:", self.trunk_vlans_input)
        
        self.pvid_input = QSpinBox()
        self.pvid_input.setRange(1, 4094)
        self.pvid_input.setEnabled(False)
        iface_form.addRow("PVID:", self.pvid_input)
        
        iface_layout.addLayout(iface_form)
        
        add_iface_btn = QPushButton("添加接口")
        add_iface_btn.clicked.connect(self.add_interface)
        iface_layout.addWidget(add_iface_btn)
        
        self.interface_list = QListWidget()
        self.interface_list.setMaximumHeight(150)
        iface_layout.addWidget(self.interface_list)
        
        del_iface_btn = QPushButton("删除选中")
        del_iface_btn.clicked.connect(self.del_interface)
        iface_layout.addWidget(del_iface_btn)
        
        interface_group.setLayout(iface_layout)
        left_panel.addWidget(interface_group)
        
        left_panel.addStretch()
        layout.addLayout(left_panel, 1)
        
        right_panel = QVBoxLayout()
        
        vlanif_group = QGroupBox("VLANIF配置")
        vlanif_layout = QVBoxLayout()
        
        vlanif_form = QFormLayout()
        
        self.vlanif_vlan_id = QSpinBox()
        self.vlanif_vlan_id.setRange(1, 4094)
        vlanif_form.addRow("VLAN ID:", self.vlanif_vlan_id)
        
        self.vlanif_ip = QLineEdit()
        self.vlanif_ip.setPlaceholderText("例如: 192.168.1.1")
        vlanif_form.addRow("IP地址:", self.vlanif_ip)
        
        self.vlanif_mask = QLineEdit()
        self.vlanif_mask.setText("255.255.255.0")
        vlanif_form.addRow("子网掩码:", self.vlanif_mask)
        
        self.vlanif_desc = QLineEdit()
        self.vlanif_desc.setPlaceholderText("描述(可选)")
        vlanif_form.addRow("描述:", self.vlanif_desc)
        
        vlanif_layout.addLayout(vlanif_form)
        
        add_vlanif_btn = QPushButton("添加VLANIF")
        add_vlanif_btn.clicked.connect(self.add_vlanif)
        vlanif_layout.addWidget(add_vlanif_btn)
        
        self.vlanif_list = QListWidget()
        self.vlanif_list.setMaximumHeight(150)
        vlanif_layout.addWidget(self.vlanif_list)
        
        del_vlanif_btn = QPushButton("删除选中")
        del_vlanif_btn.clicked.connect(self.del_vlanif)
        vlanif_layout.addWidget(del_vlanif_btn)
        
        vlanif_group.setLayout(vlanif_layout)
        right_panel.addWidget(vlanif_group)
        
        stp_group = QGroupBox("STP配置")
        stp_layout = QFormLayout()
        
        self.stp_mode_combo = QComboBox()
        self.stp_mode_combo.addItems(["stp", "rstp", "mstp"])
        stp_layout.addRow("STP模式:", self.stp_mode_combo)
        
        self.stp_priority = QSpinBox()
        self.stp_priority.setRange(0, 61440)
        self.stp_priority.setSingleStep(4096)
        self.stp_priority.setValue(32768)
        stp_layout.addRow("优先级:", self.stp_priority)
        
        self.stp_enable = QCheckBox("启用STP")
        self.stp_enable.setChecked(True)
        stp_layout.addRow("", self.stp_enable)
        
        stp_group.setLayout(stp_layout)
        right_panel.addWidget(stp_group)
        
        right_panel.addStretch()
        layout.addLayout(right_panel, 1)
    
    def add_vlan(self):
        vlan_id = self.vlan_id_input.value()
        vlan_name = self.vlan_name_input.text().strip()
        
        for v in self.vlans:
            if v["id"] == vlan_id:
                QMessageBox.warning(self, "警告", f"VLAN {vlan_id} 已存在！")
                return
        
        vlan_data = {"id": vlan_id}
        if vlan_name:
            vlan_data["name"] = vlan_name
        
        self.vlans.append(vlan_data)
        
        display_text = f"VLAN {vlan_id}" + (f" ({vlan_name})" if vlan_name else "")
        self.vlan_list.addItem(display_text)
        
        self.vlan_id_input.setValue(self.vlan_id_input.value() + 1)
        self.vlan_name_input.clear()
    
    def del_vlan(self):
        row = self.vlan_list.currentRow()
        if row >= 0:
            self.vlan_list.takeItem(row)
            del self.vlans[row]
    
    def add_interface(self):
        interface = self.interface_input.text().strip()
        if not interface:
            QMessageBox.warning(self, "警告", "请输入接口名称！")
            return
        
        vlan_type = self.vlan_type_combo.currentText()
        iface_data = {
            "interface": interface,
            "type": vlan_type
        }
        
        if vlan_type == "access":
            iface_data["vlan_id"] = self.port_vlan_id.value()
        elif vlan_type == "trunk":
            trunk_vlans = self.trunk_vlans_input.text().strip()
            if trunk_vlans:
                iface_data["trunk_vlans"] = [int(v) for v in trunk_vlans.split()]
            if self.pvid_input.value():
                iface_data["pvid"] = self.pvid_input.value()
        
        self.interfaces.append(iface_data)
        
        display_text = f"{interface} - {vlan_type}"
        self.interface_list.addItem(display_text)
        self.interface_input.clear()
    
    def del_interface(self):
        row = self.interface_list.currentRow()
        if row >= 0:
            self.interface_list.takeItem(row)
            del self.interfaces[row]
    
    def add_vlanif(self):
        vlan_id = self.vlanif_vlan_id.value()
        ip_address = self.vlanif_ip.text().strip()
        
        if not ip_address:
            QMessageBox.warning(self, "警告", "请输入IP地址！")
            return
        
        vlanif_data = {
            "vlan_id": vlan_id,
            "ip_address": ip_address,
            "mask": self.vlanif_mask.text().strip() or "255.255.255.0"
        }
        
        desc = self.vlanif_desc.text().strip()
        if desc:
            vlanif_data["description"] = desc
        
        self.vlanifs.append(vlanif_data)
        
        display_text = f"Vlanif{vlan_id} - {ip_address}"
        self.vlanif_list.addItem(display_text)
        
        self.vlanif_vlan_id.setValue(self.vlanif_vlan_id.value() + 1)
        self.vlanif_ip.clear()
        self.vlanif_desc.clear()
    
    def del_vlanif(self):
        row = self.vlanif_list.currentRow()
        if row >= 0:
            self.vlanif_list.takeItem(row)
            del self.vlanifs[row]
    
    def on_vlan_type_changed(self, vlan_type):
        is_trunk = vlan_type == "trunk"
        self.trunk_vlans_input.setEnabled(is_trunk)
        self.pvid_input.setEnabled(is_trunk)
        self.port_vlan_id.setEnabled(not is_trunk)
    
    def get_config(self):
        config = {}
        
        if self.vlans:
            config["vlans"] = self.vlans
        
        if self.interfaces:
            config["interfaces"] = self.interfaces
        
        if self.vlanifs:
            config["vlanifs"] = self.vlanifs
        
        stp_mode = self.stp_mode_combo.currentText()
        stp_priority = self.stp_priority.value()
        stp_enabled = self.stp_enable.isChecked()
        
        if stp_priority != 32768 or not stp_enabled:
            config["stp"] = {
                "mode": stp_mode,
                "priority": stp_priority,
                "enable": stp_enabled
            }
        
        if config:
            return VLANConfigGenerator.generate_vlan_all(config)
        return ""
    
    def clear_config(self):
        self.vlans.clear()
        self.interfaces.clear()
        self.vlanifs.clear()
        
        self.vlan_list.clear()
        self.interface_list.clear()
        self.vlanif_list.clear()
        
        self.vlan_id_input.setValue(1)
        self.vlan_name_input.clear()
        self.interface_input.clear()
        self.vlan_type_combo.setCurrentIndex(0)
        self.port_vlan_id.setValue(1)
        self.trunk_vlans_input.clear()
        self.pvid_input.setValue(1)
        
        self.vlanif_vlan_id.setValue(1)
        self.vlanif_ip.clear()
        self.vlanif_mask.setText("255.255.255.0")
        self.vlanif_desc.clear()
        
        self.stp_mode_combo.setCurrentIndex(0)
        self.stp_priority.setValue(32768)
        self.stp_enable.setChecked(True)
    
    def get_config_data(self):
        """获取配置数据字典"""
        data = {}
        
        if self.vlans:
            data["vlans"] = self.vlans.copy()
        if self.interfaces:
            data["interfaces"] = self.interfaces.copy()
        if self.vlanifs:
            data["vlanifs"] = self.vlanifs.copy()
        
        return data
    
    def load_config(self, config):
        """从配置字典加载配置"""
        if not config:
            return
        
        if "vlans" in config:
            self.vlans = config["vlans"].copy()
            for vlan in self.vlans:
                self.vlan_list.addItem(f"VLAN {vlan['id']}: {vlan.get('name', '')}")
        
        if "interfaces" in config:
            self.interfaces = config["interfaces"].copy()
            for iface in self.interfaces:
                self.interface_list.addItem(f"{iface['interface']} - {iface['type']}")
        
        if "vlanifs" in config:
            self.vlanifs = config["vlanifs"].copy()
            for vlanif in self.vlanifs:
                self.vlanif_list.addItem(f"Vlanif{vlanif['vlan_id']}: {vlanif.get('ip', '')}")
