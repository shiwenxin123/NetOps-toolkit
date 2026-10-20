#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""迪普 LSW 交换机配置生成器的冒烟测试。不依赖界面。"""

import inspect
import unittest

import modules.dptech_lsw_config as lsw_module
from modules.dptech_config import generate_firewall_config
from modules.dptech_lsw_config import DPTechLSWConfigError, generate_lsw_config
from modules.zte_config import generate_switch_config
from utils.manual.dptech_lsw_manual import DPTECH_LSW_CASES, DPTECH_LSW_COMMANDS
from utils.template_manager import TemplateManager


def _executable(text):
    return [
        line.strip() for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("!")
    ]


class DPTechLSWConfigTests(unittest.TestCase):
    def test_empty_input_returns_blank(self):
        self.assertEqual(generate_lsw_config(), "")

    def test_generator_does_not_reference_a_shell(self):
        source = inspect.getsource(lsw_module)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("os.system", source)
        self.assertNotIn("os.popen", source)

    def test_access_trunk_ssh_and_dynamic_bond(self):
        text = generate_lsw_config(
            basic={
                "hostname": "DP-LSW-01",
                "user": {"username": "netops", "password": "Netops1", "level": 15, "encrypted": False},
                "mgmt_interface": {
                    "interface": "Vlanif1",
                    "ip_address": "192.168.1.1",
                    "mask": "255.255.255.0",
                    "gateway": "192.168.1.254",
                },
                "enable_ssh": True,
                "ssh_port": 22,
            },
            vlan={
                "vlans": [{"id": 10, "name": "Office"}, {"id": 20, "name": "Server"}],
                "interfaces": [
                    {"interface": "gige0_1", "type": "access", "vlan_id": 10},
                    {"interface": "gige0_24", "type": "trunk", "trunk_vlans": [10, 20, 21], "pvid": 1},
                    {"interface": "tengige0_1", "type": "hybrid", "vlan_id": 20},
                ],
                "vlanifs": [{
                    "vlan_id": 10,
                    "ip_address": "192.168.10.1",
                    "mask": "255.255.255.0",
                    "description": "Office GW",
                }],
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
        self.assertIn("conf-mode", commands)
        self.assertLess(text.index("\nconf-mode\n"), text.index("\nsysname DP-LSW-01\n"))
        self.assertEqual(_executable(text)[-1], "exit")
        self.assertIn("sysname DP-LSW-01", commands)
        self.assertNotIn("hostname ", commands)
        self.assertNotIn("configure terminal", commands)
        self.assertNotIn("stelnet", commands)
        self.assertIn("ssh enable", commands)
        self.assertNotIn("ssh port", commands)
        self.assertIn("local-user netops password Netops1 role super", commands)
        self.assertNotIn("plain-text-password", commands)
        self.assertNotIn("password conf-mode", commands)
        self.assertIn("interface vlan-if 1", commands)
        self.assertIn("ip address 192.168.1.1/24", commands)
        self.assertNotIn("interface Vlanif", commands)
        self.assertIn("ip route 0.0.0.0/0 vlan-if1 192.168.1.254", commands)
        self.assertIn("vlan 10", commands)
        self.assertIn("名称 Office", text)
        self.assertNotIn("\n name Office", text)
        self.assertIn("switchport access vlan 10", commands)
        self.assertNotIn("switchport mode access", commands)
        self.assertIn("switchport mode trunk", commands)
        self.assertIn("switchport trunk allowed vlan 10,20-21", commands)
        self.assertIn("switchport trunk native vlan 1", commands)
        self.assertIn("switchport mode hybrid", commands)
        self.assertIn("switchport hybrid allowed vlan 20 untagged", commands)
        self.assertIn("interface vlan-if 10", commands)
        self.assertIn("ip address 192.168.10.1/24", commands)
        self.assertIn("interface tengige0_1", commands)
        self.assertIn("interface bond 1", commands)
        self.assertIn("bond mode dynamic", commands)
        self.assertIn("bond load-sharing mode source-destination-ip", commands)
        self.assertIn("bond group 1", commands)
        self.assertIn("switchport trunk allowed vlan 10,20", commands)
        self.assertNotIn("security-policy", commands)
        self.assertNotIn("security-zone", commands)
        self.assertNotIn("address-object", commands)
        self.assertNotIn("logging security-policy", text)
        self.assertIn("write file", text)
        self.assertNotIn("\nwrite file\n", "\n" + commands + "\n")
        self.assertIn("Save?", text)

    def test_static_bond_and_unverified_lacp_static(self):
        static_text = generate_lsw_config(interface={
            "eth_trunks": [{
                "trunk_id": 2,
                "mode": "manual",
                "member_ports": ["gige0_3"],
                "port_link_type": "access",
                "native_vlan": 10,
            }]
        })
        static_commands = "\n".join(_executable(static_text))
        self.assertIn("interface bond 2", static_commands)
        self.assertIn("bond mode static", static_commands)
        self.assertIn("bond load-sharing mode source-destination-mac", static_commands)
        self.assertIn("switchport access vlan 10", static_commands)
        self.assertIn("bond group 2", static_commands)

        commented = generate_lsw_config(interface={
            "eth_trunks": [{
                "trunk_id": 3,
                "mode": "lacp-static",
                "member_ports": ["gige0_4"],
                "port_link_type": "access",
                "native_vlan": 10,
            }]
        })
        commented_commands = "\n".join(_executable(commented))
        self.assertIn("interface bond 3", commented_commands)
        self.assertIn("bond group 3", commented_commands)
        self.assertNotIn("bond mode", commented_commands)
        self.assertIn("lacp-static", commented)
        self.assertNotIn("bond mode lacp-static", commented)

    def test_stp_rstp_and_mst_do_not_invent_instance_priority(self):
        rstp = "\n".join(_executable(generate_lsw_config(vlan={
            "interfaces": [{"interface": "gige0_1", "type": "access", "vlan_id": 10}],
            "stp": {"mode": "rstp", "priority": 4096, "enable": True},
        })))
        self.assertIn("spanning-tree enable", rstp)
        self.assertIn("spanning-tree mode rstp", rstp)
        self.assertIn("spanning-tree bridge-priority 4096", rstp)
        rstp_text = generate_lsw_config(vlan={
            "interfaces": [{"interface": "gige0_1", "type": "access", "vlan_id": 10}],
            "stp": {"mode": "rstp", "priority": 4096, "enable": True},
        })
        self.assertIn("switchport access vlan 10\n spanning-tree enable", rstp_text)

        mst = "\n".join(_executable(generate_lsw_config(vlan={
            "stp": {"mode": "mstp", "priority": 0, "enable": True},
        })))
        self.assertIn("spanning-tree mode mst", mst)
        self.assertNotIn("spanning-tree mode mstp", mst)
        self.assertNotIn("bridge-priority", mst)

        disabled = "\n".join(_executable(generate_lsw_config(vlan={
            "stp": {"mode": "stp", "priority": 32768, "enable": False},
        })))
        self.assertNotIn("spanning-tree", disabled)

    def test_routing_uses_documented_igp_and_skips_bgp(self):
        text = generate_lsw_config(routing={
            "static_routes": [{
                "dest_network": "10.2.0.0",
                "mask": "255.255.0.0",
                "next_hop": "10.1.1.2",
                "preference": 60,
            }],
            "rip": {"version": 2, "networks": ["192.168.10.0/24", "10.0.0.0"]},
            "ospf": {
                "process_id": 1,
                "router_id": "1.1.1.1",
                "area_id": "0",
                "networks": [{"address": "10.0.0.0", "mask": "0.0.0.255"}],
            },
            "bgp": {
                "as_number": 65000,
                "peers": [{"ip": "10.1.1.2", "as": 65001}],
                "networks": ["10.2.0.0/16"],
            },
        })
        commands = "\n".join(_executable(text))
        self.assertIn("ip route 10.2.0.0/16 10.1.1.2", commands)
        self.assertIn("router rip", commands)
        self.assertIn("network 192.168.10.0/24", commands)
        self.assertNotIn("network 10.0.0.0\n", text)
        self.assertIn("10.0.0.0/24", text)
        self.assertIn("router ospf 1", commands)
        self.assertIn("network 10.0.0.0/24 area 0", commands)
        self.assertNotIn("router-id 1.1.1.1", commands)
        self.assertNotIn("router bgp", commands)
        self.assertIn("BGP AS 65000", text)
        self.assertNotIn("router bgp 65000", text)

    def test_dhcp_snooping_and_input_rate_limit(self):
        text = generate_lsw_config(
            security={
                "acls": [{
                    "number": 100,
                    "type": "extended",
                    "rules": [{
                        "id": 10,
                        "action": "permit",
                        "protocol": "tcp",
                        "source": "any",
                        "destination": "192.168.10.10",
                        "dest_port": "80",
                    }],
                }],
                "dhcp_snooping": {"enable": True, "vlan": 10, "trusted_ports": ["gige0_24"]},
                "arp_inspection": {"vlans": [10], "trusted_ports": ["gige0_24"]},
            },
            interface={
                "rate_limits": [{"interface": "gige0_1", "cir_in": 10000, "cir_out": 20000}],
            },
        )
        commands = "\n".join(_executable(text))
        self.assertIn("dhcp snooping enable", commands)
        self.assertIn("dhcp snooping trust", commands)
        self.assertIn("rate-limit input 10000 burst-bucket 1024", commands)
        self.assertNotIn("rate-limit output", commands)
        self.assertNotIn("security-policy", commands)
        self.assertNotIn("acl mode", commands)
        self.assertIn("acl mode mac-ipv4", text)
        self.assertIn("arp inspection vlan", text)
        self.assertNotIn("\narp inspection", "\n" + commands)

    def test_telnet_password_mode(self):
        text = generate_lsw_config(basic={
            "enable_telnet": True,
            "telnet_port": 2233,
            "password": {"value": "LinePass1", "encrypted": False},
        })
        commands = "\n".join(_executable(text))
        self.assertIn("telnet enable", commands)
        self.assertIn("telnet port 2233", commands)
        self.assertIn("line vty", commands)
        self.assertIn("authentication mode password", commands)
        self.assertIn("password LinePass1", commands)
        self.assertNotIn("password conf-mode", commands)

    def test_newline_and_bad_names_are_rejected(self):
        with self.assertRaises(DPTechLSWConfigError):
            generate_lsw_config(basic={"hostname": "ok\nsysname injected"})
        with self.assertRaises(DPTechLSWConfigError):
            generate_lsw_config(basic={"hostname": "核心交换机"})
        with self.assertRaises(DPTechLSWConfigError):
            generate_lsw_config(vlan={
                "interfaces": [{"interface": "gige0_1\nshutdown", "type": "access", "vlan_id": 10}]
            })
        with self.assertRaises(DPTechLSWConfigError):
            generate_lsw_config(basic={
                "mgmt_interface": {
                    "interface": "GigabitEthernet0/0/1",
                    "ip_address": "10.0.0.1",
                    "mask": "255.255.255.0",
                }
            })

    def test_h3c_vlan_interface_alias(self):
        text = generate_lsw_config(basic={
            "mgmt_interface": {
                "interface": "Vlan-interface20",
                "ip_address": "10.20.0.1",
                "mask": "255.255.255.0",
            }
        })
        self.assertIn("interface vlan-if 20", text)
        self.assertIn("ip address 10.20.0.1/24", text)

    def test_builtin_template_generates_switch_script(self):
        manager = TemplateManager()
        template = manager.get_template("接入交换机基础配置", "dptech-lsw")
        self.assertIsNotNone(template)
        config = template.config
        text = generate_lsw_config(
            basic=config.get("basic"),
            vlan=config.get("vlan"),
            routing=config.get("routing"),
            security=config.get("security"),
            interface=config.get("interface"),
        )
        commands = "\n".join(_executable(text))
        self.assertIn("sysname DP-LSW-01", commands)
        self.assertIn("ssh enable", commands)
        self.assertIn("switchport access vlan 10", commands)
        self.assertIn("interface vlan-if 10", commands)
        self.assertNotIn("security-policy", commands)

        uplink = manager.get_template("汇聚链路聚合", "dptech-lsw")
        uplink_text = generate_lsw_config(
            basic=uplink.config.get("basic"),
            vlan=uplink.config.get("vlan"),
            interface=uplink.config.get("interface"),
        )
        uplink_commands = "\n".join(_executable(uplink_text))
        self.assertIn("bond mode dynamic", uplink_commands)
        self.assertIn("bond group 1", uplink_commands)

    def test_handbook_matches_switch_commands(self):
        blob = str(DPTECH_LSW_COMMANDS)
        self.assertIn("switchport access vlan", blob)
        self.assertIn("bond mode dynamic", blob)
        self.assertIn("ssh enable", blob)
        self.assertNotIn("security-policy <name>", blob)
        self.assertTrue(any(case["title"] == "动态聚合上联" for case in DPTECH_LSW_CASES))
        joined = "\n".join(DPTECH_LSW_CASES[1]["steps"])
        self.assertIn("bond group 1", joined)
        self.assertNotIn("security-zone", joined)

    def test_firewall_and_zte_generators_stay_on_their_own_syntax(self):
        firewall = generate_firewall_config(basic={"hostname": "DP-FW-01", "enable_ssh": True})
        self.assertIn("sysname DP-FW-01", firewall)
        self.assertIn("ssh enable", firewall)
        self.assertIn("security-zone", generate_firewall_config(basic={
            "mgmt_interface": {
                "interface": "meth0_0",
                "ip_address": "192.168.0.1",
                "mask": "255.255.255.0",
            }
        }))
        zte = generate_switch_config(basic={"hostname": "ZTE-Core"})
        self.assertIn("hostname ZTE-Core", zte)
        self.assertIn("configure terminal", zte)
        self.assertNotIn("conf-mode", zte)


if __name__ == "__main__":
    unittest.main()
