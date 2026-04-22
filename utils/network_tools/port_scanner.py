#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络工具集 - 端口扫描工具 (修复版)
"""

import socket
import concurrent.futures
import errno
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class PortScanner:
    """端口扫描工具"""
    
    COMMON_PORTS = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        143: "IMAP",
        443: "HTTPS",
        445: "SMB",
        993: "IMAPS",
        995: "POP3S",
        1433: "MSSQL",
        1521: "Oracle",
        3306: "MySQL",
        3389: "RDP",
        5432: "PostgreSQL",
        5900: "VNC",
        6379: "Redis",
        8080: "HTTP-Alt",
        8443: "HTTPS-Alt",
        9000: "PHP-FPM",
        27017: "MongoDB"
    }
    
    @staticmethod
    def scan_port(host: str, port: int, timeout: float = 1.0) -> Dict:
        """
        扫描单个端口
        """
        result = {
            "port": port,
            "status": "closed",
            "service": PortScanner.COMMON_PORTS.get(port, "unknown"),
            "banner": "",
            "error": ""
        }
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            connection_result = sock.connect_ex((host, port))
            
            if connection_result == 0:
                result["status"] = "open"
                
                try:
                    banner = PortScanner._grab_banner(sock, host, port)
                    if banner:
                        result["banner"] = banner
                except:
                    pass
            
            sock.close()
            
        except socket.timeout:
            result["status"] = "filtered"
        except socket.error as e:
            if e.errno == errno.ECONNREFUSED:
                result["status"] = "closed"
            elif e.errno == errno.ETIMEDOUT:
                result["status"] = "filtered"
            else:
                result["status"] = "error"
                result["error"] = str(e)
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    @staticmethod
    def _grab_banner(sock: socket.socket, host: str, port: int, timeout: float = 2.0) -> str:
        """抓取服务Banner"""
        banner = ""
        
        try:
            sock.settimeout(timeout)
            
            if port in [21, 22, 23, 25, 110, 143]:
                pass
            elif port in [80, 8080, 443, 8443]:
                try:
                    sock.sendall(b"HEAD / HTTP/1.0\r\nHost: " + host.encode() + b"\r\n\r\n")
                except:
                    pass
            
            try:
                sock.settimeout(timeout)
                data = sock.recv(1024)
                if data:
                    banner = data.decode('utf-8', errors='ignore').strip()[:200]
            except:
                pass
                
        except:
            pass
        
        return banner
    
    @staticmethod
    def scan_ports(host: str, ports: List[int], timeout: float = 1.0, max_workers: int = 100, 
                   progress_callback=None) -> Dict:
        """
        扫描多个端口
        
        Args:
            host: 目标主机
            ports: 端口列表
            timeout: 超时时间
            max_workers: 最大并发数
            progress_callback: 进度回调函数 callback(current, total, open_count)
        """
        result = {
            "success": False,
            "host": host,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": "",
            "total_ports": len(ports),
            "open_ports": 0,
            "closed_ports": 0,
            "filtered_ports": 0,
            "ports": [],
            "error": ""
        }
        
        try:
            open_ports = []
            closed_count = 0
            filtered_count = 0
            completed = 0
            total = len(ports)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_port = {
                    executor.submit(PortScanner.scan_port, host, port, timeout): port 
                    for port in ports
                }
                
                for future in concurrent.futures.as_completed(future_to_port):
                    try:
                        port_result = future.result()
                        completed += 1
                        
                        if port_result["status"] == "open":
                            open_ports.append(port_result)
                        elif port_result["status"] == "filtered":
                            filtered_count += 1
                        elif port_result["status"] == "closed":
                            closed_count += 1
                        else:
                            closed_count += 1
                        
                        if progress_callback and completed % 100 == 0:
                            progress_callback(completed, total, len(open_ports))
                            
                    except Exception as e:
                        completed += 1
                        closed_count += 1
            
            open_ports.sort(key=lambda x: x["port"])
            
            result["ports"] = open_ports
            result["open_ports"] = len(open_ports)
            result["closed_ports"] = closed_count
            result["filtered_ports"] = filtered_count
            result["success"] = True
            
            if progress_callback:
                progress_callback(total, total, len(open_ports))
            
        except Exception as e:
            result["error"] = str(e)
        
        result["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return result
    
    @staticmethod
    def scan_common_ports(host: str, timeout: float = 1.0) -> Dict:
        """
        扫描常用端口
        """
        common_ports = list(PortScanner.COMMON_PORTS.keys())
        return PortScanner.scan_ports(host, common_ports, timeout)
    
    @staticmethod
    def scan_port_range(host: str, start_port: int, end_port: int, timeout: float = 0.5, 
                         max_workers: int = 200, progress_callback=None) -> Dict:
        """
        扫描端口范围
        """
        ports = list(range(start_port, end_port + 1))
        return PortScanner.scan_ports(host, ports, timeout, max_workers, progress_callback)
    
    @staticmethod
    def scan_full_range(host: str, timeout: float = 0.3, max_workers: int = 500, 
                         progress_callback=None) -> Dict:
        """
        扫描全端口 (1-65535)
        """
        return PortScanner.scan_port_range(host, 1, 65535, timeout, max_workers, progress_callback)
    
    @staticmethod
    def test_port(host: str, port: int, timeout: float = 2.0) -> Dict:
        """
        测试单个端口（供GUI调用）
        """
        result = {
            "host": host,
            "port": port,
            "status": "closed",
            "open": False,
            "service": PortScanner.COMMON_PORTS.get(port, "unknown"),
            "banner": ""
        }
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            conn_result = sock.connect_ex((host, port))
            
            if conn_result == 0:
                result["status"] = "open"
                result["open"] = True
                
                try:
                    banner = PortScanner._grab_banner(sock, host, port, timeout)
                    if banner:
                        result["banner"] = banner
                except:
                    pass
            
            sock.close()
            
        except socket.timeout:
            result["status"] = "filtered"
        except Exception as e:
            result["status"] = "error"
        
        return result
    
    @staticmethod
    def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
        """
        快速检查端口是否开放
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
    
    @staticmethod
    def tcp_connect_test(host: str, port: int, timeout: float = 5.0) -> Tuple[bool, str]:
        """
        TCP连接测试
        """
        try:
            start_time = datetime.now()
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            sock.connect((host, port))
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000
            
            sock.close()
            
            service = PortScanner.COMMON_PORTS.get(port, "unknown")
            
            return True, f"连接成功 (端口: {port}, 服务: {service}, 耗时: {duration:.2f}ms)"
            
        except socket.timeout:
            return False, f"连接超时 (端口: {port})"
        except ConnectionRefusedError:
            return False, f"连接被拒绝 (端口: {port})"
        except socket.gaierror:
            return False, "无法解析主机名"
        except OSError as e:
            if "No route to host" in str(e):
                return False, "无法到达目标主机"
            return False, f"连接失败: {str(e)}"
        except Exception as e:
            return False, f"连接失败: {str(e)}"
    
    @staticmethod
    def get_service_name(port: int) -> str:
        """获取端口对应的服务名称"""
        return PortScanner.COMMON_PORTS.get(port, "unknown")
