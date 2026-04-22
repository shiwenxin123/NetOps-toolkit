#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络工具窗口 - HTTP状态检测
"""

import requests
from datetime import datetime
from urllib.parse import urlparse
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTextEdit, QGroupBox,
                             QSpinBox, QCheckBox, QTabWidget, QProgressBar,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gui.tool_styles import (
    TOOL_LABEL_STYLE, TOOL_LABEL_SECONDARY,
    TOOL_BUTTON_PRIMARY, TOOL_BUTTON_DANGER, TOOL_BUTTON_GHOST,
    TOOL_STATUS_SUCCESS, TOOL_STATUS_ERROR, TOOL_STATUS_WARNING, TOOL_STATUS_INFO,
    apply_tool_style
)


class HTTPCheckWorker(QThread):
    """HTTP检测工作线程"""
    result_ready = pyqtSignal(dict)
    progress_update = pyqtSignal(str)
    
    def __init__(self, url, timeout=10, follow_redirects=True, check_ssl=True):
        super().__init__()
        self.url = url
        self.timeout = timeout
        self.follow_redirects = follow_redirects
        self.check_ssl = check_ssl
    
    def run(self):
        result = {
            "success": False,
            "url": self.url,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status_code": None,
            "status_text": "",
            "response_time_ms": 0,
            "content_size": 0,
            "headers": {},
            "redirects": [],
            "ssl_info": None,
            "error": ""
        }
        
        try:
            self.progress_update.emit(f"🔍 正在检测 {self.url}...")
            
            if not self.url.startswith(('http://', 'https://')):
                self.url = 'http://' + self.url
            
            start_time = datetime.now()
            
            response = requests.get(
                self.url, 
                timeout=self.timeout,
                allow_redirects=self.follow_redirects,
                verify=self.check_ssl
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000
            
            result["success"] = True
            result["status_code"] = response.status_code
            result["status_text"] = response.reason
            result["response_time_ms"] = round(duration, 2)
            result["content_size"] = len(response.content)
            result["headers"] = dict(response.headers)
            
            if response.history:
                result["redirects"] = [r.url for r in response.history]
            
            if self.url.startswith('https://') and self.check_ssl:
                try:
                    import ssl
                    import socket
                    parsed = urlparse(self.url)
                    hostname = parsed.hostname
                    port = parsed.port or 443
                    
                    context = ssl.create_default_context()
                    with socket.create_connection((hostname, port), timeout=5) as sock:
                        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                            cert = ssock.getpeercert()
                            result["ssl_info"] = {
                                "subject": dict(x[0] for x in cert.get('subject', [])),
                                "issuer": dict(x[0] for x in cert.get('issuer', [])),
                                "version": cert.get('version'),
                                "not_before": cert.get('notBefore'),
                                "not_after": cert.get('notAfter'),
                            }
                except Exception as e:
                    result["ssl_info"] = {"error": str(e)}
            
        except requests.exceptions.Timeout:
            result["error"] = "连接超时"
        except requests.exceptions.ConnectionError as e:
            result["error"] = f"连接错误: {str(e)[:100]}"
        except requests.exceptions.SSLError as e:
            result["error"] = f"SSL错误: {str(e)[:100]}"
        except Exception as e:
            result["error"] = f"检测失败: {str(e)[:100]}"
        
        self.result_ready.emit(result)


class BatchHTTPCheckWorker(QThread):
    """批量HTTP检测工作线程"""
    result_ready = pyqtSignal(list)
    progress_update = pyqtSignal(str, int)
    
    def __init__(self, urls, timeout=10):
        super().__init__()
        self.urls = urls
        self.timeout = timeout
    
    def run(self):
        results = []
        total = len(self.urls)
        
        for i, url in enumerate(self.urls):
            self.progress_update.emit(f"检测 {url}", int((i / total) * 100))
            
            url = url.strip()
            if not url:
                continue
            
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            
            result = {
                "url": url,
                "success": False,
                "status_code": None,
                "response_time_ms": 0,
                "error": ""
            }
            
            try:
                start_time = datetime.now()
                response = requests.get(url, timeout=self.timeout, allow_redirects=True, verify=False)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds() * 1000
                
                result["success"] = True
                result["status_code"] = response.status_code
                result["response_time_ms"] = round(duration, 2)
            except Exception as e:
                result["error"] = str(e)[:50]
            
            results.append(result)
        
        self.progress_update.emit("检测完成", 100)
        self.result_ready.emit(results)


class HTTPStatusWidget(QWidget):
    """HTTP状态检测工具"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.initUI()
    
    def initUI(self):
        apply_tool_style(self)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel("🌐 HTTP状态检测")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976D2; padding: 5px 0;")
        layout.addWidget(title_label)
        
        tabs = QTabWidget()
        
        single_widget = QWidget()
        single_layout = QVBoxLayout(single_widget)
        single_layout.setSpacing(10)
        
        input_group = QGroupBox("检测设置")
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(10)
        
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        
        url_label = QLabel("URL:")
        url_label.setStyleSheet(TOOL_LABEL_STYLE)
        row1.addWidget(url_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("输入网址，如: www.baidu.com 或 https://example.com")
        self.url_input.setText("www.baidu.com")
        row1.addWidget(self.url_input)
        
        input_layout.addLayout(row1)
        
        options_row = QHBoxLayout()
        options_row.setSpacing(15)
        
        self.follow_redirects_cb = QCheckBox("跟随重定向")
        self.follow_redirects_cb.setChecked(True)
        options_row.addWidget(self.follow_redirects_cb)
        
        self.check_ssl_cb = QCheckBox("验证SSL证书")
        self.check_ssl_cb.setChecked(True)
        options_row.addWidget(self.check_ssl_cb)
        
        timeout_label = QLabel("超时(s):")
        timeout_label.setStyleSheet(TOOL_LABEL_STYLE)
        options_row.addWidget(timeout_label)
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 60)
        self.timeout_spin.setValue(10)
        self.timeout_spin.setMinimumWidth(70)
        options_row.addWidget(self.timeout_spin)
        
        options_row.addStretch()
        
        self.check_btn = QPushButton("🔍 开始检测")
        self.check_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.check_btn.clicked.connect(self.start_check)
        options_row.addWidget(self.check_btn)
        
        input_layout.addLayout(options_row)
        single_layout.addWidget(input_group)
        
        result_group = QGroupBox("检测结果")
        result_layout = QVBoxLayout(result_group)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Consolas", 10))
        self.result_text.setMinimumHeight(350)
        result_layout.addWidget(self.result_text)
        
        single_layout.addWidget(result_group)
        tabs.addTab(single_widget, "🔍 单站检测")
        
        batch_widget = QWidget()
        batch_layout = QVBoxLayout(batch_widget)
        batch_layout.setSpacing(10)
        
        batch_group = QGroupBox("批量检测")
        batch_inner = QVBoxLayout(batch_group)
        
        batch_inner.addWidget(QLabel("URL列表（每行一个）:"))
        
        self.batch_urls = QTextEdit()
        self.batch_urls.setFont(QFont("Consolas", 10))
        self.batch_urls.setPlaceholderText("www.baidu.com\nwww.google.com\nwww.github.com")
        self.batch_urls.setMaximumHeight(150)
        self.batch_urls.setText("www.baidu.com\nwww.bing.com\nwww.qq.com")
        batch_inner.addWidget(self.batch_urls)
        
        batch_btn_row = QHBoxLayout()
        batch_btn_row.addStretch()
        
        self.batch_check_btn = QPushButton("📋 批量检测")
        self.batch_check_btn.setStyleSheet(TOOL_BUTTON_PRIMARY)
        self.batch_check_btn.clicked.connect(self.start_batch_check)
        batch_btn_row.addWidget(self.batch_check_btn)
        
        batch_inner.addLayout(batch_btn_row)
        batch_layout.addWidget(batch_group)
        
        self.batch_result_table = QTableWidget()
        self.batch_result_table.setColumnCount(4)
        self.batch_result_table.setHorizontalHeaderLabels(["URL", "状态码", "响应时间", "状态"])
        self.batch_result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.batch_result_table.setMinimumHeight(300)
        batch_layout.addWidget(self.batch_result_table)
        
        tabs.addTab(batch_widget, "📋 批量检测")
        
        layout.addWidget(tabs)
        
        self.status_bar = QLabel("就绪")
        self.status_bar.setStyleSheet("color: #666666; padding: 5px; font-size: 12px;")
        layout.addWidget(self.status_bar)
    
    def start_check(self):
        url = self.url_input.text().strip()
        
        if not url:
            self.result_text.setPlainText("❌ 请输入URL")
            return
        
        self.check_btn.setEnabled(False)
        self.result_text.setPlainText("🔍 正在检测...")
        self.status_bar.setStyleSheet(TOOL_STATUS_INFO)
        self.status_bar.setText(f"正在检测 {url}...")
        
        self.worker = HTTPCheckWorker(
            url,
            self.timeout_spin.value(),
            self.follow_redirects_cb.isChecked(),
            self.check_ssl_cb.isChecked()
        )
        self.worker.result_ready.connect(self.on_result)
        self.worker.progress_update.connect(self.on_progress)
        self.worker.finished.connect(lambda: self.check_btn.setEnabled(True))
        self.worker.start()
    
    def on_progress(self, msg):
        self.status_bar.setText(msg)
    
    def on_result(self, result):
        if result["success"]:
            status_color = "#4ade80" if 200 <= result["status_code"] < 300 else "#fbbf24"
            if result["status_code"] >= 400:
                status_color = "#f87171"
            
            txt = f"""
{'─' * 60}
✅ HTTP检测成功
{'─' * 60}
📍 URL: {result['url']}
🔢 状态码: {result['status_code']} {result['status_text']}
⏱️ 响应时间: {result['response_time_ms']:.2f} ms
📦 内容大小: {result['content_size']:,} bytes
🕐 检测时间: {result['timestamp']}
"""
            
            if result['redirects']:
                txt += f"\n🔄 重定向路径:\n"
                for i, r in enumerate(result['redirects'], 1):
                    txt += f"   {i}. {r}\n"
            
            if result.get('ssl_info') and 'error' not in result['ssl_info']:
                ssl_info = result['ssl_info']
                txt += f"""
{'─' * 60}
🔐 SSL证书信息:
   颁发给: {ssl_info.get('subject', {}).get('commonName', 'N/A')}
   颁发者: {ssl_info.get('issuer', {}).get('commonName', 'N/A')}
   有效期: {ssl_info.get('not_before')} ~ {ssl_info.get('not_after')}
"""
            elif result.get('ssl_info') and 'error' in result['ssl_info']:
                txt += f"\n⚠️ SSL检测失败: {result['ssl_info']['error']}\n"
            
            txt += f"\n{'─' * 60}\n📋 响应头:\n"
            for key, value in list(result['headers'].items())[:10]:
                txt += f"   {key}: {value}\n"
            
            if len(result['headers']) > 10:
                txt += f"   ... 共 {len(result['headers'])} 个响应头\n"
            
            self.result_text.setPlainText(txt)
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText(f"✅ 检测完成 - 状态码: {result['status_code']}")
        else:
            self.result_text.setPlainText(f"""
{'─' * 60}
❌ HTTP检测失败
{'─' * 60}
📍 URL: {result['url']}
❌ 错误: {result['error']}
🕐 时间: {result['timestamp']}
{'─' * 60}
""")
            self.status_bar.setStyleSheet(TOOL_STATUS_ERROR)
            self.status_bar.setText(f"❌ 检测失败")
    
    def start_batch_check(self):
        urls_text = self.batch_urls.toPlainText().strip()
        
        if not urls_text:
            return
        
        urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
        
        if not urls:
            return
        
        self.batch_check_btn.setEnabled(False)
        self.batch_result_table.setRowCount(0)
        self.status_bar.setStyleSheet(TOOL_STATUS_INFO)
        self.status_bar.setText("批量检测中...")
        
        self.batch_worker = BatchHTTPCheckWorker(urls, self.timeout_spin.value())
        self.batch_worker.result_ready.connect(self.on_batch_result)
        self.batch_worker.progress_update.connect(self.on_batch_progress)
        self.batch_worker.finished.connect(lambda: self.batch_check_btn.setEnabled(True))
        self.batch_worker.start()
    
    def on_batch_progress(self, msg, percent):
        self.status_bar.setText(f"{msg} ({percent}%)")
    
    def on_batch_result(self, results):
        self.batch_result_table.setRowCount(len(results))
        
        success_count = 0
        for i, r in enumerate(results):
            url_item = QTableWidgetItem(r['url'])
            self.batch_result_table.setItem(i, 0, url_item)
            
            status_item = QTableWidgetItem(str(r.get('status_code', '-')))
            if r['success']:
                if 200 <= r['status_code'] < 300:
                    status_item.setForeground(QColor("#4ade80"))
                    success_count += 1
                elif r['status_code'] < 400:
                    status_item.setForeground(QColor("#fbbf24"))
                    success_count += 1
                else:
                    status_item.setForeground(QColor("#f87171"))
            else:
                status_item.setForeground(QColor("#f87171"))
            self.batch_result_table.setItem(i, 1, status_item)
            
            time_item = QTableWidgetItem(f"{r.get('response_time_ms', 0):.1f}ms")
            self.batch_result_table.setItem(i, 2, time_item)
            
            status_text = "✅ 正常" if r['success'] and 200 <= r.get('status_code', 0) < 400 else "❌ 异常"
            state_item = QTableWidgetItem(status_text)
            state_item.setForeground(QColor("#4ade80") if "正常" in status_text else QColor("#f87171"))
            self.batch_result_table.setItem(i, 3, state_item)
        
        self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
        self.status_bar.setText(f"✅ 批量检测完成 - {success_count}/{len(results)} 正常")
