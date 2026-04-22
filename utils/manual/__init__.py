#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置命令速查手册初始化
"""

from .huawei_manual import HUAWEI_COMMANDS, HUAWEI_CASES
from .h3c_manual import H3C_COMMANDS, H3C_CASES

__all__ = [
    "HUAWEI_COMMANDS",
    "HUAWEI_CASES",
    "H3C_COMMANDS",
    "H3C_CASES"
]
