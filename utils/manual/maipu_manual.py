#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
迈普交换机命令手册 - 完整版

包含迈普全系列交换机命令集，涵盖基础配置、接口配置、路由配置、
安全配置、生成树、高可用、管理与监控、QoS、IPv6等完整配置。

迈普命令风格类似Cisco，使用show命令查看信息。

作者: Dimples (QQ: 1367880198)
版本: 2.0
更新日期: 2026-04-21
"""

MAIPU_COMMANDS = {
    "基础配置": {
        "系统管理": [
            {"name": "进入配置模式", "command": "configure terminal", "description": "从特权模式进入全局配置模式", "example": "configure terminal"},
            {"name": "设置主机名", "command": "hostname <name>", "description": "设置设备主机名", "example": "hostname MP-Core-SW-01"},
            {"name": "查看版本信息", "command": "show version", "description": "查看设备硬件和软件版本信息", "example": "show version"},
            {"name": "查看当前配置", "command": "show running-config", "description": "查看当前运行配置", "example": "show running-config"},
            {"name": "查看启动配置", "command": "show startup-config", "description": "查看启动配置文件内容", "example": "show startup-config"},
            {"name": "保存配置", "command": "write memory\n或: copy running-config startup-config", "description": "保存当前配置到启动配置", "example": "write memory"},
            {"name": "重启设备", "command": "reload", "description": "重启设备", "example": "reload"},
            {"name": "恢复出厂配置", "command": "erase startup-config\nreload", "description": "清除配置并重启恢复出厂", "example": "erase startup-config\nreload"},
            {"name": "设置系统时间", "command": "clock set <HH:MM:SS> <MONTH> <DAY> <YEAR>", "description": "手动设置系统时间", "example": "clock set 14:30:00 January 15 2024"},
            {"name": "查看系统时间", "command": "show clock", "description": "查看当前系统时间", "example": "show clock"},
            {"name": "查看CPU使用率", "command": "show processes cpu", "description": "查看CPU使用率和进程信息", "example": "show processes cpu"},
            {"name": "查看内存使用", "command": "show memory", "description": "查看内存使用情况", "example": "show memory"},
            {"name": "设置空闲超时", "command": "line console 0\nexec-timeout <minutes> [seconds]", "description": "设置Console空闲超时时间", "example": "line console 0\nexec-timeout 5 30"},
            {"name": "禁用域名解析", "command": "no ip domain-lookup", "description": "禁用命令行域名解析", "example": "no ip domain-lookup"},
            {"name": "配置启动文件", "command": "boot system flash:<filename>", "description": "设置下次启动文件", "example": "boot system flash:mp3100.bin"}
        ],
        "用户与权限管理": [
            {"name": "创建本地用户", "command": "username <name> privilege <level> password <password>", "description": "创建本地用户并设置权限级别和密码", "example": "username admin privilege 15 password Admin@123"},
            {"name": "设置加密密码", "command": "username <name> secret <password>", "description": "为用户设置加密密码", "example": "username admin secret Admin@123"},
            {"name": "设置特权密码", "command": "enable secret <password>", "description": "设置进入特权模式的密码", "example": "enable secret Enable@123"},
            {"name": "设置明文特权密码", "command": "enable password <password>", "description": "设置明文特权密码(不推荐)", "example": "enable password Enable@123"},
            {"name": "配置密码加密", "command": "service password-encryption", "description": "启用密码加密服务", "example": "service password-encryption"},
            {"name": "配置用户命令权限", "command": "privilege <exec|configure> level <level> <command>", "description": "为权限级别配置允许执行的命令", "example": "privilege exec level 5 show running-config"},
            {"name": "查看用户账户", "command": "show users accounts", "description": "查看本地用户账户", "example": "show users accounts"},
            {"name": "删除用户", "command": "no username <name>", "description": "删除指定用户", "example": "no username test"},
            {"name": "AAA认证配置", "command": "aaa new-model", "description": "启用AAA认证模型", "example": "aaa new-model"},
            {"name": "登录认证配置", "command": "aaa authentication login <list-name> local", "description": "配置登录认证列表使用本地数据库", "example": "aaa authentication login default local"}
        ],
        "SSH配置": [
            {"name": "启用SSH服务", "command": "ip ssh server enable", "description": "启用SSH服务器", "example": "ip ssh server enable"},
            {"name": "设置SSH版本", "command": "ip ssh version <1|2>", "description": "设置SSH协议版本(推荐v2)", "example": "ip ssh version 2"},
            {"name": "生成RSA密钥", "command": "crypto key generate rsa modulus <bits>", "description": "生成RSA密钥对(推荐2048位)", "example": "crypto key generate rsa modulus 2048"},
            {"name": "生成ECDSA密钥", "command": "crypto key generate ecdsa", "description": "生成ECDSA密钥对", "example": "crypto key generate ecdsa"},
            {"name": "设置SSH超时", "command": "ip ssh timeout <seconds>", "description": "设置SSH连接超时时间", "example": "ip ssh timeout 60"},
            {"name": "设置认证重试", "command": "ip ssh authentication-retries <times>", "description": "设置SSH认证重试次数", "example": "ip ssh authentication-retries 3"},
            {"name": "配置VTY使用SSH", "command": "line vty 0 4\ntransport input ssh\nlogin local", "description": "配置VTY只允许SSH登录使用本地认证", "example": "line vty 0 4\ntransport input ssh\nlogin local"},
            {"name": "查看SSH状态", "command": "show ip ssh", "description": "查看SSH服务状态", "example": "show ip ssh"},
            {"name": "查看SSH会话", "command": "show ssh", "description": "查看当前SSH会话", "example": "show ssh"},
            {"name": "删除RSA密钥", "command": "crypto key zeroize rsa", "description": "删除RSA密钥对", "example": "crypto key zeroize rsa"}
        ],
        "Telnet配置": [
            {"name": "启用Telnet服务", "command": "ip telnet server enable", "description": "启用Telnet服务器(不安全)", "example": "ip telnet server enable"},
            {"name": "配置VTY允许Telnet", "command": "line vty 0 4\ntransport input telnet\nlogin local", "description": "配置VTY允许Telnet登录", "example": "line vty 0 4\ntransport input telnet\nlogin local"},
            {"name": "设置Telnet端口", "command": "ip telnet port <port>", "description": "修改Telnet服务端口(默认23)", "example": "ip telnet port 2323"},
            {"name": "关闭Telnet服务", "command": "no ip telnet server enable", "description": "关闭Telnet服务提高安全性", "example": "no ip telnet server enable"},
            {"name": "同时允许SSH和Telnet", "command": "line vty 0 4\ntransport input all", "description": "VTY同时允许SSH和Telnet", "example": "line vty 0 4\ntransport input all"}
        ],
        "Console配置": [
            {"name": "配置Console密码", "command": "line console 0\npassword <password>\nlogin", "description": "配置Console登录密码", "example": "line console 0\npassword Console@123\nlogin"},
            {"name": "Console本地认证", "command": "line console 0\nlogin local", "description": "Console使用本地用户认证", "example": "line console 0\nlogin local"},
            {"name": "设置Console波特率", "command": "line console 0\nspeed <baud-rate>", "description": "设置Console波特率(默认9600)", "example": "line console 0\nspeed 115200"},
            {"name": "设置数据位", "command": "line console 0\ndatabits <5|6|7|8>", "description": "设置数据位(默认8)", "example": "line console 0\ndatabits 8"},
            {"name": "设置停止位", "command": "line console 0\nstopbits <1|2>", "description": "设置停止位(默认1)", "example": "line console 0\nstopbits 1"}
        ],
        "域名解析": [
            {"name": "启用域名解析", "command": "ip domain-lookup", "description": "启用IP域名解析功能", "example": "ip domain-lookup"},
            {"name": "配置DNS服务器", "command": "ip name-server <ip> [ip2 ...]", "description": "配置DNS服务器地址", "example": "ip name-server 8.8.8.8 114.114.114.114"},
            {"name": "配置域名后缀", "command": "ip domain-name <domain>", "description": "配置默认域名后缀", "example": "ip domain-name example.com"},
            {"name": "静态主机映射", "command": "ip host <name> <ip>", "description": "配置静态主机名到IP映射", "example": "ip host server1 192.168.1.100"},
            {"name": "查看主机映射", "command": "show hosts", "description": "查看主机名映射表", "example": "show hosts"}
        ]
    },
    "接口配置": {
        "以太网接口": [
            {"name": "进入接口配置", "command": "interface <type> <slot/port>", "description": "进入指定接口配置模式", "example": "interface gigabitethernet 0/1"},
            {"name": "配置接口IP", "command": "interface <if>\nip address <ip> <mask>", "description": "为三层接口配置IP地址", "example": "interface gigabitethernet 0/1\nip address 192.168.1.1 255.255.255.0"},
            {"name": "配置从IP", "command": "interface <if>\nip address <ip> <mask> secondary", "description": "为接口配置第二个IP地址", "example": "interface gigabitethernet 0/1\nip address 192.168.2.1 255.255.255.0 secondary"},
            {"name": "删除接口IP", "command": "interface <if>\nno ip address", "description": "删除接口的IP地址", "example": "interface gigabitethernet 0/1\nno ip address"},
            {"name": "接口描述", "command": "interface <if>\ndescription <text>", "description": "为接口添加描述信息", "example": "interface gigabitethernet 0/1\ndescription To_Server_Room"},
            {"name": "开启接口", "command": "interface <if>\nno shutdown", "description": "开启接口", "example": "interface gigabitethernet 0/1\nno shutdown"},
            {"name": "关闭接口", "command": "interface <if>\nshutdown", "description": "关闭接口", "example": "interface gigabitethernet 0/1\nshutdown"},
            {"name": "设置接口速率", "command": "interface <if>\nspeed <10|100|1000|auto>", "description": "设置接口速率", "example": "interface gigabitethernet 0/1\nspeed 1000"},
            {"name": "设置双工模式", "command": "interface <if>\nduplex <half|full|auto>", "description": "设置接口双工模式", "example": "interface gigabitethernet 0/1\nduplex full"},
            {"name": "流量控制", "command": "interface <if>\nflowcontrol <receive|send> <on|off>", "description": "配置流量控制", "example": "interface gigabitethernet 0/1\nflowcontrol receive on"},
            {"name": "查看接口状态", "command": "show interface <if>", "description": "查看接口详细状态", "example": "show interface gigabitethernet 0/1"},
            {"name": "查看接口简要", "command": "show interface status", "description": "查看所有接口简要状态", "example": "show interface status"},
            {"name": "查看接口IP简表", "command": "show ip interface brief", "description": "查看接口IP状态简要列表", "example": "show ip interface brief"},
            {"name": "清除接口计数", "command": "clear counters <if>", "description": "清除接口统计计数器", "example": "clear counters gigabitethernet 0/1"}
        ],
        "VLAN接口": [
            {"name": "创建VLAN", "command": "vlan <id>", "description": "创建VLAN并进入VLAN配置模式", "example": "vlan 10"},
            {"name": "VLAN命名", "command": "vlan <id>\nname <name>", "description": "为VLAN设置名称", "example": "vlan 10\nname Sales_Department"},
            {"name": "批量创建VLAN", "command": "vlan range <start-end>", "description": "批量创建连续编号的VLAN", "example": "vlan range 10-20"},
            {"name": "删除VLAN", "command": "no vlan <id>", "description": "删除指定VLAN", "example": "no vlan 10"},
            {"name": "查看VLAN", "command": "show vlan", "description": "查看所有VLAN信息", "example": "show vlan"},
            {"name": "查看指定VLAN", "command": "show vlan id <id>", "description": "查看指定VLAN详细信息", "example": "show vlan id 10"},
            {"name": "创建VLAN接口", "command": "interface vlan <id>", "description": "创建并进入VLAN三层接口", "example": "interface vlan 10"},
            {"name": "VLAN接口配置IP", "command": "interface vlan <id>\nip address <ip> <mask>", "description": "为VLAN接口配置IP地址", "example": "interface vlan 10\nip address 192.168.10.1 255.255.255.0"},
            {"name": "VLAN接口描述", "command": "interface vlan <id>\ndescription <text>", "description": "为VLAN接口添加描述", "example": "interface vlan 10\ndescription Gateway_for_VLAN10"}
        ],
        "接口VLAN": [
            {"name": "配置Access接口", "command": "interface <if>\nswitchport mode access\nswitchport access vlan <id>", "description": "配置接口为Access模式并加入VLAN", "example": "interface gigabitethernet 0/1\nswitchport mode access\nswitchport access vlan 10"},
            {"name": "配置Trunk接口", "command": "interface <if>\nswitchport mode trunk\nswitchport trunk allowed vlan <list>", "description": "配置接口为Trunk模式", "example": "interface gigabitethernet 0/24\nswitchport mode trunk\nswitchport trunk allowed vlan 10,20,30"},
            {"name": "Trunk允许所有VLAN", "command": "switchport trunk allowed vlan all", "description": "Trunk允许所有VLAN通过", "example": "interface gigabitethernet 0/24\nswitchport trunk allowed vlan all"},
            {"name": "Trunk Native VLAN", "command": "switchport trunk native vlan <id>", "description": "设置Trunk接口Native VLAN", "example": "interface gigabitethernet 0/24\nswitchport trunk native vlan 99"},
            {"name": "配置Hybrid接口", "command": "interface <if>\nswitchport mode hybrid", "description": "配置接口为Hybrid模式", "example": "interface gigabitethernet 0/1\nswitchport mode hybrid"},
            {"name": "Hybrid Untagged端口", "command": "switchport hybrid untagged vlan <list>", "description": "Hybrid接口剥离VLAN标签", "example": "interface gigabitethernet 0/1\nswitchport hybrid untagged vlan 10,20"},
            {"name": "Hybrid Tagged端口", "command": "switchport hybrid tagged vlan <list>", "description": "Hybrid接口保留VLAN标签", "example": "interface gigabitethernet 0/1\nswitchport hybrid tagged vlan 100"},
            {"name": "Hybrid PVID", "command": "switchport hybrid pvid vlan <id>", "description": "设置Hybrid接口PVID", "example": "interface gigabitethernet 0/1\nswitchport hybrid pvid vlan 10"},
            {"name": "查看接口VLAN配置", "command": "show interface <if> switchport", "description": "查看接口VLAN模式配置", "example": "show interface gigabitethernet 0/1 switchport"}
        ],
        "链路聚合": [
            {"name": "创建聚合接口", "command": "interface port-channel <id>", "description": "创建链路聚合接口", "example": "interface port-channel 1"},
            {"name": "配置聚合模式LACP", "command": "interface port-channel <id>\nchannel-protocol lacp", "description": "设置聚合协议为LACP", "example": "interface port-channel 1\nchannel-protocol lacp"},
            {"name": "配置聚合模式静态", "command": "interface port-channel <id>\nchannel-group <id> mode on", "description": "设置静态聚合模式", "example": "interface port-channel 1\nchannel-group 1 mode on"},
            {"name": "加入成员接口", "command": "interface <if>\nchannel-group <id> mode <active|passive>", "description": "将物理接口加入聚合组", "example": "interface range gigabitethernet 0/1-2\nchannel-group 1 mode active"},
            {"name": "设置LACP优先级", "command": "lacp system-priority <value>", "description": "设置LACP系统优先级", "example": "lacp system-priority 100"},
            {"name": "设置端口LACP优先级", "command": "interface <if>\nlacp port-priority <value>", "description": "设置端口LACP优先级", "example": "interface gigabitethernet 0/1\nlacp port-priority 100"},
            {"name": "配置负载均衡", "command": "port-channel load-balance <src-dst-mac|src-dst-ip>", "description": "设置聚合负载均衡算法", "example": "port-channel load-balance src-dst-ip"},
            {"name": "查看聚合状态", "command": "show etherchannel summary", "description": "查看链路聚合简要状态", "example": "show etherchannel summary"},
            {"name": "查看聚合详细", "command": "show etherchannel <id> detail", "description": "查看指定聚合详细状态", "example": "show etherchannel 1 detail"}
        ]
    },
    "路由配置": {
        "静态路由": [
            {"name": "配置静态路由", "command": "ip route <network> <mask> <next-hop> [distance]", "description": "配置静态路由", "example": "ip route 192.168.100.0 255.255.255.0 10.0.0.1"},
            {"name": "默认路由", "command": "ip route 0.0.0.0 0.0.0.0 <gateway>", "description": "配置默认路由", "example": "ip route 0.0.0.0 0.0.0.0 192.168.1.254"},
            {"name": "配置路由距离值", "command": "ip route <network> <mask> <next-hop> <distance>", "description": "设置静态路由管理距离", "example": "ip route 10.0.0.0 255.255.255.0 192.168.1.1 10"},
            {"name": "黑洞路由", "command": "ip route <network> <mask> null0", "description": "配置黑洞路由丢弃流量", "example": "ip route 10.10.0.0 255.255.255.0 null0"},
            {"name": "删除静态路由", "command": "no ip route <network> <mask> <next-hop>", "description": "删除指定静态路由", "example": "no ip route 192.168.100.0 255.255.255.0 10.0.0.1"},
            {"name": "查看路由表", "command": "show ip route", "description": "查看IP路由表", "example": "show ip route"},
            {"name": "查看静态路由", "command": "show ip route static", "description": "只查看静态路由", "example": "show ip route static"},
            {"name": "追踪路由", "command": "traceroute <ip>", "description": "追踪到目标的路径", "example": "traceroute 8.8.8.8"},
            {"name": "查看路由汇总", "command": "show ip route summary", "description": "查看路由表汇总信息", "example": "show ip route summary"}
        ],
        "OSPF配置": [
            {"name": "启用OSPF进程", "command": "router ospf <process-id>", "description": "启动OSPF路由进程", "example": "router ospf 1"},
            {"name": "设置Router ID", "command": "router ospf <pid>\nrouter-id <id>", "description": "设置OSPF Router ID", "example": "router ospf 1\nrouter-id 1.1.1.1"},
            {"name": "宣告网络", "command": "router ospf <pid>\nnetwork <network> <wildcard> area <area>", "description": "宣告网络到OSPF区域", "example": "router ospf 1\nnetwork 192.168.0.0 0.0.255.255 area 0"},
            {"name": "配置Stub区域", "command": "router ospf <pid>\narea <id> stub", "description": "配置Stub区域", "example": "router ospf 1\narea 1 stub"},
            {"name": "配置NSSA区域", "command": "router ospf <pid>\narea <id> nssa", "description": "配置NSSA区域", "example": "router ospf 1\narea 1 nssa"},
            {"name": "配置被动接口", "command": "router ospf <pid>\npassive-interface <if>", "description": "禁止接口发送OSPF报文", "example": "router ospf 1\npassive-interface vlan 10"},
            {"name": "配置接口认证", "command": "interface <if>\nip ospf authentication <message-digest|clear>\nip ospf message-digest-key <key-id> md5 <password>", "description": "配置OSPF接口认证", "example": "interface gigabitethernet 0/1\nip ospf authentication message-digest\nip ospf message-digest-key 1 md5 Maipu@123"},
            {"name": "设置接口开销", "command": "interface <if>\nip ospf cost <cost>", "description": "设置OSPF接口开销", "example": "interface gigabitethernet 0/1\nip ospf cost 10"},
            {"name": "设置DR优先级", "command": "interface <if>\nip ospf priority <value>", "description": "设置DR选举优先级", "example": "interface gigabitethernet 0/1\nip ospf priority 100"},
            {"name": "查看OSPF邻居", "command": "show ip ospf neighbor", "description": "查看OSPF邻居关系", "example": "show ip ospf neighbor"},
            {"name": "查看OSPF路由", "command": "show ip ospf route", "description": "查看OSPF路由", "example": "show ip ospf route"},
            {"name": "查看OSPF接口", "command": "show ip ospf interface", "description": "查看OSPF接口信息", "example": "show ip ospf interface"},
            {"name": "重置OSPF进程", "command": "clear ip ospf process", "description": "重启OSPF进程", "example": "clear ip ospf process"}
        ],
        "BGP配置": [
            {"name": "启用BGP进程", "command": "router bgp <as-number>", "description": "启动BGP路由进程", "example": "router bgp 65001"},
            {"name": "设置Router ID", "command": "router bgp <as>\nbgp router-id <id>", "description": "设置BGP Router ID", "example": "router bgp 65001\nbgp router-id 1.1.1.1"},
            {"name": "配置邻居", "command": "router bgp <as>\nneighbor <ip> remote-as <as>", "description": "配置BGP邻居", "example": "router bgp 65001\nneighbor 10.0.0.2 remote-as 65002"},
            {"name": "指定更新源", "command": "router bgp <as>\nneighbor <ip> update-source <if>", "description": "指定BGP更新源接口", "example": "router bgp 65001\nneighbor 10.0.0.2 update-source loopback 0"},
            {"name": "宣告网络", "command": "router bgp <as>\nnetwork <network> mask <mask>", "description": "宣告网络到BGP", "example": "router bgp 65001\nnetwork 192.168.0.0 mask 255.255.0.0"},
            {"name": "配置下一跳本地", "command": "router bgp <as>\nneighbor <ip> next-hop-self", "description": "向IBGP邻居发布路由时设置下一跳为本地", "example": "router bgp 65001\nneighbor 192.168.1.2 next-hop-self"},
            {"name": "引入直连路由", "command": "router bgp <as>\nredistribute connected", "description": "引入直连路由到BGP", "example": "router bgp 65001\nredistribute connected"},
            {"name": "引入静态路由", "command": "router bgp <as>\nredistribute static", "description": "引入静态路由到BGP", "example": "router bgp 65001\nredistribute static"},
            {"name": "查看BGP邻居", "command": "show ip bgp neighbors", "description": "查看BGP邻居状态", "example": "show ip bgp neighbors"},
            {"name": "查看BGP路由", "command": "show ip bgp", "description": "查看BGP路由表", "example": "show ip bgp"},
            {"name": "刷新BGP会话", "command": "clear ip bgp <ip> [soft]", "description": "重置BGP会话", "example": "clear ip bgp 10.0.0.2 soft"}
        ],
        "RIP配置": [
            {"name": "启用RIP进程", "command": "router rip", "description": "启动RIP路由进程", "example": "router rip"},
            {"name": "设置RIP版本", "command": "router rip\nversion <1|2>", "description": "设置RIP版本", "example": "router rip\nversion 2"},
            {"name": "宣告网络", "command": "router rip\nnetwork <network>", "description": "宣告直连网络", "example": "router rip\nnetwork 192.168.0.0"},
            {"name": "关闭自动汇总", "command": "router rip\nno auto-summary", "description": "关闭RIP自动汇总", "example": "router rip\nno auto-summary"},
            {"name": "配置被动接口", "command": "router rip\npassive-interface <if>", "description": "禁止接口发送RIP报文", "example": "router rip\npassive-interface vlan 10"},
            {"name": "查看RIP路由", "command": "show ip route rip", "description": "查看RIP路由", "example": "show ip route rip"},
            {"name": "查看RIP数据库", "command": "show ip rip database", "description": "查看RIP数据库", "example": "show ip rip database"}
        ]
    },
    "安全配置": {
        "ACL配置": [
            {"name": "创建标准ACL", "command": "ip access-list standard <name|number>", "description": "创建标准ACL(1-99或1300-1999)", "example": "ip access-list standard 10"},
            {"name": "创建扩展ACL", "command": "ip access-list extended <name|number>", "description": "创建扩展ACL(100-199或2000-2699)", "example": "ip access-list extended 100"},
            {"name": "标准ACL规则", "command": "<permit|deny> <source> <wildcard>", "description": "配置标准ACL规则", "example": "ip access-list standard 10\npermit 192.168.1.0 0.0.0.255"},
            {"name": "扩展ACL规则", "command": "<permit|deny> <protocol> <src> <wld> <dst> <wld> [<port>]", "description": "配置扩展ACL规则", "example": "ip access-list extended 100\npermit tcp 192.168.1.0 0.0.0.255 host 10.0.0.1 eq 80"},
            {"name": "端口匹配eq", "command": "eq <port>", "description": "匹配特定端口", "example": "permit tcp any any eq 80"},
            {"name": "端口范围range", "command": "range <start> <end>", "description": "匹配端口范围", "example": "permit tcp any any range 20 21"},
            {"name": "拒绝所有", "command": "deny ip any any", "description": "拒绝所有IP流量", "example": "ip access-list extended 100\ndeny ip any any"},
            {"name": "接口应用ACL", "command": "interface <if>\nip access-group <acl> <in|out>", "description": "在接口应用ACL过滤流量", "example": "interface gigabitethernet 0/1\nip access-group 100 in"},
            {"name": "VTY应用ACL", "command": "line vty 0 4\naccess-class <acl> in", "description": "限制VTY访问", "example": "line vty 0 4\naccess-class 10 in"},
            {"name": "查看ACL", "command": "show access-lists [name|number]", "description": "查看ACL配置", "example": "show access-lists 100"},
            {"name": "查看接口ACL", "command": "show ip interface <if> | include access", "description": "查看接口应用的ACL", "example": "show ip interface gigabitethernet 0/1 | include access"}
        ],
        "端口安全": [
            {"name": "启用端口安全", "command": "interface <if>\nswitchport port-security", "description": "启用端口安全功能", "example": "interface gigabitethernet 0/1\nswitchport port-security"},
            {"name": "最大MAC数", "command": "interface <if>\nswitchport port-security maximum <number>", "description": "设置端口最大MAC地址数", "example": "interface gigabitethernet 0/1\nswitchport port-security maximum 1"},
            {"name": "配置安全MAC", "command": "interface <if>\nswitchport port-security mac-address <mac>", "description": "手动配置安全MAC地址", "example": "interface gigabitethernet 0/1\nswitchport port-security mac-address 0001.0002.0003"},
            {"name": "自动学习MAC", "command": "interface <if>\nswitchport port-security mac-address sticky", "description": "启用粘性MAC自动学习", "example": "interface gigabitethernet 0/1\nswitchport port-security mac-address sticky"},
            {"name": "安全违规处理", "command": "interface <if>\nswitchport port-security violation <protect|restrict|shutdown>", "description": "设置违规处理方式", "example": "interface gigabitethernet 0/1\nswitchport port-security violation shutdown"},
            {"name": "查看端口安全", "command": "show port-security interface <if>", "description": "查看接口端口安全状态", "example": "show port-security interface gigabitethernet 0/1"},
            {"name": "查看端口安全MAC", "command": "show port-security address", "description": "查看端口安全MAC地址表", "example": "show port-security address"}
        ],
        "DHCP Snooping": [
            {"name": "启用DHCP Snooping", "command": "ip dhcp snooping", "description": "全局启用DHCP Snooping", "example": "ip dhcp snooping"},
            {"name": "VLAN启用", "command": "ip dhcp snooping vlan <vlan-list>", "description": "在指定VLAN启用DHCP Snooping", "example": "ip dhcp snooping vlan 10,20"},
            {"name": "信任接口", "command": "interface <if>\nip dhcp snooping trust", "description": "配置DHCP信任接口", "example": "interface gigabitethernet 0/24\nip dhcp snooping trust"},
            {"name": "非信任接口限速", "command": "interface <if>\nip dhcp snooping limit rate <rate>", "description": "限制非信任接口DHCP报文速率", "example": "interface gigabitethernet 0/1\nip dhcp snooping limit rate 100"},
            {"name": "查看绑定表", "command": "show ip dhcp snooping binding", "description": "查看DHCP Snooping绑定表", "example": "show ip dhcp snooping binding"},
            {"name": "查看Snooping配置", "command": "show ip dhcp snooping", "description": "查看DHCP Snooping配置", "example": "show ip dhcp snooping"}
        ],
        "ARP安全": [
            {"name": "静态ARP绑定", "command": "arp <ip> <mac> arpa", "description": "配置静态ARP表项", "example": "arp 192.168.1.100 0001.0002.0003 arpa"},
            {"name": "动态ARP检测", "command": "ip arp inspection vlan <vlan-list>", "description": "在VLAN启用动态ARP检测", "example": "ip arp inspection vlan 10"},
            {"name": "配置信任接口", "command": "interface <if>\nip arp inspection trust", "description": "配置ARP检测信任接口", "example": "interface gigabitethernet 0/24\nip arp inspection trust"},
            {"name": "查看ARP表", "command": "show arp", "description": "查看ARP表", "example": "show arp"},
            {"name": "清除ARP表", "command": "clear arp-cache", "description": "清除动态ARP表项", "example": "clear arp-cache"}
        ],
        "IPSG配置": [
            {"name": "启用IPSG", "command": "interface <if>\nip verify source [port-security]", "description": "启用IP源防护", "example": "interface gigabitethernet 0/1\nip verify source port-security"},
            {"name": "静态绑定", "command": "ip source binding <mac> vlan <id> <ip> interface <if>", "description": "配置静态IP/MAC绑定", "example": "ip source binding 0001.0002.0003 vlan 10 192.168.1.100 interface gigabitethernet 0/1"},
            {"name": "查看绑定表", "command": "show ip verify source", "description": "查看IPSG绑定表", "example": "show ip verify source"}
        ]
    },
    "生成树配置": {
        "STP基础": [
            {"name": "启用STP", "command": "spanning-tree", "description": "全局启用STP", "example": "spanning-tree"},
            {"name": "关闭STP", "command": "no spanning-tree", "description": "全局关闭STP", "example": "no spanning-tree"},
            {"name": "配置STP模式", "command": "spanning-tree mode <stp|rstp|mstp>", "description": "设置STP模式", "example": "spanning-tree mode mstp"},
            {"name": "设置桥优先级", "command": "spanning-tree priority <priority>", "description": "设置网桥优先级", "example": "spanning-tree priority 4096"},
            {"name": "设置根桥", "command": "spanning-tree root <primary|secondary>", "description": "设置为主/备根桥", "example": "spanning-tree root primary"},
            {"name": "设置端口优先级", "command": "interface <if>\nspanning-tree port-priority <priority>", "description": "设置端口优先级", "example": "interface gigabitethernet 0/1\nspanning-tree port-priority 128"},
            {"name": "设置端口开销", "command": "interface <if>\nspanning-tree cost <cost>", "description": "设置端口开销", "example": "interface gigabitethernet 0/1\nspanning-tree cost 200000"},
            {"name": "启用端口边缘", "command": "interface <if>\nspanning-tree portfast", "description": "配置边缘端口(立即转发)", "example": "interface gigabitethernet 0/1\nspanning-tree portfast"},
            {"name": "BPDU保护", "command": "spanning-tree bpdufilter enable\nspanning-tree bpduguard enable", "description": "配置BPDU保护", "example": "interface gigabitethernet 0/1\nspanning-tree bpduguard enable"},
            {"name": "根保护", "command": "interface <if>\nspanning-tree guard root", "description": "配置根保护", "example": "interface gigabitethernet 0/24\nspanning-tree guard root"},
            {"name": "查看STP状态", "command": "show spanning-tree", "description": "查看STP状态", "example": "show spanning-tree"},
            {"name": "查看STP端口", "command": "show spanning-tree interface <if>", "description": "查看端口STP状态", "example": "show spanning-tree interface gigabitethernet 0/1"}
        ],
        "MSTP配置": [
            {"name": "进入MST配置", "command": "spanning-tree mst configuration", "description": "进入MST配置模式", "example": "spanning-tree mst configuration"},
            {"name": "配置域名", "command": "spanning-tree mst configuration\nname <name>", "description": "设置MST域名", "example": "spanning-tree mst configuration\nname MST_DOMAIN_1"},
            {"name": "配置实例映射", "command": "spanning-tree mst configuration\ninstance <id> vlan <list>", "description": "配置VLAN到实例映射", "example": "spanning-tree mst configuration\ninstance 1 vlan 10,20"},
            {"name": "配置修订级别", "command": "spanning-tree mst configuration\nrevision <level>", "description": "设置MST修订级别", "example": "spanning-tree mst configuration\nrevision 1"},
            {"name": "设置实例优先级", "command": "spanning-tree mst <id> priority <priority>", "description": "设置实例网桥优先级", "example": "spanning-tree mst 1 priority 4096"},
            {"name": "查看MST配置", "command": "show spanning-tree mst configuration", "description": "查看MST配置", "example": "show spanning-tree mst configuration"}
        ]
    },
    "高可用配置": {
        "VRRP配置": [
            {"name": "配置VRRP组", "command": "interface <if>\nstandby <group-id> ip <vip>", "description": "配置VRRP/HSRP虚拟网关", "example": "interface vlan 10\nstandby 1 ip 192.168.10.254"},
            {"name": "设置优先级", "command": "standby <group-id> priority <priority>", "description": "设置优先级", "example": "interface vlan 10\nstandby 1 priority 120"},
            {"name": "配置抢占", "command": "standby <group-id> preempt [delay <seconds>]", "description": "配置抢占模式", "example": "interface vlan 10\nstandby 1 preempt delay 20"},
            {"name": "跟踪接口", "command": "standby <group-id> track <if> decrement <value>", "description": "跟踪接口状态降低优先级", "example": "interface vlan 10\nstandby 1 track gigabitethernet 0/1 decrement 30"},
            {"name": "认证配置", "command": "standby <group-id> authentication <text|md5> <password>", "description": "配置VRRP认证", "example": "interface vlan 10\nstandby 1 authentication md5 key-string Maipu@123"},
            {"name": "查看VRRP状态", "command": "show standby", "description": "查看VRRP状态", "example": "show standby"},
            {"name": "查看VRRP详细", "command": "show standby <interface>", "description": "查看指定接口VRRP状态", "example": "show standby vlan 10"}
        ],
        "堆叠配置": [
            {"name": "查看堆叠状态", "command": "show switch stack-port summary", "description": "查看堆叠端口状态", "example": "show switch stack-port summary"},
            {"name": "设置堆叠优先级", "command": "switch <number> priority <value>", "description": "设置堆叠成员优先级", "example": "switch 1 priority 15"},
            {"name": "设置堆叠端口", "command": "interface port-channel <id>\nswitchport mode trunk", "description": "配置堆叠端口", "example": "interface port-channel 1\nswitchport mode trunk"}
        ],
        "BFD配置": [
            {"name": "启用BFD", "command": "bfd", "description": "全局启用BFD", "example": "bfd"},
            {"name": "创建BFD会话", "command": "bfd <name> neighbor <ip> interface <if>", "description": "创建BFD会话", "example": "bfd session1 neighbor 10.0.0.2 interface gigabitethernet 0/1"},
            {"name": "配置检测参数", "command": "bfd <name> interval <min-tx> min-rx <min-rx> multiplier <mult>", "description": "配置BFD检测参数", "example": "bfd session1 interval 100 min-rx 100 multiplier 3"},
            {"name": "查看BFD会话", "command": "show bfd neighbors", "description": "查看BFD邻居", "example": "show bfd neighbors"}
        ]
    },
    "管理与监控": {
        "日志配置": [
            {"name": "启用日志", "command": "logging on", "description": "启用系统日志功能", "example": "logging on"},
            {"name": "配置日志主机", "command": "logging host <ip>", "description": "配置日志服务器", "example": "logging host 192.168.1.100"},
            {"name": "配置日志级别", "command": "logging trap <level>", "description": "设置日志级别(emergencies/alerts/critical/errors/warnings/notifications/informational/debugging)", "example": "logging trap informational"},
            {"name": "配置日志缓冲", "command": "logging buffered <size>", "description": "配置日志缓冲区大小", "example": "logging buffered 64000"},
            {"name": "查看日志", "command": "show logging", "description": "查看日志配置和缓冲区", "example": "show logging"},
            {"name": "清除日志", "command": "clear logging", "description": "清除日志缓冲区", "example": "clear logging"}
        ],
        "SNMP配置": [
            {"name": "启用SNMP", "command": "snmp-server", "description": "启用SNMP服务", "example": "snmp-server"},
            {"name": "配置只读共同体", "command": "snmp-server community <string> ro", "description": "配置SNMP只读共同体", "example": "snmp-server community public ro"},
            {"name": "配置读写共同体", "command": "snmp-server community <string> rw", "description": "配置SNMP读写共同体", "example": "snmp-server community private rw"},
            {"name": "配置Trap", "command": "snmp-server enable traps", "description": "启用Trap", "example": "snmp-server enable traps"},
            {"name": "配置Trap目标", "command": "snmp-server host <ip> traps <community>", "description": "配置Trap目标主机", "example": "snmp-server host 192.168.1.100 traps public"},
            {"name": "配置系统信息", "command": "snmp-server contact <text>\nsnmp-server location <text>", "description": "配置系统联系人/位置", "example": "snmp-server contact admin@company.com\nsnmp-server location 'IDC_Room_A'"},
            {"name": "查看SNMP配置", "command": "show snmp", "description": "查看SNMP配置", "example": "show snmp"}
        ],
        "NTP配置": [
            {"name": "启用NTP", "command": "ntp server <ip> [prefer]", "description": "配置NTP服务器", "example": "ntp server 192.168.1.100 prefer"},
            {"name": "配置时区", "command": "clock timezone <name> <offset-hours> <offset-minutes>", "description": "配置时区", "example": "clock timezone BJ +8"},
            {"name": "查看NTP状态", "command": "show ntp status", "description": "查看NTP同步状态", "example": "show ntp status"},
            {"name": "查看NTP关联", "command": "show ntp associations", "description": "查看NTP关联", "example": "show ntp associations"}
        ],
        "NetFlow配置": [
            {"name": "启用NetFlow", "command": "interface <if>\nip flow ingress\nip flow egress", "description": "接口启用NetFlow", "example": "interface gigabitethernet 0/1\nip flow ingress"},
            {"name": "配置输出目标", "command": "ip flow-export destination <ip> <port>", "description": "配置NetFlow输出目标", "example": "ip flow-export destination 192.168.1.100 2055"},
            {"name": "设置版本", "command": "ip flow-export version <5|9>", "description": "设置NetFlow版本", "example": "ip flow-export version 9"},
            {"name": "查看NetFlow", "command": "show ip flow export", "description": "查看NetFlow配置", "example": "show ip flow export"}
        ]
    },
    "QoS配置": {
        "优先级映射": [
            {"name": "配置信任DSCP", "command": "interface <if>\nmpls qos trust dscp", "description": "信任DSCP优先级", "example": "interface gigabitethernet 0/1\nmpls qos trust dscp"},
            {"name": "配置信任CoS", "command": "interface <if>\nmpls qos trust cos", "description": "信任CoS/802.1p优先级", "example": "interface gigabitethernet 0/1\nmpls qos trust cos"},
            {"name": "设置DSCP值", "command": "interface <if>\nmpls qos dscp <value>", "description": "为流量标记DSCP值", "example": "interface gigabitethernet 0/1\nmpls qos dscp 46"}
        ],
        "流量整形与限速": [
            {"name": "接口限速", "command": "interface <if>\nrate-limit input <bps> <burst-normal> <burst-max> conform-action <action>\nrate-limit output <bps> <burst-normal> <burst-max> conform-action <action>", "description": "接口限速(committed access rate)", "example": "interface gigabitethernet 0/1\nrate-limit input 10000000 1875000 3750000 conform-action transmit exceed-action drop"},
            {"name": "策略映射限速", "command": "policy-map <name>\nclass <class-name>\nshape average <bps>", "description": "基于策略映射的流量整形", "example": "policy-map LIMIT_10M\nclass class-default\nshape average 10000000"}
        ]
    },
    "IPv6配置": {
        "基础配置": [
            {"name": "启用IPv6", "command": "ipv6 unicast-routing", "description": "启用IPv6单播路由", "example": "ipv6 unicast-routing"},
            {"name": "接口IPv6地址", "command": "interface <if>\nipv6 address <ipv6>/<prefix>", "description": "配置接口IPv6地址", "example": "interface gigabitethernet 0/1\nipv6 address 2001:db8::1/64"},
            {"name": "自动链路本地地址", "command": "interface <if>\nipv6 enable", "description": "自动配置链路本地地址", "example": "interface gigabitethernet 0/1\nipv6 enable"},
            {"name": "查看IPv6接口", "command": "show ipv6 interface <if>", "description": "查看接口IPv6信息", "example": "show ipv6 interface gigabitethernet 0/1"},
            {"name": "查看IPv6路由", "command": "show ipv6 route", "description": "查看IPv6路由表", "example": "show ipv6 route"},
            {"name": "Ping IPv6", "command": "ping ipv6 <ipv6>", "description": "测试IPv6连通性", "example": "ping ipv6 2001:db8::1"}
        ],
        "IPv6路由": [
            {"name": "静态路由", "command": "ipv6 route <dest>/<prefix> <next-hop>", "description": "配置IPv6静态路由", "example": "ipv6 route ::/0 2001:db8::ffff"},
            {"name": "OSPFv3", "command": "ipv6 router ospf <process-id>\nrouter-id <id>", "description": "配置OSPFv3", "example": "ipv6 router ospf 1\nrouter-id 1.1.1.1"}
        ]
    }
}

MAIPU_CASES = [
    {
        "title": "接入交换机基础配置",
        "description": "接入层交换机初始化配置，包括VLAN、管理IP、SSH、端口安全",
        "steps": [
            "# 1. 系统基本配置",
            "configure terminal",
            "hostname Access-SW-01",
            "",
            "# 2. 创建VLAN",
            "vlan 10",
            " name Sales",
            "vlan 20",
            " name Engineering",
            "vlan 30",
            " name Finance",
            "vlan 100",
            " name Management",
            "",
            "# 3. 配置管理IP",
            "interface vlan 1",
            " ip address 192.168.1.10 255.255.255.0",
            "",
            "# 4. 配置默认网关",
            "ip route 0.0.0.0 0.0.0.0 192.168.1.254",
            "",
            "# 5. 配置Access端口",
            "interface range gigabitethernet 0/1-10",
            " switchport mode access",
            " switchport access vlan 10",
            " description Sales_Users",
            "",
            "interface range gigabitethernet 0/11-20",
            " switchport mode access",
            " switchport access vlan 20",
            " description Engineering_Users",
            "",
            "# 6. 配置Trunk上行口",
            "interface gigabitethernet 0/24",
            " switchport mode trunk",
            " switchport trunk allowed vlan 10,20,30,100",
            " description Uplink_to_Core",
            "",
            "# 7. 配置SSH",
            "ip ssh version 2",
            "crypto key generate rsa modulus 2048",
            "ip ssh server enable",
            "",
            "username admin privilege 15 secret Admin@123",
            "",
            "line vty 0 4",
            " transport input ssh",
            " login local",
            "",
            "# 8. 配置端口安全",
            "interface range gigabitethernet 0/1-20",
            " switchport port-security",
            " switchport port-security maximum 2",
            " switchport port-security mac-address sticky",
            " switchport port-security violation shutdown",
            "",
            "# 9. 配置STP边缘端口",
            "interface range gigabitethernet 0/1-20",
            " spanning-tree portfast",
            "",
            "# 10. 保存配置",
            "write memory"
        ]
    },
    {
        "title": "核心交换机配置",
        "description": "核心交换机完整配置，包括VLAN接口、路由、ACL、VRRP",
        "steps": [
            "# 1. 系统配置",
            "configure terminal",
            "hostname Core-SW-01",
            "",
            "# 2. 创建VLAN",
            "vlan 10,20,30,100,200",
            "",
            "# 3. 配置VLAN接口",
            "interface vlan 10",
            " ip address 192.168.10.1 255.255.255.0",
            " description Gateway_VLAN10_Sales",
            "",
            "interface vlan 20",
            " ip address 192.168.20.1 255.255.255.0",
            " description Gateway_VLAN20_Engineering",
            "",
            "interface vlan 30",
            " ip address 192.168.30.1 255.255.255.0",
            " description Gateway_VLAN30_Finance",
            "",
            "interface vlan 100",
            " ip address 192.168.100.1 255.255.255.0",
            " description Management_Network",
            "",
            "interface vlan 200",
            " ip address 10.0.0.1 255.255.255.252",
            " description WAN_Uplink",
            "",
            "# 4. 配置DHCP",
            "ip dhcp pool VLAN10_POOL",
            " network 192.168.10.0 255.255.255.0",
            " default-router 192.168.10.1",
            " dns-server 8.8.8.8 114.114.114.114",
            " lease 3",
            "",
            "interface vlan 10",
            " ip dhcp relay",
            "",
            "# 5. 配置静态路由",
            "ip route 0.0.0.0 0.0.0.0 10.0.0.2",
            "",
            "# 6. 配置OSPF",
            "router ospf 1",
            " router-id 1.1.1.1",
            " network 192.168.0.0 0.0.255.255 area 0",
            " network 10.0.0.0 0.0.0.3 area 0",
            "",
            "# 7. 配置ACL",
            "ip access-list extended DENY_ENGINEERING_TO_FINANCE",
            " deny ip 192.168.20.0 0.0.0.255 192.168.30.0 0.0.0.255",
            " permit ip any any",
            "",
            "interface vlan 20",
            " ip access-group DENY_ENGINEERING_TO_FINANCE out",
            "",
            "# 8. 配置VRRP",
            "interface vlan 10",
            " standby 1 ip 192.168.10.254",
            " standby 1 priority 120",
            " standby 1 preempt delay 20",
            "",
            "# 9. 配置NTP",
            "ntp server 192.168.100.100 prefer",
            "clock timezone BJ +8",
            "",
            "# 10. 配置日志",
            "logging on",
            "logging host 192.168.100.101",
            "logging trap informational",
            "",
            "# 11. 配置SNMP",
            "snmp-server community public ro",
            "snmp-server location 'IDC_Room_A'",
            "snmp-server contact admin@company.com",
            "",
            "write memory"
        ]
    },
    {
        "title": "链路聚合配置",
        "description": "迈普链路聚合配置，LACP动态模式",
        "steps": [
            "# 1. 创建聚合接口",
            "interface port-channel 1",
            " description To_Core_Switch",
            " switchport mode trunk",
            " switchport trunk allowed vlan 10,20,30",
            "",
            "# 2. 添加成员接口",
            "interface range gigabitethernet 0/1-2",
            " channel-group 1 mode active",
            "",
            "# 3. 配置LACP优先级(可选)",
            "lacp system-priority 100",
            "",
            "# 4. 配置负载均衡",
            "port-channel load-balance src-dst-ip",
            "",
            "# 5. 验证配置",
            "show etherchannel summary",
            "show etherchannel 1 detail"
        ]
    },
    {
        "title": "MSTP多生成树配置",
        "description": "MSTP多实例生成树配置，实现负载均衡",
        "steps": [
            "# 1. 配置MSTP",
            "spanning-tree mode mstp",
            "",
            "# 2. 配置MST域",
            "spanning-tree mst configuration",
            " name COMPANY_MST",
            " revision 1",
            " instance 1 vlan 10,20",
            " instance 2 vlan 30,40",
            "",
            "# 3. 核心交换机1配置",
            "spanning-tree mst 1 root primary",
            "spanning-tree mst 2 root secondary",
            "",
            "# 4. 核心交换机2配置",
            "spanning-tree mst 1 root secondary",
            "spanning-tree mst 2 root primary",
            "",
            "# 5. 配置边缘端口",
            "interface range gigabitethernet 0/1-20",
            " spanning-tree portfast",
            "",
            "# 6. BPDU保护",
            "interface range gigabitethernet 0/1-20",
            " spanning-tree bpduguard enable",
            "",
            "# 7. 验证配置",
            "show spanning-tree mst configuration",
            "show spanning-tree mst 1"
        ]
    },
    {
        "title": "DHCP服务器配置",
        "description": "交换机作为DHCP服务器配置",
        "steps": [
            "# 1. 启用DHCP服务",
            "service dhcp",
            "",
            "# 2. 配置地址池",
            "ip dhcp pool VLAN10_POOL",
            " network 192.168.10.0 255.255.255.0",
            " default-router 192.168.10.1",
            " dns-server 8.8.8.8 114.114.114.114",
            " excluded-address 192.168.10.1 192.168.10.10",
            " lease 3",
            "",
            "ip dhcp pool VLAN20_POOL",
            " network 192.168.20.0 255.255.255.0",
            " default-router 192.168.20.1",
            " dns-server 8.8.8.8",
            " lease 7",
            "",
            "# 3. 配置DHCP中继(如需要)",
            "interface vlan 30",
            " ip helper-address 192.168.100.100",
            "",
            "# 4. 查看DHCP配置",
            "show ip dhcp binding",
            "show ip dhcp pool"
        ]
    },
    {
        "title": "QoS流量限速配置",
        "description": "基于ACL的流量限速配置",
        "steps": [
            "# 1. 创建ACL匹配流量",
            "ip access-list extended LIMIT_TRAFFIC",
            " permit ip 192.168.10.0 0.0.0.255 any",
            "",
            "# 2. 创建类映射",
            "class-map LIMIT_CLASS",
            " match access-group name LIMIT_TRAFFIC",
            "",
            "# 3. 创建策略映射",
            "policy-map LIMIT_POLICY",
            " class LIMIT_CLASS",
            "  shape average 10000000",
            "",
            "# 4. 应用策略",
            "interface gigabitethernet 0/1",
            " policy-map LIMIT_POLICY in",
            "",
            "# 5. 验证配置",
            "show policy-map interface gigabitethernet 0/1"
        ]
    },
    {
        "title": "端口镜像配置",
        "description": "配置端口镜像用于流量监控",
        "steps": [
            "# 1. 配置源端口(被镜像端口)",
            "monitor session 1 source interface gigabitethernet 0/1 both",
            "",
            "# 2. 配置目的端口(监控端口)",
            "monitor session 1 destination interface gigabitethernet 0/24",
            "",
            "# 3. 验证配置",
            "show monitor session 1",
            "show monitor session all"
        ]
    },
    {
        "title": "BFD与VRRP联动配置",
        "description": "BFD检测链路故障联动VRRP快速切换",
        "steps": [
            "# 1. 启用BFD",
            "bfd",
            "",
            "# 2. 创建跟踪对象",
            "track 1 bfd interface gigabitethernet 0/1",
            "",
            "# 3. VRRP联动Track",
            "interface vlan 10",
            " standby 1 ip 192.168.10.254",
            " standby 1 priority 120",
            " standby 1 track 1 decrement 40",
            "",
            "# 4. 验证配置",
            "show bfd neighbors",
            "show track",
            "show standby"
        ]
    }
]
