#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络工具集 - Ping测试工具 (修复版)
"""

import subprocess
import platform
import re
import socket
from typing import Dict, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed


class PingTool:
    """Ping测试工具"""
    
    @staticmethod
    def ping(host: str, count: int = 4, timeout: int = 2) -> Dict:
        """
        Ping指定主机
        
        Args:
            host: 目标主机IP或域名
            count: Ping次数
            timeout: 超时时间(秒)
            
        Returns:
            Ping结果字典
        """
        result = {
            "success": False,
            "host": host,
            "packets_sent": 0,
            "packets_received": 0,
            "packets_lost": 0,
            "loss_rate": 0.0,
            "min_time": 0.0,
            "max_time": 0.0,
            "avg_time": 0.0,
            "ip_address": "",
            "error": "",
            "raw_output": ""
        }
        
        try:
            try:
                result["ip_address"] = socket.gethostbyname(host)
            except:
                pass
        
        except:
            pass
        
        is_windows = platform.system().lower() == 'windows'
        
        if is_windows:
            cmd = ['ping', '-n', str(count), '-w', str(timeout * 1000), host]
            encoding = 'gbk'
        else:
            cmd = ['ping', '-c', str(count), '-W', str(timeout), host]
            encoding = 'utf-8'
        
        try:
            if is_windows:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            output_bytes, error_bytes = process.communicate(timeout=count * timeout + 10)
            output = output_bytes.decode(encoding, errors='ignore')
            error = error_bytes.decode(encoding, errors='ignore')
            
            result["raw_output"] = output
            
            if process.returncode != 0 and "could not find host" in output.lower():
                result["error"] = "无法解析主机名"
                return result
            
            ip_patterns = [
                r'\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]',
                r'from\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
                r'正在 Ping [^\s]+ \[?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]?',
                r'PING [^\s]+ \((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\)'
            ]
            
            for pattern in ip_patterns:
                ip_match = re.search(pattern, output)
                if ip_match:
                    result["ip_address"] = ip_match.group(1)
                    break
            
            if is_windows:
                stat_patterns = [
                    r'数据包[：:]\s*已发送\s*=\s*(\d+).*?已接收\s*=\s*(\d+).*?丢失\s*=\s*(\d+)',
                    r'Packets[：:]\s*Sent\s*=\s*(\d+).*?Received\s*=\s*(\d+).*?Lost\s*=\s*(\d+)',
                    r'已发送\s*=\s*(\d+).*?已接收\s*=\s*(\d+).*?丢失\s*=\s*(\d+)'
                ]
            else:
                stat_patterns = [
                    r'(\d+)\s+packets transmitted,\s*(\d+)\s+received',
                    r'(\d+)\s+packets transmitted,\s*(\d+)\s+packets received'
                ]
            
            for pattern in stat_patterns:
                stat_match = re.search(pattern, output, re.DOTALL | re.IGNORECASE)
                if stat_match:
                    result["packets_sent"] = int(stat_match.group(1))
                    result["packets_received"] = int(stat_match.group(2))
                    result["packets_lost"] = result["packets_sent"] - result["packets_received"]
                    result["loss_rate"] = (result["packets_lost"] / result["packets_sent"] * 100) if result["packets_sent"] > 0 else 0
                    break
            
            reply_count = len(re.findall(r'来自|Reply|来自|字节=|bytes from|time=', output, re.IGNORECASE))
            if reply_count > 0 and result["packets_received"] == 0:
                result["packets_sent"] = count
                result["packets_received"] = min(reply_count, count)
                result["packets_lost"] = count - result["packets_received"]
                result["loss_rate"] = (result["packets_lost"] / count * 100)
            
            if is_windows:
                time_patterns = [
                    r'最短\s*=\s*(\d+)ms.*?最长\s*=\s*(\d+)ms.*?平均\s*=\s*(\d+)ms',
                    r'Minimum\s*=\s*(\d+)ms.*?Maximum\s*=\s*(\d+)ms.*?Average\s*=\s*(\d+)ms',
                    r'平均\s*=\s*(\d+)ms'
                ]
            else:
                time_patterns = [
                    r'rtt min/avg/max/mdev\s*=\s*([\d.]+)/([\d.]+)/([\d.]+)',
                    r'min/avg/max/mdev\s*=\s*([\d.]+)/([\d.]+)/([\d.]+)'
                ]
            
            for pattern in time_patterns:
                time_match = re.search(pattern, output, re.DOTALL | re.IGNORECASE)
                if time_match:
                    groups = time_match.groups()
                    if len(groups) >= 3:
                        result["min_time"] = float(groups[0])
                        result["max_time"] = float(groups[2]) if len(groups) > 2 else float(groups[0])
                        result["avg_time"] = float(groups[1])
                    elif len(groups) == 1:
                        result["avg_time"] = float(groups[0])
                    break
            
            if result["avg_time"] == 0:
                time_values = re.findall(r'time[=:<]\s*(\d+)', output, re.IGNORECASE)
                if time_values:
                    times = [int(t) for t in time_values]
                    result["min_time"] = min(times)
                    result["max_time"] = max(times)
                    result["avg_time"] = sum(times) / len(times)
            
            result["success"] = result["packets_received"] > 0 or reply_count > 0
            
        except subprocess.TimeoutExpired:
            result["error"] = "Ping超时"
        except FileNotFoundError:
            result["error"] = "Ping命令未找到"
        except Exception as e:
            result["error"] = f"Ping失败: {str(e)}"
        
        return result
    
    @staticmethod
    def ping_list(hosts: List[str], count: int = 2, timeout: int = 2, max_workers: int = 10) -> List[Dict]:
        """
        批量Ping多个主机
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_host = {
                executor.submit(PingTool.ping, host, count, timeout): host 
                for host in hosts
            }
            
            for future in as_completed(future_to_host):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    host = future_to_host[future]
                    results.append({
                        "success": False,
                        "host": host,
                        "error": str(e)
                    })
        
        return results
    
    @staticmethod
    def ping_sweep(network: str, prefix: int, timeout: int = 1, max_workers: int = 50) -> List[Dict]:
        """
        Ping扫描网段
        """
        hosts = []
        
        try:
            ip_parts = network.split('.')
            base = '.'.join(ip_parts[:3]) + '.'
            
            if prefix == 24:
                for i in range(1, 255):
                    hosts.append(base + str(i))
            elif prefix == 16:
                for j in range(0, 256):
                    for i in range(1, 255):
                        hosts.append(f"{ip_parts[0]}.{ip_parts[1]}.{j}.{i}")
            else:
                for i in range(1, 255):
                    hosts.append(base + str(i))
        except:
            return []
        
        alive_hosts = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_host = {
                executor.submit(PingTool.ping, host, 1, timeout): host 
                for host in hosts
            }
            
            for future in as_completed(future_to_host):
                try:
                    result = future.result()
                    if result.get("success"):
                        alive_hosts.append(result)
                except:
                    pass
        
        return alive_hosts
