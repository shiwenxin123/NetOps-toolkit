#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
操作审计日志管理
"""

import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class AuditAction(Enum):
    """审计操作类型"""
    CONFIG_GENERATE = "配置生成"
    CONFIG_EXPORT = "配置导出"
    CONFIG_IMPORT = "配置导入"
    CONFIG_BACKUP = "配置备份"
    CONFIG_RESTORE = "配置恢复"
    CONFIG_DELETE = "配置删除"
    TEMPLATE_CREATE = "模板创建"
    TEMPLATE_APPLY = "模板应用"
    TEMPLATE_DELETE = "模板删除"
    SETTINGS_CHANGE = "设置修改"
    TOOL_USE = "工具使用"
    BATCH_OPERATION = "批量操作"
    DEVICE_SWITCH = "设备切换"
    LOGIN = "登录"
    LOGOUT = "登出"


class AuditLevel(Enum):
    """审计级别"""
    INFO = "信息"
    WARNING = "警告"
    ERROR = "错误"
    CRITICAL = "关键"


@dataclass
class AuditLog:
    """审计日志记录"""
    id: str
    timestamp: str
    action: str
    level: str
    user: str
    device_name: str
    device_type: str
    description: str
    details: Dict
    ip_address: str
    session_id: str
    result: str
    duration_ms: int


class AuditManager:
    """审计日志管理器"""
    
    def __init__(self, audit_dir: str = None):
        if audit_dir is None:
            audit_dir = os.path.join(os.path.dirname(__file__), "..", "audit")
        
        self.audit_dir = os.path.abspath(audit_dir)
        os.makedirs(self.audit_dir, exist_ok=True)
        
        self.current_log_file = os.path.join(
            self.audit_dir, 
            f"audit_{datetime.now().strftime('%Y%m')}.json"
        )
        self.logs: List[AuditLog] = []
        self._load_logs()
        
        self._current_user = "default_user"
        self._current_session = self._generate_session_id()
    
    def _generate_session_id(self) -> str:
        return hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:12]
    
    def _generate_id(self) -> str:
        return datetime.now().strftime("%Y%m%d%H%M%S%f")
    
    def _load_logs(self):
        if os.path.exists(self.current_log_file):
            try:
                with open(self.current_log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.logs = [AuditLog(**log) for log in data]
            except Exception:
                self.logs = []
    
    def _save_logs(self):
        try:
            with open(self.current_log_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(log) for log in self.logs], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存审计日志失败: {e}")
    
    def set_user(self, username: str):
        self._current_user = username
    
    def set_session(self, session_id: str):
        self._current_session = session_id
    
    def log(self, action: AuditAction, description: str, 
            level: AuditLevel = AuditLevel.INFO,
            device_name: str = "", device_type: str = "",
            details: Dict = None, result: str = "成功",
            duration_ms: int = 0, ip_address: str = ""):
        """记录审计日志"""
        log_entry = AuditLog(
            id=self._generate_id(),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            action=action.value,
            level=level.value,
            user=self._current_user,
            device_name=device_name,
            device_type=device_type,
            description=description,
            details=details or {},
            ip_address=ip_address,
            session_id=self._current_session,
            result=result,
            duration_ms=duration_ms
        )
        
        self.logs.append(log_entry)
        self._save_logs()
    
    def log_config_generate(self, device_type: str, device_name: str = "", 
                           config_type: str = "", result: str = "成功"):
        self.log(
            AuditAction.CONFIG_GENERATE,
            f"生成{device_type}配置: {config_type}",
            device_name=device_name,
            device_type=device_type,
            details={"config_type": config_type},
            result=result
        )
    
    def log_config_export(self, device_type: str, file_path: str, 
                          config_size: int = 0, result: str = "成功"):
        self.log(
            AuditAction.CONFIG_EXPORT,
            f"导出配置到: {file_path}",
            device_type=device_type,
            details={"file_path": file_path, "config_size": config_size},
            result=result
        )
    
    def log_backup(self, device_name: str, device_type: str, 
                   backup_id: str, result: str = "成功"):
        self.log(
            AuditAction.CONFIG_BACKUP,
            f"创建配置备份: {backup_id}",
            device_name=device_name,
            device_type=device_type,
            details={"backup_id": backup_id},
            result=result
        )
    
    def log_template_apply(self, template_name: str, device_type: str, 
                          result: str = "成功"):
        self.log(
            AuditAction.TEMPLATE_APPLY,
            f"应用模板: {template_name}",
            device_type=device_type,
            details={"template_name": template_name},
            result=result
        )
    
    def log_tool_use(self, tool_name: str, duration_ms: int = 0, 
                    result: str = "成功"):
        self.log(
            AuditAction.TOOL_USE,
            f"使用工具: {tool_name}",
            details={"tool_name": tool_name},
            duration_ms=duration_ms,
            result=result
        )
    
    def get_logs(self, start_date: str = None, end_date: str = None,
                action: str = None, level: str = None,
                device_type: str = None, user: str = None) -> List[AuditLog]:
        """查询审计日志"""
        results = self.logs.copy()
        
        if start_date:
            results = [l for l in results if l.timestamp >= start_date]
        if end_date:
            results = [l for l in results if l.timestamp <= end_date]
        if action:
            results = [l for l in results if l.action == action]
        if level:
            results = [l for l in results if l.level == level]
        if device_type:
            results = [l for l in results if l.device_type == device_type]
        if user:
            results = [l for l in results if l.user == user]
        
        return sorted(results, key=lambda x: x.timestamp, reverse=True)
    
    def get_statistics(self, days: int = 30) -> Dict:
        """获取审计统计信息"""
        cutoff = datetime.now().strftime("%Y-%m-%d")
        recent_logs = [l for l in self.logs if l.timestamp >= cutoff]
        
        action_counts = {}
        level_counts = {}
        device_type_counts = {}
        user_counts = {}
        
        for log in recent_logs:
            action_counts[log.action] = action_counts.get(log.action, 0) + 1
            level_counts[log.level] = level_counts.get(log.level, 0) + 1
            device_type_counts[log.device_type] = device_type_counts.get(log.device_type, 0) + 1
            user_counts[log.user] = user_counts.get(log.user, 0) + 1
        
        success_rate = 0
        if recent_logs:
            success_count = sum(1 for l in recent_logs if l.result == "成功")
            success_rate = round(success_count / len(recent_logs) * 100, 1)
        
        return {
            "total_count": len(self.logs),
            "recent_count": len(recent_logs),
            "action_counts": action_counts,
            "level_counts": level_counts,
            "device_type_counts": device_type_counts,
            "user_counts": user_counts,
            "success_rate": success_rate
        }
    
    def export_logs(self, export_path: str, format: str = "json",
                   start_date: str = None, end_date: str = None) -> bool:
        """导出审计日志"""
        logs = self.get_logs(start_date, end_date)
        
        try:
            if format == "json":
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump([asdict(l) for l in logs], f, ensure_ascii=False, indent=2)
            elif format == "csv":
                import csv
                with open(export_path, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "ID", "时间", "操作", "级别", "用户", 
                        "设备名称", "设备类型", "描述", "结果", "耗时(ms)"
                    ])
                    for log in logs:
                        writer.writerow([
                            log.id, log.timestamp, log.action, log.level,
                            log.user, log.device_name, log.device_type,
                            log.description, log.result, log.duration_ms
                        ])
            else:
                lines = []
                for log in logs:
                    lines.append(f"[{log.timestamp}] [{log.level}] {log.action} - {log.description} ({log.result})")
                with open(export_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join(lines))
            
            return True
        except Exception as e:
            print(f"导出审计日志失败: {e}")
            return False
    
    def cleanup_old_logs(self, days: int = 90) -> int:
        """清理过期日志"""
        cutoff = (datetime.now() - __import__('datetime').timedelta(days=days)).strftime("%Y-%m-%d")
        
        original_count = len(self.logs)
        self.logs = [l for l in self.logs if l.timestamp >= cutoff]
        self._save_logs()
        
        return original_count - len(self.logs)
