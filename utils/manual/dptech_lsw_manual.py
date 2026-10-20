#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
迪普 LSW 交换机 Conplat 命令速查。

只收录生成器会写出、并且能在 LSW6600 命令配置手册 v3.0、
迪普官方静态聚合示例或 LSW3600 Telnet 现场写法里对上的命令。
FW1000 的 security-policy 不在这里。
"""

DPTECH_LSW_COMMANDS = {
    "基础配置": {
        "系统与登录": [
            {"name": "进入配置视图", "command": "conf-mode", "description": "从用户视图进入配置视图。结束后用 exit 回到用户视图", "example": "conf-mode"},
            {"name": "系统名", "command": "sysname <name>", "description": "Conplat 的系统名命令，1 到 20 位字母、数字、点、下划线或短横线。LSW6600 手册示例保持出厂提示符 DPTECH", "example": "sysname DP-LSW-01"},
            {"name": "SSH", "command": "ssh enable", "description": "打开 SSH。手册没有单独的 ssh port，非 22 端口不会写进脚本", "example": "ssh enable"},
            {"name": "本地用户", "command": "local-user <name> password <password> role super", "description": "LSW3600 现场单行写法。不使用 FW1000 的 password plain-text-password，避免后续配置被交互读成密码", "example": "local-user admin password Admin@123 role super"},
            {"name": "Telnet", "command": "telnet enable\ntelnet port <port>", "description": "缺省端口 23 时不写 telnet port。用户名认证进 line vty", "example": "telnet enable\nline vty\n authentication mode username\n exit"},
            {"name": "Telnet 口令", "command": "line vty\n authentication mode password\n password <password>", "description": "没有本地用户、只填了管理密码时使用。password conf-mode 是防火墙命令，不写到交换机", "example": "line vty\n authentication mode password\n password Admin@123\n exit"},
            {"name": "保存", "command": "write file", "description": "配置视图可试。重启时设备会询问 System configuration has been modified. Save? (Y/N)。脚本里这行是注释，不会自动保存", "example": "conf-mode\nwrite file"},
        ],
        "管理地址": [
            {"name": "三层 VLAN 口", "command": "interface vlan-if <id>", "description": "地址用前缀长度。界面里的 Vlanif10 会改成 vlan-if 10", "example": "interface vlan-if 1\n ip address 192.168.1.1/24\n exit"},
            {"name": "默认路由", "command": "ip route 0.0.0.0/0 <interface> <nexthop>", "description": "管理网关写成前缀、出接口和下一跳", "example": "ip route 0.0.0.0/0 vlan-if1 192.168.1.254"},
        ],
    },
    "VLAN配置": {
        "VLAN 与接口": [
            {"name": "创建 VLAN", "command": "vlan <id>", "description": "进入 VLAN 视图后 exit。名称只写在注释里，手册示例没有 name 子命令", "example": "vlan 10\n exit"},
            {"name": "Access", "command": "switchport access vlan <id>", "description": "写在物理口下。手册用这一条把口放进 VLAN，不另写 switchport mode access", "example": "interface gige0_1\n switchport access vlan 10\n exit"},
            {"name": "Trunk", "command": "switchport mode trunk\nswitchport trunk allowed vlan <list>\nswitchport trunk native vlan <id>", "description": "连续 VLAN 收成 10-12，不连续的用逗号", "example": "interface gige0_24\n switchport mode trunk\n switchport trunk allowed vlan 10,20\n switchport trunk native vlan 1\n exit"},
            {"name": "Hybrid", "command": "switchport mode hybrid\nswitchport hybrid allowed vlan <id> untagged\nswitchport hybrid native vlan <id>", "description": "界面只填一个 VLAN 时，按手册写成 untagged，并把它设成 native", "example": "interface gige0_2\n switchport mode hybrid\n switchport hybrid allowed vlan 20 untagged\n switchport hybrid native vlan 20\n exit"},
            {"name": "生成树", "command": "spanning-tree enable\nspanning-tree mode (stp|rstp|mst)\nspanning-tree bridge-priority <priority>", "description": "界面的 mstp 写成 mode mst。STP/RSTP 的非默认优先级用 bridge-priority。MSTP 实例优先级没有实例号，不编造", "example": "spanning-tree enable\nspanning-tree mode rstp\nspanning-tree bridge-priority 4096\ninterface gige0_1\n spanning-tree enable\n exit"},
        ],
    },
    "路由配置": {
        "静态、RIP、OSPF": [
            {"name": "静态路由", "command": "ip route <dest>/<prefix> <nexthop>", "description": "同时有出接口时写成 ip route <dest>/<prefix> <interface> <nexthop>。不写管理距离", "example": "ip route 10.2.0.0/16 10.1.1.2"},
            {"name": "RIP", "command": "router rip\n network <ip>/<prefix>", "description": "网络必须带前缀。界面只填 192.168.0.0 时脚本会注释，不会猜 /24", "example": "router rip\n network 192.168.10.0/24\n exit"},
            {"name": "OSPF", "command": "router ospf <process>\n network <ip>/<prefix> area <area>", "description": "反掩码会收成前缀。LSW3600-24GT4GP-LI 彩页没有三层路由，入门型号要删掉这段", "example": "router ospf 1\n network 10.0.0.0/24 area 0\n exit"},
            {"name": "BGP", "command": "不生成", "description": "LSW3600/LSW5600/LSW6600 公开示例没有 router bgp。界面填了 BGP 也只留注释", "example": "! BGP AS 65000 未生成命令"},
        ],
    },
    "安全与接口": {
        "交换特性": [
            {"name": "DHCP Snooping", "command": "dhcp snooping enable\ndhcp snooping trust", "description": "信任口写在接口视图。不是防火墙的安全策略", "example": "dhcp snooping enable\ninterface gige0_24\n dhcp snooping trust\n exit"},
            {"name": "入方向限速", "command": "rate-limit input <kbps> burst-bucket 1024", "description": "10 Mbit/s 对应 10000。burst-bucket 1024 的单位是 Kbits，取自手册示例。出方向没有核对到命令", "example": "interface gige0_1\n rate-limit input 10000 burst-bucket 1024\n exit"},
            {"name": "动态聚合", "command": "interface bond <id>\n bond mode dynamic\n bond load-sharing mode source-destination-ip\n bond group <id>", "description": "成员口上写 bond group。对应界面的 lacp-dynamic", "example": "interface bond 1\n bond mode dynamic\n bond load-sharing mode source-destination-ip\n switchport mode trunk\n switchport trunk allowed vlan 10,20\n exit\ninterface gige0_23\n bond group 1\n exit"},
            {"name": "静态聚合", "command": "bond mode static\n bond load-sharing mode source-destination-mac", "description": "对应界面的 manual。lacp-static 没有单独关键字，脚本只注释", "example": "interface bond 2\n bond mode static\n bond load-sharing mode source-destination-mac\n exit"},
        ],
    },
}

DPTECH_LSW_CASES = [
    {
        "title": "接入 VLAN 与 SSH",
        "description": "管理地址在 vlan-if 1，gige0_1 划进 VLAN 10，并打开 SSH。",
        "steps": [
            "conf-mode",
            "sysname DP-LSW-01",
            "ssh enable",
            "local-user admin password Admin@123 role super",
            "interface vlan-if 1",
            " ip address 192.168.1.1/24",
            " exit",
            "ip route 0.0.0.0/0 vlan-if1 192.168.1.254",
            "vlan 10",
            " exit",
            "interface gige0_1",
            " switchport access vlan 10",
            " exit",
            "interface vlan-if 10",
            " ip address 192.168.10.1/24",
            " exit",
            "exit",
        ],
    },
    {
        "title": "动态聚合上联",
        "description": "bond 1 做 LACP 动态聚合，Trunk 放行 VLAN 10 和 20。",
        "steps": [
            "conf-mode",
            "vlan 10",
            " exit",
            "vlan 20",
            " exit",
            "interface bond 1",
            " bond mode dynamic",
            " bond load-sharing mode source-destination-ip",
            " switchport mode trunk",
            " switchport trunk allowed vlan 10,20",
            " exit",
            "interface gige0_23",
            " bond group 1",
            " exit",
            "interface gige0_24",
            " bond group 1",
            " exit",
            "exit",
        ],
    },
]
