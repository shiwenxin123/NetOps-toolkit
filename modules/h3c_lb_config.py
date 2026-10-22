#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
华三服务器负载均衡配置生成器（Comware，SecPath 负载均衡命令）。

可粘贴的命令只来自核对过的公开材料：

- 《01-负载均衡命令》（h3c.com，文档 1887263）：
  real-server、ip address、port、weight、server-farm（实服务器视图）、
  server-farm（系统视图）、predictor round-robin / random / least-connection /
  hash address source / hash address destination、
  probe、nqa template icmp、virtual-server type tcp|udp|http|ip、
  virtual ip address、port（虚服务器视图）、default server-farm、
  service enable、arp-nd interface
- 《Server load balancing configuration》里的 FTP 负载均衡示例，
  以及同书高可靠示例里的接口和聚合：
  system-view、interface gigabitethernet、interface route-aggregation、
  ip address <地址> <点分掩码>、quit、ip route-static、
  port link-aggregation group
- 配置指导写明 sysname 用来改设备名（基础配置命令参考）

不写成可执行命令的内容：
- SSH、本地用户、Telnet。开局示例没有 ssh server enable / local-user
- 安全域和 security-policy。示例里有，但界面没有为每个接口指定 trust/untrust
- OSPF、BGP、RIP、生成树、ACL、端口安全、LLDP、PoE、限速、NTP、SNMP、日志、DNS
- 关闭 NAT 的 transparent enable、重启、保存、恢复出厂

实服务组缺省已经打开 NAT，所以实服务器上的 port 按手册会生效。
虚服务器缺省关闭，脚本写入 service enable，这是打开虚服务，不是重启设备。

以 # 开头的行只是说明。Comware 命令行里单独输入 # 会退回用户视图，
粘贴时请跳过这些行。

