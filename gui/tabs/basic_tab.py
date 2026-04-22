#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NetOps Toolkit - 基础配置标签页（增强版）
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QSpinBox, QCheckBox, QGroupBox,
                             QComboBox, QTextEdit, QScrollArea, QFrame)
from PyQt5.QtCore import Qt
from modules.basic_config import BasicConfigGenerator


class BasicConfigTab(QWidget):
    """基础配置标签页"""
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(15)
        
        system_group = QGroupBox("系统配置")
        system_layout = QFormLayout()
        system_layout.setSpacing(10)
        
        self.hostname_input = QLineEdit()
        self.hostname_input.setPlaceholderText("例如: Core-Switch-01")
        system_layout.addRow("主机名:", self.hostname_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("管理密码")
        system_layout.addRow("管理密码:", self.password_input)
        
        self.encrypted_checkbox = QCheckBox("密文存储")
        system_layout.addRow("", self.encrypted_checkbox)
        
        system_group.setLayout(system_layout)
        main_layout.addWidget(system_group)
        
        mgmt_group = QGroupBox("管理接口配置")
        mgmt_layout = QFormLayout()
        mgmt_layout.setSpacing(10)
        
        self.mgmt_interface = QLineEdit()
        self.mgmt_interface.setText("Vlanif1")
        mgmt_layout.addRow("管理接口:", self.mgmt_interface)
        
        self.mgmt_ip = QLineEdit()
        self.mgmt_ip.setPlaceholderText("例如: 192.168.1.1")
        mgmt_layout.addRow("IP地址:", self.mgmt_ip)
        
        self.mgmt_mask = QLineEdit()
        self.mgmt_mask.setText("255.255.255.0")
        mgmt_layout.addRow("子网掩码:", self.mgmt_mask)
        
        self.mgmt_gateway = QLineEdit()
        self.mgmt_gateway.setPlaceholderText("网关地址(可选)")
        mgmt_layout.addRow("网关:", self.mgmt_gateway)
        
        mgmt_group.setLayout(mgmt_layout)
        main_layout.addWidget(mgmt_group)
        
        ssh_group = QGroupBox("SSH配置")
        ssh_layout = QFormLayout()
        ssh_layout.setSpacing(10)
        
        self.enable_ssh = QCheckBox("启用SSH")
        self.enable_ssh.setChecked(True)
        ssh_layout.addRow("", self.enable_ssh)
        
        self.ssh_version = QSpinBox()
        self.ssh_version.setRange(1, 2)
        self.ssh_version.setValue(2)
        ssh_layout.addRow("SSH版本:", self.ssh_version)
        
        self.ssh_port = QSpinBox()
        self.ssh_port.setRange(1, 65535)
        self.ssh_port.setValue(22)
        ssh_layout.addRow("SSH端口:", self.ssh_port)
        
        self.ssh_timeout = QSpinBox()
        self.ssh_timeout.setRange(10, 3600)
        self.ssh_timeout.setValue(60)
        self.ssh_timeout.setSuffix(" 秒")
        ssh_layout.addRow("超时时间:", self.ssh_timeout)
        
        self.ssh_max_auth = QSpinBox()
        self.ssh_max_auth.setRange(1, 10)
        self.ssh_max_auth.setValue(5)
        ssh_layout.addRow("最大认证次数:", self.ssh_max_auth)
        
        ssh_group.setLayout(ssh_layout)
        main_layout.addWidget(ssh_group)
        
        telnet_group = QGroupBox("Telnet配置")
        telnet_layout = QFormLayout()
        
        self.enable_telnet = QCheckBox("启用Telnet")
        telnet_layout.addRow("", self.enable_telnet)
        
        telnet_group.setLayout(telnet_layout)
        main_layout.addWidget(telnet_group)
        
        user_group = QGroupBox("用户配置")
        user_layout = QFormLayout()
        user_layout.setSpacing(10)
        
        self.username_input = QLineEdit()
        self.username_input.setText("admin")
        user_layout.addRow("用户名:", self.username_input)
        
        self.user_password_input = QLineEdit()
        self.user_password_input.setText("Admin@123")
        self.user_password_input.setEchoMode(QLineEdit.Password)
        user_layout.addRow("用户密码:", self.user_password_input)
        
        self.privilege_level = QSpinBox()
        self.privilege_level.setRange(0, 15)
        self.privilege_level.setValue(15)
        user_layout.addRow("权限级别:", self.privilege_level)
        
        self.user_encrypted = QCheckBox("密码密文存储")
        user_layout.addRow("", self.user_encrypted)
        
        user_group.setLayout(user_layout)
        main_layout.addWidget(user_group)
        
        ntp_group = QGroupBox("NTP时间同步")
        ntp_layout = QFormLayout()
        ntp_layout.setSpacing(10)
        
        self.ntp_server1 = QLineEdit()
        self.ntp_server1.setPlaceholderText("NTP服务器1，例如: 10.1.1.1")
        ntp_layout.addRow("NTP服务器1:", self.ntp_server1)
        
        self.ntp_server2 = QLineEdit()
        self.ntp_server2.setPlaceholderText("NTP服务器2(可选)")
        ntp_layout.addRow("NTP服务器2:", self.ntp_server2)
        
        self.ntp_timezone = QComboBox()
        self.ntp_timezone.addItems(["UTC+8", "UTC+0", "UTC-5", "UTC-8"])
        ntp_layout.addRow("时区:", self.ntp_timezone)
        
        ntp_group.setLayout(ntp_layout)
        main_layout.addWidget(ntp_group)
        
        snmp_group = QGroupBox("SNMP配置")
        snmp_layout = QFormLayout()
        snmp_layout.setSpacing(10)
        
        self.snmp_version = QComboBox()
        self.snmp_version.addItems(["v2c", "v3", "all"])
        snmp_layout.addRow("SNMP版本:", self.snmp_version)
        
        self.snmp_read = QLineEdit()
        self.snmp_read.setPlaceholderText("只读社区字符串")
        snmp_layout.addRow("读取社区:", self.snmp_read)
        
        self.snmp_write = QLineEdit()
        self.snmp_write.setPlaceholderText("读写社区字符串(可选)")
        snmp_layout.addRow("写入社区:", self.snmp_write)
        
        self.snmp_location = QLineEdit()
        self.snmp_location.setPlaceholderText("设备位置")
        snmp_layout.addRow("位置:", self.snmp_location)
        
        self.snmp_contact = QLineEdit()
        self.snmp_contact.setPlaceholderText("联系人信息")
        snmp_layout.addRow("联系人:", self.snmp_contact)
        
        self.snmp_trap = QCheckBox("启用Trap")
        snmp_layout.addRow("", self.snmp_trap)
        
        self.snmp_trap_host = QLineEdit()
        self.snmp_trap_host.setPlaceholderText("Trap目标主机IP")
        snmp_layout.addRow("Trap主机:", self.snmp_trap_host)
        
        snmp_group.setLayout(snmp_layout)
        main_layout.addWidget(snmp_group)
        
        log_group = QGroupBox("日志配置")
        log_layout = QFormLayout()
        log_layout.setSpacing(10)
        
        self.log_enable = QCheckBox("启用信息中心")
        self.log_enable.setChecked(True)
        log_layout.addRow("", self.log_enable)
        
        self.log_host = QLineEdit()
        self.log_host.setPlaceholderText("日志服务器IP")
        log_layout.addRow("日志服务器:", self.log_host)
        
        self.log_level = QComboBox()
        self.log_level.addItems(["emergencies", "alerts", "critical", "errors", "warnings", "notifications", "informational", "debugging"])
        self.log_level.setCurrentText("informational")
        log_layout.addRow("日志级别:", self.log_level)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        banner_group = QGroupBox("Banner配置")
        banner_layout = QFormLayout()
        
        self.motd_input = QTextEdit()
        self.motd_input.setMaximumHeight(60)
        self.motd_input.setPlaceholderText("登录后显示的消息")
        banner_layout.addRow("MOTD:", self.motd_input)
        
        self.login_input = QTextEdit()
        self.login_input.setMaximumHeight(60)
        self.login_input.setPlaceholderText("登录前显示的消息")
        banner_layout.addRow("Login Banner:", self.login_input)
        
        banner_group.setLayout(banner_layout)
        main_layout.addWidget(banner_group)
        
        dns_group = QGroupBox("DNS配置")
        dns_layout = QFormLayout()
        
        self.dns_server1 = QLineEdit()
        self.dns_server1.setPlaceholderText("DNS服务器1")
        dns_layout.addRow("DNS服务器1:", self.dns_server1)
        
        self.dns_server2 = QLineEdit()
        self.dns_server2.setPlaceholderText("DNS服务器2(可选)")
        dns_layout.addRow("DNS服务器2:", self.dns_server2)
        
        self.dns_domain = QLineEdit()
        self.dns_domain.setPlaceholderText("域名后缀(可选)")
        dns_layout.addRow("域名:", self.dns_domain)
        
        dns_group.setLayout(dns_layout)
        main_layout.addWidget(dns_group)
        
        main_layout.addStretch()
        scroll.setWidget(container)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
    
    def get_config(self):
        hostname = self.hostname_input.text().strip()
        password = self.password_input.text().strip()
        
        config = {}
        if hostname:
            config["hostname"] = hostname
        
        if password:
            config["password"] = {
                "value": password,
                "encrypted": self.encrypted_checkbox.isChecked()
            }
        
        if self.enable_ssh.isChecked():
            config["enable_ssh"] = True
            config["ssh_version"] = self.ssh_version.value()
            config["ssh_port"] = self.ssh_port.value()
            config["ssh_timeout"] = self.ssh_timeout.value()
            config["ssh_max_auth_tries"] = self.ssh_max_auth.value()
        
        if self.enable_telnet.isChecked():
            config["enable_telnet"] = True
        
        username = self.username_input.text().strip()
        user_password = self.user_password_input.text().strip()
        if username and user_password:
            config["user"] = {
                "username": username,
                "password": user_password,
                "level": self.privilege_level.value(),
                "encrypted": self.user_encrypted.isChecked()
            }
        
        mgmt_ip = self.mgmt_ip.text().strip()
        if mgmt_ip:
            config["mgmt_interface"] = {
                "interface": self.mgmt_interface.text().strip() or "Vlanif1",
                "ip_address": mgmt_ip,
                "mask": self.mgmt_mask.text().strip() or "255.255.255.0",
                "gateway": self.mgmt_gateway.text().strip() or None
            }
        
        ntp_servers = []
        ntp1 = self.ntp_server1.text().strip()
        ntp2 = self.ntp_server2.text().strip()
        if ntp1:
            ntp_servers.append({"ip": ntp1, "prefer": True})
        if ntp2:
            ntp_servers.append({"ip": ntp2, "prefer": False})
        
        if ntp_servers:
            config["ntp"] = {
                "servers": ntp_servers,
                "timezone": self.ntp_timezone.currentText()
            }
        
        snmp_read = self.snmp_read.text().strip()
        if snmp_read or self.snmp_write.text().strip():
            config["snmp"] = {
                "version": self.snmp_version.currentText(),
                "community_read": snmp_read or None,
                "community_write": self.snmp_write.text().strip() or None,
                "sys_location": self.snmp_location.text().strip() or None,
                "sys_contact": self.snmp_contact.text().strip() or None,
                "trap_enable": self.snmp_trap.isChecked(),
                "trap_host": self.snmp_trap_host.text().strip() or None
            }
        
        log_host = self.log_host.text().strip()
        if self.log_enable.isChecked() or log_host:
            config["log"] = {
                "info_center_enable": self.log_enable.isChecked(),
                "host": log_host or None,
                "log_level": self.log_level.currentText()
            }
        
        motd = self.motd_input.toPlainText().strip()
        login = self.login_input.toPlainText().strip()
        if motd or login:
            config["banner"] = {
                "motd": motd,
                "login": login
            }
        
        dns_servers = []
        dns1 = self.dns_server1.text().strip()
        dns2 = self.dns_server2.text().strip()
        if dns1:
            dns_servers.append(dns1)
        if dns2:
            dns_servers.append(dns2)
        
        if dns_servers:
            config["dns"] = {
                "servers": dns_servers,
                "domain": self.dns_domain.text().strip() or None
            }
        
        if config:
            return BasicConfigGenerator.generate_basic_all(config)
        return ""
    
    def clear_config(self):
        self.hostname_input.clear()
        self.password_input.clear()
        self.encrypted_checkbox.setChecked(False)
        
        self.mgmt_interface.setText("Vlanif1")
        self.mgmt_ip.clear()
        self.mgmt_mask.setText("255.255.255.0")
        self.mgmt_gateway.clear()
        
        self.enable_ssh.setChecked(True)
        self.ssh_version.setValue(2)
        self.ssh_port.setValue(22)
        self.ssh_timeout.setValue(60)
        self.ssh_max_auth.setValue(5)
        
        self.enable_telnet.setChecked(False)
        
        self.username_input.setText("admin")
        self.user_password_input.setText("Admin@123")
        self.privilege_level.setValue(15)
        self.user_encrypted.setChecked(False)
        
        self.ntp_server1.clear()
        self.ntp_server2.clear()
        self.ntp_timezone.setCurrentIndex(0)
        
        self.snmp_version.setCurrentIndex(0)
        self.snmp_read.clear()
        self.snmp_write.clear()
        self.snmp_location.clear()
        self.snmp_contact.clear()
        self.snmp_trap.setChecked(False)
        self.snmp_trap_host.clear()
        
        self.log_enable.setChecked(True)
        self.log_host.clear()
        self.log_level.setCurrentText("informational")
        
        self.motd_input.clear()
        self.login_input.clear()
        
        self.dns_server1.clear()
        self.dns_server2.clear()
        self.dns_domain.clear()
    
    def get_config_data(self):
        """获取配置数据字典（用于保存模板）"""
        data = {}
        
        hostname = self.hostname_input.text().strip()
        if hostname:
            data["hostname"] = hostname
        
        password = self.password_input.text().strip()
        if password:
            data["password"] = {
                "value": password,
                "encrypted": self.encrypted_checkbox.isChecked()
            }
        
        mgmt_ip = self.mgmt_ip.text().strip()
        if mgmt_ip:
            data["mgmt_interface"] = {
                "interface": self.mgmt_interface.text().strip() or "Vlanif1",
                "ip_address": mgmt_ip,
                "mask": self.mgmt_mask.text().strip() or "255.255.255.0",
                "gateway": self.mgmt_gateway.text().strip() or None
            }
        
        if self.enable_ssh.isChecked():
            data["enable_ssh"] = True
            data["ssh_version"] = self.ssh_version.value()
            data["ssh_port"] = self.ssh_port.value()
        
        if self.enable_telnet.isChecked():
            data["enable_telnet"] = True
        
        username = self.username_input.text().strip()
        user_password = self.user_password_input.text().strip()
        if username and user_password:
            data["user"] = {
                "username": username,
                "password": user_password,
                "level": self.privilege_level.value()
            }
        
        return data
    
    def load_config(self, config):
        """从配置字典加载配置（用于应用模板）"""
        if not config:
            return
        
        if "hostname" in config:
            self.hostname_input.setText(config["hostname"])
        
        if "password" in config:
            self.password_input.setText(config["password"].get("value", ""))
            self.encrypted_checkbox.setChecked(config["password"].get("encrypted", False))
        
        if "mgmt_interface" in config:
            mgmt = config["mgmt_interface"]
            self.mgmt_interface.setText(mgmt.get("interface", "Vlanif1"))
            self.mgmt_ip.setText(mgmt.get("ip_address", ""))
            self.mgmt_mask.setText(mgmt.get("mask", "255.255.255.0"))
            self.mgmt_gateway.setText(mgmt.get("gateway", ""))
        
        if config.get("enable_ssh"):
            self.enable_ssh.setChecked(True)
            self.ssh_version.setValue(config.get("ssh_version", 2))
            self.ssh_port.setValue(config.get("ssh_port", 22))
        
        if config.get("enable_telnet"):
            self.enable_telnet.setChecked(True)
        
        if "user" in config:
            user = config["user"]
            self.username_input.setText(user.get("username", ""))
            self.user_password_input.setText(user.get("password", ""))
            self.privilege_level.setValue(user.get("level", 15))
