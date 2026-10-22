#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置命令速查手册初始化
"""

from .huawei_manual import HUAWEI_COMMANDS, HUAWEI_CASES
from .h3c_manual import H3C_COMMANDS, H3C_CASES
from .zte_manual import ZTE_COMMANDS, ZTE_CASES
from .zte_rosng_manual import ZTE_ROSNG_COMMANDS, ZTE_ROSNG_CASES
from .zte_olt_manual import ZTE_OLT_COMMANDS, ZTE_OLT_CASES
from .dptech_manual import DPTECH_COMMANDS, DPTECH_CASES
from .dptech_lsw_manual import DPTECH_LSW_COMMANDS, DPTECH_LSW_CASES
from .h3c_lb_manual import H3C_LB_COMMANDS, H3C_LB_CASES

__all__ = [
    "HUAWEI_COMMANDS",
    "HUAWEI_CASES",
    "H3C_COMMANDS",
    "H3C_CASES",
    "ZTE_COMMANDS",
    "ZTE_CASES",
    "ZTE_ROSNG_COMMANDS",
    "ZTE_ROSNG_CASES",
    "ZTE_OLT_COMMANDS",
    "ZTE_OLT_CASES",
    "DPTECH_COMMANDS",
    "DPTECH_CASES",
    "DPTECH_LSW_COMMANDS",
    "DPTECH_LSW_CASES",
    "H3C_LB_COMMANDS",
    "H3C_LB_CASES",
]
