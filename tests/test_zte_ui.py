#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""离屏检查：主窗口可以选择中兴并生成 ZXR10 脚本。"""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication

from gui.main_window import DEVICE_TYPES, MainWindow


class _SilentBox:
    def information(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None


class ZTEWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = MainWindow()
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()

    def test_zhongxing_selection_changes_hints_and_script(self):
        index = DEVICE_TYPES.index("zte")
        self.window.device_combo.setCurrentIndex(index)

        self.assertEqual(self.window.current_device_type, "zte")
        self.assertIn("中兴", self.window.header_label.text())
        self.assertTrue(self.window.brand_hint.isVisible())
        self.assertIn("gei_1/1", self.window.brand_hint.text())
        self.assertEqual(self.window.tabs["basic"].mgmt_interface.text(), "vlan 1")
        self.assertIn("gei_1/1", self.window.tabs["vlan"].interface_input.placeholderText())

        basic = self.window.tabs["basic"]
        basic.hostname_input.setText("ZTE-Lab-01")
        basic.mgmt_ip.setText("192.168.8.1")
        basic.mgmt_gateway.setText("192.168.8.254")

        vlan = self.window.tabs["vlan"]
        vlan.vlan_id_input.setValue(10)
        vlan.vlan_name_input.setText("Users")
        vlan.add_vlan()
        vlan.interface_input.setText("gei_1/1")
        vlan.vlan_type_combo.setCurrentText("access")
        vlan.port_vlan_id.setValue(10)
        vlan.add_interface()

        script = self.window.compose_config()
        self.assertIn("hostname ZTE-Lab-01", script)
        self.assertIn("interface vlan 1\n", script)
        self.assertIn("ip address 192.168.8.1 255.255.255.0", script)
        self.assertIn("ip route 0.0.0.0 0.0.0.0 192.168.8.254", script)
        self.assertIn("vlan 10", script)
        self.assertIn("name Users", script)
        self.assertIn("interface gei_1/1", script)
        self.assertIn("switchport access vlan 10", script)
        self.assertIn("ssh server enable", script)
        self.assertIn("spanning-tree enable", script)
        self.assertIn("lldp enable", script)
        self.assertNotIn("sysname", script)
        self.assertNotIn("stelnet", script)
        self.assertNotIn("interface Vlanif", script)

    def test_generate_button_fills_preview(self):
        import gui.main_window as main_window

        original = main_window.QMessageBox
        main_window.QMessageBox = _SilentBox()
        try:
            self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("zte"))
            self.window.tabs["basic"].hostname_input.setText("ZTE-Preview")
            self.window.generate_config()
        finally:
            main_window.QMessageBox = original

        preview = self.window.preview_text.toPlainText()
        self.assertIn("hostname ZTE-Preview", preview)
        self.assertIn("configure terminal", preview)
        self.window.update_info()
        self.assertIn("行数:", self.window.info_label.text())

    def test_other_brands_keep_existing_command_style(self):
        self.window.tabs["basic"].hostname_input.setText("HW-Core")
        self.window.tabs["basic"].mgmt_ip.setText("10.0.0.1")
        huawei = self.window.compose_config()
        self.assertIn("sysname HW-Core", huawei)
        self.assertIn("interface Vlanif1", huawei)
        self.assertNotIn("configure terminal", huawei)

        self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("h3c"))
        self.window.tabs["basic"].hostname_input.setText("H3C-Core")
        self.window.tabs["basic"].mgmt_ip.setText("10.0.0.2")
        h3c = self.window.compose_config()
        self.assertIn("sysname H3C-Core", h3c)
        self.assertIn("interface Vlan-interface1", h3c)
        self.assertNotIn("interface Vlanif1", h3c)

    def test_bad_hostname_is_reported_without_partial_preview(self):
        import gui.main_window as main_window

        warnings = []

        class _WarnBox:
            def information(self, *args, **kwargs):
                return None

            def warning(self, *args, **kwargs):
                warnings.append(args)

        original = main_window.QMessageBox
        main_window.QMessageBox = _WarnBox()
        try:
            self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("zte"))
            self.window.tabs["basic"].hostname_input.setText("bad\nhost")
            self.window.generate_config()
        finally:
            main_window.QMessageBox = original

        self.assertTrue(warnings)
        self.assertEqual(self.window.preview_text.toPlainText(), "")


if __name__ == "__main__":
    unittest.main()
