#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NetOps Toolkit - 安全配置模块（增强版）
"""


class SecurityConfigGenerator:
    """安全配置生成器"""
    
    @staticmethod
    def generate_acl_std(number: int,
                        rules: list,
                        description: str = None) -> str:
        """生成标准ACL配置"""
        config_lines = []
        config_lines.append(f"acl number {number}\n")
        if description:
            config_lines.append(f" description {description}\n")
        
        for rule in rules:
            action = rule.get("action", "permit")
            source = rule.get("source")
            source_wildcard = rule.get("source_wildcard", "0.0.0.0")
            rule_id = rule.get("id")
            
            rule_str = f" rule {rule_id} {action} source"
            if source:
                rule_str += f" {source} {source_wildcard}"
            else:
                rule_str += " any"
            config_lines.append(rule_str + "\n")
        
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_acl_ext(number: int,
                        rules: list,
                        description: str = None) -> str:
        """生成扩展ACL配置"""
        config_lines = []
        config_lines.append(f"acl number {number}\n")
        if description:
            config_lines.append(f" description {description}\n")
        
        for rule in rules:
            action = rule.get("action", "permit")
            protocol = rule.get("protocol", "ip")
            source = rule.get("source", "any")
            src_wildcard = rule.get("source_wildcard")
            dest = rule.get("destination", "any")
            dst_wildcard = rule.get("destination_wildcard")
            dest_port = rule.get("dest_port")
            rule_id = rule.get("id")
            
            rule_str = f" rule {rule_id} {action} {protocol}"
            if source and source != "any":
                rule_str += f" source {source}"
                if src_wildcard:
                    rule_str += f" {src_wildcard}"
            else:
                rule_str += " source any"
            
            if dest and dest != "any":
                rule_str += f" destination {dest}"
                if dst_wildcard:
                    rule_str += f" {dst_wildcard}"
            else:
                rule_str += " destination any"
            
            if dest_port and protocol in ["tcp", "udp"]:
                rule_str += f" destination-port eq {dest_port}"
            
            config_lines.append(rule_str + "\n")
        
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_port_security(interface: str,
                              enable: bool = True,
                              max_mac: int = 1,
                              action: str = "protect",
                              sticky: bool = False) -> str:
        """生成端口安全配置"""
        config_lines = []
        config_lines.append(f"interface {interface}\n")
        
        if enable:
            config_lines.append(" port-security enable\n")
            config_lines.append(f" port-security max-mac-num {max_mac}\n")
            config_lines.append(f" port-security protect-action {action}\n")
            if sticky:
                config_lines.append(" port-security mac-address sticky\n")
        
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_mac_binding(interface: str,
                            mac_address: str,
                            vlan_id: int,
                            sticky: bool = True) -> str:
        """生成MAC地址绑定配置"""
        config_lines = []
        config_lines.append(f"interface {interface}\n")
        config_lines.append(f" port-security mac-address sticky {mac_address} vlan {vlan_id}\n")
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_mac_static(mac_address: str,
                           interface: str,
                           vlan_id: int) -> str:
        """生成静态MAC地址表配置"""
        return f"mac-address static {mac_address} {interface} vlan {vlan_id}\n"
    
    @staticmethod
    def generate_mac_blackhole(mac_address: str) -> str:
        """生成黑洞MAC地址配置"""
        return f"mac-address blackhole {mac_address}\n"
    
    @staticmethod
    def generate_mac_limit(vlan: int = None,
                          interface: str = None,
                          limit: int = 100,
                          action: str = "discard",
                          alarm: bool = True) -> str:
        """生成MAC地址学习限制配置"""
        config_lines = []
        
        if vlan:
            config_lines.append(f"mac-address limit maximum {limit} vlan {vlan} action {action}")
            if alarm:
                config_lines.append(" alarm enable")
            config_lines.append("\n")
        
        if interface:
            config_lines.append(f"interface {interface}\n")
            config_lines.append(f" mac-address limit maximum {limit} action {action}")
            if alarm:
                config_lines.append(" alarm enable")
            config_lines.append("\n")
            config_lines.append("#\n")
        
        return "".join(config_lines)
    
    @staticmethod
    def generate_8021x_global(enable: bool = True,
                             method: str = "chap",
                             reauth_period: int = 3600,
                             timer_tx_period: int = 30) -> str:
        """生成802.1X全局配置"""
        config_lines = []
        
        if enable:
            config_lines.append("dot1x enable\n")
        config_lines.append(f"dot1x authentication-method {method}\n")
        config_lines.append(f"dot1x reauthenticate period {reauth_period}\n")
        config_lines.append(f"dot1x timer tx-period {timer_tx_period}\n")
        
        return "".join(config_lines)
    
    @staticmethod
    def generate_8021x_interface(interface: str,
                                 enable: bool = True,
                                 port_method: str = "mac",
                                 max_users: int = 256,
                                 quiet_period: int = 60) -> str:
        """生成接口802.1X配置"""
        config_lines = []
        config_lines.append(f"interface {interface}\n")
        
        if enable:
            config_lines.append(" dot1x enable\n")
            config_lines.append(f" dot1x port-method {port_method}\n")
            config_lines.append(f" dot1x max-user {max_users}\n")
            config_lines.append(f" dot1x timer quiet-period {quiet_period}\n")
        
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_radius_server(server_name: str,
                               ip_address: str,
                               shared_key: str,
                               auth_port: int = 1812,
                               acct_port: int = 1813,
                               retransmit: int = 3,
                               timeout: int = 5) -> str:
        """生成RADIUS服务器配置"""
        config_lines = []
        config_lines.append(f"radius-server template {server_name}\n")
        config_lines.append(f" radius-server shared-key cipher {shared_key}\n")
        config_lines.append(f" radius-server authentication {ip_address} {auth_port}\n")
        config_lines.append(f" radius-server accounting {ip_address} {acct_port}\n")
        config_lines.append(f" radius-server retransmit {retransmit}\n")
        config_lines.append(f" radius-server timeout {timeout}\n")
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_aaa_authentication(scheme_name: str,
                                   auth_methods: list = None) -> str:
        """生成AAA认证方案配置"""
        config_lines = []
        config_lines.append("aaa\n")
        config_lines.append(f" authentication-scheme {scheme_name}\n")
        
        if auth_methods:
            for idx, method in enumerate(auth_methods):
                config_lines.append(f"  authentication-mode {method}\n")
        
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_aaa_domain(domain_name: str,
                           auth_scheme: str,
                           radius_server: str = None) -> str:
        """生成AAA域配置"""
        config_lines = []
        config_lines.append("aaa\n")
        config_lines.append(f" domain {domain_name}\n")
        config_lines.append(f"  authentication-scheme {auth_scheme}\n")
        if radius_server:
            config_lines.append(f"  radius-server {radius_server}\n")
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_dhcp_snooping(enable: bool = True,
                               trusted_ports: list = None,
                               vlan: int = None) -> str:
        """生成DHCP Snooping配置"""
        config_lines = []
        config_lines.append("dhcp snooping enable\n")
        
        if vlan:
            config_lines.append(f"dhcp snooping vlan {vlan}\n")
        
        if trusted_ports:
            for port in trusted_ports:
                config_lines.append(f"interface {port}\n")
                config_lines.append(" dhcp snooping trusted\n")
                config_lines.append("#\n")
        
        return "".join(config_lines)
    
    @staticmethod
    def generate_arp_inspection(vlans: list = None,
                               trusted_ports: list = None) -> str:
        """生成ARP防护配置"""
        config_lines = []
        
        if vlans:
            config_lines.append(f"arp inspection vlan {' '.join(map(str, vlans))}\n")
        
        if trusted_ports:
            for port in trusted_ports:
                config_lines.append(f"interface {port}\n")
                config_lines.append(" arp inspection trust\n")
                config_lines.append("#\n")
        
        return "".join(config_lines)
    
    @staticmethod
    def generate_arp_static(ip_address: str,
                           mac_address: str,
                           interface: str = None,
                           vlan_id: int = None) -> str:
        """生成静态ARP表配置"""
        config = f"arp static {ip_address} {mac_address}"
        if vlan_id:
            config += f" vid {vlan_id}"
        if interface:
            config += f" interface {interface}"
        return config + "\n"
    
    @staticmethod
    def generate_arp_limit(interface: str = None,
                          vlan: int = None,
                          limit: int = 100) -> str:
        """生成ARP学习限制配置"""
        config_lines = []
        
        if interface:
            config_lines.append(f"interface {interface}\n")
            config_lines.append(f" arp-limit maximum {limit}\n")
            config_lines.append("#\n")
        
        if vlan:
            config_lines.append(f"vlan {vlan}\n")
            config_lines.append(f" arp-limit maximum {limit}\n")
            config_lines.append("#\n")
        
        return "".join(config_lines)
    
    @staticmethod
    def generate_ipsg_config(enable: bool = True,
                            vlans: list = None,
                            trusted_ports: list = None) -> str:
        """生成IP源防护配置"""
        config_lines = []
        
        if vlans:
            config_lines.append(f"ip source check vlan {' '.join(map(str, vlans))}\n")
        
        if trusted_ports:
            for port in trusted_ports:
                config_lines.append(f"interface {port}\n")
                config_lines.append(" ip source check trust\n")
                config_lines.append("#\n")
        
        return "".join(config_lines)
    
    @staticmethod
    def generate_storm_control(interface: str,
                              broadcast: int = None,
                              multicast: int = None,
                              unicast: int = None,
                              action: str = "block") -> str:
        """生成风暴抑制配置"""
        config_lines = []
        config_lines.append(f"interface {interface}\n")
        
        if broadcast:
            config_lines.append(f" storm-control broadcast min-rate {broadcast}\n")
        if multicast:
            config_lines.append(f" storm-control multicast min-rate {multicast}\n")
        if unicast:
            config_lines.append(f" storm-control unicast min-rate {unicast}\n")
        
        config_lines.append(" storm-control action {action}\n")
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_anti_attack(enable: bool = True,
                            type: str = "all") -> str:
        """生成防攻击配置"""
        config_lines = []
        
        if not enable:
            return ""
        
        if type in ["all", "ip", "arp", "dhcp"]:
            config_lines.append(f"anti-attack {type} enable\n")
        
        if type in ["all", "ip"]:
            config_lines.append("anti-attack ip source-mismatch enable\n")
        
        return "".join(config_lines)
    
    @staticmethod
    def generate_traffic_filter(interface: str,
                               acl_number: int,
                               direction: str = "inbound") -> str:
        """生成流量过滤配置"""
        config_lines = []
        config_lines.append(f"interface {interface}\n")
        config_lines.append(f" traffic-filter {direction} acl {acl_number}\n")
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_user_bind(interface: str,
                          ip_address: str = None,
                          mac_address: str = None,
                          vlan_id: int = None) -> str:
        """生成用户静态绑定配置"""
        config_lines = []
        config_lines.append(f"interface {interface}\n")
        
        bind_config = " user-bind static"
        if ip_address:
            bind_config += f" ip {ip_address}"
        if mac_address:
            bind_config += f" mac {mac_address}"
        if vlan_id:
            bind_config += f" vlan {vlan_id}"
        
        config_lines.append(bind_config + "\n")
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_security_all(config: dict) -> str:
        """生成完整安全配置"""
        config_lines = ["#\n", "# 安全配置\n", "#\n"]
        
        if "acls" in config:
            for acl in config["acls"]:
                if acl.get("type") == "extended":
                    config_lines.append(SecurityConfigGenerator.generate_acl_ext(
                        acl["number"],
                        acl["rules"],
                        acl.get("description")
                    ))
                else:
                    config_lines.append(SecurityConfigGenerator.generate_acl_std(
                        acl["number"],
                        acl["rules"],
                        acl.get("description")
                    ))
        
        if "port_security" in config:
            config_lines.append("\n#\n# 端口安全配置\n#\n")
            for port_sec in config["port_security"]:
                config_lines.append(SecurityConfigGenerator.generate_port_security(
                    port_sec["interface"],
                    port_sec.get("enable", True),
                    port_sec.get("max_mac", 1),
                    port_sec.get("action", "protect"),
                    port_sec.get("sticky", False)
                ))
        
        if "mac_bindings" in config:
            config_lines.append("\n#\n# MAC地址绑定配置\n#\n")
            for binding in config["mac_bindings"]:
                config_lines.append(SecurityConfigGenerator.generate_mac_binding(
                    binding["interface"],
                    binding["mac_address"],
                    binding["vlan_id"],
                    binding.get("sticky", True)
                ))
        
        if "static_macs" in config:
            config_lines.append("\n#\n# 静态MAC地址配置\n#\n")
            for mac in config["static_macs"]:
                config_lines.append(SecurityConfigGenerator.generate_mac_static(
                    mac["mac_address"],
                    mac["interface"],
                    mac["vlan_id"]
                ))
        
        if "blackhole_macs" in config:
            config_lines.append("\n#\n# 黑洞MAC地址配置\n#\n")
            for mac in config["blackhole_macs"]:
                config_lines.append(SecurityConfigGenerator.generate_mac_blackhole(mac))
        
        if "mac_limits" in config:
            config_lines.append("\n#\n# MAC地址学习限制配置\n#\n")
            for limit in config["mac_limits"]:
                config_lines.append(SecurityConfigGenerator.generate_mac_limit(
                    limit.get("vlan"),
                    limit.get("interface"),
                    limit.get("limit", 100),
                    limit.get("action", "discard"),
                    limit.get("alarm", True)
                ))
        
        if "dot1x" in config:
            config_lines.append("\n#\n# 802.1X全局配置\n#\n")
            config_lines.append(SecurityConfigGenerator.generate_8021x_global(
                config["dot1x"].get("enable", True),
                config["dot1x"].get("method", "chap"),
                config["dot1x"].get("reauth_period", 3600),
                config["dot1x"].get("timer_tx_period", 30)
            ))
            
            if "interfaces" in config["dot1x"]:
                for iface in config["dot1x"]["interfaces"]:
                    config_lines.append(SecurityConfigGenerator.generate_8021x_interface(
                        iface["interface"],
                        iface.get("enable", True),
                        iface.get("port_method", "mac"),
                        iface.get("max_users", 256),
                        iface.get("quiet_period", 60)
                    ))
        
        if "radius" in config:
            config_lines.append("\n#\n# RADIUS服务器配置\n#\n")
            for server in config["radius"]:
                config_lines.append(SecurityConfigGenerator.generate_radius_server(
                    server["name"],
                    server["ip_address"],
                    server["shared_key"],
                    server.get("auth_port", 1812),
                    server.get("acct_port", 1813),
                    server.get("retransmit", 3),
                    server.get("timeout", 5)
                ))
        
        if "aaa_schemes" in config:
            config_lines.append("\n#\n# AAA认证方案配置\n#\n")
            for scheme in config["aaa_schemes"]:
                config_lines.append(SecurityConfigGenerator.generate_aaa_authentication(
                    scheme["name"],
                    scheme.get("methods")
                ))
        
        if "aaa_domains" in config:
            config_lines.append("\n#\n# AAA域配置\n#\n")
            for domain in config["aaa_domains"]:
                config_lines.append(SecurityConfigGenerator.generate_aaa_domain(
                    domain["name"],
                    domain["auth_scheme"],
                    domain.get("radius_server")
                ))
        
        if "traffic_filters" in config:
            config_lines.append("\n#\n# 流量过滤配置\n#\n")
            for tf in config["traffic_filters"]:
                config_lines.append(SecurityConfigGenerator.generate_traffic_filter(
                    tf["interface"],
                    tf["acl_number"],
                    tf.get("direction", "inbound")
                ))
        
        if "user_bindings" in config:
            config_lines.append("\n#\n# 用户静态绑定配置\n#\n")
            for ub in config["user_bindings"]:
                config_lines.append(SecurityConfigGenerator.generate_user_bind(
                    ub["interface"],
                    ub.get("ip_address"),
                    ub.get("mac_address"),
                    ub.get("vlan_id")
                ))
        
        if "dhcp_snooping" in config:
            config_lines.append("\n#\n# DHCP Snooping配置\n#\n")
            ds_conf = config["dhcp_snooping"]
            config_lines.append(SecurityConfigGenerator.generate_dhcp_snooping(
                ds_conf.get("enable", True),
                ds_conf.get("trusted_ports"),
                ds_conf.get("vlan")
            ))
        
        if "arp_inspection" in config:
            config_lines.append("\n#\n# ARP防护配置\n#\n")
            ai_conf = config["arp_inspection"]
            config_lines.append(SecurityConfigGenerator.generate_arp_inspection(
                ai_conf.get("vlans"),
                ai_conf.get("trusted_ports")
            ))
        
        if "static_arps" in config:
            config_lines.append("\n#\n# 静态ARP配置\n#\n")
            for arp in config["static_arps"]:
                config_lines.append(SecurityConfigGenerator.generate_arp_static(
                    arp["ip_address"],
                    arp["mac_address"],
                    arp.get("interface"),
                    arp.get("vlan_id")
                ))
        
        if "storm_controls" in config:
            config_lines.append("\n#\n# 风暴抑制配置\n#\n")
            for storm in config["storm_controls"]:
                config_lines.append(SecurityConfigGenerator.generate_storm_control(
                    storm["interface"],
                    storm.get("broadcast"),
                    storm.get("multicast"),
                    storm.get("unicast"),
                    storm.get("action", "block")
                ))
        
        if "anti_attack" in config:
            config_lines.append("\n#\n# 防攻击配置\n#\n")
            aa_conf = config["anti_attack"]
            config_lines.append(SecurityConfigGenerator.generate_anti_attack(
                aa_conf.get("enable", True),
                aa_conf.get("type", "all")
            ))
        
        if "ipsg" in config:
            config_lines.append("\n#\n# IP源防护配置\n#\n")
            ipsg_conf = config["ipsg"]
            config_lines.append(SecurityConfigGenerator.generate_ipsg_config(
                ipsg_conf.get("enable", True),
                ipsg_conf.get("vlans"),
                ipsg_conf.get("trusted_ports")
            ))
        
        return "".join(config_lines)
