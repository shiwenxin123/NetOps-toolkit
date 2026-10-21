#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
中兴 OLT 配置生成器（ZXA10 C300/C320 与 C600）。

可粘贴的命令只来自公开手册里能对上的写法。C300 和 C600 的接口名不一样，
脚本按用户填写的接口名选择其中一套，并在文件头写明假定的型号。

C300/C320 命令手册 SJ-20130520164529-010，配置手册 SJ-20130520164529-007：

- configure terminal、end、exit、hostname（1-32 字符）
- enable secret 0 <明文>。明文 3-16 字符。enable secret 5 只在加载配置文件时使用，
  正常运行时不能敲，所以密文不写进可粘贴命令
- vlan <id>、interface vlan <id>、interface vlan mng1、ip address <地址> <掩码>
- 上联口 gei_1/19/1、xgei_1/10/1、fei_1/19/1：switchport mode trunk|hybrid、
  switchport vlan <列表> tag、switchport default vlan <id>
- 上联口不能配 access。命令手册原文：An uplink port cannot be configured to access mode
- switchport vlan 的命令模式是二层 FE/GE/10GE，不写到 PON 口
- no shutdown 写在二层 FE/GE/10GE，也写在 gpon-onu（命令手册示例）
- PON 口 gpon-olt_1/5/1、epon-olt_1/14/1，ONU 接口 gpon-onu_1/5/1:1、epon-onu_1/4/1:1
- 注册示例（只作注释，界面没有类型和 SN）：
  interface gpon-olt_1/5/1 / onu 1 type ZTE-F622 sn ZTEG00000001
- SSH：命令手册 30.4 的标题是 ssh server enable。配置手册第 15 章示例是
  ssh server version 2、ssh server authentication mode local、
  ssh server authentication type pap
- 静态路由：配置手册 ip route <目的> <掩码> <下一跳>。
  SmartOLT 的 C300 开局说明把默认路由写成 ip route 0.0.0.0 0.0.0.0 <网关>

C600 维护说明和 C600 配置说明里能对上的差异：

- 上联 xgei-1/18/1、gei-1/1/1，PON gpon_olt-1/1/1，ONU gpon_onu-1/1/1:1
- 带外口 interface mgmt_eth，三层 VLAN 写作 interface vlan66（中间没有空格）
- 上联和 gpon_olt 缺省 shutdown，需要 no shutdown
- 注册示例同样是 onu <id> type <类型> sn <SN>，另有 loid。界面没有这些字段

不写成可执行命令：本地用户（C300 和 C600 的用户命令不一样）、
ONU 注册、service-port、T-CONT、聚合、OSPF、BGP、RIP、生成树、ACL、
NTP、SNMP、日志、DNS、LLDP、PoE、限速。这些只留注释。

