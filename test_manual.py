#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')

from PyQt5.QtWidgets import QApplication
app = QApplication([])

from gui.tools.manual_tool import ManualToolWidget

print('Testing manual tool...')
w = ManualToolWidget()
w.load_commands('huawei')
print('Huawei OK')

w.load_commands('ruijie')
print('Ruijie OK')

print('All tests passed!')
