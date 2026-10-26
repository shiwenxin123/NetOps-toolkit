#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把网页上的少量字段交给现有生成器。

不拼接 CLI，也不登录设备。华三走 H3CConfigGenerator，中兴经典走
generate_switch_config，迪普 FW1000 走 generate_firewall_config。
"""

import re

from modules.dptech_config import DPTechConfigError, generate_firewall_config
from modules.h3c_config import H3CConfigGenerator
from modules.zte_config import ZTEConfigError, generate_switch_config


class WebInputError(ValueError):
    """字段不能安全交给生成器。消息里不回显口令。"""


_TOKEN = re.compile(r"^[\w.-]{1,64}$")
_PASSWORD = re.compile(r"^[A-Za-z0-9_./:@%+=,-]{1,64}$")
_USERNAME = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,31}$")
_INTERFACE = re.compile(r"^[A-Za-z0-9_./:-][A-Za-z0-9_./: -]{0,63}$")
_UNSAFE = re.compile(r"[\x00-\x1f\x7f]")
_META = set("`;&|$<>\\\"'")

_PRIVILEGE = {"h3c": (0, 3), "zte": (0, 15), "dptech": (0, 15)}
_DEFAULT_PRIVILEGE = {"h3c": 3, "zte": 15, "dptech": 15}
_DEFAULT_MGMT = {
    "h3c": "Vlan-interface1",
    "zte": "Vlanif1",
    "dptech": "Vlanif1",
}

SUPPORTED = (
    {
        "id": "h3c",
        "name": "华三交换机 (H3C)",
        "supported": True,
        "note": "Comware 交换机脚本：sysname、Vlan-interface、port link-type、ssh server enable。",
    },
    {
        "id": "zte",
        "name": "中兴经典 ZXROS",
        "supported": True,
        "note": "ZXR10 5200/5900/8900。Vlanif 会写成 interface vlan。不是 ROSNG，也不是 OLT。",
    },
    {
        "id": "dptech",
        "name": "迪普 FW1000",
        "supported": True,
        "note": "防火墙 Conplat：conf-mode、gige0_1、vlan-if。不是 LSW 交换机。",
    },
)

UNSUPPORTED = (
    {
        "id": "huawei",
        "name": "华为 (Huawei)",
        "supported": False,
        "note": "网页暂未开放，请使用桌面版 python main.py。",
    },
    {
        "id": "ruijie",
        "name": "锐捷 (Ruijie)",
        "supported": False,
        "note": "网页暂未开放，请使用桌面版 python main.py。",
    },
    {
        "id": "maipu",
        "name": "迈普 (Maipu)",
        "supported": False,
        "note": "网页暂未开放，请使用桌面版 python main.py。",
    },
    {
        "id": "dptech-lsw",
        "name": "迪普 LSW (交换机)",
        "supported": False,
        "note": "网页暂未开放，请使用桌面版 python main.py。",
    },
    {
        "id": "zte-rosng",
        "name": "中兴 ROSNG (5960/9900)",
        "supported": False,
        "note": "网页暂未开放，请使用桌面版 python main.py。",
    },
    {
        "id": "zte-olt",
        "name": "中兴 OLT (C300/C600)",
        "supported": False,
        "note": "网页暂未开放，请使用桌面版 python main.py。",
    },
    {
        "id": "h3c-lb",
        "name": "华三负载均衡 (SecPath)",
        "supported": False,
        "note": "网页暂未开放，请使用桌面版 python main.py。",
    },
)

_BY_ID = {item["id"]: item for item in SUPPORTED + UNSUPPORTED}
_PASSWORD_KEYS = ("enable_password", "user_password")


def list_brands():
    """网页和 /api/brands 使用的品牌清单。顺序与桌面版选择器一致。"""
    order = (
        "huawei",
        "h3c",
        "ruijie",
        "maipu",
        "zte",
        "dptech",
        "dptech-lsw",
        "zte-rosng",
        "zte-olt",
        "h3c-lb",
    )
    return [dict(_BY_ID[brand_id]) for brand_id in order]


def generate_config(payload):
    """根据扁平字段生成配置文本。成功时返回 brand、brand_name、config。"""
    if not isinstance(payload, dict):
        raise WebInputError("请求必须是对象")
    brand = _brand(payload.get("brand"))
    try:
        config = _dispatch(brand, payload)
    except WebInputError:
        raise
    except (ZTEConfigError, DPTechConfigError) as exc:
        raise WebInputError(_redact(str(exc), payload)) from None
    if not config or not str(config).strip():
        raise WebInputError("没有生成出配置，请至少填写一项内容")
    info = _BY_ID[brand]
    return {"brand": brand, "brand_name": info["name"], "config": config}


def _dispatch(brand, payload):
    basic, vlan, routing = _sections(brand, payload)
    if brand == "h3c":
        document = {}
        if basic:
            document["basic"] = basic
        if vlan:
            document["vlan"] = vlan
        if routing:
            document["routing"] = routing
        if not document:
            raise WebInputError("请至少填写主机名、管理地址、VLAN、接入端口或静态路由中的一项")
        return H3CConfigGenerator.generate_all(document)
    if not any((basic, vlan, routing)):
        raise WebInputError("请至少填写主机名、管理地址、VLAN、接入端口或静态路由中的一项")
    if brand == "zte":
        return generate_switch_config(basic=basic, vlan=vlan, routing=routing)
    if brand == "dptech":
        return generate_firewall_config(basic=basic, vlan=vlan, routing=routing)
    raise WebInputError("网页暂未开放这个品牌")


def _brand(value):
    text = _plain(value, "品牌", 32).lower()
    if not text:
        raise WebInputError("请选择品牌")
    info = _BY_ID.get(text)
    if info is None:
        raise WebInputError("未知品牌。网页第一版只生成华三交换机、中兴经典 ZXROS 和迪普 FW1000")
    if not info["supported"]:
        raise WebInputError(
            "网页暂未开放「%s」。请继续使用桌面版 python main.py。"
            "当前网页可生成：华三交换机、中兴经典 ZXROS、迪普 FW1000。" % info["name"]
        )
    return text


def _sections(brand, payload):
    basic = {}
    hostname = _token(payload.get("hostname"), "主机名", 64)
    if hostname:
        if brand == "dptech" and len(hostname) > 20:
            raise WebInputError("迪普主机名最长 20 位")
        basic["hostname"] = hostname

    enable_password = _secret(payload.get("enable_password"), "管理密码")
    if enable_password:
        basic["password"] = {"value": enable_password, "encrypted": False}

    username = _username(payload.get("username"))
    user_password = _secret(payload.get("user_password"), "用户密码")
    if bool(username) != bool(user_password):
        raise WebInputError("用户名和用户密码需要同时填写，或全部留空")
    if username:
        low, high = _PRIVILEGE[brand]
        level = _integer(payload.get("privilege"), "权限级别", low, high)
        if level is None:
            level = _DEFAULT_PRIVILEGE[brand]
        basic["user"] = {
            "username": username,
            "password": user_password,
            "level": level,
            "service": ["ssh"],
        }

    if _flag(payload.get("enable_ssh"), default=False):
        basic["enable_ssh"] = True

    mgmt_ip = _ipv4(payload.get("mgmt_ip"), "管理IP")
    mgmt_interface = _interface(payload.get("mgmt_interface"), "管理接口")
    if mgmt_interface and not mgmt_ip:
        raise WebInputError("填写了管理接口时请同时填写管理 IP")
    if mgmt_ip:
        basic["mgmt_interface"] = {
            "interface": mgmt_interface or _DEFAULT_MGMT[brand],
            "ip_address": mgmt_ip,
            "mask": _mask(payload.get("mgmt_mask"), "管理掩码") or "255.255.255.0",
            "gateway": _ipv4(payload.get("gateway"), "网关"),
        }

    vlan = {}
    vlan_id = _integer(payload.get("vlan_id"), "VLAN ID", 1, 4094)
    vlan_name = _token(payload.get("vlan_name"), "VLAN名称", 32)
    if vlan_name and vlan_id is None:
        raise WebInputError("填写了 VLAN 名称时请同时填写 VLAN ID")
    if vlan_id is not None:
        item = {"id": vlan_id}
        if vlan_name:
            item["name"] = vlan_name
        vlan["vlans"] = [item]

    access_interface = _interface(payload.get("access_interface"), "接入端口")
    access_vlan = _integer(payload.get("access_vlan"), "接入VLAN", 1, 4094)
    if access_interface:
        port_vlan = access_vlan if access_vlan is not None else vlan_id
        if port_vlan is None:
            raise WebInputError("填写接入端口时请同时填写接入 VLAN 或上面的 VLAN ID")
        port = {"interface": access_interface, "vlan_id": port_vlan}
        if brand == "h3c":
            port["link_type"] = "access"
        else:
            port["type"] = "access"
        vlan["interfaces"] = [port]
    elif access_vlan is not None and vlan_id is None:
        raise WebInputError("填写了接入 VLAN 时请同时填写接入端口")

    routing = {}
    route_dest = _ipv4(payload.get("route_dest"), "目的网段")
    route_mask = _mask(payload.get("route_mask"), "路由掩码")
    route_nexthop = _ipv4(payload.get("route_nexthop"), "下一跳")
    present = [bool(route_dest), bool(route_mask), bool(route_nexthop)]
    if any(present) and not all(present):
        raise WebInputError("静态路由请同时填写目的网段、掩码和下一跳，或全部留空")
    if all(present):
        if brand == "h3c":
            routing["static"] = [{
                "destination": route_dest,
                "mask": route_mask,
                "next_hop": route_nexthop,
                "preference": 60,
            }]
        else:
            routing["static_routes"] = [{
                "dest_network": route_dest,
                "mask": route_mask,
                "next_hop": route_nexthop,
            }]

    if not basic and not vlan and not routing:
        return {}, {}, {}
    return basic, vlan, routing


def _redact(message, payload):
    text = message
    for key in _PASSWORD_KEYS:
        secret = payload.get(key)
        if isinstance(secret, str) and len(secret) >= 4 and secret in text:
            text = text.replace(secret, "******")
    return text


def _plain(value, field, limit):
    if value is None:
        return ""
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise WebInputError("%s 格式不正确" % field)
    text = str(value)
    if _UNSAFE.search(text) or any(char in text for char in _META):
        raise WebInputError("%s 不能包含换行或特殊字符" % field)
    text = text.strip()
    if len(text) > limit:
        raise WebInputError("%s 过长" % field)
    return text


def _token(value, field, limit):
    text = _plain(value, field, limit)
    if not text:
        return ""
    if not _TOKEN.match(text):
        raise WebInputError("%s 只能包含字母、数字、中文、下划线、点或短横线" % field)
    return text


def _username(value):
    text = _plain(value, "用户名", 32)
    if not text:
        return ""
    if not _USERNAME.match(text):
        raise WebInputError("用户名须以字母开头，只能含字母、数字、下划线或短横线")
    return text


def _secret(value, field):
    text = _plain(value, field, 64)
    if not text:
        return ""
    if not _PASSWORD.match(text):
        raise WebInputError(
            "%s 只能使用字母、数字和 . _ / : @ %% + = , - ，且不能有空格" % field
        )
    return text


def _interface(value, field):
    text = _plain(value, field, 64)
    if not text:
        return ""
    if not _INTERFACE.match(text):
        raise WebInputError("%s 不是可用的接口名" % field)
    return text


def _ipv4(value, field):
    text = _plain(value, field, 15)
    if not text:
        return ""
    parts = text.split(".")
    if len(parts) != 4 or any(not part.isdigit() for part in parts):
        raise WebInputError("%s 不是 IPv4 地址" % field)
    numbers = [int(part) for part in parts]
    if any(number > 255 for number in numbers):
        raise WebInputError("%s 不是 IPv4 地址" % field)
    return ".".join(str(number) for number in numbers)


def _mask(value, field):
    text = _ipv4(value, field)
    if not text:
        return ""
    if _prefix_length(text) is None:
        raise WebInputError("%s 不是连续掩码" % field)
    return text


def _prefix_length(dotted):
    if dotted == "0.0.0.0":
        return 0
    bits = []
    for part in dotted.split("."):
        number = int(part)
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


def _integer(value, field, low, high):
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise WebInputError("%s 不是整数" % field)
    if isinstance(value, int):
        number = value
    elif isinstance(value, float):
        if not value.is_integer():
            raise WebInputError("%s 不是整数" % field)
        number = int(value)
    else:
        text = _plain(value, field, 12)
        if not text:
            return None
        if not re.fullmatch(r"-?\d+", text):
            raise WebInputError("%s 不是整数" % field)
        number = int(text)
    if number < low or number > high:
        raise WebInputError("%s 超出范围 %s-%s" % (field, low, high))
    return number


def _flag(value, default=False):
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool) and value in (0, 1):
        return bool(value)
    text = _plain(value, "SSH开关", 8).lower()
    if text in ("1", "true", "yes", "on"):
        return True
    if text in ("0", "false", "no", "off"):
        return False
    raise WebInputError("SSH 开关只能是 true 或 false")
