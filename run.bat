@echo off
chcp 65001 >nul
title NetOps Toolkit v4.0 - 网络运维工具集

echo ========================================
echo NetOps Toolkit v4.0
echo 网络运维工具集
echo ========================================
echo.

cd /d "%~dp0"

python main.py

if %errorlevel% neq 0 (
    echo.
    echo 启动失败，请检查Python环境。
    echo 确保已安装: pip install PyQt5
    echo.
    pause
)
