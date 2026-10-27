#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""本机网页生成接口的测试。HTTP 部分不打开浏览器。华为一致性测试使用离屏 Qt。"""

import contextlib
import io
import json
import os
import re
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from modules.basic_config import BasicConfigGenerator
from modules.maipu_config import (
    MaipuBasicGenerator,
    MaipuRoutingGenerator,
    MaipuVLANGenerator,
)
from modules.routing_config import RoutingConfigGenerator
from modules.ruijie_config import (
    RuijieBasicGenerator,
    RuijieRoutingGenerator,
    RuijieVLANGenerator,
)
from modules.vlan_config import VLANConfigGenerator
from web.server import MAX_BODY_BYTES, BindError, make_server, resolve_bind_host
from web.service import WebInputError, generate_config, list_brands


def _normalize_stamp(text):
    return re.sub(r"# 生成时间: .+", "# 生成时间: TIMESTAMP", text)


def _huawei_sections(payload):
    """桌面基础页会交给生成器的同一组字段。service 键生成器不读取。"""
    return (
        {
            "hostname": payload["hostname"],
            "password": {"value": payload["enable_password"], "encrypted": False},
            "user": {
                "username": payload["username"],
                "password": payload["user_password"],
                "level": payload["privilege"],
                "service": ["ssh"],
            },
            "enable_ssh": True,
            "mgmt_interface": {
                "interface": payload["mgmt_interface"],
                "ip_address": payload["mgmt_ip"],
                "mask": payload["mgmt_mask"],
                "gateway": payload["gateway"],
            },
        },
        {
            "vlans": [{"id": payload["vlan_id"], "name": payload["vlan_name"]}],
            "interfaces": [{
                "interface": payload["access_interface"],
                "vlan_id": payload["access_vlan"],
                "type": "access",
            }],
        },
        {
            "static_routes": [{
                "dest_network": payload["route_dest"],
                "mask": payload["route_mask"],
                "next_hop": payload["route_nexthop"],
                "preference": 60,
            }],
        },
    )


def _cisco_like_sections(payload):
    basic, vlan, routing = _huawei_sections(payload)
    route = dict(routing["static_routes"][0])
    route.pop("preference")
    return basic, vlan, {"static_routes": [route]}


def _stitch_vendor(basic_text, vlan_text, iface_text, route_text):
    body = basic_text.rstrip("\n")
    if body.endswith("\nend"):
        body = body[:-4]
    chunks = [
        body,
        vlan_text.rstrip("\n"),
        iface_text.rstrip("\n"),
        route_text.rstrip("\n"),
    ]
    return "\n".join(chunks) + "\nend\n"


def _sample(brand, **overrides):
    payload = {
        "brand": brand,
        "hostname": "Access-SW-01",
        "enable_password": "LabOnly1",
        "username": "netops",
        "user_password": "LabOnly1",
        "enable_ssh": True,
        "mgmt_ip": "192.168.1.1",
        "mgmt_mask": "255.255.255.0",
        "gateway": "192.168.1.254",
        "vlan_id": 10,
        "vlan_name": "Office",
        "access_vlan": 10,
        "route_dest": "10.2.0.0",
        "route_mask": "255.255.0.0",
        "route_nexthop": "10.1.1.2",
    }
    if brand == "h3c":
        payload["privilege"] = 3
        payload["mgmt_interface"] = "Vlan-interface1"
        payload["access_interface"] = "GigabitEthernet1/0/1"
    elif brand == "huawei":
        payload["privilege"] = 15
        payload["mgmt_interface"] = "Vlanif1"
        payload["access_interface"] = "GigabitEthernet0/0/1"
    elif brand == "ruijie":
        payload["privilege"] = 15
        payload["mgmt_interface"] = "vlan 1"
        payload["access_interface"] = "GigabitEthernet 0/1"
    elif brand == "maipu":
        payload["privilege"] = 15
        payload["mgmt_interface"] = "vlan 1"
        payload["access_interface"] = "gigabitethernet 0/1"
    elif brand == "zte":
        payload["privilege"] = 15
        payload["mgmt_interface"] = "Vlanif1"
        payload["access_interface"] = "gei_1/1"
    elif brand == "dptech":
        payload["privilege"] = 15
        payload["hostname"] = "DP-FW-01"
        payload["mgmt_interface"] = "Vlanif1"
        payload["access_interface"] = "gige0_1"
    payload.update(overrides)
    return payload


