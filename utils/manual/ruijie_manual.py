#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
锐捷交换机命令手册 - 完整版

包含锐捷全系列交换机命令集，涵盖基础配置、接口配置、路由配置、
安全配置、生成树、高可用、管理与监控、QoS、IPv6等完整配置。

锐捷命令风格类似Cisco，使用show命令查看信息。

作者: Flocks Network Config Generator
版本: 2.0
更新日期: 2026-04-21
"""

RUIJIE_COMMANDS = {
    "基础配置": {
        "系统管理": [
            {
                "name": "设置主机名",
                "command": "hostname <name>",
                "description": "设置设备主机名",
                "example": "hostname RG-Core-SW-01"
            },
            {
                "name": "查看版本信息",
                "command": "show version",
                "description": "查看设备硬件和软件版本信息",
                "example": "show version"
            },
            {
                "name": "查看当前配置",
                "command": "show running-config",
                "description": "查看当前运行配置",
                "example": "show running-config"
            },
            {
                "name": "查看启动配置",
                "command": "show startup-config",
                "description": "查看启动配置文件",
                "example": "show startup-config"
            },
            {
                "name": "保存配置",
                "command": "write\n或: copy running-config startup-config",
                "description": "保存当前配置到启动配置文件",
                "example": "write"
            },
            {
                "name": "重启设备",
                "command": "reload",
                "description": "重启交换机",
                "example": "reload"
            },
            {
                "name": "恢复出厂配置",
                "command": "delete flash:config.text\ndelete flash:vlan.dat\nreload",
                "description": "清除配置文件并重启恢复出厂设置",
                "example": "delete flash:config.text"
            },
            {
                "name": "配置系统时间",
                "command": "clock set <HH:MM:SS> <YYYY-MM-DD>",
                "description": "设置系统时间",
                "example": "clock set 14:30:00 2026-04-21"
            },
            {
                "name": "查看系统时间",
                "command": "show clock",
                "description": "显示当前系统时间",
                "example": "show clock"
            },
            {
                "name": "查看CPU使用率",
                "command": "show cpu",
                "description": "查看CPU使用情况",
                "example": "show cpu"
            },
            {
                "name": "查看内存使用",
                "command": "show memory",
                "description": "查看内存使用情况",
                "example": "show memory"
            },
            {
                "name": "配置闲置超时",
                "command": "line console 0\nexec-timeout <minutes>",
                "description": "设置控制台闲置超时时间",
                "example": "line console 0\nexec-timeout 30"
            },
            {
                "name": "查看环境信息",
                "command": "show environment",
                "description": "查看温度、风扇、电源等环境信息",
                "example": "show environment"
            },
            {
                "name": "查看设备风扇状态",
                "command": "show fan",
                "description": "显示风扇状态信息",
                "example": "show fan"
            },
            {
                "name": "查看电源状态",
                "command": "show power",
                "description": "显示电源模块状态",
                "example": "show power"
            }
        ],
        "用户管理": [
            {
                "name": "创建用户",
                "command": "username <name> privilege <level> password <password>",
                "description": "创建本地用户并设置权限级别和密码",
                "example": "username admin privilege 15 password Admin@123"
            },
            {
                "name": "创建用户(密文密码)",
                "command": "username <name> privilege <level> secret <password>",
                "description": "使用加密存储的密码创建用户",
                "example": "username admin privilege 15 secret Admin@123"
            },
            {
                "name": "删除用户",
                "command": "no username <name>",
                "description": "删除指定用户",
                "example": "no username guest"
            },
            {
                "name": "配置特权密码",
                "command": "enable secret <password>",
                "description": "设置进入特权模式的密码",
                "example": "enable secret Enable@123"
            },
            {
                "name": "配置特权密码(明文)",
                "command": "enable password <password>",
                "description": "设置明文存储的特权密码(不推荐)",
                "example": "enable password Enable@123"
            },
            {
                "name": "查看用户列表",
                "command": "show users",
                "description": "查看当前登录用户",
                "example": "show users"
            },
            {
                "name": "权限级别说明",
                "command": "privilege exec level <level> <command>",
                "description": "配置命令权限级别(0-15级)",
                "example": "privilege exec level 5 show running-config"
            },
            {
                "name": "配置用户角色",
                "command": "username <name> role <role-name>",
                "description": "为用户分配角色",
                "example": "username netadmin role network-admin"
            },
            {
                "name": "创建角色",
                "command": "role name <role-name>",
                "description": "创建自定义角色",
                "example": "role name monitor"
            },
            {
                "name": "角色权限配置",
                "command": "role name <role-name>\nrule permit command <command>",
                "description": "为角色配置命令权限",
                "example": "role name monitor\nrule permit command show"
            },
            {
                "name": "查看用户信息",
                "command": "show running-config | include username",
                "description": "查看已配置的用户",
                "example": "show running-config | include username"
            }
        ],
        "SSH配置": [
            {
                "name": "启用SSH服务",
                "command": "ip ssh server enable",
                "description": "启用SSH服务器功能",
                "example": "ip ssh server enable"
            },
            {
                "name": "生成RSA密钥",
                "command": "crypto key generate rsa [modulus <bits>]",
                "description": "生成RSA密钥对",
                "example": "crypto key generate rsa modulus 2048"
            },
            {
                "name": "设置SSH版本",
                "command": "ip ssh version <1|2>",
                "description": "设置SSH协议版本",
                "example": "ip ssh version 2"
            },
            {
                "name": "配置SSH超时",
                "command": "ip ssh timeout <seconds>",
                "description": "设置SSH连接超时时间",
                "example": "ip ssh timeout 120"
            },
            {
                "name": "配置SSH认证重试",
                "command": "ip ssh authentication-retries <times>",
                "description": "设置SSH认证重试次数",
                "example": "ip ssh authentication-retries 3"
            },
            {
                "name": "配置VTY使用SSH",
                "command": "line vty 0 4\ntransport input ssh\nlogin local",
                "description": "配置VTY线路只允许SSH登录并使用本地认证",
                "example": "line vty 0 4\ntransport input ssh\nlogin local"
            },
            {
                "name": "查看SSH状态",
                "command": "show ip ssh",
                "description": "查看SSH服务状态",
                "example": "show ip ssh"
            },
            {
                "name": "查看SSH会话",
                "command": "show ssh",
                "description": "查看当前SSH连接",
                "example": "show ssh"
            },
            {
                "name": "删除RSA密钥",
                "command": "crypto key zeroize rsa",
                "description": "删除RSA密钥对",
                "example": "crypto key zeroize rsa"
            },
            {
                "name": "生成ECDSA密钥",
                "command": "crypto key generate ecdsa",
                "description": "生成ECDSA密钥对",
                "example": "crypto key generate ecdsa"
            }
        ],
        "Telnet配置": [
            {
                "name": "启用Telnet服务",
                "command": "telnet server enable",
                "description": "启用Telnet服务器(不推荐用于生产环境)",
                "example": "telnet server enable"
            },
            {
                "name": "关闭Telnet服务",
                "command": "no telnet server enable",
                "description": "关闭Telnet服务器提高安全性",
                "example": "no telnet server enable"
            },
            {
                "name": "配置VTY使用Telnet",
                "command": "line vty 0 4\ntransport input telnet\nlogin local",
                "description": "配置VTY线路允许Telnet登录",
                "example": "line vty 0 4\ntransport input telnet\nlogin local"
            },
            {
                "name": "配置Telnet端口",
                "command": "telnet server port <port>",
                "description": "修改Telnet服务端口(默认23)",
                "example": "telnet server port 2323"
            },
            {
                "name": "配置VTY超时",
                "command": "line vty 0 4\nexec-timeout <minutes>",
                "description": "设置VTY会话超时时间",
                "example": "line vty 0 4\nexec-timeout 30"
            }
        ],
        "Console配置": [
            {
                "name": "配置Console密码",
                "command": "line console 0\npassword <password>\nlogin",
                "description": "设置Console登录密码",
                "example": "line console 0\npassword Console@123\nlogin"
            },
            {
                "name": "Console本地认证",
                "command": "line console 0\nlogin local",
                "description": "Console使用本地用户认证",
                "example": "line console 0\nlogin local"
            },
            {
                "name": "配置Console超时",
                "command": "line console 0\nexec-timeout <minutes>",
                "description": "设置Console会话超时时间",
                "example": "line console 0\nexec-timeout 30"
            },
            {
                "name": "配置Console波特率",
                "command": "line console 0\nspeed <baud-rate>",
                "description": "设置Console波特率",
                "example": "line console 0\nspeed 115200"
            },
            {
                "name": "禁用Console密码",
                "command": "line console 0\nno password\nno login",
                "description": "取消Console登录密码",
                "example": "line console 0\nno password\nno login"
            }
        ],
        "域名解析": [
            {
                "name": "配置DNS服务器",
                "command": "ip name-server <ip>",
                "description": "配置DNS服务器地址",
                "example": "ip name-server 8.8.8.8"
            },
            {
                "name": "配置多个DNS服务器",
                "command": "ip name-server <ip1> <ip2>",
                "description": "配置主备DNS服务器",
                "example": "ip name-server 8.8.8.8 114.114.114.114"
            },
            {
                "name": "启用DNS解析",
                "command": "ip domain-lookup",
                "description": "启用DNS域名解析功能",
                "example": "ip domain-lookup"
            },
            {
                "name": "禁用DNS解析",
                "command": "no ip domain-lookup",
                "description": "禁用DNS域名解析功能",
                "example": "no ip domain-lookup"
            },
            {
                "name": "配置域名后缀",
                "command": "ip domain-name <domain>",
                "description": "配置默认域名后缀",
                "example": "ip domain-name example.com"
            },
            {
                "name": "配置静态主机映射",
                "command": "ip host <hostname> <ip>",
                "description": "配置静态主机名到IP的映射",
                "example": "ip host server1 192.168.1.100"
            },
            {
                "name": "查看DNS配置",
                "command": "show hosts",
                "description": "查看主机名和DNS配置",
                "example": "show hosts"
            }
        ]
    },
    "接口配置": {
        "以太网接口": [
            {
                "name": "进入接口配置",
                "command": "interface <interface>",
                "description": "进入指定接口配置模式",
                "example": "interface GigabitEthernet 0/1"
            },
            {
                "name": "配置接口描述",
                "command": "description <text>",
                "description": "为接口添加描述信息",
                "example": "description To-Server-Room"
            },
            {
                "name": "开启接口",
                "command": "no shutdown",
                "description": "激活接口",
                "example": "no shutdown"
            },
            {
                "name": "关闭接口",
                "command": "shutdown",
                "description": "关闭接口",
                "example": "shutdown"
            },
            {
                "name": "配置接口IP地址",
                "command": "interface <interface>\nip address <ip> <mask>",
                "description": "为三层接口配置IP地址",
                "example": "interface GigabitEthernet 0/1\nip address 192.168.1.1 255.255.255.0"
            },
            {
                "name": "配置接口从IP地址",
                "command": "ip address <ip> <mask> secondary",
                "description": "为接口配置从IP地址",
                "example": "ip address 192.168.2.1 255.255.255.0 secondary"
            },
            {
                "name": "删除接口IP",
                "command": "no ip address",
                "description": "删除接口IP地址",
                "example": "no ip address"
            },
            {
                "name": "设置接口速率",
                "command": "speed <10|100|1000|auto>",
                "description": "设置接口速率",
                "example": "speed 1000"
            },
            {
                "name": "设置双工模式",
                "command": "duplex <half|full|auto>",
                "description": "设置接口双工模式",
                "example": "duplex full"
            },
            {
                "name": "启用流控",
                "command": "flowcontrol receive on",
                "description": "启用流控功能",
                "example": "flowcontrol receive on"
            },
            {
                "name": "配置接口MTU",
                "command": "mtu <bytes>",
                "description": "设置接口MTU值",
                "example": "mtu 9000"
            },
            {
                "name": "查看接口状态",
                "command": "show interface <interface>",
                "description": "查看接口详细状态",
                "example": "show interface GigabitEthernet 0/1"
            },
            {
                "name": "查看接口简要信息",
                "command": "show interface brief",
                "description": "查看所有接口简要状态",
                "example": "show interface brief"
            },
            {
                "name": "批量配置接口",
                "command": "interface range <interface-range>",
                "description": "批量进入多个接口进行配置",
                "example": "interface range GigabitEthernet 0/1-10"
            },
            {
                "name": "接口计数器清零",
                "command": "clear counters <interface>",
                "description": "清除接口统计计数器",
                "example": "clear counters GigabitEthernet 0/1"
            }
        ],
        "VLAN接口": [
            {
                "name": "创建VLAN",
                "command": "vlan <id>",
                "description": "创建指定ID的VLAN",
                "example": "vlan 10"
            },
            {
                "name": "VLAN命名",
                "command": "vlan <id>\nname <name>",
                "description": "为VLAN设置名称",
                "example": "vlan 10\nname Sales_Department"
            },
            {
                "name": "批量创建VLAN",
                "command": "vlan range <id1-id2>",
                "description": "批量创建连续VLAN",
                "example": "vlan range 10-20"
            },
            {
                "name": "批量创建不连续VLAN",
                "command": "vlan <id1>,<id2>,<id3>",
                "description": "批量创建多个不连续VLAN",
                "example": "vlan 10,20,30,40"
            },
            {
                "name": "删除VLAN",
                "command": "no vlan <id>",
                "description": "删除指定VLAN",
                "example": "no vlan 10"
            },
            {
                "name": "查看VLAN信息",
                "command": "show vlan [brief]",
                "description": "查看VLAN信息",
                "example": "show vlan brief"
            },
            {
                "name": "创建VLAN接口",
                "command": "interface vlan <id>",
                "description": "创建VLAN三层接口(SVI)",
                "example": "interface vlan 10"
            },
            {
                "name": "VLAN接口配置IP",
                "command": "interface vlan <id>\nip address <ip> <mask>",
                "description": "为VLAN接口配置IP地址",
                "example": "interface vlan 10\nip address 192.168.10.1 255.255.255.0"
            },
            {
                "name": "VLAN接口描述",
                "command": "interface vlan <id>\ndescription <text>",
                "description": "为VLAN接口添加描述",
                "example": "interface vlan 10\ndescription Gateway_for_VLAN10"
            },
            {
                "name": "启用VLAN接口",
                "command": "interface vlan <id>\nno shutdown",
                "description": "激活VLAN接口",
                "example": "interface vlan 10\nno shutdown"
            },
            {
                "name": "查看VLAN接口状态",
                "command": "show interface vlan <id>",
                "description": "查看VLAN接口状态",
                "example": "show interface vlan 10"
            }
        ],
        "接口VLAN": [
            {
                "name": "配置Access接口",
                "command": "interface <interface>\nswitchport mode access\nswitchport access vlan <id>",
                "description": "配置接口为Access模式并加入VLAN",
                "example": "interface GigabitEthernet 0/1\nswitchport mode access\nswitchport access vlan 10"
            },
            {
                "name": "配置Trunk接口",
                "command": "interface <interface>\nswitchport mode trunk\nswitchport trunk allowed vlan <ids>",
                "description": "配置接口为Trunk模式并允许指定VLAN",
                "example": "interface GigabitEthernet 0/24\nswitchport mode trunk\nswitchport trunk allowed vlan 10,20,30"
            },
            {
                "name": "Trunk允许所有VLAN",
                "command": "switchport trunk allowed vlan all",
                "description": "配置Trunk允许所有VLAN通过",
                "example": "switchport trunk allowed vlan all"
            },
            {
                "name": "Trunk添加VLAN",
                "command": "switchport trunk allowed vlan add <id>",
                "description": "向Trunk添加VLAN",
                "example": "switchport trunk allowed vlan add 40"
            },
            {
                "name": "Trunk移除VLAN",
                "command": "switchport trunk allowed vlan remove <id>",
                "description": "从Trunk移除VLAN",
                "example": "switchport trunk allowed vlan remove 40"
            },
            {
                "name": "配置Trunk Native VLAN",
                "command": "switchport trunk native vlan <id>",
                "description": "设置Trunk接口Native VLAN",
                "example": "switchport trunk native vlan 99"
            },
            {
                "name": "配置Hybrid接口",
                "command": "interface <interface>\nswitchport mode hybrid",
                "description": "配置接口为Hybrid模式",
                "example": "interface GigabitEthernet 0/1\nswitchport mode hybrid"
            },
            {
                "name": "Hybrid接口Untagged",
                "command": "switchport hybrid untagged vlan <ids>",
                "description": "Hybrid接口剥离VLAN标签",
                "example": "switchport hybrid untagged vlan 10,20"
            },
            {
                "name": "Hybrid接口Tagged",
                "command": "switchport hybrid tagged vlan <ids>",
                "description": "Hybrid接口保留VLAN标签",
                "example": "switchport hybrid tagged vlan 100"
            },
            {
                "name": "Hybrid接口PVID",
                "command": "switchport hybrid native vlan <id>",
                "description": "设置Hybrid接口PVID",
                "example": "switchport hybrid native vlan 10"
            },
            {
                "name": "查看接口VLAN配置",
                "command": "show interface <interface> switchport",
                "description": "查看接口VLAN配置详情",
                "example": "show interface GigabitEthernet 0/1 switchport"
            }
        ],
        "链路聚合": [
            {
                "name": "创建聚合组",
                "command": "interface aggregateport <id>",
                "description": "创建链路聚合组",
                "example": "interface aggregateport 1"
            },
            {
                "name": "配置聚合模式(LACP)",
                "command": "interface aggregateport <id>\naggregport mode active",
                "description": "配置聚合组为LACP主动模式",
                "example": "interface aggregateport 1\naggregport mode active"
            },
            {
                "name": "配置聚合模式(静态)",
                "command": "interface aggregateport <id>\naggregport mode on",
                "description": "配置聚合组为静态聚合模式",
                "example": "interface aggregateport 1\naggregport mode on"
            },
            {
                "name": "添加成员端口",
                "command": "interface <interface>\nport-group <id>",
                "description": "将物理端口加入聚合组",
                "example": "interface GigabitEthernet 0/1\nport-group 1"
            },
            {
                "name": "批量添加成员端口",
                "command": "interface range <range>\nport-group <id>",
                "description": "批量将端口加入聚合组",
                "example": "interface range GigabitEthernet 0/1-4\nport-group 1"
            },
            {
                "name": "配置负载均衡",
                "command": "aggregateport load-balance <mode>",
                "description": "配置负载均衡模式",
                "example": "aggregateport load-balance src-dst-mac"
            },
            {
                "name": "设置最小活跃链路数",
                "command": "interface aggregateport <id>\naggregport min-links <number>",
                "description": "设置最小活跃链路数",
                "example": "interface aggregateport 1\naggregport min-links 2"
            },
            {
                "name": "设置最大活跃链路数",
                "command": "interface aggregateport <id>\naggregport max-links <number>",
                "description": "设置最大活跃链路数",
                "example": "interface aggregateport 1\naggregport max-links 4"
            },
            {
                "name": "配置聚合组为Trunk",
                "command": "interface aggregateport <id>\nswitchport mode trunk\nswitchport trunk allowed vlan <ids>",
                "description": "将聚合组配置为Trunk模式",
                "example": "interface aggregateport 1\nswitchport mode trunk\nswitchport trunk allowed vlan 10,20,30"
            },
            {
                "name": "配置聚合组IP地址",
                "command": "interface aggregateport <id>\nip address <ip> <mask>",
                "description": "为三层聚合组配置IP地址",
                "example": "interface aggregateport 1\nip address 192.168.1.1 255.255.255.0"
            },
            {
                "name": "查看聚合组状态",
                "command": "show aggregateport <id> [summary]",
                "description": "查看链路聚合状态",
                "example": "show aggregateport 1 summary"
            },
            {
                "name": "查看所有聚合组",
                "command": "show aggregateport summary",
                "description": "查看所有聚合组摘要",
                "example": "show aggregateport summary"
            },
            {
                "name": "负载均衡模式说明",
                "command": "show aggregateport load-balance",
                "description": "查看当前负载均衡模式",
                "example": "show aggregateport load-balance"
            }
        ]
    },
    "路由配置": {
        "静态路由": [
            {
                "name": "配置静态路由",
                "command": "ip route <network> <mask> <next-hop>",
                "description": "添加静态路由",
                "example": "ip route 192.168.100.0 255.255.255.0 10.0.0.1"
            },
            {
                "name": "配置默认路由",
                "command": "ip route 0.0.0.0 0.0.0.0 <gateway>",
                "description": "配置默认路由",
                "example": "ip route 0.0.0.0 0.0.0.0 192.168.1.254"
            },
            {
                "name": "配置静态路由(指定出口)",
                "command": "ip route <network> <mask> <interface>",
                "description": "通过指定出接口配置静态路由",
                "example": "ip route 192.168.100.0 255.255.255.0 vlan 10"
            },
            {
                "name": "配置浮动静态路由",
                "command": "ip route <network> <mask> <next-hop> <distance>",
                "description": "配置备份路由(管理距离越大优先级越低)",
                "example": "ip route 0.0.0.0 0.0.0.0 192.168.2.254 200"
            },
            {
                "name": "删除静态路由",
                "command": "no ip route <network> <mask>",
                "description": "删除指定静态路由",
                "example": "no ip route 192.168.100.0 255.255.255.0"
            },
            {
                "name": "查看路由表",
                "command": "show ip route",
                "description": "查看IP路由表",
                "example": "show ip route"
            },
            {
                "name": "查看静态路由",
                "command": "show ip route static",
                "description": "只查看静态路由",
                "example": "show ip route static"
            },
            {
                "name": "查看特定网段路由",
                "command": "show ip route <network>",
                "description": "查看特定网段的路由信息",
                "example": "show ip route 192.168.1.0"
            }
        ],
        "OSPF配置": [
            {
                "name": "启用OSPF进程",
                "command": "router ospf <process-id>",
                "description": "启用OSPF路由进程",
                "example": "router ospf 1"
            },
            {
                "name": "配置Router ID",
                "command": "router ospf <process-id>\nrouter-id <id>",
                "description": "配置OSPF Router ID",
                "example": "router ospf 1\nrouter-id 1.1.1.1"
            },
            {
                "name": "宣告网络",
                "command": "router ospf <process-id>\nnetwork <network> <wildcard> area <area-id>",
                "description": "宣告OSPF网络",
                "example": "router ospf 1\nnetwork 192.168.0.0 0.0.255.255 area 0"
            },
            {
                "name": "配置区域认证",
                "command": "area <area-id> authentication [message-digest]",
                "description": "配置OSPF区域认证",
                "example": "router ospf 1\narea 0 authentication message-digest"
            },
            {
                "name": "配置接口OSPF认证",
                "command": "interface <interface>\nip ospf authentication message-digest\nip ospf message-digest-key 1 md5 <key>",
                "description": "配置接口OSPF认证",
                "example": "interface vlan 10\nip ospf authentication message-digest\nip ospf message-digest-key 1 md5 OSPFKey123"
            },
            {
                "name": "配置OSPF接口开销",
                "command": "interface <interface>\nip ospf cost <cost>",
                "description": "配置OSPF接口开销值",
                "example": "interface vlan 10\nip ospf cost 10"
            },
            {
                "name": "配置OSPF优先级",
                "command": "interface <interface>\nip ospf priority <priority>",
                "description": "配置接口OSPF DR选举优先级",
                "example": "interface vlan 10\nip ospf priority 100"
            },
            {
                "name": "配置OSPF被动接口",
                "command": "router ospf <process-id>\npassive-interface <interface>",
                "description": "配置被动接口不发送OSPF报文",
                "example": "router ospf 1\npassive-interface vlan 10"
            },
            {
                "name": "配置默认路由下发",
                "command": "router ospf <process-id>\ndefault-information originate",
                "description": "向OSPF下发默认路由",
                "example": "router ospf 1\ndefault-information originate"
            },
            {
                "name": "查看OSPF邻居",
                "command": "show ip ospf neighbor",
                "description": "查看OSPF邻居状态",
                "example": "show ip ospf neighbor"
            },
            {
                "name": "查看OSPF数据库",
                "command": "show ip ospf database",
                "description": "查看OSPF链路状态数据库",
                "example": "show ip ospf database"
            },
            {
                "name": "查看OSPF接口",
                "command": "show ip ospf interface",
                "description": "查看OSPF接口信息",
                "example": "show ip ospf interface"
            },
            {
                "name": "查看OSPF路由",
                "command": "show ip route ospf",
                "description": "查看OSPF学习到的路由",
                "example": "show ip route ospf"
            }
        ],
        "BGP配置": [
            {
                "name": "启用BGP进程",
                "command": "router bgp <as-number>",
                "description": "启用BGP路由进程",
                "example": "router bgp 65001"
            },
            {
                "name": "配置BGP Router ID",
                "command": "router bgp <as-number>\nbgp router-id <id>",
                "description": "配置BGP Router ID",
                "example": "router bgp 65001\nbgp router-id 1.1.1.1"
            },
            {
                "name": "配置BGP邻居",
                "command": "router bgp <as-number>\nneighbor <ip> remote-as <as-number>",
                "description": "配置BGP邻居",
                "example": "router bgp 65001\nneighbor 192.168.1.2 remote-as 65002"
            },
            {
                "name": "配置BGP邻居描述",
                "command": "neighbor <ip> description <desc>",
                "description": "为BGP邻居添加描述",
                "example": "neighbor 192.168.1.2 description To-ISP"
            },
            {
                "name": "宣告BGP网络",
                "command": "router bgp <as-number>\nnetwork <network> mask <mask>",
                "description": "宣告BGP网络",
                "example": "router bgp 65001\nnetwork 192.168.0.0 mask 255.255.0.0"
            },
            {
                "name": "配置BGP下一跳自身",
                "command": "neighbor <ip> next-hop-self",
                "description": "向邻居通告路由时将下一跳设为自身",
                "example": "neighbor 192.168.1.2 next-hop-self"
            },
            {
                "name": "配置BGP软复位",
                "command": "clear ip bgp <neighbor> soft [in|out]",
                "description": "软复位BGP邻居",
                "example": "clear ip bgp 192.168.1.2 soft"
            },
            {
                "name": "查看BGP邻居",
                "command": "show ip bgp neighbors",
                "description": "查看BGP邻居状态",
                "example": "show ip bgp neighbors"
            },
            {
                "name": "查看BGP表",
                "command": "show ip bgp",
                "description": "查看BGP路由表",
                "example": "show ip bgp"
            },
            {
                "name": "查看BGP路由",
                "command": "show ip route bgp",
                "description": "查看BGP学习到的路由",
                "example": "show ip route bgp"
            }
        ],
        "RIP配置": [
            {
                "name": "启用RIP进程",
                "command": "router rip",
                "description": "启用RIP路由进程",
                "example": "router rip"
            },
            {
                "name": "配置RIP版本",
                "command": "router rip\nversion <1|2>",
                "description": "设置RIP版本",
                "example": "router rip\nversion 2"
            },
            {
                "name": "宣告RIP网络",
                "command": "router rip\nnetwork <network>",
                "description": "宣告RIP网络",
                "example": "router rip\nnetwork 192.168.1.0"
            },
            {
                "name": "配置被动接口",
                "command": "router rip\npassive-interface <interface>",
                "description": "配置被动接口不发送RIP更新",
                "example": "router rip\npassive-interface vlan 10"
            },
            {
                "name": "配置默认路由下发",
                "command": "router rip\ndefault-information originate",
                "description": "向RIP下发默认路由",
                "example": "router rip\ndefault-information originate"
            },
            {
                "name": "关闭自动汇总",
                "command": "router rip\nno auto-summary",
                "description": "关闭RIP自动汇总",
                "example": "router rip\nno auto-summary"
            },
            {
                "name": "查看RIP路由",
                "command": "show ip route rip",
                "description": "查看RIP学习到的路由",
                "example": "show ip route rip"
            },
            {
                "name": "查看RIP数据库",
                "command": "show ip rip database",
                "description": "查看RIP数据库",
                "example": "show ip rip database"
            }
        ]
    },
    "安全配置": {
        "ACL配置": [
            {
                "name": "创建标准ACL",
                "command": "ip access-list standard <name|number>\npermit|deny <source>",
                "description": "创建标准ACL(1-99)",
                "example": "ip access-list standard 1\npermit 192.168.1.0 0.0.0.255"
            },
            {
                "name": "创建扩展ACL",
                "command": "ip access-list extended <name|number>\npermit|deny <protocol> <src> <dst> [eq <port>]",
                "description": "创建扩展ACL(100-199)",
                "example": "ip access-list extended 100\npermit tcp any any eq 80"
            },
            {
                "name": "命名ACL",
                "command": "ip access-list extended <name>",
                "description": "创建命名扩展ACL",
                "example": "ip access-list extended WEB_ACCESS\npermit tcp any any eq 80"
            },
            {
                "name": "应用ACL到接口",
                "command": "interface <interface>\nip access-group <acl> in|out",
                "description": "在接口应用ACL",
                "example": "interface GigabitEthernet 0/1\nip access-group 100 in"
            },
            {
                "name": "应用到VTY线路",
                "command": "line vty 0 4\naccess-class <acl> in",
                "description": "限制VTY访问",
                "example": "line vty 0 4\naccess-class 1 in"
            },
            {
                "name": "查看ACL配置",
                "command": "show access-lists [name|number]",
                "description": "查看ACL配置",
                "example": "show access-lists"
            },
            {
                "name": "查看ACL匹配计数",
                "command": "show access-lists <name>",
                "description": "查看ACL匹配统计",
                "example": "show access-lists 100"
            },
            {
                "name": "删除ACL",
                "command": "no ip access-list <standard|extended> <name|number>",
                "description": "删除指定ACL",
                "example": "no ip access-list extended 100"
            },
            {
                "name": "ACL拒绝特定IP",
                "command": "ip access-list extended <name>\ndeny ip host <ip> any",
                "description": "拒绝特定IP访问",
                "example": "ip access-list extended BLOCK_HOST\ndeny ip host 192.168.1.100 any"
            },
            {
                "name": "ACL允许特定服务",
                "command": "ip access-list extended <name>\npermit tcp any any eq <port>",
                "description": "允许特定端口流量",
                "example": "ip access-list extended WEB_ONLY\npermit tcp any any eq 80\npermit tcp any any eq 443"
            }
        ],
        "端口安全": [
            {
                "name": "启用端口安全",
                "command": "interface <interface>\nswitchport port-security",
                "description": "启用端口安全功能",
                "example": "interface GigabitEthernet 0/1\nswitchport port-security"
            },
            {
                "name": "限制MAC地址数量",
                "command": "switchport port-security maximum <number>",
                "description": "限制最大MAC地址数",
                "example": "switchport port-security maximum 1"
            },
            {
                "name": "配置安全违规动作",
                "command": "switchport port-security violation protect|restrict|shutdown",
                "description": "配置违规处理方式(保护/限制/关闭)",
                "example": "switchport port-security violation shutdown"
            },
            {
                "name": "配置静态安全MAC",
                "command": "switchport port-security mac-address <mac>",
                "description": "配置静态安全MAC地址",
                "example": "switchport port-security mac-address 0011.2233.4455"
            },
            {
                "name": "配置粘性MAC",
                "command": "switchport port-security mac-address sticky",
                "description": "启用粘性MAC学习",
                "example": "switchport port-security mac-address sticky"
            },
            {
                "name": "配置安全MAC老化时间",
                "command": "switchport port-security aging time <minutes>",
                "description": "设置安全MAC老化时间",
                "example": "switchport port-security aging time 60"
            },
            {
                "name": "查看端口安全状态",
                "command": "show port-security [interface <interface>]",
                "description": "查看端口安全配置",
                "example": "show port-security interface GigabitEthernet 0/1"
            },
            {
                "name": "查看安全MAC地址",
                "command": "show port-security address",
                "description": "查看安全MAC地址表",
                "example": "show port-security address"
            },
            {
                "name": "清除安全MAC",
                "command": "clear port-security sticky [interface <interface>]",
                "description": "清除粘性MAC地址",
                "example": "clear port-security sticky interface GigabitEthernet 0/1"
            }
        ],
        "DHCP Snooping": [
            {
                "name": "启用DHCP Snooping",
                "command": "ip dhcp snooping",
                "description": "全局启用DHCP Snooping",
                "example": "ip dhcp snooping"
            },
            {
                "name": "启用VLAN的DHCP Snooping",
                "command": "ip dhcp snooping vlan <vlan-id>",
                "description": "在指定VLAN启用DHCP Snooping",
                "example": "ip dhcp snooping vlan 10,20,30"
            },
            {
                "name": "配置信任端口",
                "command": "interface <interface>\nip dhcp snooping trust",
                "description": "配置连接DHCP服务器的信任端口",
                "example": "interface GigabitEthernet 0/24\nip dhcp snooping trust"
            },
            {
                "name": "限制DHCP请求速率",
                "command": "interface <interface>\nip dhcp snooping limit rate <rate>",
                "description": "限制DHCP请求包速率(pps)",
                "example": "interface GigabitEthernet 0/1\nip dhcp snooping limit rate 100"
            },
            {
                "name": "启用Option82",
                "command": "ip dhcp snooping information option",
                "description": "启用DHCP Option82功能",
                "example": "ip dhcp snooping information option"
            },
            {
                "name": "查看DHCP Snooping绑定表",
                "command": "show ip dhcp snooping binding",
                "description": "查看DHCP Snooping绑定表",
                "example": "show ip dhcp snooping binding"
            },
            {
                "name": "查看DHCP Snooping配置",
                "command": "show ip dhcp snooping",
                "description": "查看DHCP Snooping配置",
                "example": "show ip dhcp snooping"
            }
        ],
        "ARP安全": [
            {
                "name": "配置静态ARP",
                "command": "arp <ip> <mac> arpa",
                "description": "配置静态ARP绑定",
                "example": "arp 192.168.1.100 0011.2233.4455 arpa"
            },
            {
                "name": "启用ARP检查",
                "command": "ip arp inspection vlan <vlan-id>",
                "description": "在VLAN启用ARP检查",
                "example": "ip arp inspection vlan 10"
            },
            {
                "name": "配置ARP检查信任端口",
                "command": "interface <interface>\nip arp inspection trust",
                "description": "配置ARP检查信任端口",
                "example": "interface GigabitEthernet 0/24\nip arp inspection trust"
            },
            {
                "name": "配置ARP检查限速",
                "command": "interface <interface>\nip arp inspection limit rate <rate>",
                "description": "限制ARP请求速率(pps)",
                "example": "interface GigabitEthernet 0/1\nip arp inspection limit rate 100"
            },
            {
                "name": "启用ARP防护",
                "command": "interface <interface>\narp protective",
                "description": "启用接口ARP防护功能",
                "example": "interface GigabitEthernet 0/1\narp protective"
            },
            {
                "name": "配置免费ARP检测",
                "command": "arp gratuitous-check enable",
                "description": "启用免费ARP检测",
                "example": "arp gratuitous-check enable"
            },
            {
                "name": "查看ARP表",
                "command": "show arp",
                "description": "查看ARP表",
                "example": "show arp"
            },
            {
                "name": "清除ARP表",
                "command": "clear arp-cache",
                "description": "清除ARP缓存",
                "example": "clear arp-cache"
            }
        ],
        "IPSG配置": [
            {
                "name": "启用IP源防护",
                "command": "interface <interface>\nip verify source",
                "description": "启用IP源地址检查",
                "example": "interface GigabitEthernet 0/1\nip verify source"
            },
            {
                "name": "启用IPSG端口安全",
                "command": "interface <interface>\nip verify source port-security",
                "description": "启用IP源防护结合端口安全",
                "example": "interface GigabitEthernet 0/1\nip verify source port-security"
            },
            {
                "name": "配置静态IP源绑定",
                "command": "ip source binding <mac> vlan <id> <ip> interface <interface>",
                "description": "配置静态IP源绑定",
                "example": "ip source binding 0011.2233.4455 vlan 10 192.168.10.100 interface GigabitEthernet 0/1"
            },
            {
                "name": "查看IPSG绑定表",
                "command": "show ip verify source",
                "description": "查看IP源防护绑定表",
                "example": "show ip verify source"
            },
            {
                "name": "查看IPSG统计",
                "command": "show ip source binding",
                "description": "查看源绑定信息",
                "example": "show ip source binding"
            }
        ]
    },
    "生成树配置": {
        "STP基础": [
            {
                "name": "启用STP",
                "command": "spanning-tree",
                "description": "全局启用生成树协议",
                "example": "spanning-tree"
            },
            {
                "name": "关闭STP",
                "command": "no spanning-tree",
                "description": "关闭生成树协议",
                "example": "no spanning-tree"
            },
            {
                "name": "配置STP模式",
                "command": "spanning-tree mode <stp|rstp|mstp>",
                "description": "设置生成树模式",
                "example": "spanning-tree mode rstp"
            },
            {
                "name": "配置根网桥",
                "command": "spanning-tree root primary|secondary",
                "description": "配置交换机为根网桥或备份根",
                "example": "spanning-tree root primary"
            },
            {
                "name": "配置STP优先级",
                "command": "spanning-tree priority <priority>",
                "description": "配置网桥优先级(0-61440, 步长4096)",
                "example": "spanning-tree priority 4096"
            },
            {
                "name": "配置端口优先级",
                "command": "interface <interface>\nspanning-tree port-priority <priority>",
                "description": "配置端口优先级(0-240, 步长16)",
                "example": "interface GigabitEthernet 0/1\nspanning-tree port-priority 128"
            },
            {
                "name": "配置端口开销",
                "command": "interface <interface>\nspanning-tree cost <cost>",
                "description": "配置端口路径开销",
                "example": "interface GigabitEthernet 0/1\nspanning-tree cost 200000"
            },
            {
                "name": "配置端口为边缘端口",
                "command": "interface <interface>\nspanning-tree portfast",
                "description": "配置端口快速进入转发状态",
                "example": "interface GigabitEthernet 0/1\nspanning-tree portfast"
            },
            {
                "name": "启用BPDU防护",
                "command": "interface <interface>\nspanning-tree bpduguard enable",
                "description": "启用端口BPDU防护",
                "example": "interface GigabitEthernet 0/1\nspanning-tree bpduguard enable"
            },
            {
                "name": "全局BPDU防护",
                "command": "spanning-tree portfast bpduguard default",
                "description": "全局启用端口快速的BPDU防护",
                "example": "spanning-tree portfast bpduguard default"
            },
            {
                "name": "配置BPDU过滤",
                "command": "interface <interface>\nspanning-tree bpdufilter enable",
                "description": "启用BPDU过滤",
                "example": "interface GigabitEthernet 0/1\nspanning-tree bpdufilter enable"
            },
            {
                "name": "查看STP状态",
                "command": "show spanning-tree",
                "description": "查看生成树状态",
                "example": "show spanning-tree"
            },
            {
                "name": "查看STP接口状态",
                "command": "show spanning-tree interface <interface>",
                "description": "查看接口STP状态",
                "example": "show spanning-tree interface GigabitEthernet 0/1"
            }
        ],
        "MSTP配置": [
            {
                "name": "启用MSTP模式",
                "command": "spanning-tree mode mstp",
                "description": "配置生成树模式为MSTP",
                "example": "spanning-tree mode mstp"
            },
            {
                "name": "进入MST配置模式",
                "command": "spanning-tree mst configuration",
                "description": "进入MST配置模式",
                "example": "spanning-tree mst configuration"
            },
            {
                "name": "配置MST域名",
                "command": "spanning-tree mst configuration\nname <name>",
                "description": "配置MST域名",
                "example": "spanning-tree mst configuration\nname RG-MST"
            },
            {
                "name": "配置MST版本",
                "command": "spanning-tree mst configuration\nrevision <level>",
                "description": "配置MST修订级别",
                "example": "spanning-tree mst configuration\nrevision 1"
            },
            {
                "name": "配置实例VLAN映射",
                "command": "spanning-tree mst configuration\ninstance <instance-id> vlan <vlan-list>",
                "description": "将VLAN映射到MST实例",
                "example": "spanning-tree mst configuration\ninstance 1 vlan 10,20,30"
            },
            {
                "name": "配置实例优先级",
                "command": "spanning-tree mst <instance-id> priority <priority>",
                "description": "配置MST实例优先级",
                "example": "spanning-tree mst 1 priority 4096"
            },
            {
                "name": "配置实例根网桥",
                "command": "spanning-tree mst <instance-id> root primary",
                "description": "配置实例为主根网桥",
                "example": "spanning-tree mst 1 root primary"
            },
            {
                "name": "查看MST配置",
                "command": "show spanning-tree mst configuration",
                "description": "查看MST配置信息",
                "example": "show spanning-tree mst configuration"
            },
            {
                "name": "查看MST实例状态",
                "command": "show spanning-tree mst <instance-id>",
                "description": "查看指定MST实例状态",
                "example": "show spanning-tree mst 1"
            }
        ]
    },
    "高可用配置": {
        "VRRP配置": [
            {
                "name": "启用VRRP",
                "command": "interface vlan <id>\nstandby <group> ip <virtual-ip>",
                "description": "在接口启用VRRP并配置虚拟IP",
                "example": "interface vlan 10\nstandby 1 ip 192.168.10.254"
            },
            {
                "name": "配置VRRP优先级",
                "command": "standby <group> priority <priority>",
                "description": "配置VRRP优先级(1-254)",
                "example": "standby 1 priority 150"
            },
            {
                "name": "配置VRRP抢占",
                "command": "standby <group> preempt",
                "description": "启用抢占模式",
                "example": "standby 1 preempt"
            },
            {
                "name": "配置抢占延迟",
                "command": "standby <group> preempt delay <seconds>",
                "description": "配置抢占延迟时间",
                "example": "standby 1 preempt delay 60"
            },
            {
                "name": "配置VRRP认证",
                "command": "standby <group> authentication <text|md5> <key>",
                "description": "配置VRRP认证",
                "example": "standby 1 authentication md5 VRRPKey123"
            },
            {
                "name": "配置VRRP跟踪接口",
                "command": "standby <group> track <interface> decrement <value>",
                "description": "跟踪接口状态调整优先级",
                "example": "standby 1 track GigabitEthernet 0/1 decrement 50"
            },
            {
                "name": "配置VRRP通告时间",
                "command": "standby <group> timers <hello> <hold>",
                "description": "配置VRRP通告间隔和保持时间",
                "example": "standby 1 timers 1 3"
            },
            {
                "name": "查看VRRP状态",
                "command": "show standby [brief]",
                "description": "查看VRRP状态",
                "example": "show standby brief"
            },
            {
                "name": "查看VRRP详细信息",
                "command": "show standby <interface> <group>",
                "description": "查看指定接口VRRP详情",
                "example": "show standby vlan 10 1"
            }
        ],
        "堆叠配置": [
            {
                "name": "启用堆叠",
                "command": "stacking enable",
                "description": "启用堆叠功能",
                "example": "stacking enable"
            },
            {
                "name": "配置堆叠优先级",
                "command": "stacking priority <priority>",
                "description": "配置堆叠主控选举优先级",
                "example": "stacking priority 200"
            },
            {
                "name": "配置堆叠成员编号",
                "command": "stacking member <member-id>",
                "description": "配置堆叠成员编号",
                "example": "stacking member 1"
            },
            {
                "name": "配置堆叠端口",
                "command": "interface tengigabitethernet <slot>/<port>\nstack-port <id>",
                "description": "配置堆叠端口",
                "example": "interface tengigabitethernet 0/1\nstack-port 1"
            },
            {
                "name": "查看堆叠状态",
                "command": "show stacking",
                "description": "查看堆叠状态",
                "example": "show stacking"
            },
            {
                "name": "查看堆叠成员",
                "command": "show stacking members",
                "description": "查看堆叠成员信息",
                "example": "show stacking members"
            },
            {
                "name": "堆叠合并配置",
                "command": "stacking merge",
                "description": "合并堆叠配置",
                "example": "stacking merge"
            }
        ],
        "BFD配置": [
            {
                "name": "启用BFD功能",
                "command": "bfd",
                "description": "全局启用BFD功能",
                "example": "bfd"
            },
            {
                "name": "配置BFD会话",
                "command": "bfd <session-name> bind peer-ip <ip> [interface <interface>]",
                "description": "创建BFD会话",
                "example": "bfd TO-R1 bind peer-ip 192.168.1.1 interface vlan 10"
            },
            {
                "name": "配置BFD检测参数",
                "command": "bfd <session-name>\n discriminator local <id>\n discriminator remote <id>\n min-rx-interval <ms>\n min-tx-interval <ms>\n detect-multiplier <value>",
                "description": "配置BFD会话参数",
                "example": "bfd TO-R1\ndiscriminator local 1\ndiscriminator remote 2\nmin-rx-interval 100\nmin-tx-interval 100\ndetect-multiplier 3"
            },
            {
                "name": "配置BFD与OSPF联动",
                "command": "interface <interface>\nbfd enable",
                "description": "接口启用BFD与OSPF联动",
                "example": "interface vlan 10\nbfd enable"
            },
            {
                "name": "配置BFD与VRRP联动",
                "command": "standby <group> bfd",
                "description": "VRRP启用BFD快速检测",
                "example": "standby 1 bfd"
            },
            {
                "name": "查看BFD会话",
                "command": "show bfd session",
                "description": "查看BFD会话状态",
                "example": "show bfd session"
            },
            {
                "name": "查看BFD配置",
                "command": "show bfd",
                "description": "查看BFD配置信息",
                "example": "show bfd"
            }
        ]
    },
    "管理与监控": {
        "日志配置": [
            {
                "name": "启用日志功能",
                "command": "logging on",
                "description": "启用系统日志功能",
                "example": "logging on"
            },
            {
                "name": "配置日志服务器",
                "command": "logging host <ip>",
                "description": "配置日志服务器地址",
                "example": "logging host 192.168.1.100"
            },
            {
                "name": "配置日志级别",
                "command": "logging trap <level>",
                "description": "设置发送到服务器的日志级别(emergencies/alerts/critical/errors/warnings/notifications/informational/debugging)",
                "example": "logging trap informational"
            },
            {
                "name": "配置日志源接口",
                "command": "logging source-interface <interface>",
                "description": "设置发送日志的源接口",
                "example": "logging source-interface vlan 1"
            },
            {
                "name": "配置缓冲区日志",
                "command": "logging buffered <size>",
                "description": "配置日志缓冲区大小",
                "example": "logging buffered 65535"
            },
            {
                "name": "配置控制台日志级别",
                "command": "logging console <level>",
                "description": "设置控制台日志输出级别",
                "example": "logging console warnings"
            },
            {
                "name": "查看日志",
                "command": "show logging",
                "description": "查看系统日志",
                "example": "show logging"
            },
            {
                "name": "清除日志",
                "command": "clear logging",
                "description": "清除日志缓冲区",
                "example": "clear logging"
            }
        ],
        "SNMP配置": [
            {
                "name": "启用SNMP",
                "command": "snmp-server",
                "description": "启用SNMP服务",
                "example": "snmp-server"
            },
            {
                "name": "配置SNMP只读团体名",
                "command": "snmp-server community <string> ro",
                "description": "配置SNMP只读团体字",
                "example": "snmp-server community public ro"
            },
            {
                "name": "配置SNMP读写团体名",
                "command": "snmp-server community <string> rw",
                "description": "配置SNMP读写团体字",
                "example": "snmp-server community private rw"
            },
            {
                "name": "配置SNMP系统信息",
                "command": "snmp-server contact <info>\nsnmp-server location <location>",
                "description": "配置SNMP联系人和管理位置",
                "example": "snmp-server contact admin@example.com\nsnmp-server location Server_Room_A"
            },
            {
                "name": "配置SNMP Trap",
                "command": "snmp-server enable traps",
                "description": "启用所有SNMP Trap",
                "example": "snmp-server enable traps"
            },
            {
                "name": "配置Trap接收主机",
                "command": "snmp-server host <ip> traps <community>",
                "description": "配置Trap接收服务器",
                "example": "snmp-server host 192.168.1.100 traps public"
            },
            {
                "name": "配置SNMPv3用户",
                "command": "snmp-server user <username> <group> auth [md5|sha] <auth-password> priv [des|aes] <priv-password>",
                "description": "配置SNMPv3用户",
                "example": "snmp-server user snmpadmin snmpgroup auth sha AuthPass123 priv aes PrivPass123"
            },
            {
                "name": "配置SNMPv3组",
                "command": "snmp-server group <groupname> v3 {noauth|auth|priv}",
                "description": "配置SNMPv3组",
                "example": "snmp-server group snmpgroup v3 priv"
            },
            {
                "name": "查看SNMP配置",
                "command": "show snmp",
                "description": "查看SNMP配置和统计",
                "example": "show snmp"
            }
        ],
        "NTP配置": [
            {
                "name": "配置NTP服务器",
                "command": "ntp server <ip>",
                "description": "配置NTP时间服务器",
                "example": "ntp server 192.168.1.100"
            },
            {
                "name": "配置NTP认证",
                "command": "ntp authenticate\nntp authentication-key <key> md5 <password>\nntp trusted-key <key>\nntp server <ip> key <key>",
                "description": "配置NTP密钥认证",
                "example": "ntp authenticate\nntp authentication-key 1 md5 NTPKey123\nntp trusted-key 1\nntp server 192.168.1.100 key 1"
            },
            {
                "name": "配置NTP源接口",
                "command": "ntp source <interface>",
                "description": "配置NTP源接口",
                "example": "ntp source vlan 1"
            },
            {
                "name": "设置时区",
                "command": "clock timezone <name> <offset>",
                "description": "配置时区",
                "example": "clock timezone CST +8"
            },
            {
                "name": "查看NTP状态",
                "command": "show ntp status",
                "description": "查看NTP同步状态",
                "example": "show ntp status"
            },
            {
                "name": "查看NTP关联",
                "command": "show ntp associations",
                "description": "查看NTP服务器关联",
                "example": "show ntp associations"
            }
        ],
        "NetStream配置": [
            {
                "name": "启用NetStream",
                "command": "ip netstream enable",
                "description": "全局启用NetStream功能",
                "example": "ip netstream enable"
            },
            {
                "name": "配置NetStream采集器",
                "command": "ip netstream export host <ip> <port>",
                "description": "配置NetStream数据输出目标",
                "example": "ip netstream export host 192.168.1.100 9996"
            },
            {
                "name": "配置NetStream源接口",
                "command": "ip netstream export source <interface>",
                "description": "配置NetStream输出源接口",
                "example": "ip netstream export source vlan 1"
            },
            {
                "name": "配置NetStream版本",
                "command": "ip netstream export version <5|9>",
                "description": "配置NetStream输出版本",
                "example": "ip netstream export version 9"
            },
            {
                "name": "接口启用NetStream",
                "command": "interface <interface>\nip netstream [in|out]",
                "description": "接口启用NetStream流量采集",
                "example": "interface GigabitEthernet 0/1\nip netstream in"
            },
            {
                "name": "查看NetStream统计",
                "command": "show ip netstream statistics",
                "description": "查看NetStream统计信息",
                "example": "show ip netstream statistics"
            }
        ]
    },
    "QoS配置": {
        "优先级映射": [
            {
                "name": "配置端口信任CoS",
                "command": "interface <interface>\nmls qos trust cos",
                "description": "信任端口的CoS优先级",
                "example": "interface GigabitEthernet 0/1\nmls qos trust cos"
            },
            {
                "name": "配置端口信任DSCP",
                "command": "interface <interface>\nmls qos trust dscp",
                "description": "信任端口的DSCP优先级",
                "example": "interface GigabitEthernet 0/1\nmls qos trust dscp"
            },
            {
                "name": "配置CoS到队列映射",
                "command": "mls qos srr-queue output cos-map queue <queue-id> <cos-values>",
                "description": "配置CoS值到输出队列的映射",
                "example": "mls qos srr-queue output cos-map queue 1 0 1"
            },
            {
                "name": "配置DSCP到队列映射",
                "command": "mls qos srr-queue output dscp-map queue <queue-id> <dscp-values>",
                "description": "配置DSCP值到输出队列的映射",
                "example": "mls qos srr-queue output dscp-map queue 1 0 8 16 24"
            },
            {
                "name": "配置默认CoS值",
                "command": "interface <interface>\nmld qos cos <cos-value>",
                "description": "配置接口默认CoS值",
                "example": "interface GigabitEthernet 0/1\nmls qos cos 5"
            },
            {
                "name": "查看QoS配置",
                "command": "show mls qos interface <interface>",
                "description": "查看接口QoS配置",
                "example": "show mls qos interface GigabitEthernet 0/1"
            }
        ],
        "流量整形": [
            {
                "name": "配置流量整形",
                "command": "interface <interface>\ntraffic-shape group <acl> <bps> [burst-size]",
                "description": "对匹配ACL的流量进行整形",
                "example": "interface GigabitEthernet 0/1\ntraffic-shape group 100 10000000"
            },
            {
                "name": "配置端口整形",
                "command": "interface <interface>\nshape average <bps>",
                "description": "对端口流量进行整形",
                "example": "interface GigabitEthernet 0/1\nshape average 10000000"
            },
            {
                "name": "配置策略映射整形",
                "command": "policy-map <policy-name>\nclass <class-name>\nshape average <bps>",
                "description": "在策略中配置流量整形",
                "example": "policy-map SHAPE-POLICY\nclass class-default\nshape average 50000000"
            },
            {
                "name": "查看流量整形状态",
                "command": "show traffic-shape [interface <interface>]",
                "description": "查看流量整形统计",
                "example": "show traffic-shape interface GigabitEthernet 0/1"
            }
        ],
        "拥塞管理": [
            {
                "name": "配置优先级队列",
                "command": "interface <interface>\npriority-queue out",
                "description": "启用接口优先级队列",
                "example": "interface GigabitEthernet 0/1\npriority-queue out"
            },
            {
                "name": "配置队列带宽比例",
                "command": "interface <interface>\nsrr-queue bandwidth shape <weight1> <weight2> ...",
                "description": "配置队列带宽分配比例",
                "example": "interface GigabitEthernet 0/1\nsrr-queue bandwidth shape 10 20 30 40"
            },
            {
                "name": "配置限速策略",
                "command": "policy-map <policy-name>\nclass <class-name>\npolice <bps> <burst> conform-action transmit exceed-action drop",
                "description": "配置流量限速策略",
                "example": "policy-map LIMIT-POLICY\nclass class-default\npolice 10000000 10000 conform-action transmit exceed-action drop"
            },
            {
                "name": "应用QoS策略",
                "command": "interface <interface>\nservice-policy {input|output} <policy-name>",
                "description": "在接口应用QoS策略",
                "example": "interface GigabitEthernet 0/1\nservice-policy input LIMIT-POLICY"
            },
            {
                "name": "配置WRED",
                "command": "interface <interface>\nrandom-detect",
                "description": "启用加权随机早期检测",
                "example": "interface GigabitEthernet 0/1\nrandom-detect"
            },
            {
                "name": "查看QoS策略",
                "command": "show policy-map interface <interface>",
                "description": "查看接口QoS策略统计",
                "example": "show policy-map interface GigabitEthernet 0/1"
            }
        ]
    },
    "IPv6配置": {
        "基础配置": [
            {
                "name": "启用IPv6",
                "command": "ipv6 unicast-routing",
                "description": "启用IPv6单播路由功能",
                "example": "ipv6 unicast-routing"
            },
            {
                "name": "配置IPv6地址",
                "command": "interface <interface>\nipv6 address <ipv6-address>/<prefix-length>",
                "description": "配置接口IPv6地址",
                "example": "interface vlan 10\nipv6 address 2001:db8::1/64"
            },
            {
                "name": "配置链路本地地址",
                "command": "interface <interface>\nipv6 address fe80::1 link-local",
                "description": "配置IPv6链路本地地址",
                "example": "interface vlan 10\nipv6 address fe80::1 link-local"
            },
            {
                "name": "启用IPv6自动配置",
                "command": "interface <interface>\nipv6 address autoconfig",
                "description": "启用无状态地址自动配置",
                "example": "interface vlan 10\nipv6 address autoconfig"
            },
            {
                "name": "配置IPv6邻居",
                "command": "interface <interface>\nipv6 neighbor <ipv6-address> <mac>",
                "description": "配置静态IPv6邻居",
                "example": "interface vlan 10\nipv6 neighbor 2001:db8::100 0011.2233.4455"
            },
            {
                "name": "查看IPv6接口",
                "command": "show ipv6 interface [brief]",
                "description": "查看IPv6接口信息",
                "example": "show ipv6 interface brief"
            },
            {
                "name": "查看IPv6邻居",
                "command": "show ipv6 neighbors",
                "description": "查看IPv6邻居表",
                "example": "show ipv6 neighbors"
            }
        ],
        "IPv6路由": [
            {
                "name": "配置IPv6静态路由",
                "command": "ipv6 route <prefix>/<length> <next-hop>",
                "description": "添加IPv6静态路由",
                "example": "ipv6 route 2001:db8:1::/64 2001:db8::254"
            },
            {
                "name": "配置IPv6默认路由",
                "command": "ipv6 route ::/0 <next-hop>",
                "description": "配置IPv6默认路由",
                "example": "ipv6 route ::/0 2001:db8::254"
            },
            {
                "name": "启用IPv6 OSPF",
                "command": "ipv6 router ospf <process-id>",
                "description": "启用OSPFv3进程",
                "example": "ipv6 router ospf 1\nrouter-id 1.1.1.1"
            },
            {
                "name": "接口启用OSPFv3",
                "command": "interface <interface>\nipv6 ospf <process-id> area <area-id>",
                "description": "接口启用OSPFv3",
                "example": "interface vlan 10\nipv6 ospf 1 area 0"
            },
            {
                "name": "查看IPv6路由表",
                "command": "show ipv6 route",
                "description": "查看IPv6路由表",
                "example": "show ipv6 route"
            },
            {
                "name": "查看IPv6 OSPF邻居",
                "command": "show ipv6 ospf neighbor",
                "description": "查看OSPFv3邻居",
                "example": "show ipv6 ospf neighbor"
            }
        ]
    }
}

RUIJIE_CASES = [
    {
        "title": "接入交换机基础配置",
        "description": "接入层交换机初始化配置案例，包含VLAN划分、管理IP配置、远程管理等",
        "steps": [
            "configure terminal",
            "hostname RG-Access-SW-01",
            "vlan 10",
            " name Sales_Department",
            "vlan 20",
            " name Engineering_Department",
            "vlan 30",
            " name Management",
            "interface vlan 30",
            " ip address 192.168.30.1 255.255.255.0",
            "interface range GigabitEthernet 0/1-10",
            " switchport mode access",
            " switchport access vlan 10",
            "interface range GigabitEthernet 0/11-20",
            " switchport mode access",
            " switchport access vlan 20",
            "ip route 0.0.0.0 0.0.0.0 192.168.30.254",
            "username admin privilege 15 secret Admin@123",
            "ip ssh version 2",
            "crypto key generate rsa modulus 2048",
            "line vty 0 4",
            " transport input ssh",
            " login local",
            "spanning-tree mode rstp",
            "spanning-tree portfast default",
            "write"
        ]
    },
    {
        "title": "端口安全完整配置",
        "description": "配置端口安全防止非法设备接入，包含MAC地址绑定和违规处理",
        "steps": [
            "configure terminal",
            "interface GigabitEthernet 0/1",
            " description Secure-Port-for-PC",
            " switchport mode access",
            " switchport access vlan 10",
            " switchport port-security",
            " switchport port-security maximum 1",
            " switchport port-security violation shutdown",
            " switchport port-security mac-address sticky",
            " spanning-tree portfast",
            " spanning-tree bpduguard enable",
            "switchport port-security mac-address sticky",
            "exit",
            "errdisable recovery cause psecure-violation",
            "errdisable recovery interval 300",
            "write"
        ]
    },
    {
        "title": "核心交换机VRRP配置",
        "description": "配置双核心交换机VRRP实现网关冗余",
        "steps": [
            "核心交换机A配置:",
            "configure terminal",
            "hostname RG-Core-A",
            "vlan 10",
            " name Users_VLAN",
            "interface vlan 10",
            " ip address 192.168.10.2 255.255.255.0",
            " standby 1 ip 192.168.10.1",
            " standby 1 priority 150",
            " standby 1 preempt",
            " standby 1 authentication md5 VRRPAuth",
            "",
            "核心交换机B配置:",
            "configure terminal",
            "hostname RG-Core-B",
            "vlan 10",
            " name Users_VLAN",
            "interface vlan 10",
            " ip address 192.168.10.3 255.255.255.0",
            " standby 1 ip 192.168.10.1",
            " standby 1 priority 100",
            " standby 1 preempt",
            " standby 1 authentication md5 VRRPAuth",
            "write"
        ]
    },
    {
        "title": "链路聚合配置案例",
        "description": "配置交换机间链路聚合提高带宽和冗余",
        "steps": [
            "configure terminal",
            "vlan 10",
            "vlan 20",
            "vlan 30",
            "interface aggregateport 1",
            " description To-Distribution-SW",
            " switchport mode trunk",
            " switchport trunk allowed vlan 10,20,30",
            " aggregport mode active",
            "interface range GigabitEthernet 0/23-24",
            " port-group 1",
            "interface range GigabitEthernet 0/1-10",
            " switchport mode access",
            " switchport access vlan 10",
            "interface range GigabitEthernet 0/11-20",
            " switchport mode access",
            " switchport access vlan 20",
            "write"
        ]
    },
    {
        "title": "OSPF动态路由配置",
        "description": "配置OSPF协议实现企业网络互联",
        "steps": [
            "configure terminal",
            "hostname RG-Core-Router",
            "interface vlan 10",
            " ip address 192.168.10.1 255.255.255.0",
            "interface vlan 20",
            " ip address 192.168.20.1 255.255.255.0",
            "interface vlan 100",
            " description To-WAN",
            " ip address 10.0.0.1 255.255.255.252",
            "router ospf 1",
            " router-id 1.1.1.1",
            " network 192.168.10.0 0.0.0.255 area 0",
            " network 192.168.20.0 0.0.0.255 area 0",
            " network 10.0.0.0 0.0.0.3 area 1",
            " passive-interface vlan 10",
            " passive-interface vlan 20",
            " default-information originate always",
            "ip route 0.0.0.0 0.0.0.0 10.0.0.2",
            "write"
        ]
    },
    {
        "title": "DHCP Snooping安全配置",
        "description": "配置DHCP Snooping防止DHCP欺骗攻击",
        "steps": [
            "configure terminal",
            "ip dhcp snooping",
            "ip dhcp snooping vlan 10,20,30",
            "interface GigabitEthernet 0/24",
            " description DHCP-Server-Port",
            " ip dhcp snooping trust",
            "interface range GigabitEthernet 0/1-23",
            " ip dhcp snooping limit rate 100",
            "ip dhcp snooping information option",
            "show ip dhcp snooping",
            "show ip dhcp snooping binding",
            "write"
        ]
    },
    {
        "title": "MSTP多生成树配置",
        "description": "配置MSTP实现VLAN级负载均衡和冗余",
        "steps": [
            "configure terminal",
            "spanning-tree mode mstp",
            "spanning-tree mst configuration",
            " name RG-MST-Instance",
            " revision 1",
            " instance 1 vlan 10,20",
            " instance 2 vlan 30,40",
            "instance 3 vlan 50,60",
            "exit",
            "spanning-tree mst 1 priority 4096",
            "spanning-tree mst 2 priority 8192",
            "spanning-tree mst 3 priority 12288",
            "interface range GigabitEthernet 0/1-10",
            " spanning-tree portfast",
            "interface range GigabitEthernet 0/23-24",
            " spanning-tree link-type point-to-point",
            "write"
        ]
    },
    {
        "title": "QoS限速配置案例",
        "description": "配置QoS策略限制特定流量带宽",
        "steps": [
            "configure terminal",
            "access-list 100 permit tcp any any eq 80",
            "access-list 100 permit tcp any any eq 443",
            "access-list 101 permit tcp any any range 6000 7000",
            "class-map match-all WEB-TRAFFIC",
            " match access-group 100",
            "class-map match-all P2P-TRAFFIC",
            " match access-group 101",
            "policy-map LIMIT-POLICY",
            " class WEB-TRAFFIC",
            "  police 50000000 10000 conform-action transmit exceed-action drop",
            " class P2P-TRAFFIC",
            "  police 10000000 5000 conform-action transmit exceed-action drop",
            " interface GigabitEthernet 0/1",
            " service-policy input LIMIT-POLICY",
            "write"
        ]
    },
    {
        "title": "IPv6基础配置案例",
        "description": "配置交换机IPv6功能实现双栈网络",
        "steps": [
            "configure terminal",
            "ipv6 unicast-routing",
            "vlan 10",
            " name IPv6-Test",
            "interface vlan 10",
            " ip address 192.168.10.1 255.255.255.0",
            " ipv6 address 2001:db8:10::1/64",
            " ipv6 address fe80::1 link-local",
            " ipv6 nd prefix 2001:db8:10::/64",
            "interface GigabitEthernet 0/1",
            " switchport mode access",
            " switchport access vlan 10",
            "ipv6 route ::/0 2001:db8::ffff",
            "show ipv6 interface brief",
            "show ipv6 neighbors",
            "write"
        ]
    },
    {
        "title": "SNMP网管配置案例",
        "description": "配置SNMPv3实现安全的网络管理",
        "steps": [
            "configure terminal",
            "snmp-server",
            "snmp-server contact network-admin@example.com",
            "snmp-server location DataCenter_RackA",
            "snmp-server group admin-group v3 priv",
            "snmp-server user snmpadmin admin-group auth sha AuthKey@2026 priv aes128 PrivKey@2026",
            "snmp-server enable traps",
            "snmp-server host 192.168.1.100 traps version 3 priv snmpadmin",
            "show snmp",
            "show snmp user",
            "show snmp group",
            "write"
        ]
    }
]
