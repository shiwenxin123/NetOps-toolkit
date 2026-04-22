#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NetOps Toolkit - 配置模板
"""

TEMPLATES = {
    "接入交换机标准配置": {
        "description": "企业接入层交换机标准配置模板",
        "config": {
            "basic": {
                "hostname": "Access-SW-01",
                "password": {"value": "Admin@123", "encrypted": True},
                "mgmt_interface": {
                    "interface": "Vlanif1",
                    "ip_address": "192.168.1.1",
                    "mask": "255.255.255.0",
                    "gateway": "192.168.1.254"
                },
                "enable_ssh": True,
                "enable_telnet": False,
                "user": {
                    "username": "admin",
                    "password": "Admin@123",
                    "level": 15,
                    "encrypted": True
                }
            },
            "vlan": {
                "vlans": [
                    {"id": 1, "name": "Management"},
                    {"id": 10, "name": "Sales"},
                    {"id": 20, "name": "Engineering"}
                ],
                "vlanifs": [
                    {"vlan_id": 1, "ip_address": "192.168.1.1", "mask": "255.255.255.0"}
                ],
                "stp": {"mode": "rstp", "enable": True}
            },
            "security": {
                "acls": [],
                "port_security": []
            },
            "interface": {
                "lldp": {"enable": True, "mode": "both"},
                "loopback_detection": {"enable": True}
            }
        }
    },
    
    "核心交换机配置": {
        "description": "企业核心层交换机配置模板",
        "config": {
            "basic": {
                "hostname": "Core-SW-01",
                "password": {"value": "CoreAdmin@123", "encrypted": True},
                "mgmt_interface": {
                    "interface": "Vlanif1",
                    "ip_address": "10.0.0.1",
                    "mask": "255.255.255.0"
                },
                "enable_ssh": True,
                "user": {
                    "username": "admin",
                    "password": "CoreAdmin@123",
                    "level": 15,
                    "encrypted": True
                },
                "ntp": {
                    "servers": [{"ip": "10.0.0.100", "prefer": True}],
                    "timezone": "UTC+8"
                },
                "snmp": {
                    "version": "v2c",
                    "community_read": "public",
                    "sys_location": "Core-Site-A",
                    "trap_enable": True
                },
                "log": {
                    "host": "10.0.0.200",
                    "log_level": "informational"
                }
            },
            "vlan": {
                "vlans": [
                    {"id": 1, "name": "Management"},
                    {"id": 10, "name": "Sales"},
                    {"id": 20, "name": "Engineering"},
                    {"id": 100, "name": "Server"}
                ],
                "vlanifs": [
                    {"vlan_id": 10, "ip_address": "192.168.10.1", "mask": "255.255.255.0"},
                    {"vlan_id": 20, "ip_address": "192.168.20.1", "mask": "255.255.255.0"},
                    {"vlan_id": 100, "ip_address": "192.168.100.1", "mask": "255.255.255.0"}
                ]
            },
            "routing": {
                "ospf": {
                    "process_id": 1,
                    "router_id": "1.1.1.1",
                    "area_id": "0",
                    "networks": [
                        {"address": "192.168.10.0", "mask": "0.0.0.255"},
                        {"address": "192.168.20.0", "mask": "0.0.0.255"},
                        {"address": "192.168.100.0", "mask": "0.0.0.255"}
                    ]
                }
            },
            "interface": {
                "eth_trunks": [
                    {
                        "trunk_id": 1,
                        "mode": "lacp-static",
                        "member_ports": ["XGigabitEthernet0/0/1", "XGigabitEthernet0/0/2"],
                        "port_link_type": "trunk",
                        "trunk_vlans": [10, 20, 100]
                    }
                ],
                "lldp": {"enable": True}
            }
        }
    },
    
    "PoE交换机配置": {
        "description": "PoE交换机配置模板（适合AP/电话供电）",
        "config": {
            "basic": {
                "hostname": "PoE-SW-01",
                "password": {"value": "PoeAdmin@123", "encrypted": True},
                "mgmt_interface": {
                    "interface": "Vlanif1",
                    "ip_address": "192.168.1.10",
                    "mask": "255.255.255.0"
                },
                "enable_ssh": True,
                "user": {
                    "username": "admin",
                    "password": "PoeAdmin@123",
                    "level": 15,
                    "encrypted": True
                }
            },
            "vlan": {
                "vlans": [
                    {"id": 100, "name": "Voice"},
                    {"id": 200, "name": "Data"},
                    {"id": 300, "name": "AP-Management"}
                ]
            },
            "interface": {
                "lldp": {"enable": True, "mode": "both"},
                "poe": {
                    "enable": True,
                    "max_power": 74000
                }
            }
        }
    },
    
    "数据中心接入交换机": {
        "description": "数据中心ToR交换机配置模板",
        "config": {
            "basic": {
                "hostname": "DC-TOR-01",
                "password": {"value": "DataCenter@123", "encrypted": True},
                "mgmt_interface": {
                    "interface": "Vlanif1",
                    "ip_address": "10.10.10.1",
                    "mask": "255.255.255.0",
                    "gateway": "10.10.10.254"
                },
                "enable_ssh": True,
                "enable_telnet": False,
                "user": {
                    "username": "admin",
                    "password": "DataCenter@123",
                    "level": 15,
                    "encrypted": True
                },
                "ntp": {
                    "servers": [{"ip": "10.10.0.1", "prefer": True}],
                    "timezone": "UTC+8"
                },
                "log": {
                    "host": "10.10.0.100",
                    "log_level": "informational"
                }
            },
            "vlan": {
                "vlans": [
                    {"id": 100, "name": "Web"},
                    {"id": 200, "name": "App"},
                    {"id": 300, "name": "DB"}
                ],
                "vlanifs": [
                    {"vlan_id": 100, "ip_address": "10.100.0.1", "mask": "255.255.255.0"},
                    {"vlan_id": 200, "ip_address": "10.200.0.1", "mask": "255.255.255.0"},
                    {"vlan_id": 300, "ip_address": "10.300.0.1", "mask": "255.255.255.0"}
                ]
            },
            "routing": {
                "ospf": {
                    "process_id": 1,
                    "router_id": "2.2.2.2",
                    "area_id": "0",
                    "networks": [
                        {"address": "10.100.0.0", "mask": "0.0.0.255"},
                        {"address": "10.200.0.0", "mask": "0.0.0.255"},
                        {"address": "10.300.0.0", "mask": "0.0.0.255"}
                    ]
                }
            },
            "interface": {
                "eth_trunks": [
                    {
                        "trunk_id": 10,
                        "mode": "lacp-static",
                        "member_ports": ["XGigabitEthernet0/0/47", "XGigabitEthernet0/0/48"],
                        "port_link_type": "trunk",
                        "trunk_vlans": [100, 200, 300]
                    }
                ],
                "lldp": {"enable": True}
            },
            "security": {
                "port_security": [
                    {"interface": "GigabitEthernet0/0/1", "enable": True, "max_mac": 2}
                ]
            }
        }
    },
    
    "园区汇聚交换机": {
        "description": "园区网汇聚层交换机配置模板",
        "config": {
            "basic": {
                "hostname": "Aggregation-SW-01",
                "password": {"value": "AggAdmin@123", "encrypted": True},
                "mgmt_interface": {
                    "interface": "Vlanif999",
                    "ip_address": "172.16.1.1",
                    "mask": "255.255.255.0"
                },
                "enable_ssh": True,
                "user": {
                    "username": "admin",
                    "password": "AggAdmin@123",
                    "level": 15,
                    "encrypted": True
                },
                "ntp": {
                    "servers": [{"ip": "172.16.0.1", "prefer": True}],
                    "timezone": "UTC+8"
                },
                "snmp": {
                    "version": "v2c",
                    "community_read": "public",
                    "trap_enable": True,
                    "trap_host": "172.16.0.100"
                }
            },
            "vlan": {
                "vlans": [
                    {"id": 10, "name": "Sales"},
                    {"id": 20, "name": "HR"},
                    {"id": 30, "name": "IT"},
                    {"id": 999, "name": "Management"}
                ],
                "vlanifs": [
                    {"vlan_id": 10, "ip_address": "172.16.10.1", "mask": "255.255.255.0"},
                    {"vlan_id": 20, "ip_address": "172.16.20.1", "mask": "255.255.255.0"},
                    {"vlan_id": 30, "ip_address": "172.16.30.1", "mask": "255.255.255.0"}
                ],
                "stp": {"mode": "mstp", "enable": True, "priority": 8192}
            },
            "routing": {
                "ospf": {
                    "process_id": 1,
                    "router_id": "3.3.3.3",
                    "area_id": "0",
                    "networks": [
                        {"address": "172.16.10.0", "mask": "0.0.0.255"},
                        {"address": "172.16.20.0", "mask": "0.0.0.255"},
                        {"address": "172.16.30.0", "mask": "0.0.0.255"}
                    ]
                }
            },
            "interface": {
                "eth_trunks": [
                    {
                        "trunk_id": 1,
                        "mode": "lacp-static",
                        "member_ports": ["XGigabitEthernet0/0/23", "XGigabitEthernet0/0/24"],
                        "port_link_type": "trunk",
                        "trunk_vlans": [10, 20, 30, 999]
                    }
                ],
                "lldp": {"enable": True}
            }
        }
    }
}


def get_template_names():
    """获取所有模板名称"""
    return list(TEMPLATES.keys())


def get_template_description(name):
    """获取模板描述"""
    return TEMPLATES.get(name, {}).get("description", "")


def get_template_config(name):
    """获取模板配置"""
    return TEMPLATES.get(name, {}).get("config", {})


def get_all_templates():
    """获取所有模板"""
    return TEMPLATES