class GenerateServiceTests(unittest.TestCase):
    def test_brand_list_marks_desktop_only_models(self):
        brands = {item["id"]: item for item in list_brands()}
        for opened in ("huawei", "h3c", "ruijie", "maipu", "zte", "dptech"):
            self.assertTrue(brands[opened]["supported"])
        for blocked in ("dptech-lsw", "zte-rosng", "zte-olt", "h3c-lb"):
            self.assertFalse(brands[blocked]["supported"])
            self.assertIn("暂未开放", brands[blocked]["note"])

    def test_h3c_uses_comware_generator(self):
        text = generate_config(_sample("h3c"))["config"]
        self.assertIn("sysname Access-SW-01", text)
        self.assertIn("super password simple LabOnly1", text)
        self.assertIn("ssh server enable", text)
        self.assertNotIn("stelnet server enable", text)
        self.assertIn("interface Vlan-interface1", text)
        self.assertIn("port link-type access", text)
        self.assertIn("port access vlan 10", text)
        self.assertIn("ip route-static 10.2.0.0 255.255.0.0 10.1.1.2 preference 60", text)
        self.assertIn("vlan 10", text)
        self.assertIn("name Office", text)

    def test_zte_uses_classic_zxros_generator(self):
        text = generate_config(_sample("zte"))["config"]
        self.assertIn("configure terminal", text)
        self.assertIn("hostname Access-SW-01", text)
        self.assertIn("enable secret 0 LabOnly1", text)
        self.assertIn("username netops password LabOnly1 privilege 15", text)
        self.assertIn("ssh server enable", text)
        self.assertIn("interface vlan 1", text)
        self.assertIn("switchport access vlan 10", text)
        self.assertIn("ip route 10.2.0.0 255.255.0.0 10.1.1.2", text)
        self.assertNotIn("sysname ", text)

    def test_dptech_uses_fw1000_generator(self):
        text = generate_config(_sample("dptech"))["config"]
        self.assertIn("\nconf-mode\n", text)
        self.assertIn("sysname DP-FW-01", text)
        self.assertIn("password conf-mode LabOnly1", text)
        self.assertIn("local-user netops password plain-text-password LabOnly1", text)
        self.assertIn("ssh enable", text)
        self.assertIn("interface vlan-if 1", text)
        self.assertIn("ip address 192.168.1.1/24", text)
        self.assertIn("switchport access vlan 10", text)
        self.assertIn("ip route 10.2.0.0/16 10.1.1.2", text)
        self.assertNotIn("configure terminal", text)

    def test_unsupported_brand_is_explicit(self):
        with self.assertRaises(WebInputError) as caught:
            generate_config({"brand": "h3c-lb", "hostname": "SW1"})
        self.assertIn("暂未开放", str(caught.exception))
        self.assertIn("python main.py", str(caught.exception))
        self.assertIn("华为", str(caught.exception))

    def test_newline_is_rejected_before_generation(self):
        with self.assertRaises(WebInputError):
            generate_config({"brand": "h3c", "hostname": "SW1\nsystem-view"})

    def test_partial_route_is_rejected(self):
        with self.assertRaises(WebInputError):
            generate_config({"brand": "zte", "route_dest": "10.2.0.0"})

    def test_empty_request_is_rejected(self):
        with self.assertRaises(WebInputError):
            generate_config({"brand": "h3c"})

    def test_h3c_privilege_stays_in_comware_range(self):
        with self.assertRaises(WebInputError) as caught:
            generate_config(_sample("h3c", privilege=15))
        self.assertIn("0-3", str(caught.exception))

    def test_loopback_is_the_default_bind(self):
        self.assertEqual(resolve_bind_host(None), "127.0.0.1")
        self.assertEqual(resolve_bind_host("localhost"), "127.0.0.1")
        self.assertEqual(resolve_bind_host("::1"), "::1")
        with self.assertRaises(BindError):
            resolve_bind_host("0.0.0.0")
        self.assertEqual(resolve_bind_host("0.0.0.0", allow_remote=True), "0.0.0.0")

    def test_huawei_matches_desktop_generators(self):
        payload = _sample("huawei")
        web = generate_config(payload)["config"]
        basic, vlan, routing = _huawei_sections(payload)
        expected = (
            "#\n# 华为交换机配置脚本\n# 生成时间: TIMESTAMP\n#\n\n"
            + "\n".join([
                BasicConfigGenerator.generate_basic_all(basic),
                VLANConfigGenerator.generate_vlan_all(vlan),
                RoutingConfigGenerator.generate_route_all({"static_routes": routing["static_routes"]}),
            ])
        )
        self.assertEqual(_normalize_stamp(web), expected)
        self.assertIn("sysname Access-SW-01", web)
        self.assertIn("stelnet server enable", web)
        self.assertIn("interface Vlanif1", web)
        self.assertIn("port link-type access", web)
        self.assertIn("port default vlan 10", web)
        self.assertIn("ip route-static 10.2.0.0 255.255.0.0 10.1.1.2 preference 60", web)
        self.assertIn("local-user netops privilege level 15", web)
        self.assertNotIn("hostname Access-SW-01", web)
        self.assertNotIn("switchport access vlan", web)

    def test_ruijie_matches_ruijie_generator(self):
        payload = _sample("ruijie")
        web = generate_config(payload)["config"]
        basic, vlan, routing = _cisco_like_sections(payload)
        route = routing["static_routes"][0]
        iface = vlan["interfaces"][0]
        expected = _stitch_vendor(
            RuijieBasicGenerator.generate_basic_all(basic),
            RuijieVLANGenerator.generate_vlans(vlan["vlans"]),
            RuijieVLANGenerator.generate_interface(
                iface["interface"], iface["type"], iface["vlan_id"]
            ),
            RuijieRoutingGenerator.generate_static_routes([{
                "dest": route["dest_network"],
                "mask": route["mask"],
                "nexthop": route["next_hop"],
            }]),
        )
        self.assertEqual(web, expected)
        self.assertIn("hostname Access-SW-01", web)
        self.assertIn("enable password LabOnly1", web)
        self.assertIn("username netops privilege 15 password LabOnly1", web)
        self.assertIn("ip default-gateway 192.168.1.254", web)
        self.assertIn("switchport access vlan 10", web)
        self.assertIn("ip route 10.2.0.0 255.255.0.0 10.1.1.2 60", web)
        self.assertIn("line vty 0 4", web)
        self.assertNotIn("sysname ", web)
        self.assertNotIn("stelnet", web)
        self.assertTrue(web.rstrip().endswith("end"))

    def test_maipu_matches_maipu_generator(self):
        payload = _sample("maipu")
        web = generate_config(payload)["config"]
        basic, vlan, routing = _cisco_like_sections(payload)
        route = routing["static_routes"][0]
        iface = vlan["interfaces"][0]
        expected = _stitch_vendor(
            MaipuBasicGenerator.generate_basic_all(basic),
            MaipuVLANGenerator.generate_vlans(vlan["vlans"]),
            MaipuVLANGenerator.generate_interface(
                iface["interface"], iface["type"], iface["vlan_id"]
            ),
            MaipuRoutingGenerator.generate_static_routes([{
                "dest": route["dest_network"],
                "mask": route["mask"],
                "nexthop": route["next_hop"],
            }]),
        )
        self.assertEqual(web, expected)
        self.assertIn("hostname Access-SW-01", web)
        self.assertIn("ip route 0.0.0.0 0.0.0.0 192.168.1.254", web)
        self.assertIn("switchport access vlan 10", web)
        self.assertIn("ip route 10.2.0.0 255.255.0.0 10.1.1.2 60", web)
        self.assertIn("line vty 0 15", web)
        self.assertNotIn("ip default-gateway", web)
        self.assertNotIn("sysname ", web)
        self.assertNotIn("line vty 0 4", web)

    def test_new_brands_reject_bad_vlan_ip_and_interface(self):
        with self.assertRaises(WebInputError) as vlan_error:
            generate_config(_sample("huawei", vlan_id=4095))
        self.assertIn("VLAN ID", str(vlan_error.exception))
        self.assertIn("1-4094", str(vlan_error.exception))

        with self.assertRaises(WebInputError) as ip_error:
            generate_config(_sample("ruijie", mgmt_ip="192.168.1.999"))
        self.assertIn("不是 IPv4 地址", str(ip_error.exception))

        with self.assertRaises(WebInputError) as iface_error:
            generate_config(_sample("maipu", access_interface="gi0/1;shutdown"))
        self.assertIn("特殊字符", str(iface_error.exception))

        with self.assertRaises(WebInputError) as level_error:
            generate_config(_sample("huawei", privilege=16))
        self.assertIn("权限级别", str(level_error.exception))
        self.assertIn("0-15", str(level_error.exception))

    def test_markup_in_hostname_is_rejected(self):
        with self.assertRaises(WebInputError) as caught:
            generate_config({"brand": "ruijie", "hostname": "SW<script>"})
        message = str(caught.exception)
        self.assertIn("特殊字符", message)
        self.assertNotIn("<script>", message)

    def test_sources_do_not_shell_out(self):
        root = Path(__file__).resolve().parents[1] / "web"
        text = "\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.py"))
        self.assertNotIn("subprocess", text)
        self.assertNotIn("os.system", text)
        self.assertNotIn("Popen", text)


