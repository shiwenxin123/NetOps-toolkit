#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
迈普交换机配置生成器
"""


class MaipuBasicGenerator:
    """迈普基础配置生成器"""
    
    @staticmethod
    def generate_hostname(hostname):
        return f"hostname {hostname}"
    
    @staticmethod
    def generate_password(password, encrypted=False):
        if encrypted:
            return f"enable password 5 {password}"
        return f"enable password {password}"
    
    @staticmethod
    def generate_user(username, password, level=15, encrypted=False):
        lines = []
        priv_level = "15" if level >= 15 else str(level)
        if encrypted:
            lines.append(f"username {username} privilege {priv_level} password 5 {password}")
        else:
            lines.append(f"username {username} privilege {priv_level} password {password}")
        return "\n".join(lines)
    
    @staticmethod
    def generate_mgmt_interface(interface, ip, mask, gateway=None):
        lines = [
            f"interface {interface}",
            f" ip address {ip} {mask}",
            " no shutdown",
            "!"
        ]
        if gateway:
            lines.append(f"ip route 0.0.0.0 0.0.0.0 {gateway}")
            lines.append("!")
        return "\n".join(lines)
    
    @staticmethod
    def generate_ssh(ssh_version=2, port=22, timeout=60, max_auth=5):
        lines = [
            f"ip ssh version {ssh_version}",
            f"ip ssh port {port}",
            f"ip ssh timeout {timeout}",
            f"ip ssh authentication-retries {max_auth}",
            "crypto key generate rsa",
            "!",
            "line vty 0 15",
            " transport input ssh",
            " login local",
            "!"
        ]
        return "\n".join(lines)
    
    @staticmethod
    def generate_telnet():
        return """line vty 0 15
 transport input telnet
 login local
!"""
    
    @staticmethod
    def generate_ntp(servers, timezone="UTC+8"):
        lines = []
        for server in servers:
            prefer = "prefer" if server.get("prefer") else ""
            lines.append(f"ntp server {server['ip']} {prefer}")
        lines.append(f"clock timezone {timezone}")
        return "\n".join(lines)
    
    @staticmethod
    def generate_snmp(version="2c", community_read=None, community_write=None,
                     location=None, contact=None, trap_enable=False, trap_host=None):
        lines = [f"snmp-server version {version}"]
        
        if community_read:
            lines.append(f"snmp-server community {community_read} ro")
        if community_write:
            lines.append(f"snmp-server community {community_write} rw")
        if location:
            lines.append(f"snmp-server location {location}")
        if contact:
            lines.append(f"snmp-server contact {contact}")
        if trap_enable and trap_host:
            lines.append(f"snmp-server host {trap_host} traps")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_logging(host, level="informational"):
        return f"""logging host {host}
