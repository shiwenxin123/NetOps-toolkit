#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NetOps Toolkit - 接口配置模块
"""


class InterfaceConfigGenerator:
    """接口配置生成器"""
    
    @staticmethod
    def generate_eth_trunk(trunk_id: int,
                          mode: str = "lacp-static",
                          member_ports: list = None,
                          description: str = None,
                          port_link_type: str = "trunk",
                          trunk_vlans: list = None,
                          native_vlan: int = None) -> str:
        """生成Eth-Trunk端口聚合配置"""
        config_lines = []
        config_lines.append(f"interface Eth-Trunk{trunk_id}\n")
        
        if description:
            config_lines.append(f" description {description}\n")
        
        config_lines.append(f" port link-type {port_link_type}\n")
        
        if port_link_type == "trunk" and trunk_vlans:
            config_lines.append(f" port trunk allow-pass vlan {' '.join(map(str, trunk_vlans))}\n")
        
        if port_link_type == "access" and native_vlan:
            config_lines.append(f" port default vlan {native_vlan}\n")
        
        config_lines.append(f" mode {mode}\n")
        config_lines.append("#\n")
        
        if member_ports:
            for port in member_ports:
                config_lines.append(f"interface {port}\n")
                config_lines.append(f" eth-trunk {trunk_id}\n")
                config_lines.append("#\n")
        
        return "".join(config_lines)
    
    @staticmethod
    def generate_lacp_config(priority: int = 32768,
                             system_id: str = None,
                             fast_switchover: bool = True) -> str:
        """生成LACP全局配置"""
        config_lines = []
        config_lines.append("lacp priority {priority}\n")
        
        if system_id:
            config_lines.append(f"lacp system-id {system_id}\n")
        
        if fast_switchover:
            config_lines.append("lacp fast-switchover enable\n")
        
        return "".join(config_lines)
    
    @staticmethod
    def generate_lldp_config(enable: bool = True,
                             mode: str = "both",
                             interval: int = 30,
                             holdtime: int = 120,
                             fast_count: int = 4) -> str:
        """生成LLDP配置"""
        config_lines = []
        
        if not enable:
            config_lines.append("lldp disable\n")
            return "".join(config_lines)
        
        config_lines.append("lldp enable\n")
        config_lines.append(f"lldp mode {mode}\n")
        config_lines.append(f"lldp message-fasts count {fast_count}\n")
        
        config_lines.append("lldp transmit interval {interval}\n")
        config_lines.append(f"lldp transmit holdtime {holdtime}\n")
        
        return "".join(config_lines)
    
    @staticmethod
    def generate_lldp_interface(interface: str,
                                enable: bool = True,
                                admin_status: str = "txrx") -> str:
        """生成接口LLDP配置"""
        config_lines = []
        config_lines.append(f"interface {interface}\n")
        
        if enable:
            config_lines.append(" lldp enable\n")
            config_lines.append(f" lldp admin-status {admin_status}\n")
        else:
            config_lines.append(" lldp disable\n")
        
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_poe_config(enable: bool = True,
                           max_power: int = 74000,
                           legacy_enable: bool = False) -> str:
        """生成PoE全局配置"""
        config_lines = []
        
        if enable:
            config_lines.append("poe enable\n")
        else:
            config_lines.append("poe disable\n")
        
        config_lines.append(f"poe max-power {max_power}\n")
        
        if legacy_enable:
            config_lines.append("poe legacy enable\n")
        
        return "".join(config_lines)
    
    @staticmethod
    def generate_poe_interface(interface: str,
                              enable: bool = True,
                              mode: str = "auto",
                              priority: str = "low",
                              max_power: int = 15400) -> str:
        """生成接口PoE配置"""
        config_lines = []
        config_lines.append(f"interface {interface}\n")
        
        if enable:
            config_lines.append(" poe enable\n")
            config_lines.append(f" poe mode {mode}\n")
            config_lines.append(f" poe priority {priority}\n")
            config_lines.append(f" poe max-power {max_power}\n")
        else:
            config_lines.append(" poe disable\n")
        
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_port_isolation(enable: bool = True,
                                group_id: int = 1,
                                interfaces: list = None) -> str:
        """生成端口隔离配置"""
        config_lines = []
        
        if not enable or not interfaces:
            return ""
        
        for interface in interfaces:
            config_lines.append(f"interface {interface}\n")
            config_lines.append(f" port-isolate enable group {group_id}\n")
            config_lines.append("#\n")
        
        if config_lines:
            config_lines.insert(0, f"port-isolate mode all\n")
        
        return "".join(config_lines)
    
    @staticmethod
    def generate_interface_qos(interface: str,
                              car_inbound: int = None,
                              car_outbound: int = None,
                              priority: int = None) -> str:
        """生成接口QOS配置"""
        config_lines = []
        config_lines.append(f"interface {interface}\n")
        
        if car_inbound:
            config_lines.append(f" qos car inbound cir {car_inbound} cbs {car_inbound * 125}\n")
        
        if car_outbound:
            config_lines.append(f" qos car outbound cir {car_outbound} cbs {car_outbound * 125}\n")
        
        if priority is not None:
            config_lines.append(f" qos priority {priority}\n")
        
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_loopback_detection(enable: bool = True,
                                    interval: int = 5,
                                    action: str = "block",
                                    vlan_ids: list = None) -> str:
        """生成环路检测配置"""
        config_lines = []
        
        if not enable:
            return ""
        
        config_lines.append("loopback-detect enable\n")
        config_lines.append(f"loopback-detect interval {interval}\n")
        
        if vlan_ids:
            config_lines.append(f"loopback-detect vlan {' '.join(map(str, vlan_ids))}\n")
            config_lines.append(f"loopback-detect action {action}\n")
        
        return "".join(config_lines)
    
    @staticmethod
    def generate_rate_limit(interface: str,
                           cir_in: int = None,
                           cir_out: int = None) -> str:
        """生成接口速率限制配置"""
        config_lines = []
        config_lines.append(f"interface {interface}\n")
        
        if cir_in:
            config_lines.append(f" qos lr inbound cir {cir_in}\n")
        
        if cir_out:
            config_lines.append(f" qos lr outbound cir {cir_out}\n")
        
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_interface_all(config: dict) -> str:
        """生成完整接口配置"""
        config_lines = ["#\n", "# 接口配置\n", "#\n"]
        
        if "eth_trunks" in config:
            for trunk in config["eth_trunks"]:
                config_lines.append(InterfaceConfigGenerator.generate_eth_trunk(
                    trunk["trunk_id"],
                    trunk.get("mode", "lacp-static"),
                    trunk.get("member_ports"),
                    trunk.get("description"),
                    trunk.get("port_link_type", "trunk"),
                    trunk.get("trunk_vlans"),
                    trunk.get("native_vlan")
                ))
        
        if "lacp" in config:
            config_lines.append("\n#\n# LACP全局配置\n#\n")
            config_lines.append(InterfaceConfigGenerator.generate_lacp_config(
                config["lacp"].get("priority", 32768),
                config["lacp"].get("system_id"),
                config["lacp"].get("fast_switchover", True)
            ))
        
        if "lldp" in config:
            config_lines.append("\n#\n# LLDP配置\n#\n")
            lldp_conf = config["lldp"]
            config_lines.append(InterfaceConfigGenerator.generate_lldp_config(
                lldp_conf.get("enable", True),
                lldp_conf.get("mode", "both"),
                lldp_conf.get("interval", 30),
                lldp_conf.get("holdtime", 120),
                lldp_conf.get("fast_count", 4)
            ))
            
            if "interfaces" in lldp_conf:
                for iface in lldp_conf["interfaces"]:
                    config_lines.append(InterfaceConfigGenerator.generate_lldp_interface(
                        iface["interface"],
                        iface.get("enable", True),
                        iface.get("admin_status", "txrx")
                    ))
        
        if "poe" in config:
            config_lines.append("\n#\n# PoE全局配置\n#\n")
            poe_conf = config["poe"]
            config_lines.append(InterfaceConfigGenerator.generate_poe_config(
                poe_conf.get("enable", True),
                poe_conf.get("max_power", 74000),
                poe_conf.get("legacy_enable", False)
            ))
            
            if "interfaces" in poe_conf:
                for iface in poe_conf["interfaces"]:
                    config_lines.append(InterfaceConfigGenerator.generate_poe_interface(
                        iface["interface"],
                        iface.get("enable", True),
                        iface.get("mode", "auto"),
                        iface.get("priority", "low"),
                        iface.get("max_power", 15400)
                    ))
        
        if "port_isolation" in config:
            config_lines.append("\n#\n# 端口隔离配置\n#\n")
            config_lines.append(InterfaceConfigGenerator.generate_port_isolation(
                config["port_isolation"].get("enable", True),
                config["port_isolation"].get("group_id", 1),
                config["port_isolation"].get("interfaces")
            ))
        
        if "loopback_detection" in config:
            config_lines.append("\n#\n# 环路检测配置\n#\n")
            config_lines.append(InterfaceConfigGenerator.generate_loopback_detection(
                config["loopback_detection"].get("enable", True),
                config["loopback_detection"].get("interval", 5),
                config["loopback_detection"].get("action", "block"),
                config["loopback_detection"].get("vlan_ids")
            ))
        
        if "rate_limits" in config:
            config_lines.append("\n#\n# 接口限速配置\n#\n")
            for rate_limit in config["rate_limits"]:
                config_lines.append(InterfaceConfigGenerator.generate_rate_limit(
                    rate_limit["interface"],
                    rate_limit.get("cir_in"),
                    rate_limit.get("cir_out")
                ))
        
        return "".join(config_lines)
