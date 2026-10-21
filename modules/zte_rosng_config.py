#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
中兴 ZXR10 新一代 ROSNG 交换机配置生成器（5960 / 9900 这一类）。

可粘贴的命令只来自 ZXR10 5900E（V3.00.11）公开配置手册，5960/9900 与 5900E
同属 ROSNG。核对过的材料：

- Basic Configuration：configure terminal、end、hostname、banner incoming、
  ssh server enable [listen {22|49152-65535}]、ssh server disable、write
- Link Layer：switchvlan-configuration、vlan、interface、
  switchport mode {access|hybrid|trunk}、switchport access vlan、
  switchport trunk vlan、switchport trunk native vlan、
  switchport hybrid native vlan、switchport hybrid vlan <list> {tag|untag}、
  interface smartgroup、switch attribute enable、lacp、
  lacp mode {802.3ad|on}、smartgroup <id> mode {active|passive|on}
- Security：system-user、user-name、password、password encrypted、
  bind authentication-template、bind authorization-template、
  authentication-template、bind aaa-authentication-template、
  authorization-template、bind aaa-authorization-template、
  local-privilege-level、aaa-authentication-template、
  aaa-authentication-type local、aaa-authorization-template、
  aaa-authorization-type none、interface vlan<id>、ip address
- IPv4 Routing：ip route <dest> <mask> <nexthop> [distance]、
  ip route <dest> <mask> <interface> <nexthop>、
  ip route 0.0.0.0 0.0.0.0 <nexthop>

物理口示例是 gei-0/1/1/1。xlgeis- 出现在同一本基础手册的命令帮助里。
5960/9900 的万兆、25GE、40GE、100GE 口使用同一套架/槽/子槽/端口编号，
前缀写成 xgei、xxvgei、xlgei、cgei。命令关键字不变。

没有写成可执行命令的内容：VLAN 名称、接口描述、enable secret、
Telnet、NTP、SNMP、Syslog、DNS、OSPF、BGP、RIP、STP、ACL、
端口安全、LLDP、PoE、限速。这些只留注释。

