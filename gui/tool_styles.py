#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络工具箱统一样式定义 v4.0
浅色背景 + 蓝色强调色 - 清爽明亮风格
"""

TOOL_LABEL_STYLE = "color: #1976D2; font-weight: bold;"
TOOL_LABEL_SECONDARY = "color: #666666;"

TOOL_GROUP_STYLE = """
QGroupBox {
    font-weight: bold;
    font-size: 13px;
    color: #1976D2;
    border: 2px solid rgba(33, 150, 243, 0.35);
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    background: #ffffff;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
}
"""

TOOL_INPUT_STYLE = """
QLineEdit {
    padding: 8px 12px;
    border: 2px solid rgba(33, 150, 243, 0.3);
    border-radius: 6px;
    background: #ffffff;
    color: #1a1a1a;
    font-size: 13px;
}
QLineEdit:focus {
    border: 2px solid #2196F3;
}
QLineEdit::placeholder {
    color: #9e9e9e;
}
"""

TOOL_SPINBOX_STYLE = """
QSpinBox, QDoubleSpinBox {
    padding: 6px 10px;
    border: 2px solid rgba(33, 150, 243, 0.3);
    border-radius: 6px;
    background: #ffffff;
    color: #1a1a1a;
    font-size: 13px;
}
QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #2196F3;
}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background: #2196F3;
    border: none;
    width: 18px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
    background: #1976D2;
}
"""

TOOL_COMBO_STYLE = """
QComboBox {
    padding: 8px 12px;
    border: 2px solid rgba(33, 150, 243, 0.3);
    border-radius: 6px;
    background: #ffffff;
    color: #1a1a1a;
    font-size: 13px;
}
QComboBox:focus {
    border: 2px solid #2196F3;
}
QComboBox::drop-down {
    border: none;
    width: 28px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 7px solid #2196F3;
    margin-right: 8px;
}
QComboBox QAbstractItemView {
    background: #ffffff;
    border: 2px solid #2196F3;
    selection-background-color: #2196F3;
    color: #1a1a1a;
    outline: none;
}
"""

TOOL_BUTTON_PRIMARY = """
QPushButton {
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 13px;
    border: none;
    background: #2196F3;
    color: #ffffff;
}
QPushButton:hover {
    background: #1976D2;
}
QPushButton:disabled {
    background: #bdbdbd;
    color: #757575;
}
"""

TOOL_BUTTON_SECONDARY = """
QPushButton {
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 13px;
    border: none;
    background: #64B5F6;
    color: #ffffff;
}
QPushButton:hover {
    background: #42A5F5;
}
"""

TOOL_BUTTON_DANGER = """
QPushButton {
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 13px;
    border: none;
    background: #F44336;
    color: #ffffff;
}
QPushButton:hover {
    background: #D32F2F;
}
QPushButton:disabled {
    background: #bdbdbd;
    color: #757575;
}
"""

TOOL_BUTTON_GHOST = """
QPushButton {
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 13px;
    background: transparent;
    border: 2px solid #2196F3;
    color: #2196F3;
}
QPushButton:hover {
    background: #e3f2fd;
}
"""

TOOL_TEXTEDIT_STYLE = """
QTextEdit, QPlainTextEdit {
    border: 2px solid rgba(33, 150, 243, 0.3);
    border-radius: 8px;
    background: #ffffff;
    color: #1a1a1a;
    padding: 8px;
    font-size: 13px;
}
QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #2196F3;
}
"""

TOOL_TABLE_STYLE = """
QTableWidget, QTableView {
    gridline-color: #e0e0e0;
    border: 2px solid rgba(33, 150, 243, 0.3);
    border-radius: 8px;
    background: #ffffff;
    selection-background-color: #2196F3;
    selection-color: #ffffff;
    color: #1a1a1a;
    font-size: 13px;
}
QTableWidget::item, QTableView::item {
    padding: 6px;
    border: none;
}
QTableWidget::item:selected, QTableView::item:selected {
    background: #2196F3;
    color: #ffffff;
}
QTableWidget::item:hover, QTableView::item:hover {
    background: #e3f2fd;
}
QHeaderView::section {
    background: #f5f5f5;
    color: #1976D2;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #2196F3;
    font-weight: bold;
    font-size: 12px;
}
"""

TOOL_LIST_STYLE = """
QListWidget {
    border: 2px solid rgba(33, 150, 243, 0.3);
    border-radius: 8px;
    background: #ffffff;
    outline: none;
}
QListWidget::item {
    padding: 8px 10px;
    border-bottom: 1px solid #e0e0e0;
    color: #1a1a1a;
}
QListWidget::item:selected {
    background: #2196F3;
    color: #ffffff;
}
QListWidget::item:hover:!selected {
    background: #e3f2fd;
}
"""

TOOL_CHECKBOX_STYLE = """
QCheckBox {
    spacing: 8px;
    color: #1a1a1a;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #2196F3;
    background: #ffffff;
}
QCheckBox::indicator:checked {
    background: #2196F3;
    border-color: #2196F3;
}
QCheckBox::indicator:hover {
    border: 2px solid #64B5F6;
}
"""

TOOL_RADIO_STYLE = """
QRadioButton {
    spacing: 8px;
    color: #1a1a1a;
    font-size: 13px;
}
QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid #2196F3;
    background: #ffffff;
}
QRadioButton::indicator:checked {
    background: #2196F3;
    border-color: #2196F3;
}
"""

TOOL_TAB_STYLE = """
QTabWidget::pane {
    border: 2px solid rgba(33, 150, 243, 0.3);
    border-radius: 8px;
    background: #ffffff;
}
QTabBar::tab {
    background: #e8e8e8;
    color: #666666;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: bold;
    font-size: 12px;
}
QTabBar::tab:selected {
    background: #2196F3;
    color: #ffffff;
}
QTabBar::tab:hover:!selected {
    background: #d0d0d0;
    color: #1a1a1a;
}
"""

TOOL_TREE_STYLE = """
QTreeWidget {
    background: #ffffff;
    border: 2px solid rgba(33, 150, 243, 0.3);
    border-radius: 8px;
    color: #1a1a1a;
    font-size: 13px;
}
QTreeWidget::item {
    padding: 5px;
    border: none;
}
QTreeWidget::item:selected {
    background: #2196F3;
    color: #ffffff;
}
QTreeWidget::item:hover {
    background: #e3f2fd;
}
QTreeWidget::branch {
    background: transparent;
}
"""

TOOL_PROGRESS_STYLE = """
QProgressBar {
    border: 2px solid rgba(33, 150, 243, 0.3);
    border-radius: 6px;
    background: #e0e0e0;
    text-align: center;
    color: #1a1a1a;
    font-weight: bold;
}
QProgressBar::chunk {
    background: #2196F3;
    border-radius: 4px;
}
"""

TOOL_SLIDER_STYLE = """
QSlider::groove:horizontal {
    height: 8px;
    background: #e0e0e0;
    border-radius: 4px;
}
QSlider::handle:horizontal {
    background: #2196F3;
    width: 18px;
    height: 18px;
    margin: -5px 0;
    border-radius: 9px;
}
QSlider::handle:horizontal:hover {
    background: #1976D2;
}
QSlider::sub-page:horizontal {
    background: #2196F3;
    border-radius: 4px;
}
"""

TOOL_SCROLL_STYLE = """
QScrollBar:vertical {
    background: #f5f5f5;
    width: 12px;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background: #bdbdbd;
    min-height: 30px;
    border-radius: 6px;
}
QScrollBar::handle:vertical:hover {
    background: #9e9e9e;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background: #f5f5f5;
    height: 12px;
    border-radius: 6px;
}
QScrollBar::handle:horizontal {
    background: #bdbdbd;
    min-width: 30px;
    border-radius: 6px;
}
QScrollBar::handle:horizontal:hover {
    background: #9e9e9e;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
"""

TOOL_TOOLTIP_STYLE = """
QToolTip {
    background: #ffffff;
    color: #1a1a1a;
    border: 2px solid #2196F3;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}
"""

TOOL_RADIO_STYLE = """
QRadioButton {
    spacing: 8px;
    color: #1a1a1a;
    font-size: 13px;
}
QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid #2196F3;
    background: #ffffff;
}
QRadioButton::indicator:checked {
    background: #2196F3;
    border-color: #2196F3;
}
"""

TOOL_TOOLBUTTON_STYLE = """
QToolButton {
    padding: 8px 12px;
    border-radius: 6px;
    background: transparent;
    color: #2196F3;
    border: 2px solid rgba(33, 150, 243, 0.3);
}
QToolButton:hover {
    background: #e3f2fd;
    border-color: #2196F3;
}
QToolButton:pressed {
    background: #bbdefb;
}
"""

TOOL_STATUS_SUCCESS = "color: #4CAF50; font-weight: bold;"
TOOL_STATUS_ERROR = "color: #F44336; font-weight: bold;"
TOOL_STATUS_WARNING = "color: #FF9800; font-weight: bold;"
TOOL_STATUS_INFO = "color: #2196F3;"

RESULT_HEADER = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

RESULT_FOOTER = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

def apply_tool_style(widget):
    """为工具窗口应用统一基础样式"""
    widget.setStyleSheet(f"""
        QWidget {{
            font-size: 13px;
            color: #1a1a1a;
            background: #f5f5f5;
        }}
        QLabel {{
            color: #333333;
            font-size: 13px;
        }}
        {TOOL_GROUP_STYLE}
        {TOOL_INPUT_STYLE}
        {TOOL_SPINBOX_STYLE}
        {TOOL_COMBO_STYLE}
        {TOOL_TEXTEDIT_STYLE}
        {TOOL_TABLE_STYLE}
        {TOOL_LIST_STYLE}
        {TOOL_CHECKBOX_STYLE}
        {TOOL_RADIO_STYLE}
        {TOOL_TAB_STYLE}
        {TOOL_TREE_STYLE}
        {TOOL_PROGRESS_STYLE}
        {TOOL_SLIDER_STYLE}
        {TOOL_SCROLL_STYLE}
        {TOOL_TOOLTIP_STYLE}
        {TOOL_TOOLBUTTON_STYLE}
    """)