class GenerateHttpTests(unittest.TestCase):
    def setUp(self):
        self.httpd = make_server("127.0.0.1", 0)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=5)

    def _open(self, path, data=None, content_type=None):
        headers = {}
        body = None
        if data is not None:
            body = data if isinstance(data, bytes) else data.encode("utf-8")
            headers["Content-Type"] = content_type or "application/json"
            headers["Content-Length"] = str(len(body))
        request = urllib.request.Request(
            "http://127.0.0.1:%s%s" % (self.port, path),
            data=body,
            method="POST" if data is not None else "GET",
            headers=headers,
        )
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read()

    def test_home_page_lists_supported_and_blocked_brands(self):
        status, body = self._open("/")
        page = body.decode("utf-8")
        self.assertEqual(status, 200)
        self.assertIn("华为 (Huawei)", page)
        self.assertIn("华三交换机", page)
        self.assertIn("锐捷 (Ruijie)", page)
        self.assertIn("迈普 (Maipu)", page)
        self.assertIn("中兴经典 ZXROS", page)
        self.assertIn("迪普 FW1000", page)
        self.assertIn("网页暂未开放", page)
        self.assertIn("华三负载均衡", page)
        self.assertNotIn("Admin@123", page)
        self.assertIn('<option value="huawei"', page)
        self.assertNotIn("华为 (Huawei)</span>", page)

    def test_brands_api(self):
        status, body = self._open("/api/brands")
        payload = json.loads(body.decode("utf-8"))
        self.assertEqual(status, 200)
        self.assertTrue(payload["ok"])
        supported = [item["id"] for item in payload["brands"] if item["supported"]]
        self.assertEqual(supported, ["huawei", "h3c", "ruijie", "maipu", "zte", "dptech"])

    def test_json_generate_and_text_format(self):
        status, body = self._open("/api/generate", json.dumps(_sample("zte")))
        payload = json.loads(body.decode("utf-8"))
        self.assertEqual(status, 200)
        self.assertTrue(payload["ok"])
        self.assertIn("configure terminal", payload["config"])

        status, body = self._open(
            "/api/generate?format=text",
            json.dumps({"brand": "h3c", "hostname": "Edge-SW-01"}),
        )
        text = body.decode("utf-8")
        self.assertEqual(status, 200)
        self.assertIn("sysname Edge-SW-01", text)
        self.assertFalse(text.startswith("{"))

    def test_form_post_returns_html_without_echoing_password_field(self):
        form = urllib.parse.urlencode({
            "response": "html",
            "brand": "h3c",
            "hostname": "Access-SW-01",
            "enable_password": "LabOnly1",
            "enable_ssh": "1",
        })
        status, body = self._open(
            "/api/generate",
            form,
            content_type="application/x-www-form-urlencoded",
        )
        page = body.decode("utf-8")
        self.assertEqual(status, 200)
        self.assertIn("super password simple LabOnly1", page)
        self.assertIn('id="enable_password"', page)
        self.assertNotIn('value="LabOnly1"', page)

    def test_log_does_not_contain_password(self):
        secret = "LabOnly1"
        buffer = io.StringIO()
        with contextlib.redirect_stderr(buffer):
            status, body = self._open("/api/generate", json.dumps(_sample("dptech")))
        payload = json.loads(body.decode("utf-8"))
        self.assertEqual(status, 200)
        self.assertIn(secret, payload["config"])
        logged = buffer.getvalue()
        self.assertNotIn(secret, logged)
        self.assertIn("POST /api/generate 200", logged)

    def test_oversized_body_is_rejected(self):
        blob = b'{"brand":"h3c","hostname":"A","pad":"' + (b"B" * (MAX_BODY_BYTES + 8)) + b'"}'
        status, body = self._open("/api/generate", blob)
        payload = json.loads(body.decode("utf-8"))
        self.assertEqual(status, 413)
        self.assertIn("32KB", payload["error"])
        self.assertNotIn("config", payload)

    def test_unknown_path(self):
        status, body = self._open("/api/shell")
        self.assertEqual(status, 404)
        self.assertFalse(json.loads(body.decode("utf-8"))["ok"])

    def test_new_brands_generate_over_http(self):
        expectations = {
            "huawei": "stelnet server enable",
            "ruijie": "switchport access vlan 10",
            "maipu": "line vty 0 15",
        }
        for brand, marker in expectations.items():
            status, body = self._open("/api/generate", json.dumps(_sample(brand)))
            payload = json.loads(body.decode("utf-8"))
            self.assertEqual(status, 200, payload)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["brand"], brand)
            self.assertIn(marker, payload["config"])
            self.assertEqual(
                _normalize_stamp(payload["config"]),
                _normalize_stamp(generate_config(_sample(brand))["config"]),
            )

    def test_rejected_hostname_is_escaped_in_html(self):
        form = urllib.parse.urlencode({
            "response": "html",
            "brand": "huawei",
            "hostname": "A<b>c",
        })
        status, body = self._open(
            "/api/generate",
            form,
            content_type="application/x-www-form-urlencoded",
        )
        page = body.decode("utf-8")
        self.assertEqual(status, 400)
        self.assertIn("特殊字符", page)
        self.assertIn("A&lt;b&gt;c", page)
        self.assertNotIn("A<b>c", page)


