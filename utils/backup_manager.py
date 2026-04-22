#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置备份管理器
"""

import os
import json
import shutil
import hashlib
import zipfile
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import difflib


@dataclass
class BackupRecord:
    """备份记录"""
    id: str
    filename: str
    device_name: str
    device_type: str
    ip_address: str
    backup_time: str
    file_size: int
    md5_hash: str
    description: str
    is_auto: bool
    tags: List[str]


class ConfigBackupManager:
    """配置备份管理器"""
    
    def __init__(self, backup_dir: str = None):
        if backup_dir is None:
            backup_dir = os.path.join(os.path.dirname(__file__), "..", "backups")
        
        self.backup_dir = os.path.abspath(backup_dir)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        self.records_file = os.path.join(self.backup_dir, "backup_records.json")
        self.records: List[BackupRecord] = []
        self._load_records()
    
    def _load_records(self):
        if os.path.exists(self.records_file):
            try:
                with open(self.records_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.records = [BackupRecord(**r) for r in data]
            except Exception:
                self.records = []
    
    def _save_records(self):
        try:
            with open(self.records_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(r) for r in self.records], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存备份记录失败: {e}")
    
    def _calculate_md5(self, file_path: str) -> str:
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _generate_id(self) -> str:
        return datetime.now().strftime("%Y%m%d%H%M%S%f")
    
    def create_backup(self, config_content: str, device_name: str, device_type: str,
                     ip_address: str = "", description: str = "", 
                     is_auto: bool = False, tags: List[str] = None) -> Optional[str]:
        """创建配置备份"""
        try:
            backup_id = self._generate_id()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            filename = f"{device_type}_{device_name}_{timestamp}.cfg"
            filename = filename.replace(" ", "_").replace("/", "-")
            
            file_path = os.path.join(self.backup_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            file_size = os.path.getsize(file_path)
            md5_hash = self._calculate_md5(file_path)
            
            record = BackupRecord(
                id=backup_id,
                filename=filename,
                device_name=device_name,
                device_type=device_type,
                ip_address=ip_address,
                backup_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                file_size=file_size,
                md5_hash=md5_hash,
                description=description,
                is_auto=is_auto,
                tags=tags or []
            )
            
            self.records.append(record)
            self._save_records()
            
            return backup_id
        except Exception as e:
            print(f"创建备份失败: {e}")
            return None
    
    def restore_backup(self, backup_id: str) -> Optional[str]:
        """恢复配置备份"""
        record = self.get_backup_by_id(backup_id)
        if not record:
            return None
        
        file_path = os.path.join(self.backup_dir, record.filename)
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
    
    def delete_backup(self, backup_id: str) -> bool:
        """删除备份"""
        record = self.get_backup_by_id(backup_id)
        if not record:
            return False
        
        file_path = os.path.join(self.backup_dir, record.filename)
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            
            self.records = [r for r in self.records if r.id != backup_id]
            self._save_records()
            return True
        except Exception:
            return False
    
    def get_backup_by_id(self, backup_id: str) -> Optional[BackupRecord]:
        """根据ID获取备份记录"""
        for record in self.records:
            if record.id == backup_id:
                return record
        return None
    
    def get_backups_by_device(self, device_name: str, device_type: str = None) -> List[BackupRecord]:
        """获取设备的所有备份"""
        results = []
        for record in self.records:
            if record.device_name == device_name:
                if device_type is None or record.device_type == device_type:
                    results.append(record)
        return sorted(results, key=lambda x: x.backup_time, reverse=True)
    
    def get_all_backups(self, device_type: str = None, 
                       start_date: str = None, 
                       end_date: str = None) -> List[BackupRecord]:
        """获取所有备份（支持筛选）"""
        results = self.records.copy()
        
        if device_type:
            results = [r for r in results if r.device_type == device_type]
        
        if start_date:
            results = [r for r in results if r.backup_time >= start_date]
        
        if end_date:
            results = [r for r in results if r.backup_time <= end_date]
        
        return sorted(results, key=lambda x: x.backup_time, reverse=True)
    
    def compare_backups(self, backup_id1: str, backup_id2: str) -> Optional[Dict]:
        """比较两个备份的差异"""
        config1 = self.restore_backup(backup_id1)
        config2 = self.restore_backup(backup_id2)
        
        if not config1 or not config2:
            return None
        
        lines1 = config1.splitlines()
        lines2 = config2.splitlines()
        
        diff = list(difflib.unified_diff(
            lines1, lines2,
            fromfile=f"备份1 ({backup_id1})",
            tofile=f"备份2 ({backup_id2})",
            lineterm=""
        ))
        
        return {
            "backup1_id": backup_id1,
            "backup2_id": backup_id2,
            "diff": "\n".join(diff),
            "added": len([l for l in diff if l.startswith('+') and not l.startswith('+++')]),
            "removed": len([l for l in diff if l.startswith('-') and not l.startswith('---')]),
            "changed": sum(1 for l in diff if l.startswith('@@'))
        }
    
    def export_backups(self, backup_ids: List[str], export_path: str) -> bool:
        """导出备份到压缩包"""
        try:
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for backup_id in backup_ids:
                    record = self.get_backup_by_id(backup_id)
                    if record:
                        file_path = os.path.join(self.backup_dir, record.filename)
                        if os.path.exists(file_path):
                            zf.write(file_path, record.filename)
            
            return True
        except Exception as e:
            print(f"导出备份失败: {e}")
            return False
    
    def cleanup_old_backups(self, days: int = 30, keep_count: int = 10) -> int:
        """清理过期备份"""
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        to_delete = []
        device_backups = {}
        
        for record in self.records:
            key = (record.device_name, record.device_type)
            if key not in device_backups:
                device_backups[key] = []
            device_backups[key].append(record)
        
        for key, backups in device_backups.items():
            sorted_backups = sorted(backups, key=lambda x: x.backup_time, reverse=True)
            for i, record in enumerate(sorted_backups):
                backup_date = datetime.strptime(record.backup_time, "%Y-%m-%d %H:%M:%S")
                if i >= keep_count and backup_date < cutoff_date:
                    to_delete.append(record.id)
        
        for backup_id in to_delete:
            if self.delete_backup(backup_id):
                deleted_count += 1
        
        return deleted_count
    
    def get_backup_statistics(self) -> Dict:
        """获取备份统计信息"""
        total_count = len(self.records)
        total_size = sum(r.file_size for r in self.records)
        
        device_types = {}
        for record in self.records:
            dt = record.device_type
            device_types[dt] = device_types.get(dt, 0) + 1
        
        auto_count = sum(1 for r in self.records if r.is_auto)
        manual_count = total_count - auto_count
        
        return {
            "total_count": total_count,
            "total_size": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "device_types": device_types,
            "auto_count": auto_count,
            "manual_count": manual_count,
            "oldest_backup": min((r.backup_time for r in self.records), default=None),
            "newest_backup": max((r.backup_time for r in self.records), default=None)
        }
