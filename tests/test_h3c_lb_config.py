#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""华三 SecPath 负载均衡脚本：只把核对过的命令写成可执行行。"""

import unittest

from modules.h3c_lb_config import H3CLBConfigError, generate_lb_config
from utils.manual.h3c_lb_manual import H3C_LB_CASES, H3C_LB_COMMANDS
from utils.template_manager import TemplateManager


def _executable(text):
    return "\n".join(
        line.strip() for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )


def _web():
    return generate_lb_config(
        basic={
            "hostname": "H3C-LB-01",
            "enable_ssh": True,
            "user": {"username": "admin", "password": "Admin@123", "level": 15},
            "mgmt_interface": {
                "interface": "GigabitEthernet1/0/1",
                "ip_address": "192.168.1.1",
                "mask": "255.255.255.0",
                "gateway": "192.168.1.254",
            },
        },
        routing={
            "static_routes": [{
                "dest_network": "198.51.100.0",
                "mask": "255.255.255.0",
                "next_hop": "192.168.1.254",
                "preference": 60,
            }],
            "ospf": {"process_id": 1, "networks": [{"network": "10.0.0.0", "area": "0"}]},
            "slb": {
                "server_farm": "web",
                "predictor": "round-robin",
                "health_check": "icmp",
                "real_servers": [
                    {"name": "rs1", "ip": "192.168.10.11", "port": 80, "weight": 150},
                    {"name": "rs2", "ip": "192.168.10.12", "port": 80, "weight": 100},
                ],
                "virtual_servers": [
                    {"name": "vs-web", "type": "tcp", "ip": "192.168.1.80", "port": 80},
                ],
            },
        },
        security={"acls": [{"number": 3000, "rules": []}]},
        interface={
            "eth_trunks": [{
                "trunk_id": 1,
                "mode": "lacp-dynamic",
                "member_ports": ["GigabitEthernet1/0/3", "GigabitEthernet1/0/4"],
            }]
        },
    )


