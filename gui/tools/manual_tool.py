#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置命令速查手册
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTextEdit, QPushButton, QTreeWidget, QTreeWidgetItem,
                             QComboBox, QGroupBox, QSplitter, QDialogButtonBox,
                             QDialog, QTabWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from utils.manual.huawei_manual import HUAWEI_COMMANDS, HUAWEI_CASES
from utils.manual.h3c_manual import H3C_COMMANDS, H3C_CASES
from utils.manual.ruijie_manual import RUIJIE_COMMANDS, RUIJIE_CASES
from utils.manual.maipu_manual import MAIPU_COMMANDS, MAIPU_CASES
from gui.tool_styles import (
    TOOL_LABEL_STYLE, TOOL_LABEL_SECONDARY,
    TOOL_BUTTON_PRIMARY, TOOL_BUTTON_GHOST,
    TOOL_STATUS_SUCCESS, TOOL_STATUS_ERROR,
    apply_tool_style
)


class ManualToolWidget(QWidget):
    """配置命令速查手册"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_device = "huawei"
        self.initUI()
    
    def initUI(self):
        apply_tool_style(self)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel("📚 配置命令速查手册")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ff9500; padding: 5px 0;")
        layout.addWidget(title_label)
        
        header = QHBoxLayout()
        header.setSpacing(8)
        
        device_label = QLabel("设备类型:")
        device_label.setStyleSheet(TOOL_LABEL_STYLE)
        header.addWidget(device_label)
        
        self.device_combo = QComboBox()
        self.device_combo.addItems([
            "🔷 华为 (Huawei)", 
            "🔶 H3C / 华三",
            "🔷 锐捷",
            "🔷 迈普"
        ])
        self.device_combo.currentIndexChanged.connect(self.on_device_changed)
        header.addWidget(self.device_combo)
        
        header.addStretch()
        
        layout.addLayout(header)
        
        splitter = QSplitter(Qt.Horizontal)
        
        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderLabel("📋 命令分类")
        self.category_tree.setMinimumWidth(280)
        self.category_tree.itemClicked.connect(self.on_item_clicked)
        splitter.addWidget(self.category_tree)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)
        right_layout.setSpacing(8)
        
        self.title_label = QLabel("请选择命令分类")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ff9500;")
        right_layout.addWidget(self.title_label)
        
        self.command_label = QLabel("")
        self.command_label.setStyleSheet("font-size: 14px; color: #ffc107; font-family: Consolas;")
        right_layout.addWidget(self.command_label)
        
        self.desc_label = QLabel("")
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("font-size: 13px; color: #8a8580; margin: 5px 0;")
        right_layout.addWidget(self.desc_label)
        
        self.example_text = QTextEdit()
        self.example_text.setReadOnly(True)
        self.example_text.setFont(QFont("Consolas", 11))
        self.example_text.setStyleSheet("""
            background-color: #0a0806;
            border: 2px solid #ff9500;
            border-radius: 6px;
            padding: 8px;
            color: #f0f0f0;
        """)
        self.example_text.setPlaceholderText("配置示例将显示在这里...")
        right_layout.addWidget(self.example_text)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([280, 500])
        
        layout.addWidget(splitter)
        
        tabs = QTabWidget()
        
        self.load_commands("huawei")
        
        self.cases_widget = QWidget()
        self.cases_layout = QVBoxLayout(self.cases_widget)
        self.cases_layout.setSpacing(8)
        
        cases_header = QHBoxLayout()
        cases_header.setSpacing(8)
        
        cases_label = QLabel("配置案例:")
        cases_label.setStyleSheet(TOOL_LABEL_STYLE)
        cases_header.addWidget(cases_label)
        
        self.case_combo = QComboBox()
        self.case_combo.currentIndexChanged.connect(self.on_case_changed)
        cases_header.addWidget(self.case_combo)
        
        cases_header.addStretch()
        self.cases_layout.addLayout(cases_header)
        
        self.case_title = QLabel("")
        self.case_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #ff9500;")
        self.cases_layout.addWidget(self.case_title)
        
        self.case_desc = QLabel("")
        self.case_desc.setStyleSheet("font-size: 13px; color: #8a8580;")
        self.cases_layout.addWidget(self.case_desc)
        
        self.case_text = QTextEdit()
        self.case_text.setReadOnly(True)
        self.case_text.setFont(QFont("Consolas", 10))
        self.case_text.setStyleSheet("""
            background-color: #0a0806;
            border: 2px solid #ff9500;
            border-radius: 6px;
            color: #f0f0f0;
        """)
        self.cases_layout.addWidget(self.case_text)
        
        cases_btn_layout = QHBoxLayout()
        self.copy_case_btn = QPushButton("📋 复制案例配置")
        self.copy_case_btn.setStyleSheet(TOOL_BUTTON_GHOST)
        self.copy_case_btn.clicked.connect(self.copy_case)
        cases_btn_layout.addWidget(self.copy_case_btn)
        cases_btn_layout.addStretch()
        self.cases_layout.addLayout(cases_btn_layout)
        
        tabs.addTab(self.cases_widget, "📋 配置案例")
        
        compare_widget = QWidget()
        compare_layout = QVBoxLayout(compare_widget)
        compare_layout.setSpacing(8)
        
        compare_label = QLabel("华为 vs H3C 命令对照表")
        compare_label.setStyleSheet(TOOL_LABEL_STYLE)
        compare_layout.addWidget(compare_label)
        
        compare_text = QTextEdit()
        compare_text.setReadOnly(True)
        compare_text.setFont(QFont("Consolas", 10))
        compare_text.setPlainText(self.get_comparison_text())
        compare_layout.addWidget(compare_text)
        
        tabs.addTab(compare_widget, "🔄 命令对照")
        
        layout.addWidget(tabs)
        
        self.status_bar = QLabel("就绪")
        self.status_bar.setStyleSheet("color: #8a8580; padding: 5px; font-size: 12px;")
        layout.addWidget(self.status_bar)
        
        self.load_cases("huawei")
    
    def load_commands(self, device_type):
        """加载命令树"""
        self.category_tree.clear()
        
        commands_map = {
            "huawei": HUAWEI_COMMANDS,
            "h3c": H3C_COMMANDS,
            "ruijie": RUIJIE_COMMANDS,
            "maipu": MAIPU_COMMANDS
        }
        commands = commands_map.get(device_type, HUAWEI_COMMANDS)
        
        for category, subcategories in commands.items():
            cat_item = QTreeWidgetItem([f"📁 {category}"])
            cat_item.setData(0, Qt.UserRole, {"type": "category", "name": category})
            
            for subcategory, cmds in subcategories.items():
                sub_item = QTreeWidgetItem([f"📂 {subcategory}"])
                sub_item.setData(0, Qt.UserRole, {"type": "subcategory", "name": subcategory})
                
                if isinstance(cmds, list):
                    for cmd_info in cmds:
                        cmd_name = cmd_info.get("name", "未命名")
                        cmd_item = QTreeWidgetItem([f"📝 {cmd_name}"])
                        cmd_item.setData(0, Qt.UserRole, {
                            "type": "command",
                            "name": cmd_name,
                            "command": cmd_info.get("command", ""),
                            "description": cmd_info.get("description", ""),
                            "example": cmd_info.get("example", "")
                        })
                        sub_item.addChild(cmd_item)
                else:
                    for cmd_name, cmd_info in cmds.items():
                        cmd_item = QTreeWidgetItem([f"📝 {cmd_name}"])
                        cmd_item.setData(0, Qt.UserRole, {
                            "type": "command",
                            "name": cmd_name,
                            "command": cmd_info["command"],
                            "description": cmd_info["description"],
                            "example": cmd_info["example"]
                        })
                        sub_item.addChild(cmd_item)
                
                cat_item.addChild(sub_item)
            
            self.category_tree.addTopLevelItem(cat_item)
        
        self.category_tree.expandAll()
    
    def load_cases(self, device_type):
        """加载配置案例"""
        cases_map = {
            "huawei": HUAWEI_CASES,
            "h3c": H3C_CASES,
            "ruijie": RUIJIE_CASES,
            "maipu": MAIPU_CASES
        }
        cases = cases_map.get(device_type, HUAWEI_CASES)
        
        self.case_combo.clear()
        for case in cases:
            self.case_combo.addItem(f"📋 {case['title']}")
        
        if cases:
            self.on_case_changed(0)
    
    def on_device_changed(self, index):
        """设备类型切换"""
        device_types = ["huawei", "h3c", "ruijie", "maipu"]
        device_names = ["华为", "H3C", "锐捷", "迈普"]
        
        self.current_device = device_types[index]
        self.load_commands(self.current_device)
        self.load_cases(self.current_device)
        
        self.title_label.setText("请选择命令分类")
        self.command_label.setText("")
        self.desc_label.setText("")
        self.example_text.clear()
        
        self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
        self.status_bar.setText(f"✅ 已切换到 {device_names[index]} 命令手册")
    
    def on_item_clicked(self, item, column):
        """选项点击"""
        data = item.data(0, Qt.UserRole)
        
        if not data:
            return
        
        if data["type"] == "command":
            self.show_command(data)
        elif data["type"] == "subcategory":
            self.title_label.setText(f"📂 {data['name']}")
            self.command_label.setText("")
            self.desc_label.setText("请选择具体命令查看详情")
            self.example_text.clear()
        elif data["type"] == "category":
            self.title_label.setText(f"📁 {data['name']}")
            self.command_label.setText("")
            self.desc_label.setText("请选择子分类和具体命令")
            self.example_text.clear()
    
    def show_command(self, data):
        """显示命令详情"""
        self.title_label.setText(f"📝 {data['name']}")
        self.command_label.setText(f"命令: {data['command']}")
        self.desc_label.setText(f"说明: {data['description']}")
        
        example = data['example']
        formatted = f"""
{'─' * 40}
📝 {data['name']}
{'─' * 40}
{example}
{'─' * 40}
"""
        self.example_text.setPlainText(formatted)
        
        self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
        self.status_bar.setText(f"✅ 查看: {data['name']}")
    
    def on_case_changed(self, index):
        """案例选择变化"""
        cases = HUAWEI_CASES if self.current_device == "huawei" else H3C_CASES
        
        if 0 <= index < len(cases):
            case = cases[index]
            self.case_title.setText(f"📋 {case['title']}")
            self.case_desc.setText(case['description'])
            self.case_text.setPlainText(case['config'])
    
    def copy_case(self):
        """复制案例配置"""
        from PyQt5.QtWidgets import QApplication
        config = self.case_text.toPlainText()
        if config:
            QApplication.clipboard().setText(config)
            self.status_bar.setStyleSheet(TOOL_STATUS_SUCCESS)
            self.status_bar.setText("✅ 已复制配置到剪贴板")
    
    def get_comparison_text(self):
        """获取命令对照表"""
        return """
