#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NetOps Toolkit - GUI标签页包
"""

from .basic_tab import BasicConfigTab
from .vlan_tab import VLANConfigTab
from .routing_tab import RoutingConfigTab
from .security_tab import SecurityConfigTab

__all__ = [
    "BasicConfigTab",
    "VLANConfigTab",
    "RoutingConfigTab",
    "SecurityConfigTab"
]
