#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
迪普 FW1000 防火墙配置生成器。

命令风格是 Conplat，和《DPtech WAF3000 系列命令参考手册 v5.0》里写明的视图一致，
FW1000 维护手册、现场配置也使用同一套写法：

- 用户视图执行 conf-mode 进入 [DPTECH]
- sysname、local-user、password conf-mode、ssh enable、ssh port
- banner motd、snmp-agent、ntp server、clock timezone GMT
- interface gige0_1 / interface vlan-if 10 / interface bond 1
- ip address 使用前缀长度，ip route、ip name-server
- security-zone、address-object、service-object、security-policy
- 保存是 write file

不覆盖，也不编造这些产品的命令：
- LSW3600 / LSW5600 等交换机（公开资料没有可核对的 CLI）
- ADX 应用交付、只支持 Web 的旧版本
- OSPF / BGP / RIP 的进程写法、生成树、LLDP、PoE、端口安全、DHCP Snooping

界面里的 VlanifN / Vlan-interfaceN 会写成 vlan-if N。
用户输入只做单行拼接，拒绝换行和控制字符。没有核对完整参数的功能只写注释。
"""

import re
import time


class DPTechConfigError(ValueError):
    """用户字段无法安全写入一条 CLI。"""


_BREAK = re.compile(r"[\r\n\x00]")
_SINGLE = re.compile(r"^[A-Za-z0-9_./:@%+=,-]{1,128}$")
_IFACE = re.compile(
    r"^(?:gige\d+_\d+|meth\d+_\d+|bond\d+|loopback\d+|ppp\d+|vlan-if\d+|tunnel_ssl\d+)$"
)
_IPV4 = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")
_BANNER_BAD = set(":/\\,")

_TIMEZONES = {
    "UTC+8": 8,
    "UTC+0": 0,
    "UTC-5": -5,
    "UTC-8": -8,
}
_SNMP_VERSION = {
    "v1": "1",
    "1": "1",
    "v2c": "2c",
    "2c": "2c",
    "v3": "3",
    "3": "3",
    "all": "all",
}
_BOND_DYNAMIC = {"lacp-dynamic", "dynamic"}


def _raw(value):
    return "" if value is None else str(value)


def _single(value, field):
    text = _raw(value).strip()
    if not text or _BREAK.search(_raw(value)) or not _SINGLE.match(text):
        raise DPTechConfigError(f"{field} 含有空格、换行或无法写入命令的字符")
    return text


def _optional_single(value, field):
    if value is None or str(value).strip() == "":
        return ""
    return _single(value, field)


def _phrase(value, field):
    text = _raw(value).replace("\t", " ").strip()
    if _BREAK.search(_raw(value)):
        raise DPTechConfigError(f"{field} 不能包含换行")
    if any(char in text for char in "`;&|$<>\\"):
        raise DPTechConfigError(f"{field} 含有无法写入命令的字符")
    return text


def _integer(value, field, low, high):
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise DPTechConfigError(f"{field} 不是整数")
    if number < low or number > high:
        raise DPTechConfigError(f"{field} 超出范围 {low}-{high}")
    return number


def _ipv4(value, field):
    text = _single(value, field)
    if not _IPV4.match(text):
        raise DPTechConfigError(f"{field} 不是 IPv4 地址")
    parts = [int(part) for part in text.split(".")]
    if any(part > 255 for part in parts):
        raise DPTechConfigError(f"{field} 不是 IPv4 地址")
    return text


def _leading_ones(dotted):
    bits = []
    for part in dotted.split("."):
        number = int(part)
        if number < 0 or number > 255:
            return None
        for shift in range(7, -1, -1):
            bits.append((number >> shift) & 1)
    if not bits[0]:
        return None
    seen_zero = False
    count = 0
    for bit in bits:
        if bit:
            if seen_zero:
                return None
            count += 1
        else:
            seen_zero = True
    return count


def _mask_to_prefix(mask, field):
    text = _single(mask, field)
    if text.isdigit():
        return _integer(text, field, 0, 32)
    if not _IPV4.match(text):
        raise DPTechConfigError(f"{field} 不是子网掩码")
    parts = [int(part) for part in text.split(".")]
    if any(part > 255 for part in parts):
        raise DPTechConfigError(f"{field} 不是子网掩码")
    if text == "0.0.0.0":
        return 0
    prefix = _leading_ones(text)
    if prefix is None:
        raise DPTechConfigError(f"{field} 不是连续掩码")
    return prefix


def _invert_dotted(dotted):
    return ".".join(str(255 - int(part)) for part in dotted.split("."))


def _acl_prefix(addr, wildcard, field):
    """华为式通配符或点分掩码都收成 A.B.C.D/前缀。any 返回空串。"""
    token = _optional_single(addr, field) if addr else ""
    if not token or token.lower() == "any":
        return ""
    ip_addr = _ipv4(token, field)
    extra = _optional_single(wildcard, field + "掩码") if wildcard else ""
    if not extra:
        return f"{ip_addr}/32"
    if extra.isdigit():
        return f"{ip_addr}/{_integer(extra, field + '前缀', 0, 32)}"
    if not _IPV4.match(extra):
        raise DPTechConfigError(f"{field} 掩码不是 IPv4")
    parts = [int(part) for part in extra.split(".")]
    if any(part > 255 for part in parts):
        raise DPTechConfigError(f"{field} 掩码不是 IPv4")
    if extra == "0.0.0.0":
        return f"{ip_addr}/32"
    if extra.split(".")[0] != "0":
        prefix = _leading_ones(extra)
        if prefix is None:
            raise DPTechConfigError(f"{field} 掩码不是连续的")
        return f"{ip_addr}/{prefix}"
    prefix = _leading_ones(_invert_dotted(extra))
    if prefix is None:
        raise DPTechConfigError(f"{field} 通配符不是连续的")
    return f"{ip_addr}/{prefix}"


def _sysname(value):
    text = _phrase(value, "主机名")
    if not re.match(r"^[A-Za-z0-9._-]{1,20}$", text):
        raise DPTechConfigError("主机名只能是 1-20 位字母、数字、点、下划线或短横线")
    return text


def _username(value):
    text = _single(value, "用户名")
    if not re.match(r"^[A-Za-z][A-Za-z0-9_-]{2,19}$", text):
        raise DPTechConfigError("用户名须以字母开头，3-20 位，只能含字母、数字、下划线或短横线")
    return text


def normalize_interface(name, field="接口"):
    """把华为/H3C 的 Vlanif 写法改成 FW1000 的 vlan-ifN。"""
    text = _phrase(name, field)
    if not text:
        raise DPTechConfigError(f"{field} 为空")
    compact = re.sub(r"\s+", "", text)
    matched = re.match(r"(?i)^(?:vlanif|vlan-interface|vlan-if|vlan)(\d{1,4})$", compact)
    if matched:
        vlan_id = int(matched.group(1))
        if vlan_id < 1 or vlan_id > 4094:
            raise DPTechConfigError(f"{field} 的 VLAN 超出 1-4094")
        return f"vlan-if{vlan_id}"
    lowered = compact.lower()
    if _IFACE.match(lowered):
        return lowered
    spaced = re.match(r"(?i)^bond(\d{1,4})$", lowered)
    if spaced and _IFACE.match(f"bond{int(spaced.group(1))}"):
        return f"bond{int(spaced.group(1))}"
    raise DPTechConfigError(
        f"{field} 不是 FW1000 接口名。请填写 gige0_1、meth0_0、bond1 或 vlan-if 10"
    )


def _interface_command(name):
    vlan = re.match(r"vlan-if(\d+)$", name)
    if vlan:
        return f"interface vlan-if {vlan.group(1)}"
    bond = re.match(r"bond(\d+)$", name)
    if bond:
        return f"interface bond {bond.group(1)}"
    loopback = re.match(r"loopback(\d+)$", name)
    if loopback:
        return f"interface loopback {loopback.group(1)}"
    return f"interface {name}"


def _banner(text):
    body = _raw(text).replace("\r\n", "\n").replace("\r", "\n").strip("\n")
    if not body:
        return ""
    if "\x00" in body or _BREAK.search(body.replace("\n", "")):
        raise DPTechConfigError("Banner 含有无法写入的字符")
    if any(char in body for char in _BANNER_BAD):
        raise DPTechConfigError("Banner 不能包含 : / \\ ,")
    for mark in ("#", "%", "^", "~", "@"):
        if mark not in body:
            return f"banner motd {mark}\n{body}\n{mark}"
    raise DPTechConfigError("Banner 同时包含 # % ^ ~ @，无法选择结束符")


def _section(title, lines):
    kept = [line for line in lines if line is not None and line != ""]
    if not kept:
        return ""
    return "!\n! " + title + "\n!\n" + "\n".join(kept)


def _remember(zone_ports, name):
    if name and name not in zone_ports:
        zone_ports.append(name)


class DPTechBasicGenerator:
    """系统名、管理员、管理口、SSH、NTP、SNMP、日志、DNS。"""

    @staticmethod
    def generate(config, zone_ports):
        if not config:
            return ""
        lines = []

        hostname = config.get("hostname")
        if hostname:
            lines.append(f"sysname {_sysname(hostname)}")

        password = config.get("password") or {}
        if password.get("value"):
            secret = _single(password["value"], "管理密码")
            if password.get("encrypted"):
                lines.append("! 进入配置视图的密码只核对到明文命令 password conf-mode，密文没有写入")
            else:
                lines.append(f"password conf-mode {secret}")

        user = config.get("user") or {}
        if user.get("username") and user.get("password"):
            username = _username(user["username"])
            secret = _single(user["password"], "用户密码")
            if user.get("encrypted"):
                lines.append(f"local-user {username}")
                lines.append(f" password encrypted-password {secret}")
                lines.append(" exit")
            else:
                lines.append(
                    "! 命令参考里的 password plain-text-password 会交互读密码。"
                    "这里用现场单行写法，避免后面的配置被当成密码"
                )
                lines.append(f"local-user {username} password plain-text-password {secret}")
            if user.get("level") is not None:
                level = _integer(user.get("level"), "权限级别", 0, 15)
                lines.append(
                    f"! 权限级别 {level} 未写入。FW1000 用 local-group 区分管理员，不是 privilege"
                )

        mgmt = config.get("mgmt_interface") or {}
        if mgmt.get("ip_address"):
            interface = normalize_interface(mgmt.get("interface") or "meth0_0", "管理接口")
            ip_addr = _ipv4(mgmt["ip_address"], "管理IP")
            prefix = _mask_to_prefix(mgmt.get("mask") or "255.255.255.0", "管理掩码")
            lines.append(_interface_command(interface))
            lines.append(f" ip address {ip_addr}/{prefix}")
            lines.append(" no shutdown")
            lines.append(" exit")
            _remember(zone_ports, interface)
            gateway = mgmt.get("gateway")
            if gateway:
                nexthop = _ipv4(gateway, "网关")
                lines.append(f"ip route 0.0.0.0/0 {interface} {nexthop}")

        if config.get("enable_ssh"):
            lines.append("ssh enable")
            if config.get("ssh_port") not in (None, "", 22, "22"):
                lines.append(f"ssh port {_integer(config.get('ssh_port'), 'SSH端口', 1, 65535)}")
            version = config.get("ssh_version")
            if version not in (None, "", 2, "2"):
                lines.append(
                    f"! SSH 版本 {_integer(version, 'SSH版本', 1, 2)} 未写入，已核对的只有 ssh enable 和 ssh port"
                )
            timeout = config.get("ssh_timeout")
            if timeout not in (None, "", 60, "60"):
                lines.append(
                    f"! SSH 超时 {_integer(timeout, 'SSH超时', 1, 86400)} 秒未写入，没有核对到对应命令"
                )

        if config.get("enable_telnet"):
            lines.append("! Telnet 未生成。命令参考没有单独的 telnet enable，运行配置里的 login-configure 参数未核对")

        banner = config.get("banner") or {}
        banner_text = banner.get("motd") or banner.get("login") or ""
        if banner.get("motd") and banner.get("login"):
            banner_text = banner["motd"].rstrip() + "\n" + banner["login"].lstrip()
            lines.append("! FW1000 只核对到 banner motd，登录前和登录后的文字写在同一条里")
        rendered = _banner(banner_text)
        if rendered:
            lines.append(rendered)

        ntp = config.get("ntp") or {}
        servers = ntp.get("servers") or []
        if servers:
            zone = ntp.get("timezone") or "UTC+8"
            offset = _TIMEZONES.get(zone)
            if offset is None:
                lines.append(f"! 时区 {_phrase(str(zone), '时区')} 未识别，未写 clock timezone")
            else:
                lines.append(f"clock timezone GMT {offset}")
            for server in servers:
                ip_addr = _ipv4(server.get("ip"), "NTP服务器")
                if server.get("prefer"):
                    lines.append(f"ntp server {ip_addr} prefer")
                else:
                    lines.append(f"ntp server {ip_addr}")

        snmp = config.get("snmp") or {}
        if any(snmp.get(key) for key in ("version", "community_read", "community_write", "trap_host", "sys_location", "sys_contact")):
            version = _SNMP_VERSION.get(str(snmp.get("version") or "v2c").lower())
            if not version:
                raise DPTechConfigError("SNMP 版本只能是 v1、v2c、v3 或 all")
            lines.append(f"snmp-agent version {version}")
            if version == "3":
                lines.append("! SNMPv3 还要 snmp-agent v3-user。表单没有认证和加密密码，未生成用户")
            read_community = _optional_single(snmp.get("community_read"), "SNMP只读团体字")
            write_community = _optional_single(snmp.get("community_write"), "SNMP读写团体字")
            if read_community:
                lines.append(f"snmp-agent community {read_community} ro")
            if write_community:
                lines.append(f"snmp-agent community {write_community} rw")
            location = _phrase(snmp.get("sys_location") or "", "SNMP位置")
            contact = _phrase(snmp.get("sys_contact") or "", "SNMP联系人")
            if location:
                lines.append(f"snmp-agent location {location}")
            if contact:
                lines.append(f"snmp-agent contact {contact}")
            if snmp.get("trap_enable") and snmp.get("trap_host"):
                host = _ipv4(snmp["trap_host"], "Trap主机")
                lines.append(f"snmp-agent trap target-host address {host} target-port 162")

        log = config.get("log") or {}
        if log.get("info_center_enable") or log.get("host"):
            lines.append("logging security-policy enable")
            if log.get("host"):
                host = _ipv4(log["host"], "日志服务器")
                lines.append(f"logging security-policy host {host} port 514")
            level = _phrase(str(log.get("log_level") or ""), "日志级别")
            if level and level != "informational":
                lines.append(f"! 日志级别 {level} 未写入。已核对的是 logging security-policy，没有级别关键字")

        dns = config.get("dns") or {}
        servers = [_ipv4(server, "DNS服务器") for server in (dns.get("servers") or [])]
        if servers:
            lines.append("ip name-server " + " ".join(servers))
        domain = _phrase(dns.get("domain") or "", "域名")
        if domain:
            lines.append(f"! 域名 {domain} 未写入。没有核对到与 ip domain-name 对应的 FW1000 命令")

        return _section("基础配置", lines)


class DPTechVLANGenerator:
    """VLAN、二层口、vlan-if。生成树只注释。"""

    @staticmethod
    def generate(config, zone_ports):
        if not config:
            return ""
        lines = []
        for vlan in config.get("vlans") or []:
            vlan_id = _integer(vlan.get("id"), "VLAN ID", 1, 4094)
            lines.append(f"vlan {vlan_id}")
            name = _phrase(vlan.get("name") or "", "VLAN名称")
            if name:
                lines.append(f"! 名称 {name} 只作说明。vlan 视图没有已核对的 name 子命令")
            lines.append(" exit")

        for iface in config.get("interfaces") or []:
            lines.extend(DPTechVLANGenerator._port(iface, zone_ports))

        created = { _integer(vlan.get("id"), "VLAN ID", 1, 4094) for vlan in (config.get("vlans") or []) }
        for vlanif in config.get("vlanifs") or []:
            vlan_id = _integer(vlanif.get("vlan_id"), "VLAN接口", 1, 4094)
            if vlan_id not in created:
                lines.append(f"vlan {vlan_id}")
                lines.append(" exit")
                created.add(vlan_id)
            name = f"vlan-if{vlan_id}"
            lines.append(_interface_command(name))
            description = _phrase(vlanif.get("description") or "", "VLAN接口描述")
            if description:
                lines.append(f" description {description}")
            ip_addr = _ipv4(vlanif.get("ip_address") or vlanif.get("ip"), "VLAN接口IP")
            prefix = _mask_to_prefix(vlanif.get("mask") or "255.255.255.0", "VLAN接口掩码")
            lines.append(f" ip address {ip_addr}/{prefix}")
            lines.append(" no shutdown")
            lines.append(" exit")
            _remember(zone_ports, name)

        stp = config.get("stp") or {}
        if stp:
            enabled = bool(stp.get("enable", True))
            mode = _phrase(str(stp.get("mode") or "stp"), "STP模式").lower()
            priority = _integer(stp.get("priority", 32768), "STP优先级", 0, 61440)
            changed = (not enabled) or mode != "stp" or priority != 32768
            if changed:
                state = "启用" if enabled else "关闭"
                lines.append(
                    f"! 生成树未写入命令（界面为{state} {mode}，优先级 {priority}）。"
                    "FW1000 这份生成器不覆盖 LSW 交换机的 spanning-tree"
                )

        return _section("VLAN配置", lines)

    @staticmethod
    def _port(iface, zone_ports):
        name = normalize_interface(iface.get("interface"), "二层接口")
        kind = str(iface.get("type") or "access").lower()
        lines = [_interface_command(name)]
        if kind == "access":
            vlan_id = _integer(iface.get("vlan_id"), "Access VLAN", 1, 4094)
            lines.append(" switchport mode access")
            lines.append(f" switchport access vlan {vlan_id}")
        elif kind == "trunk":
            lines.append(" switchport mode trunk")
            vlans = iface.get("trunk_vlans") or []
            if vlans:
                numbers = [_integer(item, "Trunk VLAN", 1, 4094) for item in vlans]
                lines.append(" switchport trunk allowed vlan " + ",".join(str(item) for item in numbers))
            else:
                lines.append("! 未填写允许 VLAN，请在本接口补 switchport trunk allowed vlan")
            if iface.get("pvid"):
                lines.append(
                    " switchport trunk native vlan "
                    + str(_integer(iface["pvid"], "PVID", 1, 4094))
                )
        elif kind == "hybrid":
            lines.append(" switchport mode hybrid")
            vlan_id = iface.get("vlan_id")
            vlan_text = str(_integer(vlan_id, "Hybrid VLAN", 1, 4094)) if vlan_id else ""
            lines.append(
                "! Hybrid 的 tag/untag 参数在命令参考标题里不完整，未生成 switchport hybrid allowed。"
                + (f"界面填写的 VLAN 是 {vlan_text}" if vlan_text else "界面未填写 VLAN")
            )
        else:
            raise DPTechConfigError(f"不支持的端口类型 {kind}")
        lines.append(" no shutdown")
        lines.append(" exit")
        _remember(zone_ports, name)
        return lines


class DPTechRoutingGenerator:
    """静态路由写成 ip route。OSPF、BGP、RIP 只保留注释。"""

    @staticmethod
    def generate(config, zone_ports):
        del zone_ports
        if not config:
            return ""
        lines = []
        for route in config.get("static_routes") or []:
            dest = _ipv4(route.get("dest_network") or route.get("dest"), "目的网络")
            prefix = _mask_to_prefix(route.get("mask"), "路由掩码")
            nexthop = route.get("next_hop") or route.get("nexthop")
            interface = route.get("interface")
            nexthop_text = _ipv4(nexthop, "下一跳") if nexthop else ""
            interface_text = normalize_interface(interface, "路由出接口") if interface else ""
            if interface_text and nexthop_text:
                lines.append(f"ip route {dest}/{prefix} {interface_text} {nexthop_text}")
            elif nexthop_text:
                lines.append(f"ip route {dest}/{prefix} {nexthop_text}")
            elif interface_text:
                lines.append(f"ip route {dest}/{prefix} {interface_text}")
                lines.append("! 这条静态路由没有下一跳，FW1000 示例通常还要带下一跳地址")
            else:
                raise DPTechConfigError("静态路由缺少下一跳或出接口")
            if route.get("preference") is not None:
                distance = _integer(route["preference"], "路由优先级", 1, 255)
                if distance != 60:
                    lines.append(f"! 路由优先级 {distance} 未写入。已核对的 ip route 示例没有管理距离参数")

        ospf = config.get("ospf") or {}
        if ospf.get("networks") or ospf.get("router_id"):
            process = _integer(ospf.get("process_id", 1), "OSPF进程", 1, 65535)
            router_id = _optional_single(ospf.get("router_id"), "OSPF Router-ID")
            area = _phrase(str(ospf.get("area_id") or "0"), "OSPF区域") or "0"
            if not re.match(r"^[0-9.]+$", area):
                raise DPTechConfigError("OSPF 区域只能是数字或点分格式")
            networks = []
            for network in ospf.get("networks") or []:
                address = _ipv4(network.get("address") or network.get("network"), "OSPF网络")
                wildcard = _single(network.get("mask") or network.get("wildcard") or "0.0.0.255", "OSPF反掩码")
                networks.append(f"{address} {wildcard}")
            detail = f"进程 {process}"
            if router_id:
                detail += f" router-id {router_id}"
            detail += f" 区域 {area}"
            if networks:
                detail += " 网络 " + ", ".join(networks)
            lines.append(f"! OSPF {detail} 未生成命令。FW1000 支持 OSPF，但没有核对到可粘贴的进程写法")

        bgp = config.get("bgp") or {}
        peers = bgp.get("peers") or []
        bgp_networks = bgp.get("networks") or []
        if peers or bgp_networks:
            asn = _integer(bgp.get("as_number"), "BGP AS", 1, 4294967295)
            peer_text = []
            for peer in peers:
                peer_ip = _ipv4(peer.get("ip"), "BGP邻居")
                remote_as = _integer(peer.get("as") or peer.get("remote_as"), "对端AS", 1, 4294967295)
                peer_text.append(f"{peer_ip} AS {remote_as}")
            announced = [_phrase(network, "BGP网络") for network in bgp_networks]
            detail = f"AS {asn}"
            if peer_text:
                detail += " 邻居 " + ", ".join(peer_text)
            if announced:
                detail += " 网络 " + ", ".join(announced)
            lines.append(f"! BGP {detail} 未生成命令。没有核对到 FW1000 的 router bgp 写法")

        rip = config.get("rip") or {}
        rip_networks = rip.get("networks") or []
        if rip_networks:
            version = _integer(rip.get("version", 2), "RIP版本", 1, 2)
            networks = [_single(network, "RIP网络") for network in rip_networks]
            lines.append(
                f"! RIP 版本 {version} 网络 {', '.join(networks)} 未生成命令。没有核对到 FW1000 的 router rip 写法"
            )

        return _section("路由配置", lines)


class DPTechSecurityGenerator:
    """包过滤用 address-object / service-object / security-policy。"""

    @staticmethod
    def generate(config, zone_ports):
        del zone_ports
        if not config:
            return ""
        lines = []
        arp_written = False

        for acl in config.get("acls") or []:
            lines.extend(DPTechSecurityGenerator._acl(acl))

        for port in config.get("port_security") or []:
            if not port.get("enable", True):
                continue
            interface = normalize_interface(port.get("interface"), "端口安全接口")
            maximum = _integer(port.get("max_mac", 1), "MAC数量", 1, 1024)
            action = _single(str(port.get("action") or "shutdown").lower(), "端口安全动作")
            if action not in ("protect", "restrict", "shutdown"):
                raise DPTechConfigError("端口安全违规动作只能是 protect、restrict 或 shutdown")
            lines.append(
                f"! 端口安全未写入（接口 {interface}，MAC 上限 {maximum}，动作 {action}）。"
                "FW1000 命令参考没有与 switchport port-security 对应的已核对命令"
            )

        for rule in config.get("traffic_filters") or []:
            interface = normalize_interface(rule.get("interface"), "ACL应用接口")
            number = _integer(rule.get("acl_number"), "ACL号", 1, 39999)
            direction = _phrase(str(rule.get("direction") or "in"), "ACL方向").lower()
            if direction not in ("inbound", "outbound", "in", "out"):
                raise DPTechConfigError("ACL 方向只能是 inbound 或 outbound")
            lines.append(
                f"! 接口 {interface} {direction} 引用 ACL {number} 未写成接口命令。"
                "FW1000 在安全域上用 security-policy，没有已核对的 ip access-group"
            )

        dhcp = config.get("dhcp_snooping") or {}
        if dhcp.get("enable"):
            vlan_text = ""
            if dhcp.get("vlan"):
                vlan_text = str(_integer(dhcp["vlan"], "DHCP Snooping VLAN", 1, 4094))
            ports = []
            for port in dhcp.get("trusted_ports") or []:
                if str(port).strip():
                    ports.append(normalize_interface(port, "DHCP信任端口"))
            lines.append(
                "! DHCP Snooping 未生成命令"
                + (f"，界面 VLAN {vlan_text}" if vlan_text else "")
                + (f"，信任端口 {', '.join(ports)}" if ports else "")
                + "。FW1000 这份生成器没有核对到对应 CLI"
            )

        arp = config.get("arp_inspection") or {}
        arp_vlans = []
        for vlan in arp.get("vlans") or []:
            arp_vlans.append(str(_integer(vlan, "ARP VLAN", 1, 4094)))
        arp_ports = []
        for port in arp.get("trusted_ports") or []:
            if str(port).strip():
                arp_ports.append(normalize_interface(port, "ARP信任端口"))
        if arp_vlans or arp_ports:
            lines.append("arp source-suppression enable")
            arp_written = True
            lines.append(
                "! 按 VLAN 的动态 ARP 检测未写入"
                + (f"，界面 VLAN {', '.join(arp_vlans)}" if arp_vlans else "")
                + (f"，信任端口 {', '.join(arp_ports)}" if arp_ports else "")
                + "。已生成的是全局 arp source-suppression enable"
            )

        for storm in config.get("storm_controls") or []:
            interface = normalize_interface(storm.get("interface"), "风暴抑制接口")
            broadcast = storm.get("broadcast")
            multicast = storm.get("multicast")
            detail = interface
            if broadcast is not None:
                detail += f" 广播 {_integer(broadcast, '广播pps', 0, 100000000)}"
            if multicast is not None:
                detail += f" 组播 {_integer(multicast, '组播pps', 0, 100000000)}"
            lines.append(
                f"! 风暴抑制未生成可执行命令（{detail}）。命令参考有 storm-control，但速率参数未核对"
            )

        anti = config.get("anti_attack") or {}
        if anti.get("enable"):
            raw_type = _phrase(str(anti.get("type") or "all"), "防攻击类型")
            kinds = [part.strip().lower() for part in raw_type.split(",") if part.strip()]
            if "arp" in kinds or "all" in kinds:
                if not arp_written:
                    lines.append("arp source-suppression enable")
                    arp_written = True
            lines.append(
                f"! 防攻击选项 {raw_type}：除 arp source-suppression enable 外，没有核对到可粘贴的命令"
            )

        return _section("安全配置", lines)

    @staticmethod
    def _acl(acl):
        number = _integer(acl.get("number"), "ACL号", 1, 39999)
        extended = str(acl.get("type") or "extended").lower() == "extended"
        lines = []
        description = _phrase(acl.get("description") or "", "ACL描述")
        if description:
            lines.append(f"! ACL {number} {description}")
        for rule in acl.get("rules") or []:
            lines.extend(DPTechSecurityGenerator._rule(number, rule, extended))
        if not acl.get("rules"):
            lines.append(f"! ACL {number} 没有规则，未生成 security-policy")
        return lines

    @staticmethod
    def _rule(number, rule, extended):
        rule_id = _integer(rule.get("id", 5), "ACL规则号", 1, 65535)
        action = _single(rule.get("action") or "permit", "ACL动作")
        if action not in ("permit", "deny"):
            raise DPTechConfigError("ACL 动作只能是 permit 或 deny")
        policy = f"pf{number}r{rule_id}"
        source = _acl_prefix(rule.get("source"), rule.get("source_wildcard"), "ACL源")
        lines = []
        if source:
            object_name = f"a{number}s{rule_id}"
            lines.append(f"address-object {object_name} {source}")
            lines.append(
                f"security-policy {policy} src-zone any dst-zone any src-address address-object {object_name}"
            )
            lines.append("! src-address 与命令参考中的 dst-address 使用同一句式。若设备不识别，删掉该行后在 Web 上绑定地址对象")
        destination = ""
        protocol = "ip"
        if extended:
            destination = _acl_prefix(rule.get("destination"), rule.get("destination_wildcard"), "ACL目的")
            protocol = _single(rule.get("protocol") or "ip", "ACL协议")
            if protocol not in ("ip", "tcp", "udp", "icmp"):
                raise DPTechConfigError("ACL 协议只能是 ip、tcp、udp 或 icmp")
            if destination:
                object_name = f"a{number}d{rule_id}"
                lines.append(f"address-object {object_name} {destination}")
                lines.append(
                    f"security-policy {policy} src-zone any dst-zone any dst-address address-object {object_name}"
                )
            port = _optional_single(rule.get("dest_port") or rule.get("port"), "ACL端口")
            if port:
                if protocol not in ("tcp", "udp"):
                    raise DPTechConfigError("只有 TCP/UDP 规则可以带端口")
                if not port.isdigit():
                    raise DPTechConfigError("ACL 端口必须是数字")
                port_number = _integer(port, "ACL端口", 0, 65535)
                service = f"s{number}p{rule_id}"
                lines.append(
                    f"service-object {service} protocol {protocol} src-port 0 to 65535 dst-port {port_number}"
                )
                lines.append(
                    f"security-policy {policy} src-zone any dst-zone any service service-object {service}"
                )
        lines.append(f"security-policy {policy} src-zone any dst-zone any action {action}")
        return lines


class DPTechInterfaceGenerator:
    """bond。LLDP、PoE、限速、环路检测只在用户改过默认值时注释。"""

    @staticmethod
    def generate(config, zone_ports):
        if not config:
            return ""
        lines = []
        for trunk in config.get("eth_trunks") or []:
            lines.extend(DPTechInterfaceGenerator._bond(trunk, zone_ports))

        lldp = config.get("lldp") or {}
        if lldp.get("enable"):
            interval = _integer(lldp.get("interval", 30), "LLDP间隔", 1, 65535)
            hold = _integer(lldp.get("holdtime", 120), "LLDP保持时间", 1, 65535)
            mode = _phrase(str(lldp.get("mode") or "both"), "LLDP模式")
            if not (interval == 30 and hold == 120 and mode.lower() == "both"):
                lines.append(
                    f"! LLDP 未生成命令（模式 {mode}，间隔 {interval}，保持 {hold}）。"
                    "FW1000 命令参考没有已核对的 lldp 关键字"
                )

        loop = config.get("loopback_detection") or {}
        if loop.get("enable"):
            action = _phrase(str(loop.get("action") or "block"), "环路检测动作")
            vlans = []
            for item in loop.get("vlan_ids") or []:
                vlans.append(str(_integer(item, "环路检测VLAN", 1, 4094)))
            lines.append(
                "! 环路检测未生成命令"
                + (f"，动作 {action}" if action else "")
                + (f"，VLAN {', '.join(vlans)}" if vlans else "")
            )

        poe = config.get("poe") or {}
        poe_interfaces = poe.get("interfaces") or []
        power = poe.get("max_power")
        non_default_power = power not in (None, "", 74000, "74000")
        if poe_interfaces or non_default_power or poe.get("enable") is False:
            lines.append("! PoE 未生成命令。FW1000 防火墙命令参考没有 power inline")
            for item in poe_interfaces:
                interface = normalize_interface(item.get("interface"), "PoE接口")
                mode = _single(item.get("mode") or "auto", "PoE模式")
                lines.append(f"! PoE 接口 {interface} 模式 {mode} 仅作说明")

        for limit in config.get("rate_limits") or []:
            interface = normalize_interface(limit.get("interface"), "限速接口")
            inbound = limit.get("cir_in")
            outbound = limit.get("cir_out")
            detail = interface
            if inbound:
                detail += f" 入 {_integer(inbound, '入方向限速', 1, 100000000)}"
            if outbound:
                detail += f" 出 {_integer(outbound, '出方向限速', 1, 100000000)}"
            lines.append(f"! 接口限速未生成命令（{detail}）。没有核对到可粘贴的 qos car / rate-limit 参数")

        return _section("接口配置", lines)

    @staticmethod
    def _bond(trunk, zone_ports):
        trunk_id = _integer(trunk.get("trunk_id"), "聚合组", 1, 64)
        mode_key = str(trunk.get("mode") or "lacp-dynamic").lower()
        bond_name = f"bond{trunk_id}"
        lines = [_interface_command(bond_name)]
        description = _phrase(trunk.get("description") or "", "聚合描述")
        if description:
            lines.append(f" description {description}")
        if mode_key in _BOND_DYNAMIC:
            lines.append(" bond mode dynamic")
        else:
            lines.append(
                f"! 聚合模式 {mode_key} 未写入 bond mode。已核对的关键字只有 dynamic，请在本视图执行 bond mode ?"
            )
        link_type = str(trunk.get("port_link_type") or "access").lower()
        if link_type == "trunk":
            lines.append(" switchport mode trunk")
            vlans = trunk.get("trunk_vlans") or []
            if vlans:
                numbers = [_integer(item, "聚合VLAN", 1, 4094) for item in vlans]
                lines.append(" switchport trunk allowed vlan " + ",".join(str(item) for item in numbers))
        else:
            lines.append(" switchport mode access")
            if trunk.get("native_vlan"):
                lines.append(
                    " switchport access vlan "
                    + str(_integer(trunk["native_vlan"], "聚合Access VLAN", 1, 4094))
                )
        lines.append(" no shutdown")
        lines.append(" exit")
        _remember(zone_ports, bond_name)
        for member in trunk.get("member_ports") or []:
            if not str(member).strip():
                continue
            member_name = normalize_interface(member, "聚合成员")
            lines.append(_interface_command(member_name))
            lines.append(f" bond group {trunk_id}")
            lines.append(" exit")
            _remember(zone_ports, member_name)
        return lines


def _security_zones(zone_ports):
    if not zone_ports:
        return ""
    lines = ["security-zone Trust"]
    for name in zone_ports:
        lines.append(f" interface {name}")
    lines.append(" exit")
    lines.append("! Trust、DMZ、Untrust 是预定义安全域，优先级分别是 85、50、5，不能修改")
    lines.append("! 上面的接口先放入 Trust。外网口请改到 Untrust，对外服务器口改到 DMZ")
    lines.append("! 没有加入安全域的接口不能转发")
    return _section("安全域", lines)


def generate_firewall_config(basic=None, vlan=None, routing=None, security=None, interface=None):
    """把各页签的结构化配置拼成一份可预览的 FW1000 脚本。没有内容时返回空串。"""
    zone_ports = []
    parts = [
        DPTechBasicGenerator.generate(basic or {}, zone_ports),
        DPTechVLANGenerator.generate(vlan or {}, zone_ports),
        DPTechRoutingGenerator.generate(routing or {}, zone_ports),
        DPTechSecurityGenerator.generate(security or {}, zone_ports),
        DPTechInterfaceGenerator.generate(interface or {}, zone_ports),
        _security_zones(zone_ports),
    ]
    body = "\n".join(part for part in parts if part)
    if not body:
        return ""

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    header = "\n".join([
        "!",
        "! 迪普 FW1000 防火墙配置脚本",
        f"! 生成时间: {timestamp}",
        "! 命令风格: Conplat。请在用户视图执行 conf-mode 后粘贴下面的配置。",
        "! 适用于 FW1000 系列。不适用于 LSW 交换机，也不适用于 ADX 应用交付。",
        "! 接口示例: gige0_1、meth0_0、bond1。三层 VLAN 口写作 interface vlan-if 10。",
        "! 管理口如果仍填写 VlanifN 或 Vlan-interfaceN，生成时会改成 vlan-if N。",
        "!",
    ])
    return "\n".join([
        header,
        "conf-mode",
        body,
        "end",
        "! 确认无误后重新进入配置视图，执行 write file 保存",
        "",
    ])
