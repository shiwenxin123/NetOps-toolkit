#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
中兴 ZXR10 交换机配置生成器。

目标 CLI 是经典 ZXROS，覆盖常见的 ZXR10 5200 / 5900 / 8900 系列：
configure terminal、hostname、interface vlan、switchport、acl standard/extend、
router ospf/bgp、smartgroup、spanning-tree、lldp、ssh server enable。

不覆盖：
- 5900E / 5960 / 9900 的 ROSNG（见 zte_rosng_config.py：system-user、gei-0/1/1/1、switchvlan-configuration）
- C300 / C600 等 OLT（见 zte_olt_config.py）

界面里的 VlanifN / Vlan-interfaceN 会写成 interface vlan N。
用户输入只做单行拼接，拒绝换行和控制字符，避免一条字段变成多条命令。
"""

import re
import time


class ZTEConfigError(ValueError):
    """用户字段无法安全写入一条 CLI。"""


_BREAK = re.compile(r"[\r\n\x00]")
_SINGLE = re.compile(r"^[A-Za-z0-9_./:@%+=,-]{1,128}$")
_IFACE = re.compile(r"^(?:vlan \d{1,4}|[A-Za-z][A-Za-z0-9_./:-]{0,63})$")
_VLANIF = re.compile(r"(?i)^(?:vlanif|vlan-interface)\s*(\d{1,4})$")

_TIMEZONES = {
    "UTC+8": ("Beijing", 8),
    "UTC+0": ("UTC", 0),
    "UTC-5": ("EST", -5),
    "UTC-8": ("PST", -8),
}

_STP_MODE = {"stp": "sstp", "sstp": "sstp", "rstp": "rstp", "mstp": "mstp"}
_SMARTGROUP_MODE = {
    "manual": "on",
    "lacp-static": "active",
    "lacp-dynamic": "passive",
    "on": "on",
    "active": "active",
    "passive": "passive",
}
_ACL_DIRECTION = {
    "inbound": "in",
    "outbound": "out",
    "in": "in",
    "out": "out",
}
_PORT_SEC_VIOLATION = {"protect", "restrict", "shutdown"}


def _raw(value):
    return "" if value is None else str(value)


def _single(value, field):
    text = _raw(value).strip()
    if not text or _BREAK.search(_raw(value)) or not _SINGLE.match(text):
        raise ZTEConfigError(f"{field} 含有空格、换行或无法写入命令的字符")
    return text


def _optional_single(value, field):
    if value is None or str(value).strip() == "":
        return ""
    return _single(value, field)


def _phrase(value, field):
    text = _raw(value).replace("\t", " ").strip()
    if _BREAK.search(_raw(value)):
        raise ZTEConfigError(f"{field} 不能包含换行")
    if any(char in text for char in "`;&|$<>\\"):
        raise ZTEConfigError(f"{field} 含有无法写入命令的字符")
    return text


def _label(value, field):
    """主机名、VLAN 名：允许中文，但不允许空格和换行。"""
    text = _phrase(value, field)
    if not text or not re.match(r"^[\w.-]{1,64}$", text):
        raise ZTEConfigError(f"{field} 只能包含字母、数字、中文、下划线、点或短横线")
    return text


def _integer(value, field, low, high):
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ZTEConfigError(f"{field} 不是整数")
    if number < low or number > high:
        raise ZTEConfigError(f"{field} 超出范围 {low}-{high}")
    return number


def normalize_interface(name, field="接口"):
    """把华为/H3C 的 Vlanif 写法改成 ZXR10 的 vlan N，其余名称原样校验。"""
    text = _phrase(name, field)
    if not text:
        raise ZTEConfigError(f"{field} 为空")
    matched = _VLANIF.match(text)
    if matched:
        text = f"vlan {int(matched.group(1))}"
    if not _IFACE.match(text):
        raise ZTEConfigError(f"{field} 不是可用的 ZXR10 接口名")
    return text


def _address(addr, wildcard, field):
    token = _optional_single(addr, field) if addr else ""
    if not token or token.lower() == "any":
        return "any"
    wild = _optional_single(wildcard, field + "通配符")
    if wild:
        return f"{token} {wild}"
    return token


def _banner(text):
    body = _raw(text).replace("\r\n", "\n").replace("\r", "\n")
    if "\x00" in body:
        raise ZTEConfigError("Banner 含有无法写入的字符")
    body = body.strip("\n")
    if not body:
        return ""
    for mark in ("#", "%", "^", "~", "@"):
        if mark not in body:
            return f"banner incoming {mark}\n{body}\n{mark}"
    raise ZTEConfigError("Banner 同时包含 # % ^ ~ @，无法选择结束符")


def _section(title, lines):
    kept = [line for line in lines if line is not None and line != ""]
    if not kept:
        return ""
    return "!\n! " + title + "\n!\n" + "\n".join(kept)


class ZTEBasicGenerator:
    """系统、管理地址、登录、NTP、SNMP、日志。"""

    @staticmethod
    def generate(config):
        if not config:
            return "", []
        lines = []
        privileged = []

        hostname = config.get("hostname")
        if hostname:
            lines.append(f"hostname {_label(hostname, '主机名')}")

        password = config.get("password") or {}
        if password.get("value"):
            secret = _single(password["value"], "管理密码")
            kind = "5" if password.get("encrypted") else "0"
            lines.append(f"enable secret {kind} {secret}")

        user = config.get("user") or {}
        if user.get("username") and user.get("password"):
            username = _single(user["username"], "用户名")
            user_password = _single(user["password"], "用户密码")
            level = _integer(user.get("level", 15), "权限级别", 0, 15)
            if user.get("encrypted"):
                lines.append(
                    f"username {username} password encrypted {user_password} privilege {level}"
                )
            else:
                lines.append(
                    f"username {username} password {user_password} privilege {level}"
                )

        mgmt = config.get("mgmt_interface") or {}
        if mgmt.get("ip_address"):
            interface = normalize_interface(mgmt.get("interface") or "vlan 1", "管理接口")
            ip_addr = _single(mgmt["ip_address"], "管理IP")
            mask = _single(mgmt.get("mask") or "255.255.255.0", "管理掩码")
            lines.append(f"interface {interface}")
            lines.append(f" ip address {ip_addr} {mask}")
            lines.append(" no shutdown")
            lines.append(" exit")
            gateway = _optional_single(mgmt.get("gateway"), "网关")
            if gateway:
                lines.append(f"ip route 0.0.0.0 0.0.0.0 {gateway}")

        if config.get("enable_ssh"):
            lines.append("ssh server enable")
            port = config.get("ssh_port", 22)
            if port and int(port) != 22:
                lines.append(
                    f"! 非默认 SSH 端口 {int(port)}：经典 ZXR10 只保证 ssh server enable，"
                    "端口请按当前版本手册单独配置"
                )

        if config.get("enable_telnet"):
            lines.append("! Telnet 在经典 ZXR10 上通常随 username 可用，此处不额外打开服务")

        banner = config.get("banner") or {}
        banner_text = banner.get("login") or banner.get("motd") or ""
        if banner.get("login") and banner.get("motd"):
            banner_text = banner["motd"].rstrip() + "\n" + banner["login"].lstrip()
        rendered = _banner(banner_text)
        if rendered:
            lines.append(rendered)

        ntp = config.get("ntp") or {}
        servers = ntp.get("servers") or []
        if servers:
            zone = ntp.get("timezone") or "UTC+8"
            name, offset = _TIMEZONES.get(zone, ("Beijing", 8))
            privileged.append(f"clock timezone {name} {offset}")
            lines.append("ntp enable")
            for server in servers:
                ip_addr = _single(server.get("ip"), "NTP服务器")
                lines.append(f"ntp server {ip_addr}")

        snmp = config.get("snmp") or {}
        if any(snmp.get(key) for key in ("community_read", "community_write", "trap_host", "sys_location", "sys_contact")):
            version = _optional_single(snmp.get("version"), "SNMP版本") or "v2c"
            lines.append(f"! SNMP 版本 {version}。经典 ZXR10 用 community 区分读写")
            read_community = _optional_single(snmp.get("community_read"), "SNMP只读团体字")
            write_community = _optional_single(snmp.get("community_write"), "SNMP读写团体字")
            if read_community:
                lines.append(f"snmp-server community {read_community} ro")
            if write_community:
                lines.append(f"snmp-server community {write_community} rw")
            location = _phrase(snmp.get("sys_location") or "", "SNMP位置")
            contact = _phrase(snmp.get("sys_contact") or "", "SNMP联系人")
            if location:
                lines.append(f"snmp-server location {location}")
            if contact:
                lines.append(f"snmp-server contact {contact}")
            if snmp.get("trap_enable") and snmp.get("trap_host"):
                host = _single(snmp["trap_host"], "Trap主机")
                community = read_community or write_community or "public"
                lines.append(f"snmp host {host} ver 2c community-name {community}")

        log = config.get("log") or {}
        if log.get("info_center_enable") or log.get("host"):
            lines.append("logging on")
            if log.get("host"):
                host = _single(log["host"], "日志服务器")
                level = _optional_single(log.get("log_level"), "日志级别") or "informational"
                lines.append("syslog on")
                lines.append(f"syslog level {level}")
                lines.append(f"syslog server {host}")

        dns = config.get("dns") or {}
        for server in dns.get("servers") or []:
            lines.append(f"ip name-server {_single(server, 'DNS服务器')}")
        domain = _optional_single(dns.get("domain"), "域名")
        if domain:
            lines.append(f"ip domain-name {domain}")

        return _section("基础配置", lines), privileged


class ZTEVLANGenerator:
    """VLAN、端口、SVI、生成树。"""

    @staticmethod
    def generate(config):
        if not config:
            return ""
        lines = []
        for vlan in config.get("vlans") or []:
            vlan_id = _integer(vlan.get("id"), "VLAN ID", 1, 4094)
            lines.append(f"vlan {vlan_id}")
            name = _label(vlan["name"], "VLAN名称") if vlan.get("name") else ""
            if name:
                lines.append(f" name {name}")
            lines.append(" exit")

        for iface in config.get("interfaces") or []:
            lines.extend(ZTEVLANGenerator._port(iface))

        for vlanif in config.get("vlanifs") or []:
            vlan_id = _integer(vlanif.get("vlan_id"), "VLAN接口", 1, 4094)
            lines.append(f"interface vlan {vlan_id}")
            description = _phrase(vlanif.get("description") or "", "VLAN接口描述")
            if description:
                lines.append(f" description {description}")
            ip_addr = _single(vlanif.get("ip_address") or vlanif.get("ip"), "VLAN接口IP")
            mask = _single(vlanif.get("mask") or "255.255.255.0", "VLAN接口掩码")
            lines.append(f" ip address {ip_addr} {mask}")
            lines.append(" no shutdown")
            lines.append(" exit")

        stp = config.get("stp") or {}
        if stp:
            if stp.get("enable", True):
                mode = _STP_MODE.get(str(stp.get("mode") or "rstp").lower(), "rstp")
                lines.append("spanning-tree enable")
                lines.append(f"spanning-tree mode {mode}")
                priority = _integer(stp.get("priority", 32768), "STP优先级", 0, 61440)
                if priority != 32768:
                    lines.append(f"spanning-tree priority {priority}")
            else:
                lines.append("spanning-tree disable")

        return _section("VLAN配置", lines)

    @staticmethod
    def _port(iface):
        name = normalize_interface(iface.get("interface"), "二层接口")
        kind = str(iface.get("type") or "access").lower()
        lines = [f"interface {name}"]
        if kind == "access":
            vlan_id = _integer(iface.get("vlan_id"), "Access VLAN", 1, 4094)
            lines.append(" switchport mode access")
            lines.append(f" switchport access vlan {vlan_id}")
        elif kind == "trunk":
            lines.append(" switchport mode trunk")
            vlans = iface.get("trunk_vlans") or []
            if vlans:
                numbers = [_integer(item, "Trunk VLAN", 1, 4094) for item in vlans]
                lines.append(" switchport trunk vlan " + ",".join(str(item) for item in numbers))
            if iface.get("pvid"):
                lines.append(
                    f" switchport trunk native vlan {_integer(iface['pvid'], 'PVID', 1, 4094)}"
                )
        elif kind == "hybrid":
            lines.append(" switchport mode hybrid")
            vlan_id = iface.get("vlan_id")
            if vlan_id:
                number = _integer(vlan_id, "Hybrid VLAN", 1, 4094)
                lines.append(f" switchport hybrid native vlan {number}")
                lines.append(f" switchport hybrid vlan {number} untag")
        else:
            raise ZTEConfigError(f"不支持的端口类型 {kind}")
        lines.append(" no shutdown")
        lines.append(" exit")
        return lines


class ZTERoutingGenerator:
    """静态路由、RIP、OSPF、BGP。"""

    @staticmethod
    def generate(config):
        if not config:
            return ""
        lines = []
        for route in config.get("static_routes") or []:
            dest = _single(route.get("dest_network") or route.get("dest"), "目的网络")
            mask = _single(route.get("mask"), "路由掩码")
            nexthop = _optional_single(route.get("next_hop") or route.get("nexthop"), "下一跳")
            interface = route.get("interface")
            target = nexthop or (normalize_interface(interface, "路由出接口") if interface else "")
            if not target:
                raise ZTEConfigError("静态路由缺少下一跳或出接口")
            command = f"ip route {dest} {mask} {target}"
            if route.get("preference") is not None:
                distance = _integer(route["preference"], "路由优先级", 1, 255)
                command += f" {distance}"
            lines.append(command)

        rip = config.get("rip") or {}
        networks = rip.get("networks") or []
        if networks:
            lines.append("router rip")
            version = _integer(rip.get("version", 2), "RIP版本", 1, 2)
            lines.append(f" version {version}")
            for network in networks:
                lines.append(f" network {_single(network, 'RIP网络')}")
            lines.append(" exit")

        ospf = config.get("ospf") or {}
        ospf_networks = ospf.get("networks") or []
        if ospf_networks or ospf.get("router_id"):
            process = _integer(ospf.get("process_id", 1), "OSPF进程", 1, 65535)
            lines.append(f"router ospf {process}")
            router_id = _optional_single(ospf.get("router_id"), "OSPF Router-ID")
            if router_id:
                lines.append(f" router-id {router_id}")
            area = _phrase(str(ospf.get("area_id") or "0"), "OSPF区域") or "0"
            if not re.match(r"^[0-9.]+$", area):
                raise ZTEConfigError("OSPF 区域只能是数字或点分格式")
            for network in ospf_networks:
                address = _single(network.get("address") or network.get("network"), "OSPF网络")
                wildcard = _single(network.get("mask") or network.get("wildcard") or "0.0.0.255", "OSPF反掩码")
                lines.append(f" network {address} {wildcard} area {area}")
            lines.append(" exit")

        bgp = config.get("bgp") or {}
        peers = bgp.get("peers") or []
        bgp_networks = bgp.get("networks") or []
        if peers or bgp_networks:
            asn = _integer(bgp.get("as_number"), "BGP AS", 1, 4294967295)
            lines.append(f"router bgp {asn}")
            router_id = _optional_single(bgp.get("router_id"), "BGP Router-ID")
            if router_id:
                lines.append(f" bgp router-id {router_id}")
            for peer in peers:
                peer_ip = _single(peer.get("ip"), "BGP邻居")
                remote_as = _integer(peer.get("as") or peer.get("remote_as"), "对端AS", 1, 4294967295)
                lines.append(f" neighbor {peer_ip} remote-as {remote_as}")
            for network in bgp_networks:
                lines.append(f" network {_phrase(network, 'BGP网络')}")
            lines.append(" exit")

        return _section("路由配置", lines)


class ZTESecurityGenerator:
    """ACL、端口安全、DHCP Snooping、ARP 检测、风暴抑制。"""

    @staticmethod
    def generate(config):
        if not config:
            return ""
        lines = []
        for acl in config.get("acls") or []:
            lines.extend(ZTESecurityGenerator._acl(acl))

        for port in config.get("port_security") or []:
            if not port.get("enable", True):
                continue
            interface = normalize_interface(port.get("interface"), "端口安全接口")
            maximum = _integer(port.get("max_mac", 1), "MAC数量", 1, 1024)
            action = str(port.get("action") or "shutdown").lower()
            if action not in _PORT_SEC_VIOLATION:
                raise ZTEConfigError("端口安全违规动作只能是 protect、restrict 或 shutdown")
            lines.append(f"interface {interface}")
            lines.append(" switchport port-security")
            lines.append(f" switchport port-security maximum {maximum}")
            lines.append(f" switchport port-security violation {action}")
            if port.get("sticky"):
                lines.append(" switchport port-security mac-address sticky")
            lines.append(" exit")

        for rule in config.get("traffic_filters") or []:
            interface = normalize_interface(rule.get("interface"), "ACL应用接口")
            number = _integer(rule.get("acl_number"), "ACL号", 1, 39999)
            direction = _ACL_DIRECTION.get(str(rule.get("direction") or "in").lower())
            if not direction:
                raise ZTEConfigError("ACL 方向只能是 inbound/outbound")
            lines.append(f"interface {interface}")
            lines.append(f" ip access-group {number} {direction}")
            lines.append(" exit")

        dhcp = config.get("dhcp_snooping") or {}
        if dhcp.get("enable"):
            lines.append("ip dhcp snooping")
            if dhcp.get("vlan"):
                lines.append(
                    f"ip dhcp snooping vlan {_integer(dhcp['vlan'], 'DHCP Snooping VLAN', 1, 4094)}"
                )
            for port in dhcp.get("trusted_ports") or []:
                if not str(port).strip():
                    continue
                lines.append(f"interface {normalize_interface(port, 'DHCP信任端口')}")
                lines.append(" ip dhcp snooping trust")
                lines.append(" exit")

        arp = config.get("arp_inspection") or {}
        for vlan in arp.get("vlans") or []:
            lines.append(f"ip arp inspection vlan {_integer(vlan, 'ARP VLAN', 1, 4094)}")
        for port in arp.get("trusted_ports") or []:
            if not str(port).strip():
                continue
            lines.append(f"interface {normalize_interface(port, 'ARP信任端口')}")
            lines.append(" ip arp inspection trust")
            lines.append(" exit")

        for storm in config.get("storm_controls") or []:
            interface = normalize_interface(storm.get("interface"), "风暴抑制接口")
            lines.append(f"interface {interface}")
            if storm.get("broadcast") is not None:
                lines.append(
                    f" storm-control broadcast pps {_integer(storm['broadcast'], '广播pps', 0, 1488100)}"
                )
            if storm.get("multicast") is not None:
                lines.append(
                    f" storm-control multicast pps {_integer(storm['multicast'], '组播pps', 0, 1488100)}"
                )
            lines.append(" exit")

        anti = config.get("anti_attack") or {}
        if anti.get("enable"):
            kind = _phrase(str(anti.get("type") or "all"), "防攻击类型")
            lines.append(f"! 防攻击选项 {kind}")
            lines.append("! 经典 ZXR10 没有与华为 anti-attack 同名的命令，请用上面的 ACL、DHCP Snooping 和 ARP 检测落地")

        return _section("安全配置", lines)

    @staticmethod
    def _acl(acl):
        number = _integer(acl.get("number"), "ACL号", 1, 39999)
        extended = str(acl.get("type") or "extended").lower() == "extended"
        keyword = "extend" if extended else "standard"
        lines = []
        description = _phrase(acl.get("description") or "", "ACL描述")
        if description:
            lines.append(f"! ACL {number} {description}")
        lines.append(f"acl {keyword} number {number}")
        for rule in acl.get("rules") or []:
            rule_id = _integer(rule.get("id", 5), "ACL规则号", 1, 65535)
            action = _single(rule.get("action") or "permit", "ACL动作")
            if action not in ("permit", "deny"):
                raise ZTEConfigError("ACL 动作只能是 permit 或 deny")
            if not extended:
                source = _address(rule.get("source"), rule.get("source_wildcard"), "ACL源")
                lines.append(f" rule {rule_id} {action} {source}")
                continue
            protocol = _single(rule.get("protocol") or "ip", "ACL协议")
            if protocol not in ("ip", "tcp", "udp", "icmp"):
                raise ZTEConfigError("ACL 协议只能是 ip、tcp、udp 或 icmp")
            source = _address(rule.get("source"), rule.get("source_wildcard"), "ACL源")
            dest = _address(rule.get("destination"), rule.get("destination_wildcard"), "ACL目的")
            command = f" rule {rule_id} {action} {protocol} {source} {dest}"
            port = _optional_single(rule.get("dest_port") or rule.get("port"), "ACL端口")
            if port:
                if protocol not in ("tcp", "udp"):
                    raise ZTEConfigError("只有 TCP/UDP 规则可以带端口")
                if not port.isdigit():
                    raise ZTEConfigError("ACL 端口必须是数字")
                command += f" eq {port}"
            lines.append(command)
        lines.append(" exit")
        return lines


class ZTEInterfaceGenerator:
    """Smartgroup、LLDP、环路检测、PoE、限速。"""

    @staticmethod
    def generate(config):
        if not config:
            return ""
        lines = []
        for trunk in config.get("eth_trunks") or []:
            lines.extend(ZTEInterfaceGenerator._smartgroup(trunk))

        lldp = config.get("lldp") or {}
        if lldp.get("enable"):
            interval = _integer(lldp.get("interval", 30), "LLDP间隔", 5, 32768)
            hold = _integer(lldp.get("holdtime", interval * 4), "LLDP保持时间", 1, 65535)
            multiple = max(2, min(10, int(round(hold / float(interval)))))
            mode = str(lldp.get("mode") or "both").lower()
            admin = {"both": "enabledtxrx", "tx": "txonly", "rx": "rxonly"}.get(mode, "enabledtxrx")
            lines.append("lldp enable")
            lines.append(f"lldp hellotime {interval}")
            lines.append(f"lldp holdtime {multiple}")
            lines.append(f"! 界面保持时间按秒填写，已换算为 hello 倍数 {multiple}")
            lines.append(f"! 端口收发模式示例: interface gei_1/1 / lldp setAdminStatus {admin}")

        loop = config.get("loopback_detection") or {}
        if loop.get("enable"):
            action = str(loop.get("action") or "block").lower()
            state = "block" if action in ("block", "shutdown") else "normal"
            lines.append(f"loop-detect portstate {state}")
            vlans = loop.get("vlan_ids") or []
            vlan_text = ",".join(str(_integer(item, "环路检测VLAN", 1, 4094)) for item in vlans)
            if vlan_text:
                lines.append(f"! 按端口开启示例: loop-detect interface gei_1/1 vlan {vlan_text} enable")
            else:
                lines.append("! 按端口开启示例: loop-detect interface gei_1/1 enable")

        poe = config.get("poe") or {}
        if poe.get("enable") or poe.get("interfaces"):
            power = poe.get("max_power")
            if power:
                lines.append(f"! PoE 全局功率预算 {int(power)} mW，经典 ZXR10 多在板卡环境中配置")
            for item in poe.get("interfaces") or []:
                interface = normalize_interface(item.get("interface"), "PoE接口")
                mode = _single(item.get("mode") or "auto", "PoE模式")
                if mode not in ("auto", "force"):
                    raise ZTEConfigError("PoE 模式只能是 auto 或 force")
                priority = _single(item.get("priority") or "low", "PoE优先级")
                if priority not in ("critical", "high", "low"):
                    raise ZTEConfigError("PoE 优先级只能是 critical、high 或 low")
                lines.append(f"interface {interface}")
                if item.get("enable", True):
                    lines.append(f" power inline {mode}")
                    lines.append(f" power inline priority {priority}")
                    if item.get("max_power"):
                        lines.append(
                            f" power inline max {_integer(item['max_power'], 'PoE功率', 1, 100000)}"
                        )
                else:
                    lines.append(" power inline never")
                lines.append(" exit")

        rate_limits = config.get("rate_limits") or []
        for limit in rate_limits:
            interface = normalize_interface(limit.get("interface"), "限速接口")
            lines.append(f"interface {interface}")
            if limit.get("cir_in"):
                lines.append(
                    f" rate-limit input {_integer(limit['cir_in'], '入方向限速', 1, 10000000)}"
                )
            if limit.get("cir_out"):
                lines.append(
                    f" rate-limit output {_integer(limit['cir_out'], '出方向限速', 1, 10000000)}"
                )
            lines.append(" exit")
        if rate_limits:
            lines.append("! rate-limit 单位为 kbps；个别版本需改成 qos car")

        return _section("接口配置", lines)

    @staticmethod
    def _smartgroup(trunk):
        trunk_id = _integer(trunk.get("trunk_id"), "聚合组", 1, 64)
        mode_key = str(trunk.get("mode") or "lacp-static").lower()
        mode = _SMARTGROUP_MODE.get(mode_key)
        if not mode:
            raise ZTEConfigError("聚合模式只能是 manual、lacp-static 或 lacp-dynamic")
        lines = [f"interface smartgroup{trunk_id}"]
        description = _phrase(trunk.get("description") or "", "聚合描述")
        if description:
            lines.append(f" description {description}")
        link_type = str(trunk.get("port_link_type") or "access").lower()
        if link_type == "trunk":
            lines.append(" switchport mode trunk")
            vlans = trunk.get("trunk_vlans") or []
            if vlans:
                numbers = [_integer(item, "聚合VLAN", 1, 4094) for item in vlans]
                lines.append(" switchport trunk vlan " + ",".join(str(item) for item in numbers))
        else:
            lines.append(" switchport mode access")
            if trunk.get("native_vlan"):
                lines.append(
                    " switchport access vlan "
                    + str(_integer(trunk["native_vlan"], "聚合Access VLAN", 1, 4094))
                )
        lines.append(" exit")
        for member in trunk.get("member_ports") or []:
            if not str(member).strip():
                continue
            lines.append(f"interface {normalize_interface(member, '聚合成员')}")
            lines.append(f" smartgroup {trunk_id} mode {mode}")
            lines.append(" exit")
        return lines


def generate_switch_config(basic=None, vlan=None, routing=None, security=None, interface=None):
    """把各页签的结构化配置拼成一份可预览的 ZXR10 脚本。没有内容时返回空串。"""
    basic_text, privileged = ZTEBasicGenerator.generate(basic or {})
    parts = [
        basic_text,
        ZTEVLANGenerator.generate(vlan or {}),
        ZTERoutingGenerator.generate(routing or {}),
        ZTESecurityGenerator.generate(security or {}),
        ZTEInterfaceGenerator.generate(interface or {}),
    ]
    body = "\n".join(part for part in parts if part)
    if not body and not privileged:
        return ""

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    header = "\n".join([
        "!",
        "! 中兴 ZXR10 交换机配置脚本",
        f"! 生成时间: {timestamp}",
        "! 命令风格: 经典 ZXROS（5200/5900/8900）。请在特权模式 ZXR10# 下粘贴。",
        "! 不适用于 5900E/5960/9900 的 ROSNG（请改用品牌「中兴 ROSNG」），也不适用于 C300/C600 OLT（请改用品牌「中兴 OLT」）。",
        "! 接口示例: gei_1/1、fei_1/1。三层口写作 interface vlan 10。",
        "! 管理口如果仍填写 VlanifN 或 Vlan-interfaceN，生成时会改成 vlan N。",
        "!",
    ])
    chunks = [header]
    if privileged:
        chunks.append("!\n! 下面的命令在特权模式执行，先于 configure terminal\n!")
        chunks.extend(privileged)
    chunks.append("configure terminal")
    if body:
        chunks.append(body)
    chunks.append("end")
    chunks.append("! 确认无误后执行 write 保存")
    return "\n".join(chunks) + "\n"
