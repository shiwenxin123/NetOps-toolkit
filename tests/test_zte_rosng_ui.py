#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""离屏检查：主窗口可以选择中兴 ROSNG 并生成 5960/9900 脚本。"""

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


class ZTEROSNGWindowTests(unittest.TestCase):
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

    def test_rosng_choice_is_separate_from_classic_zte(self):
        labels = [self.window.device_combo.itemText(i) for i in range(self.window.device_combo.count())]
        self.assertTrue(any("ROSNG" in label for label in labels))
        self.assertTrue(any(label == "中兴 (ZTE)" for label in labels))
        self.assertIn("zte-rosng", DEVICE_TYPES)
        self.assertIn("zte", DEVICE_TYPES)
        self.assertNotEqual(DEVICE_TYPES.index("zte-rosng"), DEVICE_TYPES.index("zte"))

    def test_selection_changes_hints_and_script(self):
        self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("zte-rosng"))

        self.assertEqual(self.window.current_device_type, "zte-rosng")
        self.assertIn("ROSNG", self.window.header_label.text())
        self.assertTrue(self.window.brand_hint.isVisible())
        self.assertIn("gei-0/1/1/1", self.window.brand_hint.text())
        self.assertIn("xgei-0/1/1/1", self.window.brand_hint.text())
        self.assertIn("5960", self.window.brand_hint.text())
        self.assertEqual(self.window.tabs["basic"].mgmt_interface.text(), "vlan1")
        self.assertIn("xgei-0/1/1/1", self.window.tabs["vlan"].interface_input.placeholderText())

        basic = self.window.tabs["basic"]
        basic.hostname_input.setText("ZTE-ROSNG-Lab")
        basic.username_input.setText("netops")
        basic.user_password_input.setText("Placeholder1")
        basic.mgmt_ip.setText("192.168.8.1")
        basic.mgmt_gateway.setText("192.168.8.254")

        vlan = self.window.tabs["vlan"]
        vlan.vlan_id_input.setValue(10)
        vlan.vlan_name_input.setText("Users")
        vlan.add_vlan()
        vlan.interface_input.setText("gei-0/1/1/1")
        vlan.vlan_type_combo.setCurrentText("access")
        vlan.port_vlan_id.setValue(10)
        vlan.add_interface()

        vlan.interface_input.setText("gei-0/1/1/24")
        vlan.vlan_type_combo.setCurrentText("trunk")
        vlan.trunk_vlans_input.setText("10 20")
        vlan.add_interface()

        interface = self.window.tabs["interface"]
        interface.trunk_mode.setCurrentText("lacp-static")
        interface.trunk_members.setText("gei-0/1/1/23,gei-0/1/1/24")
        interface.trunk_link_type.setCurrentText("trunk")
        interface.trunk_vlans.setText("10 20")
        interface.add_eth_trunk()

        routing = self.window.tabs["routing"]
        routing.route_dest.setText("198.51.100.0")
        routing.route_mask.setText("255.255.255.0")
        routing.route_nexthop.setText("192.0.2.1")
        routing.route_preference.setValue(1)
        routing.add_static_route()

        script = self.window.compose_config()
        commands = _executable(script)
        self.assertIn("configure terminal", commands)
        self.assertIn("hostname ZTE-ROSNG-Lab", commands)
        self.assertIn("user-name netops", commands)
        self.assertIn("password Placeholder1", commands)
        self.assertIn("ssh server enable", commands)
        self.assertIn("interface vlan1", commands)
        self.assertIn("ip address 192.168.8.1 255.255.255.0", commands)
        self.assertIn("ip route 0.0.0.0 0.0.0.0 vlan1 192.168.8.254", commands)
        self.assertIn("switchvlan-configuration", commands)
        self.assertIn("switchport access vlan 10", commands)
        self.assertIn("switchport trunk vlan 10", commands)
        self.assertIn("switchport trunk vlan 20", commands)
        self.assertIn("名称 Users", script)
        self.assertIn("interface smartgroup1", commands)
        self.assertIn("lacp mode 802.3ad", commands)
        self.assertIn("smartgroup 1 mode active", commands)
        self.assertIn("ip route 198.51.100.0 255.255.255.0 192.0.2.1", commands)
        self.assertNotIn("LLDP 未生成", script)
        self.assertNotIn("PoE 未生成", script)
        self.assertNotIn("生成树未生成", script)
        self.assertNotIn("sysname", commands)
        self.assertNotIn("stelnet", commands)
        self.assertNotIn("interface Vlanif", commands)
        self.assertNotIn("gei_1/1", commands)
        self.assertNotIn("enable secret", commands)

    def test_generate_button_fills_preview(self):
        import gui.main_window as main_window

        original = main_window.QMessageBox
        main_window.QMessageBox = _SilentBox()
        try:
            self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("zte-rosng"))
            self.window.tabs["basic"].hostname_input.setText("ZTE-ROSNG-Preview")
            self.window.generate_config()
        finally:
            main_window.QMessageBox = original

        preview = self.window.preview_text.toPlainText()
        self.assertIn("hostname ZTE-ROSNG-Preview", preview)
        self.assertIn("configure terminal", preview)
        self.assertIn("ssh server enable", preview)
        self.assertIn("system-user", preview)
        self.assertNotIn("\nwrite\n", "\n" + _executable(preview) + "\n")
        self.window.update_info()
        self.assertIn("行数:", self.window.info_label.text())

    def test_template_can_be_applied_and_generated(self):
        import gui.main_window as main_window
        from utils.template_manager import TemplateManager

        template = TemplateManager().get_template("上联聚合与静态路由", "zte-rosng")
        original = main_window.QMessageBox
        main_window.QMessageBox = _SilentBox()
        try:
            self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("zte-rosng"))
            self.window.apply_template_config({
                "name": template.name,
                "device_type": "zte-rosng",
                "config": template.config,
            })
            self.window.generate_config()
        finally:
            main_window.QMessageBox = original

        preview = _executable(self.window.preview_text.toPlainText())
        self.assertIn("hostname ZTE-ROSNG-Agg", preview)
        self.assertIn("lacp mode 802.3ad", preview)
        self.assertIn("smartgroup 1 mode active", preview)
        self.assertIn("ip route 198.51.100.0 255.255.255.0 192.0.2.1", preview)
        self.assertNotIn("gei_1/1", preview)

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
            self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("zte-rosng"))
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
            self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("zte-rosng"))
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
        self.assertNotIn("switchvlan-configuration", huawei)

        self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("zte"))
        self.window.tabs["basic"].hostname_input.setText("ZTE-Core")
        self.window.tabs["basic"].mgmt_ip.setText("10.0.0.3")
        classic = self.window.compose_config()
        self.assertIn("hostname ZTE-Core", classic)
        self.assertIn("interface vlan 1", classic)
        self.assertNotIn("switchvlan-configuration", classic)
        self.assertNotIn("system-user", classic)

        self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("dptech-lsw"))
        self.window.tabs["basic"].hostname_input.setText("DP-LSW-Lab")
        self.window.tabs["basic"].mgmt_ip.setText("192.168.0.1")
        lsw = self.window.compose_config()
        self.assertIn("sysname DP-LSW-Lab", lsw)
        self.assertIn("conf-mode", lsw)
        self.assertNotIn("switchvlan-configuration", lsw)

    def test_leaving_rosng_restores_huawei_placeholders(self):
        self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("zte-rosng"))
        self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("huawei"))
        self.assertFalse(self.window.brand_hint.isVisible())
        self.assertEqual(self.window.tabs["basic"].mgmt_interface.text(), "Vlanif1")
        self.assertIn("GigabitEthernet", self.window.tabs["vlan"].interface_input.placeholderText())

    def test_handbook_lists_rosng_section(self):
        widget = ManualToolWidget()
        labels = [widget.device_combo.itemText(i) for i in range(widget.device_combo.count())]
        index = next(i for i, label in enumerate(labels) if "ROSNG" in label)
        widget.device_combo.setCurrentIndex(index)
        self.app.processEvents()
        self.assertIn("ROSNG", widget.status_bar.text())
        self.assertGreater(widget.category_tree.topLevelItemCount(), 0)
        case_index = widget.case_combo.findText("聚合上联", Qt.MatchContains)
        self.assertGreaterEqual(case_index, 0)
        widget.case_combo.setCurrentIndex(case_index)
        case_text = widget.case_text.toPlainText()
        self.assertIn("lacp mode 802.3ad", case_text)
        self.assertIn("smartgroup 1 mode active", case_text)
        self.assertNotIn("gei_1/1", case_text)
        widget.deleteLater()


if __name__ == "__main__":
    unittest.main()