用户输入只做单行拼接，拒绝换行和控制字符。生成过程不调用 shell。
"""

import re
import time

from modules.zte_config import ZTEConfigError


class ZTEROSNGConfigError(ZTEConfigError):
    """用户字段无法安全写入一条 ROSNG CLI。"""


_BREAK = re.compile(r"[\r\n\x00]")
_SINGLE = re.compile(r"^[A-Za-z0-9_./:@%+=,-]{1,128}$")
_IPV4 = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")
_ETH = re.compile(
    r"^(?:gei|xgei|xxvgei|xlgei|xlgeis|cgei)-\d+/\d+/\d+/\d+(?:/\d+)?$"
)
_CLASSIC_ETH = re.compile(r"(?i)^(?:fei|gei|xgei|xlgei|cgei)_\d")
_HEX = re.compile(r"^[0-9a-fA-F]{16,128}$")

_LACP_ACTIVE = {"lacp-static", "lacp-dynamic", "active", "802.3ad"}
_LACP_ON = {"manual", "on", "static"}
_LINK_TYPES = {"access", "trunk", "hybrid"}


def _raw(value):
    return "" if value is None else str(value)


def _single(value, field):
    text = _raw(value).strip()
    if not text or _BREAK.search(_raw(value)) or not _SINGLE.match(text):
        raise ZTEROSNGConfigError(f"{field} 含有空格、换行或无法写入命令的字符")
    return text


def _optional_single(value, field):
    if value is None or str(value).strip() == "":
        return ""
    return _single(value, field)


def _phrase(value, field):
    text = _raw(value).replace("\t", " ").strip()
    if _BREAK.search(_raw(value)):
        raise ZTEROSNGConfigError(f"{field} 不能包含换行")
    if any(char in text for char in "`;&|$<>\\"):
        raise ZTEROSNGConfigError(f"{field} 含有无法写入命令的字符")
    return text


def _integer(value, field, low, high):
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ZTEROSNGConfigError(f"{field} 不是整数")
    if number < low or number > high:
        raise ZTEROSNGConfigError(f"{field} 超出范围 {low}-{high}")
    return number


def _ipv4(value, field):
    text = _single(value, field)
    if not _IPV4.match(text):
        raise ZTEROSNGConfigError(f"{field} 不是 IPv4 地址")
    parts = [int(part) for part in text.split(".")]
    if any(part > 255 for part in parts):
        raise ZTEROSNGConfigError(f"{field} 不是 IPv4 地址")
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


def _prefix_to_mask(prefix):
    if prefix <= 0:
        return "0.0.0.0"
    value = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
    return ".".join(str((value >> shift) & 255) for shift in (24, 16, 8, 0))


def _mask(value, field):
    text = _single(value, field)
    if text.isdigit():
        return _prefix_to_mask(_integer(text, field, 0, 32))
    if not _IPV4.match(text):
        raise ZTEROSNGConfigError(f"{field} 不是子网掩码")
    parts = [int(part) for part in text.split(".")]
    if any(part > 255 for part in parts):
        raise ZTEROSNGConfigError(f"{field} 不是子网掩码")
    if text != "0.0.0.0" and _leading_ones(text) is None:
        raise ZTEROSNGConfigError(f"{field} 不是连续掩码")
    return text


def _hostname(value):
    text = _phrase(value, "主机名")
    if not text or not re.match(r"^[\w.-]{1,32}$", text) or " " in text:
        raise ZTEROSNGConfigError("主机名只能是 1-32 位字母、数字、中文、下划线、点或短横线")
    return text


def _username(value):
    text = _single(value, "用户名")
    if not re.match(r"^[A-Za-z][A-Za-z0-9_-]{0,31}$", text):
        raise ZTEROSNGConfigError("用户名须以字母开头，1-32 位，只能含字母、数字、下划线或短横线")
    return text


def _plain_password(value, field):
    text = _single(value, field)
    if len(text) < 3 or len(text) > 32:
        raise ZTEROSNGConfigError(f"{field} 长度须为 3-32，与 5900E 手册给出的明文范围一致")
    return text


def _encrypted_password(value, field):
    text = _single(value, field)
    if not _HEX.match(text):
        raise ZTEROSNGConfigError(f"{field} 须是手册示例那种十六进制密文，不能把明文标成密文")
    return text


def _is_ethernet(name):
    return bool(_ETH.match(name))


def _is_vlan(name):
    return bool(re.match(r"^vlan(\d+)$", name))


def normalize_interface(name, field="接口"):
    """把 Vlanif / vlan 10 收成 ROSNG 的 vlan10。物理口保持 gei-0/1/1/1 这种写法。"""
    text = _phrase(name, field)
    if not text:
        raise ZTEROSNGConfigError(f"{field} 为空")
    if _CLASSIC_ETH.match(text):
        raise ZTEROSNGConfigError(
            f"{field} 是经典 ZXROS 接口名。ROSNG 请填 gei-0/1/1/1 或 xgei-0/1/1/1"
        )
    compact = re.sub(r"\s+", "", text)
    matched = re.match(r"(?i)^(?:vlanif|vlan-interface|vlan-if|vlan)(\d{1,4})$", compact)
    if matched:
        vlan_id = int(matched.group(1))
        if vlan_id < 1 or vlan_id > 4094:
            raise ZTEROSNGConfigError(f"{field} 的 VLAN 超出 1-4094")
        return f"vlan{vlan_id}"
    smartgroup = re.match(r"(?i)^smartgroup(\d+)$", compact)
    if smartgroup:
        group_id = int(smartgroup.group(1))
        if group_id < 1 or group_id > 128:
            raise ZTEROSNGConfigError(f"{field} 的 smartgroup 编号超出 1-128")
        return f"smartgroup{group_id}"
    lowered = compact.lower()
    if _ETH.match(lowered):
        return lowered
    raise ZTEROSNGConfigError(
        f"{field} 不是 ROSNG 接口名。请填写 gei-0/1/1/1、xgei-0/1/1/1、smartgroup1 或 vlan10"
    )


def _ethernet(name, field):
    text = normalize_interface(name, field)
    if not _is_ethernet(text):
        raise ZTEROSNGConfigError(f"{field} 需要物理口，例如 gei-0/1/1/1 或 xgei-0/1/1/1")
    return text


def _vlan_id_of(name):
    matched = re.match(r"^vlan(\d+)$", name)
    return int(matched.group(1)) if matched else None


def _vlan_numbers(value, field):
    if value is None or value == "" or value == []:
        return []
    if isinstance(value, str):
        parts = [part for part in re.split(r"[\s,]+", value.strip()) if part]
        return [_integer(part, field, 1, 4094) for part in parts]
    if isinstance(value, int):
        return [_integer(value, field, 1, 4094)]
    return [_integer(item, field, 1, 4094) for item in value]


def _vlan_span_commands(prefix, numbers):
    """连续 VLAN 收成手册 running-config 里的 1-6。不连续的拆开，不写逗号。"""
    ordered = sorted(set(numbers))
    if not ordered:
        return []
    spans = []
    start = previous = ordered[0]
    for item in ordered[1:]:
        if item == previous + 1:
            previous = item
            continue
        spans.append((start, previous))
        start = previous = item
    spans.append((start, previous))
    commands = []
    for begin, end in spans:
        if begin == end:
            commands.append(f"{prefix} {begin}")
        else:
            commands.append(f"{prefix} {begin}-{end}")
    return commands


def _comment_lines(text, field):
    body = _raw(text).replace("\r\n", "\n").replace("\r", "\n").strip("\n")
    if not body:
        return []
    if "\x00" in body:
        raise ZTEROSNGConfigError(f"{field} 含有无法写入的字符")
    lines = []
    for line in body.split("\n"):
        if any(char in line for char in "`;&|$<>\\"):
            raise ZTEROSNGConfigError(f"{field} 含有无法写入命令的字符")
        lines.append("! " + line if line else "!")
    return lines


def _banner(text):
    body = _raw(text).replace("\r\n", "\n").replace("\r", "\n")
    if "\x00" in body:
        raise ZTEROSNGConfigError("Banner 含有无法写入的字符")
    body = body.strip("\n")
    if not body:
        return []
    for mark in ("#", "%", "^", "~", "@"):
        if mark not in body and not any(char in body for char in "`;&|$<>\\"):
            return [f"banner incoming {mark}", body, mark]
    raise ZTEROSNGConfigError("Banner 含有无法写入的字符，或同时包含 # % ^ ~ @")


def _section(title, lines):
    kept = [line for line in lines if line is not None and line != ""]
    if not kept:
        return ""
    return "!\n! " + title + "\n!\n" + "\n".join(kept)


def _shutdown(names):
    lines = []
    seen = []
    for name in names:
        if name in seen or not _is_ethernet(name):
            continue
        seen.append(name)
        lines.extend([f"interface {name}", " no shutdown", " exit"])
    return lines


class ZTEROSNGBasicGenerator:
    """主机名、本地用户、SSH、管理 VLAN 地址和默认路由。"""

    @staticmethod
    def generate(config):
        if not config:
            return ""
        lines = []

        hostname = config.get("hostname")
        if hostname:
            lines.append(f"hostname {_hostname(hostname)}")

        password = config.get("password") or {}
        if password.get("value"):
            _phrase(str(password.get("value")), "管理密码")
            lines.append(
                "! 管理密码未写入。5900E 手册的登录口令写在 system-user 的 password 下，"
                "没有核对到 enable secret"
            )

        user = config.get("user") or {}
        if user.get("username") or user.get("password"):
            lines.extend(ZTEROSNGBasicGenerator._user(user))

        if config.get("enable_ssh"):
            lines.extend(ZTEROSNGBasicGenerator._ssh(config))
        elif config.get("enable_ssh") is False:
            lines.append("ssh server disable")

        if config.get("enable_telnet"):
            lines.append("! Telnet 未生成命令。已核对的远程登录命令是 ssh server enable")

        banner = config.get("banner") or {}
        banner_text = banner.get("login") or banner.get("motd") or ""
        if banner.get("login") and banner.get("motd"):
            banner_text = banner["motd"].rstrip() + "\n" + banner["login"].lstrip()
        lines.extend(_banner(banner_text))

        mgmt = config.get("mgmt_interface") or {}
        if mgmt.get("ip_address"):
            lines.extend(ZTEROSNGBasicGenerator._mgmt(mgmt))

        lines.extend(ZTEROSNGBasicGenerator._unverified(config))
        return _section("基础配置", lines)

    @staticmethod
    def _user(user):
        username = _username(user.get("username"))
        level = _integer(user.get("level", 15), "权限级别", 0, 15)
        if user.get("encrypted"):
            secret = _encrypted_password(user.get("password"), "用户密码")
            password_line = f"  password encrypted {secret}"
        else:
            secret = _plain_password(user.get("password"), "用户密码")
            password_line = f"  password {secret}"
        return [
            "! 本地用户按 5900E 安全手册 6.4.1 书写。模板 1 和 AAA 模板 2001 与该示例相同",
            "! 若设备上 2001 已绑定 RADIUS，请换一个空闲 AAA 模板号后再粘贴",
            "system-user",
            f" user-name {username}",
            password_line,
            "  bind authentication-template 1",
            "  bind authorization-template 1",
            "  exit",
            " authentication-template 1",
            "  bind aaa-authentication-template 2001",
            "  exit",
            " authorization-template 1",
            "  bind aaa-authorization-template 2001",
            f"  local-privilege-level {level}",
            "  exit",
            " exit",
            "aaa-authentication-template 2001",
            " aaa-authentication-type local",
            " exit",
            "aaa-authorization-template 2001",
            " aaa-authorization-type none",
            " exit",
        ]

    @staticmethod
    def _ssh(config):
        lines = []
        port = config.get("ssh_port", 22)
        if port in (None, "", 22, "22"):
            lines.append("ssh server enable")
        else:
            number = _integer(port, "SSH端口", 1, 65535)
            if number == 22 or 49152 <= number <= 65535:
                lines.append(f"ssh server enable listen {number}")
            else:
                lines.append("ssh server enable")
                lines.append(
                    f"! SSH 端口 {number} 未写入。手册只允许 listen 22 或 49152-65535"
                )
        version = config.get("ssh_version")
        if version not in (None, "", 2, "2"):
            lines.append(
                f"! SSH 版本 {_integer(version, 'SSH版本', 1, 2)} 未写入。"
                "已核对的命令只有 ssh server enable"
            )
        timeout = config.get("ssh_timeout")
        if timeout not in (None, "", 60, "60"):
            lines.append(
                f"! SSH 超时 {_integer(timeout, 'SSH超时', 1, 86400)} 秒未写入，没有核对到对应命令"
            )
        tries = config.get("ssh_max_auth_tries")
        if tries not in (None, "", 5, "5"):
            lines.append(
                f"! SSH 最大认证次数 {_integer(tries, 'SSH认证次数', 1, 10)} 未写入，没有核对到对应命令"
            )
        return lines

    @staticmethod
    def _mgmt(mgmt):
        interface = normalize_interface(mgmt.get("interface") or "vlan1", "管理接口")
        ip_addr = _ipv4(mgmt["ip_address"], "管理IP")
        mask = _mask(mgmt.get("mask") or "255.255.255.0", "管理掩码")
        lines = []
        vlan_id = _vlan_id_of(interface)
        if vlan_id is None:
            lines.append(
                f"! 管理地址未写入 {interface}。已核对的三层地址写在 interface vlan<id> 下"
            )
        else:
            lines.append(f"interface vlan{vlan_id}")
            lines.append(f" ip address {ip_addr} {mask}")
            lines.append(" exit")
        gateway = mgmt.get("gateway")
        if gateway:
            nexthop = _ipv4(gateway, "网关")
            if vlan_id is None:
                lines.append(f"ip route 0.0.0.0 0.0.0.0 {nexthop}")
            else:
                lines.append(f"ip route 0.0.0.0 0.0.0.0 vlan{vlan_id} {nexthop}")
        return lines

    @staticmethod
    def _unverified(config):
        lines = []
        ntp = config.get("ntp") or {}
        servers = ntp.get("servers") or []
        if servers:
            zone = _phrase(str(ntp.get("timezone") or "UTC+8"), "时区")
            addresses = [_ipv4(server.get("ip"), "NTP服务器") for server in servers]
            lines.append(
                f"! NTP 未生成命令（时区 {zone}，服务器 {', '.join(addresses)}）。"
                "没有核对到 ROSNG 的 ntp server"
            )

        snmp = config.get("snmp") or {}
        if any(snmp.get(key) for key in ("version", "community_read", "community_write", "trap_host", "sys_location", "sys_contact")):
            version = _phrase(str(snmp.get("version") or "v2c"), "SNMP版本")
            detail = f"版本 {version}"
            if snmp.get("community_read"):
                _optional_single(snmp.get("community_read"), "SNMP只读团体字")
                detail += "，已填写只读团体字"
            if snmp.get("community_write"):
                _optional_single(snmp.get("community_write"), "SNMP读写团体字")
                detail += "，已填写读写团体字"
            location = _phrase(snmp.get("sys_location") or "", "SNMP位置")
            contact = _phrase(snmp.get("sys_contact") or "", "SNMP联系人")
            if location:
                detail += f"，位置 {location}"
            if contact:
                detail += f"，联系人 {contact}"
            if snmp.get("trap_host"):
                detail += f"，Trap {_ipv4(snmp['trap_host'], 'Trap主机')}"
            lines.append(f"! SNMP 未生成命令（{detail}）。没有把团体字写进脚本")

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
            lines.append(f"! 日志未生成命令（{detail}）。没有核对到可粘贴的 syslog 写法")

        dns = config.get("dns") or {}
        servers = [_ipv4(server, "DNS服务器") for server in (dns.get("servers") or [])]
        domain = _phrase(dns.get("domain") or "", "域名")
        if servers or domain:
            detail = " ".join(servers)
            if domain:
                detail = (detail + " " if detail else "") + f"域名 {domain}"
            lines.append(f"! DNS 未生成命令（{detail}）。没有核对到 ROSNG 的 ip name-server")
        return lines


class ZTEROSNGVLANGenerator:
    """VLAN、Access/Trunk/Hybrid、三层 VLAN 口。"""

    @staticmethod
    def generate(config):
        if not config:
            return ""
        lines = []
        names = {}
        ordered = []
        for vlan in config.get("vlans") or []:
            vlan_id = _integer(vlan.get("id"), "VLAN ID", 1, 4094)
            if vlan_id not in names:
                ordered.append(vlan_id)
                names[vlan_id] = ""
            name = _phrase(vlan.get("name") or "", "VLAN名称")
            if name:
                names[vlan_id] = name

        inner = []
        physical = []
        for iface in config.get("interfaces") or []:
            port_lines, port_name, used = ZTEROSNGVLANGenerator._port(iface)
            physical.append(port_name)
            for vlan_id in used:
                if vlan_id not in names:
                    ordered.append(vlan_id)
                    names[vlan_id] = ""
            inner.extend(port_lines)

        for vlanif in config.get("vlanifs") or []:
            vlan_id = _integer(vlanif.get("vlan_id"), "VLAN接口", 1, 4094)
            if vlan_id not in names:
                ordered.append(vlan_id)
                names[vlan_id] = ""

        vlan_blocks = []
        for vlan_id in ordered:
            if names[vlan_id]:
                vlan_blocks.append(
                    f"! VLAN {vlan_id} 名称 {names[vlan_id]} 只作说明。"
                    "show vlan 的名称是设备自动生成的，配置步骤里没有 name"
                )
            vlan_blocks.extend([f" vlan {vlan_id}", "  exit"])

        if vlan_blocks or inner:
            lines.extend(_shutdown(physical))
            lines.append("switchvlan-configuration")
            lines.extend(vlan_blocks)
            lines.extend(inner)
            lines.append(" exit")

        for vlanif in config.get("vlanifs") or []:
            vlan_id = _integer(vlanif.get("vlan_id"), "VLAN接口", 1, 4094)
            description = _phrase(vlanif.get("description") or "", "VLAN接口描述")
            if description:
                lines.append(f"! VLAN 接口 {vlan_id} 描述 {description} 未写入。手册示例没有 description")
            ip_addr = _ipv4(vlanif.get("ip_address") or vlanif.get("ip"), "VLAN接口IP")
            mask = _mask(vlanif.get("mask") or "255.255.255.0", "VLAN接口掩码")
            lines.append(f"interface vlan{vlan_id}")
            lines.append(f" ip address {ip_addr} {mask}")
            lines.append(" exit")

        stp = config.get("stp") or {}
        if stp:
            lines.extend(ZTEROSNGVLANGenerator._stp(stp))
        return _section("VLAN配置", lines)

    @staticmethod
    def _port(iface):
        name = _ethernet(iface.get("interface"), "二层接口")
        kind = str(iface.get("type") or "access").lower()
        if kind not in _LINK_TYPES:
            raise ZTEROSNGConfigError(f"不支持的端口类型 {kind}")
        lines = [f" interface {name}"]
        used = []
        if kind == "access":
            vlan_id = _integer(iface.get("vlan_id"), "Access VLAN", 1, 4094)
            used.append(vlan_id)
            lines.append("  switchport mode access")
            lines.append(f"  switchport access vlan {vlan_id}")
        elif kind == "trunk":
            lines.append("  switchport mode trunk")
            numbers = _vlan_numbers(iface.get("trunk_vlans") or [], "Trunk VLAN")
            used.extend(numbers)
            if numbers:
                lines.extend(
                    "  " + command for command in _vlan_span_commands("switchport trunk vlan", numbers)
                )
            else:
                lines.append("! 未填写允许 VLAN，没有写 switchport trunk vlan")
            if iface.get("pvid"):
                pvid = _integer(iface["pvid"], "PVID", 1, 4094)
                used.append(pvid)
                lines.append(f"  switchport trunk native vlan {pvid}")
        else:
            vlan_id = _integer(iface.get("vlan_id"), "Hybrid VLAN", 1, 4094)
            used.append(vlan_id)
            lines.append("  switchport mode hybrid")
            lines.append(f"  switchport hybrid native vlan {vlan_id}")
            lines.append(f"  switchport hybrid vlan {vlan_id} untag")
            lines.append("! 界面只填了一个 VLAN，按 untag 写入。手册另有 switchport hybrid vlan <id> tag")
        lines.append("  exit")
        return lines, name, used

    @staticmethod
    def _stp(stp):
        enabled = bool(stp.get("enable", True))
        mode = str(stp.get("mode") or "stp").lower()
        if mode not in ("stp", "rstp", "mstp"):
            raise ZTEROSNGConfigError("STP 模式只能是 stp、rstp 或 mstp")
        priority = _integer(stp.get("priority", 32768), "STP优先级", 0, 61440)
        if enabled and mode == "stp" and priority == 32768:
            return []
        state = "打开" if enabled else "关闭"
        return [
            f"! 生成树未生成命令（界面为 {state}，模式 {mode}，优先级 {priority}）。"
            "本切片没有核对 spanning-tree 的可粘贴参数"
        ]


class ZTEROSNGRoutingGenerator:
    """静态路由。OSPF、BGP、RIP 只留注释。"""

    @staticmethod
    def generate(config):
        if not config:
            return ""
        lines = []
        for route in config.get("static_routes") or []:
            lines.extend(ZTEROSNGRoutingGenerator._route(route))

        rip = config.get("rip") or {}
        if rip.get("networks"):
            version = _integer(rip.get("version", 2), "RIP版本", 1, 2)
            networks = [_phrase(str(item), "RIP网络") for item in rip.get("networks") or []]
            lines.append(
                f"! RIP 未生成命令（版本 {version}，网络 {', '.join(networks)}）。"
                "本切片只写已核对的 ip route"
            )

        ospf = config.get("ospf") or {}
        if ospf.get("networks") or ospf.get("router_id"):
            process = _integer(ospf.get("process_id", 1), "OSPF进程", 1, 65535)
            area = _phrase(str(ospf.get("area_id") or "0"), "OSPF区域") or "0"
            if not re.match(r"^[0-9.]+$", area):
                raise ZTEROSNGConfigError("OSPF 区域只能是数字或点分格式")
            lines.append(
                f"! OSPF 未生成命令（进程 {process}，区域 {area}）。本切片只写已核对的 ip route"
            )

        bgp = config.get("bgp") or {}
        if bgp.get("peers") or bgp.get("networks"):
            asn = _integer(bgp.get("as_number"), "BGP AS", 1, 4294967295)
            lines.append(f"! BGP 未生成命令（AS {asn}）。本切片只写已核对的 ip route")
        return _section("路由配置", lines)

    @staticmethod
    def _route(route):
        dest = _ipv4(route.get("dest_network") or route.get("dest"), "目的网络")
        mask = _mask(route.get("mask"), "路由掩码")
        nexthop = route.get("next_hop") or route.get("nexthop")
        interface = route.get("interface")
        nexthop_text = _ipv4(nexthop, "下一跳") if nexthop else ""
        interface_text = normalize_interface(interface, "路由出接口") if interface else ""
        distance = None
        if route.get("preference") is not None:
            distance = _integer(route["preference"], "路由优先级", 1, 255)
        lines = []
        if interface_text and nexthop_text:
            lines.append(f"ip route {dest} {mask} {interface_text} {nexthop_text}")
            if distance not in (None, 1):
                lines.append(
                    f"! 管理距离 {distance} 未写在带出接口的路由后面。"
                    "手册里带距离的例子是 ip route <网段> <掩码> <下一跳> <距离>"
                )
        elif nexthop_text:
            command = f"ip route {dest} {mask} {nexthop_text}"
            if distance not in (None, 1):
                command += f" {distance}"
            lines.append(command)
        else:
            lines.append(
                f"! 静态路由 {dest} {mask} 未写入。手册要求必须有下一跳，不能只写出接口"
            )
        return lines


class ZTEROSNGSecurityGenerator:
    """安全页签只校验并注释。不把经典 ZXROS 的 ACL 写进来。"""

    @staticmethod
    def generate(config):
        if not config:
            return ""
        lines = []
        for acl in config.get("acls") or []:
            number = _integer(acl.get("number"), "ACL号", 1, 39999)
            description = _phrase(acl.get("description") or "", "ACL描述")
            for rule in acl.get("rules") or []:
                action = _single(rule.get("action") or "permit", "ACL动作")
                if action not in ("permit", "deny"):
                    raise ZTEROSNGConfigError("ACL 动作只能是 permit 或 deny")
                _integer(rule.get("id", 5), "ACL规则号", 1, 65535)
            text = f"! ACL {number}"
            if description:
                text += f" {description}"
            text += " 未生成命令。本切片没有核对可粘贴的 ACL 规则"
            lines.append(text)

        for port in config.get("port_security") or []:
            if not port.get("enable", True):
                continue
            interface = _ethernet(port.get("interface"), "端口安全接口")
            maximum = _integer(port.get("max_mac", 1), "MAC数量", 1, 1024)
            action = _single(str(port.get("action") or "shutdown").lower(), "端口安全动作")
            if action not in ("protect", "restrict", "shutdown"):
                raise ZTEROSNGConfigError("端口安全违规动作只能是 protect、restrict 或 shutdown")
            lines.append(
                f"! 端口安全未写入（接口 {interface}，MAC 上限 {maximum}，动作 {action}）"
            )

        for rule in config.get("traffic_filters") or []:
            interface = _ethernet(rule.get("interface"), "ACL应用接口")
            number = _integer(rule.get("acl_number"), "ACL号", 1, 39999)
            direction = _phrase(str(rule.get("direction") or "in"), "ACL方向").lower()
            if direction not in ("inbound", "outbound", "in", "out"):
                raise ZTEROSNGConfigError("ACL 方向只能是 inbound 或 outbound")
            lines.append(f"! 接口 {interface} {direction} 引用 ACL {number} 未写成命令")

        dhcp = config.get("dhcp_snooping") or {}
        if dhcp.get("enable"):
            detail = "已在界面打开"
            if dhcp.get("vlan"):
                detail += f"，VLAN {_integer(dhcp['vlan'], 'DHCP Snooping VLAN', 1, 4094)}"
            ports = []
            for port in dhcp.get("trusted_ports") or []:
                if str(port).strip():
                    ports.append(_ethernet(port, "DHCP信任端口"))
            if ports:
                detail += "，信任口 " + ", ".join(ports)
            lines.append(f"! DHCP Snooping 未生成命令（{detail}）")

        arp = config.get("arp_inspection") or {}
        arp_vlans = [_integer(vlan, "ARP VLAN", 1, 4094) for vlan in (arp.get("vlans") or [])]
        arp_ports = []
        for port in arp.get("trusted_ports") or []:
            if str(port).strip():
                arp_ports.append(_ethernet(port, "ARP信任端口"))
        if arp_vlans or arp_ports:
            detail = ""
            if arp_vlans:
                detail += "VLAN " + ", ".join(str(item) for item in arp_vlans)
            if arp_ports:
                detail += ("，" if detail else "") + "信任口 " + ", ".join(arp_ports)
            lines.append(f"! ARP 检测未生成命令（{detail}）")

        for storm in config.get("storm_controls") or []:
            interface = _ethernet(storm.get("interface"), "风暴抑制接口")
            detail = interface
            if storm.get("broadcast") is not None:
                detail += f" 广播 {_integer(storm['broadcast'], '广播pps', 0, 100000000)}"
            if storm.get("multicast") is not None:
                detail += f" 组播 {_integer(storm['multicast'], '组播pps', 0, 100000000)}"
            lines.append(f"! 风暴抑制未生成命令（{detail}）")

        anti = config.get("anti_attack") or {}
        if anti.get("enable"):
            raw_type = _phrase(str(anti.get("type") or "all"), "防攻击类型")
            lines.append(f"! 防攻击选项 {raw_type} 未生成命令")
        return _section("安全配置", lines)


class ZTEROSNGInterfaceGenerator:
    """Smartgroup。其余接口页签只在偏离界面默认值时留注释。"""

    @staticmethod
    def generate(config):
        if not config:
            return ""
        lines = []
        for trunk in config.get("eth_trunks") or []:
            lines.extend(ZTEROSNGInterfaceGenerator._smartgroup(trunk))
        lines.extend(ZTEROSNGInterfaceGenerator._unverified(config))
        return _section("接口配置", lines)

    @staticmethod
    def _smartgroup(trunk):
        trunk_id = _integer(trunk.get("trunk_id"), "聚合组", 1, 128)
        mode_key = str(trunk.get("mode") or "lacp-static").lower()
        if mode_key in _LACP_ON:
            lacp_mode = "on"
            member_mode = "on"
        elif mode_key == "passive":
            lacp_mode = "802.3ad"
            member_mode = "passive"
        elif mode_key in _LACP_ACTIVE:
            lacp_mode = "802.3ad"
            member_mode = "active"
        else:
            raise ZTEROSNGConfigError("聚合模式只能是 manual、lacp-static 或 lacp-dynamic")

        members = []
        for member in trunk.get("member_ports") or []:
            if not str(member).strip():
                continue
            members.append(_ethernet(member, "聚合成员"))
        if len(members) > 8:
            raise ZTEROSNGConfigError("5900E 手册写明每个 smartgroup 最多 8 个成员口")

        lines = [f"interface smartgroup{trunk_id}", " switch attribute enable", " exit"]
        description = _phrase(trunk.get("description") or "", "聚合描述")
        if description:
            lines.append(f"! 描述 {description} 未写入。聚合示例没有 description 子命令")
        if mode_key in ("lacp-static", "lacp-dynamic"):
            lines.append(
                f"! 界面模式 {mode_key} 按手册的 802.3ad 示例写成成员 {member_mode}。"
                "手册没有 lacp-static / lacp-dynamic 这两个关键字；对端要 passive 时把成员改成 "
                f"smartgroup {trunk_id} mode passive"
            )
        lines.append("lacp")
        lines.append(f" interface smartgroup{trunk_id}")
        lines.append(f"  lacp mode {lacp_mode}")
        lines.append("  exit")
        for member in members:
            lines.append(f" interface {member}")
            lines.append(f"  smartgroup {trunk_id} mode {member_mode}")
            lines.append("  exit")
        lines.append(" exit")
        lines.extend(_shutdown(members))

        link_type = str(trunk.get("port_link_type") or "access").lower()
        if link_type not in _LINK_TYPES:
            raise ZTEROSNGConfigError(f"不支持的聚合端口类型 {link_type}")
        lines.append("! 聚合口 VLAN 使用和物理口相同的 switchport。手册的 switchport 示例写在 gei 上")
        lines.append("switchvlan-configuration")
        lines.append(f" interface smartgroup{trunk_id}")
        if link_type == "trunk":
            lines.append("  switchport mode trunk")
            numbers = _vlan_numbers(trunk.get("trunk_vlans") or [], "聚合VLAN")
            if numbers:
                lines.extend(
                    "  " + command for command in _vlan_span_commands("switchport trunk vlan", numbers)
                )
            else:
                lines.append("! 聚合口未填写允许 VLAN")
            if trunk.get("pvid") or (
                trunk.get("native_vlan") and str(trunk.get("port_link_type") or "").lower() == "trunk"
            ):
                native = trunk.get("pvid") if trunk.get("pvid") else trunk.get("native_vlan")
                lines.append(
                    "  switchport trunk native vlan "
                    + str(_integer(native, "聚合Native VLAN", 1, 4094))
                )
        elif link_type == "hybrid":
            vlan_id = _integer(trunk.get("native_vlan") or trunk.get("vlan_id"), "聚合Hybrid VLAN", 1, 4094)
            lines.append("  switchport mode hybrid")
            lines.append(f"  switchport hybrid native vlan {vlan_id}")
            lines.append(f"  switchport hybrid vlan {vlan_id} untag")
        elif trunk.get("native_vlan"):
            vlan_id = _integer(trunk["native_vlan"], "聚合Access VLAN", 1, 4094)
            lines.append("  switchport mode access")
            lines.append(f"  switchport access vlan {vlan_id}")
        else:
            lines.append("! 聚合口未填写 Access VLAN")
        lines.append("  exit")
        lines.append(" exit")
        return lines

    @staticmethod
    def _unverified(config):
        lines = []
        lldp = config.get("lldp") or {}
        if lldp.get("enable"):
            interval = _integer(lldp.get("interval", 30), "LLDP间隔", 1, 65535)
            hold = _integer(lldp.get("holdtime", 120), "LLDP保持时间", 1, 65535)
            mode = _phrase(str(lldp.get("mode") or "both"), "LLDP模式")
            if not (interval == 30 and hold == 120 and mode.lower() == "both"):
                lines.append(
                    f"! LLDP 未生成命令（模式 {mode}，间隔 {interval}，保持 {hold}）。"
                    "没有按界面秒数改写 lldp hellotime"
                )

        loop = config.get("loopback_detection") or {}
        if loop.get("enable"):
            action = _phrase(str(loop.get("action") or "block"), "环路检测动作")
            vlans = [str(_integer(item, "环路检测VLAN", 1, 4094)) for item in (loop.get("vlan_ids") or [])]
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
            lines.append("! PoE 未生成命令。没有核对到 power inline 的 ROSNG 写法")
            for item in poe_interfaces:
                interface = _ethernet(item.get("interface"), "PoE接口")
                mode = _single(item.get("mode") or "auto", "PoE模式")
                lines.append(f"! PoE 接口 {interface} 模式 {mode} 仅作说明")

        for limit in config.get("rate_limits") or []:
            interface = _ethernet(limit.get("interface"), "限速接口")
            detail = interface
            if limit.get("cir_in"):
                detail += f" 入 {_integer(limit['cir_in'], '入方向限速', 1, 100000000)}"
            if limit.get("cir_out"):
                detail += f" 出 {_integer(limit['cir_out'], '出方向限速', 1, 100000000)}"
            lines.append(f"! 限速未生成命令（{detail}）。没有核对到 ROSNG 的 rate-limit")
        return lines


def generate_rosng_config(basic=None, vlan=None, routing=None, security=None, interface=None):
    """把各页签的结构化配置拼成一份可预览的 ROSNG 脚本。没有内容时返回空串。"""
    parts = [
        ZTEROSNGBasicGenerator.generate(basic or {}),
        ZTEROSNGVLANGenerator.generate(vlan or {}),
        ZTEROSNGRoutingGenerator.generate(routing or {}),
        ZTEROSNGSecurityGenerator.generate(security or {}),
        ZTEROSNGInterfaceGenerator.generate(interface or {}),
    ]
    body = "\n".join(part for part in parts if part)
    if not body:
        return ""

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    header = "\n".join([
        "!",
        "! 中兴 ZXR10 ROSNG 交换机配置脚本",
        f"! 生成时间: {timestamp}",
        "! 命令风格: ROSNG（5960/9900）。请在特权模式 ZXR10# 下粘贴。",
        "! 命令依据: ZXR10 5900E V3.00.11 配置手册（Basic / Link Layer / Security / IPv4 Routing）。",
        "! 接口示例: gei-0/1/1/1、xgei-0/1/1/1。三层口写作 interface vlan10。",
        "! 管理口如果仍填写 VlanifN 或 vlan 10，生成时会改成 vlan10。",
        "! 不是经典 ZXROS，没有 gei_1/1。C300/C600 OLT 请改用品牌「中兴 OLT」。",
        "! 核对不到的语法只写在 ! 注释里，不会猜一条命令。",
        "! 生成结果只是文本，不会下发到设备。",
        "!",
    ])
    return "\n".join([
        header,
        "configure terminal",
        body,
        "end",
        "! 确认无误后在特权模式执行 write 保存。脚本本身不会保存，也不会登录设备。",
        "",
    ])
