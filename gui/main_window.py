#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
交换机配置生成器 - 主窗口 v3.0
支持华为/H3C配置生成，集成网络工具箱
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QPushButton, QTextEdit, QLabel,
                             QMessageBox, QFileDialog, QSplitter, QStatusBar,
                             QDialog, QListWidget, QDialogButtonBox, QMenu, QAction,
                             QComboBox, QMenuBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from gui.styles import MODERN_STYLE, TOOLTIP_STYLE, DIALOG_STYLE
from gui.tabs.basic_tab import BasicConfigTab
from gui.tabs.vlan_tab import VLANConfigTab
from gui.tabs.routing_tab import RoutingConfigTab
from gui.tabs.security_tab import SecurityConfigTab
from gui.tabs.interface_tab import InterfaceConfigTab
from utils.templates import get_template_names, get_template_config
from utils.validator import ConfigValidator


HUAWEI_TEMPLATES = {
    "接入交换机标准配置": {
        "description": "企业接入层交换机标准配置模板",
        "config": {
            "basic": {
                "hostname": "Access-SW-01",
                "password": {"value": "Admin@123", "encrypted": True},
                "mgmt_interface": {
                    "interface": "Vlanif1",
                    "ip_address": "192.168.1.1",
                    "mask": "255.255.255.0",
                    "gateway": "192.168.1.254"
                },
                "enable_ssh": True,
                "user": {"username": "admin", "password": "Admin@123", "level": 15}
            },
            "vlan": {
                "vlans": [{"id": 1, "name": "Management"}, {"id": 10, "name": "Sales"}]
            }
        }
    }
}

H3C_TEMPLATES = {
    "接入交换机标准配置": {
        "description": "H3C接入层交换机标准配置模板",
        "config": {
            "basic": {
                "hostname": "Access-SW-01",
                "password": {"value": "Admin@123", "encrypted": True},
                "mgmt_interface": {
                    "interface": "Vlan-interface1",
                    "ip_address": "192.168.1.1",
                    "mask": "255.255.255.0",
                    "gateway": "192.168.1.254"
                },
                "enable_ssh": True,
                "user": {"username": "admin", "password": "Admin@123", "level": 3}
            }
        }
    },
    "核心交换机配置": {
        "description": "H3C核心层交换机配置模板",
        "config": {
            "basic": {
                "hostname": "Core-SW-01",
                "password": {"value": "CoreAdmin@123", "encrypted": True},
                "mgmt_interface": {
                    "interface": "Vlan-interface1",
                    "ip_address": "10.0.0.1",
                    "mask": "255.255.255.0"
                },
                "enable_ssh": True,
                "user": {"username": "admin", "password": "CoreAdmin@123", "level": 3}
            }
        }
    }
}


