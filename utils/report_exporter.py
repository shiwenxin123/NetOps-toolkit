#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
报表导出器
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional

try:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


class ReportExporter:
    """报表导出器"""
    
    def __init__(self):
        self.app_name = "NetOps Toolkit"
        self.version = "v4.0"
        self.author = "Dimples"
    
    def _get_timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def export_to_txt(self, content: str, file_path: str, 
                     title: str = "配置报表") -> bool:
        """导出为文本文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"{'='*60}\n")
                f.write(f"{title}\n")
                f.write(f"生成时间: {self._get_timestamp()}\n")
                f.write(f"工具版本: {self.app_name} {self.version}\n")
                f.write(f"{'='*60}\n\n")
                f.write(content)
            return True
        except Exception as e:
            print(f"导出TXT失败: {e}")
            return False
    
    def export_to_json(self, data: Dict, file_path: str,
                      title: str = "配置报表") -> bool:
        """导出为JSON"""
        try:
            export_data = {
                "title": title,
                "generated_at": self._get_timestamp(),
                "tool": f"{self.app_name} {self.version}",
                "data": data
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"导出JSON失败: {e}")
            return False
    
    def export_config_report(self, config: str, device_type: str,
                            file_path: str, format: str = "txt",
                            metadata: Dict = None) -> bool:
        """导出配置报表"""
        if format == "txt":
            content = f"设备类型: {device_type}\n"
            if metadata:
                content += f"设备名称: {metadata.get('device_name', 'N/A')}\n"
                content += f"IP地址: {metadata.get('ip_address', 'N/A')}\n"
                content += f"描述: {metadata.get('description', 'N/A')}\n"
            content += f"\n{'-'*50}\n配置内容:\n{'-'*50}\n\n{config}"
            return self.export_to_txt(content, file_path, "交换机配置报表")
        
        elif format == "json":
            return self.export_to_json({
                "device_type": device_type,
                "config": config,
                "metadata": metadata or {}
            }, file_path, "交换机配置报表")
        
        return False
    
    def export_audit_report(self, logs: List[Dict], file_path: str,
                           format: str = "txt", stats: Dict = None) -> bool:
        """导出审计报表"""
        if format == "txt":
            content = "审计日志报表\n\n"
            
            if stats:
                content += "统计信息:\n"
                content += f"  总记录数: {stats.get('total_count', 0)}\n"
                content += f"  成功率: {stats.get('success_rate', 0)}%\n\n"
            
            content += "详细记录:\n"
            content += "-" * 80 + "\n"
            
            for log in logs:
                content += f"[{log.get('timestamp', '')}] "
                content += f"[{log.get('level', '')}] "
                content += f"{log.get('action', '')} - "
                content += f"{log.get('description', '')} "
                content += f"({log.get('result', '')})\n"
            
            return self.export_to_txt(content, file_path, "操作审计报表")
        
        elif format == "json":
            return self.export_to_json({
                "statistics": stats or {},
                "logs": logs
            }, file_path, "操作审计报表")
        
        elif format == "csv":
            try:
                import csv
                with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "时间", "级别", "操作", "用户", "设备", "描述", "结果"
                    ])
                    for log in logs:
                        writer.writerow([
                            log.get('timestamp', ''),
                            log.get('level', ''),
                            log.get('action', ''),
                            log.get('user', ''),
                            log.get('device_name', ''),
                            log.get('description', ''),
                            log.get('result', '')
                        ])
                return True
            except Exception as e:
                print(f"导出CSV失败: {e}")
                return False
        
        return False
    
    def export_backup_report(self, backups: List[Dict], file_path: str,
                            format: str = "txt", stats: Dict = None) -> bool:
        """导出备份报表"""
        if format == "txt":
            content = "配置备份报表\n\n"
            
            if stats:
                content += "统计信息:\n"
                content += f"  总备份数: {stats.get('total_count', 0)}\n"
                content += f"  总大小: {stats.get('total_size_mb', 0)} MB\n"
                content += f"  自动备份: {stats.get('auto_count', 0)}\n"
                content += f"  手动备份: {stats.get('manual_count', 0)}\n\n"
            
            content += "备份记录:\n"
            content += "-" * 80 + "\n"
            
            for backup in backups:
                content += f"ID: {backup.get('id', '')}\n"
                content += f"  设备: {backup.get('device_name', '')} ({backup.get('device_type', '')})\n"
                content += f"  时间: {backup.get('backup_time', '')}\n"
                content += f"  大小: {backup.get('file_size', 0)} bytes\n"
                content += f"  MD5: {backup.get('md5_hash', '')}\n"
                content += "\n"
            
            return self.export_to_txt(content, file_path, "配置备份报表")
        
        elif format == "json":
            return self.export_to_json({
                "statistics": stats or {},
                "backups": backups
            }, file_path, "配置备份报表")
        
        return False
    
    def export_comparison_report(self, diff_result: Dict, file_path: str,
                                format: str = "txt") -> bool:
        """导出对比报表"""
        if format == "txt":
            content = "配置对比报表\n\n"
            content += f"备份1 ID: {diff_result.get('backup1_id', '')}\n"
            content += f"备份2 ID: {diff_result.get('backup2_id', '')}\n"
            content += f"新增行数: {diff_result.get('added', 0)}\n"
            content += f"删除行数: {diff_result.get('removed', 0)}\n"
            content += f"变更块数: {diff_result.get('changed', 0)}\n\n"
            content += "差异详情:\n"
            content += "-" * 60 + "\n"
            content += diff_result.get('diff', '')
            
            return self.export_to_txt(content, file_path, "配置对比报表")
        
        return False


def check_docx_available() -> bool:
    return DOCX_AVAILABLE


def check_pdf_available() -> bool:
    return PDF_AVAILABLE
