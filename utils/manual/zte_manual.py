#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
中兴 ZXR10 经典 ZXROS 命令速查。

覆盖本工具会生成的交换机场景。命令取自 ZXR10 5200/5900/8900 常见写法，
不是 5900E/5960 ROSNG，也不是 OLT。
"""

ZTE_COMMANDS = {
    "基础配置": {
        "系统与登录": [
            {"name": "进入全局配置", "command": "configure terminal", "description": "从特权模式 ZXR10# 进入全局配置", "example": "configure terminal"},
            {"name": "主机名", "command": "hostname <name>", "description": "立即生效，1 到 32 个字符", "example": "hostname ZTE-Core-01"},
            {"name": "特权密码", "command": "enable secret {0|5} <password>", "description": "0 为明文，5 为设备上的密文", "example": "enable secret 0 Admin@123"},
            {"name": "本地用户", "command": "username <name> password <password> privilege <0-15>", "description": "创建登录用户并指定权限", "example": "username admin password Admin@123 privilege 15"},
            {"name": "SSH 服务", "command": "ssh server enable", "description": "打开 SSH 服务器。经典版本默认关闭", "example": "ssh server enable"},
            {"name": "登录横幅", "command": "banner incoming <结束符>", "description": "设置登录提示，结束符不能出现在正文里", "example": "banner incoming #\nAuthorized only\n#"},
            {"name": "保存配置", "command": "write", "description": "在特权模式保存运行配置", "example": "end\nwrite"},
        ],
        "管理与时间": [
            {"name": "三层 VLAN 口", "command": "interface vlan <id>", "description": "ZXR10 的 SVI 写法，不是 Vlanif", "example": "interface vlan 1\n ip address 192.168.1.1 255.255.255.0\n no shutdown"},
            {"name": "默认路由", "command": "ip route 0.0.0.0 0.0.0.0 <nexthop> [distance]", "description": "静态默认路由，distance 为管理距离", "example": "ip route 0.0.0.0 0.0.0.0 192.168.1.254"},
            {"name": "时区", "command": "clock timezone <name> <hours>", "description": "特权模式命令，要写在 configure terminal 之前", "example": "clock timezone Beijing 8"},
            {"name": "NTP", "command": "ntp enable\nntp server <ip>", "description": "把交换机作为 NTP 客户端", "example": "ntp enable\nntp server 10.0.0.100"},
            {"name": "SNMP 团体字", "command": "snmp-server community <name> {ro|rw}", "description": "v1/v2c 团体字", "example": "snmp-server community public ro"},
            {"name": "Syslog", "command": "syslog server <ip>", "description": "把日志送到后台服务器", "example": "logging on\nsyslog on\nsyslog server 10.0.0.200"},
            {"name": "DNS", "command": "ip name-server <ip>", "description": "指定 DNS 服务器", "example": "ip name-server 223.5.5.5\nip domain-name example.com"},
        ],
    },
    "VLAN配置": {
        "VLAN 与端口": [
            {"name": "创建 VLAN", "command": "vlan <id>", "description": "创建 VLAN 并进入 VLAN 配置模式", "example": "vlan 10\n name Office\n exit"},
            {"name": "Access", "command": "switchport mode access\nswitchport access vlan <id>", "description": "端口只属于一个 VLAN", "example": "interface gei_1/1\n switchport mode access\n switchport access vlan 10"},
            {"name": "Trunk", "command": "switchport mode trunk\nswitchport trunk vlan <list>", "description": "允许多个 VLAN，列表用逗号", "example": "interface gei_1/24\n switchport mode trunk\n switchport trunk vlan 10,20\n switchport trunk native vlan 1"},
            {"name": "Hybrid", "command": "switchport mode hybrid\nswitchport hybrid vlan <id> untag", "description": "Hybrid 端口可同时带 tag 和 untag", "example": "interface gei_1/2\n switchport mode hybrid\n switchport hybrid native vlan 10\n switchport hybrid vlan 10 untag"},
            {"name": "生成树", "command": "spanning-tree enable\nspanning-tree mode {sstp|rstp|mstp}", "description": "全局默认关闭 STP。界面里的 stp 会写成 sstp", "example": "spanning-tree enable\nspanning-tree mode rstp"},
        ],
    },
    "路由配置": {
        "路由协议": [
            {"name": "静态路由", "command": "ip route <prefix> <mask> <nexthop> [distance]", "description": "全局静态路由", "example": "ip route 10.2.0.0 255.255.0.0 10.1.1.2 60"},
            {"name": "OSPF", "command": "router ospf <id>", "description": "进入 OSPF，再写 router-id 和 network", "example": "router ospf 1\n router-id 1.1.1.1\n network 10.0.0.0 0.0.0.255 area 0"},
            {"name": "BGP", "command": "router bgp <as>", "description": "建立 BGP 邻居", "example": "router bgp 65001\n bgp router-id 1.1.1.1\n neighbor 10.1.1.2 remote-as 65002"},
            {"name": "RIP", "command": "router rip", "description": "RIP 版本和网络", "example": "router rip\n version 2\n network 10.0.0.0"},
        ],
    },
    "安全配置": {
        "ACL 与端口安全": [
            {"name": "标准 ACL", "command": "acl standard number <id>", "description": "8900 手册中的标准 ACL。更老的版本可能写成 acl basic", "example": "acl standard number 10\n rule 5 permit 192.168.1.0 0.0.0.255\n exit"},
            {"name": "扩展 ACL", "command": "acl extend number <id>", "description": "可匹配协议和端口", "example": "acl extend number 100\n rule 10 permit tcp any any eq 80\n exit"},
            {"name": "应用 ACL", "command": "ip access-group <id> {in|out}", "description": "在接口上应用 ACL", "example": "interface gei_1/1\n ip access-group 100 in"},
            {"name": "端口安全", "command": "switchport port-security", "description": "限制接入 MAC 数量。部分核心版本命令名不同，下发前请对照手册", "example": "interface gei_1/1\n switchport port-security\n switchport port-security maximum 1\n switchport port-security violation shutdown"},
            {"name": "DHCP Snooping", "command": "ip dhcp snooping", "description": "按 VLAN 开启，信任端口单独标记", "example": "ip dhcp snooping\nip dhcp snooping vlan 10\ninterface gei_1/24\n ip dhcp snooping trust"},
            {"name": "ARP 检测", "command": "ip arp inspection vlan <id>", "description": "在指定 VLAN 做动态 ARP 检测", "example": "ip arp inspection vlan 10\ninterface gei_1/24\n ip arp inspection trust"},
            {"name": "风暴抑制", "command": "storm-control broadcast pps <n>", "description": "按包每秒限制广播或组播", "example": "interface gei_1/1\n storm-control broadcast pps 1000"},
        ],
    },
    "接口配置": {
        "聚合与链路": [
            {"name": "Smartgroup", "command": "interface smartgroup<id>", "description": "创建聚合组。成员口用 smartgroup <id> mode", "example": "interface smartgroup1\n switchport mode trunk\n exit\ninterface gei_1/1\n smartgroup 1 mode active"},
            {"name": "LLDP", "command": "lldp enable\nlldp hellotime <sec>\nlldp holdtime <multiple>", "description": "holdtime 是 hello 的倍数，不是秒", "example": "lldp enable\nlldp hellotime 30\nlldp holdtime 4"},
            {"name": "环路检测", "command": "loop-detect interface <port> enable", "description": "按端口开启。全局动作是 loop-detect portstate", "example": "loop-detect portstate block\nloop-detect interface gei_1/1 enable"},
            {"name": "PoE", "command": "power inline {auto|force}", "description": "接入型交换机常见写法。8900 核心通常没有 PoE", "example": "interface gei_1/1\n power inline auto\n power inline priority low"},
            {"name": "端口限速", "command": "rate-limit {input|output} <kbps>", "description": "单位 kbps。个别版本要改用 qos car", "example": "interface gei_1/1\n rate-limit input 10000\n rate-limit output 10000"},
        ],
    },
}

ZTE_CASES = [
    {
        "title": "接入交换机基础配置",
        "description": "主机名、管理 SVI、SSH、Access/Trunk 和 RSTP。从 ZXR10# 粘贴。",
        "steps": [
            "clock timezone Beijing 8",
            "configure terminal",
            "hostname ZTE-Access-01",
            "enable secret 0 Admin@123",
            "username admin password Admin@123 privilege 15",
            "ssh server enable",
            "interface vlan 1",
            " ip address 192.168.1.1 255.255.255.0",
            " no shutdown",
            " exit",
            "ip route 0.0.0.0 0.0.0.0 192.168.1.254",
            "vlan 10",
            " name Office",
            " exit",
            "interface gei_1/1",
            " switchport mode access",
            " switchport access vlan 10",
            " no shutdown",
            " exit",
            "interface gei_1/24",
            " switchport mode trunk",
            " switchport trunk vlan 10,20",
            " switchport trunk native vlan 1",
            " exit",
            "spanning-tree enable",
            "spanning-tree mode rstp",
            "end",
        ],
    },
    {
        "title": "ACL 与聚合口",
        "description": "扩展 ACL 限制 Web，并把两个千兆口放进 smartgroup1。",
        "steps": [
            "configure terminal",
            "acl extend number 100",
            " rule 10 permit tcp any any eq 80",
            " rule 20 deny ip any any",
            " exit",
            "interface gei_1/1",
            " ip access-group 100 in",
            " exit",
            "interface smartgroup1",
            " switchport mode trunk",
            " switchport trunk vlan 10,20",
            " exit",
            "interface gei_1/23",
            " smartgroup 1 mode active",
            " exit",
            "interface gei_1/24",
            " smartgroup 1 mode active",
            " exit",
            "end",
        ],
    },
]