class TemplateDialog(QDialog):
    """模板选择对话框"""
    
    def __init__(self, device_type="huawei", parent=None):
        super().__init__(parent)
        self.selected_template = None
        self.device_type = device_type
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(f"选择{'华为' if self.device_type == 'huawei' else 'H3C'}配置模板")
        self.setFixedSize(500, 400)
        self.setStyleSheet(MODERN_STYLE + DIALOG_STYLE)
        
        layout = QVBoxLayout(self)
        
        label = QLabel("请选择一个预设模板快速生成配置：")
        label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px; color: #1976D2;")
        layout.addWidget(label)
        
        self.template_list = QListWidget()
        
        if self.device_type == "huawei":
            templates = get_template_names()
        else:
            templates = list(H3C_TEMPLATES.keys())
        
        for name in templates:
            self.template_list.addItem(name)
        
        self.template_list.setStyleSheet("font-size: 13px;")
        self.template_list.currentRowChanged.connect(self.on_selection_changed)
        layout.addWidget(self.template_list)
        
        self.desc_label = QLabel("选择模板查看描述")
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("font-size: 12px; padding: 10px; color: #8a8a9e;")
        layout.addWidget(self.desc_label)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def on_selection_changed(self, row):
        if self.device_type == "huawei":
            from utils.templates import get_template_description
            template_names = get_template_names()
            if 0 <= row < len(template_names):
                desc = get_template_description(template_names[row])
                self.desc_label.setText(desc)
        else:
            template_names = list(H3C_TEMPLATES.keys())
            if 0 <= row < len(template_names):
                desc = H3C_TEMPLATES[template_names[row]]["description"]
                self.desc_label.setText(desc)


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        self.current_device_type = "huawei"
        self.h3c_tabs = {}
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("NetOps Toolkit v4.0 - 网络运维工具集")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        self.setStyleSheet(MODERN_STYLE + TOOLTIP_STYLE)
        
        self.createMenuBar()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        self.header_label = QLabel("华为交换机配置脚本生成工具")
        self.header_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #1976D2;
            padding: 8px;
            background: transparent;
        """)
        self.header_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.header_label, 1)
        
        device_widget = QWidget()
        device_layout = QHBoxLayout(device_widget)
        device_layout.setContentsMargins(15, 0, 0, 0)
        device_layout.setSpacing(10)
        
        device_label = QLabel("设备品牌")
        device_label.setStyleSheet("font-weight: bold; color: #1976D2; font-size: 13px;")
        device_layout.addWidget(device_label)
        
        self.device_combo = QComboBox()
        self.device_combo.addItems(["华为 (Huawei)", "华三 (H3C)", "锐捷 (Ruijie)", "迈普 (Maipu)"])
        self.device_combo.currentIndexChanged.connect(self.on_device_changed)
        self.device_combo.setMinimumWidth(160)
        device_layout.addWidget(self.device_combo)
        
        header_layout.addWidget(device_widget)
        
        version_label = QLabel("v4.0")
        version_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2196F3;
            padding: 5px 10px;
            background: rgba(124, 58, 237, 0.1);
            border-radius: 4px;
        """)
        header_layout.addWidget(version_label)
        
        main_layout.addWidget(header_widget)
        
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setHandleWidth(3)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setDocumentMode(True)
        
        self.tabs = {
            "basic": BasicConfigTab(),
            "vlan": VLANConfigTab(),
            "routing": RoutingConfigTab(),
            "security": SecurityConfigTab(),
            "interface": InterfaceConfigTab()
        }
        
        self.tab_widget.addTab(self.tabs["basic"], "基础配置")
        self.tab_widget.addTab(self.tabs["vlan"], "VLAN配置")
        self.tab_widget.addTab(self.tabs["routing"], "路由配置")
        self.tab_widget.addTab(self.tabs["security"], "安全配置")
        self.tab_widget.addTab(self.tabs["interface"], "接口配置")
        
        left_layout.addWidget(self.tab_widget)
        
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setSpacing(12)
        button_layout.setContentsMargins(5, 10, 5, 5)
        
        template_btn = QPushButton("配置模板")
        template_btn.setObjectName("ghostButton")
        template_btn.setToolTip("选择预设配置模板 (Ctrl+L)")
        template_btn.clicked.connect(self.show_template_dialog)
        button_layout.addWidget(template_btn)
        
        validate_btn = QPushButton("验证配置")
        validate_btn.setObjectName("ghostButton")
        validate_btn.setToolTip("验证当前配置参数")
        validate_btn.clicked.connect(self.validate_config)
        button_layout.addWidget(validate_btn)
        
        generate_btn = QPushButton("生成配置")
        generate_btn.setObjectName("primaryButton")
        generate_btn.setToolTip("生成完整配置脚本 (Ctrl+G)")
        generate_btn.clicked.connect(self.generate_config)
        button_layout.addWidget(generate_btn)
        
        clear_btn = QPushButton("清空")
        clear_btn.setObjectName("dangerButton")
        clear_btn.setToolTip("清空所有配置项")
        clear_btn.clicked.connect(self.clear_config)
        button_layout.addWidget(clear_btn)
        
        left_layout.addWidget(button_widget)
        
        content_splitter.addWidget(left_widget)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        
        preview_header = QHBoxLayout()
        preview_label = QLabel("配置预览")
        preview_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1976D2;
            padding: 5px;
        """)
        preview_header.addWidget(preview_label)
        
        preview_header.addStretch()
        
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("font-size: 12px; color: rgba(224, 224, 224, 0.7);")
        preview_header.addWidget(self.info_label)
        
        right_layout.addLayout(preview_header)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet("""
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 13px;
            background: rgba(10, 10, 30, 0.9);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 8px;
            padding: 10px;
            color: #e0e0e0;
        """)
        self.preview_text.textChanged.connect(self.update_info)
        right_layout.addWidget(self.preview_text, 1)
        
        export_widget = QWidget()
        export_layout = QHBoxLayout(export_widget)
        export_layout.setSpacing(12)
        export_layout.setContentsMargins(5, 10, 5, 5)
        
        export_btn = QPushButton("导出文件")
        export_btn.setObjectName("secondaryButton")
        export_btn.setToolTip("导出配置到文件")
        export_btn.clicked.connect(self.export_config)
        export_layout.addWidget(export_btn)
        
        copy_btn = QPushButton("复制配置")
        copy_btn.setObjectName("warningButton")
        copy_btn.setToolTip("复制配置到剪贴板 (Ctrl+C)")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        export_layout.addWidget(copy_btn)
        
        export_layout.addStretch()
        
        right_layout.addWidget(export_widget)
        
        content_splitter.addWidget(right_widget)
        content_splitter.setSizes([600, 800])
        
        main_layout.addWidget(content_splitter, 1)
        
        self.statusBar().showMessage("就绪 | 点击「网络工具」菜单使用网络工具箱")
    
    def createMenuBar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("文件(&F)")
        
        batch_action = QAction("批量配置生成", self)
        batch_action.setShortcut("Ctrl+B")
        batch_action.triggered.connect(self.open_batch_config)
        file_menu.addAction(batch_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("导出配置", self)
        export_action.setShortcut("Ctrl+S")
        export_action.triggered.connect(self.export_config)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        settings_action = QAction("系统设置", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        tools_menu = menubar.addMenu("网络工具(&T)")
        
        subnet_action = QAction("子网计算器", self)
        subnet_action.triggered.connect(lambda: self.open_network_tool("subnet"))
        tools_menu.addAction(subnet_action)
        
        ping_action = QAction("Ping测试", self)
        ping_action.triggered.connect(lambda: self.open_network_tool("ping"))
        tools_menu.addAction(ping_action)
        
        port_action = QAction("端口扫描", self)
        port_action.triggered.connect(lambda: self.open_network_tool("port"))
        tools_menu.addAction(port_action)
        
        trace_action = QAction("路由跟踪", self)
        trace_action.triggered.connect(lambda: self.open_network_tool("trace"))
        tools_menu.addAction(trace_action)
        
        dns_action = QAction("DNS/Whois查询", self)
        dns_action.triggered.connect(lambda: self.open_network_tool("dns"))
        tools_menu.addAction(dns_action)
        
        http_action = QAction("HTTP状态检测", self)
        http_action.triggered.connect(lambda: self.open_network_tool("http"))
        tools_menu.addAction(http_action)
        
        mac_action = QAction("MAC地址查询", self)
        mac_action.triggered.connect(lambda: self.open_network_tool("mac"))
        tools_menu.addAction(mac_action)
        
        tools_menu.addSeparator()
        
        password_action = QAction("密码生成器", self)
        password_action.triggered.connect(lambda: self.open_network_tool("password"))
        tools_menu.addAction(password_action)
        
        encoder_action = QAction("编码转换器", self)
        encoder_action.triggered.connect(lambda: self.open_network_tool("encoder"))
        tools_menu.addAction(encoder_action)
        
        tools_menu.addSeparator()
        
        manual_action = QAction("配置命令手册", self)
        manual_action.setShortcut("Ctrl+M")
        manual_action.triggered.connect(lambda: self.open_network_tool("manual"))
        tools_menu.addAction(manual_action)
        
        tools_menu.addSeparator()
        
        compare_action = QAction("配置比较工具", self)
        compare_action.setShortcut("Ctrl+Shift+C")
        compare_action.triggered.connect(lambda: self.open_network_tool("compare"))
        tools_menu.addAction(compare_action)
        
        io_action = QAction("配置导入导出", self)
        io_action.setShortcut("Ctrl+I")
        io_action.triggered.connect(lambda: self.open_network_tool("configio"))
        tools_menu.addAction(io_action)
        
        tools_menu.addSeparator()
        
        all_tools_action = QAction("打开工具箱", self)
        all_tools_action.setShortcut("Ctrl+T")
        all_tools_action.triggered.connect(self.open_tools_window)
        tools_menu.addAction(all_tools_action)
        
        template_menu = menubar.addMenu("模板(&M)")
        
        manager_action = QAction("模板管理器", self)
        manager_action.setShortcut("Ctrl+M")
        manager_action.triggered.connect(self.open_template_manager)
        template_menu.addAction(manager_action)
        
        save_action = QAction("保存为模板", self)
        save_action.setShortcut("Ctrl+Shift+S")
        save_action.triggered.connect(self.save_as_template)
        template_menu.addAction(save_action)
        
        template_menu.addSeparator()
        
        apply_huawei_action = QAction("应用华为模板", self)
        apply_huawei_action.triggered.connect(lambda: self.quick_apply_template("huawei"))
        template_menu.addAction(apply_huawei_action)
        
        apply_h3c_action = QAction("应用H3C模板", self)
        apply_h3c_action.triggered.connect(lambda: self.quick_apply_template("h3c"))
        template_menu.addAction(apply_h3c_action)
        
        template_menu.addSeparator()
        
        import_template_action = QAction("导入模板", self)
        import_template_action.triggered.connect(self.import_template)
        template_menu.addAction(import_template_action)
        
        export_template_action = QAction("导出当前模板", self)
        export_template_action.triggered.connect(self.export_current_template)
        template_menu.addAction(export_template_action)
        
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于", self)
        about_action.setShortcut("F1")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def on_device_changed(self, index):
        """设备类型切换"""
        device_types = ["huawei", "h3c", "ruijie", "maipu"]
        self.current_device_type = device_types[index]
        
        device_names = {
            "huawei": ("华为交换机配置脚本生成工具", "华为", "Huawei"),
            "h3c": ("H3C华三交换机配置脚本生成工具", "H3C", "H3C"),
            "ruijie": ("锐捷交换机配置脚本生成工具", "锐捷", "Ruijie"),
            "maipu": ("迈普交换机配置脚本生成工具", "迈普", "Maipu")
        }
        
        title, name, _ = device_names[self.current_device_type]
        self.header_label.setText(title)
        self.setWindowTitle(f"NetOps Toolkit v4.0 - {name}配置")
        
        for tab in self.tabs.values():
            tab.clear_config()
        self.preview_text.clear()
        
        self.statusBar().showMessage(f"已切换到{name}模式", 3000)
    
    def open_network_tool(self, tool_name):
        """打开单个网络工具"""
        from gui.tools_window import NetworkToolsWindow
        from gui.tools.subnet_tool import SubnetCalculatorWidget
        from gui.tools.ping_tool import PingTestWidget
        from gui.tools.port_tool import PortScanWidget
        from gui.tools.trace_tool import TraceRouteWidget
        from gui.tools.dns_tool import DNSToolWidget
        from gui.tools.manual_tool import ManualToolWidget
        from gui.tools.config_compare_tool import ConfigCompareWidget
        from gui.tools.config_io_tool import ConfigIOWidget
        
        tool_widgets = {
            "subnet": SubnetCalculatorWidget,
            "ping": PingTestWidget,
            "port": PortScanWidget,
            "trace": TraceRouteWidget,
            "dns": DNSToolWidget,
            "manual": ManualToolWidget,
            "compare": ConfigCompareWidget,
            "configio": ConfigIOWidget
        }
        
        if tool_name in tool_widgets:
            dialog = QDialog(self)
            
            titles = {
                "subnet": "子网计算器",
                "ping": "Ping测试",
                "port": "端口扫描",
                "trace": "路由跟踪",
                "dns": "DNS工具",
                "manual": "配置命令速查手册",
                "compare": "配置比较工具",
                "configio": "配置导入导出"
            }
            
            dialog.setWindowTitle(f"{titles.get(tool_name, tool_name)}")
            dialog.setMinimumSize(800, 600)
            dialog.resize(1000, 750)
            
            dialog.setStyleSheet(MODERN_STYLE + TOOLTIP_STYLE + DIALOG_STYLE)
            
            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(15, 15, 15, 15)
            layout.setSpacing(10)
            widget = tool_widgets[tool_name]()
            layout.addWidget(widget)
            
            dialog.exec_()
    
    def open_tools_window(self):
        """打开完整工具箱窗口"""
        from gui.tools_window import NetworkToolsWindow
        
        self.tools_window = NetworkToolsWindow()
        self.tools_window.show()
    
    def open_settings(self):
        """打开设置对话框"""
        from gui.dialogs import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.exec_()
    
    def open_batch_config(self):
        """打开批量配置生成对话框"""
        from gui.dialogs import BatchConfigDialog
        dialog = BatchConfigDialog(self, self.current_device_type)
        dialog.exec_()
    
    def show_about(self):
        """显示关于对话框"""
        from gui.dialogs import AboutDialog
        dialog = AboutDialog(self)
        dialog.exec_()
    
    def update_info(self):
        text = self.preview_text.toPlainText()
        line_count = text.count('\n') + 1 if text else 0
        char_count = len(text)
        config_sections = text.count('#')
        self.info_label.setText(f"行数: {line_count} | 字符: {char_count} | 配置块: {config_sections // 2}")
    
    def show_template_dialog(self):
        dialog = TemplateDialog(self.current_device_type, self)
        if dialog.exec_() == QDialog.Accepted:
            if self.current_device_type == "huawei":
                template_names = get_template_names()
            else:
                template_names = list(H3C_TEMPLATES.keys())
            
            row = dialog.template_list.currentRow()
            if 0 <= row < len(template_names):
                template_name = template_names[row]
                self.load_template(template_name)
    
    def load_template(self, template_name):
        if self.current_device_type == "huawei":
            template_config = get_template_config(template_name)
        else:
            template_config = H3C_TEMPLATES.get(template_name, {}).get("config", {})
        
        if not template_config:
            QMessageBox.warning(self, "警告", f"模板 {template_name} 不存在！")
            return
        
        reply = QMessageBox.question(
            self, "加载模板",
            f"确定要加载模板 \"{template_name}\" 吗？\n这将覆盖当前所有配置。",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for tab in self.tabs.values():
                tab.clear_config()
            
            if "basic" in template_config:
                basic_tab = self.tabs["basic"]
                basic_cfg = template_config["basic"]
                if "hostname" in basic_cfg:
                    basic_tab.hostname_input.setText(basic_cfg["hostname"])
                if "password" in basic_cfg:
                    basic_tab.password_input.setText(basic_cfg["password"]["value"])
                    basic_tab.encrypted_checkbox.setChecked(basic_cfg["password"].get("encrypted", False))
                if "mgmt_interface" in basic_cfg:
                    mgmt = basic_cfg["mgmt_interface"]
                    basic_tab.mgmt_interface.setText(mgmt.get("interface", "Vlanif1"))
                    basic_tab.mgmt_ip.setText(mgmt.get("ip_address", ""))
                    basic_tab.mgmt_mask.setText(mgmt.get("mask", "255.255.255.0"))
                    basic_tab.mgmt_gateway.setText(mgmt.get("gateway", ""))
                if basic_cfg.get("enable_ssh"):
                    basic_tab.enable_ssh.setChecked(True)
                if "user" in basic_cfg:
                    user = basic_cfg["user"]
                    basic_tab.username_input.setText(user.get("username", "admin"))
                    basic_tab.user_password_input.setText(user.get("password", ""))
                    basic_tab.privilege_level.setValue(user.get("level", 15))
            
            self.statusBar().showMessage(f"已加载模板: {template_name}", 5000)
            QMessageBox.information(self, "成功", f"模板 \"{template_name}\" 已加载！")
    
    def validate_config(self):
        errors = []
        basic_tab = self.tabs["basic"]
        
        hostname = basic_tab.hostname_input.text().strip()
        if hostname:
            is_valid, msg = ConfigValidator.validate_hostname(hostname)
            if not is_valid:
                errors.append(f"主机名: {msg}")
        
        mgmt_ip = basic_tab.mgmt_ip.text().strip()
        if mgmt_ip:
            is_valid, msg = ConfigValidator.validate_ip_address(mgmt_ip)
            if not is_valid:
                errors.append(f"管理IP: {msg}")
        
        mgmt_mask = basic_tab.mgmt_mask.text().strip()
        if mgmt_mask:
            is_valid, msg = ConfigValidator.validate_subnet_mask(mgmt_mask)
            if not is_valid:
                errors.append(f"子网掩码: {msg}")
        
        if errors:
            error_msg = "配置验证失败：\n\n" + "\n".join(f"• {e}" for e in errors)
            QMessageBox.warning(self, "验证失败", error_msg)
            self.statusBar().showMessage(f"验证失败: {len(errors)} 个错误", 5000)
        else:
            QMessageBox.information(self, "验证通过", "所有配置参数格式正确！")
            self.statusBar().showMessage("验证通过", 3000)
    
    def generate_config(self):
        all_config = []
        
        device_headers = {
            "huawei": ("华为交换机配置脚本", "huawei"),
            "h3c": ("H3C华三交换机配置脚本", "h3c"),
            "ruijie": ("锐捷交换机配置脚本", "ruijie"),
            "maipu": ("迈普交换机配置脚本", "maipu")
        }
        
        basic_config = self.tabs["basic"].get_config()
        if basic_config:
            all_config.append(basic_config)
        
        vlan_config = self.tabs["vlan"].get_config()
        if vlan_config:
            all_config.append(vlan_config)
        
        routing_config = self.tabs["routing"].get_config()
        if routing_config:
            all_config.append(routing_config)
        
        security_config = self.tabs["security"].get_config()
        if security_config:
            all_config.append(security_config)
        
        interface_config = self.tabs["interface"].get_config()
        if interface_config:
            all_config.append(interface_config)
        
        if not all_config:
            QMessageBox.warning(self, "警告", "请至少配置一个模块！")
            return
        
        full_config = "\n".join(all_config)
        
        header_title, _ = device_headers.get(self.current_device_type, device_headers["huawei"])
        header = f"""#