class HuaweiDesktopParityTests(unittest.TestCase):
    """同一组字段下，网页华为脚本与桌面 compose_config 一致（时间戳除外）。"""

    @classmethod
    def setUpClass(cls):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt5.QtWidgets import QApplication
        from gui.main_window import MainWindow

        cls.app = QApplication.instance() or QApplication([])
        cls.MainWindow = MainWindow

    def setUp(self):
        self.window = self.MainWindow()

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()

    def test_same_fields_match_desktop_compose(self):
        payload = _sample("huawei")
        basic = self.window.tabs["basic"]
        basic.hostname_input.setText(payload["hostname"])
        basic.password_input.setText(payload["enable_password"])
        basic.encrypted_checkbox.setChecked(False)
        basic.username_input.setText(payload["username"])
        basic.user_password_input.setText(payload["user_password"])
        basic.user_encrypted.setChecked(False)
        basic.privilege_level.setValue(payload["privilege"])
        basic.enable_ssh.setChecked(True)
        basic.enable_telnet.setChecked(False)
        basic.log_enable.setChecked(False)
        basic.mgmt_interface.setText(payload["mgmt_interface"])
        basic.mgmt_ip.setText(payload["mgmt_ip"])
        basic.mgmt_mask.setText(payload["mgmt_mask"])
        basic.mgmt_gateway.setText(payload["gateway"])

        vlan = self.window.tabs["vlan"]
        vlan.vlan_id_input.setValue(payload["vlan_id"])
        vlan.vlan_name_input.setText(payload["vlan_name"])
        vlan.add_vlan()
        vlan.interface_input.setText(payload["access_interface"])
        vlan.vlan_type_combo.setCurrentText("access")
        vlan.port_vlan_id.setValue(payload["access_vlan"])
        vlan.add_interface()

        routing = self.window.tabs["routing"]
        routing.route_dest.setText(payload["route_dest"])
        routing.route_mask.setText(payload["route_mask"])
        routing.route_nexthop.setText(payload["route_nexthop"])
        routing.route_preference.setValue(60)
        routing.add_static_route()

        self.window.tabs["interface"].lldp_enable.setChecked(False)
        self.window.tabs["interface"].poe_global_enable.setChecked(False)

        desktop = self.window.compose_config()
        web = generate_config(payload)["config"]
        self.assertEqual(_normalize_stamp(desktop), _normalize_stamp(web))


if __name__ == "__main__":
    unittest.main()
