#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NetOps Toolkit - VLAN配置模块
"""


class VLANConfigGenerator:
    """VLAN配置生成器"""
    
    @staticmethod
    def generate_vlan_batch(vlan_ids: list) -> str:
        """批量生成VLAN"""
        if not vlan_ids:
            return ""
        
        sorted_vlans = sorted(vlan_ids)
        ranges = []
        start = sorted_vlans[0]
        end = sorted_vlans[0]
        
        for i in range(1, len(sorted_vlans)):
            if sorted_vlans[i] == end + 1:
                end = sorted_vlans[i]
            else:
                if start == end:
                    ranges.append(str(start))
                else:
                    ranges.append(f"{start} to {end}")
                start = sorted_vlans[i]
                end = sorted_vlans[i]
        
        if start == end:
            ranges.append(str(start))
        else:
            ranges.append(f"{start} to {end}")
        
        return f"vlan batch {' '.join(ranges)}\n"
    
    @staticmethod
    def generate_vlan_single(vlan_id: int, name: str = None, description: str = None) -> str:
        """生成单个VLAN配置"""
        config_lines = []
        config_lines.append(f"vlan {vlan_id}\n")
        if name:
            config_lines.append(f" name {name}\n")
        if description:
            config_lines.append(f" description {description}\n")
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_port_vlan(interface: str, 
                          vlan_type: str = "access",
                          vlan_id: int = None,
                          trunk_vlans: list = None,
                          pvid: int = None) -> str:
        """生成接口VLAN配置"""
        config_lines = []
        config_lines.append(f"interface {interface}\n")
        config_lines.append(f" port link-type {vlan_type}\n")
        
        if vlan_type == "access" and vlan_id:
            config_lines.append(f" port default vlan {vlan_id}\n")
        elif vlan_type == "trunk":
            if trunk_vlans:
                config_lines.append(f" port trunk allow-pass vlan {' '.join(map(str, trunk_vlans))}\n")
            if pvid:
                config_lines.append(f" port trunk pvid vlan {pvid}\n")
        elif vlan_type == "hybrid":
            if vlan_id:
                config_lines.append(f" port hybrid pvid vlan {vlan_id}\n")
            if trunk_vlans:
                config_lines.append(f" port hybrid untagged vlan {' '.join(map(str, trunk_vlans))}\n")
        
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_vlanif(vlan_id: int, 
                        ip_address: str,
                        mask: str = "255.255.255.0",
                        description: str = None) -> str:
        """生成VLANIF接口配置"""
        config_lines = []
        config_lines.append(f"interface Vlanif{vlan_id}\n")
        if description:
            config_lines.append(f" description {description}\n")
        config_lines.append(f" ip address {ip_address} {mask}\n")
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_voice_vlan(interface: str, 
                           vlan_id: int,
                           untagged: bool = True) -> str:
        """生成Voice VLAN配置"""
        config_lines = []
        config_lines.append(f"interface {interface}\n")
        config_lines.append(f" voice-vlan {vlan_id} {'untag' if untagged else 'tag'}\n")
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_stp_config(mode: str = "stp",
                            priority: int = 32768,
                            enable: bool = True) -> str:
        """生成STP配置"""
        config_lines = []
        config_lines.append("stp mode {mode}\n")
        config_lines.append(f"stp {'enable' if enable else 'disable'}\n")
        if priority != 32768:
            config_lines.append(f"stp priority {priority}\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_vlan_all(config: dict) -> str:
        """生成完整VLAN配置"""
        config_lines = ["#\n", "# VLAN配置\n", "#\n"]
        
        if "vlans" in config:
            vlan_ids = [v["id"] if isinstance(v, dict) else v for v in config["vlans"]]
            if len(vlan_ids) > 3:
                config_lines.append(VLANConfigGenerator.generate_vlan_batch(vlan_ids))
            else:
                for vlan in config["vlans"]:
                    if isinstance(vlan, dict):
                        config_lines.append(VLANConfigGenerator.generate_vlan_single(
                            vlan["id"],
                            vlan.get("name"),
                            vlan.get("description")
                        ))
                    else:
                        config_lines.append(VLANConfigGenerator.generate_vlan_single(vlan))
        
        if "interfaces" in config:
            config_lines.append("\n#\n# 接口VLAN配置\n#\n")
            for iface in config["interfaces"]:
                config_lines.append(VLANConfigGenerator.generate_port_vlan(
                    iface["interface"],
                    iface.get("type", "access"),
                    iface.get("vlan_id"),
                    iface.get("trunk_vlans"),
                    iface.get("pvid")
                ))
        
        if "vlanifs" in config:
            config_lines.append("\n#\n# VLANIF配置\n#\n")
            for vlanif in config["vlanifs"]:
                config_lines.append(VLANConfigGenerator.generate_vlanif(
                    vlanif["vlan_id"],
                    vlanif["ip_address"],
                    vlanif.get("mask", "255.255.255.0"),
                    vlanif.get("description")
                ))
        
        if "voice_vlans" in config:
            config_lines.append("\n#\n# Voice VLAN配置\n#\n")
            for voice in config["voice_vlans"]:
                config_lines.append(VLANConfigGenerator.generate_voice_vlan(
                    voice["interface"],
                    voice["vlan_id"],
                    voice.get("untagged", True)
                ))
        
        if "stp" in config:
            config_lines.append("\n#\n# STP配置\n#\n")
            config_lines.append(VLANConfigGenerator.generate_stp_config(
                config["stp"].get("mode", "stp"),
                config["stp"].get("priority", 32768),
                config["stp"].get("enable", True)
            ))
        
        return "".join(config_lines)
