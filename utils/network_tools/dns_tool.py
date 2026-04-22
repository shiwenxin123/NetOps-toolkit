#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络工具集 - DNS查询和其他工具
"""

import socket
import subprocess
import platform
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class DNSTool:
    """DNS查询工具"""
    
    @staticmethod
    def lookup(domain: str, record_type: str = "A") -> Dict:
        """
        DNS查询
        
        Args:
            domain: 域名
            record_type: 记录类型 (A, AAAA, MX, NS, TXT, CNAME, SOA, PTR)
            
        Returns:
            查询结果
        """
        result = {
            "success": False,
            "domain": domain,
            "record_type": record_type.upper(),
            "records": [],
            "error": "",
            "query_time": ""
        }
        
        try:
            start_time = datetime.now()
            
            if record_type.upper() in ["A", "AAAA"]:
                try:
                    if record_type.upper() == "A":
                        answers = socket.getaddrinfo(domain, None, socket.AF_INET)
                    else:
                        answers = socket.getaddrinfo(domain, None, socket.AF_INET6)
                    
                    for answer in answers:
                        ip = answer[4][0]
                        if ip not in result["records"]:
                            result["records"].append(ip)
                    
                    result["success"] = True
                except socket.gaierror as e:
                    result["error"] = f"DNS查询失败: {str(e)}"
            
            elif record_type.upper() == "MX":
                output = DNSTool._nslookup(domain, "MX")
                if output:
                    mx_records = re.findall(r'mail exchanger\s*=\s*(\d+)\s+([^\s]+)', output, re.IGNORECASE)
                    for priority, server in mx_records:
                        result["records"].append({
                            "priority": int(priority),
                            "server": server.rstrip('.')
                        })
                    result["success"] = True
                else:
                    result["error"] = "未找到MX记录"
            
            elif record_type.upper() == "NS":
                output = DNSTool._nslookup(domain, "NS")
                if output:
                    ns_records = re.findall(r'nameserver\s*=\s*([^\s]+)', output, re.IGNORECASE)
                    for ns in ns_records:
                        result["records"].append(ns.rstrip('.'))
                    result["success"] = True
                else:
                    result["error"] = "未找到NS记录"
            
            elif record_type.upper() == "TXT":
                output = DNSTool._nslookup(domain, "TXT")
                if output:
                    txt_records = re.findall(r'text\s*=\s*"([^"]+)"', output, re.IGNORECASE)
                    for txt in txt_records:
                        result["records"].append(txt)
                    result["success"] = True
                else:
                    result["error"] = "未找到TXT记录"
            
            elif record_type.upper() == "CNAME":
                output = DNSTool._nslookup(domain, "CNAME")
                if output:
                    cname = re.search(r'canonical name\s*=\s*([^\s]+)', output, re.IGNORECASE)
                    if cname:
                        result["records"].append(cname.group(1).rstrip('.'))
                        result["success"] = True
                    else:
                        result["error"] = "未找到CNAME记录"
            
            else:
                output = DNSTool._nslookup(domain, record_type)
                if output:
                    result["records"] = [line.strip() for line in output.split('\n') if line.strip()]
                    result["success"] = True
            
            end_time = datetime.now()
            result["query_time"] = str(end_time - start_time)
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    @staticmethod
    def _nslookup(domain: str, record_type: str) -> Optional[str]:
        """执行nslookup命令"""
        try:
            cmd = ['nslookup', '-type=' + record_type, domain]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='gbk' if platform.system().lower() == 'windows' else 'utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system().lower() == 'windows' else 0
            )
            
            output, _ = process.communicate(timeout=10)
            return output
            
        except:
            return None
    
    @staticmethod
    def reverse_lookup(ip: str) -> Dict:
        """
        反向DNS查询 (IP转域名)
        
        Args:
            ip: IP地址
            
        Returns:
            查询结果
        """
        result = {
            "success": False,
            "ip": ip,
            "hostname": "",
            "aliases": [],
            "error": ""
        }
        
        try:
            hostname, aliases, _ = socket.gethostbyaddr(ip)
            result["hostname"] = hostname
            result["aliases"] = aliases
            result["success"] = True
            
        except socket.herror as e:
            result["error"] = "反向DNS查询失败"
        except socket.gaierror as e:
            result["error"] = "无效的IP地址"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    @staticmethod
    def lookup_all(domain: str) -> Dict:
        """
        查询所有常见记录类型
        
        Args:
            domain: 域名
            
        Returns:
            所有记录
        """
        result = {
            "domain": domain,
            "A": [],
            "AAAA": [],
            "MX": [],
            "NS": [],
            "TXT": [],
            "CNAME": "",
            "errors": []
        }
        
        for record_type in ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]:
            lookup_result = DNSTool.lookup(domain, record_type)
            if lookup_result["success"]:
                if record_type == "CNAME":
                    result[record_type] = lookup_result["records"][0] if lookup_result["records"] else ""
                else:
                    result[record_type] = lookup_result["records"]
            else:
                if lookup_result["error"]:
                    result["errors"].append(f"{record_type}: {lookup_result['error']}")
        
        return result


class WhoisTool:
    """Whois查询工具（简化版）"""
    
    @staticmethod
    def query(domain: str) -> Dict:
        """
        Whois查询
        
        Args:
            domain: 域名
            
        Returns:
            Whois信息
        """
        result = {
            "success": False,
            "domain": domain,
            "registrar": "",
            "creation_date": "",
            "expiration_date": "",
            "name_servers": [],
            "status": "",
            "raw_output": "",
            "error": ""
        }
        
        try:
            whois_servers = {
                ".com": "whois.verisign-grs.com",
                ".net": "whois.verisign-grs.com",
                ".org": "whois.pir.org",
                ".cn": "whois.cnnic.cn",
                ".io": "whois.nic.io",
                ".co": "whois.nic.co",
                ".xyz": "whois.nic.xyz",
            }
            
            whois_server = None
            for suffix, server in whois_servers.items():
                if domain.endswith(suffix):
                    whois_server = server
                    break
            
            if not whois_server:
                whois_server = "whois.iana.org"
            
            output = WhoisTool._whois_query(domain, whois_server)
            
            if output:
                result["raw_output"] = output
                result["success"] = True
                
                registrar_match = re.search(r'Registrar:\s*(.+)', output, re.IGNORECASE)
                if registrar_match:
                    result["registrar"] = registrar_match.group(1).strip()
                
                creation_match = re.search(r'Creation Date:\s*(.+)', output, re.IGNORECASE)
                if not creation_match:
                    creation_match = re.search(r'Registered:\s*(.+)', output, re.IGNORECASE)
                if creation_match:
                    result["creation_date"] = creation_match.group(1).strip()
                
                exp_match = re.search(r'(?:Expir|Expire)[a-z\s]*:\s*(.+)', output, re.IGNORECASE)
                if exp_match:
                    result["expiration_date"] = exp_match.group(1).strip()
                
                ns_matches = re.findall(r'Name Server:\s*(.+)', output, re.IGNORECASE)
                if ns_matches:
                    result["name_servers"] = [ns.strip().rstrip('.') for ns in ns_matches]
                
                status_match = re.search(r'Status:\s*(.+)', output, re.IGNORECASE)
                if status_match:
                    result["status"] = status_match.group(1).strip()
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    @staticmethod
    def _whois_query(domain: str, server: str, port: int = 43, timeout: int = 10) -> Optional[str]:
        """执行Whois查询"""
        import socket
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((server, port))
            
            sock.send((domain + "\r\n").encode())
            
            response = b""
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                response += data
            
            sock.close()
            return response.decode('utf-8', errors='ignore')
            
        except socket.timeout:
            return None
        except Exception as e:
            return None


class NetworkInfo:
    """网络信息工具"""
    
    @staticmethod
    def get_local_ip() -> str:
        """获取本机IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
    
    @staticmethod
    def get_hostname() -> str:
        """获取本机主机名"""
        return socket.gethostname()
    
    @staticmethod
    def get_public_ip(timeout: int = 5) -> Dict:
        """
        获取公网IP
        
        Args:
            timeout: 超时时间
            
        Returns:
            公网IP信息
        """
        result = {
            "success": False,
            "ip": "",
            "country": "",
            "city": "",
            "isp": "",
            "error": ""
        }
        
        try:
            import urllib.request
            
            ip_services = [
                "https://api.ipify.org?format=text",
                "https://icanhazip.com",
                "https://ifconfig.me/ip"
            ]
            
            for service in ip_services:
                try:
                    with urllib.request.urlopen(service, timeout=timeout) as response:
                        ip = response.read().decode().strip()
                        if ip:
                            result["ip"] = ip
                            result["success"] = True
                            break
                except:
                    continue
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    @staticmethod
    def get_network_interfaces() -> List[Dict]:
        """获取网络接口信息"""
        interfaces = []
        
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            interfaces.append({
                "name": "主网络接口",
                "ip": local_ip,
                "hostname": hostname
            })
            
            try:
                all_ips = socket.gethostbyname_ex(hostname)[2]
                for ip in all_ips:
                    if ip != local_ip:
                        interfaces.append({
                            "name": "其他接口",
                            "ip": ip,
                            "hostname": hostname
                        })
            except:
                pass
                
        except Exception as e:
            interfaces.append({
                "name": "错误",
                "ip": "",
                "error": str(e)
            })
        
        return interfaces


