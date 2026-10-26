#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""本机浏览器配置生成。只调用 modules 里已有的生成器，不重写命令。"""

from .service import WebInputError, generate_config, list_brands

__all__ = ["WebInputError", "generate_config", "list_brands"]
