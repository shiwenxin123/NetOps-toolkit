#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置验证器
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    level: str
    message: str
    line_number: int
    suggestion: str


class ConfigValidator:
    """配置验证器"""
    
    def __init__(self, device_type: str = "huawei"):
        self.device_type = device_type
        self.errors: List[ValidationResult] = []
        self.warnings: List[ValidationResult] = []
        self.info: List[ValidationResult] = []
    
    def _reset(self):
        self.errors = []
        self.warnings = []
        self.info = []
    
    def validate(self, config: str) -> Tuple[bool, List[ValidationResult]]:
        """验证配置"""
        self._reset()
        lines = config.splitlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            if not line or line.startswith('#') or line.startswith('!'):
                continue
            
            self._check_syntax(line, i)
            self._check_security(line, i)
            self._check_best_practices(line, i)
        
        all_results = self.errors + self.warnings + self.info
        return len(self.errors) == 0, all_results
    
    def _check_syntax(self, line: str, line_num: int):
        """语法检查"""
        if 'sysname' in line or 'hostname' in line:
            match = re.search(r'(sysname|hostname)\s+(\S+)', line)
            if match:
                name = match.group(2)
                if len(name) > 30:
                    self.warnings.append(ValidationResult(
                        is_valid=True, level="warning",
                        message=f"主机名 '{name}' 超过30字符",
                        line_number=line_num,
                        suggestion="建议使用较短的主机名"
                    ))
        
        if 'ip address' in line.lower():
            ip_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            ips = re.findall(ip_pattern, line)
            for ip in ips:
                if not self._is_valid_ip(ip):
                    self.errors.append(ValidationResult(
                        is_valid=False, level="error",
                        message=f"无效的IP地址: {ip}",
                        line_number=line_num,
                        suggestion="请检查IP地址格式"
                    ))
        
        if 'vlan' in line.lower():
            match = re.search(r'vlan\s+(\d+)', line)
            if match:
                vlan_id = int(match.group(1))
                if vlan_id < 1 or vlan_id > 4094:
                    self.errors.append(ValidationResult(
                        is_valid=False, level="error",
                        message=f"无效的VLAN ID: {vlan_id}",
                        line_number=line_num,
                        suggestion="VLAN ID范围: 1-4094"
                    ))
    
    def _check_security(self, line: str, line_num: int):
        """安全检查"""
        if 'password' in line.lower():
            if 'simple' in line or 'cipher' not in line:
                self.warnings.append(ValidationResult(
                    is_valid=True, level="warning",
                    message="密码未加密存储",
                    line_number=line_num,
                    suggestion="建议使用cipher加密密码"
                ))
            
            if re.search(r'password\s+\d*\s*(admin|123456|password)', line, re.I):
                self.errors.append(ValidationResult(
                    is_valid=False, level="error",
                    message="使用弱密码",
                    line_number=line_num,
                    suggestion="请使用强密码（大小写字母+数字+特殊字符）"
                ))
        
        if 'telnet' in line.lower() and 'enable' in line.lower():
            self.warnings.append(ValidationResult(
                is_valid=True, level="warning",
                message="启用了Telnet不安全协议",
                line_number=line_num,
                suggestion="建议禁用Telnet，使用SSH"
            ))
        
        if 'ssh' in line.lower() and 'version 1' in line.lower():
            self.warnings.append(ValidationResult(
                is_valid=True, level="warning",
                message="使用SSHv1不安全版本",
                line_number=line_num,
                suggestion="建议使用SSHv2"
            ))
        
        if 'permit any any' in line.lower() or 'permit ip any any' in line.lower():
            self.warnings.append(ValidationResult(
                is_valid=True, level="warning",
                message="ACL规则过于宽松",
                line_number=line_num,
                suggestion="建议细化ACL规则"
            ))
    
    def _check_best_practices(self, line: str, line_num: int):
        """最佳实践检查"""
        if 'shutdown' not in line and 'interface' in line.lower():
            if 'description' not in line.lower():
                self.info.append(ValidationResult(
                    is_valid=True, level="info",
                    message="接口缺少描述",
                    line_number=line_num,
                    suggestion="建议为接口添加描述"
                ))
        
        if 'vlan 1' in line.lower() and 'name' in line.lower():
            self.info.append(ValidationResult(
                is_valid=True, level="info",
                message="使用VLAN 1",
                line_number=line_num,
                suggestion="建议将管理流量迁移到其他VLAN"
            ))
        
        if 'spanning-tree' not in line.lower() and 'stp' not in line.lower():
            pass
    
    def _is_valid_ip(self, ip: str) -> bool:
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                num = int(part)
                if num < 0 or num > 255:
                    return False
            return True
        except ValueError:
            return False
    
    def get_summary(self) -> Dict:
        """获取验证摘要"""
        return {
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "info_count": len(self.info),
            "is_valid": len(self.errors) == 0,
            "security_score": self._calculate_security_score()
        }
    
    def _calculate_security_score(self) -> int:
        """计算安全评分"""
        base_score = 100
        for err in self.errors:
            base_score -= 15
        for warn in self.warnings:
            base_score -= 5
        return max(0, min(100, base_score))


