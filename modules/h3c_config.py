#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
H3C华三交换机配置生成器
"""

import time
from typing import Dict, List, Optional, Any


class H3CConfigGenerator:
    """H3C华三交换机配置生成器"""
    
    @staticmethod
    def generate_header(description: str = "H3C Switch Configuration") -> str:
        """生成配置头部注释"""
        return f"""#
# H3C华三交换机配置脚本
# 描述: {description}
# 生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
# 设备品牌: H3C (Huawei-3Com)
#
"""
    
    @staticmethod
    def generate_basic_config(config: Dict[str, Any]) -> str:
        """
        生成基础配置
        
        Args:
            config: 基础配置字典
                - hostname: 主机名
                - password: 密码配置
                - mgmt_interface: 管理接口配置
                - ssh: SSH配置
                - telnet: Telnet配置
                - user: 用户配置
                
        Returns:
            配置字符串
        """
        lines = []
        lines.append("\n# ==================== 基础配置 ====================")
        lines.append("#\n# 设备基本设置\n#")
        
        if config.get("hostname"):
            lines.append(f"\nsysname {config['hostname']}")
        
        if config.get("password"):
            pwd_config = config["password"]
            pwd = pwd_config.get("value", "")
            encrypted = pwd_config.get("encrypted", False)
            
            if encrypted:
                lines.append(f"\nsuper password cipher {pwd}")
            else:
                lines.append(f"\nsuper password simple {pwd}")
        
        if config.get("mgmt_interface"):
            mgmt = config["mgmt_interface"]
            interface = mgmt.get("interface", "Vlan-interface1")
            ip = mgmt.get("ip_address", "")
            mask = mgmt.get("mask", "255.255.255.0")
            gateway = mgmt.get("gateway", "")
            
            if ip:
                lines.append(f"\ninterface {interface}")
                lines.append(f" ip address {ip} {mask}")
                lines.append(" quit")
            
            if gateway:
                lines.append(f"\nip route-static 0.0.0.0 0 {gateway}")
        
        if config.get("enable_ssh"):
            ssh_config = config.get("ssh", {})
            port = ssh_config.get("port", 22)
            timeout = ssh_config.get("timeout", 60)
            attempts = ssh_config.get("max_auth_attempts", 5)
            version = ssh_config.get("version", "2")
            
            lines.append(f"\n# SSH服务器配置")
            lines.append(f"ssh server enable")
            lines.append(f"ssh server port {port}")
            lines.append(f"ssh server timeout {timeout}")
            lines.append(f"ssh server authentication-timeout {timeout}")
            lines.append(f"ssh server max-auth-times {attempts}")
            lines.append(f"ssh server compatible-ssh1-{version} disable")
            
            if config.get("ssh_user"):
                user = config["ssh_user"]
                username = user.get("username", "admin")
                password = user.get("password", "")
                user_type = user.get("type", "password")
                
                lines.append(f"\nlocal-user {username}")
                lines.append(f" password simple {password}")
                lines.append(f" service-type ssh")
                lines.append(" authorization-attribute level 3")
                lines.append(" quit")
        
        if config.get("enable_telnet"):
            lines.append(f"\n# Telnet服务器配置")
            lines.append(f"telnet server enable")
            lines.append("")
            lines.append("user-interface vty 0 4")
            lines.append(" authentication-mode scheme")
            lines.append(" protocol inbound all")
            lines.append(" quit")
        
        if config.get("user"):
            user = config["user"]
            username = user.get("username", "admin")
            password = user.get("password", "")
            level = user.get("level", 3)
            service = user.get("service", ["ssh", "telnet"])
            
            lines.append(f"\n# 用户管理")
            lines.append(f"local-user {username}")
            lines.append(f" password simple {password}")
            lines.append(f" authorization-attribute level {level}")
            service_str = " ".join(service)
            lines.append(f" service-type {service_str}")
            lines.append(" quit")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_vlan_config(config: Dict[str, Any]) -> str:
        """
        生成VLAN配置
        
        Args:
            config: VLAN配置字典
                - vlans: VLAN列表
                - vlanifs: VLAN接口列表
                - stp: STP配置
                
        Returns:
            配置字符串
        """
        lines = []
        lines.append("\n# ==================== VLAN配置 ====================")
        lines.append("#\n# VLAN及接口配置\n#")
        
        if config.get("vlans"):
            lines.append("\n# 批量创建VLAN")
            vlan_ids = []
            for vlan in config["vlans"]:
                vlan_id = vlan.get("id")
                vlan_name = vlan.get("name", "")
                if vlan_id:
                    if vlan_name:
                        lines.append(f"vlan {vlan_id}")
                        lines.append(f" name {vlan_name}")
                        lines.append(" quit")
                    else:
                        vlan_ids.append(str(vlan_id))
            
            if vlan_ids:
                lines.append(f"vlan {','.join(vlan_ids)}")
                lines.append(" quit")
        
        if config.get("interfaces"):
            lines.append("\n# 接口VLAN配置")
            for intf in config["interfaces"]:
                interface = intf.get("interface", "")
                link_type = intf.get("link_type", "access")
                
                if not interface:
                    continue
                
                lines.append(f"\ninterface {interface}")
                
                if link_type == "access":
                    vlan_id = intf.get("vlan_id", 1)
                    lines.append(f" port link-type access")
                    lines.append(f" port access vlan {vlan_id}")
                
                elif link_type == "trunk":
                    pvid = intf.get("pvid", 1)
                    trunk_vlans = intf.get("trunk_vlans", [])
                    lines.append(f" port link-type trunk")
                    lines.append(f" port trunk pvid vlan {pvid}")
                    if trunk_vlans:
                        vlan_str = ",".join(map(str, trunk_vlans))
                        lines.append(f" port trunk permit vlan {vlan_str}")
                
                elif link_type == "hybrid":
                    pvid = intf.get("pvid", 1)
                    untagged = intf.get("untagged_vlans", [])
                    tagged = intf.get("tagged_vlans", [])
                    lines.append(f" port link-type hybrid")
                    lines.append(f" port hybrid pvid vlan {pvid}")
                    if untagged:
                        lines.append(f" port hybrid vlan {','.join(map(str, untagged))} untagged")
                    if tagged:
                        lines.append(f" port hybrid vlan {','.join(map(str, tagged))} tagged")
                
                lines.append(" quit")
        
        if config.get("vlanifs"):
            lines.append("\n# VLAN接口配置")
            for vlanif in config["vlanifs"]:
                vlan_id = vlanif.get("vlan_id")
                ip = vlanif.get("ip_address", "")
                mask = vlanif.get("mask", "255.255.255.0")
                desc = vlanif.get("description", "")
                
                if vlan_id and ip:
                    lines.append(f"\ninterface Vlan-interface{vlan_id}")
                    if desc:
                        lines.append(f" description {desc}")
                    lines.append(f" ip address {ip} {mask}")
                    lines.append(" quit")
        
        if config.get("stp"):
            stp_config = config["stp"]
            if stp_config.get("enable"):
                lines.append("\n# STP配置")
                mode = stp_config.get("mode", "rstp")
                priority = stp_config.get("priority", 32768)
                
                lines.append(f"stp mode {mode}")
                lines.append(f"stp priority {priority}")
                lines.append("stp enable")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_routing_config(config: Dict[str, Any]) -> str:
        """
        生成路由配置
        
        Args:
            config: 路由配置字典
                - static: 静态路由列表
                - default: 默认路由
                - ospf: OSPF配置
                - bgp: BGP配置
                - rip: RIP配置
                
        Returns:
            配置字符串
        """
        lines = []
        lines.append("\n# ==================== 路由配置 ====================")
        lines.append("#\n# 路由协议配置\n#")
        
        if config.get("static"):
            lines.append("\n# 静态路由")
            for route in config["static"]:
                dest = route.get("destination", "")
                mask = route.get("mask", "")
                next_hop = route.get("next_hop", "")
                preference = route.get("preference", 60)
                
                if dest and next_hop:
                    lines.append(f"ip route-static {dest} {mask} {next_hop} preference {preference}")
        
        if config.get("default"):
            default = config["default"]
            next_hop = default.get("next_hop", "")
            preference = default.get("preference", 60)
            
            if next_hop:
                lines.append(f"\n# 默认路由")
                lines.append(f"ip route-static 0.0.0.0 0.0.0.0 {next_hop} preference {preference}")
        
        if config.get("ospf"):
            ospf = config["ospf"]
            process_id = ospf.get("process_id", 1)
            router_id = ospf.get("router_id", "")
            area_id = ospf.get("area_id", "0")
            networks = ospf.get("networks", [])
            
            lines.append(f"\n# OSPF配置")
            lines.append(f"ospf {process_id} router-id {router_id}")
            lines.append(f" area {area_id}")
            
            for net in networks:
                addr = net.get("address", "")
                mask = net.get("mask", "0.0.0.255")
                if addr:
                    lines.append(f"  network {addr} {mask}")
            
            lines.append("  quit")
            lines.append(" quit")
        
        if config.get("bgp"):
            bgp = config["bgp"]
            as_num = bgp.get("as_number", "")
            router_id = bgp.get("router_id", "")
            neighbors = bgp.get("neighbors", [])
            networks = bgp.get("networks", [])
            
            if as_num:
                lines.append(f"\n# BGP配置")
                lines.append(f"bgp {as_num}")
                if router_id:
                    lines.append(f" router-id {router_id}")
                
                for neighbor in neighbors:
                    ip = neighbor.get("ip", "")
                    remote_as = neighbor.get("remote_as", "")
                    if ip and remote_as:
                        lines.append(f" peer {ip} as-number {remote_as}")
                
                if networks:
                    lines.append(" #")
                    lines.append(" # 网络宣告")
                    for net in networks:
                        addr = net.get("address", "")
                        mask_len = net.get("mask_length", 24)
                        if addr:
                            lines.append(f" network {addr} {mask_len}")
                
                lines.append(" quit")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_security_config(config: Dict[str, Any]) -> str:
        """
        生成安全配置
        
        Args:
            config: 安全配置字典
                - acls: ACL列表
                - port_security: 端口安全配置
                - mac_binding: MAC绑定配置
                - arp_protection: ARP防护配置
                
        Returns:
            配置字符串
        """
        lines = []
        lines.append("\n# ==================== 安全配置 ====================")
        lines.append("#\n# 安全策略配置\n#")
        
        if config.get("acls"):
            lines.append("\n# ACL配置")
            for acl in config["acls"]:
                acl_num = acl.get("number", 2000)
                acl_type = "basic" if 2000 <= acl_num < 3000 else "advanced"
                rules = acl.get("rules", [])
                
                lines.append(f"\nacl number {acl_num}")
                
                for i, rule in enumerate(rules, 1):
                    action = rule.get("action", "permit")
                    src = rule.get("source", "")
                    dst = rule.get("destination", "")
                    sport = rule.get("source_port", "")
                    dport = rule.get("destination_port", "")
                    protocol = rule.get("protocol", "")
                    
                    rule_line = f" rule {i} {action}"
                    
                    if acl_type == "basic":
                        if src:
                            rule_line += f" source {src}"
                    else:  # advanced
                        if protocol:
                            rule_line += f" {protocol}"
                        if src:
                            rule_line += f" source {src}"
                        if dst:
                            rule_line += f" destination {dst}"
                        if dport:
                            rule_line += f" destination-port eq {dport}"
                    
                    lines.append(rule_line)
                
                lines.append(" quit")
        
        if config.get("port_security"):
            lines.append("\n# 端口安全配置")
            for psec in config["port_security"]:
                interface = psec.get("interface", "")
                max_mac = psec.get("max_mac", 1)
                violation = psec.get("violation", "shutdown")
                
                if interface:
                    lines.append(f"\ninterface {interface}")
                    lines.append(" port-security enable")
                    lines.append(f" port-security max-mac-count {max_mac}")
                    lines.append(f" port-security violation {violation}")
                    lines.append(" quit")
        
        if config.get("mac_binding"):
            lines.append("\n# MAC地址绑定")
            for bind in config["mac_binding"]:
                mac = bind.get("mac", "")
                interface = bind.get("interface", "")
                vlan = bind.get("vlan", 1)
                
                if mac and interface:
                    lines.append(f"mac-address static {mac} interface {interface} vlan {vlan}")
        
        if config.get("arp_protection"):
            arp = config["arp_protection"]
            if arp.get("enable"):
                lines.append("\n# ARP防护配置")
                lines.append("arp-check enable")
                
                if arp.get("static_entries"):
                    lines.append(" # 静态ARP条目")
                    for entry in arp["static_entries"]:
                        ip = entry.get("ip", "")
                        mac = entry.get("mac", "")
                        interface = entry.get("interface", "")
                        if ip and mac:
                            lines.append(f"arp static {ip} {mac} {interface}")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_interface_config(config: Dict[str, Any]) -> str:
        """
        生成接口配置
        
        Args:
            config: 接口配置字典
                - eth_trunks: Eth-Trunk配置
                - lldp: LLDP配置
                - rate_limit: 速率限制配置
                
        Returns:
            配置字符串
        """
        lines = []
        lines.append("\n# ==================== 接口配置 ====================")
        lines.append("#\n# 接口高级配置\n#")
        
        if config.get("eth_trunks"):
            lines.append("\n# 端口聚合配置")
            for trunk in config["eth_trunks"]:
                trunk_id = trunk.get("trunk_id", 1)
                mode = trunk.get("mode", "lacp-static")
                members = trunk.get("member_ports", [])
                link_type = trunk.get("port_link_type", "trunk")
                trunk_vlans = trunk.get("trunk_vlans", [])
                
                lines.append(f"\ninterface Bridge-Aggregation {trunk_id}")
                lines.append(f" link-aggregation mode {mode}")
                lines.append(f" port link-type {link_type}")
                
                if link_type == "trunk" and trunk_vlans:
                    vlan_str = ",".join(map(str, trunk_vlans))
                    lines.append(f" port trunk permit vlan {vlan_str}")
                
                lines.append(" quit")
                
                if members:
                    for member in members:
                        lines.append(f"\ninterface {member}")
                        lines.append(f" port link-aggregation group {trunk_id}")
                        lines.append(" quit")
        
        if config.get("lldp"):
            lldp = config["lldp"]
            if lldp.get("enable"):
                lines.append("\n# LLDP配置")
                lines.append("lldp global enable")
                mode = lldp.get("mode", "both")
                lines.append(f"lldp work {mode}")
        
        if config.get("rate_limit"):
            lines.append("\n# 接口速率限制")
            for rl in config["rate_limit"]:
                interface = rl.get("interface", "")
                cir = rl.get("cir", 1000)  # kbps
                cbs = rl.get("cbs", 125000)  # bytes
                
                if interface:
                    lines.append(f"\ninterface {interface}")
                    lines.append(f" qos lr outbound cir {cir} cbs {cbs}")
                    lines.append(" quit")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_service_config(config: Dict[str, Any]) -> str:
        """
        生服务配置
        
        Args:
            config: 服务配置字典
                - ntp: NTP配置
                - snmp: SNMP配置
                - log: 日志配置
                
        Returns:
            配置字符串
        """
        lines = []
        lines.append("\n# ==================== 服务配置 ====================")
        lines.append("#\n# 系统服务配置\n#")
        
        if config.get("ntp"):
            ntp = config["ntp"]
            servers = ntp.get("servers", [])
            timezone = ntp.get("timezone", "UTC+8")
            
            lines.append("\n# NTP服务器配置")
            lines.append("ntp-service enable")
            lines.append(f"clock timezone {timezone}")
            
            for server in servers:
                ip = server.get("ip", "")
                prefer = server.get("prefer", False)
                if ip:
                    pref_str = " preference" if prefer else ""
                    lines.append(f"ntp-service unicast-server {ip}{pref_str}")
        
        if config.get("snmp"):
            snmp = config["snmp"]
            version = snmp.get("version", "v2c")
            
            lines.append("\n# SNMP配置")
            lines.append("snmp-agent")
            lines.append(f" snmp-agent sys-info version {version.replace('v', 'v').lower()}")
            
            if version == "v2c":
                community_read = snmp.get("community_read", "public")
                community_write = snmp.get("community_write", "")
                
                lines.append(f" snmp-agent community read {community_read}")
                if community_write:
                    lines.append(f" snmp-agent community write {community_write}")
            
            if snmp.get("trap_enable"):
                trap_host = snmp.get("trap_host", "")
                if trap_host:
                    lines.append(f" snmp-agent target-host trap address udp-domain {trap_host} params securityname {community_read} v2c")
        
        if config.get("log"):
            log = config["log"]
            host = log.get("host", "")
            level = log.get("log_level", "informational")
            
            if host:
                lines.append("\n# 日志配置")
                lines.append("info-center enable")
                lines.append("info-center loghost " + host)
                lines.append(f"info-center source default module default level {level}")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_all(config: Dict[str, Any]) -> str:
        """
        生成完整配置
        
        Args:
            config: 完整配置字典
                - basic: 基础配置
                - vlan: VLAN配置
                - routing: 路由配置
                - security: 安全配置
                - interface: 接口配置
                - service: 服务配置
                
        Returns:
            完整配置字符串
        """
        sections = []
        
        sections.append(H3CConfigGenerator.generate_header(
            config.get("description", "H3C Switch Configuration")
        ))
        
        if config.get("basic"):
            sections.append(H3CConfigGenerator.generate_basic_config(config["basic"]))
        
        if config.get("vlan"):
            sections.append(H3CConfigGenerator.generate_vlan_config(config["vlan"]))
        
        if config.get("routing"):
            sections.append(H3CConfigGenerator.generate_routing_config(config["routing"]))
        
        if config.get("security"):
            sections.append(H3CConfigGenerator.generate_security_config(config["security"]))
        
        if config.get("interface"):
            sections.append(H3CConfigGenerator.generate_interface_config(config["interface"]))
        
        if config.get("service"):
            sections.append(H3CConfigGenerator.generate_service_config(config["service"]))
        
        sections.append("\n\nreturn")
        
        return "\n".join(sections)
