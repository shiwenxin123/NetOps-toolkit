#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""本机网页生成接口的冒烟测试。不打开浏览器，也不依赖 PyQt。"""

import contextlib
import io
import json
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from web.server import MAX_BODY_BYTES, BindError, make_server, resolve_bind_host
from web.service import WebInputError, generate_config, list_brands


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
        self.assertTrue(brands["h3c"]["supported"])
        self.assertTrue(brands["zte"]["supported"])
        self.assertTrue(brands["dptech"]["supported"])
        for blocked in ("huawei", "ruijie", "maipu", "dptech-lsw", "zte-rosng", "zte-olt", "h3c-lb"):
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
            generate_config({"brand": "huawei", "hostname": "SW1"})
        self.assertIn("暂未开放", str(caught.exception))
        self.assertIn("python main.py", str(caught.exception))

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
        self.assertIn("华三交换机", page)
        self.assertIn("中兴经典 ZXROS", page)
        self.assertIn("迪普 FW1000", page)
        self.assertIn("网页暂未开放", page)
        self.assertIn("华三负载均衡", page)
        self.assertNotIn("Admin@123", page)

    def test_brands_api(self):
        status, body = self._open("/api/brands")
        payload = json.loads(body.decode("utf-8"))
        self.assertEqual(status, 200)
        self.assertTrue(payload["ok"])
        supported = [item["id"] for item in payload["brands"] if item["supported"]]
        self.assertEqual(supported, ["h3c", "zte", "dptech"])

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


if __name__ == "__main__":
    unittest.main()
