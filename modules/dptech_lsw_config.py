#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
迪普 LSW 交换机配置生成器（LSW3600 / LSW5600 这一类 Conplat 交换机）。

可粘贴的命令只来自核对过的公开材料，不把 FW1000 的安全策略搬过来：

- 《DPtech LSW6600 Series Ethernet Switches Command Configuration Manual v3.0》
  conf-mode、ssh enable、telnet enable、line vty、vlan、port、
  interface vlan-if、ip address A.B.C.D/前缀、switchport、
  interface bond、bond mode dynamic、bond load-sharing、bond group、
  router rip、router ospf、dhcp snooping、rate-limit input、
  spanning-tree enable / mode stp|rstp|mst、arp inspection vlan ... untrust
- 迪普官方对「交换机静态聚合」的答复：bond mode static、
  bond load-sharing mode source-destination-mac、bond group
- LSW3600-24GT4GP-SI 的 Telnet 现场写法：telnet port、
  line vty 里的 authentication mode password / password，
  以及 local-user <name> password <明文> role super

不写成可执行命令的内容：
- FW1000 的 security-zone、address-object、service-object、security-policy
- BGP（LSW3600/5600/6600 的公开示例和彩页都没有 router bgp）
- 编号 ACL、端口安全、风暴抑制、LLDP、PoE、banner、SNMP、NTP
  （彩页有这些特性，但没有核对到可粘贴的参数）

sysname 是同一套 Conplat 上 FW/WAF 用来改系统名的命令。LSW6600 手册示例
保持出厂提示符 DPTECH，没有另写改名步骤，所以这里仍然生成 sysname，
让主机名页签有对应命令。

