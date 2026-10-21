#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""离屏检查：主窗口可以选择中兴 OLT 并生成 C300/C600 脚本。"""

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


class ZTEOLTWindowTests(unittest.TestCase):
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

    def test_olt_choice_is_separate_from_switch_brands(self):
        labels = [self.window.device_combo.itemText(i) for i in range(self.window.device_combo.count())]
        self.assertIn("中兴 OLT (C300/C600)", labels)
        self.assertTrue(any(label == "中兴 (ZTE)" for label in labels))
        self.assertTrue(any("ROSNG" in label for label in labels))
        self.assertIn("zte-olt", DEVICE_TYPES)
        self.assertNotEqual(DEVICE_TYPES.index("zte-olt"), DEVICE_TYPES.index("zte"))
        self.assertNotEqual(DEVICE_TYPES.index("zte-olt"), DEVICE_TYPES.index("zte-rosng"))

    def test_selection_changes_hints_and_script(self):
        self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("zte-olt"))

        self.assertEqual(self.window.current_device_type, "zte-olt")
        self.assertIn("OLT", self.window.header_label.text())
        self.assertTrue(self.window.brand_hint.isVisible())
        hint = self.window.brand_hint.text()
        self.assertIn("gei_1/19/1", hint)
        self.assertIn("gpon-olt_1/1/1", hint)
        self.assertIn("xgei-1/1/1", hint)
        self.assertIn("gpon_olt-1/1/1", hint)
        self.assertIn("C300", hint)
        self.assertIn("C600", hint)
        self.assertEqual(self.window.tabs["basic"].mgmt_interface.text(), "vlan mng1")
        self.assertIn("gpon-olt_1/1/1", self.window.tabs["vlan"].interface_input.placeholderText())

        basic = self.window.tabs["basic"]
        basic.hostname_input.setText("OLT-C300-Lab")
        basic.password_input.setText("LabOnly1")
        basic.username_input.setText("netops")
        basic.user_password_input.setText("Placeholder1")
        basic.mgmt_ip.setText("10.200.0.2")
        basic.mgmt_gateway.setText("10.200.0.1")

        vlan = self.window.tabs["vlan"]
        vlan.vlan_id_input.setValue(100)
        vlan.vlan_name_input.setText("Uplink")
        vlan.add_vlan()
        vlan.interface_input.setText("gei_1/19/1")
        vlan.vlan_type_combo.setCurrentText("trunk")
        vlan.trunk_vlans_input.setText("100")
        vlan.add_interface()
        vlan.interface_input.setText("gpon-olt_1/1/1")
        vlan.vlan_type_combo.setCurrentText("access")
        vlan.port_vlan_id.setValue(100)
        vlan.add_interface()

        routing = self.window.tabs["routing"]
        routing.route_dest.setText("198.51.100.0")
        routing.route_mask.setText("255.255.255.0")
        routing.route_nexthop.setText("10.200.0.1")
        routing.route_preference.setValue(60)
        routing.add_static_route()

        script = self.window.compose_config()
        commands = _executable(script)
        self.assertIn("configure terminal", commands)
        self.assertIn("hostname OLT-C300-Lab", commands)
        self.assertIn("enable secret 0 LabOnly1", commands)
        self.assertIn("ssh server enable", commands)
        self.assertIn("ssh server version 2", commands)
        self.assertIn("interface vlan mng1", commands)
        self.assertIn("ip address 10.200.0.2 255.255.255.0", commands)
        self.assertIn("ip route 0.0.0.0 0.0.0.0 10.200.0.1", commands)
        self.assertIn("switchport mode trunk", commands)
        self.assertIn("switchport vlan 100 tag", commands)
        self.assertIn("interface gpon-olt_1/1/1", commands)
        self.assertIn("名称 Uplink", script)
        self.assertIn("ip route 198.51.100.0 255.255.255.0 10.200.0.1", commands)
        self.assertNotIn("onu 1 type", commands)
        self.assertNotIn("Placeholder1", script)
        self.assertNotIn("Admin@123", script)
        self.assertNotIn("switchport mode access", commands)
        self.assertNotIn("sysname", commands)
        self.assertNotIn("system-user", commands)
        self.assertNotIn("switchvlan-configuration", commands)
        self.assertNotIn("LLDP 未生成", script)
        self.assertNotIn("PoE 未生成", script)
        self.assertNotIn("生成树未生成", script)

    def test_generate_button_fills_preview(self):
        import gui.main_window as main_window

        original = main_window.QMessageBox
        main_window.QMessageBox = _SilentBox()
        try:
            self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("zte-olt"))
            self.window.tabs["basic"].hostname_input.setText("OLT-C300-Preview")
            self.window.generate_config()
        finally:
            main_window.QMessageBox = original

        preview = self.window.preview_text.toPlainText()
        self.assertIn("hostname OLT-C300-Preview", preview)
        self.assertIn("configure terminal", preview)
        self.assertIn("ssh server enable", preview)
        self.assertIn("本地用户 admin", preview)
        self.assertNotIn("Admin@123", preview)
        self.assertNotIn("\nwrite\n", "\n" + _executable(preview) + "\n")
        self.window.update_info()
        self.assertIn("行数:", self.window.info_label.text())

    def test_template_can_be_applied_and_generated(self):
        import gui.main_window as main_window
        from utils.template_manager import TemplateManager

        template = TemplateManager().get_template("C600 带内管理与PON口", "zte-olt")
        original = main_window.QMessageBox
        main_window.QMessageBox = _SilentBox()
        try:
            self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("zte-olt"))
            self.window.apply_template_config({
                "name": template.name,
                "device_type": "zte-olt",
                "config": template.config,
            })
            self.window.generate_config()
        finally:
            main_window.QMessageBox = original

        preview = _executable(self.window.preview_text.toPlainText())
        self.assertIn("hostname OLT-C600", preview)
        self.assertIn("interface vlan100", preview)
        self.assertIn("interface xgei-1/1/1", preview)
        self.assertIn("interface gpon_olt-1/1/1", preview)
        self.assertIn("no shutdown", preview)
        self.assertIn("ip route 198.51.100.0 255.255.255.0 10.1.1.254", preview)
        self.assertNotIn("gpon-olt_", preview)
        self.assertNotIn("Placeholder1", preview)

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
            self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("zte-olt"))
            self.window.tabs["basic"].hostname_input.setText("bad\nhost")
            self.window.generate_config()
        finally:
            main_window.QMessageBox = original

        self.assertTrue(warnings)
        self.assertEqual(self.window.preview_text.toPlainText(), "")

    def test_classic_interface_name_is_reported(self):
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
            self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("zte-olt"))
            vlan = self.window.tabs["vlan"]
            vlan.interface_input.setText("gei_1/1")
            vlan.vlan_type_combo.setCurrentText("access")
            vlan.port_vlan_id.setValue(10)
            vlan.add_interface()
            self.window.generate_config()
        finally:
            main_window.QMessageBox = original

        self.assertTrue(warnings)
        self.assertIn("经典 ZXROS", str(warnings[0]))
        self.assertEqual(self.window.preview_text.toPlainText(), "")

    def test_other_brands_keep_existing_command_style(self):
        self.window.tabs["basic"].hostname_input.setText("HW-Core")
        self.window.tabs["basic"].mgmt_ip.setText("10.0.0.1")
        huawei = self.window.compose_config()
        self.assertIn("sysname HW-Core", huawei)
        self.assertIn("interface Vlanif1", huawei)
        self.assertNotIn("gpon-olt_", huawei)

        self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("zte"))
        self.window.tabs["basic"].hostname_input.setText("ZTE-Core")
        self.window.tabs["basic"].mgmt_ip.setText("10.0.0.3")
        classic = self.window.compose_config()
        self.assertIn("hostname ZTE-Core", classic)
        self.assertIn("interface vlan 1", classic)
        self.assertIn("中兴 OLT", classic)
        self.assertNotIn("gpon-olt_", classic)

        self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("zte-rosng"))
        self.window.tabs["basic"].hostname_input.setText("ZTE-ROSNG-Lab")
        self.window.tabs["basic"].mgmt_ip.setText("10.0.0.4")
        rosng = self.window.compose_config()
        self.assertIn("interface vlan1", rosng)
        self.assertIn("中兴 OLT", rosng)
        self.assertNotIn("gpon_olt-", rosng)

    def test_leaving_olt_restores_huawei_placeholders(self):
        self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("zte-olt"))
        self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("huawei"))
        self.assertFalse(self.window.brand_hint.isVisible())
        self.assertEqual(self.window.tabs["basic"].mgmt_interface.text(), "Vlanif1")
        self.assertIn("GigabitEthernet", self.window.tabs["vlan"].interface_input.placeholderText())

    def test_handbook_lists_olt_section(self):
        widget = ManualToolWidget()
        labels = [widget.device_combo.itemText(i) for i in range(widget.device_combo.count())]
        index = next(i for i, label in enumerate(labels) if "OLT" in label)
        widget.device_combo.setCurrentIndex(index)
        self.app.processEvents()
        self.assertIn("OLT", widget.status_bar.text())
        self.assertGreater(widget.category_tree.topLevelItemCount(), 0)
        case_index = widget.case_combo.findText("C300", Qt.MatchContains)
        self.assertGreaterEqual(case_index, 0)
        widget.case_combo.setCurrentIndex(case_index)
        case_text = widget.case_text.toPlainText()
        self.assertIn("interface vlan mng1", case_text)
        self.assertIn("switchport vlan 100 tag", case_text)
        self.assertIn("gpon-olt_1/1/1", case_text)
        self.assertIn("! ONU 注册未写", case_text)
        self.assertNotIn("gei-0/1/1/1", case_text)
        widget.deleteLater()


if __name__ == "__main__":
    unittest.main()
