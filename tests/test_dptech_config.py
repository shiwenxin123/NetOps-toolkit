#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""迪普 FW1000 配置生成器的冒烟测试。不依赖界面。"""

import unittest

from modules import generate_firewall_config, generate_switch_config
from modules.dptech_config import DPTechConfigError
from utils.template_manager import TemplateManager


def _executable(text):
    return [
        line for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("!")
    ]


class DPTechConfigTests(unittest.TestCase):
    def test_empty_input_returns_blank(self):
        self.assertEqual(generate_firewall_config(), "")

    def test_core_sections_use_fw1000_commands(self):
        text = generate_firewall_config(
            basic={
                "hostname": "DP-FW-01",
                "password": {"value": "Enable1", "encrypted": False},
                "user": {"username": "netops", "password": "Netops1", "level": 15, "encrypted": False},
                "mgmt_interface": {
                    "interface": "Vlanif1",
                    "ip_address": "192.168.1.1",
                    "mask": "255.255.255.0",
                    "gateway": "192.168.1.254",
                },
                "enable_ssh": True,
                "ssh_port": 22,
                "ntp": {"servers": [{"ip": "10.0.0.100", "prefer": True}], "timezone": "UTC+8"},
                "snmp": {
                    "version": "v2c",
                    "community_read": "public",
                    "sys_location": "Lab A",
                    "trap_enable": True,
                    "trap_host": "10.0.0.9",
                },
                "log": {"info_center_enable": True, "host": "10.0.0.200", "log_level": "informational"},
                "dns": {"servers": ["223.5.5.5", "223.6.6.6"], "domain": "example.com"},
            },
            vlan={
                "vlans": [{"id": 10, "name": "Office"}, {"id": 20, "name": "Server"}],
                "interfaces": [
                    {"interface": "gige0_1", "type": "access", "vlan_id": 10},
                    {"interface": "gige0_24", "type": "trunk", "trunk_vlans": [10, 20], "pvid": 1},
                    {"interface": "gige0_2", "type": "hybrid", "vlan_id": 20},
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
                    "dest_network": "10.2.0.0",
                    "mask": "255.255.0.0",
                    "next_hop": "10.1.1.2",
                    "preference": 60,
                }],
                "ospf": {
                    "process_id": 1,
                    "router_id": "1.1.1.1",
                    "area_id": "0",
                    "networks": [{"address": "10.0.0.0", "mask": "0.0.0.255"}],
                },
            },
            security={
                "acls": [
                    {
                        "number": 10,
                        "type": "standard",
                        "rules": [{
                            "id": 5,
                            "action": "permit",
                            "source": "192.168.1.0",
                            "source_wildcard": "0.0.0.255",
                        }],
                    },
                    {
                        "number": 100,
                        "type": "extended",
                        "description": "web",
                        "rules": [{
                            "id": 10,
                            "action": "permit",
                            "protocol": "tcp",
                            "source": "any",
                            "destination": "192.168.10.10",
                            "destination_wildcard": "0.0.0.0",
                            "dest_port": "80",
                        }],
                    },
                ],
                "arp_inspection": {"vlans": [10], "trusted_ports": ["gige0_24"]},
                "storm_controls": [{"interface": "gige0_1", "broadcast": 1000, "multicast": 500}],
            },
            interface={
                "eth_trunks": [{
                    "trunk_id": 1,
                    "mode": "lacp-dynamic",
                    "description": "uplink",
                    "member_ports": ["gige0_5", "gige0_6"],
                    "port_link_type": "trunk",
                    "trunk_vlans": [10, 20],
                }],
                "lldp": {"enable": True, "mode": "both", "interval": 30, "holdtime": 120},
            },
        )

        commands = "\n".join(_executable(text))
        self.assertIn("\nconf-mode\n", text)
        self.assertLess(text.index("\nconf-mode\n"), text.index("\nclock timezone GMT 8\n"))
        self.assertIn("sysname DP-FW-01", commands)
        self.assertNotIn("\nhostname ", text)
        self.assertNotIn("configure terminal", commands)
        self.assertNotIn("stelnet", commands)
        self.assertIn("password conf-mode Enable1", commands)
        self.assertIn("local-user netops password plain-text-password Netops1", commands)
        self.assertIn("ssh enable", commands)
        self.assertNotIn("ssh port", commands)
        self.assertIn("interface vlan-if 1\n", text)
        self.assertIn("ip address 192.168.1.1/24", commands)
        self.assertNotIn("interface Vlanif", commands)
        self.assertIn("ip route 0.0.0.0/0 vlan-if1 192.168.1.254", commands)
        self.assertIn("ntp server 10.0.0.100 prefer", commands)
        self.assertIn("snmp-agent version 2c", commands)
        self.assertIn("snmp-agent community public ro", commands)
        self.assertIn("snmp-agent location Lab A", commands)
        self.assertIn("snmp-agent trap target-host address 10.0.0.9 target-port 162", commands)
        self.assertIn("logging security-policy enable", commands)
        self.assertIn("logging security-policy host 10.0.0.200 port 514", commands)
        self.assertIn("ip name-server 223.5.5.5 223.6.6.6", commands)
        self.assertIn("域名 example.com", text)
        self.assertNotIn("ip domain-name", commands)
        self.assertIn("vlan 10", commands)
        self.assertIn("名称 Office", text)
        self.assertNotIn("\n name Office", text)
        self.assertIn("switchport access vlan 10", commands)
        self.assertIn("switchport trunk allowed vlan 10,20", commands)
        self.assertIn("switchport trunk native vlan 1", commands)
        self.assertIn("interface vlan-if 10", commands)
        self.assertIn("description Office GW", commands)
        self.assertIn("ip address 192.168.10.1/24", commands)
        self.assertNotIn("spanning-tree", commands)
        self.assertIn("生成树未写入", text)
        self.assertIn("ip route 10.2.0.0/16 10.1.1.2", commands)
        self.assertNotIn("router ospf", commands)
        self.assertIn("OSPF", text)
        self.assertIn("address-object a10s5 192.168.1.0/24", commands)
        self.assertIn("address-object a100d10 192.168.10.10/32", commands)
        self.assertIn("service-object s100p10 protocol tcp src-port 0 to 65535 dst-port 80", commands)
        self.assertIn("security-policy pf100r10 src-zone any dst-zone any action permit", commands)
        self.assertNotIn("acl ", commands)
        self.assertIn("arp source-suppression enable", commands)
        self.assertNotIn("storm-control", commands)
        self.assertIn("风暴抑制未生成", text)
        self.assertIn("interface bond 1", commands)
        self.assertIn("bond mode dynamic", commands)
        self.assertIn("bond group 1", commands)
        self.assertIn("security-zone Trust", commands)
        self.assertIn("interface gige0_1", commands)
        self.assertIn("interface bond1", commands)
        self.assertLess(text.index("interface gige0_1"), text.index("security-zone Trust"))
        self.assertNotIn("lldp ", commands)
        self.assertIn("end", commands)
        self.assertIn("write file", text)
        for line in _executable(text):
            self.assertNotIn("untag", line)

    def test_manual_aggregation_is_not_invented(self):
        text = generate_firewall_config(interface={
            "eth_trunks": [{
                "trunk_id": 2,
                "mode": "manual",
                "member_ports": ["gige0_3"],
                "port_link_type": "access",
                "native_vlan": 10,
            }]
        })
        commands = "\n".join(_executable(text))
        self.assertIn("interface bond 2", commands)
        self.assertIn("switchport access vlan 10", commands)
        self.assertIn("bond group 2", commands)
        self.assertNotIn("bond mode manual", commands)
        self.assertNotIn("bond mode on", commands)
        self.assertIn("bond mode ?", text)

    def test_ssh_port_and_banner(self):
        text = generate_firewall_config(basic={
            "enable_ssh": True,
            "ssh_port": 830,
            "banner": {"login": "line1\nline2"},
        })
        self.assertIn("ssh enable", text)
        self.assertIn("ssh port 830", text)
        self.assertIn("banner motd #", text)
        self.assertIn("line1\nline2", text)

    def test_encrypted_admin_and_rejected_conf_mode_cipher(self):
        text = generate_firewall_config(basic={
            "password": {"value": "Cipher1", "encrypted": True},
            "user": {"username": "admin", "password": "Cipher2", "level": 3, "encrypted": True},
        })
        commands = "\n".join(_executable(text))
        self.assertNotIn("password conf-mode", commands)
        self.assertIn("密文没有写入", text)
        self.assertIn("password encrypted-password Cipher2", commands)

    def test_newline_in_hostname_is_rejected(self):
        with self.assertRaises(DPTechConfigError):
            generate_firewall_config(basic={"hostname": "ok\nsysname injected"})

    def test_chinese_hostname_is_rejected(self):
        with self.assertRaises(DPTechConfigError):
            generate_firewall_config(basic={"hostname": "核心防火墙"})

    def test_unknown_interface_is_rejected(self):
        with self.assertRaises(DPTechConfigError):
            generate_firewall_config(basic={
                "mgmt_interface": {
                    "interface": "GigabitEthernet0/0/1",
                    "ip_address": "10.0.0.1",
                    "mask": "255.255.255.0",
                }
            })

    def test_h3c_vlan_interface_alias(self):
        text = generate_firewall_config(basic={
            "mgmt_interface": {
                "interface": "Vlan-interface20",
                "ip_address": "10.20.0.1",
                "mask": "255.255.255.0",
            }
        })
        self.assertIn("interface vlan-if 20", text)
        self.assertIn("ip address 10.20.0.1/24", text)
        self.assertIn("interface vlan-if20", text)

    def test_builtin_template_generates_fw1000_script(self):
        manager = TemplateManager()
        template = manager.get_template("三层防火墙基础配置", "dptech")
        self.assertIsNotNone(template)
        config = template.config
        text = generate_firewall_config(
            basic=config.get("basic"),
            vlan=config.get("vlan"),
            routing=config.get("routing"),
            security=config.get("security"),
            interface=config.get("interface"),
        )
        self.assertIn("sysname DP-FW-01", text)
        self.assertIn("interface meth0_0", text)
        self.assertIn("ssh enable", text)
        self.assertIn("security-zone Trust", text)

    def test_zte_export_is_unchanged(self):
        text = generate_switch_config(basic={"hostname": "ZTE-Core"})
        self.assertIn("hostname ZTE-Core", text)
        self.assertIn("configure terminal", text)
        self.assertNotIn("conf-mode", text)


if __name__ == "__main__":
    unittest.main()