class BestPracticeChecker:
    """最佳实践检查器"""
    
    CHECKS = [
        {
            "id": "BP001",
            "name": "禁用Telnet",
            "description": "检查是否禁用了不安全的Telnet服务",
            "severity": "high"
        },
        {
            "id": "BP002", 
            "name": "SSH版本",
            "description": "检查SSH版本是否为v2",
            "severity": "medium"
        },
        {
            "id": "BP003",
            "name": "密码加密",
            "description": "检查密码是否加密存储",
            "severity": "high"
        },
        {
            "id": "BP004",
            "name": "接口描述",
            "description": "检查接口是否有描述",
            "severity": "low"
        },
        {
            "id": "BP005",
            "name": "默认VLAN",
            "description": "检查是否使用了VLAN 1",
            "severity": "medium"
        },
        {
            "id": "BP006",
            "name": "ACL规则",
            "description": "检查ACL规则是否合理",
            "severity": "medium"
        }
    ]
    
    def check(self, config: str) -> List[Dict]:
        """执行最佳实践检查"""
        results = []
        config_lower = config.lower()
        
        has_telnet = 'telnet' in config_lower and 'no telnet' not in config_lower
        results.append({
            "check_id": "BP001",
            "name": "禁用Telnet",
            "passed": not has_telnet,
            "severity": "high",
            "message": "Telnet服务已禁用" if not has_telnet else "建议禁用Telnet服务"
        })
        
        has_sshv2 = 'ssh version 2' in config_lower or 'sshv2' in config_lower
        has_ssh = 'ssh' in config_lower
        results.append({
            "check_id": "BP002",
            "name": "SSH版本",
            "passed": not has_ssh or has_sshv2,
            "severity": "medium",
            "message": "使用SSHv2" if has_sshv2 else "建议使用SSHv2"
        })
        
        has_cipher = 'cipher' in config_lower or 'encrypted' in config_lower
        has_password = 'password' in config_lower
        results.append({
            "check_id": "BP003",
            "name": "密码加密",
            "passed": not has_password or has_cipher,
            "severity": "high",
            "message": "密码已加密" if has_cipher else "建议使用加密密码"
        })
        
        desc_count = config_lower.count('description')
        interface_count = config_lower.count('interface')
        results.append({
            "check_id": "BP004",
            "name": "接口描述",
            "passed": interface_count == 0 or desc_count > 0,
            "severity": "low",
            "message": f"接口描述覆盖: {desc_count}/{interface_count}"
        })
        
        uses_vlan1 = 'vlan 1' in config_lower or 'vlan 1' in config
        results.append({
            "check_id": "BP005",
            "name": "默认VLAN",
            "passed": not uses_vlan1,
            "severity": "medium",
            "message": "未使用VLAN 1" if not uses_vlan1 else "建议避免使用VLAN 1"
        })
        
        has_permit_any = 'permit any any' in config_lower
        results.append({
            "check_id": "BP006",
            "name": "ACL规则",
            "passed": not has_permit_any,
            "severity": "medium",
            "message": "ACL规则安全" if not has_permit_any else "ACL规则过于宽松"
        })
        
        return results
