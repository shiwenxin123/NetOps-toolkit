#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NetOps Toolkit - 打包脚本
"""

import os
import sys
import shutil
import subprocess


def build_exe():
    """打包为Windows可执行文件"""
    
    print("=" * 60)
    print("NetOps Toolkit - 打包脚本")
    print("=" * 60)
    
    try:
        import PyInstaller
    except ImportError:
        print("正在安装 PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("\n开始打包...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=NetOps Toolkit",
        "--icon=NONE",
        "--clean",
        "main.py"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("打包成功！")
        print("=" * 60)
        
        dist_dir = os.path.join(script_dir, "dist")
        exe_path = os.path.join(dist_dir, "NetOps Toolkit.exe")
        
        if os.path.exists(exe_path):
            print(f"\n可执行文件位置: {exe_path}")
            print(f"文件大小: {os.path.getsize(exe_path) / 1024 / 1024:.2f} MB")
        
        print("\n使用方法:")
        print("1. 双击运行 'NetOps Toolkit.exe'")
        print("2. 在界面中配置各项参数")
        print("3. 点击'生成配置'按钮")
        print("4. 导出或复制配置脚本")
        
    else:
        print("\n打包失败！")
        print("错误信息:")
        print(result.stderr)
        return False
    
    return True


if __name__ == "__main__":
    build_exe()