class H3CLBConfigTests(unittest.TestCase):
    def test_empty_input_stays_empty(self):
        self.assertEqual(generate_lb_config(), "")
        self.assertEqual(generate_lb_config(basic={}, routing={}), "")

    def test_web_script_uses_verified_slb_commands(self):
        script = _web()
        commands = _executable(script)
        self.assertIn("system-view", commands)
        self.assertIn("sysname H3C-LB-01", commands)
        self.assertIn("interface GigabitEthernet 1/0/1", commands)
        self.assertIn("ip address 192.168.1.1 255.255.255.0", commands)
        self.assertIn("ip route-static 0.0.0.0 0.0.0.0 192.168.1.254", commands)
        self.assertIn("ip route-static 198.51.100.0 255.255.255.0 192.168.1.254", commands)
        self.assertIn("nqa template icmp icmp1", commands)
        self.assertIn("server-farm web", commands)
        self.assertIn("predictor round-robin", commands)
        self.assertIn("probe icmp1", commands)
        self.assertIn("real-server rs1", commands)
        self.assertIn("ip address 192.168.10.11", commands)
        self.assertIn("port 80", commands)
        self.assertIn("weight 150", commands)
        self.assertIn("server-farm web", commands)
        self.assertIn("virtual-server vs-web type tcp", commands)
        self.assertIn("virtual ip address 192.168.1.80", commands)
        self.assertIn("default server-farm web", commands)
        self.assertIn("service enable", commands)
        self.assertIn("arp-nd interface GigabitEthernet 1/0/1", commands)
        self.assertIn("interface Route-Aggregation 1", commands)
        self.assertIn("port link-aggregation group 1", commands)
        self.assertTrue(commands.strip().endswith("quit"))

    def test_unverified_items_stay_comments(self):
        script = _web()
        commands = _executable(script)
        self.assertIn("SSH", script)
        self.assertIn("local-user", script)
        self.assertIn("OSPF", script)
        self.assertIn("ACL 3000", script)
        self.assertIn("lacp-dynamic", script)
        self.assertNotIn("ssh server enable", commands)
        self.assertNotIn("local-user", commands)
        self.assertNotIn("Admin@123", script)
        self.assertNotIn("ospf ", commands)
        self.assertNotIn("security-policy", commands)
        self.assertNotIn("security-zone", commands)
        self.assertNotIn("switchport", commands)
        self.assertNotIn("transparent enable", commands)
        self.assertNotIn("stelnet", commands)
        for word in ("reboot", "reset", "shutdown", "undo ", "erase", "save"):
            self.assertNotIn(word, commands)

    def test_different_subnet_skips_arp_nd(self):
        script = generate_lb_config(
            basic={
                "mgmt_interface": {
                    "interface": "GE1/0/1",
                    "ip_address": "10.1.1.1",
                    "mask": "24",
                }
            },
            routing={
                "slb": {
                    "server_farm": "web",
                    "predictor": "least-connection",
                    "health_check": "",
                    "real_servers": [
                        {"name": "rs1", "ip": "10.1.1.11", "port": 0, "weight": 100}
                    ],
                    "virtual_servers": [
                        {"name": "vs1", "type": "http", "ip": "192.0.2.80", "port": 80}
                    ],
                }
            },
        )
        commands = _executable(script)
        self.assertIn("interface GigabitEthernet 1/0/1", commands)
        self.assertIn("ip address 10.1.1.1 255.255.255.0", commands)
        self.assertIn("predictor least-connection", commands)
        self.assertIn("port 0", commands)
        self.assertNotIn("nqa template", commands)
        self.assertNotIn("probe ", commands)
        self.assertNotIn("arp-nd", commands)
        self.assertNotIn("\nport 80\n", "\n" + commands + "\n")
        self.assertIn("同一网段", script)

    def test_hash_and_vlan_interface(self):
        script = generate_lb_config(
            vlan={
                "vlans": [{"id": 10, "name": "Servers"}],
                "interfaces": [{"interface": "GigabitEthernet1/0/2", "type": "access", "vlan_id": 10}],
                "vlanifs": [{
                    "vlan_id": 10,
                    "ip_address": "192.168.10.1",
                    "mask": "255.255.255.0",
                    "description": "server-gw",
                }],
            },
            routing={
                "slb": {
                    "predictor": "hash-source",
                    "health_check": "tcp",
                    "real_servers": [
                        {"name": "db1", "ip": "192.168.10.21", "port": 3306, "weight": 50}
                    ],
                    "virtual_servers": [
                        {"name": "vs-db", "type": "tcp", "ip": "192.168.10.80", "port": 3306}
                    ],
                }
            },
        )
        commands = _executable(script)
        self.assertIn("interface Vlan-interface 10", commands)
        self.assertIn("ip address 192.168.10.1 255.255.255.0", commands)
        self.assertIn("predictor hash address source", commands)
        self.assertIn("arp-nd interface Vlan-interface 10", commands)
        self.assertIn("描述 server-gw", script)
        self.assertIn("VLAN 10", script)
        self.assertIn("switchport", script)
        self.assertNotIn("switchport", commands)
        self.assertIn("健康检查 tcp", script)
        self.assertNotIn("nqa template", commands)

    def test_rejects_bad_fields(self):
        with self.assertRaises(H3CLBConfigError):
            generate_lb_config(basic={"hostname": "bad name"})
        with self.assertRaises(H3CLBConfigError):
            generate_lb_config(basic={"hostname": "bad\nhost"})
        with self.assertRaises(H3CLBConfigError):
            generate_lb_config(routing={"slb": {
                "real_servers": [{"name": "rs1", "ip": "224.0.0.1", "port": 80}]
            }})
        with self.assertRaises(H3CLBConfigError):
            generate_lb_config(routing={"slb": {
                "virtual_servers": [{"name": "vs", "type": "http", "ip": "192.168.1.80", "port": 0}]
            }})
        with self.assertRaises(H3CLBConfigError):
            generate_lb_config(basic={"mgmt_interface": {
                "interface": "gei_1/1",
                "ip_address": "192.168.1.1",
            }})

    def test_non_default_preference_is_comment_only(self):
        script = generate_lb_config(routing={
            "static_routes": [{
                "dest_network": "10.2.0.5",
                "mask": "255.255.0.0",
                "next_hop": "10.1.1.1",
                "interface": "GigabitEthernet1/0/2",
                "preference": 10,
            }],
            "bgp": {"as_number": 65000, "peers": [{"ip": "10.1.1.2", "as": 65001}]},
            "rip": {"networks": ["10.0.0.0"]},
        })
        commands = _executable(script)
        self.assertIn("ip route-static 10.2.0.0 255.255.0.0 10.1.1.1", commands)
        self.assertIn("优先级 10", script)
        self.assertIn("GigabitEthernet 1/0/2", script)
        self.assertNotIn("preference", commands)
        self.assertIn("BGP", script)
        self.assertIn("RIP", script)
        self.assertNotIn("bgp ", commands)

    def test_template_and_manual_match_generator(self):
        template = TemplateManager().get_template("Web 服务器负载均衡", "h3c-lb")
        self.assertIsNotNone(template)
        script = generate_lb_config(
            basic=template.config["basic"],
            routing=template.config["routing"],
            interface=template.config["interface"],
        )
        commands = _executable(script)
        self.assertIn("real-server rs2", commands)
        self.assertIn("weight 100", commands)
        self.assertIn("virtual ip address 192.168.1.80", commands)
        blob = str(H3C_LB_COMMANDS)
        self.assertIn("virtual-server", blob)
        self.assertIn("nqa template icmp", blob)
        self.assertNotIn("security-policy", blob)
        self.assertTrue(any(case["title"] == "Web 服务器负载均衡" for case in H3C_LB_CASES))
        joined = "\n".join(H3C_LB_CASES[0]["steps"])
        self.assertIn("service enable", joined)
        self.assertNotIn("reboot", joined)
        self.assertNotIn("61.159.", joined)


if __name__ == "__main__":
    unittest.main()
