#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
华三 SecPath 服务器负载均衡命令速查。

只收录生成器会写出、并且能在《01-负载均衡命令》或
《服务器负载均衡配置》开局示例里对上的命令。
交换机的 switchport、迪普 ADX 的 Web 配置流程不在这里。
"""

H3C_LB_COMMANDS = {
    "基础配置": {
        "系统与接口": [
            {"name": "进入系统视图", "command": "system-view", "description": "从用户视图进入系统视图。结束后用 quit 回到用户视图。以 # 开头的行是说明，命令行里输入 # 会退回用户视图", "example": "system-view"},
            {"name": "系统名", "command": "sysname <name>", "description": "配置指导写明用 sysname 改设备名。1 到 64 位字母、数字、点、下划线或短横线", "example": "sysname H3C-LB-01"},
            {"name": "接口地址", "command": "interface GigabitEthernet <slot>\n ip address <ip> <mask>", "description": "掩码用点分格式。Route-Aggregation 和 Vlan-interface 也按同样的 ip address 写法", "example": "interface GigabitEthernet 1/0/1\n ip address 192.168.1.1 255.255.255.0\n quit"},
            {"name": "静态路由", "command": "ip route-static <dest> <mask> <nexthop>", "description": "默认路由的掩码是 0.0.0.0。示例只带下一跳，不带出接口和管理距离", "example": "ip route-static 0.0.0.0 0.0.0.0 192.168.1.254"},
            {"name": "三层聚合", "command": "interface Route-Aggregation <id>\n port link-aggregation group <id>", "description": "成员口上写 port link-aggregation group。没有核对 link-aggregation mode，模式只留注释", "example": "interface Route-Aggregation 1\n quit\ninterface GigabitEthernet 1/0/3\n port link-aggregation group 1\n quit"},
            {"name": "保存", "command": "save", "description": "用户视图执行，会交互确认。脚本里这行是注释，不会自动保存，也不会重启", "example": "# save"},
        ],
    },
    "服务器负载均衡": {
        "实服务器与虚服务器": [
            {"name": "健康检查", "command": "nqa template icmp <name>\n probe <name>", "description": "先建 ICMP 类型的 NQA 模板，再在实服务组里 probe。其他检查方式没有写成命令", "example": "nqa template icmp icmp1\n quit\nserver-farm web\n probe icmp1\n quit"},
            {"name": "实服务组", "command": "server-farm <name>\n predictor <algorithm>", "description": "已核对 round-robin、random、least-connection、hash address source、hash address destination。缺省 NAT 是开的，脚本不写 transparent enable", "example": "server-farm web\n predictor round-robin\n quit"},
            {"name": "实服务器", "command": "real-server <name>\n ip address <ip>\n port <port>\n weight <1-255>\n server-farm <farm>", "description": "权值 1 到 255，缺省 100。端口 0 表示沿用报文原来的端口。地址不能是环回、组播或 0 开头", "example": "real-server rs1\n ip address 192.168.10.11\n port 80\n weight 150\n server-farm web\n quit"},
            {"name": "虚服务器", "command": "virtual-server <name> type <tcp|udp|http|ip>\n virtual ip address <vip>\n port <port>\n default server-farm <farm>\n service enable", "description": "虚服务器缺省关闭，service enable 只打开虚服务，不是重启设备。TCP/UDP/IP 缺省端口 0 时不写 port；HTTP 缺省端口是 80", "example": "virtual-server vs-web type tcp\n virtual ip address 192.168.1.80\n port 80\n default server-farm web\n service enable\n quit"},
            {"name": "同网段免费 ARP", "command": "arp-nd interface <type> <number>", "description": "虚地址和设备接口在同一网段时必须指定接口。不在同一网段则不写这条", "example": "virtual-server vs-web type tcp\n virtual ip address 192.168.1.80\n arp-nd interface GigabitEthernet 1/0/1\n quit"},
        ],
    },
}

H3C_LB_CASES = [
    {
        "title": "Web 服务器负载均衡",
        "description": "管理口 192.168.1.1，两台实服务器做轮转，虚地址和接口在同一网段，所以写 arp-nd interface。",
        "steps": [
            "system-view",
            "sysname H3C-LB-01",
            "interface GigabitEthernet 1/0/1",
            " ip address 192.168.1.1 255.255.255.0",
            " quit",
            "ip route-static 0.0.0.0 0.0.0.0 192.168.1.254",
            "nqa template icmp icmp1",
            " quit",
            "server-farm web",
            " predictor round-robin",
            " probe icmp1",
            " quit",
            "real-server rs1",
            " ip address 192.168.10.11",
            " port 80",
            " weight 150",
            " server-farm web",
            " quit",
            "real-server rs2",
            " ip address 192.168.10.12",
            " port 80",
            " weight 100",
            " server-farm web",
            " quit",
            "virtual-server vs-web type tcp",
            " virtual ip address 192.168.1.80",
            " port 80",
            " default server-farm web",
            " service enable",
            " arp-nd interface GigabitEthernet 1/0/1",
            " quit",
            "quit",
        ],
    },
    {
        "title": "三层聚合上联",
        "description": "Route-Aggregation 1 收两个千兆口。不写交换机的 switchport。",
        "steps": [
            "system-view",
            "interface Route-Aggregation 1",
            " quit",
            "interface GigabitEthernet 1/0/3",
            " port link-aggregation group 1",
            " quit",
            "interface GigabitEthernet 1/0/4",
            " port link-aggregation group 1",
            " quit",
            "quit",
        ],
    },
]