logging trap {level}
logging enable
!"""
    
    @staticmethod
    def generate_banner(motd=None, login=None):
        lines = []
        if motd:
            lines.append(f"banner motd ^\n{motd}\n^")
        if login:
            lines.append(f"banner login ^\n{login}\n^")
        return "\n".join(lines)
    
    @staticmethod
    def generate_dns(servers, domain=None):
        lines = []
        for server in servers:
            lines.append(f"ip name-server {server}")
        if domain:
            lines.append(f"ip domain-name {domain}")
        return "\n".join(lines)
    
    @staticmethod
    def generate_basic_all(config):
        lines = ["!", "# 迈普交换机基础配置", "!"]
        
        if "hostname" in config:
            lines.append(MaipuBasicGenerator.generate_hostname(config["hostname"]))
            lines.append("!")
        
        if "password" in config:
            pwd = config["password"]
            lines.append(MaipuBasicGenerator.generate_password(
                pwd["value"], pwd.get("encrypted", False)
            ))
            lines.append("!")
        
        if "user" in config:
            user = config["user"]
            lines.append(MaipuBasicGenerator.generate_user(
                user["username"], user["password"],
                user.get("level", 15), user.get("encrypted", False)
            ))
            lines.append("!")
        
        if "mgmt_interface" in config:
            mgmt = config["mgmt_interface"]
            lines.append(MaipuBasicGenerator.generate_mgmt_interface(
                mgmt["interface"], mgmt["ip_address"],
                mgmt["mask"], mgmt.get("gateway")
            ))
        
        if config.get("enable_ssh"):
            lines.append(MaipuBasicGenerator.generate_ssh(
                config.get("ssh_version", 2),
                config.get("ssh_port", 22),
                config.get("ssh_timeout", 60),
                config.get("ssh_max_auth_tries", 5)
            ))
        
        if config.get("enable_telnet"):
            lines.append(MaipuBasicGenerator.generate_telnet())
            lines.append("!")
        
        if "ntp" in config:
            lines.append(MaipuBasicGenerator.generate_ntp(
                config["ntp"]["servers"],
                config["ntp"].get("timezone", "UTC+8")
            ))
            lines.append("!")
        
        if "snmp" in config:
            snmp = config["snmp"]
            lines.append(MaipuBasicGenerator.generate_snmp(
                snmp.get("version", "2c"),
                snmp.get("community_read"),
                snmp.get("community_write"),
                snmp.get("sys_location"),
                snmp.get("sys_contact"),
                snmp.get("trap_enable", False),
                snmp.get("trap_host")
            ))
            lines.append("!")
        
        if "log" in config:
            log = config["log"]
            if log.get("host"):
                lines.append(MaipuBasicGenerator.generate_logging(
                    log["host"], log.get("log_level", "informational")
                ))
        
        if "banner" in config:
            banner = config["banner"]
            lines.append(MaipuBasicGenerator.generate_banner(
                banner.get("motd"), banner.get("login")
            ))
            lines.append("!")
        
        if "dns" in config:
            dns = config["dns"]
            lines.append(MaipuBasicGenerator.generate_dns(
                dns["servers"], dns.get("domain")
            ))
            lines.append("!")
        
        lines.append("end")
        return "\n".join(lines)


class MaipuVLANGenerator:
    """迈普VLAN配置生成器"""
    
    @staticmethod
    def generate_vlan(vlan_id, name=None):
        lines = [f"vlan {vlan_id}"]
        if name:
            lines.append(f" name {name}")
        lines.append("!")
        return "\n".join(lines)
    
    @staticmethod
    def generate_vlans(vlans):
        lines = []
        for vlan in vlans:
            lines.append(MaipuVLANGenerator.generate_vlan(
                vlan["id"], vlan.get("name")
            ))
        return "\n".join(lines)
    
    @staticmethod
    def generate_interface(interface, vlan_type, vlan_id, trunk_vlans=None, pvid=None):
        lines = [f"interface {interface}"]
        
        if vlan_type == "access":
            lines.append(" switchport mode access")
            lines.append(f" switchport access vlan {vlan_id}")
        elif vlan_type == "trunk":
            lines.append(" switchport mode trunk")
            if trunk_vlans:
                if trunk_vlans == "all":
                    lines.append(" switchport trunk allowed vlan all")
                else:
                    lines.append(f" switchport trunk allowed vlan {trunk_vlans}")
            if pvid:
                lines.append(f" switchport trunk native vlan {pvid}")
        elif vlan_type == "hybrid":
            lines.append(" switchport mode hybrid")
            lines.append(f" switchport hybrid vlan {vlan_id}")
        
        lines.append(" no shutdown")
        lines.append("!")
        return "\n".join(lines)
    
    @staticmethod
    def generate_vlanif(vlan_id, ip, mask, description=None):
        lines = [
            f"interface vlan {vlan_id}",
            f" ip address {ip} {mask}"
        ]
        if description:
            lines.append(f" description {description}")
        lines.append(" no shutdown")
        lines.append("!")
        return "\n".join(lines)
    
    @staticmethod
    def generate_stp(mode="rstp", priority=32768, enable=True):
        lines = []
        if enable:
            lines.append("spanning-tree enable")
            lines.append(f"spanning-tree mode {mode}")
            if priority != 32768:
                lines.append(f"spanning-tree priority {priority}")
        else:
            lines.append("no spanning-tree enable")
        lines.append("!")
        return "\n".join(lines)


class MaipuRoutingGenerator:
    """迈普路由配置生成器"""
    
    @staticmethod
    def generate_static_route(dest, mask, nexthop, preference=60):
        return f"ip route {dest} {mask} {nexthop} {preference}"
    
    @staticmethod
    def generate_static_routes(routes):
        lines = []
        for route in routes:
            lines.append(MaipuRoutingGenerator.generate_static_route(
                route["dest"], route["mask"],
                route["nexthop"], route.get("preference", 60)
            ))
        return "\n".join(lines)
    
    @staticmethod
    def generate_ospf(process_id, router_id, networks):
        lines = [
            f"router ospf {process_id}",
            f" router-id {router_id}"
        ]
        for net in networks:
            lines.append(f" network {net['network']} {net['wildcard']} area {net['area']}")
        lines.append("!")
        return "\n".join(lines)
    
    @staticmethod
    def generate_bgp(as_number, router_id, peers, networks):
        lines = [
            f"router bgp {as_number}",
            f" bgp router-id {router_id}"
        ]
        for peer in peers:
            lines.append(f" neighbor {peer['ip']} remote-as {peer['remote_as']}")
        for net in networks:
            lines.append(f" network {net}")
        lines.append("!")
        return "\n".join(lines)


class MaipuSecurityGenerator:
    """迈普安全配置生成器"""
    
    @staticmethod
    def generate_acl(number, rules, description=None):
        acl_type = "extended" if int(number) >= 100 else "standard"
        lines = [f"ip access-list {acl_type} {number}"]
        if description:
            lines.append(f" remark {description}")
        
        for rule in rules:
            action = rule.get("action", "permit")
            proto = rule.get("protocol", "ip")
            src = rule.get("source", "any")
            src_wc = rule.get("src_wildcard", "")
            dst = rule.get("dest", "any")
            dst_wc = rule.get("dst_wildcard", "")
            port = rule.get("port", "")
            
            line = f" {action} {proto}"
            
            if src != "any":
                line += f" {src}"
                if src_wc:
                    line += f" {src_wc}"
            else:
                line += " any"
            
            if dst != "any":
                line += f" {dst}"
                if dst_wc:
                    line += f" {dst_wc}"
            else:
                line += " any"
            
            if port and proto in ["tcp", "udp"]:
                line += f" eq {port}"
            
            lines.append(line)
        
        lines.append("!")
        return "\n".join(lines)
    
    @staticmethod
    def generate_port_security(interface, max_mac=1, violation="shutdown", sticky=False):
        lines = [
            f"interface {interface}",
            " switchport port-security",
            f" switchport port-security maximum {max_mac}",
            f" switchport port-security violation {violation}"
        ]
        if sticky:
            lines.append(" switchport port-security mac-address sticky")
        lines.append("!")
        return "\n".join(lines)
    
    @staticmethod
    def generate_traffic_filter(interface, acl_number, direction="in"):
        return f"""interface {interface}
 ip access-group {acl_number} {direction}