用户输入只做单行拼接，拒绝换行和控制字符。生成过程不调用 shell。
"""

import re
import time

from modules.dptech_config import DPTechConfigError


class DPTechLSWConfigError(DPTechConfigError):
    """用户字段无法安全写入一条 LSW CLI。"""


_BREAK = re.compile(r"[\r\n\x00]")
_SINGLE = re.compile(r"^[A-Za-z0-9_./:@%+=,-]{1,128}$")
_IFACE = re.compile(
    r"^(?:gige\d+_\d+|tengige\d+_\d+|meth\d+_\d+|bond\d+|vlan-if\d+)$"
)
_IPV4 = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")

_BOND_DYNAMIC = {"lacp-dynamic", "dynamic"}
_BOND_STATIC = {"manual", "static", "on"}
_STP_MODE = {"stp": "stp", "rstp": "rstp", "mstp": "mst", "mst": "mst"}


def _raw(value):
    return "" if value is None else str(value)


def _single(value, field):
    text = _raw(value).strip()
    if not text or _BREAK.search(_raw(value)) or not _SINGLE.match(text):
        raise DPTechLSWConfigError(f"{field} 含有空格、换行或无法写入命令的字符")
    return text


def _optional_single(value, field):
    if value is None or str(value).strip() == "":
        return ""
    return _single(value, field)


def _phrase(value, field):
    text = _raw(value).replace("\t", " ").strip()
    if _BREAK.search(_raw(value)):
        raise DPTechLSWConfigError(f"{field} 不能包含换行")
    if any(char in text for char in "`;&|$<>\\"):
        raise DPTechLSWConfigError(f"{field} 含有无法写入命令的字符")
    return text


def _integer(value, field, low, high):
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise DPTechLSWConfigError(f"{field} 不是整数")
    if number < low or number > high:
        raise DPTechLSWConfigError(f"{field} 超出范围 {low}-{high}")
    return number


def _ipv4(value, field):
    text = _single(value, field)
    if not _IPV4.match(text):
        raise DPTechLSWConfigError(f"{field} 不是 IPv4 地址")
    parts = [int(part) for part in text.split(".")]
    if any(part > 255 for part in parts):
        raise DPTechLSWConfigError(f"{field} 不是 IPv4 地址")
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
        raise DPTechLSWConfigError(f"{field} 不是子网掩码")
    parts = [int(part) for part in text.split(".")]
    if any(part > 255 for part in parts):
        raise DPTechLSWConfigError(f"{field} 不是子网掩码")
    if text == "0.0.0.0":
        return 0
    prefix = _leading_ones(text)
    if prefix is None:
        raise DPTechLSWConfigError(f"{field} 不是连续掩码")
    return prefix


def _invert_dotted(dotted):
    return ".".join(str(255 - int(part)) for part in dotted.split("."))


def _wildcard_to_prefix(wildcard, field):
    """OSPF 反掩码收成前缀长度。0.0.0.0 表示主机，前缀是 32。"""
    text = _single(wildcard, field)
    if text.isdigit():
        return _integer(text, field, 0, 32)
    if not _IPV4.match(text):
        raise DPTechLSWConfigError(f"{field} 不是反掩码")
    parts = [int(part) for part in text.split(".")]
    if any(part > 255 for part in parts):
        raise DPTechLSWConfigError(f"{field} 不是反掩码")
    if text == "0.0.0.0":
        return 32
    if text.split(".")[0] != "0":
        prefix = _leading_ones(text)
        if prefix is None:
            raise DPTechLSWConfigError(f"{field} 不是连续掩码")
        return prefix
    prefix = _leading_ones(_invert_dotted(text))
    if prefix is None:
        raise DPTechLSWConfigError(f"{field} 不是连续反掩码")
    return prefix


def _network_address(ip_addr, prefix):
    parts = [int(part) for part in ip_addr.split(".")]
    value = (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]
    if prefix <= 0:
        value = 0
    else:
        mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
        value &= mask
    return ".".join(str((value >> shift) & 255) for shift in (24, 16, 8, 0))


def _sysname(value):
    text = _phrase(value, "主机名")
    if not re.match(r"^[A-Za-z0-9._-]{1,20}$", text):
        raise DPTechLSWConfigError("主机名只能是 1-20 位字母、数字、点、下划线或短横线")
    return text


def _username(value):
    text = _single(value, "用户名")
    if not re.match(r"^[A-Za-z][A-Za-z0-9_-]{2,19}$", text):
        raise DPTechLSWConfigError("用户名须以字母开头，3-20 位，只能含字母、数字、下划线或短横线")
    return text


def normalize_interface(name, field="接口"):
    """把华为/H3C 的 Vlanif 写法改成 LSW 的 vlan-ifN。"""
    text = _phrase(name, field)
    if not text:
        raise DPTechLSWConfigError(f"{field} 为空")
    compact = re.sub(r"\s+", "", text)
    matched = re.match(r"(?i)^(?:vlanif|vlan-interface|vlan-if|vlan)(\d{1,4})$", compact)
    if matched:
        vlan_id = int(matched.group(1))
        if vlan_id < 1 or vlan_id > 4094:
            raise DPTechLSWConfigError(f"{field} 的 VLAN 超出 1-4094")
        return f"vlan-if{vlan_id}"
    lowered = compact.lower()
    if _IFACE.match(lowered):
        return lowered
    raise DPTechLSWConfigError(
        f"{field} 不是 LSW 接口名。请填写 gige0_1、tengige0_1、bond1 或 vlan-if 10"
    )


def _interface_command(name):
    vlan = re.match(r"vlan-if(\d+)$", name)
    if vlan:
        return f"interface vlan-if {vlan.group(1)}"
    bond = re.match(r"bond(\d+)$", name)
    if bond:
        return f"interface bond {bond.group(1)}"
    return f"interface {name}"


def _vlan_spec(numbers):
    ordered = sorted(set(numbers))
    if not ordered:
        return ""
    chunks = []
    start = previous = ordered[0]
    for item in ordered[1:]:
        if item == previous + 1:
            previous = item
            continue
        chunks.append(str(start) if start == previous else f"{start}-{previous}")
        start = previous = item
    chunks.append(str(start) if start == previous else f"{start}-{previous}")
    return ",".join(chunks)


def _comment_lines(text, field):
    body = _raw(text).replace("\r\n", "\n").replace("\r", "\n").strip("\n")
    if not body:
        return []
    if "\x00" in body:
        raise DPTechLSWConfigError(f"{field} 含有无法写入的字符")
    lines = []
    for line in body.split("\n"):
        if any(char in line for char in "`;&|$<>\\"):
            raise DPTechLSWConfigError(f"{field} 含有无法写入命令的字符")
        lines.append("! " + line if line else "!")
    return lines


def _section(title, lines):
    kept = [line for line in lines if line is not None and line != ""]
    if not kept:
        return ""
    return "!\n! " + title + "\n!\n" + "\n".join(kept)


def _route_command(dest, prefix, interface, nexthop):
    target = f"{dest}/{prefix}"
    if interface and nexthop:
        return f"ip route {target} {interface} {nexthop}"
    if nexthop:
        return f"ip route {target} {nexthop}"
    if interface:
        return f"ip route {target} {interface}"
    raise DPTechLSWConfigError("静态路由缺少下一跳或出接口")


class DPTechLSWBasicGenerator:
    """系统名、本地用户、SSH/Telnet、管理地址。"""

    @staticmethod
    def generate(config):
        if not config:
            return ""
        lines = []

        hostname = config.get("hostname")
        if hostname:
            lines.append(f"sysname {_sysname(hostname)}")

        password = config.get("password") or {}
        secret = ""
        if password.get("value"):
            if password.get("encrypted"):
                lines.append("! 管理密码按密文填写，没有核对到 LSW 的密文关键字，未写入")
            else:
                secret = _single(password["value"], "管理密码")

        user = config.get("user") or {}
        user_line = ""
        if user.get("username") and user.get("password"):
            username = _username(user["username"])
            if user.get("encrypted"):
                lines.append(
                    f"! 用户 {username} 的密文没有写入。"
                    "LSW3600 现场写法是 local-user <name> password <明文> role super"
                )
            else:
                user_secret = _single(user["password"], "用户密码")
                user_line = f"local-user {username} password {user_secret} role super"
                level = user.get("level")
                if level is not None and _integer(level, "权限级别", 0, 15) != 15:
                    lines.append(
                        f"! 权限级别 {_integer(level, '权限级别', 0, 15)} 未写入。"
                        "已核对的本地用户关键字是 role super"
                    )

        if config.get("enable_ssh"):
            lines.append("ssh enable")
            if config.get("ssh_port") not in (None, "", 22, "22"):
                port = _integer(config.get("ssh_port"), "SSH端口", 1, 65535)
                lines.append(
                    f"! SSH 端口 {port} 未写入。LSW 示例只有 ssh enable；telnet port 不能拿来改 SSH"
                )
            version = config.get("ssh_version")
            if version not in (None, "", 2, "2"):
                lines.append(
                    f"! SSH 版本 {_integer(version, 'SSH版本', 1, 2)} 未写入，已核对的只有 ssh enable"
                )
            timeout = config.get("ssh_timeout")
            if timeout not in (None, "", 60, "60"):
                lines.append(
                    f"! SSH 超时 {_integer(timeout, 'SSH超时', 1, 86400)} 秒未写入，没有核对到对应命令"
                )

        if config.get("enable_telnet"):
            lines.append("telnet enable")
            if config.get("telnet_port") not in (None, "", 23, "23"):
                lines.append(
                    f"telnet port {_integer(config.get('telnet_port'), 'Telnet端口', 1, 65535)}"
                )
            lines.append("line vty")
            if user_line:
                lines.append(" authentication mode username")
                lines.append(" exit")
                lines.append(user_line)
                user_line = ""
            elif secret:
                lines.append(" authentication mode password")
                lines.append(f" password {secret}")
                lines.append(" exit")
                secret = ""
            else:
                lines.append(" authentication mode username")
                lines.append(" exit")
                lines.append("! Telnet 已改为用户名认证。请补一条 local-user，出厂账号是 admin")

        if user_line:
            lines.append(user_line)
        if secret:
            lines.append(
                "! 管理密码未写入。password conf-mode 是 FW1000 命令。"
                "LSW 打开 Telnet 后，口令写在 line vty 的 password 下"
            )

        mgmt = config.get("mgmt_interface") or {}
        if mgmt.get("ip_address"):
            interface = normalize_interface(mgmt.get("interface") or "vlan-if1", "管理接口")
            ip_addr = _ipv4(mgmt["ip_address"], "管理IP")
            prefix = _mask_to_prefix(mgmt.get("mask") or "255.255.255.0", "管理掩码")
            lines.append(_interface_command(interface))
            lines.append(f" ip address {ip_addr}/{prefix}")
            if not interface.startswith("vlan-if"):
                lines.append("! LSW 示例把三层地址写在 vlan-if 上。物理口若仍是二层，请改到 vlan-if")
            lines.append(" exit")
            gateway = mgmt.get("gateway")
            if gateway:
                nexthop = _ipv4(gateway, "网关")
                lines.append(f"ip route 0.0.0.0/0 {interface} {nexthop}")

        banner = config.get("banner") or {}
        banner_text = banner.get("motd") or banner.get("login") or ""
        if banner.get("motd") and banner.get("login"):
            banner_text = banner["motd"].rstrip() + "\n" + banner["login"].lstrip()
        if str(banner_text).strip():
            lines.append("! Banner 未生成命令。LSW 配置手册没有 banner motd")
            lines.extend(_comment_lines(banner_text, "Banner"))

        ntp = config.get("ntp") or {}
        servers = ntp.get("servers") or []
        if servers:
            zone = _phrase(str(ntp.get("timezone") or "UTC+8"), "时区")
            addresses = [_ipv4(server.get("ip"), "NTP服务器") for server in servers]
            lines.append(
                f"! NTP 未生成命令（时区 {zone}，服务器 {', '.join(addresses)}）。"
                "LSW 配置手册没有 ntp server"
            )

        snmp = config.get("snmp") or {}
        if any(snmp.get(key) for key in ("version", "community_read", "community_write", "trap_host", "sys_location", "sys_contact")):
            version = _phrase(str(snmp.get("version") or "v2c"), "SNMP版本")
            read_community = _optional_single(snmp.get("community_read"), "SNMP只读团体字")
            write_community = _optional_single(snmp.get("community_write"), "SNMP读写团体字")
            location = _phrase(snmp.get("sys_location") or "", "SNMP位置")
            contact = _phrase(snmp.get("sys_contact") or "", "SNMP联系人")
            detail = f"版本 {version}"
            if read_community:
                detail += f" 只读 {read_community}"
            if write_community:
                detail += f" 读写 {write_community}"
            if location:
                detail += f" 位置 {location}"
            if contact:
                detail += f" 联系人 {contact}"
            if snmp.get("trap_host"):
                detail += f" Trap {_ipv4(snmp['trap_host'], 'Trap主机')}"
            lines.append(f"! SNMP 未生成命令（{detail}）。没有核对到 LSW 的 snmp-agent 写法，也不使用 FW1000 的那套")

        log = config.get("log") or {}
        host = log.get("host")
        level = _phrase(str(log.get("log_level") or ""), "日志级别")
        default_log = (not host) and level in ("", "informational") and log.get("info_center_enable", True)
        if log and not default_log:
            detail = "已打开信息中心" if log.get("info_center_enable") else "界面关闭了信息中心"
            if host:
                detail += f"，服务器 {_ipv4(host, '日志服务器')}"
            if level and level != "informational":
                detail += f"，级别 {level}"
            lines.append(
                f"! 日志未生成命令（{detail}）。没有使用 FW1000 的 logging security-policy"
            )

        dns = config.get("dns") or {}
        servers = [_ipv4(server, "DNS服务器") for server in (dns.get("servers") or [])]
        domain = _phrase(dns.get("domain") or "", "域名")
        if servers or domain:
            detail = " ".join(servers)
            if domain:
                detail = (detail + " " if detail else "") + f"域名 {domain}"
            lines.append(f"! DNS 未生成命令（{detail}）。LSW 配置手册没有 ip name-server")

        return _section("基础配置", lines)


class DPTechLSWVLANGenerator:
    """VLAN、Access/Trunk/Hybrid、vlan-if、生成树。"""

    @staticmethod
    def generate(config):
        if not config:
            return ""
        lines = []
        created = []
        for vlan in config.get("vlans") or []:
            vlan_id = _integer(vlan.get("id"), "VLAN ID", 1, 4094)
            if vlan_id in created:
                continue
            created.append(vlan_id)
            lines.append(f"vlan {vlan_id}")
            name = _phrase(vlan.get("name") or "", "VLAN名称")
            if name:
                lines.append(f"! 名称 {name} 只作说明。LSW 的 vlan 视图示例没有 name 子命令")
            lines.append(" exit")

        stp = config.get("stp") or {}
        stp_on = bool(stp) and bool(stp.get("enable", True))
        for iface in config.get("interfaces") or []:
            lines.extend(DPTechLSWVLANGenerator._port(iface, stp_on))

        for vlanif in config.get("vlanifs") or []:
            vlan_id = _integer(vlanif.get("vlan_id"), "VLAN接口", 1, 4094)
            if vlan_id not in created:
                lines.append(f"vlan {vlan_id}")
                lines.append(" exit")
                created.append(vlan_id)
            lines.append(_interface_command(f"vlan-if{vlan_id}"))
            description = _phrase(vlanif.get("description") or "", "VLAN接口描述")
            if description:
                lines.append(f"! 描述 {description} 未写入。LSW 示例没有 description 子命令")
            ip_addr = _ipv4(vlanif.get("ip_address") or vlanif.get("ip"), "VLAN接口IP")
            prefix = _mask_to_prefix(vlanif.get("mask") or "255.255.255.0", "VLAN接口掩码")
            lines.append(f" ip address {ip_addr}/{prefix}")
            lines.append(" exit")

        if stp:
            lines.extend(DPTechLSWVLANGenerator._stp(stp))
        return _section("VLAN配置", lines)

    @staticmethod
    def _port(iface, stp_on):
        name = normalize_interface(iface.get("interface"), "二层接口")
        kind = str(iface.get("type") or "access").lower()
        lines = [_interface_command(name)]
        if kind == "access":
            vlan_id = _integer(iface.get("vlan_id"), "Access VLAN", 1, 4094)
            lines.append(f" switchport access vlan {vlan_id}")
        elif kind == "trunk":
            lines.append(" switchport mode trunk")
            vlans = iface.get("trunk_vlans") or []
            if vlans:
                numbers = [_integer(item, "Trunk VLAN", 1, 4094) for item in vlans]
                lines.append(f" switchport trunk allowed vlan {_vlan_spec(numbers)}")
            else:
                lines.append("! 未填写允许 VLAN，请在本接口补 switchport trunk allowed vlan")
            if iface.get("pvid"):
                lines.append(
                    " switchport trunk native vlan "
                    + str(_integer(iface["pvid"], "PVID", 1, 4094))
                )
        elif kind == "hybrid":
            lines.append(" switchport mode hybrid")
            vlan_id = _integer(iface.get("vlan_id"), "Hybrid VLAN", 1, 4094)
            lines.append(f" switchport hybrid allowed vlan {vlan_id} untagged")
            lines.append(f" switchport hybrid native vlan {vlan_id}")
        else:
            raise DPTechLSWConfigError(f"不支持的端口类型 {kind}")
        if stp_on:
            lines.append(" spanning-tree enable")
        lines.append(" exit")
        return lines

    @staticmethod
    def _stp(stp):
        enabled = bool(stp.get("enable", True))
        mode_key = str(stp.get("mode") or "stp").lower()
        mode = _STP_MODE.get(mode_key)
        if not mode:
            raise DPTechLSWConfigError("STP 模式只能是 stp、rstp 或 mstp")
        priority = _integer(stp.get("priority", 32768), "STP优先级", 0, 61440)
        if not enabled:
            return [
                "! 生成树已在界面关闭。已核对的是 spanning-tree enable，没有写入关闭命令"
            ]
        lines = ["spanning-tree enable", f"spanning-tree mode {mode}"]
        if mode == "mst":
            if priority != 32768:
                lines.append(
                    f"! MSTP 优先级 {priority} 未写入。"
                    "手册按实例写 spanning-tree mst <id> bridge-priority，界面没有实例号"
                )
            lines.append("! 实例映射示例: spanning-tree mst configuration / instance 1 vlan 2")
        elif priority != 32768:
            lines.append(f"spanning-tree bridge-priority {priority}")
        return lines


class DPTechLSWRoutingGenerator:
    """静态路由、RIP、OSPF。BGP 只留注释。"""

    @staticmethod
    def generate(config):
        if not config:
            return ""
        lines = []
        static_routes = config.get("static_routes") or []
        rip = config.get("rip") or {}
        ospf = config.get("ospf") or {}
        bgp = config.get("bgp") or {}
        if static_routes or rip.get("networks") or ospf.get("networks") or ospf.get("router_id") or bgp.get("peers") or bgp.get("networks"):
            lines.append(
                "! LSW3600-24GT4GP-LI 彩页没有列出三层路由。下面的命令给支持静态/RIP/OSPF 的 LSW3600 与 LSW5600"
            )

        for route in static_routes:
            dest = _ipv4(route.get("dest_network") or route.get("dest"), "目的网络")
            prefix = _mask_to_prefix(route.get("mask"), "路由掩码")
            nexthop = route.get("next_hop") or route.get("nexthop")
            interface = route.get("interface")
            nexthop_text = _ipv4(nexthop, "下一跳") if nexthop else ""
            interface_text = normalize_interface(interface, "路由出接口") if interface else ""
            dest_text = _network_address(dest, prefix)
            lines.append(_route_command(dest_text, prefix, interface_text, nexthop_text))
            if route.get("preference") is not None:
                distance = _integer(route["preference"], "路由优先级", 1, 255)
                if distance != 60:
                    lines.append(
                        f"! 路由优先级 {distance} 未写入。LSW 的 ip route 示例没有管理距离"
                    )

        networks = rip.get("networks") or []
        if networks:
            version = _integer(rip.get("version", 2), "RIP版本", 1, 2)
            body = []
            notes = []
            if version != 2:
                notes.append(f"! RIP 版本 {version} 未写入。手册示例没有 version 关键字")
            for network in networks:
                token = _single(network, "RIP网络")
                if "/" not in token:
                    notes.append(
                        f"! RIP 网络 {token} 未写入。手册写法是 network A.B.C.D/前缀，例如 network {token}/24"
                    )
                    continue
                address, _, length = token.partition("/")
                ip_addr = _ipv4(address, "RIP网络")
                prefix = _integer(length, "RIP前缀", 0, 32)
                body.append(f" network {_network_address(ip_addr, prefix)}/{prefix}")
            if body:
                lines.append("router rip")
                lines.extend(notes)
                lines.extend(body)
                lines.append(" exit")
            else:
                lines.extend(notes)

        ospf_networks = ospf.get("networks") or []
        if ospf_networks or ospf.get("router_id"):
            process = _integer(ospf.get("process_id", 1), "OSPF进程", 1, 65535)
            lines.append(f"router ospf {process}")
            router_id = _optional_single(ospf.get("router_id"), "OSPF Router-ID")
            if router_id:
                _ipv4(router_id, "OSPF Router-ID")
                lines.append(f"! router-id {router_id} 未写入。手册示例只有 network A.B.C.D/前缀 area")
            area = _phrase(str(ospf.get("area_id") or "0"), "OSPF区域") or "0"
            if not re.match(r"^[0-9.]+$", area):
                raise DPTechLSWConfigError("OSPF 区域只能是数字或点分格式")
            for network in ospf_networks:
                address = _ipv4(network.get("address") or network.get("network"), "OSPF网络")
                wildcard = network.get("mask") or network.get("wildcard") or "0.0.0.255"
                prefix = _wildcard_to_prefix(wildcard, "OSPF反掩码")
                lines.append(
                    f" network {_network_address(address, prefix)}/{prefix} area {area}"
                )
            lines.append(" exit")

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
            lines.append(
                f"! BGP {detail} 未生成命令。LSW 公开示例没有 router bgp，不能写成防火墙或别家的 BGP 语法"
            )

        return _section("路由配置", lines)


class DPTechLSWSecurityGenerator:
    """DHCP Snooping 使用手册命令。包过滤不生成 FW1000 安全策略。"""

    @staticmethod
    def generate(config):
        if not config:
            return ""
        lines = []
        for acl in config.get("acls") or []:
            lines.extend(DPTechLSWSecurityGenerator._acl(acl))

        for port in config.get("port_security") or []:
            if not port.get("enable", True):
                continue
            interface = normalize_interface(port.get("interface"), "端口安全接口")
            maximum = _integer(port.get("max_mac", 1), "MAC数量", 1, 1024)
            action = _single(str(port.get("action") or "shutdown").lower(), "端口安全动作")
            if action not in ("protect", "restrict", "shutdown"):
                raise DPTechLSWConfigError("端口安全违规动作只能是 protect、restrict 或 shutdown")
            lines.append(
                f"! 端口安全未写入（接口 {interface}，MAC 上限 {maximum}，动作 {action}）。"
                "彩页有端口安全，配置手册没有 switchport port-security"
            )

        for rule in config.get("traffic_filters") or []:
            interface = normalize_interface(rule.get("interface"), "ACL应用接口")
            number = _integer(rule.get("acl_number"), "ACL号", 1, 39999)
            direction = _phrase(str(rule.get("direction") or "in"), "ACL方向").lower()
            if direction not in ("inbound", "outbound", "in", "out"):
                raise DPTechLSWConfigError("ACL 方向只能是 inbound 或 outbound")
            lines.append(
                f"! 接口 {interface} {direction} 引用 ACL {number} 未写成命令。"
                "LSW 不使用 FW1000 的 security-policy，也没有已核对的 ip access-group"
            )

        dhcp = config.get("dhcp_snooping") or {}
        if dhcp.get("enable"):
            lines.append("dhcp snooping enable")
            if dhcp.get("vlan"):
                vlan_id = _integer(dhcp["vlan"], "DHCP Snooping VLAN", 1, 4094)
                lines.append(
                    f"! 界面 VLAN {vlan_id} 未写入。已核对的是全局 dhcp snooping enable，不是按 VLAN 打开"
                )
            for port in dhcp.get("trusted_ports") or []:
                if not str(port).strip():
                    continue
                name = normalize_interface(port, "DHCP信任端口")
                lines.append(_interface_command(name))
                lines.append(" dhcp snooping trust")
                lines.append(" exit")

        arp = config.get("arp_inspection") or {}
        arp_vlans = []
        for vlan in arp.get("vlans") or []:
            arp_vlans.append(str(_integer(vlan, "ARP VLAN", 1, 4094)))
        arp_ports = []
        for port in arp.get("trusted_ports") or []:
            if str(port).strip():
                arp_ports.append(normalize_interface(port, "ARP信任端口"))
        if arp_vlans or arp_ports:
            lines.append(
                "! 动态 ARP 检测未按界面上的信任口生成。"
                "手册命令是 arp inspection vlan <id> untrust interface <接口>，信任口和不可信口相反"
            )
            if arp_vlans:
                lines.append("! 界面 VLAN " + ", ".join(arp_vlans))
            if arp_ports:
                lines.append("! 界面信任口 " + ", ".join(arp_ports))

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
                f"! 风暴抑制未生成命令（{detail}）。彩页有该特性，配置手册没有给出可粘贴的速率关键字"
            )

        anti = config.get("anti_attack") or {}
        if anti.get("enable"):
            raw_type = _phrase(str(anti.get("type") or "all"), "防攻击类型")
            lines.append(
                f"! 防攻击选项 {raw_type} 未生成命令。不要用 FW1000 的 arp source-suppression 代替交换机上的 ARP 检测"
            )

        return _section("安全配置", lines)

    @staticmethod
    def _acl(acl):
        number = _integer(acl.get("number"), "ACL号", 1, 39999)
        description = _phrase(acl.get("description") or "", "ACL描述")
        lines = [
            f"! ACL {number}"
            + (f" {description}" if description else "")
            + " 未生成。LSW 示例是 acl mode mac-ipv4 type icap，规则要带 physical-ports，"
            "界面没有这些字段，因此不写 security-policy"
        ]
        for rule in acl.get("rules") or []:
            action = _single(rule.get("action") or "permit", "ACL动作")
            if action not in ("permit", "deny"):
                raise DPTechLSWConfigError("ACL 动作只能是 permit 或 deny")
            _integer(rule.get("id", 5), "ACL规则号", 1, 65535)
            if str(acl.get("type") or "extended").lower() == "extended":
                protocol = _single(rule.get("protocol") or "ip", "ACL协议")
                if protocol not in ("ip", "tcp", "udp", "icmp"):
                    raise DPTechLSWConfigError("ACL 协议只能是 ip、tcp、udp 或 icmp")
        return lines


class DPTechLSWInterfaceGenerator:
    """bond 聚合。限速只写已核对的入方向。"""

    @staticmethod
    def generate(config):
        if not config:
            return ""
        lines = []
        for trunk in config.get("eth_trunks") or []:
            lines.extend(DPTechLSWInterfaceGenerator._bond(trunk))

        lldp = config.get("lldp") or {}
        if lldp.get("enable"):
            interval = _integer(lldp.get("interval", 30), "LLDP间隔", 1, 65535)
            hold = _integer(lldp.get("holdtime", 120), "LLDP保持时间", 1, 65535)
            mode = _phrase(str(lldp.get("mode") or "both"), "LLDP模式")
            if not (interval == 30 and hold == 120 and mode.lower() == "both"):
                lines.append(
                    f"! LLDP 未生成命令（模式 {mode}，间隔 {interval}，保持 {hold}）。"
                    "LSW 配置手册没有 lldp 关键字"
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
                + "。不要把它写成别家的 loopback-detect"
            )

        poe = config.get("poe") or {}
        poe_interfaces = poe.get("interfaces") or []
        power = poe.get("max_power")
        non_default_power = power not in (None, "", 74000, "74000")
        if poe_interfaces or non_default_power or poe.get("enable") is False:
            lines.append("! PoE 未生成命令。彩页支持 PoE+，配置手册没有 power inline 的可粘贴写法")
            for item in poe_interfaces:
                interface = normalize_interface(item.get("interface"), "PoE接口")
                mode = _single(item.get("mode") or "auto", "PoE模式")
                lines.append(f"! PoE 接口 {interface} 模式 {mode} 仅作说明")

        for limit in config.get("rate_limits") or []:
            lines.extend(DPTechLSWInterfaceGenerator._rate(limit))

        return _section("接口配置", lines)

    @staticmethod
    def _bond(trunk):
        trunk_id = _integer(trunk.get("trunk_id"), "聚合组", 1, 64)
        mode_key = str(trunk.get("mode") or "lacp-dynamic").lower()
        lines = [_interface_command(f"bond{trunk_id}")]
        description = _phrase(trunk.get("description") or "", "聚合描述")
        if description:
            lines.append(f"! 描述 {description} 未写入。show bond 能看到描述，配置手册没有 description 子命令")
        if mode_key in _BOND_DYNAMIC:
            lines.append(" bond mode dynamic")
            lines.append(" bond load-sharing mode source-destination-ip")
        elif mode_key in _BOND_STATIC:
            lines.append(" bond mode static")
            lines.append(" bond load-sharing mode source-destination-mac")
        else:
            lines.append(
                f"! 聚合模式 {mode_key} 未写入 bond mode。"
                "已核对的只有 dynamic（LACP）和 static（静态聚合）"
            )
        link_type = str(trunk.get("port_link_type") or "access").lower()
        if link_type == "trunk":
            lines.append(" switchport mode trunk")
            vlans = trunk.get("trunk_vlans") or []
            if vlans:
                numbers = [_integer(item, "聚合VLAN", 1, 4094) for item in vlans]
                lines.append(f" switchport trunk allowed vlan {_vlan_spec(numbers)}")
            else:
                lines.append("! 聚合口未填写允许 VLAN")
            if trunk.get("native_vlan") and str(trunk.get("port_link_type") or "").lower() == "trunk":
                lines.append(
                    " switchport trunk native vlan "
                    + str(_integer(trunk["native_vlan"], "聚合Native VLAN", 1, 4094))
                )
        else:
            if trunk.get("native_vlan"):
                lines.append(
                    " switchport access vlan "
                    + str(_integer(trunk["native_vlan"], "聚合Access VLAN", 1, 4094))
                )
        lines.append(" exit")
        for member in trunk.get("member_ports") or []:
            if not str(member).strip():
                continue
            member_name = normalize_interface(member, "聚合成员")
            lines.append(_interface_command(member_name))
            lines.append(f" bond group {trunk_id}")
            lines.append(" exit")
        return lines

    @staticmethod
    def _rate(limit):
        interface = normalize_interface(limit.get("interface"), "限速接口")
        inbound = limit.get("cir_in")
        outbound = limit.get("cir_out")
        lines = []
        if inbound:
            rate = _integer(inbound, "入方向限速", 1, 100000000)
            lines.append(_interface_command(interface))
            lines.append(f" rate-limit input {rate} burst-bucket 1024")
            lines.append("! burst-bucket 1024 的单位是 Kbits，取自手册里 10Mbit/s 示例，界面没有突发字段")
            lines.append(" exit")
        if outbound:
            rate = _integer(outbound, "出方向限速", 1, 100000000)
            lines.append(
                f"! 出方向限速 {rate} 未写入。手册只给出 rate-limit input <kbps> burst-bucket <kbits>"
            )
        if not inbound and not outbound:
            lines.append(f"! 接口 {interface} 没有填写限速值")
        return lines


def generate_lsw_config(basic=None, vlan=None, routing=None, security=None, interface=None):
    """把各页签的结构化配置拼成一份可预览的 LSW 交换机脚本。没有内容时返回空串。"""
    parts = [
        DPTechLSWBasicGenerator.generate(basic or {}),
        DPTechLSWVLANGenerator.generate(vlan or {}),
        DPTechLSWRoutingGenerator.generate(routing or {}),
        DPTechLSWSecurityGenerator.generate(security or {}),
        DPTechLSWInterfaceGenerator.generate(interface or {}),
    ]
    body = "\n".join(part for part in parts if part)
    if not body:
        return ""

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    header = "\n".join([
        "!",
        "! 迪普 LSW 交换机配置脚本",
        f"! 生成时间: {timestamp}",
        "! 命令风格: Conplat。适用于 LSW3600 / LSW5600 系列交换机。",
        "! 请在用户视图执行 conf-mode 后粘贴。粘贴结束后用 exit 回到用户视图。",
        "! 不是 FW1000 防火墙脚本：没有 security-zone，也没有 security-policy。",
        "! 不适用于 ADX 应用交付。",
        "! 接口示例: gige0_1、tengige0_1。三层 VLAN 口写作 interface vlan-if 10。",
        "! 管理口如果仍填写 VlanifN 或 Vlan-interfaceN，生成时会改成 vlan-if N。",
        "! 命令依据: LSW6600 命令配置手册 v3.0、迪普官方静态聚合示例、LSW3600 Telnet 现场写法。",
        "!",
    ])
    return "\n".join([
        header,
        "conf-mode",
        body,
        "exit",
        "! 确认无误后保存。重启时设备会询问 System configuration has been modified. Save? (Y/N)。",
        "! 配置视图里也可执行 write file。若当前版本不识别，用 Web 管理页保存。",
        "",
    ])
