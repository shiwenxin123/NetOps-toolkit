#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络工具集 - 子网计算器
"""

import re
from typing import Tuple, List, Dict, Optional


class SubnetCalculator:
    """子网计算器"""
    
    @staticmethod
    def ip_to_int(ip: str) -> int:
        """IP地址转整数"""
        parts = [int(x) for x in ip.split('.')]
        return (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3]
    
    @staticmethod
    def int_to_ip(num: int) -> str:
        """整数转IP地址"""
        return f"{(num >> 24) & 255}.{(num >> 16) & 255}.{(num >> 8) & 255}.{num & 255}"
    
    @staticmethod
    def mask_to_prefix(mask: str) -> int:
        """子网掩码转前缀长度"""
        valid_masks = {
            "0.0.0.0": 0, "128.0.0.0": 1, "192.0.0.0": 2, "224.0.0.0": 3,
            "240.0.0.0": 4, "248.0.0.0": 5, "252.0.0.0": 6, "254.0.0.0": 7,
            "255.0.0.0": 8, "255.128.0.0": 9, "255.192.0.0": 10, "255.224.0.0": 11,
            "255.240.0.0": 12, "255.248.0.0": 13, "255.252.0.0": 14, "255.254.0.0": 15,
            "255.255.0.0": 16, "255.255.128.0": 17, "255.255.192.0": 18, "255.255.224.0": 19,
            "255.255.240.0": 20, "255.255.248.0": 21, "255.255.252.0": 22, "255.255.254.0": 23,
            "255.255.255.0": 24, "255.255.255.128": 25, "255.255.255.192": 26, "255.255.255.224": 27,
            "255.255.255.240": 28, "255.255.255.248": 29, "255.255.255.252": 30, "255.255.255.254": 31,
            "255.255.255.255": 32
        }
        return valid_masks.get(mask, -1)
    
    @staticmethod
    def prefix_to_mask(prefix: int) -> str:
        """前缀长度转子网掩码"""
        if prefix < 0 or prefix > 32:
            return ""
        
        mask = (0xffffffff << (32 - prefix)) & 0xffffffff
        return f"{(mask >> 24) & 255}.{(mask >> 16) & 255}.{(mask >> 8) & 255}.{mask & 255}"
    
    @staticmethod
    def calculate(ip: str, mask_or_prefix: str) -> Dict[str, any]:
        """
        计算子网信息
        
        Args:
            ip: IP地址
            mask_or_prefix: 子网掩码或前缀长度 (如 "255.255.255.0" 或 "24")
            
        Returns:
            包含子网信息的字典
        """
        result = {
            "success": False,
            "error": "",
            "ip_address": ip,
            "subnet_mask": "",
            "prefix_length": 0,
            "network_address": "",
            "broadcast_address": "",
            "first_usable": "",
            "last_usable": "",
            "total_hosts": 0,
            "usable_hosts": 0,
            "wildcard_mask": "",
            "ip_class": "",
            "ip_type": "",
            "is_private": False,
            "binary_ip": "",
            "binary_mask": ""
        }
        
        ip_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
        if not re.match(ip_pattern, ip):
            result["error"] = "IP地址格式无效"
            return result
        
        for i in range(1, 5):
            if int(re.match(ip_pattern, ip).group(i)) > 255:
                result["error"] = "IP地址值超出范围"
                return result
        
        if mask_or_prefix.isdigit():
            prefix = int(mask_or_prefix)
            if prefix < 0 or prefix > 32:
                result["error"] = "前缀长度必须在0-32之间"
                return result
            mask = SubnetCalculator.prefix_to_mask(prefix)
        else:
            mask = mask_or_prefix
            prefix = SubnetCalculator.mask_to_prefix(mask)
            if prefix == -1:
                result["error"] = "无效的子网掩码"
                return result
        
        result["subnet_mask"] = mask
        result["prefix_length"] = prefix
        
        ip_int = SubnetCalculator.ip_to_int(ip)
        mask_int = SubnetCalculator.ip_to_int(mask)
        
        network_int = ip_int & mask_int
        wildcard_int = mask_int ^ 0xffffffff
        broadcast_int = network_int | wildcard_int
        
        result["network_address"] = SubnetCalculator.int_to_ip(network_int)
        result["broadcast_address"] = SubnetCalculator.int_to_ip(broadcast_int)
        result["wildcard_mask"] = SubnetCalculator.int_to_ip(wildcard_int)
        
        result["total_hosts"] = broadcast_int - network_int + 1
        result["usable_hosts"] = max(0, result["total_hosts"] - 2)
        
        if result["usable_hosts"] > 0:
            result["first_usable"] = SubnetCalculator.int_to_ip(network_int + 1)
            result["last_usable"] = SubnetCalculator.int_to_ip(broadcast_int - 1)
        
        first_octet = int(ip.split('.')[0])
        if first_octet < 128:
            result["ip_class"] = "A"
        elif first_octet < 192:
            result["ip_class"] = "B"
        elif first_octet < 224:
            result["ip_class"] = "C"
        elif first_octet < 240:
            result["ip_class"] = "D (组播)"
        else:
            result["ip_class"] = "E (保留)"
        
        if first_octet == 10:
            result["is_private"] = True
            result["ip_type"] = "私有地址 (A类)"
        elif first_octet == 172 and 16 <= int(ip.split('.')[1]) <= 31:
            result["is_private"] = True
            result["ip_type"] = "私有地址 (B类)"
        elif first_octet == 192 and int(ip.split('.')[1]) == 168:
            result["is_private"] = True
            result["ip_type"] = "私有地址 (C类)"
        elif first_octet == 127:
            result["ip_type"] = "环回地址"
        elif first_octet >= 224 and first_octet < 240:
            result["ip_type"] = "组播地址"
        elif first_octet >= 240:
            result["ip_type"] = "保留地址"
        elif first_octet == 0:
            result["ip_type"] = "网络地址"
        elif network_int == ip_int:
            result["ip_type"] = "网络地址"
        elif broadcast_int == ip_int:
            result["ip_type"] = "广播地址"
        else:
            result["ip_type"] = "公网地址"
        
        result["binary_ip"] = '.'.join([bin(int(x))[2:].zfill(8) for x in ip.split('.')])
        result["binary_mask"] = '.'.join([bin(int(x))[2:].zfill(8) for x in mask.split('.')])
        
        result["success"] = True
        return result
    
    @staticmethod
    def split_subnet(network: str, prefix: int, new_prefix: int) -> List[Dict]:
        """
        子网划分
        
        Args:
            network: 网络地址
            prefix: 原前缀长度
            new_prefix: 新前缀长度
            
        Returns:
            子网列表
        """
        if new_prefix <= prefix:
            return []
        
        subnets = []
        network_int = SubnetCalculator.ip_to_int(network)
        original_mask = SubnetCalculator.ip_to_int(SubnetCalculator.prefix_to_mask(prefix))
        
        if network_int != (network_int & original_mask):
            return []
        
        new_mask = SubnetCalculator.ip_to_int(SubnetCalculator.prefix_to_mask(new_prefix))
        subnet_size = (0xffffffff >> new_prefix) + 1
        
        num_subnets = 2 ** (new_prefix - prefix)
        
        for i in range(num_subnets):
            subnet_int = network_int + (i * subnet_size)
            broadcast_int = subnet_int | (0xffffffff >> new_prefix)
            
            subnets.append({
                "subnet": SubnetCalculator.int_to_ip(subnet_int),
                "prefix": new_prefix,
                "mask": SubnetCalculator.prefix_to_mask(new_prefix),
                "first_host": SubnetCalculator.int_to_ip(subnet_int + 1) if new_prefix < 31 else "",
                "last_host": SubnetCalculator.int_to_ip(broadcast_int - 1) if new_prefix < 31 else "",
                "broadcast": SubnetCalculator.int_to_ip(broadcast_int),
                "hosts": max(0, (subnet_size - 2))
            })
        
        return subnets
    
    @staticmethod
    def get_all_masks() -> List[Dict]:
        """获取所有有效子网掩码"""
        masks = []
        for prefix in range(33):
            mask = SubnetCalculator.prefix_to_mask(prefix)
            hosts = 2 ** (32 - prefix)
            usable = max(0, hosts - 2) if prefix < 31 else hosts
            
            masks.append({
                "prefix": prefix,
                "mask": mask,
                "total_hosts": hosts,
                "usable_hosts": usable,
                "notation": f"/{prefix}"
            })
        
        return masks
    
    @staticmethod
    def ip_range_to_cidr(start_ip: str, end_ip: str) -> List[Dict]:
        """
        IP范围转CIDR
        
        Args:
            start_ip: 起始IP
            end_ip: 结束IP
            
        Returns:
            CIDR块列表
        """
        cidrs = []
        start = SubnetCalculator.ip_to_int(start_ip)
        end = SubnetCalculator.ip_to_int(end_ip)
        
        if start > end:
            return cidrs
        
        while start <= end:
            max_size = 32
            
            while max_size > 0:
                mask = SubnetCalculator.ip_to_int(SubnetCalculator.prefix_to_mask(max_size))
                network = start & mask
                
                if network != start:
                    max_size -= 1
                    continue
                
                broadcast = network | (mask ^ 0xffffffff)
                
                if broadcast > end:
                    max_size -= 1
                    continue
                
                break
            
            cidrs.append({
                "network": SubnetCalculator.int_to_ip(start),
                "prefix": max_size,
                "cidr": f"{SubnetCalculator.int_to_ip(start)}/{max_size}",
                "mask": SubnetCalculator.prefix_to_mask(max_size),
                "broadcast": SubnetCalculator.int_to_ip(start | (SubnetCalculator.ip_to_int(SubnetCalculator.prefix_to_mask(max_size)) ^ 0xffffffff))
            })
            
            start = start + (2 ** (32 - max_size))
        
        return cidrs
