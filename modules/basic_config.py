#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NetOps Toolkit - 基础配置模块（增强版）
"""


class BasicConfigGenerator:
    """基础配置生成器"""
    
    @staticmethod
    def generate_hostname(hostname: str) -> str:
        """生成主机名配置"""
        return f"sysname {hostname}\n"
    
    @staticmethod
    def generate_password(password: str, encrypted: bool = False) -> str:
        """生成密码配置"""
        if encrypted:
            return f"super password cipher {password}\n"
        return f"super password simple {password}\n"
    
    @staticmethod
    def generate_ssh_config(enable: bool = True, 
                           version: int = 2,
                           port: int = 22,
                           timeout: int = 60,
                           max_auth_tries: int = 5,
                           rekey_interval: int = 60) -> str:
        """生成SSH配置"""
        config_lines = []
        config_lines.append("rsa local-key-pair create\n")
        config_lines.append("stelnet server enable\n")
        config_lines.append(f"ssh server port {port}\n")
        config_lines.append(f"ssh server timeout {timeout}\n")
        config_lines.append(f"ssh server max-auth-times {max_auth_tries}\n")
        config_lines.append(f"ssh server rekey-interval {rekey_interval}\n")
        config_lines.append("ssh server compatible-huawei-version enable\n")
        config_lines.append(f"ssh version {version}\n")
        config_lines.append("ssh user admin\n")
        config_lines.append("ssh user admin authentication-type password\n")
        config_lines.append("ssh user admin service-type stelnet\n")
        config_lines.append("user-interface vty 0 4\n")
        config_lines.append(" authentication-mode aaa\n")
        config_lines.append(" protocol inbound ssh\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_telnet_config(enable: bool = True) -> str:
        """生成Telnet配置"""
        config_lines = []
        config_lines.append("telnet server enable\n")
        config_lines.append("user-interface vty 0 4\n")
        config_lines.append(" authentication-mode aaa\n")
        config_lines.append(" protocol inbound telnet\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_console_config(password: str = None,
                                authentication: str = "password",
                                idle_timeout: int = 10) -> str:
        """生成Console口配置"""
        config_lines = []
        config_lines.append("user-interface console 0\n")
        if authentication == "password" and password:
            config_lines.append(" authentication-mode password\n")
            config_lines.append(f" set authentication password simple {password}\n")
        elif authentication == "aaa":
            config_lines.append(" authentication-mode aaa\n")
        config_lines.append(f" idle-timeout {idle_timeout} 0\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_banner(motd: str = None, 
                       login: str = None) -> str:
        """生成Banner配置"""
        config_lines = []
        if motd:
            config_lines.append(f"header shell information \"{'#' * 50}\n{motd}\n{'#' * 50}\"\n")
        if login:
            config_lines.append(f"header login information \"{'#' * 50}\n{login}\n{'#' * 50}\"\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_aaa_user(username: str = "admin",
                         password: str = "admin@123",
                         level: int = 15,
                         encrypted: bool = False,
                         service_types: list = None) -> str:
        """生成用户配置"""
        config_lines = []
        config_lines.append("aaa\n")
        config_lines.append(f" local-user {username} password {'cipher' if encrypted else 'simple'} {password}\n")
        config_lines.append(f" local-user {username} privilege level {level}\n")
        if service_types is None:
            service_types = ["terminal", "ssh", "telnet"]
        config_lines.append(f" local-user {username} service-type {' '.join(service_types)}\n")
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_ntp_config(servers: list = None,
                           timezone: str = "UTC+8",
                           broadcast_enable: bool = False) -> str:
        """生成NTP配置"""
        config_lines = []
        config_lines.append(f"clock timezone {timezone} add 08:00:00\n")
        
        if servers:
            for idx, server in enumerate(servers, 1):
                server_ip = server.get("ip")
                prefer = server.get("prefer", False)
                config_lines.append(f"ntp-service unicast-server {server_ip}")
                if prefer:
                    config_lines.append(" preference")
                config_lines.append("\n")
        
        if broadcast_enable:
            config_lines.append("ntp-service broadcast enable\n")
        
        return "".join(config_lines)
    
    @staticmethod
    def generate_snmp_config(version: str = "v2c",
                            community_read: str = None,
                            community_write: str = None,
                            sys_name: str = None,
                            sys_location: str = None,
                            sys_contact: str = None,
                            trap_enable: bool = False,
                            trap_host: str = None) -> str:
        """生成SNMP配置"""
        config_lines = []
        config_lines.append(f"snmp-agent\n")
        config_lines.append(f"snmp-agent sys-info version {version}\n")
        
        if sys_name:
            config_lines.append(f"snmp-agent sys-info contact {sys_contact}\n")
        if sys_location:
            config_lines.append(f"snmp-agent sys-info location {sys_location}\n")
        if sys_contact:
            config_lines.append(f"snmp-agent sys-info contact {sys_contact}\n")
        
        if version in ["v2c", "all"]:
            if community_read:
                config_lines.append(f"snmp-agent community read {community_read}\n")
            if community_write:
                config_lines.append(f"snmp-agent community write {community_write}\n")
        
        if trap_enable and trap_host:
            config_lines.append("snmp-agent trap enable\n")
            config_lines.append(f"snmp-agent target-host trap address udp-domain {trap_host} params securityname public\n")
        
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_log_config(host: str = None,
                           info_center_enable: bool = True,
                           log_level: str = "informational",
                           time_stamp: str = "date") -> str:
        """生成日志配置"""
        config_lines = []
        
        if info_center_enable:
            config_lines.append("info-center enable\n")
        
        config_lines.append(f"info-center timestamp log {time_stamp}\n")
        
        if host:
            config_lines.append(f"info-center loghost {host}\n")
            config_lines.append(f"info-center loghost source Vlanif1\n")
        
        config_lines.append(f"info-center console channel 0\n")
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_mgmt_interface(interface: str = "Vlanif1",
                                ip_address: str = None,
                                mask: str = "255.255.255.0",
                                gateway: str = None,
                                description: str = "Management Interface") -> str:
        """生成管理接口配置"""
        config_lines = []
        config_lines.append(f"interface {interface}\n")
        config_lines.append(f" description {description}\n")
        
        if ip_address:
            config_lines.append(f" ip address {ip_address} {mask}\n")
        
        config_lines.append("#\n")
        
        if gateway:
            config_lines.append(f"ip route-static 0.0.0.0 0.0.0.0 {gateway}\n")
        
        return "".join(config_lines)
    
    @staticmethod
    def generate_dhcp_config(enable: bool = True,
                            excluded_ips: list = None,
                            dns_servers: list = None) -> str:
        """生成DHCP配置"""
        config_lines = []
        
        if enable:
            config_lines.append("dhcp enable\n")
        
        if excluded_ips:
            for ip_range in excluded_ips:
                start = ip_range.get("start")
                end = ip_range.get("end")
                if end:
                    config_lines.append(f"dhcp server excluded-ip-address {start} {end}\n")
                else:
                    config_lines.append(f"dhcp server excluded-ip-address {start}\n")
        
        if dns_servers:
            config_lines.append(f"dhcp server dns-list {' '.join(dns_servers)}\n")
        
        return "".join(config_lines)
    
    @staticmethod
    def generate_dns_config(servers: list = None,
                           domain: str = None,
                           resolve_enable: bool = True) -> str:
        """生成DNS配置"""
        config_lines = []
        
        if resolve_enable:
            config_lines.append("ip dns resolve\n")
        
        if servers:
            for idx, server in enumerate(servers, 1):
                config_lines.append(f"ip dns server {server}\n")
        
        if domain:
            config_lines.append(f"ip dns domain {domain}\n")
        
        return "".join(config_lines)
    
    @staticmethod
    def generate_vlan_config(enable: bool = True) -> str:
        """生成VLAN批量创建"""
        if not enable:
            return ""
        return "vlan batch 1\n"
    
    @staticmethod
    def generate_basic_all(config: dict) -> str:
        """生成完整基础配置"""
        config_lines = ["#\n", "# 基础配置\n", "#\n"]
        
        if "hostname" in config:
            config_lines.append(BasicConfigGenerator.generate_hostname(config["hostname"]))
        
        if "password" in config:
            config_lines.append(BasicConfigGenerator.generate_password(
                config["password"]["value"],
                config["password"].get("encrypted", False)
            ))
        
        if config.get("enable_ssh", False):
            config_lines.append("\n#\n# SSH配置\n#\n")
            config_lines.append(BasicConfigGenerator.generate_ssh_config(
                version=config.get("ssh_version", 2),
                port=config.get("ssh_port", 22),
                timeout=config.get("ssh_timeout", 60),
                max_auth_tries=config.get("ssh_max_auth_tries", 5),
                rekey_interval=config.get("ssh_rekey_interval", 60)
            ))
        
        if config.get("enable_telnet", False):
            config_lines.append("\n#\n# Telnet配置\n#\n")
            config_lines.append(BasicConfigGenerator.generate_telnet_config())
        
        if "console" in config:
            config_lines.append("\n#\n# Console配置\n#\n")
            config_lines.append(BasicConfigGenerator.generate_console_config(
                config["console"].get("password"),
                config["console"].get("authentication", "password"),
                config["console"].get("idle_timeout", 10)
            ))
        
        if "banner" in config:
            config_lines.append("\n#\n# Banner配置\n#\n")
            config_lines.append(BasicConfigGenerator.generate_banner(
                config["banner"].get("motd"),
                config["banner"].get("login")
            ))
        
        if "user" in config:
            config_lines.append("\n#\n# 用户配置\n#\n")
            config_lines.append(BasicConfigGenerator.generate_aaa_user(
                config["user"].get("username", "admin"),
                config["user"].get("password", "admin@123"),
                config["user"].get("level", 15),
                config["user"].get("encrypted", False),
                config["user"].get("service_types")
            ))
        
        if "ntp" in config:
            config_lines.append("\n#\n# NTP配置\n#\n")
            config_lines.append(BasicConfigGenerator.generate_ntp_config(
                config["ntp"].get("servers"),
                config["ntp"].get("timezone", "UTC+8"),
                config["ntp"].get("broadcast_enable", False)
            ))
        
        if "snmp" in config:
            config_lines.append("\n#\n# SNMP配置\n#\n")
            config_lines.append(BasicConfigGenerator.generate_snmp_config(
                config["snmp"].get("version", "v2c"),
                config["snmp"].get("community_read"),
                config["snmp"].get("community_write"),
                config["snmp"].get("sys_name"),
                config["snmp"].get("sys_location"),
                config["snmp"].get("sys_contact"),
                config["snmp"].get("trap_enable", False),
                config["snmp"].get("trap_host")
            ))
        
        if "log" in config:
            config_lines.append("\n#\n# 日志配置\n#\n")
            config_lines.append(BasicConfigGenerator.generate_log_config(
                config["log"].get("host"),
                config["log"].get("info_center_enable", True),
                config["log"].get("log_level", "informational"),
                config["log"].get("time_stamp", "date")
            ))
        
        if "mgmt_interface" in config:
            config_lines.append("\n#\n# 管理接口配置\n#\n")
            config_lines.append(BasicConfigGenerator.generate_mgmt_interface(
                config["mgmt_interface"].get("interface", "Vlanif1"),
                config["mgmt_interface"].get("ip_address"),
                config["mgmt_interface"].get("mask", "255.255.255.0"),
                config["mgmt_interface"].get("gateway"),
                config["mgmt_interface"].get("description", "Management Interface")
            ))
        
        if "dhcp_global" in config:
            config_lines.append("\n#\n# DHCP全局配置\n#\n")
            config_lines.append(BasicConfigGenerator.generate_dhcp_config(
                config["dhcp_global"].get("enable", True),
                config["dhcp_global"].get("excluded_ips"),
                config["dhcp_global"].get("dns_servers")
            ))
        
        if "dns" in config:
            config_lines.append("\n#\n# DNS配置\n#\n")
            config_lines.append(BasicConfigGenerator.generate_dns_config(
                config["dns"].get("servers"),
                config["dns"].get("domain"),
                config["dns"].get("resolve_enable", True)
            ))
        
        return "".join(config_lines)
