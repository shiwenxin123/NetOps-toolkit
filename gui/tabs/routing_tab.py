#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NetOps Toolkit - 路由配置标签页
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QSpinBox, QCheckBox, QGroupBox,
                             QComboBox, QPushButton, QListWidget, QMessageBox, QLabel,
                             QScrollArea, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer
from modules.routing_config import RoutingConfigGenerator


class RoutingConfigTab(QWidget):
    """路由配置标签页"""
    
    def __init__(self):
        super().__init__()
        self.static_routes = []
        self.ospf_networks = []
        self.bgp_peers = []
        self.real_servers = []
        self.virtual_servers = []
        self.initUI()
    
    def initUI(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        # Keep the preferred row height (so inputs are not crushed) and let
        # the scroll area move vertically. Width may shrink with the pane.
        container.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
        self._form_container = container
        layout = QHBoxLayout(container)

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

        slb_group = QGroupBox("服务器负载均衡（华三 SecPath）")
        self.slb_group = slb_group
        slb_group.setVisible(False)
        slb_layout = QVBoxLayout()
        slb_form = QFormLayout()
        self.slb_farm = QLineEdit("web")
        self.slb_farm.setPlaceholderText("实服务组名称，例如 web")
        slb_form.addRow("实服务组:", self.slb_farm)
        self.slb_predictor = QComboBox()
        self.slb_predictor.addItems([
            "round-robin", "random", "least-connection", "hash-source", "hash-destination"
        ])
        slb_form.addRow("调度算法:", self.slb_predictor)
        slb_layout.addLayout(slb_form)
        self.slb_icmp = QCheckBox("ICMP 健康检查（nqa template icmp）")
        self.slb_icmp.setChecked(True)
        slb_layout.addWidget(self.slb_icmp)

        rs_form = QFormLayout()
        self.slb_rs_name = QLineEdit()
        self.slb_rs_name.setPlaceholderText("例如: rs1")
        rs_form.addRow("实服务器:", self.slb_rs_name)
        self.slb_rs_ip = QLineEdit()
        self.slb_rs_ip.setPlaceholderText("例如: 192.168.10.11")
        rs_form.addRow("地址:", self.slb_rs_ip)
        self.slb_rs_port = QSpinBox()
        self.slb_rs_port.setRange(0, 65535)
        self.slb_rs_port.setValue(80)
        rs_form.addRow("端口:", self.slb_rs_port)
        self.slb_rs_weight = QSpinBox()
        self.slb_rs_weight.setRange(1, 255)
        self.slb_rs_weight.setValue(100)
        rs_form.addRow("权值:", self.slb_rs_weight)
        slb_layout.addLayout(rs_form)
        add_rs_btn = QPushButton("添加实服务器")
        add_rs_btn.clicked.connect(self.add_real_server)
        slb_layout.addWidget(add_rs_btn)
        self.slb_rs_list = QListWidget()
        self.slb_rs_list.setMaximumHeight(80)
        slb_layout.addWidget(self.slb_rs_list)
        del_rs_btn = QPushButton("删除选中实服务器")
        del_rs_btn.clicked.connect(self.del_real_server)
        slb_layout.addWidget(del_rs_btn)

        vs_form = QFormLayout()
        self.slb_vs_name = QLineEdit()
        self.slb_vs_name.setPlaceholderText("例如: vs-web")
        vs_form.addRow("虚服务器:", self.slb_vs_name)
        self.slb_vs_type = QComboBox()
        self.slb_vs_type.addItems(["tcp", "http", "udp", "ip"])
        vs_form.addRow("类型:", self.slb_vs_type)
        self.slb_vs_ip = QLineEdit()
        self.slb_vs_ip.setPlaceholderText("例如: 192.168.1.80")
        vs_form.addRow("虚地址:", self.slb_vs_ip)
        self.slb_vs_port = QSpinBox()
        self.slb_vs_port.setRange(0, 65535)
        self.slb_vs_port.setValue(80)
        vs_form.addRow("虚端口:", self.slb_vs_port)
        slb_layout.addLayout(vs_form)
        add_vs_btn = QPushButton("添加虚服务器")
        add_vs_btn.clicked.connect(self.add_virtual_server)
        slb_layout.addWidget(add_vs_btn)
        self.slb_vs_list = QListWidget()
        self.slb_vs_list.setMaximumHeight(70)
        slb_layout.addWidget(self.slb_vs_list)
        del_vs_btn = QPushButton("删除选中虚服务器")
        del_vs_btn.clicked.connect(self.del_virtual_server)
        slb_layout.addWidget(del_vs_btn)
        slb_group.setLayout(slb_layout)
        right_panel.addWidget(slb_group)

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

        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._lock_form_height)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._lock_form_height()

    def _lock_form_height(self):
        """Stop the scroll area from squeezing rows once styles are applied."""
        content = getattr(self, "_form_container", None)
        if content is None or content.layout() is None:
            return
        preferred = content.layout().sizeHint().height()
        if preferred > content.minimumHeight():
            content.setMinimumHeight(preferred)

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
    
    def collect_config(self):
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

        slb = self._slb_payload()
        if slb:
            config["slb"] = slb
        
        return config
    
    def get_config(self):
        config = self.collect_config()
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

        self.real_servers.clear()
        self.virtual_servers.clear()
        self.slb_rs_list.clear()
        self.slb_vs_list.clear()
        self.slb_farm.setText("web")
        self.slb_predictor.setCurrentIndex(0)
        self.slb_icmp.setChecked(True)
        self.slb_rs_name.clear()
        self.slb_rs_ip.clear()
        self.slb_rs_port.setValue(80)
        self.slb_rs_weight.setValue(100)
        self.slb_vs_name.clear()
        self.slb_vs_ip.clear()
        self.slb_vs_type.setCurrentIndex(0)
        self.slb_vs_port.setValue(80)
    
    def get_config_data(self):
        """获取配置数据字典"""
        data = {
            "static_routes": self.static_routes.copy(),
            "ospf_networks": self.ospf_networks.copy(),
            "bgp_peers": self.bgp_peers.copy(),
            "bgp_networks": self.bgp_networks.copy()
        }
        slb = self._slb_payload()
        if slb:
            data["slb"] = slb
        return data
    
    def load_config(self, config):
        """从配置字典加载配置"""
        if not config:
            return
        
        if "static_routes" in config:
            self.static_routes = config["static_routes"].copy()
            for route in self.static_routes:
                dest = route.get("dest_network") or route.get("dest", "")
                nexthop = route.get("next_hop") or route.get("nexthop") or route.get("interface", "")
                self.route_list.addItem(f"{dest}/{route.get('mask', '')} -> {nexthop}")
        
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

        slb = config.get("slb") or {}
        if slb:
            self.slb_farm.setText(slb.get("server_farm") or "web")
            predictor = slb.get("predictor") or "round-robin"
            index = self.slb_predictor.findText(predictor)
            if index >= 0:
                self.slb_predictor.setCurrentIndex(index)
            self.slb_icmp.setChecked(slb.get("health_check", "icmp") == "icmp")
            self.real_servers = [dict(item) for item in slb.get("real_servers") or []]
            self.slb_rs_list.clear()
            for item in self.real_servers:
                self.slb_rs_list.addItem(self._real_label(item))
            self.virtual_servers = [dict(item) for item in slb.get("virtual_servers") or []]
            self.slb_vs_list.clear()
            for item in self.virtual_servers:
                self.slb_vs_list.addItem(self._virtual_label(item))

    def set_slb_visible(self, visible):
        self.slb_group.setVisible(bool(visible))

    def _slb_payload(self):
        if not self.real_servers and not self.virtual_servers:
            return None
        return {
            "server_farm": self.slb_farm.text().strip() or "web",
            "predictor": self.slb_predictor.currentText(),
            "health_check": "icmp" if self.slb_icmp.isChecked() else "",
            "real_servers": [dict(item) for item in self.real_servers],
            "virtual_servers": [dict(item) for item in self.virtual_servers],
        }

    @staticmethod
    def _real_label(item):
        return f"{item.get('name', '')} {item.get('ip', '')}:{item.get('port', '')} 权值 {item.get('weight', '')}"

    @staticmethod
    def _virtual_label(item):
        return f"{item.get('name', '')} {item.get('type', 'tcp')} {item.get('ip', '')}:{item.get('port', '')}"

    def add_real_server(self):
        name = self.slb_rs_name.text().strip()
        ip_addr = self.slb_rs_ip.text().strip()
        if not name or not ip_addr:
            QMessageBox.warning(self, "警告", "请填写实服务器名称和地址！")
            return
        item = {
            "name": name,
            "ip": ip_addr,
            "port": self.slb_rs_port.value(),
            "weight": self.slb_rs_weight.value(),
        }
        self.real_servers.append(item)
        self.slb_rs_list.addItem(self._real_label(item))
        self.slb_rs_name.clear()
        self.slb_rs_ip.clear()

    def del_real_server(self):
        row = self.slb_rs_list.currentRow()
        if row >= 0:
            self.slb_rs_list.takeItem(row)
            del self.real_servers[row]

    def add_virtual_server(self):
        name = self.slb_vs_name.text().strip()
        ip_addr = self.slb_vs_ip.text().strip()
        if not name or not ip_addr:
            QMessageBox.warning(self, "警告", "请填写虚服务器名称和地址！")
            return
        item = {
            "name": name,
            "type": self.slb_vs_type.currentText(),
            "ip": ip_addr,
            "port": self.slb_vs_port.value(),
        }
        self.virtual_servers.append(item)
        self.slb_vs_list.addItem(self._virtual_label(item))
        self.slb_vs_name.clear()
        self.slb_vs_ip.clear()

    def del_virtual_server(self):
        row = self.slb_vs_list.currentRow()
        if row >= 0:
            self.slb_vs_list.takeItem(row)
            del self.virtual_servers[row]
