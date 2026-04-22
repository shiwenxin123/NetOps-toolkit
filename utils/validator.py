#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NetOps Toolkit - 验证工具
"""

import re
from typing import Tuple


class ConfigValidator:
    """配置验证器"""
    
    @staticmethod
    def validate_ip_address(ip: str) -> Tuple[bool, str]:
        """验证IP地址格式"""
        if not ip or ip.strip() == "":
            return False, "IP地址不能为空"
        
        pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
        match = re.match(pattern, ip.strip())
        
        if not match:
            return False, "IP地址格式不正确"
        
        for i in range(1, 5):
            octet = int(match.group(i))
            if octet < 0 or octet > 255:
                return False, f"IP地址第{i}段超出范围（0-255）"
        
        return True, "IP地址格式正确"
    
    @staticmethod
    def validate_subnet_mask(mask: str) -> Tuple[bool, str]:
        """验证子网掩码"""
        if not mask or mask.strip() == "":
            return False, "子网掩码不能为空"
        
        valid_masks = [
            "255.255.255.255", "255.255.255.254", "255.255.255.252",
            "255.255.255.248", "255.255.255.240", "255.255.255.224",
            "255.255.255.192", "255.255.255.128", "255.255.255.0",
            "255.255.254.0", "255.255.252.0", "255.255.248.0",
            "255.255.240.0", "255.255.224.0", "255.255.192.0",
            "255.255.128.0", "255.255.0.0", "255.254.0.0",
            "255.252.0.0", "255.240.0.0", "255.224.0.0",
            "255.192.0.0", "255.128.0.0", "255.0.0.0",
            "254.0.0.0", "252.0.0.0", "248.0.0.0",
            "240.0.0.0", "224.0.0.0", "192.0.0.0",
            "128.0.0.0", "0.0.0.0"
        ]
        
        if mask.strip() not in valid_masks:
            return False, "子网掩码格式不正确或不是有效的连续掩码"
        
        return True, "子网掩码格式正确"
    
    @staticmethod
    def validate_vlan_id(vlan_id: int) -> Tuple[bool, str]:
        """验证VLAN ID"""
        if not isinstance(vlan_id, int):
            return False, "VLAN ID必须是整数"
        
        if vlan_id < 1 or vlan_id > 4094:
            return False, "VLAN ID必须在1-4094范围内"
        
        return True, "VLAN ID有效"
    
    @staticmethod
    def validate_vlan_name(name: str) -> Tuple[bool, str]:
        """验证VLAN名称"""
        if not name or name.strip() == "":
            return True, "VLAN名称为可选"
        
        if len(name) > 32:
            return False, "VLAN名称不能超过32个字符"
        
        if not re.match(r'^[\w\-]+$', name):
            return False, "VLAN名称只能包含字母、数字、下划线和连字符"
        
        return True, "VLAN名称有效"
    
    @staticmethod
    def validate_interface_name(interface: str) -> Tuple[bool, str]:
        """验证接口名称"""
        if not interface or interface.strip() == "":
            return False, "接口名称不能为空"
        
        patterns = [
            r'^GigabitEthernet\d+/\d+/\d+$',
            r'^XGigabitEthernet\d+/\d+/\d+$',
            r'^Ethernet\d+/\d+/\d+$',
            r'^Eth-Trunk\d+$',
            r'^Vlanif\d+$',
            r'^LoopBack\d+$',
            r'^GE\d+/\d+/\d+$',
            r'^XGE\d+/\d+/\d+$',
        ]
        
        for pattern in patterns:
            if re.match(pattern, interface.strip(), re.IGNORECASE):
                return True, "接口名称格式正确"
        
        return False, "接口名称格式不正确，例: GigabitEthernet0/0/1"
    
    @staticmethod
    def validate_mac_address(mac: str) -> Tuple[bool, str]:
        """验证MAC地址"""
        if not mac or mac.strip() == "":
            return False, "MAC地址不能为空"
        
        patterns = [
            r'^([0-9A-Fa-f]{4}-){2}[0-9A-Fa-f]{4}$',
            r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$',
            r'^([0-9A-Fa-f]{4}:){2}[0-9A-Fa-f]{4}$',
        ]
        
        for pattern in patterns:
            if re.match(pattern, mac.strip()):
                return True, "MAC地址格式正确"
        
        return False, "MAC地址格式不正确，例: 0001-0002-0003 或 00:01:02:03:04:05"
    
    @staticmethod
    def validate_hostname(hostname: str) -> Tuple[bool, str]:
        """验证主机名"""
        if not hostname or hostname.strip() == "":
            return False, "主机名不能为空"
        
        if len(hostname) > 64:
            return False, "主机名不能超过64个字符"
        
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9\-]*$', hostname):
            return False, "主机名必须以字母开头，只能包含字母、数字和连字符"
        
        return True, "主机名格式正确"
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """验证密码强度"""
        if not password or password.strip() == "":
            return False, "密码不能为空"
        
        if len(password) < 8:
            return False, "密码长度至少8位"
        
        if len(password) > 128:
            return False, "密码长度不能超过128位"
        
        has_lower = re.search(r'[a-z]', password)
        has_upper = re.search(r'[A-Z]', password)
        has_digit = re.search(r'\d', password)
        has_special = re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;/`~]', password)
        
        strength = sum([bool(has_lower), bool(has_upper), bool(has_digit), bool(has_special)])
        
        if strength < 3:
            return False, "密码强度不足，需包含大小写字母、数字和特殊字符中的至少3种"
        
        return True, "密码强度满足要求"
    
    @staticmethod
    def validate_port_number(port: int) -> Tuple[bool, str]:
        """验证端口号"""
        if not isinstance(port, int):
            return False, "端口号必须是整数"
        
        if port < 1 or port > 65535:
            return False, "端口号必须在1-65535范围内"
        
        return True, "端口号有效"
    
    @staticmethod
    def validate_as_number(as_num: int) -> Tuple[bool, str]:
        """验证AS号"""
        if not isinstance(as_num, int):
            return False, "AS号必须是整数"
        
        if as_num < 1 or as_num > 4294967295:
            return False, "AS号必须在1-4294967295范围内"
        
        return True, "AS号有效"
    
    @staticmethod
    def validate_wildcard_mask(wildcard: str) -> Tuple[bool, str]:
        """验证反掩码"""
        if not wildcard or wildcard.strip() == "":
            return False, "反掩码不能为空"
        
        is_valid, msg = ConfigValidator.validate_ip_address(wildcard)
        if not is_valid:
            return False, "反掩码格式不正确"
        
        parts = [int(x) for x in wildcard.split('.')]
        for i in range(3):
            if parts[i] < parts[i+1]:
                return False, "反掩码格式不正确（必须为连续的0和1）"
        
        return True, "反掩码格式正确"


def validate_and_show_errors(validator_func, value, field_name="字段"):
    """验证并返回错误信息"""
    is_valid, message = validator_func(value)
    if not is_valid:
        return f"{field_name}: {message}"
    return None
