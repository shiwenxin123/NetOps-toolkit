#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NetOps Toolkit - 路由配置标签页
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QSpinBox, QCheckBox, QGroupBox,
                             QComboBox, QPushButton, QListWidget, QMessageBox, QLabel)
from PyQt5.QtCore import Qt
from modules.routing_config import RoutingConfigGenerator


class RoutingConfigTab(QWidget):
    """路由配置标签页"""
    
    def __init__(self):
        super().__init__()
        self.static_routes = []
        self.ospf_networks = []
        self.bgp_peers = []
        self.initUI()
    
    def initUI(self):
        layout = QHBoxLayout(self)
        
        left_panel = QVBoxLayout()
        
        static_group = QGroupBox("静态路由/默认路由")
        static_layout = QVBoxLayout()
        
        static_form = QFormLayout()
        
        self.route_dest = QLineEdit()
        self.route_dest.setPlaceholderText("例如: 192.168.10.0")
        static_form.addRow("目标网络:", self.route_dest)
        
        self.route_mask = QLineEdit()
        self.route_mask.setPlaceholderText("例如: 255.255.255.0")
        static_form.addRow("子网掩码:", self.route_mask)
        
        self.route_nexthop = QLineEdit()
        self.route_nexthop.setPlaceholderText("下一跳IP或接口名")
        static_form.addRow("下一跳:", self.route_nexthop)
        
        self.route_preference = QSpinBox()
        self.route_preference.setRange(1, 255)
        self.route_preference.setValue(60)
        static_form.addRow("优先级:", self.route_preference)
        
        static_layout.addLayout(static_form)
        
        route_btn_layout = QHBoxLayout()
        add_route_btn = QPushButton("添加静态路由")
        add_route_btn.clicked.connect(self.add_static_route)
        route_btn_layout.addWidget(add_route_btn)
        
        add_default_btn = QPushButton("添加默认路由")
        add_default_btn.clicked.connect(self.add_default_route)
        route_btn_layout.addWidget(add_default_btn)
        static_layout.addLayout(route_btn_layout)
        
        self.route_list = QListWidget()
        self.route_list.setMaximumHeight(150)
        static_layout.addWidget(self.route_list)
        
        del_route_btn = QPushButton("删除选中")
        del_route_btn.clicked.connect(self.del_route)
        static_layout.addWidget(del_route_btn)
        
        static_group.setLayout(static_layout)
        left_panel.addWidget(static_group)
        
        ospf_group = QGroupBox("OSPF配置")
        ospf_layout = QVBoxLayout()
        
        ospf_form = QFormLayout()
        
        self.ospf_process_id = QSpinBox()
        self.ospf_process_id.setRange(1, 65535)
        self.ospf_process_id.setValue(1)
        ospf_form.addRow("进程ID:", self.ospf_process_id)
        
        self.ospf_router_id = QLineEdit()
        self.ospf_router_id.setPlaceholderText("例如: 1.1.1.1")
        ospf_form.addRow("Router ID:", self.ospf_router_id)
        
        self.ospf_area = QLineEdit()
        self.ospf_area.setText("0")
        ospf_form.addRow("区域ID:", self.ospf_area)
        
        self.ospf_network = QLineEdit()
        self.ospf_network.setPlaceholderText("例如: 192.168.1.0")
        ospf_form.addRow("网络地址:", self.ospf_network)
        
        self.ospf_wildcard = QLineEdit()
        self.ospf_wildcard.setPlaceholderText("例如: 0.0.0.255")
        ospf_form.addRow("反掩码:", self.ospf_wildcard)
        
        ospf_layout.addLayout(ospf_form)
        
        add_ospf_net_btn = QPushButton("添加OSPF网络")
        add_ospf_net_btn.clicked.connect(self.add_ospf_network)
        ospf_layout.addWidget(add_ospf_net_btn)
        
        self.ospf_net_list = QListWidget()
        self.ospf_net_list.setMaximumHeight(100)
        ospf_layout.addWidget(self.ospf_net_list)
        
        del_ospf_btn = QPushButton("删除选中")
        del_ospf_btn.clicked.connect(self.del_ospf_network)
        ospf_layout.addWidget(del_ospf_btn)
        
        ospf_group.setLayout(ospf_layout)
        left_panel.addWidget(ospf_group)
        
        left_panel.addStretch()
        layout.addLayout(left_panel, 1)
        
        right_panel = QVBoxLayout()
        
        bgp_group = QGroupBox("BGP配置")
        bgp_layout = QVBoxLayout()
        
        bgp_form = QFormLayout()
        
        self.bgp_as = QSpinBox()
        self.bgp_as.setRange(1, 65535)
        bgp_form.addRow("本地AS号:", self.bgp_as)
        
        self.bgp_router_id = QLineEdit()
        self.bgp_router_id.setPlaceholderText("例如: 1.1.1.1")
        bgp_form.addRow("Router ID:", self.bgp_router_id)
        
        self.bgp_peer_ip = QLineEdit()
        self.bgp_peer_ip.setPlaceholderText("对等体IP地址")
        bgp_form.addRow("对等体IP:", self.bgp_peer_ip)
        
        self.bgp_peer_as = QSpinBox()
        self.bgp_peer_as.setRange(1, 65535)
        bgp_form.addRow("对等体AS:", self.bgp_peer_as)
        
        bgp_layout.addLayout(bgp_form)
        
        add_peer_btn = QPushButton("添加BGP对等体")
        add_peer_btn.clicked.connect(self.add_bgp_peer)
        bgp_layout.addWidget(add_peer_btn)
        
        self.bgp_peer_list = QListWidget()
        self.bgp_peer_list.setMaximumHeight(100)
        bgp_layout.addWidget(self.bgp_peer_list)
        
        del_peer_btn = QPushButton("删除选中")
        del_peer_btn.clicked.connect(self.del_bgp_peer)
        bgp_layout.addWidget(del_peer_btn)
        
        bgp_network_input_layout = QHBoxLayout()
        bgp_network_input_layout.addWidget(QLabel("宣告网络:"))
        self.bgp_network_input = QLineEdit()
        self.bgp_network_input.setPlaceholderText("例如: 192.168.0.0")
        bgp_network_input_layout.addWidget(self.bgp_network_input)
        bgp_layout.addLayout(bgp_network_input_layout)
        
        self.bgp_networks = []
        self.bgp_network_list = QListWidget()
        self.bgp_network_list.setMaximumHeight(80)
        bgp_layout.addWidget(self.bgp_network_list)
        
        network_btn_layout = QHBoxLayout()
        add_net_btn = QPushButton("添加网络")
        add_net_btn.clicked.connect(self.add_bgp_network)
        network_btn_layout.addWidget(add_net_btn)
        
        del_net_btn = QPushButton("删除网络")
        del_net_btn.clicked.connect(self.del_bgp_network)
        network_btn_layout.addWidget(del_net_btn)
        bgp_layout.addLayout(network_btn_layout)
        
        bgp_group.setLayout(bgp_layout)
        right_panel.addWidget(bgp_group)
        
        rip_group = QGroupBox("RIP配置")
        rip_layout = QFormLayout()
        
        self.rip_version = QSpinBox()
        self.rip_version.setRange(1, 2)
        self.rip_version.setValue(2)
        rip_layout.addRow("RIP版本:", self.rip_version)
        
        self.rip_networks = QLineEdit()
        self.rip_networks.setPlaceholderText("例如: 192.168.0.0 10.0.0.0")
        rip_layout.addRow("网络:", self.rip_networks)
        
        rip_group.setLayout(rip_layout)
        right_panel.addWidget(rip_group)
        
        right_panel.addStretch()
        layout.addLayout(right_panel, 1)
    
    def add_static_route(self):
        dest = self.route_dest.text().strip()
        mask = self.route_mask.text().strip()
        nexthop = self.route_nexthop.text().strip()
        
        if not dest or not mask or not nexthop:
            QMessageBox.warning(self, "警告", "请填写完整的路由信息！")
            return
        
        route_data = {
            "dest_network": dest,
            "mask": mask,
            "next_hop": nexthop if "." in nexthop else None,
            "interface": nexthop if "." not in nexthop else None,
            "preference": self.route_preference.value()
        }
        
        self.static_routes.append(route_data)
        display_text = f"{dest}/{mask} -> {nexthop} (优先级: {self.route_preference.value()})"
        self.route_list.addItem(display_text)
        
        self.route_dest.clear()
        self.route_mask.clear()
        self.route_nexthop.clear()
        self.route_preference.setValue(60)
    
    def add_default_route(self):
        nexthop = self.route_nexthop.text().strip()
        if not nexthop:
            QMessageBox.warning(self, "警告", "请输入下一跳地址！")
            return
        
        route_data = {
            "dest_network": "0.0.0.0",
            "mask": "0.0.0.0",
            "next_hop": nexthop if "." in nexthop else None,
            "interface": nexthop if "." not in nexthop else None,
            "preference": 60
        }
        
        self.static_routes.append(route_data)
        self.route_list.addItem(f"默认路由 -> {nexthop}")
        
        self.route_dest.clear()
        self.route_mask.clear()
        self.route_nexthop.clear()
    
    def del_route(self):
        row = self.route_list.currentRow()
        if row >= 0:
            self.route_list.takeItem(row)
            del self.static_routes[row]
    
    def add_ospf_network(self):
        network = self.ospf_network.text().strip()
        wildcard = self.ospf_wildcard.text().strip()
        
        if not network:
            QMessageBox.warning(self, "警告", "请输入网络地址！")
            return
        
        self.ospf_networks.append({
            "address": network,
            "mask": wildcard or "0.0.0.255"
        })
        
        display_text = f"{network} {wildcard or '0.0.0.255'}"
        self.ospf_net_list.addItem(display_text)
        
        self.ospf_network.clear()
        self.ospf_wildcard.clear()
    
    def del_ospf_network(self):
        row = self.ospf_net_list.currentRow()
        if row >= 0:
            self.ospf_net_list.takeItem(row)
            del self.ospf_networks[row]
    
    def add_bgp_peer(self):
        peer_ip = self.bgp_peer_ip.text().strip()
        peer_as = self.bgp_peer_as.value()
        
        if not peer_ip:
            QMessageBox.warning(self, "警告", "请输入对等体IP！")
            return
        
        self.bgp_peers.append({
            "ip": peer_ip,
            "as": peer_as
        })
        
        self.bgp_peer_list.addItem(f"{peer_ip} AS{peer_as}")
        self.bgp_peer_ip.clear()
    
    def del_bgp_peer(self):
        row = self.bgp_peer_list.currentRow()
        if row >= 0:
            self.bgp_peer_list.takeItem(row)
            del self.bgp_peers[row]
    
    def add_bgp_network(self):
        network = self.bgp_network_input.text().strip()
        if not network:
            QMessageBox.warning(self, "警告", "请输入网络地址！")
            return
        
        self.bgp_networks.append(network)
        self.bgp_network_list.addItem(network)
        self.bgp_network_input.clear()
    
    def del_bgp_network(self):
        row = self.bgp_network_list.currentRow()
        if row >= 0:
            self.bgp_network_list.takeItem(row)
            del self.bgp_networks[row]
    
    def get_config(self):
        config = {}
        
        if self.static_routes:
            config["static_routes"] = self.static_routes
        
        if self.ospf_networks:
            config["ospf"] = {
                "process_id": self.ospf_process_id.value(),
                "router_id": self.ospf_router_id.text().strip() or None,
                "area_id": self.ospf_area.text().strip() or "0",
                "networks": self.ospf_networks
            }
        
        if self.bgp_peers or self.bgp_networks:
            config["bgp"] = {
                "as_number": self.bgp_as.value(),
                "router_id": self.bgp_router_id.text().strip() or None,
                "peers": self.bgp_peers,
                "networks": self.bgp_networks
            }
        
        rip_nets = self.rip_networks.text().strip()
        if rip_nets:
            config["rip"] = {
                "version": self.rip_version.value(),
                "networks": rip_nets.split()
            }
        
        if config:
            return RoutingConfigGenerator.generate_route_all(config)
        return ""
    
    def clear_config(self):
        self.static_routes.clear()
        self.ospf_networks.clear()
        self.bgp_peers.clear()
        self.bgp_networks.clear()
        
        self.route_list.clear()
        self.ospf_net_list.clear()
        self.bgp_peer_list.clear()
        self.bgp_network_list.clear()
        
        self.route_dest.clear()
        self.route_mask.clear()
        self.route_nexthop.clear()
        self.route_preference.setValue(60)
        
        self.ospf_process_id.setValue(1)
        self.ospf_router_id.clear()
        self.ospf_area.setText("0")
        self.ospf_network.clear()
        self.ospf_wildcard.clear()
        
        self.bgp_as.setValue(1)
        self.bgp_router_id.clear()
        self.bgp_peer_ip.clear()
        self.bgp_peer_as.setValue(1)
        self.bgp_network_input.clear()
    
    def get_config_data(self):
        """获取配置数据字典"""
        return {
            "static_routes": self.static_routes.copy(),
            "ospf_networks": self.ospf_networks.copy(),
            "bgp_peers": self.bgp_peers.copy(),
            "bgp_networks": self.bgp_networks.copy()
        }
    
    def load_config(self, config):
        """从配置字典加载配置"""
        if not config:
            return
        
        if "static_routes" in config:
            self.static_routes = config["static_routes"].copy()
            for route in self.static_routes:
                self.route_list.addItem(f"{route['dest']}/{route['mask']} -> {route['nexthop']}")
        
        if "ospf_networks" in config:
            self.ospf_networks = config["ospf_networks"].copy()
            for net in self.ospf_networks:
                self.ospf_net_list.addItem(f"{net['network']} Area {net['area']}")
        
        if "bgp_peers" in config:
            self.bgp_peers = config["bgp_peers"].copy()
        
        if "bgp_networks" in config:
            self.bgp_networks = config["bgp_networks"].copy()
        
        self.rip_version.setValue(2)
        self.rip_networks.clear()
