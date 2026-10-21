#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
中兴 ZXR10 新一代 ROSNG 命令速查。

只收录生成器会写出、并且能在 ZXR10 5900E V3.00.11 配置手册里对上的命令。
5960/9900 与 5900E 同属 ROSNG。经典 ZXROS 的 gei_1/1 不在这里。
口令 Placeholder1 是占位符，不是设备口令。
"""

ZTE_ROSNG_COMMANDS = {
    "基础配置": {
        "系统与登录": [
            {"name": "进入全局配置", "command": "configure terminal", "description": "从特权模式 ZXR10# 进入全局配置。回到特权模式用 end", "example": "configure terminal"},
            {"name": "主机名", "command": "hostname <name>", "description": "立即生效，1 到 32 个字符", "example": "hostname ZTE-ROSNG-01"},
            {"name": "本地用户", "command": "system-user\n user-name <name>\n  password <password>\n  bind authentication-template 1\n  bind authorization-template 1", "description": "5900E 安全手册 6.4.1 的本地认证示例。还要绑定 AAA 模板 2001，类型为 local。占位口令请在下发前修改", "example": "system-user\n user-name netops\n  password Placeholder1\n  bind authentication-template 1\n  bind authorization-template 1\n  exit"},
            {"name": "授权级别", "command": "local-privilege-level <0-15>", "description": "写在 authorization-template 下。示例用 15", "example": "authorization-template 1\n bind aaa-authorization-template 2001\n local-privilege-level 15\n exit"},
            {"name": "SSH", "command": "ssh server enable", "description": "打开 SSH。非默认端口只有 listen 22 或 49152-65535 会写入", "example": "ssh server enable"},
            {"name": "SSH 监听端口", "command": "ssh server enable listen <port>", "description": "手册允许 22，或 49152 到 65535。2222 这类端口只留注释", "example": "ssh server enable listen 50000"},
            {"name": "关闭 SSH", "command": "ssh server disable", "description": "只有界面明确关掉 SSH 时才写", "example": "ssh server disable"},
            {"name": "登录横幅", "command": "banner incoming <结束符>", "description": "5900E 的 running-config 用 banner incoming。结束符不能出现在正文里", "example": "banner incoming #\nLab only\n#"},
            {"name": "保存", "command": "write", "description": "特权模式命令。脚本里这行是注释，不会自动保存，也不会登录设备", "example": "end\nwrite"},
        ],
        "管理地址": [
            {"name": "三层 VLAN 口", "command": "interface vlan<id>", "description": "地址用点分掩码。界面里的 Vlanif10 或 vlan 10 会改成 vlan10", "example": "interface vlan1\n ip address 192.168.1.1 255.255.255.0\n exit"},
            {"name": "默认路由", "command": "ip route 0.0.0.0 0.0.0.0 <interface> <nexthop>", "description": "管理网关按手册的出接口加下一跳写法。也可以只写下一跳", "example": "ip route 0.0.0.0 0.0.0.0 vlan1 192.168.1.254"},
        ],
    },
    "VLAN配置": {
        "VLAN 与端口": [
            {"name": "进入 VLAN 配置", "command": "switchvlan-configuration", "description": "VLAN 和 switchport 都写在这个模式里，不是接口配置模式", "example": "switchvlan-configuration\n vlan 10\n  exit\n exit"},
            {"name": "创建 VLAN", "command": "vlan <id>", "description": "名称只写在注释里。show vlan 显示的是设备自动名称，手册步骤没有 name", "example": "switchvlan-configuration\n vlan 10\n  exit"},
            {"name": "Access", "command": "switchport mode access\nswitchport access vlan <id>", "description": "写在 switchvlan 的 interface 下。默认模式就是 access", "example": "interface gei-0/1/1/1\n switchport mode access\n switchport access vlan 10\n exit"},
            {"name": "Trunk", "command": "switchport mode trunk\nswitchport trunk vlan <list>\nswitchport trunk native vlan <id>", "description": "连续 VLAN 收成 10-12。不连续的拆成多条，不写逗号", "example": "interface gei-0/1/1/24\n switchport mode trunk\n switchport trunk vlan 10\n switchport trunk vlan 20\n switchport trunk native vlan 1\n exit"},
            {"name": "Hybrid", "command": "switchport mode hybrid\nswitchport hybrid native vlan <id>\nswitchport hybrid vlan <id> untag", "description": "界面只填一个 VLAN 时按 untag 写。手册另有 tag 写法", "example": "interface gei-0/1/1/2\n switchport mode hybrid\n switchport hybrid native vlan 20\n switchport hybrid vlan 20 untag\n exit"},
            {"name": "打开物理口", "command": "no shutdown", "description": "写在全局的 interface 下，不写在 switchvlan 模式里", "example": "interface gei-0/1/1/1\n no shutdown\n exit"},
        ],
    },
    "路由与聚合": {
        "静态路由和 Smartgroup": [
            {"name": "静态路由", "command": "ip route <dest> <mask> <nexthop> [distance]", "description": "管理距离 1 到 255，缺省 1 时不写。必须有下一跳", "example": "ip route 198.51.100.0 255.255.255.0 192.0.2.1"},
            {"name": "带出接口的静态路由", "command": "ip route <dest> <mask> <interface> <nexthop>", "description": "出接口用 vlan1 这种名字。带出接口时，管理距离只留在注释里", "example": "ip route 198.51.100.0 255.255.255.0 vlan10 192.0.2.1"},
            {"name": "创建聚合口", "command": "interface smartgroup<id>\n switch attribute enable", "description": "先把 smartgroup 设成二层口。编号 1 到 128，每个组最多 8 个成员", "example": "interface smartgroup1\n switch attribute enable\n exit"},
            {"name": "LACP", "command": "lacp\n interface smartgroup<id>\n  lacp mode 802.3ad\n interface <port>\n  smartgroup <id> mode active", "description": "界面的 lacp-static 和 lacp-dynamic 都按手册示例写成 802.3ad 加 active。对端要 passive 时再改成员模式", "example": "lacp\n interface smartgroup1\n  lacp mode 802.3ad\n  exit\n interface gei-0/1/1/23\n  smartgroup 1 mode active\n  exit\n exit"},
            {"name": "静态聚合", "command": "lacp mode on\nsmartgroup <id> mode on", "description": "对应界面的 manual。两端都要 on，不跑 LACP", "example": "lacp\n interface smartgroup1\n  lacp mode on\n  exit\n interface gei-0/1/1/23\n  smartgroup 1 mode on\n  exit"},
        ],
    },
}

ZTE_ROSNG_CASES = [
    {
        "title": "接入 VLAN 与 SSH",
        "description": "管理地址在 vlan1，gei-0/1/1/1 划进 VLAN 10。口令 Placeholder1 是占位符。从 ZXR10# 粘贴。",
        "steps": [
            "configure terminal",
            "hostname ZTE-ROSNG-01",
            "system-user",
            " user-name netops",
            "  password Placeholder1",
            "  bind authentication-template 1",
            "  bind authorization-template 1",
            "  exit",
            " authentication-template 1",
            "  bind aaa-authentication-template 2001",
            "  exit",
            " authorization-template 1",
            "  bind aaa-authorization-template 2001",
            "  local-privilege-level 15",
            "  exit",
            " exit",
            "aaa-authentication-template 2001",
            " aaa-authentication-type local",
            " exit",
            "aaa-authorization-template 2001",
            " aaa-authorization-type none",
            " exit",
            "ssh server enable",
            "interface vlan1",
            " ip address 192.168.1.1 255.255.255.0",
            " exit",
            "ip route 0.0.0.0 0.0.0.0 vlan1 192.168.1.254",
            "interface gei-0/1/1/1",
            " no shutdown",
            " exit",
            "switchvlan-configuration",
            " vlan 10",
            "  exit",
            " interface gei-0/1/1/1",
            "  switchport mode access",
            "  switchport access vlan 10",
            "  exit",
            " exit",
            "interface vlan10",
            " ip address 192.168.10.1 255.255.255.0",
            " exit",
            "end",
        ],
    },
    {
        "title": "聚合上联与静态路由",
        "description": "smartgroup1 做 802.3ad，Trunk 放行 VLAN 10 和 20，并写一条文档网段的静态路由。",
        "steps": [
            "configure terminal",
            "interface smartgroup1",
            " switch attribute enable",
            " exit",
            "lacp",
            " interface smartgroup1",
            "  lacp mode 802.3ad",
            "  exit",
            " interface gei-0/1/1/23",
            "  smartgroup 1 mode active",
            "  exit",
            " interface gei-0/1/1/24",
            "  smartgroup 1 mode active",
            "  exit",
            " exit",
            "switchvlan-configuration",
            " interface smartgroup1",
            "  switchport mode trunk",
            "  switchport trunk vlan 10",
            "  switchport trunk vlan 20",
            "  exit",
            " exit",
            "ip route 198.51.100.0 255.255.255.0 192.0.2.1",
            "end",
        ],
    },
]