用户输入只做单行拼接，拒绝换行和控制字符。生成过程不调用 shell。
"""

import re
import time


class H3CLBConfigError(ValueError):
    """用户字段无法安全写入一条负载均衡 CLI。"""


_BREAK = re.compile(r"[\r\n\x00]")
_SINGLE = re.compile(r"^[A-Za-z0-9_./:@%+=,-]{1,128}$")
_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,62}$")
_IPV4 = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")
_FORBIDDEN = re.compile(
    r"\b(?:reboot|reset|shutdown|erase|format|restore|undo|delete|save)\b",
    re.IGNORECASE,
)

_IFACE_KINDS = (
    (re.compile(r"(?i)^(?:gigabitethernet|ge)\s*(\d+/\d+/\d+)$"), "GigabitEthernet"),
    (re.compile(r"(?i)^(?:ten-gigabitethernet|xge)\s*(\d+/\d+/\d+)$"), "Ten-GigabitEthernet"),
    (re.compile(r"(?i)^(?:route-aggregation|ragg)\s*(\d+)$"), "Route-Aggregation"),
    (re.compile(r"(?i)^(?:vlan-interface|vlanif)\s*(\d+)$"), "Vlan-interface"),
)

_PREDICTOR = {
    "round-robin": "predictor round-robin",
    "random": "predictor random",
    "least-connection": "predictor least-connection",
    "hash-source": "predictor hash address source",
    "hash-destination": "predictor hash address destination",
}
_VS_TYPES = {"tcp", "udp", "http", "ip"}
_VS_DEFAULT_PORT = {"tcp": 0, "udp": 0, "http": 80, "ip": 0}


def _raw(value):
    return "" if value is None else str(value)


def _single(value, field):
    text = _raw(value).strip()
    if not text or _BREAK.search(_raw(value)) or not _SINGLE.match(text):
        raise H3CLBConfigError(f"{field} 含有空格、换行或无法写入命令的字符")
    return text


def _optional_single(value, field):
    if value is None or str(value).strip() == "":
        return ""
    return _single(value, field)


def _phrase(value, field):
    text = _raw(value).replace("\t", " ").strip()
    if _BREAK.search(_raw(value)):
        raise H3CLBConfigError(f"{field} 不能包含换行")
    if any(char in text for char in "`;&|$<>\\"):
        raise H3CLBConfigError(f"{field} 含有无法写入命令的字符")
    return text


def _integer(value, field, low, high):
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise H3CLBConfigError(f"{field} 不是整数")
    if number < low or number > high:
        raise H3CLBConfigError(f"{field} 超出范围 {low}-{high}")
    return number


def _name(value, field, limit=63):
    text = _single(value, field)
    if len(text) > limit or not _NAME.match(text):
        raise H3CLBConfigError(
            f"{field} 须为 1-{limit} 位，以字母或数字开头，只能含字母、数字、点、下划线或短横线"
        )
    return text


def _ipv4(value, field, allow_zero=False):
    text = _single(value, field)
    if not _IPV4.match(text):
        raise H3CLBConfigError(f"{field} 不是 IPv4 地址")
    parts = [int(part) for part in text.split(".")]
    if any(part > 255 for part in parts):
        raise H3CLBConfigError(f"{field} 不是 IPv4 地址")
    if text == "255.255.255.255" or parts[0] >= 224 or parts[0] == 127:
        raise H3CLBConfigError(f"{field} 不能是环回、组播或广播地址")
    if parts[0] == 0 and not allow_zero:
        raise H3CLBConfigError(f"{field} 不能是 0 开头的地址")
    return text


def _ip_int(text):
    parts = [int(part) for part in text.split(".")]
    return (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]


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
        raise H3CLBConfigError(f"{field} 不是子网掩码")
    parts = [int(part) for part in text.split(".")]
    if any(part > 255 for part in parts):
        raise H3CLBConfigError(f"{field} 不是子网掩码")
    if text != "0.0.0.0" and _leading_ones(text) is None:
        raise H3CLBConfigError(f"{field} 不是连续掩码")
    return text


def _prefix_of(mask):
    if mask == "0.0.0.0":
        return 0
    return _leading_ones(mask)


def _network_address(ip_addr, mask):
    prefix = _prefix_of(mask)
    value = _ip_int(ip_addr)
    if prefix <= 0:
        value = 0
    else:
        bits = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
        value &= bits
    return ".".join(str((value >> shift) & 255) for shift in (24, 16, 8, 0))


def _same_subnet(left, right, mask):
    prefix = _prefix_of(mask)
    if prefix <= 0:
        return True
    bits = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
    return (_ip_int(left) & bits) == (_ip_int(right) & bits)


def _sysname(value):
    text = _phrase(value, "主机名")
    if not re.match(r"^[A-Za-z0-9._-]{1,64}$", text):
        raise H3CLBConfigError("主机名只能是 1-64 位字母、数字、点、下划线或短横线")
    return text


def normalize_interface(name, field="接口"):
    """把 GE1/0/1、Vlanif10 收成命令里的接口类型和编号。"""
    text = _phrase(name, field)
    compact = re.sub(r"\s+", "", text)
    spaced = re.sub(r"(?i)^(vlan-interface|vlanif|ten-gigabitethernet|gigabitethernet|route-aggregation|ge|xge|ragg)", r"\1 ", compact)
    spaced = re.sub(r"\s+", " ", spaced).strip()
    for pattern, kind in _IFACE_KINDS:
        matched = pattern.match(spaced) or pattern.match(compact)
        if matched:
            number = matched.group(1)
            if kind == "Vlan-interface":
                vlan_id = int(number)
                if vlan_id < 1 or vlan_id > 4094:
                    raise H3CLBConfigError(f"{field} 的 VLAN 超出 1-4094")
            return kind, number
    raise H3CLBConfigError(
        f"{field} 不是负载均衡接口名。请填写 GigabitEthernet1/0/1、"
        "Ten-GigabitEthernet1/0/1、Route-Aggregation1 或 Vlan-interface10"
    )


def _interface_command(kind, number):
    return f"interface {kind} {number}"


def _comment_lines(text, field):
    body = _raw(text).replace("\r\n", "\n").replace("\r", "\n").strip("\n")
    if not body:
        return []
    if "\x00" in body:
        raise H3CLBConfigError(f"{field} 含有无法写入的字符")
    lines = []
    for line in body.split("\n"):
        if any(char in line for char in "`;&|$<>\\"):
            raise H3CLBConfigError(f"{field} 含有无法写入命令的字符")
        lines.append("# " + line if line else "#")
    return lines


def _section(title, lines):
    kept = [line for line in lines if line is not None and line != ""]
    if not kept:
        return []
    return ["#", f"# {title}", "#"] + kept


def _guard(lines):
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if _FORBIDDEN.search(stripped):
            raise H3CLBConfigError("生成结果含有不允许自动下发的命令，已中止")
    return lines


class H3CLBBasicGenerator:
    """系统名、接口地址、默认路由。SSH 只留注释。"""

    @staticmethod
    def generate(config, interfaces):
        if not config and not interfaces:
            return []
        lines = []
        hostname = (config or {}).get("hostname")
        if hostname:
            lines.append(f"sysname {_sysname(hostname)}")

        for item in interfaces:
            lines.extend(H3CLBBasicGenerator._address(item))

        config = config or {}
        password = config.get("password") or {}
        user = config.get("user") or {}
        if password.get("value") or (user.get("username") and user.get("password")) or config.get("enable_ssh") or config.get("enable_telnet"):
            detail = []
            if config.get("enable_ssh"):
                detail.append("SSH")
                if config.get("ssh_port") not in (None, "", 22, "22"):
                    _integer(config.get("ssh_port"), "SSH端口", 1, 65535)
            if config.get("enable_telnet"):
                detail.append("Telnet")
            if user.get("username"):
                detail.append("用户 " + _name(user["username"], "用户名", 55))
            if password.get("value"):
                _phrase(password["value"], "管理密码")
                detail.append("管理密码")
            lines.append(
                "# "
                + "、".join(detail)
                + " 未写入。负载均衡开局示例没有 ssh server enable 和 local-user，口令也不会写进注释"
            )

        banner = config.get("banner") or {}
        banner_text = banner.get("motd") or banner.get("login") or ""
        if banner.get("motd") and banner.get("login"):
            banner_text = banner["motd"].rstrip() + "\n" + banner["login"].lstrip()
        if str(banner_text).strip():
            lines.append("# Banner 未生成命令。开局示例没有 header login")
            lines.extend(_comment_lines(banner_text, "Banner"))

        ntp = config.get("ntp") or {}
        servers = ntp.get("servers") or []
        if servers:
            addresses = [_ipv4(server.get("ip"), "NTP服务器") for server in servers]
            lines.append(
                "# NTP 未生成命令（服务器 "
                + ", ".join(addresses)
                + "）。本次只核对了负载均衡开局命令，没有写入 ntp-service"
            )

        snmp = config.get("snmp") or {}
        if any(snmp.get(key) for key in ("version", "community_read", "community_write", "trap_host", "sys_location", "sys_contact")):
            lines.append("# SNMP 未生成命令。开局示例没有 snmp-agent")

        log = config.get("log") or {}
        host = log.get("host")
        level = _phrase(str(log.get("log_level") or ""), "日志级别")
        default_log = (not host) and level in ("", "informational") and log.get("info_center_enable", True)
        if log and not default_log:
            lines.append("# 日志未生成命令。开局示例没有 info-center")

        dns = config.get("dns") or {}
        dns_servers = [_ipv4(server, "DNS服务器") for server in (dns.get("servers") or [])]
        domain = _phrase(dns.get("domain") or "", "域名")
        if dns_servers or domain:
            lines.append("# DNS 未生成命令。开局示例没有 dns server")

        return _section("基础配置", lines)

    @staticmethod
    def _address(item):
        kind, number = item["kind"], item["number"]
        lines = [_interface_command(kind, number)]
        if item.get("description"):
            lines.append(f"# 描述 {item['description']} 未写入。开局示例的接口下只有 ip address")
        lines.append(f" ip address {item['ip']} {item['mask']}")
        lines.append(" quit")
        gateway = item.get("gateway")
        if gateway:
            lines.append(f"ip route-static 0.0.0.0 0.0.0.0 {gateway}")
        return lines


class H3CLBServiceGenerator:
    """实服务器、实服务组、虚服务器、ICMP 健康检查。"""

    @staticmethod
    def generate(slb, interfaces):
        if not slb:
            return []
        real_servers = slb.get("real_servers") or []
        virtual_servers = slb.get("virtual_servers") or []
        if not real_servers and not virtual_servers:
            return []

        farm = _name(slb.get("server_farm") or "web", "实服务组")
        predictor_key = str(slb.get("predictor") or "round-robin").strip().lower()
        predictor = _PREDICTOR.get(predictor_key)
        if not predictor:
            raise H3CLBConfigError(
                "调度算法只能是 round-robin、random、least-connection、hash-source 或 hash-destination"
            )

        lines = []
        health = str(slb.get("health_check") or "").strip().lower()
        if health == "icmp":
            lines.extend([
                "nqa template icmp icmp1",
                " quit",
            ])
        elif health:
            lines.append(
                f"# 健康检查 {health} 未写入。已核对的是 nqa template icmp 和 server-farm 下的 probe"
            )

        lines.append(f"server-farm {farm}")
        lines.append(f" {predictor}")
        if health == "icmp":
            lines.append(" probe icmp1")
        lines.append(" quit")

        seen = set()
        for server in real_servers:
            lines.extend(H3CLBServiceGenerator._real(server, farm, seen, interfaces))

        if real_servers and not virtual_servers:
            lines.append("# 未填写虚服务器。实服务器已写入，但没有 virtual-server 时业务不会被调度")

        seen_vs = set()
        for server in virtual_servers:
            lines.extend(H3CLBServiceGenerator._virtual(server, farm, seen_vs, interfaces))

        return _section("服务器负载均衡", lines)

    @staticmethod
    def _real(server, farm, seen, interfaces):
        name = _name(server.get("name"), "实服务器")
        key = name.lower()
        if key in seen:
            raise H3CLBConfigError(f"实服务器 {name} 重复")
        seen.add(key)
        ip_addr = _ipv4(server.get("ip") or server.get("ip_address"), "实服务器地址")
        port = _integer(server.get("port", 80), "实服务器端口", 0, 65535)
        weight = _integer(server.get("weight", 100), "权值", 1, 255)
        lines = [
            f"real-server {name}",
            f" ip address {ip_addr}",
            f" port {port}",
            f" weight {weight}",
            f" server-farm {farm}",
            " quit",
        ]
        if not any(_same_subnet(ip_addr, item["ip"], item["mask"]) for item in interfaces):
            lines.append(
                f"# 实服务器 {name} 的地址 {ip_addr} 不在已配置接口网段内。"
                "请另配通往服务器的接口或静态路由"
            )
        return lines

    @staticmethod
    def _virtual(server, farm, seen, interfaces):
        name = _name(server.get("name"), "虚服务器")
        key = name.lower()
        if key in seen:
            raise H3CLBConfigError(f"虚服务器 {name} 重复")
        seen.add(key)
        kind = str(server.get("type") or "tcp").strip().lower()
        if kind not in _VS_TYPES:
            raise H3CLBConfigError("虚服务器类型只能是 tcp、udp、http 或 ip")
        vip = _ipv4(server.get("ip") or server.get("vip"), "虚服务器地址")
        port = _integer(server.get("port", _VS_DEFAULT_PORT[kind]), "虚服务器端口", 0, 65535)
        if kind == "http" and port == 0:
            raise H3CLBConfigError("HTTP 虚服务器端口范围是 1-65535，不能是 0")
        lines = [
            f"virtual-server {name} type {kind}",
            f" virtual ip address {vip}",
        ]
        if port != _VS_DEFAULT_PORT[kind]:
            lines.append(f" port {port}")
        lines.append(f" default server-farm {farm}")
        lines.append(" service enable")
        matched = [
            item for item in interfaces
            if _same_subnet(vip, item["ip"], item["mask"])
        ]
        if matched:
            for item in matched:
                lines.append(f" arp-nd interface {item['kind']} {item['number']}")
        else:
            lines.append(
                "# 虚服务器地址和已配置接口不在同一网段，未写 arp-nd interface。"
                "同一网段时手册要求指定发送免费 ARP 的接口"
            )
        lines.append(" quit")
        return lines


class H3CLBRoutingGenerator:
    """静态路由可粘贴。OSPF、BGP、RIP 只留注释。"""

    @staticmethod
    def generate(config):
        if not config:
            return []
        lines = []
        seen = set()
        for route in config.get("static_routes") or []:
            dest = _ipv4(route.get("dest_network") or route.get("dest"), "目的网络", allow_zero=True)
            mask = _mask(route.get("mask") or "255.255.255.0", "路由掩码")
            nexthop = route.get("next_hop") or route.get("nexthop")
            interface = route.get("interface")
            network = _network_address(dest, mask)
            if nexthop:
                hop = _ipv4(nexthop, "下一跳")
                command = f"ip route-static {network} {mask} {hop}"
                if command not in seen:
                    seen.add(command)
                    lines.append(command)
                if interface:
                    kind, number = normalize_interface(interface, "路由出接口")
                    lines.append(
                        f"# 出接口 {kind} {number} 未写入。开局示例的 ip route-static 只带下一跳"
                    )
            elif interface:
                kind, number = normalize_interface(interface, "路由出接口")
                lines.append(
                    f"# 静态路由 {network} {mask} 经由 {kind} {number} 未写入。"
                    "已核对的写法必须带下一跳地址"
                )
            else:
                raise H3CLBConfigError("静态路由缺少下一跳")
            if route.get("preference") is not None:
                distance = _integer(route["preference"], "路由优先级", 1, 255)
                if distance != 60:
                    lines.append(
                        f"# 路由优先级 {distance} 未写入。开局示例的 ip route-static 没有 preference"
                    )

        ospf = config.get("ospf") or {}
        if ospf.get("networks") or ospf.get("router_id"):
            process = _integer(ospf.get("process_id", 1), "OSPF进程", 1, 65535)
            lines.append(
                f"# OSPF 进程 {process} 未生成命令。负载均衡开局示例只有 ip route-static"
            )

        bgp = config.get("bgp") or {}
        if bgp.get("peers") or bgp.get("networks"):
            asn = _integer(bgp.get("as_number"), "BGP AS", 1, 4294967295)
            lines.append(f"# BGP AS {asn} 未生成命令。开局示例没有 bgp")

        rip = config.get("rip") or {}
        if rip.get("networks"):
            lines.append("# RIP 未生成命令。开局示例没有 rip")

        return _section("路由配置", lines)


class H3CLBVLANGenerator:
    """三层 VLAN 口写地址。二层 VLAN 和生成树只留注释。"""

    @staticmethod
    def addresses(config):
        found = []
        for vlanif in (config or {}).get("vlanifs") or []:
            vlan_id = _integer(vlanif.get("vlan_id"), "VLAN接口", 1, 4094)
            ip_addr = _ipv4(vlanif.get("ip_address") or vlanif.get("ip"), "VLAN接口IP")
            mask = _mask(vlanif.get("mask") or "255.255.255.0", "VLAN接口掩码")
            description = _phrase(vlanif.get("description") or "", "VLAN接口描述")
            found.append({
                "kind": "Vlan-interface",
                "number": str(vlan_id),
                "ip": ip_addr,
                "mask": mask,
                "description": description,
            })
        return found

    @staticmethod
    def comments(config):
        if not config:
            return []
        lines = []
        for vlan in config.get("vlans") or []:
            vlan_id = _integer(vlan.get("id"), "VLAN ID", 1, 4094)
            name = _phrase(vlan.get("name") or "", "VLAN名称")
            text = f"# VLAN {vlan_id}"
            if name:
                text += f"（{name}）"
            text += " 未生成二层命令。负载均衡脚本不写 vlan / switchport"
            lines.append(text)
        for iface in config.get("interfaces") or []:
            kind, number = normalize_interface(iface.get("interface"), "二层接口")
            mode = _phrase(str(iface.get("type") or "access"), "端口类型")
            lines.append(
                f"# {kind} {number} 的 {mode} 未写入。这不是交换机脚本，没有 switchport"
            )
        stp = config.get("stp") or {}
        if stp:
            lines.append("# 生成树未写入。负载均衡开局示例没有 stp")
        return _section("VLAN说明", lines)


class H3CLBSecurityGenerator:
    """包过滤和端口安全没有对应的界面字段，只留注释。"""

    @staticmethod
    def generate(config):
        if not config:
            return []
        lines = []
        if config.get("acls"):
            numbers = []
            for acl in config["acls"]:
                numbers.append(str(_integer(acl.get("number"), "ACL号", 1, 65535)))
            lines.append(
                "# ACL "
                + ", ".join(numbers)
                + " 未生成。开局示例用的是 security-policy ip，界面没有安全域，不能代填 trust/untrust"
            )
        if any(item.get("enable", True) for item in (config.get("port_security") or [])):
            lines.append("# 端口安全未写入。负载均衡开局示例没有 port-security")
        if config.get("traffic_filters"):
            lines.append("# 接口包过滤未写入。没有核对到 packet-filter，也不代填 security-policy")
        if (config.get("dhcp_snooping") or {}).get("enable"):
            lines.append("# DHCP Snooping 未写入")
        if config.get("storm_controls"):
            lines.append("# 风暴抑制未写入")
        if (config.get("anti_attack") or {}).get("enable"):
            lines.append("# 防攻击选项未写入。不生成攻击防护的阈值命令")
        return _section("安全说明", lines)


class H3CLBInterfaceGenerator:
    """三层聚合。只写配置指导里出现过的两条。"""

    @staticmethod
    def generate(config):
        if not config:
            return []
        lines = []
        for trunk in config.get("eth_trunks") or []:
            lines.extend(H3CLBInterfaceGenerator._aggregate(trunk))

        lldp = config.get("lldp") or {}
        if lldp.get("enable"):
            lines.append("# LLDP 未生成命令。开局示例没有 lldp global enable")

        poe = config.get("poe") or {}
        if poe.get("interfaces") or poe.get("enable") is False:
            lines.append("# PoE 未生成命令。负载均衡开局示例没有 poe enable")

        if config.get("rate_limits"):
            lines.append("# 限速未生成命令。开局示例没有 qos lr")

        loop = config.get("loopback_detection") or {}
        if loop.get("enable"):
            lines.append("# 环路检测未生成命令")

        return _section("接口配置", lines)

    @staticmethod
    def _aggregate(trunk):
        trunk_id = _integer(trunk.get("trunk_id"), "聚合组", 1, 64)
        lines = [f"interface Route-Aggregation {trunk_id}", " quit"]
        description = _phrase(trunk.get("description") or "", "聚合描述")
        if description:
            lines.append(f"# 聚合描述 {description} 未写入")
        mode = _phrase(str(trunk.get("mode") or ""), "聚合模式")
        if mode:
            lines.append(
                f"# 聚合模式 {mode} 未写入 link-aggregation mode。"
                "配置指导只给出 interface route-aggregation 和 port link-aggregation group"
            )
        if str(trunk.get("port_link_type") or "").lower() == "trunk" or trunk.get("trunk_vlans"):
            lines.append("# 聚合口的 VLAN 未写入。示例里的聚合口是三层口，没有 switchport")
        for member in trunk.get("member_ports") or []:
            if not str(member).strip():
                continue
            kind, number = normalize_interface(member, "聚合成员")
            lines.append(_interface_command(kind, number))
            lines.append(f" port link-aggregation group {trunk_id}")
            lines.append(" quit")
        return lines


def _mgmt_interface(config):
    mgmt = (config or {}).get("mgmt_interface") or {}
    if not mgmt.get("ip_address"):
        return None
    kind, number = normalize_interface(mgmt.get("interface") or "GigabitEthernet1/0/1", "管理接口")
    ip_addr = _ipv4(mgmt["ip_address"], "管理IP")
    mask = _mask(mgmt.get("mask") or "255.255.255.0", "管理掩码")
    gateway = _ipv4(mgmt["gateway"], "网关") if mgmt.get("gateway") else ""
    return {
        "kind": kind,
        "number": number,
        "ip": ip_addr,
        "mask": mask,
        "gateway": gateway,
        "description": "",
    }


def generate_lb_config(basic=None, vlan=None, routing=None, security=None, interface=None):
    """把各页签的结构化配置拼成一份可预览的华三负载均衡脚本。没有内容时返回空串。"""
    basic = basic or {}
    vlan = vlan or {}
    routing = routing or {}
    security = security or {}
    interface = interface or {}

    interfaces = []
    mgmt = _mgmt_interface(basic)
    if mgmt:
        interfaces.append(mgmt)
    interfaces.extend(H3CLBVLANGenerator.addresses(vlan))

    parts = [
        H3CLBBasicGenerator.generate(basic, interfaces),
        H3CLBInterfaceGenerator.generate(interface),
        H3CLBRoutingGenerator.generate(routing),
        H3CLBServiceGenerator.generate(routing.get("slb") or {}, interfaces),
        H3CLBVLANGenerator.comments(vlan),
        H3CLBSecurityGenerator.generate(security),
    ]
    body = []
    for part in parts:
        if part:
            if body:
                body.append("")
            body.extend(part)
    if not body:
        return ""

    _guard(body)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    header = [
        "#",
        "# 华三服务器负载均衡配置脚本",
        f"# 生成时间: {timestamp}",
        "# 命令风格: Comware。适用于配置指导中的 real-server / server-farm / virtual-server。",
        "# 不是华三交换机脚本，也不是迪普 ADX。",
        "# 请在用户视图粘贴 system-view 以及下面不以 # 开头的行。",
        "# 以 # 开头的行是说明。Comware 命令行里输入 # 会退回用户视图，粘贴时请跳过。",
        "# 命令依据: H3C《01-负载均衡命令》和《服务器负载均衡配置》开局示例。",
        "#",
    ]
    footer = [
        "quit",
        "# 确认无误后在用户视图执行 save。本脚本不会保存，也不会重启或恢复出厂。",
        "# service enable 只打开虚服务器，虚服务器缺省是关闭的。",
    ]
    return "\n".join(header + ["system-view"] + body + footer) + "\n"
