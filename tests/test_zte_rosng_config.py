#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""中兴 ZXR10 ROSNG 配置生成器的冒烟测试。不依赖界面。"""

import inspect
import unittest

import modules.zte_rosng_config as rosng_module
from modules.zte_config import ZTEConfigError, generate_switch_config
from modules.zte_rosng_config import ZTEROSNGConfigError, generate_rosng_config
from utils.manual.zte_rosng_manual import ZTE_ROSNG_CASES, ZTE_ROSNG_COMMANDS
from utils.template_manager import TemplateManager


def _executable(text):
    return [
        line.strip() for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("!")
    ]


class ZTEROSNGConfigTests(unittest.TestCase):
    def test_empty_input_returns_blank(self):
        self.assertEqual(generate_rosng_config(), "")

    def test_error_is_a_zte_config_error(self):
        self.assertTrue(issubclass(ZTEROSNGConfigError, ZTEConfigError))

    def test_generator_does_not_reference_a_shell(self):
        source = inspect.getsource(rosng_module)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("os.system", source)
        self.assertNotIn("os.popen", source)

    def test_access_trunk_ssh_and_static_route(self):
        text = generate_rosng_config(
            basic={
                "hostname": "ZTE-ROSNG-01",
                "password": {"value": "Enable1", "encrypted": False},
                "user": {"username": "netops", "password": "Placeholder1", "level": 15},
                "mgmt_interface": {
                    "interface": "Vlanif1",
                    "ip_address": "192.168.1.1",
                    "mask": "255.255.255.0",
                    "gateway": "192.168.1.254",
                },
                "enable_ssh": True,
                "ssh_port": 22,
                "banner": {"login": "Lab only"},
            },
            vlan={
                "vlans": [{"id": 10, "name": "Office"}, {"id": 20, "name": "Server"}],
                "interfaces": [
                    {"interface": "gei-0/1/1/1", "type": "access", "vlan_id": 10},
                    {"interface": "xgei-0/1/1/24", "type": "trunk", "trunk_vlans": [10, 20, 21], "pvid": 1},
                    {"interface": "gei-0/1/1/2", "type": "hybrid", "vlan_id": 20},
                ],
                "vlanifs": [{
                    "vlan_id": 10,
                    "ip_address": "192.168.10.1",
                    "mask": "255.255.255.0",
                    "description": "Office GW",
                }],
                "stp": {"mode": "rstp", "priority": 4096, "enable": True},
            },
            routing={
                "static_routes": [{
                    "dest_network": "198.51.100.0",
                    "mask": "255.255.255.0",
                    "next_hop": "192.0.2.1",
                    "preference": 20,
                }],
                "ospf": {
                    "process_id": 1,
                    "router_id": "192.0.2.10",
                    "area_id": "0",
                    "networks": [{"address": "192.0.2.0", "mask": "0.0.0.255"}],
                },
            },
            security={
                "acls": [{
                    "number": 100,
                    "type": "extended",
                    "description": "web",
                    "rules": [{"id": 10, "action": "permit", "protocol": "tcp"}],
                }]
            },
        )
        commands = _executable(text)
        joined = "\n".join(commands)
        self.assertIn("configure terminal", commands)
        self.assertEqual(commands[-1], "end")
        self.assertLess(text.index("\nconfigure terminal\n"), text.index("\nhostname ZTE-ROSNG-01\n"))
        self.assertIn("hostname ZTE-ROSNG-01", commands)
        self.assertNotIn("sysname ZTE-ROSNG-01", joined)
        self.assertNotIn("enable secret", joined)
        self.assertIn("管理密码未写入", text)
        self.assertNotIn("Enable1", text)
        self.assertIn("system-user", commands)
        self.assertIn("user-name netops", commands)
        self.assertIn("password Placeholder1", commands)
        self.assertIn("bind authentication-template 1", commands)
        self.assertIn("bind authorization-template 1", commands)
        self.assertIn("bind aaa-authentication-template 2001", commands)
        self.assertIn("local-privilege-level 15", commands)
        self.assertIn("aaa-authentication-type local", commands)
        self.assertIn("aaa-authorization-type none", commands)
        self.assertIn("ssh server enable", commands)
        self.assertNotIn("ssh server enable listen", joined)
        self.assertIn("banner incoming #", commands)
        self.assertIn("Lab only", commands)
        self.assertIn("interface vlan1", commands)
        self.assertNotIn("interface vlan 1", joined)
        self.assertNotIn("interface Vlanif1", joined)
        self.assertIn("ip address 192.168.1.1 255.255.255.0", commands)
        self.assertIn("ip route 0.0.0.0 0.0.0.0 vlan1 192.168.1.254", commands)
        self.assertIn("vlan 10", commands)
        self.assertIn("vlan 20", commands)
        self.assertLess(joined.index("vlan 10"), joined.index("vlan 20"))
        self.assertIn("名称 Office", text)
        self.assertNotIn("name Office", joined)
        self.assertIn("interface gei-0/1/1/1", commands)
        self.assertIn("no shutdown", commands)
        self.assertIn("switchvlan-configuration", commands)
        self.assertIn("switchport mode access", commands)
        self.assertIn("switchport access vlan 10", commands)
        self.assertIn("switchport mode trunk", commands)
        self.assertIn("switchport trunk vlan 10", commands)
        self.assertIn("switchport trunk vlan 20-21", commands)
        self.assertNotIn("switchport trunk vlan 10,20", joined)
        self.assertIn("switchport trunk native vlan 1", commands)
        self.assertIn("switchport hybrid vlan 20 untag", commands)
        self.assertIn("interface vlan10", commands)
        self.assertIn("ip address 192.168.10.1 255.255.255.0", commands)
        self.assertIn("描述 Office GW", text)
        self.assertNotIn("description Office GW", joined)
        self.assertIn("生成树未生成命令", text)
        self.assertNotIn("spanning-tree", joined)
        self.assertIn("ip route 198.51.100.0 255.255.255.0 192.0.2.1 20", commands)
        self.assertIn("OSPF 未生成命令", text)
        self.assertNotIn("router ospf", joined)
        self.assertIn("ACL 100", text)
        self.assertNotIn("acl extend", joined)
        self.assertNotIn("acl standard", joined)
        self.assertIn("ROSNG", text)
        self.assertIn("5960/9900", text)
        self.assertIn("5900E", text)
        self.assertNotIn("\nwrite\n", "\n" + joined + "\n")
        self.assertIn("write", text)

    def test_link_aggregation_modes(self):
        lacp = generate_rosng_config(
            interface={
                "eth_trunks": [{
                    "trunk_id": 1,
                    "mode": "lacp-static",
                    "description": "uplink",
                    "member_ports": ["gei-0/1/1/23", "gei-0/1/1/24"],
                    "port_link_type": "trunk",
                    "trunk_vlans": [10, 12],
                }],
                "lldp": {"enable": True, "mode": "both", "interval": 30, "holdtime": 120},
                "poe": {"enable": True, "max_power": 74000, "interfaces": []},
            }
        )
        commands = _executable(lacp)
        self.assertIn("interface smartgroup1", commands)
        self.assertIn("switch attribute enable", commands)
        self.assertIn("lacp", commands)
        self.assertIn("lacp mode 802.3ad", commands)
        self.assertIn("smartgroup 1 mode active", commands)
        self.assertIn("switchport trunk vlan 10", commands)
        self.assertIn("switchport trunk vlan 12", commands)
        self.assertIn("界面模式 lacp-static", lacp)
        self.assertIn("描述 uplink", lacp)
        self.assertNotIn("description uplink", "\n".join(commands))
        self.assertNotIn("LLDP 未生成", lacp)
        self.assertNotIn("PoE 未生成", lacp)
        self.assertLess(lacp.index("interface smartgroup1"), lacp.index("switchport mode trunk"))

        manual = generate_rosng_config(
            interface={
                "eth_trunks": [{
                    "trunk_id": 2,
                    "mode": "manual",
                    "member_ports": ["xgei-0/1/1/1", "xgei-0/1/1/2"],
                    "port_link_type": "access",
                    "native_vlan": 10,
                }]
            }
        )
        manual_commands = "\n".join(_executable(manual))
        self.assertIn("interface smartgroup2", manual_commands)
        self.assertIn("lacp mode on", manual_commands)
        self.assertIn("smartgroup 2 mode on", manual_commands)
        self.assertNotIn("802.3ad", manual_commands)
        self.assertIn("switchport access vlan 10", manual_commands)

    def test_ssh_listen_port_follows_the_manual(self):
        high = _executable(generate_rosng_config(basic={"enable_ssh": True, "ssh_port": 50000}))
        self.assertIn("ssh server enable listen 50000", high)

        odd = generate_rosng_config(basic={"enable_ssh": True, "ssh_port": 2222})
        odd_commands = _executable(odd)
        self.assertIn("ssh server enable", odd_commands)
        self.assertNotIn("ssh server enable listen 2222", odd_commands)
        self.assertIn("2222", odd)

        disabled = _executable(generate_rosng_config(basic={"enable_ssh": False}))
        self.assertIn("ssh server disable", disabled)
        self.assertNotIn("ssh server enable", disabled)

    def test_direct_route_keeps_distance_in_a_comment(self):
        text = generate_rosng_config(routing={
            "static_routes": [{
                "dest_network": "198.51.100.0",
                "mask": "24",
                "next_hop": "192.0.2.1",
                "interface": "vlan 10",
                "preference": 20,
            }]
        })
        commands = _executable(text)
        self.assertIn("ip route 198.51.100.0 255.255.255.0 vlan10 192.0.2.1", commands)
        self.assertNotIn("ip route 198.51.100.0 255.255.255.0 vlan10 192.0.2.1 20", commands)
        self.assertIn("管理距离 20", text)

    def test_route_without_nexthop_is_only_a_comment(self):
        text = generate_rosng_config(routing={
            "static_routes": [{
                "dest_network": "198.51.100.0",
                "mask": "255.255.255.0",
                "interface": "vlan10",
            }]
        })
        self.assertNotIn("ip route 198.51.100.0", "\n".join(_executable(text)))
        self.assertIn("必须有下一跳", text)

    def test_encrypted_user_password_uses_the_manual_keyword(self):
        cipher = "1f5c880d9ead3446d94f7c409209244d764ce5f3fe9c010bf6b033b34d3e4d30"
        text = generate_rosng_config(basic={
            "user": {"username": "netops", "password": cipher, "encrypted": True, "level": 3}
        })
        commands = _executable(text)
        self.assertIn(f"password encrypted {cipher}", commands)
        self.assertIn("local-privilege-level 3", commands)

        with self.assertRaises(ZTEROSNGConfigError):
            generate_rosng_config(basic={
                "user": {"username": "netops", "password": "Placeholder1", "encrypted": True}
            })

    def test_classic_interface_name_is_rejected(self):
        with self.assertRaises(ZTEROSNGConfigError) as caught:
            generate_rosng_config(vlan={
                "interfaces": [{"interface": "gei_1/1", "type": "access", "vlan_id": 10}]
            })
        self.assertIn("经典 ZXROS", str(caught.exception))

    def test_newline_in_hostname_is_rejected(self):
        with self.assertRaises(ZTEROSNGConfigError):
            generate_rosng_config(basic={"hostname": "bad\nhost"})

    def test_too_many_members_is_rejected(self):
        members = [f"gei-0/1/1/{index}" for index in range(1, 10)]
        with self.assertRaises(ZTEROSNGConfigError):
            generate_rosng_config(interface={
                "eth_trunks": [{"trunk_id": 1, "mode": "manual", "member_ports": members}]
            })

    def test_default_stp_lldp_and_log_stay_quiet(self):
        text = generate_rosng_config(
            basic={"hostname": "ZTE-ROSNG-01", "log": {"info_center_enable": True, "log_level": "informational"}},
            vlan={"stp": {"mode": "stp", "priority": 32768, "enable": True}},
            interface={"lldp": {"enable": True, "mode": "both", "interval": 30, "holdtime": 120}},
        )
        self.assertIn("hostname ZTE-ROSNG-01", text)
        self.assertNotIn("生成树未生成", text)
        self.assertNotIn("LLDP 未生成", text)
        self.assertNotIn("日志未生成", text)

    def test_builtin_templates_generate_checked_commands(self):
        manager = TemplateManager()
        access = manager.get_template("接入交换机基础配置", "zte-rosng")
        self.assertIsNotNone(access)
        self.assertIn("占位", access.description)
        access_text = generate_rosng_config(**access.config)
        access_commands = _executable(access_text)
        self.assertIn("hostname ZTE-ROSNG-01", access_commands)
        self.assertIn("password Placeholder1", access_commands)
        self.assertIn("switchport access vlan 10", access_commands)
        self.assertIn("switchport trunk vlan 10", access_commands)
        self.assertIn("switchport trunk vlan 20", access_commands)
        self.assertIn("interface vlan10", access_commands)
        self.assertIn("名称 Office", access_text)

        uplink = manager.get_template("上联聚合与静态路由", "zte-rosng")
        uplink_commands = _executable(generate_rosng_config(**uplink.config))
        self.assertIn("lacp mode 802.3ad", uplink_commands)
        self.assertIn("smartgroup 1 mode active", uplink_commands)
        self.assertIn("ip route 198.51.100.0 255.255.255.0 192.0.2.1", uplink_commands)

    def test_handbook_cases_use_the_same_commands(self):
        titles = [case["title"] for case in ZTE_ROSNG_CASES]
        self.assertIn("接入 VLAN 与 SSH", titles)
        self.assertIn("聚合上联与静态路由", titles)
        access = next(case for case in ZTE_ROSNG_CASES if "SSH" in case["title"])
        steps = "\n".join(access["steps"])
        self.assertIn("switchvlan-configuration", steps)
        self.assertIn("ssh server enable", steps)
        self.assertIn("Placeholder1", steps)
        self.assertNotIn("gei_1/1", steps)
        self.assertNotIn("enable secret", steps)
        generated = "\n".join(_executable(generate_rosng_config(
            basic={
                "hostname": "ZTE-ROSNG-01",
                "user": {"username": "netops", "password": "Placeholder1", "level": 15},
                "mgmt_interface": {
                    "interface": "vlan1",
                    "ip_address": "192.168.1.1",
                    "mask": "255.255.255.0",
                    "gateway": "192.168.1.254",
                },
                "enable_ssh": True,
            },
            vlan={
                "vlans": [{"id": 10, "name": "Office"}],
                "interfaces": [{"interface": "gei-0/1/1/1", "type": "access", "vlan_id": 10}],
                "vlanifs": [{"vlan_id": 10, "ip_address": "192.168.10.1", "mask": "255.255.255.0"}],
            },
        )))
        for step in access["steps"]:
            if step in ("configure terminal", "end"):
                continue
            self.assertIn(step.strip(), generated)
        command_names = []
        for group in ZTE_ROSNG_COMMANDS.values():
            for commands in group.values():
                command_names.extend(item["name"] for item in commands)
        self.assertIn("SSH", command_names)
        self.assertIn("LACP", command_names)

    def test_classic_generator_is_unchanged(self):
        classic = generate_switch_config(basic={
            "hostname": "ZTE-Core",
            "mgmt_interface": {"interface": "Vlanif1", "ip_address": "192.168.1.1", "mask": "255.255.255.0"},
        })
        self.assertIn("interface vlan 1", classic)
        self.assertIn("hostname ZTE-Core", classic)
        self.assertNotIn("switchvlan-configuration", classic)
        self.assertNotIn("system-user", classic)


if __name__ == "__main__":
    unittest.main()
