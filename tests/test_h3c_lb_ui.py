#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""离屏检查：主窗口可以选择华三负载均衡并生成实服务器脚本。"""

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
        if line.strip() and not line.lstrip().startswith("#")
    )


class _SilentBox:
    def information(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None


class H3CLBWindowTests(unittest.TestCase):
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

    def test_lb_choice_is_separate_from_h3c_switch(self):
        labels = [self.window.device_combo.itemText(i) for i in range(self.window.device_combo.count())]
        self.assertTrue(any("华三负载均衡" in label for label in labels))
        self.assertTrue(any(label.startswith("华三 (H3C)") for label in labels))
        self.assertIn("h3c-lb", DEVICE_TYPES)
        self.assertNotEqual(DEVICE_TYPES.index("h3c-lb"), DEVICE_TYPES.index("h3c"))
        self.assertFalse(self.window.tabs["routing"].slb_group.isVisible())

    def test_selection_shows_slb_form_and_script(self):
        self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("h3c-lb"))
        self.app.processEvents()

        self.assertEqual(self.window.current_device_type, "h3c-lb")
        self.assertIn("负载均衡", self.window.header_label.text())
        self.assertTrue(self.window.brand_hint.isVisible())
        self.assertIn("GigabitEthernet1/0/1", self.window.brand_hint.text())
        self.assertIn("路由配置", self.window.brand_hint.text())
        routing_tab = self.window.tabs["routing"]
        self.assertFalse(routing_tab.slb_group.isHidden())
        self.window.tab_widget.setCurrentWidget(routing_tab)
        self.app.processEvents()
        self.assertTrue(routing_tab.slb_group.isVisible())
        self.assertEqual(self.window.tabs["basic"].mgmt_interface.text(), "GigabitEthernet1/0/1")

        basic = self.window.tabs["basic"]
        basic.hostname_input.setText("H3C-LB-Lab")
        basic.mgmt_ip.setText("192.168.1.1")
        basic.mgmt_gateway.setText("192.168.1.254")

        routing = self.window.tabs["routing"]
        routing.slb_rs_name.setText("rs1")
        routing.slb_rs_ip.setText("192.168.10.11")
        routing.slb_rs_port.setValue(80)
        routing.slb_rs_weight.setValue(150)
        routing.add_real_server()
        routing.slb_vs_name.setText("vs-web")
        routing.slb_vs_type.setCurrentText("tcp")
        routing.slb_vs_ip.setText("192.168.1.80")
        routing.slb_vs_port.setValue(80)
        routing.add_virtual_server()

        script = self.window.compose_config()
        commands = _executable(script)
        self.assertIn("system-view", commands)
        self.assertIn("sysname H3C-LB-Lab", commands)
        self.assertIn("interface GigabitEthernet 1/0/1", commands)
        self.assertIn("ip address 192.168.1.1 255.255.255.0", commands)
        self.assertIn("ip route-static 0.0.0.0 0.0.0.0 192.168.1.254", commands)
        self.assertIn("nqa template icmp icmp1", commands)
        self.assertIn("real-server rs1", commands)
        self.assertIn("weight 150", commands)
        self.assertIn("virtual-server vs-web type tcp", commands)
        self.assertIn("virtual ip address 192.168.1.80", commands)
        self.assertIn("service enable", commands)
        self.assertIn("arp-nd interface GigabitEthernet 1/0/1", commands)
        self.assertNotIn("switchport", commands)
        self.assertNotIn("security-policy", commands)
        self.assertNotIn("local-user", commands)
        self.assertNotIn("Admin@123", script)
        self.assertNotIn("reboot", commands)
        self.assertNotIn("save", commands)

    def test_generate_button_fills_preview(self):
        import gui.main_window as main_window

        original = main_window.QMessageBox
        main_window.QMessageBox = _SilentBox()
        try:
            self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("h3c-lb"))
            self.window.tabs["basic"].hostname_input.setText("H3C-LB-Preview")
            routing = self.window.tabs["routing"]
            routing.slb_rs_name.setText("rs1")
            routing.slb_rs_ip.setText("192.168.10.11")
            routing.add_real_server()
            routing.slb_vs_name.setText("vs-web")
            routing.slb_vs_ip.setText("192.0.2.80")
            routing.add_virtual_server()
            self.window.generate_config()
        finally:
            main_window.QMessageBox = original

        preview = self.window.preview_text.toPlainText()
        self.assertIn("sysname H3C-LB-Preview", preview)
        self.assertIn("system-view", preview)
        self.assertIn("real-server rs1", _executable(preview))
        self.assertNotIn("arp-nd", _executable(preview))
        self.window.update_info()
        self.assertIn("行数:", self.window.info_label.text())

    def test_template_can_be_applied_and_generated(self):
        import gui.main_window as main_window
        from utils.template_manager import TemplateManager

        template = TemplateManager().get_template("Web 服务器负载均衡", "h3c-lb")
        original = main_window.QMessageBox
        main_window.QMessageBox = _SilentBox()
        try:
            self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("h3c-lb"))
            self.window.apply_template_config({
                "name": template.name,
                "device_type": "h3c-lb",
                "config": template.config,
            })
            self.window.generate_config()
        finally:
            main_window.QMessageBox = original

        preview = _executable(self.window.preview_text.toPlainText())
        self.assertIn("sysname H3C-LB-01", preview)
        self.assertIn("real-server rs2", preview)
        self.assertIn("port link-aggregation group 1", preview)
        self.assertIn("ip route-static 198.51.100.0 255.255.255.0 192.168.1.254", preview)
        self.assertNotIn("switchport", preview)

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
            self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("h3c-lb"))
            self.window.tabs["basic"].hostname_input.setText("bad\nhost")
            self.window.generate_config()
        finally:
            main_window.QMessageBox = original

        self.assertTrue(warnings)
        self.assertEqual(self.window.preview_text.toPlainText(), "")

    def test_h3c_switch_path_is_unchanged(self):
        self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("h3c"))
        self.assertFalse(self.window.tabs["routing"].slb_group.isVisible())
        self.window.tabs["basic"].hostname_input.setText("H3C-Core")
        self.window.tabs["basic"].mgmt_ip.setText("10.0.0.2")
        script = self.window.compose_config()
        commands = _executable(script)
        self.assertIn("sysname H3C-Core", commands)
        self.assertIn("interface Vlan-interface1", commands)
        self.assertNotIn("real-server", commands)
        self.assertNotIn("system-view", commands)

    def test_leaving_lb_hides_the_form(self):
        self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("h3c-lb"))
        self.window.device_combo.setCurrentIndex(DEVICE_TYPES.index("huawei"))
        self.assertFalse(self.window.tabs["routing"].slb_group.isVisible())
        self.assertFalse(self.window.brand_hint.isVisible())
        self.assertEqual(self.window.tabs["basic"].mgmt_interface.text(), "Vlanif1")

    def test_handbook_lists_lb_section(self):
        widget = ManualToolWidget()
        labels = [widget.device_combo.itemText(i) for i in range(widget.device_combo.count())]
        index = next(i for i, label in enumerate(labels) if "负载均衡" in label)
        widget.device_combo.setCurrentIndex(index)
        self.app.processEvents()
        self.assertIn("负载均衡", widget.status_bar.text())
        self.assertGreater(widget.category_tree.topLevelItemCount(), 0)
        case_index = widget.case_combo.findText("Web 服务器负载均衡", Qt.MatchContains)
        self.assertGreaterEqual(case_index, 0)
        widget.case_combo.setCurrentIndex(case_index)
        self.assertIn("real-server rs1", widget.case_text.toPlainText())
        self.assertNotIn("switchport", widget.case_text.toPlainText())
        widget.deleteLater()


if __name__ == "__main__":
    unittest.main()