!"""


class MaipuInterfaceGenerator:
    """迈普接口配置生成器"""
    
    @staticmethod
    def generate_eth_trunk(trunk_id, mode="lacp", members=None, description=None):
        lines = [f"interface eth-trunk {trunk_id}"]
        if description:
            lines.append(f" description {description}")
        lines.append(f" port link-type {mode}")
        lines.append("!")
        
        if members:
            for member in members:
                lines.append(f"interface {member}")
                lines.append(f" eth-trunk {trunk_id}")
                lines.append("!")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_lldp(enable=True, mode="tx_rx", interval=30, holdtime=120):
        lines = []
        if enable:
            lines.append("lldp enable")
            lines.append(f"lldp timer {interval}")
            lines.append(f"lldp holdtime {holdtime}")
        else:
            lines.append("no lldp enable")
        lines.append("!")
        return "\n".join(lines)
    
    @staticmethod
    def generate_loop_detect(enable=True, interval=5, action="shutdown"):
        lines = []
        if enable:
            lines.append("loopback-detection enable")
            lines.append(f"loopback-detection interval {interval}")
            lines.append(f"loopback-detection action {action}")
        else:
            lines.append("no loopback-detection enable")
        lines.append("!")
        return "\n".join(lines)
    
    @staticmethod
    def generate_poe(interface=None, enable=True, priority="low", power=None):
        lines = []
        if interface:
            lines.append(f"interface {interface}")
            if enable:
                lines.append(" poe enable")
                if priority:
                    lines.append(f" poe priority {priority}")
                if power:
                    lines.append(f" poe max-power {power}")
            else:
                lines.append(" no poe enable")
            lines.append("!")
        else:
            if enable:
                lines.append("poe enable")
            else:
                lines.append("no poe enable")
        return "\n".join(lines)
    
    @staticmethod
    def generate_rate_limit(interface, rate_in=None, rate_out=None):
        lines = [f"interface {interface}"]
        if rate_in:
            lines.append(f" storm-control broadcast rate {rate_in}")
        if rate_out:
            lines.append(f" storm-control multicast rate {rate_out}")
        lines.append("!")
        return "\n".join(lines)
