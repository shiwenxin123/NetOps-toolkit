#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
迪普 FW1000 Conplat 命令速查。

只收录本工具会生成、并且能在公开命令参考或 FW1000 现场配置里对上的命令。
LSW 交换机、ADX 应用交付不在这里。
"""

DPTECH_COMMANDS = {
    "基础配置": {
        "系统与登录": [
            {"name": "进入配置视图", "command": "conf-mode", "description": "从用户视图 DPTECH 进入配置视图 [DPTECH]", "example": "conf-mode"},
            {"name": "系统名", "command": "sysname <name>", "description": "1 到 20 位字母、数字、点、下划线或短横线", "example": "sysname DP-FW-01"},
            {"name": "配置视图密码", "command": "password conf-mode <password>", "description": "从用户视图进入配置视图时要输入的密码", "example": "password conf-mode Admin@123"},
            {"name": "管理员", "command": "local-user <name> password plain-text-password <password>", "description": "命令参考中的 password plain-text-password 会交互读入。单行写法来自 FW1000 现场配置，避免后续行被当成密码", "example": "local-user admin password plain-text-password Admin@123"},
            {"name": "密文密码", "command": "password encrypted-password <cipher>", "description": "在管理员视图写入设备上已有的密文", "example": "local-user admin\n password encrypted-password CipherText\n exit"},
            {"name": "SSH", "command": "ssh enable\nssh port <1-65535>", "description": "缺省关闭 SSH。端口不是 22 时再写 ssh port", "example": "ssh enable\nssh port 830"},
            {"name": "登录横幅", "command": "banner motd <结束符>", "description": "结束符是正文里不能出现的一个字符。正文不要包含 : / \\ ,", "example": "banner motd #\nAuthorized only\n#"},
            {"name": "保存", "command": "write file", "description": "在配置视图保存。不是 write", "example": "conf-mode\nwrite file"},
        ],
        "管理与时间": [
            {"name": "管理口", "command": "interface meth0_0", "description": "缺省带外管理口。地址用前缀长度", "example": "interface meth0_0\n ip address 192.168.0.1/24\n no shutdown"},
            {"name": "业务口", "command": "interface gige0_1", "description": "千兆口名字是 gige槽位_端口，不是 GigabitEthernet", "example": "interface gige0_1\n ip address 10.1.1.1/24\n no shutdown"},
            {"name": "默认路由", "command": "ip route 0.0.0.0/0 <interface> <nexthop>", "description": "前缀用斜线。示例同时带出接口和下一跳", "example": "ip route 0.0.0.0/0 gige0_4 122.1.1.2"},
            {"name": "时区", "command": "clock timezone GMT <offset>", "description": "在配置视图执行。东八区偏移是 8", "example": "clock timezone GMT 8"},
            {"name": "NTP", "command": "ntp server <ip> [prefer]", "description": "最多 8 台。prefer 表示优先", "example": "ntp server 10.0.0.100 prefer"},
            {"name": "SNMP", "command": "snmp-agent version (1|2c|3|all)\nsnmp-agent community <name> {ro|rw}", "description": "团体字不能带空格", "example": "snmp-agent version 2c\nsnmp-agent community public ro\nsnmp-agent location Lab"},
            {"name": "Trap", "command": "snmp-agent trap target-host address <ip> target-port <port>", "description": "目的端口缺省 162", "example": "snmp-agent trap target-host address 10.0.0.9 target-port 162"},
            {"name": "日志", "command": "logging security-policy enable\nlogging security-policy host <ip> port 514", "description": "FW1000 现场配置里的安全策略日志", "example": "logging security-policy enable\nlogging security-policy host 10.0.0.200 port 514"},
            {"name": "DNS", "command": "ip name-server <ip> [<ip>]", "description": "可以写多个地址", "example": "ip name-server 223.5.5.5 223.6.6.6"},
        ],
    },
    "VLAN配置": {
        "VLAN 与接口": [
            {"name": "创建 VLAN", "command": "vlan <id>", "description": "进入 VLAN 视图。本工具不写 name，命令参考没有核对到这个子命令", "example": "vlan 10\n exit"},
            {"name": "三层 VLAN 口", "command": "interface vlan-if <id>", "description": "不是 Vlanif。界面里的 Vlanif10 会改成 vlan-if 10", "example": "interface vlan-if 10\n ip address 192.168.10.1/24\n no shutdown"},
            {"name": "Access", "command": "switchport mode access\nswitchport access vlan <id>", "description": "二层口只属于一个 VLAN", "example": "interface gige0_1\n switchport mode access\n switchport access vlan 10"},
            {"name": "Trunk", "command": "switchport mode trunk\nswitchport trunk allowed vlan <list>\nswitchport trunk native vlan <id>", "description": "允许 VLAN 用逗号", "example": "interface gige0_24\n switchport mode trunk\n switchport trunk allowed vlan 10,20\n switchport trunk native vlan 1"},
        ],
    },
    "安全配置": {
        "安全域与包过滤": [
            {"name": "安全域", "command": "security-zone <name>", "description": "预定义 Trust / DMZ / Untrust，优先级 85 / 50 / 5，不能改。接口必须加入安全域才能转发", "example": "security-zone Trust\n interface gige0_1\n exit"},
            {"name": "地址对象", "command": "address-object <name> <ip>/<prefix>", "description": "包过滤要先有地址对象", "example": "address-object a100s5 192.168.1.0/24"},
            {"name": "服务对象", "command": "service-object <name> protocol <tcp|udp> src-port 0 to 65535 dst-port <port>", "description": "一条服务对象对应一个目的端口", "example": "service-object s100p10 protocol tcp src-port 0 to 65535 dst-port 80"},
            {"name": "安全策略", "command": "security-policy <name> src-zone any dst-zone any action {permit|deny}", "description": "每条匹配条件单独一行，并重复策略名和安全域。src-address 与已核对的 dst-address 同句式", "example": "security-policy pf100r10 src-zone any dst-zone any dst-address address-object a100d10\nsecurity-policy pf100r10 src-zone any dst-zone any service service-object s100p10\nsecurity-policy pf100r10 src-zone any dst-zone any action permit"},
            {"name": "ARP 源抑制", "command": "arp source-suppression enable", "description": "全局命令。按 VLAN 的动态 ARP 检测没有写入脚本", "example": "arp source-suppression enable"},
        ],
    },
    "接口配置": {
        "聚合": [
            {"name": "聚合口", "command": "interface bond <id>\n bond mode dynamic", "description": "已核对的模式关键字是 dynamic。manual / lacp-static 只在脚本里注释", "example": "interface bond 1\n bond mode dynamic\n description to_core\n exit"},
            {"name": "成员口", "command": "bond group <id>", "description": "写在物理口下，不是写在 bond 口下", "example": "interface gige0_5\n bond group 1\n exit"},
        ],
    },
}

DPTECH_CASES = [
    {
        "title": "带外管理与 SSH",
        "description": "从用户视图粘贴。管理口 meth0_0，打开 SSH，并指向一台 NTP。",
        "steps": [
            "conf-mode",
            "sysname DP-FW-01",
            "password conf-mode Admin@123",
            "local-user admin password plain-text-password Admin@123",
            "ssh enable",
            "interface meth0_0",
            " ip address 192.168.0.1/24",
            " no shutdown",
            " exit",
            "ip route 0.0.0.0/0 meth0_0 192.168.0.254",
            "clock timezone GMT 8",
            "ntp server 10.0.0.100 prefer",
            "ip name-server 223.5.5.5",
            "security-zone Trust",
            " interface meth0_0",
            " exit",
            "end",
            "conf-mode",
            "write file",
        ],
    },
    {
        "title": "业务口、安全域和 Web 放通",
        "description": "gige0_1 进 Trust，并用地址对象加服务对象放通到 192.168.10.10 的 TCP 80。",
        "steps": [
            "conf-mode",
            "interface gige0_1",
            " ip address 192.168.10.1/24",
            " no shutdown",
            " exit",
            "security-zone Trust",
            " interface gige0_1",
            " exit",
            "address-object a100d10 192.168.10.10/32",
            "service-object s100p10 protocol tcp src-port 0 to 65535 dst-port 80",
            "security-policy pf100r10 src-zone any dst-zone any dst-address address-object a100d10",
            "security-policy pf100r10 src-zone any dst-zone any service service-object s100p10",
            "security-policy pf100r10 src-zone any dst-zone any action permit",
            "end",
        ],
    },
]
