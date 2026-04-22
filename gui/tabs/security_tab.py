#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NetOps Toolkit - 安全配置标签页
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QSpinBox, QCheckBox, QGroupBox,
                             QComboBox, QPushButton, QListWidget, QTextEdit,
                             QMessageBox, QRadioButton, QButtonGroup, QLabel)
from PyQt5.QtCore import Qt
from modules.security_config import SecurityConfigGenerator


class SecurityConfigTab(QWidget):
    """安全配置标签页"""
    
    def __init__(self):
        super().__init__()
        self.acls = []
        self.port_security_list = []
        self.anti_attack_types = []
        self.initUI()
    
    def initUI(self):
        layout = QHBoxLayout(self)
        
        left_panel = QVBoxLayout()
        
        acl_group = QGroupBox("ACL配置")
        acl_layout = QVBoxLayout()
        
        acl_form = QFormLayout()
        
        self.acl_number = QSpinBox()
        self.acl_number.setRange(2000, 39999)
        self.acl_number.setValue(3000)
        acl_form.addRow("ACL编号:", self.acl_number)
        
        self.acl_type_group = QButtonGroup()
        self.acl_std_radio = QRadioButton("标准ACL (2000-2999)")
        self.acl_ext_radio = QRadioButton("扩展ACL (3000-3999)")
        self.acl_ext_radio.setChecked(True)
        self.acl_type_group.addButton(self.acl_std_radio)
        self.acl_type_group.addButton(self.acl_ext_radio)
        
        acl_type_layout = QHBoxLayout()
        acl_type_layout.addWidget(self.acl_std_radio)
        acl_type_layout.addWidget(self.acl_ext_radio)
        acl_form.addRow("类型:", acl_type_layout)
        
        self.acl_desc = QLineEdit()
        self.acl_desc.setPlaceholderText("ACL描述(可选)")
        acl_form.addRow("描述:", self.acl_desc)
        
        rule_form = QFormLayout()
        
        self.rule_id = QSpinBox()
        self.rule_id.setRange(1, 65535)
        self.rule_id.setValue(5)
        acl_form.addRow("规则ID:", self.rule_id)
        
        self.rule_action_combo = QComboBox()
        self.rule_action_combo.addItems(["permit", "deny"])
        acl_form.addRow("动作:", self.rule_action_combo)
        
        self.rule_protocol = QComboBox()
        self.rule_protocol.addItems(["ip", "tcp", "udp", "icmp"])
        acl_form.addRow("协议:", self.rule_protocol)
        
        self.rule_source = QLineEdit()
        self.rule_source.setPlaceholderText("例如: 192.168.1.0")
        acl_form.addRow("源地址:", self.rule_source)
        
        self.rule_src_wildcard = QLineEdit()
        self.rule_src_wildcard.setPlaceholderText("反掩码 例如: 0.0.0.255")
        acl_form.addRow("源反掩码:", self.rule_src_wildcard)
        
        self.rule_dest = QLineEdit()
        self.rule_dest.setPlaceholderText("目标地址")
        acl_form.addRow("目标地址:", self.rule_dest)
        
        self.rule_dst_wildcard = QLineEdit()
        self.rule_dst_wildcard.setPlaceholderText("反掩码")
        acl_form.addRow("目标反掩码:", self.rule_dst_wildcard)
        
        self.rule_port = QLineEdit()
        self.rule_port.setPlaceholderText("端口号(仅TCP/UDP)")
        acl_form.addRow("端口:", self.rule_port)
        
        acl_layout.addLayout(acl_form)
        
        add_acl_btn = QPushButton("添加ACL规则")
        add_acl_btn.clicked.connect(self.add_acl_rule)
        acl_layout.addWidget(add_acl_btn)
        
        self.acl_list = QListWidget()
        self.acl_list.setMaximumHeight(150)
        acl_layout.addWidget(self.acl_list)
        
        del_acl_btn = QPushButton("删除选中")
        del_acl_btn.clicked.connect(self.del_acl_rule)
        acl_layout.addWidget(del_acl_btn)
        
        acl_group.setLayout(acl_layout)
        left_panel.addWidget(acl_group)
        
        port_sec_group = QGroupBox("端口安全配置")
        port_sec_layout = QFormLayout()
        
        self.port_sec_interface = QLineEdit()
        self.port_sec_interface.setPlaceholderText("例如: GigabitEthernet0/0/1")
        port_sec_layout.addRow("接口:", self.port_sec_interface)
        
        self.port_sec_enable = QCheckBox("启用端口安全")
        self.port_sec_enable.setChecked(True)
        port_sec_layout.addRow("", self.port_sec_enable)
        
        self.port_sec_max_mac = QSpinBox()
        self.port_sec_max_mac.setRange(1, 1024)
        self.port_sec_max_mac.setValue(1)
        port_sec_layout.addRow("最大MAC数:", self.port_sec_max_mac)
        
        self.port_sec_action = QComboBox()
        self.port_sec_action.addItems(["protect", "restrict", "shutdown"])
        port_sec_layout.addRow("违规动作:", self.port_sec_action)
        
        self.port_sec_sticky = QCheckBox("启用MAC粘连")
        port_sec_layout.addRow("", self.port_sec_sticky)
        
        self.traffic_filter_interface = QLineEdit()
        self.traffic_filter_interface.setPlaceholderText("应用ACL的接口")
        port_sec_layout.addRow("应用接口:", self.traffic_filter_interface)
        
        self.traffic_filter_acl = QSpinBox()
        self.traffic_filter_acl.setRange(2000, 39999)
        self.traffic_filter_acl.setValue(3000)
        port_sec_layout.addRow("ACL编号:", self.traffic_filter_acl)
        
        self.traffic_filter_direction = QComboBox()
        self.traffic_filter_direction.addItems(["inbound", "outbound"])
        port_sec_layout.addRow("方向:", self.traffic_filter_direction)
        
        apply_filter_btn = QPushButton("应用ACL到接口")
        apply_filter_btn.clicked.connect(self.apply_traffic_filter)
        port_sec_layout.addRow("", apply_filter_btn)
        
        port_sec_group.setLayout(port_sec_layout)
        left_panel.addWidget(port_sec_group)
        
        left_panel.addStretch()
        layout.addLayout(left_panel, 1)
        
        right_panel = QVBoxLayout()
        
        dhcp_snoop_group = QGroupBox("DHCP Snooping")
        dhcp_layout = QFormLayout()
        
        self.dhcp_snoop_enable = QCheckBox("启用DHCP Snooping")
        dhcp_layout.addRow("", self.dhcp_snoop_enable)
        
        self.dhcp_vlan = QSpinBox()
        self.dhcp_vlan.setRange(1, 4094)
        dhcp_layout.addRow("VLAN:", self.dhcp_vlan)
        
        self.dhcp_trusted = QLineEdit()
        self.dhcp_trusted.setPlaceholderText("信任端口(逗号分隔)")
        dhcp_layout.addRow("信任端口:", self.dhcp_trusted)
        
        dhcp_snoop_group.setLayout(dhcp_layout)
        right_panel.addWidget(dhcp_snoop_group)
        
        arp_group = QGroupBox("ARP防护")
        arp_layout = QFormLayout()
        
        self.arp_inspect_vlans = QLineEdit()
        self.arp_inspect_vlans.setPlaceholderText("VLAN列表(逗号分隔)")
        arp_layout.addRow("监控VLAN:", self.arp_inspect_vlans)
        
        self.arp_trusted = QLineEdit()
        self.arp_trusted.setPlaceholderText("信任端口(逗号分隔)")
        arp_layout.addRow("信任端口:", self.arp_trusted)
        
        arp_group.setLayout(arp_layout)
        right_panel.addWidget(arp_group)
        
        storm_group = QGroupBox("风暴抑制")
        storm_layout = QFormLayout()
        
        self.storm_interface = QLineEdit()
        self.storm_interface.setPlaceholderText("接口名称")
        storm_layout.addRow("接口:", self.storm_interface)
        
        self.broadcast_rate = QSpinBox()
        self.broadcast_rate.setRange(0, 1488100)
        self.broadcast_rate.setValue(1000)
        storm_layout.addRow("广播(pps):", self.broadcast_rate)
        
        self.multicast_rate = QSpinBox()
        self.multicast_rate.setRange(0, 1488100)
        self.multicast_rate.setValue(1000)
        storm_layout.addRow("组播(pps):", self.multicast_rate)
        
        self.storm_action = QComboBox()
        self.storm_action.addItems(["block", "shutdown"])
        storm_layout.addRow("动作:", self.storm_action)
        
        storm_group.setLayout(storm_layout)
        right_panel.addWidget(storm_group)
        
        anti_group = QGroupBox("防攻击配置")
        anti_layout = QVBoxLayout()
        
        self.anti_all = QCheckBox("防所有攻击")
        self.anti_ip = QCheckBox("防IP攻击")
        self.anti_arp = QCheckBox("防ARP攻击")
        self.anti_dhcp = QCheckBox("防DHCP攻击")
        
        anti_layout.addWidget(self.anti_all)
        anti_layout.addWidget(self.anti_ip)
        anti_layout.addWidget(self.anti_arp)
        anti_layout.addWidget(self.anti_dhcp)
        
        anti_group.setLayout(anti_layout)
        right_panel.addWidget(anti_group)
        
        right_panel.addStretch()
        layout.addLayout(right_panel, 1)
    
    def add_acl_rule(self):
        acl_num = self.acl_number.value()
        
        is_extended = self.acl_ext_radio.isChecked()
        
        for acl in self.acls:
            if acl["number"] == acl_num:
                rule = {
                    "id": self.rule_id.value(),
                    "action": self.rule_action_combo.currentText(),
                    "protocol": self.rule_protocol.currentText() if is_extended else None,
                    "source": self.rule_source.text().strip() or None,
                    "source_wildcard": self.rule_src_wildcard.text().strip() or None,
                    "destination": self.rule_dest.text().strip() if is_extended else None,
                    "destination_wildcard": self.rule_dst_wildcard.text().strip() if is_extended else None,
                    "dest_port": self.rule_port.text().strip() if is_extended else None
                }
                acl["rules"].append(rule)
                
                display_text = f"ACL {acl_num} - 规则{rule['id']}: {rule['action']} {rule['protocol'] or ''} {rule['source'] or 'any'}"
                self.acl_list.addItem(display_text)
                
                self.rule_id.setValue(self.rule_id.value() + 5)
                return
        
        acl_data = {
            "number": acl_num,
            "type": "extended" if is_extended else "standard",
            "description": self.acl_desc.text().strip() or None,
            "rules": [{
                "id": self.rule_id.value(),
                "action": self.rule_action_combo.currentText(),
                "protocol": self.rule_protocol.currentText() if is_extended else None,
                "source": self.rule_source.text().strip() or None,
                "source_wildcard": self.rule_src_wildcard.text().strip() or None,
                "destination": self.rule_dest.text().strip() if is_extended else None,
                "destination_wildcard": self.rule_dst_wildcard.text().strip() if is_extended else None,
                "dest_port": self.rule_port.text().strip() if is_extended else None
            }]
        }
        
        self.acls.append(acl_data)
        
        display_text = f"ACL {acl_num} - 规则{self.rule_id.value()}: {self.rule_action_combo.currentText()}"
        self.acl_list.addItem(display_text)
        
        self.rule_id.setValue(self.rule_id.value() + 5)
    
    def del_acl_rule(self):
        row = self.acl_list.currentRow()
        if row >= 0:
            self.acl_list.takeItem(row)
            
            acl_idx = 0
            rule_count = 0
            for i, acl in enumerate(self.acls):
                if row < rule_count + len(acl["rules"]):
                    acl_idx = i
                    del acl["rules"][row - rule_count]
                    if not acl["rules"]:
                        del self.acls[i]
                    break
                rule_count += len(acl["rules"])
    
    def apply_traffic_filter(self):
        interface = self.traffic_filter_interface.text().strip()
        if not interface:
            QMessageBox.warning(self, "警告", "请输入接口名称！")
            return
        
        self.port_security_list.append({
            "interface": interface,
            "enable": False
        })
        
        QMessageBox.information(self, "成功", f"ACL {self.traffic_filter_acl.value()} 已应用到接口 {interface}")
    
    def get_config(self):
        config = {}
        
        if self.acls:
            config["acls"] = self.acls
        
        port_sec_interfaces = []
        if self.port_sec_enable.isChecked():
            interface = self.port_sec_interface.text().strip()
            if interface:
                port_sec_interfaces.append({
                    "interface": interface,
                    "enable": True,
                    "max_mac": self.port_sec_max_mac.value(),
                    "action": self.port_sec_action.currentText(),
                    "sticky": self.port_sec_sticky.isChecked()
                })
        
        if port_sec_interfaces:
            config["port_security"] = port_sec_interfaces
        
        traffic_filters = []
        interface = self.traffic_filter_interface.text().strip()
        if interface:
            traffic_filters.append({
                "interface": interface,
                "acl_number": self.traffic_filter_acl.value(),
                "direction": self.traffic_filter_direction.currentText()
            })
        
        if traffic_filters:
            config["traffic_filters"] = traffic_filters
        
        if self.dhcp_snoop_enable.isChecked():
            trusted = self.dhcp_trusted.text().strip()
            config["dhcp_snooping"] = {
                "enable": True,
                "vlan": self.dhcp_vlan.value() if self.dhcp_vlan.value() else None,
                "trusted_ports": trusted.split(",") if trusted else None
            }
        
        arp_vlans = self.arp_inspect_vlans.text().strip()
        arp_trusted = self.arp_trusted.text().strip()
        if arp_vlans or arp_trusted:
            config["arp_inspection"] = {
                "vlans": [int(v.strip()) for v in arp_vlans.split(",")] if arp_vlans else None,
                "trusted_ports": [p.strip() for p in arp_trusted.split(",")] if arp_trusted else None
            }
        
        storm_interface = self.storm_interface.text().strip()
        if storm_interface:
            config["storm_controls"] = [{
                "interface": storm_interface,
                "broadcast": self.broadcast_rate.value(),
                "multicast": self.multicast_rate.value(),
                "action": self.storm_action.currentText()
            }]
        
        anti_types = []
        if self.anti_all.isChecked():
            anti_types.append("all")
        if self.anti_ip.isChecked():
            anti_types.append("ip")
        if self.anti_arp.isChecked():
            anti_types.append("arp")
        if self.anti_dhcp.isChecked():
            anti_types.append("dhcp")
        
        if anti_types:
            config["anti_attack"] = {
                "enable": True,
                "type": anti_types[0] if len(anti_types) == 1 else ",".join(anti_types)
            }
        
        if config:
            return SecurityConfigGenerator.generate_security_all(config)
        return ""
    
    def clear_config(self):
        self.acls.clear()
        self.port_security_list.clear()
        self.anti_attack_types.clear()
        
        self.acl_list.clear()
        
        self.acl_number.setValue(3000)
        self.acl_ext_radio.setChecked(True)
        self.acl_desc.clear()
        self.rule_id.setValue(5)
        self.rule_action_combo.setCurrentIndex(0)
        self.rule_protocol.setCurrentIndex(0)
        self.rule_source.clear()
        self.rule_src_wildcard.clear()
        self.rule_dest.clear()
        self.rule_dst_wildcard.clear()
        self.rule_port.clear()
        
        self.port_sec_interface.clear()
        self.port_sec_enable.setChecked(True)
        self.port_sec_max_mac.setValue(1)
        self.port_sec_action.setCurrentIndex(0)
        self.port_sec_sticky.setChecked(False)
        
        self.traffic_filter_interface.clear()
        self.traffic_filter_acl.setValue(3000)
        self.traffic_filter_direction.setCurrentIndex(0)
    
    def get_config_data(self):
        """获取配置数据字典"""
        return {
            "acls": self.acls.copy(),
            "port_security": self.port_security_list.copy(),
            "anti_attack": self.anti_attack_types.copy()
        }
    
    def load_config(self, config):
        """从配置字典加载配置"""
        if not config:
            return
        
        if "acls" in config:
            self.acls = config["acls"].copy()
            for acl in self.acls:
                self.acl_list.addItem(f"ACL {acl['number']}: {acl.get('description', '')}")
        
        if "port_security" in config:
            self.port_security_list = config["port_security"].copy()
        
        if "anti_attack" in config:
            self.anti_attack_types = config["anti_attack"].copy()
        
        self.dhcp_snoop_enable.setChecked(False)
        self.dhcp_vlan.setValue(1)
        self.dhcp_trusted.clear()
        
        self.arp_inspect_vlans.clear()
        self.arp_trusted.clear()
        
        self.storm_interface.clear()
        self.broadcast_rate.setValue(1000)
        self.multicast_rate.setValue(1000)
        self.storm_action.setCurrentIndex(0)
        
        self.anti_all.setChecked(False)
        self.anti_ip.setChecked(False)
        self.anti_arp.setChecked(False)
        self.anti_dhcp.setChecked(False)
