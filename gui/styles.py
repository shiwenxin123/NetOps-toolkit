#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
交换机配置生成器 - 明亮清爽风格 v4.0
浅色背景 + 蓝色强调色 - 清爽明亮风格
"""

MODERN_STYLE = """
* {
    font-family: "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
}

QMainWindow {
    background: #f0f2f5;
}

QWidget {
    font-size: 13px;
    color: #1a1a1a;
}

QLabel {
    color: #333333;
    font-size: 13px;
}

QGroupBox {
    font-weight: bold;
    font-size: 14px;
    color: #1976D2;
    border: 2px solid rgba(33, 150, 243, 0.35);
    border-radius: 8px;
    margin-top: 15px;
    padding-top: 15px;
    background: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 10px;
    background: #ffffff;
}

QLineEdit {
    padding: 8px 12px;
    border: 2px solid rgba(33, 150, 243, 0.3);
    border-radius: 6px;
    background: #ffffff;
    color: #1a1a1a;
    font-size: 13px;
    selection-background-color: #2196F3;
    selection-color: #ffffff;
}

QLineEdit:focus {
    border: 2px solid #2196F3;
    background: #ffffff;
}

QLineEdit:disabled {
    background: #f5f5f5;
    border-color: #e0e0e0;
    color: #9e9e9e;
}

QSpinBox, QDoubleSpinBox {
    padding: 6px 12px;
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
    width: 20px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
    background: #1976D2;
}

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
    width: 30px;
    background: transparent;
}

QComboBox::down-arrow {
    image: none;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 8px solid #2196F3;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background: #ffffff;
    border: 2px solid #2196F3;
    selection-background-color: #2196F3;
    selection-color: #ffffff;
    color: #1a1a1a;
    outline: none;
}

QPushButton {
    padding: 10px 25px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 13px;
    border: none;
    color: #ffffff;
}

QPushButton:hover {
    opacity: 0.9;
}

QPushButton:pressed {
    opacity: 0.8;
}

QPushButton#primaryButton {
    background: #2196F3;
    color: #ffffff;
}

QPushButton#primaryButton:hover {
    background: #1976D2;
}

QPushButton#secondaryButton {
    background: #64B5F6;
    color: #ffffff;
}

QPushButton#secondaryButton:hover {
    background: #42A5F5;
}

QPushButton#warningButton {
    background: #FF9800;
    color: #ffffff;
}

QPushButton#warningButton:hover {
    background: #F57C00;
}

QPushButton#dangerButton {
    background: #F44336;
    color: #ffffff;
}

QPushButton#dangerButton:hover {
    background: #D32F2F;
}

QPushButton#ghostButton {
    background: transparent;
    border: 2px solid #2196F3;
    color: #2196F3;
}

QPushButton#ghostButton:hover {
    background: rgba(33, 150, 243, 0.1);
    border: 2px solid #2196F3;
}

QListWidget {
    border: 2px solid rgba(33, 150, 243, 0.3);
    border-radius: 8px;
    background: #ffffff;
    outline: none;
}

QListWidget::item {
    padding: 8px 12px;
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

QCheckBox {
    spacing: 10px;
    color: #1a1a1a;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
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

QRadioButton {
    spacing: 10px;
    color: #1a1a1a;
}

QRadioButton::indicator {
    width: 20px;
    height: 20px;
    border-radius: 10px;
    border: 2px solid #2196F3;
    background: #ffffff;
}

QRadioButton::indicator:checked {
    background: #2196F3;
    border-color: #2196F3;
}

QTabWidget::pane {
    border: 2px solid rgba(33, 150, 243, 0.3);
    border-radius: 8px;
    background: #ffffff;
}

QTabBar::tab {
    background: #e8e8e8;
    color: #666666;
    padding: 12px 25px;
    margin-right: 3px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: bold;
    font-size: 13px;
}

QTabBar::tab:selected {
    background: #2196F3;
    color: #ffffff;
}

QTabBar::tab:hover:!selected {
    background: #d0d0d0;
    color: #1a1a1a;
}

QSplitter::handle {
    background: #2196F3;
}

QSplitter::handle:hover {
    background: #64B5F6;
}

QScrollBar:vertical {
    border: none;
    background: #f5f5f5;
    width: 14px;
    margin: 0px;
    border-radius: 7px;
}

QScrollBar::handle:vertical {
    background: #bdbdbd;
    min-height: 30px;
    border-radius: 7px;
}

QScrollBar::handle:vertical:hover {
    background: #9e9e9e;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: #f5f5f5;
    height: 14px;
    margin: 0px;
    border-radius: 7px;
}

QScrollBar::handle:horizontal {
    background: #bdbdbd;
    min-width: 30px;
    border-radius: 7px;
}

QScrollBar::handle:horizontal:hover {
    background: #9e9e9e;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QTableWidget, QTableView {
    gridline-color: #e0e0e0;
    border: 2px solid rgba(33, 150, 243, 0.3);
    border-radius: 8px;
    background: #ffffff;
    selection-background-color: #2196F3;
    selection-color: #ffffff;
    color: #1a1a1a;
}

QTableWidget::item, QTableView::item {
    padding: 8px;
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
    padding: 10px;
    border: none;
    border-bottom: 2px solid #2196F3;
    font-weight: bold;
    font-size: 13px;
}

QHeaderView::section:first {
    border-top-left-radius: 8px;
}

QHeaderView::section:last {
    border-top-right-radius: 8px;
}

QProgressBar {
    border: 2px solid rgba(33, 150, 243, 0.3);
    border-radius: 8px;
    text-align: center;
    background: #e0e0e0;
    color: #1a1a1a;
    font-weight: bold;
}

QProgressBar::chunk {
    background: #2196F3;
    border-radius: 7px;
}

QStatusBar {
    background: #f5f5f5;
    color: #1976D2;
    font-size: 12px;
    padding: 8px;
    border-top: 1px solid #e0e0e0;
}

QMenuBar {
    background: #ffffff;
    color: #1a1a1a;
    font-weight: bold;
    border-bottom: 1px solid #e0e0e0;
}

QMenuBar::item {
    padding: 10px 18px;
    background: transparent;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background: #2196F3;
    color: #ffffff;
}

QMenuBar::item:hover:!selected {
    background: #e3f2fd;
    color: #1a1a1a;
}

QMenu {
    background: #ffffff;
    border: 2px solid #2196F3;
    border-radius: 8px;
    padding: 5px;
}

QMenu::item {
    padding: 10px 35px;
}

QMenu::item:selected {
    background: #2196F3;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background: #e0e0e0;
    margin: 5px 10px;
}

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

QToolTip {
    background: #ffffff;
    color: #1a1a1a;
    border: 2px solid #2196F3;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}
"""

TOOLTIP_STYLE = """
QToolTip {
    background: #ffffff;
    color: #1a1a1a;
    border: 2px solid #2196F3;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}
"""

DIALOG_STYLE = """
QDialog {
    background: #f5f5f5;
}
"""

LABEL_STYLE = "color: #1976D2; font-weight: bold;"
SECONDARY_LABEL_STYLE = "color: #666666;"
SUCCESS_STYLE = "color: #4CAF50; font-weight: bold;"
ERROR_STYLE = "color: #F44336; font-weight: bold;"
WARNING_STYLE = "color: #FF9800; font-weight: bold;"
INFO_STYLE = "color: #2196F3;"
