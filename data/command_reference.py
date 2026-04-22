#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
命令参考手册
"""

COMMAND_REFERENCES = {
    "huawei": {
        "基础配置": {
            "主机名": {
                "command": "sysname <name>",
                "description": "设置设备主机名",
                "example": "sysname Core-SW-01",
                "category": "basic"
            },
            "管理IP": {
                "command": "interface Vlanif <id>\nip address <ip> <mask>",
                "description": "配置管理接口IP地址",
                "example": "interface Vlanif 1\nip address 192.168.1.1 255.255.255.0",
                "category": "basic"
            },
            "用户创建": {
                "command": "local-user <username> password <password>\nlocal-user <username> service-type ssh\nlocal-user <username> privilege level <0-15>",
                "description": "创建本地用户并设置权限级别",
                "example": "local-user admin password Admin@123\nlocal-user admin service-type ssh\nlocal-user admin privilege level 15",
                "category": "basic"
            },
            "SSH配置": {
                "command": "stelnet server enable\nssh user <username> authentication-type password\nssh user <username> service-type stelnet",
                "description": "启用SSH服务并配置认证",
                "example": "stelnet server enable\nssh user admin authentication-type password\nssh user admin service-type stelnet",
                "category": "basic"
            },
            "密码加密": {
                "command": "password cipher <password>",
                "description": "设置加密密码",
                "example": "password cipher Admin@123",
                "category": "basic"
            }
        },
        "VLAN配置": {
            "创建VLAN": {
                "command": "vlan <id>\nname <name>",
                "description": "创建VLAN并命名",
                "example": "vlan 10\nname Sales_Department",
                "category": "vlan"
            },
            "批量创建VLAN": {
                "command": "vlan batch <id1> <id2> <id3> to <idN>",
                "description": "批量创建多个VLAN",
                "example": "vlan batch 10 20 30 to 40",
                "category": "vlan"
            },
            "Access接口": {
                "command": "interface <interface>\nport link-type access\nport default vlan <id>",
                "description": "配置接口为Access模式并加入VLAN",
                "example": "interface GigabitEthernet0/0/1\nport link-type access\nport default vlan 10",
                "category": "vlan"
            },
            "Trunk接口": {
                "command": "interface <interface>\nport link-type trunk\nport trunk allow-pass vlan <ids>",
                "description": "配置接口为Trunk模式",
                "example": "interface GigabitEthernet0/0/24\nport link-type trunk\nport trunk allow-pass vlan 10 20 30",
                "category": "vlan"
            },
            "VLAN接口IP": {
                "command": "interface Vlanif <id>\nip address <ip> <mask>",
                "description": "配置VLAN接口IP（SVI）",
                "example": "interface Vlanif 10\nip address 192.168.10.1 255.255.255.0",
                "category": "vlan"
            }
        },
        "路由配置": {
            "静态路由": {
                "command": "ip route-static <dest> <mask> <nexthop>",
                "description": "配置静态路由",
                "example": "ip route-static 0.0.0.0 0.0.0.0 192.168.1.254",
                "category": "routing"
            },
            "OSPF配置": {
                "command": "ospf <process-id>\nrouter-id <id>\nnetwork <network> <wildcard> area <area-id>",
                "description": "配置OSPF动态路由",
                "example": "ospf 1\nrouter-id 1.1.1.1\nnetwork 192.168.0.0 0.0.255.255 area 0",
                "category": "routing"
            },
            "默认路由": {
                "command": "ip route-static 0.0.0.0 0.0.0.0 <gateway>",
                "description": "配置默认路由",
                "example": "ip route-static 0.0.0.0 0.0.0.0 10.0.0.1",
                "category": "routing"
            }
        },
        "安全配置": {
            "ACL配置": {
                "command": "acl <number> [basic|advance]\nrule <id> permit|deny <protocol> source <src> <wildcard>",
                "description": "创建访问控制列表",
                "example": "acl 3000\nrule 5 permit ip source 192.168.1.0 0.0.0.255 destination 10.0.0.0 0.0.255.255",
                "category": "security"
            },
            "应用ACL": {
                "command": "interface <interface>\ntraffic-filter inbound acl <number>",
                "description": "在接口上应用ACL",
                "example": "interface GigabitEthernet0/0/1\ntraffic-filter inbound acl 3000",
                "category": "security"
            },
            "端口安全": {
                "command": "interface <interface>\nport-security enable\nport-security max-mac-num <number>\nport-security protect-action protect|restrict|shutdown",
                "description": "配置端口安全",
                "example": "interface GigabitEthernet0/0/1\nport-security enable\nport-security max-mac-num 1\nport-security protect-action shutdown",
                "category": "security"
            },
            "关闭未使用端口": {
                "command": "interface range <interface-list>\nshutdown",
                "description": "关闭未使用的端口提高安全性",
                "example": "interface range GigabitEthernet0/0/1 to GigabitEthernet0/0/10\nshutdown",
                "category": "security"
            }
        },
        "接口配置": {
            "Eth-Trunk": {
                "command": "interface Eth-Trunk <id>\nmode lacp-static|lacp-dynamic|manual\ninterface <member>\neth-trunk <id>",
                "description": "配置链路聚合",
                "example": "interface Eth-Trunk 1\nmode lacp-static\ninterface GigabitEthernet0/0/1\neth-trunk 1",
                "category": "interface"
            },
            "接口描述": {
                "command": "interface <interface>\ndescription <text>",
                "description": "为接口添加描述",
                "example": "interface GigabitEthernet0/0/1\ndescription Connect_to_Server_Room",
                "category": "interface"
            },
            "端口镜像": {
                "command": "observe-port <id> interface <interface>\ninterface <interface>\nport-mirroring to observe-port <id> [inbound|outbound|both]",
                "description": "配置端口镜像",
                "example": "observe-port 1 interface GigabitEthernet0/0/24\ninterface GigabitEthernet0/0/1\nport-mirroring to observe-port 1 both",
                "category": "interface"
            }
        },
        "管理与维护": {
            "保存配置": {
                "command": "save [configuration]",
                "description": "保存当前配置",
                "example": "save",
                "category": "manage"
            },
            "查看配置": {
                "command": "display current-configuration\ndisplay saved-configuration",
                "description": "查看当前/保存的配置",
                "example": "display current-configuration",
                "category": "manage"
            },
            "查看接口状态": {
                "command": "display interface [brief|<interface>]",
                "description": "查看接口状态信息",
                "example": "display interface brief",
                "category": "manage"
            },
            "查看MAC地址表": {
                "command": "display mac-address [dynamic|static]",
                "description": "查看MAC地址表",
                "example": "display mac-address dynamic",
                "category": "manage"
            },
            "Ping测试": {
                "command": "ping <ip> [-c count] [-s size]",
                "description": "测试网络连通性",
                "example": "ping 192.168.1.1",
                "category": "manage"
            },
            "Traceroute": {
                "command": "tracert <ip>",
                "description": "追踪路由路径",
                "example": "tracert 8.8.8.8",
                "category": "manage"
            },
            "查看日志": {
                "command": "display logbuffer\ndisplay info-center logbuffer",
                "description": "查看系统日志",
                "example": "display logbuffer",
                "category": "manage"
            }
        }
    },
    "h3c": {
        "基础配置": {
            "主机名": {
                "command": "sysname <name>",
                "description": "设置设备主机名",
                "example": "sysname H3C-Core-SW",
                "category": "basic"
            },
            "管理IP": {
                "command": "interface Vlan-interface <id>\nip address <ip> <mask>",
                "description": "配置管理接口IP地址（注意：H3C使用Vlan-interface）",
                "example": "interface Vlan-interface 1\nip address 192.168.1.1 255.255.255.0",
                "category": "basic"
            },
            "用户创建": {
                "command": "local-user <username> class manage\npassword simple <password>\nservice-type ssh\nauthorization-attribute user-role level-<0-15>",
                "description": "创建本地用户（H3C Comware V7风格）",
                "example": "local-user admin class manage\npassword simple Admin@123\nservice-type ssh\nauthorization-attribute user-role level-15",
                "category": "basic"
            }
        },
        "VLAN配置": {
            "创建VLAN": {
                "command": "vlan <id>\nname <name>",
                "description": "创建VLAN并命名",
                "example": "vlan 10\nname Sales",
                "category": "vlan"
            },
            "Access接口": {
                "command": "interface <interface>\nport link-mode bridge\nport access vlan <id>",
                "description": "配置Access接口",
                "example": "interface GigabitEthernet1/0/1\nport link-mode bridge\nport access vlan 10",
                "category": "vlan"
            },
            "Trunk接口": {
                "command": "interface <interface>\nport link-mode bridge\nport link-type trunk\nport trunk permit vlan <ids>",
                "description": "配置Trunk接口",
                "example": "interface GigabitEthernet1/0/24\nport link-type trunk\nport trunk permit vlan 10 20",
                "category": "vlan"
            }
        }
    },
    "ruijie": {
        "基础配置": {
            "主机名": {
                "command": "hostname <name>",
                "description": "设置设备主机名（锐捷使用hostname而非sysname）",
                "example": "hostname RG-Core-SW",
                "category": "basic"
            },
            "管理IP": {
                "command": "interface vlan <id>\nip address <ip> <mask>",
                "description": "配置VLAN接口IP",
                "example": "interface vlan 1\nip address 192.168.1.1 255.255.255.0",
                "category": "basic"
            },
            "用户创建": {
                "command": "username <name> privilege <level> password <password>",
                "description": "创建用户（类Cisco命令风格）",
                "example": "username admin privilege 15 password Admin@123",
                "category": "basic"
            },
            "SSH配置": {
                "command": "ip ssh version 2\ncrypto key generate rsa\nline vty 0 4\ntransport input ssh\nlogin local",
                "description": "启用SSH登录",
                "example": "ip ssh version 2\ncrypto key generate rsa",
                "category": "basic"
            }
        },
        "VLAN配置": {
            "创建VLAN": {
                "command": "vlan <id>\nname <name>",
                "description": "创建VLAN",
                "example": "vlan 10\nname Sales_Dept",
                "category": "vlan"
            },
            "Access接口": {
                "command": "interface <interface>\nswitchport mode access\nswitchport access vlan <id>",
                "description": "配置Access接口",
                "example": "interface GigabitEthernet0/1\nswitchport mode access\nswitchport access vlan 10",
                "category": "vlan"
            },
            "Trunk接口": {
                "command": "interface <interface>\nswitchport mode trunk\nswitchport trunk allowed vlan <ids>",
                "description": "配置Trunk接口",
                "example": "interface GigabitEthernet0/24\nswitchport mode trunk\nswitchport trunk allowed vlan 10,20,30",
                "category": "vlan"
            }
        },
        "安全配置": {
            "ACL配置": {
                "command": "ip access-list extended <name|number>\npermit|deny <protocol> <src> <dst> eq <port>",
                "description": "配置扩展ACL",
                "example": "ip access-list extended 100\npermit tcp any any eq 80\ndeny ip any any",
                "category": "security"
            },
            "应用ACL": {
                "command": "interface <interface>\nip access-group <acl> in|out",
                "description": "应用ACL到接口",
                "example": "interface GigabitEthernet0/1\nip access-group 100 in",
                "category": "security"
            }
        }
    },
    "maipu": {
        "基础配置": {
            "主机名": {
                "command": "hostname <name>",
                "description": "设置设备主机名",
                "example": "hostname MP-Core-SW",
                "category": "basic"
            },
            "管理IP": {
                "command": "interface vlan <id>\nip address <ip> <mask>",
                "description": "配置管理IP",
                "example": "interface vlan 1\nip address 192.168.1.1 255.255.255.0",
                "category": "basic"
            },
            "用户创建": {
                "command": "username <name> privilege <level> password <password>",
                "description": "创建用户",
                "example": "username admin privilege 15 password Admin@123",
                "category": "basic"
            }
        },
        "VLAN配置": {
            "创建VLAN": {
                "command": "vlan <id>\nname <name>",
                "description": "创建VLAN",
                "example": "vlan 10\nname Sales",
                "category": "vlan"
            },
            "Access接口": {
                "command": "interface <interface>\nswitchport mode access\nswitchport access vlan <id>",
                "description": "配置Access接口",
                "example": "interface fastethernet0/1\nswitchport mode access\nswitchport access vlan 10",
                "category": "vlan"
            }
        }
    }
}


BEST_PRACTICES = [
    {
        "title": "安全基线",
        "items": [
            "修改默认密码，使用复杂密码策略",
            "关闭Telnet，仅使用SSHv2",
            "关闭不必要的服务和端口",
            "配置ACL限制管理访问",
            "启用日志记录和审计",
            "定期备份配置文件"
        ]
    },
    {
        "title": "网络设计",
        "items": [
            "核心层高可用，部署双核心+VRRP/堆叠",
            "接入层端口安全，绑定MAC地址",
            "VLAN规划设计，业务隔离",
            "使用PVLAN隔离同一VLAN内用户",
            "端口描述规范，便于维护"
        ]
    },
    {
        "title": "运维管理",
        "items": [
            "配置自动备份和异地存储",
            "定期验证备份可恢复性",
            "变更前备份，变更后验证",
            "建立变更审批流程",
            "监控日志，及时发现异常"
        ]
    }
]


SHORTCUTS = {
    "通用快捷键": {
        "Ctrl+S": "保存配置",
        "Ctrl+Z": "返回用户视图",
        "Ctrl+C": "中断当前命令",
        "Tab": "自动补全命令",
        "?": "显示帮助信息",
        "↑ / ↓": "历史命令"
    },
    "视图切换": {
        "system-view": "进入系统视图",
        "quit": "退出当前视图",
        "return": "返回用户视图"
    }
}