# {header_title}
# 生成时间: {__import__('time').strftime('%Y-%m-%d %H:%M:%S')}
#

"""
        
        if self.current_device_type == "h3c":
            full_config = full_config.replace("Vlanif", "Vlan-interface")
        
        self.preview_text.setPlainText(header + full_config)
        self.statusBar().showMessage("配置生成成功！", 3000)
        QMessageBox.information(self, "成功", "配置生成成功！")
    
    def export_config(self):
        config_text = self.preview_text.toPlainText()
        if not config_text:
            QMessageBox.warning(self, "警告", "请先生成配置！")
            return
        
        default_name = f"{self.current_device_type}_switch_config.txt"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存配置文件", default_name,
            "配置文件 (*.txt);;脚本文件 (*.cfg);;所有文件 (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(config_text)
                self.statusBar().showMessage(f"配置已导出到: {file_path}", 5000)
                QMessageBox.information(self, "成功", f"配置已导出到：\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败：\n{str(e)}")
    
    def copy_to_clipboard(self):
        config_text = self.preview_text.toPlainText()
        if not config_text:
            QMessageBox.warning(self, "警告", "请先生成配置！")
            return
        
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(config_text)
        
        self.statusBar().showMessage("配置已复制到剪贴板", 3000)
        QMessageBox.information(self, "成功", "配置已复制到剪贴板！")
    
    def clear_config(self):
        reply = QMessageBox.question(
            self, "确认", "确定要清空所有配置吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for tab in self.tabs.values():
                tab.clear_config()
            self.preview_text.clear()
            self.statusBar().showMessage("配置已清空", 3000)
    
    def open_template_manager(self):
        from gui.dialogs.template_dialog import TemplateManagerDialog
        
        dialog = TemplateManagerDialog(self, self.current_device_type)
        dialog.template_selected.connect(self.apply_template_config)
        dialog.exec_()
    
    def apply_template_config(self, template_data):
        config = template_data.get("config", {})
        
        if "basic" in config and "basic" in self.tabs:
            self.tabs["basic"].load_config(config["basic"])
        if "vlan" in config and "vlan" in self.tabs:
            self.tabs["vlan"].load_config(config["vlan"])
        if "routing" in config and "routing" in self.tabs:
            self.tabs["routing"].load_config(config["routing"])
        if "security" in config and "security" in self.tabs:
            self.tabs["security"].load_config(config["security"])
        if "interface" in config and "interface" in self.tabs:
            self.tabs["interface"].load_config(config["interface"])
        
        self.statusBar().showMessage(f"已应用模板: {template_data.get('name', '')}", 5000)
        QMessageBox.information(self, "成功", f"模板 '{template_data.get('name', '')}' 已应用！")
    
    def save_as_template(self):
        from gui.dialogs.template_dialog import SaveTemplateDialog
        
        config = self._collect_current_config()
        
        dialog = SaveTemplateDialog(self, config, self.current_device_type)
        dialog.exec_()
    
    def _collect_current_config(self):
        config = {}
        
        if "basic" in self.tabs:
            config["basic"] = self.tabs["basic"].get_config_data()
        if "vlan" in self.tabs:
            config["vlan"] = self.tabs["vlan"].get_config_data()
        if "routing" in self.tabs:
            config["routing"] = self.tabs["routing"].get_config_data()
        if "security" in self.tabs:
            config["security"] = self.tabs["security"].get_config_data()
        if "interface" in self.tabs:
            config["interface"] = self.tabs["interface"].get_config_data()
        
        return config
    
    def quick_apply_template(self, device_type):
        from gui.dialogs.template_dialog import TemplateManagerDialog
        
        dialog = TemplateManagerDialog(self, device_type)
        dialog.template_selected.connect(self.apply_template_config)
        dialog.exec_()
    
    def import_template(self):
        from utils.template_manager import TemplateManager
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入模板", "", "JSON文件 (*.json)"
        )
        
        if file_path:
            manager = TemplateManager()
            if manager.import_template(file_path):
                QMessageBox.information(self, "成功", "模板导入成功！")
            else:
                QMessageBox.warning(self, "失败", "导入模板失败，请检查文件格式。")
    
    def export_current_template(self):
        from utils.template_manager import TemplateManager
        from PyQt5.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(self, "导出模板", "请输入模板名称:")
        if not ok or not name:
            return
        
        config = self._collect_current_config()
        manager = TemplateManager()
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出模板", f"{name}.json", "JSON文件 (*.json)"
        )
        
        if file_path:
            from utils.template_manager import Template
            template = Template(
                name=name,
                device_type=self.current_device_type,
                config=config
            )
            if manager.export_template(name, self.current_device_type, file_path):
                QMessageBox.information(self, "成功", "模板导出成功！")
            else:
                QMessageBox.warning(self, "失败", "导出模板失败。")
