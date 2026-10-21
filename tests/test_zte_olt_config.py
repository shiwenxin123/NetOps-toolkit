#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""中兴 OLT（C300/C600）配置生成器的冒烟测试。不依赖界面。"""

import inspect
import unittest

import modules.zte_olt_config as olt_module
from modules.zte_config import ZTEConfigError
from modules.zte_olt_config import ZTEOLTConfigError, generate_olt_config
from utils.manual.zte_olt_manual import ZTE_OLT_CASES, ZTE_OLT_COMMANDS
from utils.template_manager import TemplateManager


def _executable(text):
    return [
        line.strip() for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("!")
    ]


class ZTEOLTConfigTests(unittest.TestCase):
    def test_empty_input_returns_blank(self):
        self.assertEqual(generate_olt_config(), "")

    def test_error_is_a_zte_config_error(self):
        self.assertTrue(issubclass(ZTEOLTConfigError, ZTEConfigError))

    def test_generator_does_not_reference_a_shell(self):
        source = inspect.getsource(olt_module)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("os.system", source)
        self.assertNotIn("os.popen", source)

    def test_c300_management_uplink_and_pon_comment(self):
        text = generate_olt_config(
            basic={
                "hostname": "OLT-C300",
                "password": {"value": "LabOnly1", "encrypted": False},
                "user": {"username": "netops", "password": "Placeholder1", "level": 15},
                "mgmt_interface": {
                    "interface": "mng1",
                    "ip_address": "10.200.0.2",
                    "mask": "24",
                    "gateway": "10.200.0.1",
                },
                "enable_ssh": True,
                "ssh_port": 22,
            },
            vlan={
                "vlans": [{"id": 100, "name": "Uplink"}],
                "interfaces": [
                    {"interface": "gei_1/19/1", "type": "trunk", "trunk_vlans": [100, 102, 103, 104], "pvid": 1},
                    {"interface": "xgei_1/10/1", "type": "access", "vlan_id": 200},
                    {"interface": "gpon-olt_1/1/1", "type": "access", "vlan_id": 100},
                    {"interface": "gpon-onu_1/1/1:1", "type": "hybrid", "vlan_id": 100},
                ],
                "stp": {"mode": "rstp", "priority": 4096, "enable": True},
            },
            routing={
                "static_routes": [{
                    "dest_network": "198.51.100.0",
                    "mask": "255.255.255.0",
                    "next_hop": "10.200.0.1",
                    "preference": 20,
                }],
                "ospf": {"process_id": 1, "router_id": "10.200.0.2", "area_id": "0", "networks": []},
            },
        )
        commands = _executable(text)
        self.assertIn("configure terminal", commands)
        self.assertIn("end", commands)
        self.assertIn("hostname OLT-C300", commands)
        self.assertIn("enable secret 0 LabOnly1", commands)
        self.assertIn("ssh server enable", commands)
        self.assertIn("ssh server version 2", commands)
        self.assertIn("ssh server authentication mode local", commands)
        self.assertIn("ssh server authentication type pap", commands)
        self.assertIn("interface vlan mng1", commands)
        self.assertIn("ip address 10.200.0.2 255.255.255.0", commands)
        self.assertIn("ip route 0.0.0.0 0.0.0.0 10.200.0.1", commands)
        self.assertIn("vlan 100", commands)
        self.assertIn("名称 Uplink", text)
        self.assertIn("interface gei_1/19/1", commands)
        self.assertIn("no shutdown", commands)
        self.assertIn("switchport mode trunk", commands)
        self.assertIn("switchport vlan 100,102-104 tag", commands)
        self.assertIn("switchport default vlan 200", commands)
        self.assertNotIn("switchport mode access", commands)
        self.assertIn("interface gpon-olt_1/1/1", commands)
        self.assertIn("interface gpon-onu_1/1/1:1", commands)
        pon = text.split("interface gpon-olt_1/1/1", 1)[1].split("interface gpon-onu", 1)[0]
        pon_commands = "\n".join(_executable(pon))
        self.assertNotIn("no shutdown", pon_commands)
        self.assertNotIn("switchport", pon_commands)
        self.assertIn("onu <编号> type <类型> sn <SN>", pon)
        onu = text.split("interface gpon-onu_1/1/1:1", 1)[1].split("exit", 1)[0]
        self.assertIn("no shutdown", onu)
        self.assertNotIn("switchport", onu)
        self.assertIn("ip route 198.51.100.0 255.255.255.0 10.200.0.1", commands)
        self.assertIn("路由优先级 20", text)
        self.assertIn("OSPF 未生成命令", text)
        self.assertIn("生成树未生成", text)
        self.assertIn("C300/C320", text)
        joined = "\n".join(commands)
        self.assertNotIn("onu 1 type", joined)
        self.assertNotIn("service-port", joined)
        self.assertNotIn("router ospf", joined)
        self.assertNotIn("Placeholder1", text)
        self.assertNotIn("system-user", joined)
        self.assertNotIn("sysname", joined)
        self.assertNotIn("switchvlan-configuration", joined)
        self.assertNotIn("interface vlan100", joined)

    def test_c600_uses_hyphen_names_and_vlan_without_space(self):
        text = generate_olt_config(
            basic={
                "hostname": "OLT-C600",
                "mgmt_interface": {
                    "interface": "vlan 100",
                    "ip_address": "10.1.1.1",
                    "mask": "255.255.255.0",
                    "gateway": "10.1.1.254",
                },
                "enable_ssh": True,
                "ssh_version": 1,
                "ssh_port": 2222,
            },
            vlan={
                "interfaces": [
                    {"interface": "xgei-1/1/1", "type": "hybrid", "vlan_id": 100},
                    {"interface": "gpon_olt-1/3/10", "type": "access", "vlan_id": 100},
                ]
            },
        )
        commands = _executable(text)
        self.assertIn("interface vlan100", commands)
        self.assertNotIn("interface vlan 100", commands)
        self.assertIn("interface xgei-1/1/1", commands)
        self.assertIn("switchport mode hybrid", commands)
        self.assertIn("switchport vlan 100 tag", commands)
        self.assertIn("interface gpon_olt-1/3/10", commands)
        pon = text.split("interface gpon_olt-1/3/10", 1)[1]
        self.assertIn("no shutdown", pon)
        self.assertIn("loid", pon)
        self.assertNotIn("ssh server version 2", commands)
        self.assertIn("SSH 版本 1", text)
        self.assertIn("SSH 端口 2222", text)
        self.assertIn("C600", text.split("configure terminal", 1)[0])
        self.assertNotIn("gpon-olt_", "\n".join(commands))

    def test_c600_out_of_band_port(self):
        commands = _executable(generate_olt_config(basic={
            "hostname": "OLT-OOB",
            "mgmt_interface": {
                "interface": "mgmt_eth",
                "ip_address": "11.1.1.1",
                "mask": "255.255.255.0",
            },
        }))
        self.assertIn("interface mgmt_eth", commands)
        self.assertIn("ip address 11.1.1.1 255.255.255.0", commands)
        self.assertNotIn("interface vlan mng1", commands)

    def test_encrypted_secret_and_disabled_ssh_stay_comments(self):
        text = generate_olt_config(basic={
            "hostname": "OLT-C300",
            "password": {"value": "ciphertext", "encrypted": True},
            "enable_ssh": False,
        })
        commands = _executable(text)
        self.assertNotIn("enable secret", "\n".join(commands))
        self.assertIn("密文", text)
        self.assertNotIn("ssh server enable", commands)
        self.assertIn("SSH 已在界面关闭", text)

    def test_rejected_names_and_mixed_models(self):
        with self.assertRaises(ZTEOLTConfigError) as classic:
            generate_olt_config(vlan={"interfaces": [
                {"interface": "gei_1/1", "type": "access", "vlan_id": 10}
            ]})
        self.assertIn("经典 ZXROS", str(classic.exception))

        with self.assertRaises(ZTEOLTConfigError) as rosng:
            generate_olt_config(vlan={"interfaces": [
                {"interface": "gei-0/1/1/1", "type": "access", "vlan_id": 10}
            ]})
        self.assertIn("ROSNG", str(rosng.exception))

        with self.assertRaises(ZTEOLTConfigError) as mixed:
            generate_olt_config(vlan={"interfaces": [
                {"interface": "gei_1/19/1", "type": "trunk", "trunk_vlans": [10]},
                {"interface": "xgei-1/1/1", "type": "trunk", "trunk_vlans": [10]},
            ]})
        self.assertIn("一份脚本只能选一种", str(mixed.exception))

        with self.assertRaises(ZTEOLTConfigError):
            generate_olt_config(basic={"hostname": "bad\nhost"})

        with self.assertRaises(ZTEOLTConfigError):
            generate_olt_config(basic={"password": {"value": "this-password-is-too-long", "encrypted": False}})

    def test_aggregation_is_comment_only(self):
        text = generate_olt_config(interface={
            "eth_trunks": [{
                "trunk_id": 1,
                "mode": "lacp-static",
                "description": "uplink",
                "member_ports": ["gei_1/19/1", "gei_1/19/2"],
                "port_link_type": "trunk",
                "trunk_vlans": [100, 200],
            }]
        })
        commands = _executable(text)
        self.assertIn("聚合未生成命令", text)
        self.assertIn("gei_1/19/1", text)
        self.assertNotIn("smartgroup 1 mode", "\n".join(commands))
        self.assertNotIn("interface smartgroup1", commands)

    def test_default_stp_lldp_and_log_stay_quiet(self):
        text = generate_olt_config(
            basic={"hostname": "OLT-C300", "log": {"info_center_enable": True, "log_level": "informational"}},
            vlan={"stp": {"mode": "stp", "priority": 32768, "enable": True}},
            interface={"lldp": {"enable": True, "mode": "both", "interval": 30, "holdtime": 120}},
        )
        self.assertIn("hostname OLT-C300", text)
        self.assertNotIn("生成树未生成", text)
        self.assertNotIn("LLDP 未生成", text)
        self.assertNotIn("日志未生成", text)

    def test_builtin_templates_generate_checked_commands(self):
        manager = TemplateManager()
        c300 = manager.get_template("C300 带外管理与上联", "zte-olt")
        self.assertIsNotNone(c300)
        self.assertIn("占位", c300.description)
        c300_text = generate_olt_config(**c300.config)
        c300_commands = _executable(c300_text)
        self.assertIn("hostname OLT-C300", c300_commands)
        self.assertIn("enable secret 0 LabOnly1", c300_commands)
        self.assertIn("interface vlan mng1", c300_commands)
        self.assertIn("switchport vlan 100 tag", c300_commands)
        self.assertIn("interface gpon-olt_1/1/1", c300_commands)
        self.assertIn("名称 Uplink", c300_text)
        self.assertNotIn("Placeholder1", c300_text)
        self.assertNotIn("onu 1 type", "\n".join(c300_commands))

        c600 = manager.get_template("C600 带内管理与PON口", "zte-olt")
        c600_commands = _executable(generate_olt_config(**c600.config))
        self.assertIn("hostname OLT-C600", c600_commands)
        self.assertIn("interface vlan100", c600_commands)
        self.assertIn("interface xgei-1/1/1", c600_commands)
        self.assertIn("interface gpon_olt-1/1/1", c600_commands)
        self.assertIn("ip route 198.51.100.0 255.255.255.0 10.1.1.254", c600_commands)
        self.assertNotIn("interface vlan 100", c600_commands)
        self.assertNotIn("gpon-olt_", c600_commands)

    def test_handbook_cases_use_the_same_commands(self):
        titles = [case["title"] for case in ZTE_OLT_CASES]
        self.assertIn("C300 带外管理与上联", titles)
        self.assertIn("C600 带内管理与 PON 口", titles)
        c300 = next(case for case in ZTE_OLT_CASES if case["title"].startswith("C300"))
        steps = "\n".join(c300["steps"])
        self.assertIn("interface vlan mng1", steps)
        self.assertIn("switchport vlan 100 tag", steps)
        self.assertIn("gpon-olt_1/1/1", steps)
        self.assertIn("! ONU 注册未写", steps)
        self.assertNotIn("\nonu ", "\n" + steps + "\n")
        generated = "\n".join(_executable(generate_olt_config(**TemplateManager().get_template(
            "C300 带外管理与上联", "zte-olt"
        ).config)))
        for step in c300["steps"]:
            if step.startswith("!"):
                continue
            self.assertIn(step.strip(), generated)
        command_names = []
        for group in ZTE_OLT_COMMANDS.values():
            for commands in group.values():
                command_names.extend(item["name"] for item in commands)
        self.assertIn("打开 SSH", command_names)
        self.assertIn("C300 PON 口", command_names)
        self.assertIn("ONU 注册示例", command_names)


if __name__ == "__main__":
    unittest.main()