用户输入只做单行拼接，拒绝换行和控制字符。生成过程不调用 shell。
"""

import re
import time

from modules.zte_config import ZTEConfigError


class ZTEOLTConfigError(ZTEConfigError):
    """用户字段无法安全写入一条 OLT CLI。"""


_BREAK = re.compile(r"[\r\n\x00]")
_SINGLE = re.compile(r"^[A-Za-z0-9_./:@%+=,-]{1,128}$")
_IPV4 = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")
_C300_ETH = re.compile(r"^(?:gei|xgei|fei)_\d+/\d+/\d+$")
_C300_PON = re.compile(r"^(?:gpon|epon)-olt_\d+/\d+/\d+$")
_C300_ONU = re.compile(r"^(?:gpon|epon)-onu_\d+/\d+/\d+:(\d+)$")
_C600_ETH = re.compile(r"^(?:gei|xgei)-\d+/\d+/\d+$")
_C600_PON = re.compile(r"^(?:gpon|epon)_olt-\d+/\d+/\d+$")
_C600_ONU = re.compile(r"^(?:gpon|epon)_onu-\d+/\d+/\d+:(\d+)$")
_ROSNG_ETH = re.compile(r"^(?:gei|xgei|xxvgei|xlgei|cgei)-\d+/\d+/\d+/\d+")
_CLASSIC_ETH = re.compile(r"^(?:fei|gei|xgei)_\d+/\d+$")
_LINK_TYPES = {"access", "trunk", "hybrid"}


def _raw(value):
    return "" if value is None else str(value)


def _single(value, field):
    text = _raw(value).strip()
    if not text or _BREAK.search(_raw(value)) or not _SINGLE.match(text):
        raise ZTEOLTConfigError(f"{field} 含有空格、换行或无法写入命令的字符")
    return text


def _optional_single(value, field):
    if value is None or str(value).strip() == "":
        return ""
    return _single(value, field)


def _phrase(value, field):
    text = _raw(value).replace("\t", " ").strip()
    if _BREAK.search(_raw(value)):
        raise ZTEOLTConfigError(f"{field} 不能包含换行")
    if any(char in text for char in "`;&|$<>\\"):
        raise ZTEOLTConfigError(f"{field} 含有无法写入命令的字符")
    return text


def _integer(value, field, low, high):
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ZTEOLTConfigError(f"{field} 不是整数")
    if number < low or number > high:
        raise ZTEOLTConfigError(f"{field} 超出范围 {low}-{high}")
    return number


def _ipv4(value, field):
    text = _single(value, field)
    if not _IPV4.match(text):
        raise ZTEOLTConfigError(f"{field} 不是 IPv4 地址")
    parts = [int(part) for part in text.split(".")]
    if any(part > 255 for part in parts):
        raise ZTEOLTConfigError(f"{field} 不是 IPv4 地址")
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
        raise ZTEOLTConfigError(f"{field} 不是子网掩码")
    parts = [int(part) for part in text.split(".")]
    if any(part > 255 for part in parts):
        raise ZTEOLTConfigError(f"{field} 不是子网掩码")
    if text != "0.0.0.0" and _leading_ones(text) is None:
        raise ZTEOLTConfigError(f"{field} 不是连续掩码")
    return text


def _hostname(value):
    text = _phrase(value, "主机名")
    if not text or not re.match(r"^[\w.-]{1,32}$", text) or " " in text:
        raise ZTEOLTConfigError("主机名只能是 1-32 位字母、数字、中文、下划线、点或短横线")
    return text


def _username(value):
    text = _single(value, "用户名")
    if not re.match(r"^[A-Za-z][A-Za-z0-9_-]{0,31}$", text):
        raise ZTEOLTConfigError("用户名须以字母开头，1-32 位，只能含字母、数字、下划线或短横线")
    return text


def _enable_secret(value):
    text = _single(value, "管理密码")
    if len(text) < 3 or len(text) > 16:
        raise ZTEOLTConfigError("管理密码长度须为 3-16，与 C300 命令手册 enable secret 的明文范围一致")
    if text.lower() == "level":
        raise ZTEOLTConfigError("管理密码不能是 level，这会和 enable secret level 撞车")
    return text


def _family_of(name):
    if name == "mgmt_eth":
        return "c600"
    if name == "vlan mng1":
        return "c300"
    if _C600_ETH.match(name) or _C600_PON.match(name) or _C600_ONU.match(name):
        return "c600"
    if _C300_ETH.match(name) or _C300_PON.match(name) or _C300_ONU.match(name):
        return "c300"
    return ""


def _check_onu_index(name):
    matched = _C300_ONU.match(name) or _C600_ONU.match(name)
    if not matched:
        return
    index = int(matched.group(1))
    if index < 1 or index > 256:
        raise ZTEOLTConfigError(f"ONU 编号 {index} 超出 1-256")


def normalize_interface(name, field="接口"):
    """收成 C300 或 C600 的接口名。两套写法不互相改写。"""
    text = _phrase(name, field)
    if not text:
        raise ZTEOLTConfigError(f"{field} 为空")
    compact = re.sub(r"\s+", "", text)
    lowered = compact.lower()
    if _ROSNG_ETH.match(lowered):
        raise ZTEOLTConfigError(
            f"{field} 是 ROSNG 接口名。OLT 的 C300 上联写 gei_1/19/1，C600 上联写 xgei-1/1/1"
        )
    if _CLASSIC_ETH.match(lowered):
        raise ZTEOLTConfigError(
            f"{field} 是经典 ZXROS 的两位接口名。OLT 需要架/槽/端口，例如 gei_1/19/1 或 xgei-1/1/1"
        )
    if lowered in ("mng1", "vlanmng1"):
        return "vlan mng1"
    if lowered in ("mgmt_eth", "mgmt-eth"):
        return "mgmt_eth"
    vlan = re.match(r"(?i)^(?:vlanif|vlan-interface|vlan-if|vlan)(\d{1,4})$", compact)
    if vlan:
        vlan_id = int(vlan.group(1))
        if vlan_id < 1 or vlan_id > 4094:
            raise ZTEOLTConfigError(f"{field} 的 VLAN 超出 1-4094")
        return f"vlan {vlan_id}"
    if _family_of(lowered):
        _check_onu_index(lowered)
        return lowered
    raise ZTEOLTConfigError(
        f"{field} 不是 OLT 接口名。C300 填 gei_1/19/1、gpon-olt_1/1/1 或 vlan mng1；"
        "C600 填 xgei-1/1/1、gpon_olt-1/1/1 或 mgmt_eth"
    )


def _is_ethernet(name):
    return bool(_C300_ETH.match(name) or _C600_ETH.match(name))


def _is_pon_olt(name):
    return bool(_C300_PON.match(name) or _C600_PON.match(name))


def _is_onu(name):
    return bool(_C300_ONU.match(name) or _C600_ONU.match(name))


def _is_l3(name):
    return name == "vlan mng1" or name == "mgmt_eth" or name.startswith("vlan ")


def _vlan_id_of(name):
    matched = re.match(r"^vlan (\d+)$", name)
    return int(matched.group(1)) if matched else None


def _l3_command(name, model):
    if name == "vlan mng1":
        return "interface vlan mng1"
    if name == "mgmt_eth":
        return "interface mgmt_eth"
    vlan_id = _vlan_id_of(name)
    if vlan_id is None:
        return f"interface {name}"
    if model == "c600":
        return f"interface vlan{vlan_id}"
    return f"interface vlan {vlan_id}"


def _vlan_numbers(value, field):
    if value is None or value == "" or value == []:
        return []
    if isinstance(value, str):
        parts = [part for part in re.split(r"[\s,]+", value.strip()) if part]
        return [_integer(part, field, 1, 4094) for part in parts]
    if isinstance(value, int):
        return [_integer(value, field, 1, 4094)]
    return [_integer(item, field, 1, 4094) for item in value]


def _vlan_spec(numbers):
    """收成命令手册示例里的 100,102-110。"""
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
        raise ZTEOLTConfigError(f"{field} 含有无法写入的字符")
    lines = []
    for line in body.split("\n"):
        if any(char in line for char in "`;&|$<>\\"):
            raise ZTEOLTConfigError(f"{field} 含有无法写入命令的字符")
        lines.append("! " + line if line else "!")
    return lines


def _section(title, lines):
    kept = [line for line in lines if line is not None and line != ""]
    if not kept:
        return ""
    return "!\n! " + title + "\n!\n" + "\n".join(kept)


def _iter_names(*sections):
    for section in sections:
        if not section:
            continue
        mgmt = section.get("mgmt_interface") or {}
        if mgmt.get("interface"):
            yield mgmt["interface"]
        for iface in section.get("interfaces") or []:
            if iface.get("interface"):
                yield iface["interface"]
        for route in section.get("static_routes") or []:
            if route.get("interface"):
                yield route["interface"]
        for trunk in section.get("eth_trunks") or []:
            for member in trunk.get("member_ports") or []:
                if str(member).strip():
                    yield member
        for item in section.get("port_security") or []:
            if item.get("interface"):
                yield item["interface"]
        for item in section.get("traffic_filters") or []:
            if item.get("interface"):
                yield item["interface"]
        dhcp = section.get("dhcp_snooping") or {}
        for port in dhcp.get("trusted_ports") or []:
            if str(port).strip():
                yield port
        arp = section.get("arp_inspection") or {}
        for port in arp.get("trusted_ports") or []:
            if str(port).strip():
                yield port
        for storm in section.get("storm_controls") or []:
            if storm.get("interface"):
                yield storm["interface"]
        for limit in section.get("rate_limits") or []:
            if limit.get("interface"):
                yield limit["interface"]
        poe = section.get("poe") or {}
        for item in poe.get("interfaces") or []:
            if item.get("interface"):
                yield item["interface"]


def _resolve_model(*sections):
    seen = {"c300": "", "c600": ""}
    for raw_name in _iter_names(*sections):
        name = normalize_interface(raw_name)
        family = _family_of(name)
        if family and not seen[family]:
            seen[family] = name
    if seen["c300"] and seen["c600"]:
        raise ZTEOLTConfigError(
            f"接口同时出现了 C300 写法（{seen['c300']}）和 C600 写法（{seen['c600']}）。"
            "一份脚本只能选一种。C300 用 gei_1/19/1 和 gpon-olt_1/1/1，"
            "C600 用 xgei-1/1/1 和 gpon_olt-1/1/1"
        )
    if seen["c600"]:
        return "c600"
    return "c300"


class ZTEOLTBasicGenerator:
    """主机名、enable 口令、SSH、管理地址。"""

    @staticmethod
    def generate(config, model):
        if not config:
            return ""
        lines = []
        hostname = config.get("hostname")
        if hostname:
            lines.append(f"hostname {_hostname(hostname)}")

        password = config.get("password") or {}
        if password.get("value"):
            if password.get("encrypted"):
                _phrase(str(password.get("value")), "管理密码")
                lines.append(
                    "! 管理密码按密文填写，未写入。C300 命令手册写明 enable secret 5 只在加载配置文件时使用，"
                    "系统正常运行时不能敲"
                )
            else:
                lines.append(f"enable secret 0 {_enable_secret(password['value'])}")

        user = config.get("user") or {}
        if user.get("username") or user.get("password"):
            lines.extend(ZTEOLTBasicGenerator._user(user))

        if config.get("enable_ssh"):
            lines.extend(ZTEOLTBasicGenerator._ssh(config))
        elif config.get("enable_ssh") is False:
            lines.append("! SSH 已在界面关闭。没有核对到可粘贴的关闭命令，因此不写 ssh server disable")

        if config.get("enable_telnet"):
            lines.append("! Telnet 未生成命令。已核对的远程登录命令是 ssh server")

        banner = config.get("banner") or {}
        banner_text = banner.get("login") or banner.get("motd") or ""
        if banner.get("login") and banner.get("motd"):
            banner_text = banner["motd"].rstrip() + "\n" + banner["login"].lstrip()
        if str(banner_text).strip():
            lines.append("! Banner 未生成命令。命令手册目录有 banner incoming，正文没有核对到结束符写法")
            lines.extend(_comment_lines(banner_text, "Banner"))

        mgmt = config.get("mgmt_interface") or {}
        if mgmt.get("ip_address"):
            lines.extend(ZTEOLTBasicGenerator._mgmt(mgmt, model))

        lines.extend(ZTEOLTBasicGenerator._unverified(config))
        return _section("基础配置", lines)

    @staticmethod
    def _user(user):
        username = _username(user.get("username"))
        if user.get("password"):
            _phrase(str(user.get("password")), "用户密码")
        level = _integer(user.get("level", 15), "权限级别", 0, 15)
        secret = "已填写口令" if user.get("password") else "未填写口令"
        if user.get("encrypted"):
            secret = "按密文填写"
        return [
            f"! 本地用户 {username}（权限 {level}，{secret}）未写入。"
            "C300 公开示例没有可粘贴的 username 行，C600 用 system-user，两套不一样"
        ]

    @staticmethod
    def _ssh(config):
        lines = [
            "ssh server enable",
            "ssh server authentication mode local",
            "ssh server authentication type pap",
        ]
        version = config.get("ssh_version", 2)
        if version in (None, "", 2, "2"):
            lines.insert(1, "ssh server version 2")
        else:
            lines.append(
                f"! SSH 版本 {_integer(version, 'SSH版本', 1, 2)} 未写入。"
                "配置手册第 15 章的示例是 ssh server version 2"
            )
        port = config.get("ssh_port", 22)
        if port not in (None, "", 22, "22"):
            lines.append(
                f"! SSH 端口 {_integer(port, 'SSH端口', 1, 65535)} 未写入。没有核对到改监听端口的命令"
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
    def _mgmt(mgmt, model):
        raw_name = mgmt.get("interface") or ("mgmt_eth" if model == "c600" else "vlan mng1")
        interface = normalize_interface(raw_name, "管理接口")
        if not _is_l3(interface):
            raise ZTEOLTConfigError(
                "管理地址要写在 vlan <id>、vlan mng1 或 mgmt_eth 上，不能写在上联口或 PON 口"
            )
        family = _family_of(interface)
        if family and family != model:
            raise ZTEOLTConfigError("管理口和其余接口不是同一套 C300/C600 写法")
        ip_addr = _ipv4(mgmt["ip_address"], "管理IP")
        mask = _mask(mgmt.get("mask") or "255.255.255.0", "管理掩码")
        lines = []
        vlan_id = _vlan_id_of(interface)
        if vlan_id == 1:
            lines.append("! VLAN 1 是缺省 VLAN。若设备提示已存在，删掉下面的 vlan 1")
        if vlan_id is not None:
            lines.extend([f"vlan {vlan_id}", "exit"])
        if interface == "vlan mng1":
            lines.append("! 带外口按 C300/C320 命令手册 1.14 写成 interface vlan mng1")
        if model == "c600" and vlan_id is not None:
            lines.append("! C600 维护说明的三层口没有空格，例如 interface vlan66")
        lines.extend([
            _l3_command(interface, model),
            f" ip address {ip_addr} {mask}",
            " exit",
        ])
        gateway = mgmt.get("gateway")
        if gateway:
            lines.append(f"ip route 0.0.0.0 0.0.0.0 {_ipv4(gateway, '网关')}")
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
                "没有把界面上的服务器写进未核对的 ntp 命令"
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
            lines.append(f"! 日志未生成命令（{detail}）")

        dns = config.get("dns") or {}
        servers = [_ipv4(server, "DNS服务器") for server in (dns.get("servers") or [])]
        domain = _phrase(dns.get("domain") or "", "域名")
        if servers or domain:
            detail = " ".join(servers)
            if domain:
                detail = (detail + " " if detail else "") + f"域名 {domain}"
            lines.append(f"! DNS 未生成命令（{detail}）")
        return lines


class ZTEOLTVLANGenerator:
    """创建 VLAN，并把上联口放进 VLAN。PON 口只留说明。"""

    @staticmethod
    def generate(config, model):
        if not config:
            return ""
        lines = []
        names = {}
        ordered = []

        def remember(vlan_id, name=""):
            if vlan_id not in names:
                ordered.append(vlan_id)
                names[vlan_id] = ""
            if name:
                names[vlan_id] = name

        for vlan in config.get("vlans") or []:
            vlan_id = _integer(vlan.get("id"), "VLAN ID", 1, 4094)
            remember(vlan_id, _phrase(vlan.get("name") or "", "VLAN名称"))

        prepared = []
        for iface in config.get("interfaces") or []:
            port_lines, used = ZTEOLTVLANGenerator._port(iface, model)
            prepared.append(port_lines)
            for vlan_id in used:
                remember(vlan_id)

        for vlanif in config.get("vlanifs") or []:
            remember(_integer(vlanif.get("vlan_id"), "VLAN接口", 1, 4094))

        for vlan_id in ordered:
            if names[vlan_id]:
                lines.append(
                    f"! VLAN {vlan_id} 名称 {names[vlan_id]} 只作说明。"
                    "全局 vlan 命令的示例没有 name 子命令，名称要进 vlan database"
                )
            if vlan_id == 1:
                lines.append("! VLAN 1 是缺省 VLAN。若设备提示已存在，删掉下面这一段")
            lines.extend([f"vlan {vlan_id}", "exit"])

        for port_lines in prepared:
            lines.extend(port_lines)

        for vlanif in config.get("vlanifs") or []:
            lines.extend(ZTEOLTVLANGenerator._vlanif(vlanif, model))

        stp = config.get("stp") or {}
        if stp:
            lines.extend(ZTEOLTVLANGenerator._stp(stp))
        return _section("VLAN配置", lines)

    @staticmethod
    def _port(iface, model):
        name = normalize_interface(iface.get("interface"), "二层接口")
        kind = str(iface.get("type") or "access").lower()
        if kind not in _LINK_TYPES:
            raise ZTEOLTConfigError(f"不支持的端口类型 {kind}")
        used = []
        lines = [f"interface {name}"]
        if _is_ethernet(name):
            lines.append(" no shutdown")
            lines.extend(ZTEOLTVLANGenerator._ethernet_vlan(iface, kind, used))
        elif _is_pon_olt(name):
            lines.extend(ZTEOLTVLANGenerator._pon(name, iface, kind, model, used))
        elif _is_onu(name):
            lines.extend(ZTEOLTVLANGenerator._onu_port(name, iface, kind, model, used))
        else:
            raise ZTEOLTConfigError(f"{name} 不能当作二层口。请填上联口或 PON 口")
        lines.append(" exit")
        return lines, used

    @staticmethod
    def _ethernet_vlan(iface, kind, used):
        lines = []
        if kind == "access":
            vlan_id = _integer(iface.get("vlan_id"), "Access VLAN", 1, 4094)
            used.append(vlan_id)
            lines.append(
                "! 上联口不能写成 switchport mode access。"
                "命令手册写明 uplink port cannot be configured to access mode"
            )
            lines.append(
                f"! 界面 Access VLAN {vlan_id} 改用设置 PVID 的 switchport default vlan"
            )
            lines.append(f" switchport default vlan {vlan_id}")
        elif kind == "trunk":
            lines.append(" switchport mode trunk")
            numbers = _vlan_numbers(iface.get("trunk_vlans") or [], "Trunk VLAN")
            used.extend(numbers)
            if numbers:
                lines.append(f" switchport vlan {_vlan_spec(numbers)} tag")
            else:
                lines.append("! 未填写允许 VLAN，没有写 switchport vlan")
            if iface.get("pvid") not in (None, "", 1, "1"):
                pvid = _integer(iface["pvid"], "PVID", 1, 4094)
                used.append(pvid)
                lines.append(f" switchport default vlan {pvid}")
        else:
            vlan_id = _integer(iface.get("vlan_id"), "Hybrid VLAN", 1, 4094)
            used.append(vlan_id)
            lines.append(" switchport mode hybrid")
            lines.append(f" switchport vlan {vlan_id} tag")
            lines.append("! 界面只填了一个 VLAN，按命令手册示例写成 tag。hybrid 口也能收不带标签的报文")
        return lines

    @staticmethod
    def _pon(name, iface, kind, model, used):
        lines = []
        if model == "c600":
            lines.append(" no shutdown")
        else:
            lines.append(
                "! C300 的 no shutdown 示例在 GE/10GE 和 gpon-onu 上，不在 gpon-olt 上，所以这里不写"
            )
        detail = ZTEOLTVLANGenerator._vlan_detail(iface, kind, used)
        lines.append(
            f"! PON 口 {name} 不写 switchport。switchport vlan 的命令模式是二层 FE/GE/10GE"
        )
        if detail:
            lines.append(f"! 界面把这个口标成 {kind}，{detail}")
        if model == "c600":
            lines.append(
                "! ONU 注册未写成命令。C600 维护说明的示例是 "
                "onu <编号> type <类型> sn <SN>，或 onu <编号> type <类型> loid <LOID>。"
                "界面没有类型、SN 和 LOID"
            )
        else:
            lines.append(
                "! ONU 注册未写成命令。C300 命令手册 1.13 的示例写在 PON 口下："
                "onu <编号> type <类型> sn <SN>。界面没有类型和 SN"
            )
        lines.append("! service-port 需要 vport 和 user-vlan，界面没有这两个字段，所以不写")
        return lines

    @staticmethod
    def _onu_port(name, iface, kind, model, used):
        lines = []
        if model == "c300":
            lines.append(" no shutdown")
        else:
            lines.append(
                "! C600 维护说明的 no shutdown 写在上联口和 gpon_olt，不写在 onu 接口上"
            )
        detail = ZTEOLTVLANGenerator._vlan_detail(iface, kind, used)
        parent = "gpon_olt" if model == "c600" else "gpon-olt"
        lines.append(
            f"! {name} 是注册之后的 ONU 接口。认证命令写在 {parent} 口下，不写在这里"
        )
        if detail:
            lines.append(f"! 界面 VLAN（{kind}，{detail}）未映射。service-port 需要 vport 和 user-vlan")
        return lines

    @staticmethod
    def _vlan_detail(iface, kind, used):
        if kind == "trunk":
            numbers = _vlan_numbers(iface.get("trunk_vlans") or [], "Trunk VLAN")
            used.extend(numbers)
            return "VLAN " + (_vlan_spec(numbers) if numbers else "未填")
        if iface.get("vlan_id") in (None, ""):
            return ""
        vlan_id = _integer(iface.get("vlan_id"), "VLAN", 1, 4094)
        used.append(vlan_id)
        return f"VLAN {vlan_id}"

    @staticmethod
    def _vlanif(vlanif, model):
        vlan_id = _integer(vlanif.get("vlan_id"), "VLAN接口", 1, 4094)
        description = _phrase(vlanif.get("description") or "", "VLAN接口描述")
        ip_addr = _ipv4(vlanif.get("ip_address") or vlanif.get("ip"), "VLAN接口IP")
        mask = _mask(vlanif.get("mask") or "255.255.255.0", "VLAN接口掩码")
        lines = []
        if description:
            lines.append(f"! VLAN 接口 {vlan_id} 描述 {description} 未写入。已核对的示例没有 description")
        if model == "c600":
            lines.append(f"! C600 三层口写作 interface vlan{vlan_id}")
        lines.extend([
            _l3_command(f"vlan {vlan_id}", model),
            f" ip address {ip_addr} {mask}",
            " exit",
        ])
        return lines

    @staticmethod
    def _stp(stp):
        enabled = bool(stp.get("enable", True))
        mode = str(stp.get("mode") or "stp").lower()
        if mode not in ("stp", "rstp", "mstp"):
            raise ZTEOLTConfigError("STP 模式只能是 stp、rstp 或 mstp")
        priority = _integer(stp.get("priority", 32768), "STP优先级", 0, 61440)
        if enabled and mode == "stp" and priority == 32768:
            return []
        state = "打开" if enabled else "关闭"
        return [
            f"! 生成树未生成命令（界面为 {state}，模式 {mode}，优先级 {priority}）。"
            "OLT 上联保护用的是 UAPS，不是交换机那套 spanning-tree"
        ]


class ZTEOLTRoutingGenerator:
    """静态路由。OSPF、BGP、RIP 只留注释。"""

    @staticmethod
    def generate(config, model):
        if not config:
            return ""
        lines = []
        for route in config.get("static_routes") or []:
            lines.extend(ZTEOLTRoutingGenerator._route(route))

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
                raise ZTEOLTConfigError("OSPF 区域只能是数字或点分格式")
            lines.append(
                f"! OSPF 未生成命令（进程 {process}，区域 {area}）。"
                "C300 配置手册里的 router ospf 出现在 MPLS 示例，不在本切片"
            )

        bgp = config.get("bgp") or {}
        if bgp.get("peers") or bgp.get("networks"):
            asn = _integer(bgp.get("as_number"), "BGP AS", 1, 4294967295)
            lines.append(f"! BGP 未生成命令（AS {asn}）。本切片只写已核对的 ip route")
        if model == "c600" and lines:
            lines.insert(0, "! 静态路由按 C600 配置说明的 ip route <目的> <掩码> <下一跳> 书写")
        return _section("路由配置", lines)

    @staticmethod
    def _route(route):
        dest = _ipv4(route.get("dest_network") or route.get("dest"), "目的网络")
        mask = _mask(route.get("mask"), "路由掩码")
        nexthop = route.get("next_hop") or route.get("nexthop")
        interface = route.get("interface")
        lines = []
        if nexthop:
            lines.append(f"ip route {dest} {mask} {_ipv4(nexthop, '下一跳')}")
        else:
            lines.append(
                f"! 静态路由 {dest} {mask} 未写入。已核对的全局 ip route 必须有下一跳"
            )
        if interface:
            lines.append(
                "! 出接口 "
                + normalize_interface(interface, "路由出接口")
                + " 未写进 ip route。已核对的全局示例只有下一跳"
            )
        if route.get("preference") not in (None, "", 60, "60"):
            distance = _integer(route["preference"], "路由优先级", 1, 255)
            lines.append(
                f"! 路由优先级 {distance} 未写入。已核对的 ip route 示例没有管理距离"
            )
        return lines


class ZTEOLTSecurityGenerator:
    """安全页签只校验并注释。"""

    @staticmethod
    def generate(config, model):
        del model
        if not config:
            return ""
        lines = []
        for acl in config.get("acls") or []:
            number = _integer(acl.get("number"), "ACL号", 1, 39999)
            description = _phrase(acl.get("description") or "", "ACL描述")
            for rule in acl.get("rules") or []:
                action = _single(rule.get("action") or "permit", "ACL动作")
                if action not in ("permit", "deny"):
                    raise ZTEOLTConfigError("ACL 动作只能是 permit 或 deny")
                _integer(rule.get("id", 5), "ACL规则号", 1, 65535)
            text = f"! ACL {number}"
            if description:
                text += f" {description}"
            text += " 未生成命令。本切片没有核对可粘贴的 ACL 规则"
            lines.append(text)

        for port in config.get("port_security") or []:
            if not port.get("enable", True):
                continue
            interface = normalize_interface(port.get("interface"), "端口安全接口")
            maximum = _integer(port.get("max_mac", 1), "MAC数量", 1, 1024)
            action = _single(str(port.get("action") or "shutdown").lower(), "端口安全动作")
            if action not in ("protect", "restrict", "shutdown"):
                raise ZTEOLTConfigError("端口安全违规动作只能是 protect、restrict 或 shutdown")
            lines.append(
                f"! 端口安全未写入（接口 {interface}，MAC 上限 {maximum}，动作 {action}）"
            )

        for rule in config.get("traffic_filters") or []:
            interface = normalize_interface(rule.get("interface"), "ACL应用接口")
            number = _integer(rule.get("acl_number"), "ACL号", 1, 39999)
            direction = _phrase(str(rule.get("direction") or "in"), "ACL方向").lower()
            if direction not in ("inbound", "outbound", "in", "out"):
                raise ZTEOLTConfigError("ACL 方向只能是 inbound 或 outbound")
            lines.append(f"! 接口 {interface} {direction} 引用 ACL {number} 未写成命令")

        dhcp = config.get("dhcp_snooping") or {}
        if dhcp.get("enable"):
            detail = "已在界面打开"
            if dhcp.get("vlan"):
                detail += f"，VLAN {_integer(dhcp['vlan'], 'DHCP Snooping VLAN', 1, 4094)}"
            ports = []
            for port in dhcp.get("trusted_ports") or []:
                if str(port).strip():
                    ports.append(normalize_interface(port, "DHCP信任端口"))
            if ports:
                detail += "，信任口 " + ", ".join(ports)
            lines.append(f"! DHCP Snooping 未生成命令（{detail}）")

        arp = config.get("arp_inspection") or {}
        arp_vlans = [_integer(vlan, "ARP VLAN", 1, 4094) for vlan in (arp.get("vlans") or [])]
        arp_ports = []
        for port in arp.get("trusted_ports") or []:
            if str(port).strip():
                arp_ports.append(normalize_interface(port, "ARP信任端口"))
        if arp_vlans or arp_ports:
            detail = ""
            if arp_vlans:
                detail += "VLAN " + ", ".join(str(item) for item in arp_vlans)
            if arp_ports:
                detail += ("，" if detail else "") + "信任口 " + ", ".join(arp_ports)
            lines.append(f"! ARP 检测未生成命令（{detail}）")

        for storm in config.get("storm_controls") or []:
            interface = normalize_interface(storm.get("interface"), "风暴抑制接口")
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


class ZTEOLTInterfaceGenerator:
    """聚合、LLDP、PoE、限速只在界面偏离默认值时留注释。"""

    @staticmethod
    def generate(config, model):
        del model
        if not config:
            return ""
        lines = []
        for trunk in config.get("eth_trunks") or []:
            lines.extend(ZTEOLTInterfaceGenerator._trunk(trunk))
        lines.extend(ZTEOLTInterfaceGenerator._unverified(config))
        return _section("接口配置", lines)

    @staticmethod
    def _trunk(trunk):
        trunk_id = _integer(trunk.get("trunk_id"), "聚合组", 1, 64)
        mode_key = _single(str(trunk.get("mode") or "lacp-static").lower(), "聚合模式")
        if mode_key not in ("manual", "lacp-static", "lacp-dynamic", "active", "on", "passive"):
            raise ZTEOLTConfigError("聚合模式只能是 manual、lacp-static 或 lacp-dynamic")
        members = []
        for member in trunk.get("member_ports") or []:
            if not str(member).strip():
                continue
            name = normalize_interface(member, "聚合成员")
            if not _is_ethernet(name):
                raise ZTEOLTConfigError(f"聚合成员 {name} 需要是上联口，不能是 PON 口")
            members.append(name)
        description = _phrase(trunk.get("description") or "", "聚合描述")
        link_type = str(trunk.get("port_link_type") or "access").lower()
        if link_type not in _LINK_TYPES:
            raise ZTEOLTConfigError(f"不支持的聚合端口类型 {link_type}")
        detail = f"smartgroup{trunk_id}，模式 {mode_key}，成员 {', '.join(members) or '未填'}"
        if description:
            detail += f"，描述 {description}"
        if link_type == "trunk":
            numbers = _vlan_numbers(trunk.get("trunk_vlans") or [], "聚合VLAN")
            detail += "，Trunk VLAN " + (_vlan_spec(numbers) if numbers else "未填")
        elif trunk.get("native_vlan"):
            detail += f"，VLAN {_integer(trunk['native_vlan'], '聚合VLAN', 1, 4094)}"
        return [
            f"! 聚合未生成命令（{detail}）。"
            "C300 成员口是 smartgroup <id> mode active，C600 要进 lacp 视图，两套不混写"
        ]

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
                    f"! LLDP 未生成命令（模式 {mode}，间隔 {interval}，保持 {hold}）"
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
            lines.append("! PoE 未生成命令")
            for item in poe_interfaces:
                interface = normalize_interface(item.get("interface"), "PoE接口")
                mode = _single(item.get("mode") or "auto", "PoE模式")
                lines.append(f"! PoE 接口 {interface} 模式 {mode} 仅作说明")

        for limit in config.get("rate_limits") or []:
            interface = normalize_interface(limit.get("interface"), "限速接口")
            detail = interface
            if limit.get("cir_in"):
                detail += f" 入 {_integer(limit['cir_in'], '入方向限速', 1, 100000000)}"
            if limit.get("cir_out"):
                detail += f" 出 {_integer(limit['cir_out'], '出方向限速', 1, 100000000)}"
            lines.append(f"! 限速未生成命令（{detail}）")
        return lines


def _header(model):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    if model == "c600":
        assumed = (
            "! 本份脚本按 C600 接口写法：上联 xgei-1/1/1，PON gpon_olt-1/1/1，"
            "带外口 mgmt_eth，三层口 interface vlan100（中间没有空格）。"
        )
        other = "! 若设备是 C300/C320，请改用 gei_1/19/1、gpon-olt_1/1/1 和 interface vlan mng1。"
    else:
        assumed = (
            "! 本份脚本按 C300/C320 接口写法：上联 gei_1/19/1 或 xgei_1/10/1，"
            "PON gpon-olt_1/1/1，带外口 interface vlan mng1，三层口 interface vlan 10。"
        )
        other = "! 若设备是 C600，请改用 xgei-1/1/1、gpon_olt-1/1/1、interface mgmt_eth，三层口写作 interface vlan100。"
    return "\n".join([
        "!",
        "! 中兴 OLT 配置脚本（ZXA10 C300/C320 与 C600）",
        f"! 生成时间: {timestamp}",
        assumed,
        other,
        "! 命令依据: C300/C320 命令手册 SJ-20130520164529-010，C300 配置手册 SJ-20130520164529-007，",
        "! C600 维护说明中的 vlan、ip route、xgei-、gpon_olt- 和 no shutdown。",
        "! 请在特权模式 ZXAN# 下粘贴。不是经典 ZXROS，也不是 ROSNG。",
        "! ONU 的类型、SN 和 LOID 没有界面字段，只留在 ! 注释里，不会猜一条 onu 命令。",
        "! 核对不到的语法只写在 ! 注释里。生成结果只是文本，不会下发到设备。",
        "!",
    ])


def generate_olt_config(basic=None, vlan=None, routing=None, security=None, interface=None):
    """把各页签的结构化配置拼成一份可预览的 OLT 脚本。没有内容时返回空串。"""
    basic = basic or {}
    vlan = vlan or {}
    routing = routing or {}
    security = security or {}
    interface = interface or {}
    if not any((basic, vlan, routing, security, interface)):
        return ""
    model = _resolve_model(basic, vlan, routing, security, interface)
    parts = [
        ZTEOLTBasicGenerator.generate(basic, model),
        ZTEOLTVLANGenerator.generate(vlan, model),
        ZTEOLTRoutingGenerator.generate(routing, model),
        ZTEOLTSecurityGenerator.generate(security, model),
        ZTEOLTInterfaceGenerator.generate(interface, model),
    ]
    body = "\n".join(part for part in parts if part)
    if not body:
        return ""
    return "\n".join([
        _header(model),
        "configure terminal",
        body,
        "end",
        "! 确认无误后在特权模式执行 write 保存。脚本本身不会保存，也不会登录设备。",
        "",
    ])
