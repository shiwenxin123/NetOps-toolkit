#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络工具集 - 路由跟踪工具 (修复版)
"""

import subprocess
import platform
import re
import socket
from typing import Dict, List, Optional


class TraceRoute:
    """路由跟踪工具"""
    
    @staticmethod
    def traceroute(host: str, max_hops: int = 30, timeout: int = 2) -> Dict:
        """
        路由跟踪
        
        Args:
            host: 目标主机
            max_hops: 最大跳数
            timeout: 超时时间(秒)
            
        Returns:
            路由跟踪结果
        """
        result = {
            "success": False,
            "host": host,
            "ip_address": "",
            "hops": [],
            "total_hops": 0,
            "reached_destination": False,
            "error": "",
            "raw_output": ""
        }
        
        try:
            try:
                result["ip_address"] = socket.gethostbyname(host)
            except socket.gaierror:
                result["error"] = "无法解析主机名"
                return result
            
            is_windows = platform.system().lower() == 'windows'
            
            if is_windows:
                output = TraceRoute._traceroute_windows(host, max_hops, timeout)
            else:
                output = TraceRoute._traceroute_linux(host, max_hops, timeout)
            
            result["raw_output"] = output
            
            if output:
                result["hops"] = TraceRoute._parse_traceroute_output(output)
            else:
                result["hops"] = TraceRoute._simple_traceroute(host, max_hops, timeout)
            
            result["total_hops"] = len(result["hops"])
            
            if result["hops"]:
                for hop in result["hops"]:
                    if hop.get("reached") or hop.get("ip") == result["ip_address"]:
                        result["reached_destination"] = True
                        result["success"] = True
                        break
                
                if not result["success"] and len(result["hops"]) > 0:
                    result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    @staticmethod
    def _traceroute_windows(host: str, max_hops: int, timeout: int) -> str:
        """Windows tracert命令"""
        cmd = [
            'tracert',
            '-h', str(max_hops),
            '-w', str(timeout * 1000),
            '-d',
            host
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            output_bytes, _ = process.communicate(timeout=max_hops * timeout * 3)
            return output_bytes.decode('gbk', errors='ignore')
        except subprocess.TimeoutExpired:
            return ""
        except Exception:
            return ""
    
    @staticmethod
    def _traceroute_linux(host: str, max_hops: int, timeout: int) -> str:
        """Linux traceroute命令"""
        for cmd_name in ['traceroute', 'tracepath']:
            try:
                cmd = [cmd_name, '-m', str(max_hops), '-w', str(timeout), host]
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                output, _ = process.communicate(timeout=max_hops * timeout * 3)
                return output.decode('utf-8', errors='ignore')
            except FileNotFoundError:
                continue
            except:
                continue
        
        return ""
    
    @staticmethod
    def _parse_traceroute_output(output: str) -> List[Dict]:
        """解析traceroute输出"""
        hops = []
        lines = output.split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            
            if 'trace complete' in line.lower() or '跟踪完成' in line:
                continue
            
            if 'over a maximum of' in line.lower() or '最大' in line:
                continue
            
            hop = TraceRoute._parse_hop_line(line)
            if hop and hop.get("hop_number", 0) > 0:
                hops.append(hop)
        
        return hops
    
    @staticmethod
    def _parse_hop_line(line: str) -> Optional[Dict]:
        """解析单行路由信息"""
        hop = {
            "hop_number": 0,
            "ip": "",
            "hostname": "",
            "rtt_times": [],
            "avg_rtt": 0.0,
            "timeout": False,
            "reached": False
        }
        
        line = line.strip()
        
        if not line:
            return None
        
        number_match = re.match(r'^\s*(\d+)', line)
        if not number_match:
            return None
        
        hop["hop_number"] = int(number_match.group(1))
        
        if '*' in line and not re.search(r'(\d+)\s*ms', line):
            hop["timeout"] = True
            return hop
        
        ip_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        ip_matches = re.findall(ip_pattern, line)
        
        if ip_matches:
            hop["ip"] = ip_matches[0]
        
        rtt_matches = re.findall(r'(\d+)\s*ms', line)
        if rtt_matches:
            hop["rtt_times"] = [float(t) for t in rtt_matches]
            if hop["rtt_times"]:
                hop["avg_rtt"] = sum(hop["rtt_times"]) / len(hop["rtt_times"])
        
        return hop
    
    @staticmethod
    def _simple_traceroute(host: str, max_hops: int, timeout: int) -> List[Dict]:
        """
        简单模拟traceroute - 使用ping的TTL
        """
        hops = []
        
        try:
            dest_ip = socket.gethostbyname(host)
            
            for ttl in range(1, min(max_hops + 1, 10)):
                hop = {
                    "hop_number": ttl,
                    "ip": "",
                    "hostname": "",
                    "rtt_times": [],
                    "avg_rtt": 0.0,
                    "timeout": False,
                    "reached": False
                }
                
                is_windows = platform.system().lower() == 'windows'
                
                if is_windows:
                    cmd = ['ping', '-n', '1', '-i', str(ttl), '-w', str(timeout * 1000), host]
                    encoding = 'gbk'
                else:
                    cmd = ['ping', '-c', '1', '-t', str(ttl), '-W', str(timeout), host]
                    encoding = 'utf-8'
                
                try:
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW if is_windows else 0
                    )
                    output, _ = process.communicate(timeout=timeout + 5)
                    output = output.decode(encoding, errors='ignore')
                    
                    ip_match = re.search(r'来自\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', output)
                    if not ip_match:
                        ip_match = re.search(r'From\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', output)
                    if not ip_match:
                        ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[：:]\s*时间', output)
                    if not ip_match:
                        ip_match = re.search(r'回复来自\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', output)
                    
                    if ip_match:
                        hop["ip"] = ip_match.group(1)
                    else:
                        hop["timeout"] = True
                    
                    time_match = re.search(r'时间[=：<]\s*(\d+)', output)
                    if not time_match:
                        time_match = re.search(r'time[=：<]\s*(\d+)', output)
                    if not time_match:
                        time_match = re.search(r'(\d+)\s*ms', output)
                    
                    if time_match:
                        rtt = float(time_match.group(1))
                        hop["rtt_times"] = [rtt]
                        hop["avg_rtt"] = rtt
                    
                    if "TTL expired" in output or "ttl expired" in output.lower():
                        pass
                    elif hop["ip"] == dest_ip or "无法到达" in output or "unreachable" in output.lower():
                        hop["reached"] = True
                        
                except:
                    hop["timeout"] = True
                
                hops.append(hop)
                
                if hop.get("reached") or hop.get("ip") == dest_ip:
                    break
                
        except Exception:
            pass
        
        return hops
    
    @staticmethod
    def trace_parallel(hosts: List[str], max_hops: int = 30, timeout: int = 2, max_workers: int = 5) -> List[Dict]:
        """
        并行路由跟踪多个主机
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_host = {
                executor.submit(TraceRoute.traceroute, host, max_hops, timeout): host 
                for host in hosts
            }
            
            for future in as_completed(future_to_host):
                try:
                    r = future.result()
                    results.append(r)
                except Exception as e:
                    host = future_to_host[future]
                    results.append({
                        "success": False,
                        "host": host,
                        "error": str(e)
                    })
        
        return results