class IPAddressConverter:
    """IP地址转换工具"""
    
    @staticmethod
    def ip_to_decimal(ip: str) -> Dict:
        """IP地址转十进制"""
        try:
            parts = [int(x) for x in ip.split('.')]
            decimal = (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3]
            return {
                "success": True,
                "ip": ip,
                "decimal": decimal,
                "hex": hex(decimal),
                "binary": bin(decimal)
            }
        except Exception as e:
            return {
                "success": False,
                "ip": ip,
                "error": str(e)
            }
    
    @staticmethod
    def decimal_to_ip(decimal: int) -> Dict:
        """十进制转IP地址"""
        try:
            decimal = int(decimal)
            ip = f"{(decimal >> 24) & 255}.{(decimal >> 16) & 255}.{(decimal >> 8) & 255}.{decimal & 255}"
            return {
                "success": True,
                "decimal": decimal,
                "ip": ip,
                "hex": hex(decimal),
                "binary": bin(decimal)
            }
        except Exception as e:
            return {
                "success": False,
                "decimal": decimal,
                "error": str(e)
            }
    
    @staticmethod
    def ip_to_binary(ip: str) -> Dict:
        """IP地址转二进制"""
        try:
            parts = [int(x) for x in ip.split('.')]
            binary_parts = [bin(p)[2:].zfill(8) for p in parts]
            binary_str = ''.join(binary_parts)
            
            return {
                "success": True,
                "ip": ip,
                "binary": binary_str,
                "binary_dotted": '.'.join(binary_parts),
                "decimal": (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3]
            }
        except Exception as e:
            return {
                "success": False,
                "ip": ip,
                "error": str(e)
            }
    
    @staticmethod
    def hex_to_ip(hex_str: str) -> Dict:
        """十六进制转IP地址"""
        try:
            hex_str = hex_str.replace('0x', '').replace('0X', '')
            decimal = int(hex_str, 16)
            ip = f"{(decimal >> 24) & 255}.{(decimal >> 16) & 255}.{(decimal >> 8) & 255}.{decimal & 255}"
            
            return {
                "success": True,
                "hex": hex_str,
                "ip": ip,
                "decimal": decimal,
                "binary": bin(decimal)
            }
        except Exception as e:
            return {
                "success": False,
                "hex": hex_str,
                "error": str(e)
            }
