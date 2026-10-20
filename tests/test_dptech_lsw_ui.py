#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""离屏检查：主窗口可以选择迪普 LSW 并生成交换机脚本。"""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from gui.main_window import DEVICE_TYPES, MainWindow
from gui.tools.manual_tool import ManualToolWidget


def _executable(text):
    return "\n".join(
        line.strip() for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("!")
    )


class _SilentBox:
    def information(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None


class DPTechLSWWindowTests(unittest.TestCase):
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

    def test_lsw_choice_is_separate_from_firewall(self):
        labels = [self.window.device_combo.itemText(i) for i in range(self.window.device_combo.count())]
        self.assertTrue(any("迪普 LSW" in label for label in labels))
        self.assertTrue(any("FW1000" in label for label in labels))
        self.assertIn("dptech-lsw", DEVICE_TYPES)
        self.assertIn("dptech", DEVICE_TYPES)

    def test_selection_changes_hints_and_script(self):
        self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("dptech-lsw"))

        self.assertEqual(self.window.current_device_type, "dptech-lsw")
        self.assertIn("LSW", self.window.header_label.text())
        self.assertTrue(self.window.brand_hint.isVisible())
        self.assertIn("gige0_1", self.window.brand_hint.text())
        self.assertIn("vlan-if", self.window.brand_hint.text())
        self.assertIn("LSW3600", self.window.brand_hint.text())
        self.assertEqual(self.window.tabs["basic"].mgmt_interface.text(), "vlan-if 1")
        self.assertIn("tengige0_1", self.window.tabs["vlan"].interface_input.placeholderText())

        basic = self.window.tabs["basic"]
        basic.hostname_input.setText("DP-LSW-Lab")
        basic.mgmt_ip.setText("192.168.8.1")
        basic.mgmt_gateway.setText("192.168.8.254")

        vlan = self.window.tabs["vlan"]
        vlan.vlan_id_input.setValue(10)
        vlan.vlan_name_input.setText("Users")
        vlan.add_vlan()
        vlan.interface_input.setText("gige0_1")
        vlan.vlan_type_combo.setCurrentText("access")
        vlan.port_vlan_id.setValue(10)
        vlan.add_interface()

        vlan.interface_input.setText("gige0_24")
        vlan.vlan_type_combo.setCurrentText("trunk")
        vlan.trunk_vlans_input.setText("10 20")
        vlan.add_interface()

        interface = self.window.tabs["interface"]
        interface.trunk_mode.setCurrentText("lacp-dynamic")
        interface.trunk_members.setText("gige0_23,gige0_24")
        interface.trunk_link_type.setCurrentText("trunk")
        interface.trunk_vlans.setText("10 20")
        interface.add_eth_trunk()

        script = self.window.compose_config()
        commands = _executable(script)
        self.assertIn("conf-mode", commands)
        self.assertIn("sysname DP-LSW-Lab", commands)
        self.assertIn("interface vlan-if 1", commands)
        self.assertIn("ip address 192.168.8.1/24", commands)
        self.assertIn("ip route 0.0.0.0/0 vlan-if1 192.168.8.254", commands)
        self.assertIn("vlan 10", commands)
        self.assertIn("名称 Users", script)
        self.assertIn("interface gige0_1", commands)
        self.assertIn("switchport access vlan 10", commands)
        self.assertIn("switchport mode trunk", commands)
        self.assertIn("switchport trunk allowed vlan 10,20", commands)
        self.assertIn("ssh enable", commands)
        self.assertIn("local-user admin password Admin@123 role super", commands)
        self.assertIn("interface bond 1", commands)
        self.assertIn("bond mode dynamic", commands)
        self.assertIn("bond group 1", commands)
        self.assertNotIn("security-policy", commands)
        self.assertNotIn("security-zone", commands)
        self.assertNotIn("hostname ", commands)
        self.assertNotIn("configure terminal", commands)
        self.assertNotIn("interface Vlanif", commands)
        self.assertNotIn("stelnet", commands)

    def test_generate_button_fills_preview(self):
        import gui.main_window as main_window

        original = main_window.QMessageBox
        main_window.QMessageBox = _SilentBox()
        try:
            self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("dptech-lsw"))
            self.window.tabs["basic"].hostname_input.setText("DP-LSW-Preview")
            self.window.generate_config()
        finally:
            main_window.QMessageBox = original

        preview = self.window.preview_text.toPlainText()
        self.assertIn("sysname DP-LSW-Preview", preview)
        self.assertIn("conf-mode", preview)
        self.assertIn("ssh enable", preview)
        self.assertNotIn("security-policy", _executable(preview))
        self.window.update_info()
        self.assertIn("行数:", self.window.info_label.text())

    def test_template_can_be_applied_and_generated(self):
        import gui.main_window as main_window
        from utils.template_manager import TemplateManager

        template = TemplateManager().get_template("汇聚链路聚合", "dptech-lsw")
        original = main_window.QMessageBox
        main_window.QMessageBox = _SilentBox()
        try:
            self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("dptech-lsw"))
            self.window.apply_template_config({
                "name": template.name,
                "device_type": "dptech-lsw",
                "config": template.config,
            })
            self.window.generate_config()
        finally:
            main_window.QMessageBox = original

        preview = _executable(self.window.preview_text.toPlainText())
        self.assertIn("sysname DP-LSW-Agg", preview)
        self.assertIn("switchport access vlan 10", preview)
        self.assertIn("bond mode dynamic", preview)
        self.assertIn("bond group 1", preview)
        self.assertNotIn("security-policy", preview)

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
            self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("dptech-lsw"))
            self.window.tabs["basic"].hostname_input.setText("bad\nhost")
            self.window.generate_config()
        finally:
            main_window.QMessageBox = original

        self.assertTrue(warnings)
        self.assertEqual(self.window.preview_text.toPlainText(), "")

    def test_firewall_path_still_uses_security_policy(self):
        self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("dptech"))
        self.window.tabs["basic"].hostname_input.setText("DP-FW-Lab")
        self.window.tabs["basic"].mgmt_ip.setText("192.168.0.1")
        script = self.window.compose_config()
        self.assertIn("sysname DP-FW-Lab", script)
        self.assertIn("interface meth0_0", script)
        self.assertIn("security-zone Trust", script)
        self.assertNotIn("role super", script)

    def test_other_brands_keep_existing_command_style(self):
        self.window.tabs["basic"].hostname_input.setText("HW-Core")
        self.window.tabs["basic"].mgmt_ip.setText("10.0.0.1")
        huawei = self.window.compose_config()
        self.assertIn("sysname HW-Core", huawei)
        self.assertIn("interface Vlanif1", huawei)
        self.assertNotIn("conf-mode", huawei)

        self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("h3c"))
        self.window.tabs["basic"].hostname_input.setText("H3C-Core")
        self.window.tabs["basic"].mgmt_ip.setText("10.0.0.2")
        h3c = self.window.compose_config()
        self.assertIn("sysname H3C-Core", h3c)
        self.assertIn("interface Vlan-interface1", h3c)

        self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("zte"))
        self.window.tabs["basic"].hostname_input.setText("ZTE-Core")
        self.window.tabs["basic"].mgmt_ip.setText("10.0.0.3")
        zte = self.window.compose_config()
        self.assertIn("hostname ZTE-Core", zte)
        self.assertIn("configure terminal", zte)
        self.assertNotIn("conf-mode", zte)

    def test_leaving_lsw_restores_huawei_placeholders(self):
        self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("dptech-lsw"))
        self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("huawei"))
        self.assertFalse(self.window.brand_hint.isVisible())
        self.assertEqual(self.window.tabs["basic"].mgmt_interface.text(), "Vlanif1")
        self.assertIn("GigabitEthernet", self.window.tabs["vlan"].interface_input.placeholderText())

    def test_handbook_lists_lsw_section(self):
        widget = ManualToolWidget()
        labels = [widget.device_combo.itemText(i) for i in range(widget.device_combo.count())]
        index = next(i for i, label in enumerate(labels) if "LSW" in label)
        widget.device_combo.setCurrentIndex(index)
        self.app.processEvents()
        self.assertIn("LSW", widget.status_bar.text())
        self.assertGreater(widget.category_tree.topLevelItemCount(), 0)
        case_index = widget.case_combo.findText("动态聚合", Qt.MatchContains)
        self.assertGreaterEqual(case_index, 0)
        widget.case_combo.setCurrentIndex(case_index)
        self.assertIn("bond group 1", widget.case_text.toPlainText())
        self.assertNotIn("security-zone", widget.case_text.toPlainText())
        widget.deleteLater()


if __name__ == "__main__":
    unittest.main()
