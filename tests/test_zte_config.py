#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""中兴 ZXR10 配置生成器的冒烟测试。不依赖界面。"""

import unittest

from modules.zte_config import ZTEConfigError, generate_switch_config


class ZTEConfigTests(unittest.TestCase):
    def test_empty_input_returns_blank(self):
        self.assertEqual(generate_switch_config(), "")

    def test_core_sections_use_zxr10_commands(self):
        text = generate_switch_config(
            basic={
                "hostname": "ZTE-Core-01",
                "password": {"value": "Enable1", "encrypted": False},
                "user": {"username": "netops", "password": "Netops1", "level": 15},
                "mgmt_interface": {
                    "interface": "Vlanif1",
                    "ip_address": "192.168.1.1",
                    "mask": "255.255.255.0",
                    "gateway": "192.168.1.254",
                },
                "enable_ssh": True,
                "ssh_port": 22,
                "ntp": {"servers": [{"ip": "10.0.0.100", "prefer": True}], "timezone": "UTC+8"},
                "snmp": {"version": "v2c", "community_read": "public", "sys_location": "Lab A"},
                "log": {"info_center_enable": True, "host": "10.0.0.200", "log_level": "informational"},
                "dns": {"servers": ["223.5.5.5"], "domain": "example.com"},
            },
            vlan={
                "vlans": [{"id": 10, "name": "Office"}, {"id": 20, "name": "Server"}],
                "interfaces": [
                    {"interface": "gei_1/1", "type": "access", "vlan_id": 10},
                    {"interface": "gei_1/24", "type": "trunk", "trunk_vlans": [10, 20], "pvid": 1},
                    {"interface": "gei_1/2", "type": "hybrid", "vlan_id": 20},
                ],
                "vlanifs": [{
                    "vlan_id": 10,
                    "ip_address": "192.168.10.1",
                    "mask": "255.255.255.0",
                    "description": "Office GW",
                }],
                "stp": {"mode": "stp", "priority": 4096, "enable": True},
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
                "bgp": {
                    "as_number": 65001,
                    "router_id": "1.1.1.1",
                    "peers": [{"ip": "10.1.1.2", "as": 65002}],
                    "networks": ["10.2.0.0 255.255.0.0"],
                },
                "rip": {"version": 2, "networks": ["10.0.0.0"]},
            },
            security={
                "acls": [
                    {
                        "number": 10,
                        "type": "standard",
                        "rules": [{"id": 5, "action": "permit", "source": "192.168.1.0", "source_wildcard": "0.0.0.255"}],
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
                            "destination": "any",
                            "dest_port": "80",
                        }],
                    },
                ],
                "port_security": [{
                    "interface": "gei_1/1",
                    "enable": True,
                    "max_mac": 2,
                    "action": "shutdown",
                    "sticky": True,
                }],
                "traffic_filters": [{"interface": "gei_1/1", "acl_number": 100, "direction": "inbound"}],
                "dhcp_snooping": {"enable": True, "vlan": 10, "trusted_ports": ["gei_1/24"]},
                "arp_inspection": {"vlans": [10], "trusted_ports": ["gei_1/24"]},
                "storm_controls": [{"interface": "gei_1/1", "broadcast": 1000, "multicast": 500}],
            },
            interface={
                "eth_trunks": [{
                    "trunk_id": 1,
                    "mode": "lacp-static",
                    "description": "uplink",
                    "member_ports": ["gei_1/23", "gei_1/24"],
                    "port_link_type": "trunk",
                    "trunk_vlans": [10, 20],
                }],
                "lldp": {"enable": True, "mode": "both", "interval": 30, "holdtime": 120},
                "loopback_detection": {"enable": True, "action": "block", "vlan_ids": [10]},
                "rate_limits": [{"interface": "gei_1/1", "cir_in": 10000, "cir_out": 20000}],
            },
        )

        self.assertIn("configure terminal", text)
        self.assertIn("hostname ZTE-Core-01", text)
        self.assertIn("enable secret 0 Enable1", text)
        self.assertIn("username netops password Netops1 privilege 15", text)
        self.assertIn("interface vlan 1\n", text)
        self.assertNotIn("interface Vlanif", text)
        self.assertNotIn("sysname", text)
        self.assertNotIn("stelnet", text)
        self.assertIn("ip route 0.0.0.0 0.0.0.0 192.168.1.254", text)
        self.assertIn("clock timezone Beijing 8", text)
        self.assertLess(text.index("\nclock timezone Beijing 8\n"), text.index("\nconfigure terminal\n"))
        self.assertIn("ssh server enable", text)
        self.assertIn("ntp server 10.0.0.100", text)
        self.assertIn("snmp-server community public ro", text)
        self.assertIn("snmp-server location Lab A", text)
        self.assertIn("syslog server 10.0.0.200", text)
        self.assertIn("ip name-server 223.5.5.5", text)
        self.assertIn("switchport access vlan 10", text)
        self.assertIn("switchport trunk vlan 10,20", text)
        self.assertIn("switchport trunk native vlan 1", text)
        self.assertIn("switchport hybrid vlan 20 untag", text)
        self.assertIn("interface vlan 10", text)
        self.assertIn("description Office GW", text)
        self.assertIn("spanning-tree mode sstp", text)
        self.assertIn("spanning-tree priority 4096", text)
        self.assertIn("ip route 10.2.0.0 255.255.0.0 10.1.1.2 60", text)
        self.assertIn("router ospf 1", text)
        self.assertIn("network 10.0.0.0 0.0.0.255 area 0", text)
        self.assertIn("neighbor 10.1.1.2 remote-as 65002", text)
        self.assertIn("router rip", text)
        self.assertIn("acl standard number 10", text)
        self.assertIn("acl extend number 100", text)
        self.assertIn("rule 10 permit tcp any any eq 80", text)
        self.assertIn("ip access-group 100 in", text)
        self.assertIn("switchport port-security maximum 2", text)
        self.assertIn("ip dhcp snooping vlan 10", text)
        self.assertIn("ip arp inspection vlan 10", text)
        self.assertIn("storm-control broadcast pps 1000", text)
        self.assertIn("interface smartgroup1", text)
        self.assertIn("smartgroup 1 mode active", text)
        self.assertIn("lldp holdtime 4", text)
        self.assertIn("loop-detect portstate block", text)
        self.assertIn("rate-limit input 10000", text)
        self.assertIn("end", text)

    def test_manual_aggregation_maps_to_mode_on(self):
        text = generate_switch_config(interface={
            "eth_trunks": [{
                "trunk_id": 2,
                "mode": "manual",
                "member_ports": ["fei_1/1"],
                "port_link_type": "access",
                "native_vlan": 10,
            }]
        })
        self.assertIn("smartgroup 2 mode on", text)
        self.assertIn("switchport access vlan 10", text)

    def test_stp_disable_and_rstp(self):
        text = generate_switch_config(vlan={"stp": {"mode": "rstp", "enable": False, "priority": 32768}})
        self.assertIn("spanning-tree disable", text)
        self.assertNotIn("spanning-tree mode", text)

    def test_newline_in_hostname_is_rejected(self):
        with self.assertRaises(ZTEConfigError):
            generate_switch_config(basic={"hostname": "ok\nhostname injected"})

    def test_banner_keeps_multiple_lines(self):
        text = generate_switch_config(basic={"banner": {"login": "line1\nline2"}})
        self.assertIn("banner incoming #", text)
        self.assertIn("line1\nline2", text)

    def test_chinese_hostname_and_vlan_name(self):
        text = generate_switch_config(
            basic={"hostname": "核心-SW"},
            vlan={"vlans": [{"id": 10, "name": "办公"}]},
        )
        self.assertIn("hostname 核心-SW", text)
        self.assertIn("name 办公", text)

    def test_vlan_interface_alias_from_h3c(self):
        text = generate_switch_config(basic={
            "mgmt_interface": {
                "interface": "Vlan-interface20",
                "ip_address": "10.20.0.1",
                "mask": "255.255.255.0",
            }
        })
        self.assertIn("interface vlan 20", text)
        self.assertIn("ip address 10.20.0.1 255.255.255.0", text)


if __name__ == "__main__":
    unittest.main()