┌────────────────────────────────────────────────────────────────┐
│                    华为 vs H3C 命令对照表                      │
├────────────────────────────────────────────────────────────────┤
│ 功能           │ 华为 (Huawei)           │ H3C                 │
├────────────────────────────────────────────────────────────────┤
│ 显示当前配置   │ display current-configuration │ display current-configuration │
│ 保存配置       │ save                        │ save                  │
│ 进入系统视图   │ system-view                │ system-view           │
│ 创建VLAN       │ vlan batch 10 20          │ vlan 10 20            │
│ 进入接口       │ interface GigabitEthernet0/0/1 │ interface GigabitEthernet1/0/1 │
│ 配置IP         │ ip address 192.168.1.1 24  │ ip address 192.168.1.1 24 │
│ 设置端口类型   │ port link-type access     │ port link-mode bridge │
│ 加入VLAN       │ port default vlan 10      │ port access vlan 10   │
│ Trunk允许VLAN  │ port trunk allow-pass vlan all │ port trunk permit vlan all │
│ 静态路由       │ ip route-static 0.0.0.0 0  │ ip route-static 0.0.0.0 0 │
│ 查看路由表     │ display ip routing-table  │ display ip routing-table │
│ 配置SNMP       │ snmp-agent community      │ snmp-agent community  │
│ 配置SSH        │ stelnet server enable     │ ssh server enable     │
│ 查看接口状态   │ display interface brief   │ display interface brief │
│ 查看ARP表      │ display arp all           │ display arp all       │
│ 查看MAC地址表  │ display mac-address       │ display mac-address   │
│ 配置ACL        │ acl number 3000           │ acl number 3000       │
│ 应用ACL        │ traffic-filter inbound    │ packet-filter inbound │
│ 配置NTP        │ ntp-service unicast-server │ ntp-service unicast-server │
├────────────────────────────────────────────────────────────────┤
│ 注意: H3C接口编号从1开始，华为从0开始                          │
│ 例: 华为 GE0/0/1 = H3C GE1/0/1                                │
└────────────────────────────────────────────────────────────────┘
"""
