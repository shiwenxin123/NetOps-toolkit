#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
对话框模块
"""

from .settings_dialog import SettingsDialog
from .about_dialog import AboutDialog
from .batch_config_dialog import BatchConfigDialog
from .template_dialog import TemplateManagerDialog, SaveTemplateDialog

__all__ = ['SettingsDialog', 'AboutDialog', 'BatchConfigDialog', 'TemplateManagerDialog', 'SaveTemplateDialog']
