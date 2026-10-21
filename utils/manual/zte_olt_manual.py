#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
中兴 OLT（ZXA10 C300/C320 与 C600）命令速查。

只收录生成器会写成可粘贴命令、并且能在公开手册里对上的写法。
C300/C320 依据命令手册 SJ-20130520164529-010 和配置手册 SJ-20130520164529-007。
C600 的接口名依据维护说明里的 xgei-、gpon_olt-、interface vlan66、mgmt_eth。
ONU 注册只作为注释里的手册示例，生成器不会凭空写 onu 命令。
口令 LabOnly1 是占位符，不是设备口令。
"""

ZTE_OLT_COMMANDS = {
    "基础配置": {
        "系统与登录": [
            {"name": "进入全局配置", "command": "configure terminal", "description": "从特权模式 ZXAN# 进入全局配置。回到特权模式用 end", "example": "configure terminal"},
            {"name": "主机名", "command": "hostname <name>", "description": "C300 命令手册 1.12。1 到 32 个字符，立即生效。缺省主机名是 ZXAN", "example": "hostname OLT-C300"},
            {"name": "特权口令", "command": "enable secret 0 <password>", "description": "明文 3 到 16 字符。和 enable secret <password> 等价。密文 enable secret 5 只在加载配置文件时使用，脚本不写", "example": "enable secret 0 LabOnly1"},
            {"name": "打开 SSH", "command": "ssh server enable", "description": "C300/C320 命令手册 30.4 的命令名。配置手册第 15 章接着写版本和本地认证", "example": "ssh server enable"},
            {"name": "SSH 版本", "command": "ssh server version 2", "description": "配置手册第 15 章的示例是版本 2。界面改成 1 时只留注释", "example": "ssh server version 2"},
            {"name": "SSH 本地认证", "command": "ssh server authentication mode local\nssh server authentication type pap", "description": "和版本命令同一节。本地用户命令 C300 与 C600 不一致，所以不写 username", "example": "ssh server authentication mode local\nssh server authentication type pap"},
            {"name": "保存", "command": "write", "description": "C600 配置说明在特权模式执行 write。脚本里这行是注释，不会自动保存，也不会登录设备", "example": "end\nwrite"},
        ],
        "管理地址": [
            {"name": "C300 带外口", "command": "interface vlan mng1\n ip address <ip> <mask>", "description": "命令手册 1.14 的示例。界面里的 mng1 会收成 vlan mng1", "example": "interface vlan mng1\n ip address 10.200.0.2 255.255.255.0\n exit"},
            {"name": "C300 三层 VLAN", "command": "interface vlan <id>\n ip address <ip> <mask>", "description": "配置手册的 in-band 示例。先 vlan <id>。界面里的 Vlanif10 会改成 vlan 10", "example": "vlan 100\nexit\ninterface vlan 100\n ip address 10.1.1.1 255.255.255.0\n exit"},
            {"name": "C600 带外口", "command": "interface mgmt_eth\n ip address <ip> <mask>", "description": "C600 配置说明的带外口。不要写成 C300 的 vlan mng1", "example": "interface mgmt_eth\n ip address 11.1.1.1 255.255.255.0\n exit"},
            {"name": "C600 三层 VLAN", "command": "interface vlan<id>", "description": "C600 维护说明写作 interface vlan66，中间没有空格。和 C300 的 interface vlan 10 不同", "example": "vlan 100\nexit\ninterface vlan100\n ip address 10.1.1.1 255.255.255.0\n exit"},
            {"name": "默认路由", "command": "ip route 0.0.0.0 0.0.0.0 <nexthop>", "description": "目的、掩码、下一跳。C300 配置手册和 C600 配置说明都是这个顺序。不写管理距离", "example": "ip route 0.0.0.0 0.0.0.0 10.200.0.1"},
        ],
    },
    "VLAN与PON": {
        "上联 VLAN": [
            {"name": "创建 VLAN", "command": "vlan <id>", "description": "进入 VLAN 配置后 exit。名称只写在注释里，全局示例没有 name", "example": "vlan 100\nexit"},
            {"name": "Trunk", "command": "switchport mode trunk\nswitchport vlan <list> tag", "description": "写在 gei_ 或 xgei- 上。连续 VLAN 收成 100,102-110。缺省模式就是 trunk", "example": "interface gei_1/19/1\n no shutdown\n switchport mode trunk\n switchport vlan 100 tag\n exit"},
            {"name": "Hybrid", "command": "switchport mode hybrid\nswitchport vlan <id> tag", "description": "界面只填一个 VLAN 时按手册示例写成 tag", "example": "interface xgei-1/1/1\n no shutdown\n switchport mode hybrid\n switchport vlan 100 tag\n exit"},
            {"name": "PVID", "command": "switchport default vlan <id>", "description": "设置 PVID。上联口不能配 access，界面的 Access VLAN 改用这条", "example": "interface gei_1/19/1\n switchport default vlan 100\n exit"},
            {"name": "打开上联口", "command": "no shutdown", "description": "C300 命令手册写在二层 FE/GE/10GE。C600 上联和 PON 口缺省是 shutdown", "example": "interface xgei-1/1/1\n no shutdown\n exit"},
        ],
        "PON 接口名": [
            {"name": "C300 PON 口", "command": "interface gpon-olt_<架>/<槽>/<口>", "description": "命令手册 1.13 的示例是 gpon-olt_1/5/1。EPON 是 epon-olt_1/14/1。这里不写 switchport", "example": "interface gpon-olt_1/1/1\n exit"},
            {"name": "C300 ONU 接口", "command": "interface gpon-onu_<架>/<槽>/<口>:<编号>", "description": "注册成功之后进入 ONU 接口。命令手册在这个接口上有 no shutdown 示例", "example": "interface gpon-onu_1/5/1:1\n no shutdown\n exit"},
            {"name": "C600 PON 口", "command": "interface gpon_olt-<架>/<槽>/<口>", "description": "维护说明的示例是 gpon_olt-1/1/1，并在这个口上 no shutdown。不要写成 C300 的 gpon-olt_", "example": "interface gpon_olt-1/1/1\n no shutdown\n exit"},
            {"name": "ONU 注册示例", "command": "onu <编号> type <类型> sn <SN>", "description": "C300 命令手册 1.13 和 C600 GPON 操作说明都有这条。生成器只把它留在注释里，因为界面没有类型和 SN。C600 另有 loid", "example": "! interface gpon-olt_1/5/1\n! onu 1 type ZTE-F622 sn ZTEG00000001"},
        ],
    },
    "路由": {
        "静态路由": [
            {"name": "静态路由", "command": "ip route <dest> <mask> <nexthop>", "description": "C300 配置手册示例是 ip route 3.3.3.3 255.255.255.255 10.1.1.2。必须有下一跳，不写出接口，不写优先级", "example": "ip route 198.51.100.0 255.255.255.0 10.1.1.254"},
        ],
    },
}

ZTE_OLT_CASES = [
    {
        "title": "C300 带外管理与上联",
        "description": "带外口 vlan mng1，gei_1/19/1 以 Trunk 放行 VLAN 100。gpon-olt 上的 ONU 注册只留注释。口令 LabOnly1 是占位符。从 ZXAN# 粘贴。",
        "steps": [
            "configure terminal",
            "hostname OLT-C300",
            "enable secret 0 LabOnly1",
            "ssh server enable",
            "ssh server version 2",
            "ssh server authentication mode local",
            "ssh server authentication type pap",
            "vlan 100",
            "exit",
            "interface vlan mng1",
            " ip address 10.200.0.2 255.255.255.0",
            " exit",
            "ip route 0.0.0.0 0.0.0.0 10.200.0.1",
            "interface gei_1/19/1",
            " no shutdown",
            " switchport mode trunk",
            " switchport vlan 100 tag",
            " exit",
            "interface gpon-olt_1/1/1",
            "! ONU 注册未写。手册示例：onu 1 type ZTE-F622 sn ZTEG00000001",
            "exit",
            "end",
        ],
    },
    {
        "title": "C600 带内管理与 PON 口",
        "description": "三层口按 C600 写成 interface vlan100，上联是 xgei-1/1/1，PON 是 gpon_olt-1/1/1。不要和 C300 的下划线接口名混在一份脚本里。",
        "steps": [
            "configure terminal",
            "hostname OLT-C600",
            "ssh server enable",
            "ssh server version 2",
            "ssh server authentication mode local",
            "ssh server authentication type pap",
            "vlan 100",
            "exit",
            "interface vlan100",
            " ip address 10.1.1.1 255.255.255.0",
            " exit",
            "ip route 0.0.0.0 0.0.0.0 10.1.1.254",
            "interface xgei-1/1/1",
            " no shutdown",
            " switchport mode trunk",
            " switchport vlan 100 tag",
            " exit",
            "interface gpon_olt-1/1/1",
            " no shutdown",
            "! ONU 注册未写。手册示例：onu 1 type ZTE-F601 sn <SN>",
            "exit",
            "ip route 198.51.100.0 255.255.255.0 10.1.1.254",
            "end",
        ],
    },
]
