#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""本机 HTTP 服务。默认只绑定 127.0.0.1，不记录请求体。"""

import argparse
import ipaddress
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from web.page import render_page
from web.service import WebInputError, generate_config, list_brands


MAX_BODY_BYTES = 32 * 1024
_PASSWORD_KEYS = ("enable_password", "user_password")
_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
    "Content-Security-Policy": "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'",
}


class BindError(ValueError):
    """监听地址或端口不被接受。"""


class LocalConfigServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class ConfigRequestHandler(BaseHTTPRequestHandler):
    server_version = "NetOpsWeb/0.1"
    protocol_version = "HTTP/1.0"

    def log_request(self, code="-", size="-"):
        path = urlsplit(self.path).path or "/"
        sys.stderr.write("[netops-web] %s %s %s\n" % (self.command, path, code))

    def log_message(self, fmt, *args):
        return

    def do_GET(self):
        path, query = self._locate()
        if path is None:
            return
        if path in ("/", "/index.html"):
            page = render_page(list_brands())
            self._send(200, page.encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/api/brands":
            self._send_json(200, {"ok": True, "brands": list_brands()})
            return
        if path == "/api/health":
            self._send_json(200, {"ok": True, "service": "netops-web"})
            return
        self._send_error(404, "页面不存在")

    def do_POST(self):
        path, query = self._locate()
        if path is None:
            return
        if path != "/api/generate":
            self._send_error(404, "页面不存在")
            return
        payload, mode, error = self._read_payload(query)
        if error:
            self._reply_error(mode, error[0], error[1])
            return
        try:
            result = generate_config(payload)
        except WebInputError as exc:
            self._reply_error(mode, 400, _redact(str(exc), payload), payload)
            return
        except Exception:
            sys.stderr.write("[netops-web] internal error\n")
            self._reply_error(mode, 500, "生成失败", payload)
            return
        if mode == "text":
            self._send(200, result["config"].encode("utf-8"), "text/plain; charset=utf-8")
            return
        if mode == "html":
            page = render_page(list_brands(), values=_public_values(payload), config_text=result["config"])
            self._send(200, page.encode("utf-8"), "text/html; charset=utf-8")
            return
        body = {"ok": True, "brand": result["brand"], "brand_name": result["brand_name"], "config": result["config"]}
        self._send_json(200, body)

    def do_PUT(self):
        self._send_error(405, "只支持 GET 和 POST")

    def do_DELETE(self):
        self._send_error(405, "只支持 GET 和 POST")

    def _locate(self):
        if len(self.path) > 2048:
            self._send_error(414, "地址过长")
            return None, None
        parsed = urlsplit(self.path)
        path = parsed.path or "/"
        if len(path) > 1 and path.endswith("/"):
            path = path[:-1]
        return path, parse_qs(parsed.query, keep_blank_values=False)

    def _read_payload(self, query):
        mode = "json"
        if query.get("format") == ["text"]:
            mode = "text"
        header = self.headers.get("Transfer-Encoding")
        if header:
            return None, mode, (411, "请使用 Content-Length，不支持分块传输")
        length = self.headers.get("Content-Length")
        if length is None:
            return None, mode, (411, "需要 Content-Length")
        try:
            size = int(length)
        except ValueError:
            return None, mode, (400, "Content-Length 无效")
        if size < 0:
            return None, mode, (400, "Content-Length 无效")
        if size > MAX_BODY_BYTES:
            self._drain(min(size, MAX_BODY_BYTES))
            return None, mode, (413, "请求体过大，上限为 32KB")
        if size == 0:
            return None, mode, (400, "请求体为空")
        raw = self.rfile.read(size)
        if len(raw) != size:
            return None, mode, (400, "请求体不完整")
        content_type = (self.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        try:
            payload = _decode_payload(raw, content_type)
        except WebInputError as exc:
            return None, mode, (400, str(exc))
        if mode != "text" and str(payload.get("response") or "") == "html":
            mode = "html"
        return payload, mode, None

    def _drain(self, size):
        remaining = size
        while remaining:
            chunk = self.rfile.read(min(8192, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
        self.close_connection = True

    def _reply_error(self, mode, status, message, payload=None):
        if mode == "html":
            page = render_page(
                list_brands(),
                values=_public_values(payload or {}),
                error=message,
            )
            self._send(status, page.encode("utf-8"), "text/html; charset=utf-8")
            return
        if mode == "text":
            self._send(status, (message + "\n").encode("utf-8"), "text/plain; charset=utf-8")
            return
        self._send_json(status, {"ok": False, "error": message})

    def _send_json(self, status, payload):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send(status, raw, "application/json; charset=utf-8")

    def _send(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for key, value in _SECURITY_HEADERS.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status, message):
        self._send_json(status, {"ok": False, "error": message})


def _decode_payload(raw, content_type):
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise WebInputError("请求体必须是 UTF-8")
    if content_type == "application/json":
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            raise WebInputError("请求不是合法的 JSON")
        if not isinstance(data, dict):
            raise WebInputError("JSON 根必须是对象")
        return data
    if content_type == "application/x-www-form-urlencoded":
        parsed = parse_qs(text, keep_blank_values=True, strict_parsing=False)
        data = {}
        for key, values in parsed.items():
            if len(key) > 64:
                raise WebInputError("表单字段名无效")
            if len(values) != 1:
                raise WebInputError("字段重复")
            data[key] = values[0]
        return data
    if content_type.startswith("multipart/"):
        raise WebInputError("不支持文件上传")
    raise WebInputError("仅支持 JSON 或表单")


def _public_values(payload):
    """回填表单时丢掉口令，避免结果页再次带上密码。"""
    values = {}
    for key, value in payload.items():
        if key in _PASSWORD_KEYS or key == "response":
            continue
        if isinstance(value, bool):
            values[key] = "1" if value else "0"
        elif value is None:
            values[key] = ""
        else:
            values[key] = str(value)
    return values


def _redact(message, payload):
    text = message or ""
    if not isinstance(payload, dict):
        return text
    for key in _PASSWORD_KEYS:
        secret = payload.get(key)
        if isinstance(secret, str) and len(secret) >= 4 and secret in text:
            text = text.replace(secret, "******")
    return text


def resolve_bind_host(host, allow_remote=False):
    """默认只接受回环地址。非回环必须显式允许。"""
    if host is None:
        return "127.0.0.1"
    if not isinstance(host, str):
        raise BindError("监听地址无效")
    text = host.strip()
    if text == "" or text.lower() == "localhost":
        return "127.0.0.1"
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]
    try:
        address = ipaddress.ip_address(text)
    except ValueError:
        raise BindError("监听地址必须是 IP。默认使用 127.0.0.1")
    if address.is_loopback:
        return str(address)
    if allow_remote:
        return str(address)
    raise BindError(
        "默认只监听本机 127.0.0.1。若要在隔离实验环境绑定其他地址，请显式加上 --allow-remote。"
        "不要对公网或不可信网络开放。"
    )


def resolve_port(port):
    try:
        number = int(port)
    except (TypeError, ValueError):
        raise BindError("端口无效")
    if number < 1 or number > 65535:
        raise BindError("端口超出范围 1-65535")
    return number


def make_server(host="127.0.0.1", port=0):
    return LocalConfigServer((host, port), ConfigRequestHandler)


def main(argv=None):
    parser = argparse.ArgumentParser(description="在本机浏览器里生成网络设备配置")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址，默认 127.0.0.1")
    parser.add_argument("--port", default=8765, type=int, help="监听端口，默认 8765")
    parser.add_argument(
        "--allow-remote",
        action="store_true",
        help="允许绑定非回环地址。仅限隔离实验，默认关闭",
    )
    args = parser.parse_args(argv)
    try:
        host = resolve_bind_host(args.host, allow_remote=args.allow_remote)
        port = resolve_port(args.port)
    except BindError as exc:
        sys.stderr.write(str(exc) + "\n")
        return 2
    try:
        httpd = make_server(host, port)
    except OSError as exc:
        sys.stderr.write("无法监听 %s:%s：%s\n" % (host, port, exc.strerror or exc))
        return 1
    bound_host, bound_port = httpd.server_address[:2]
    browse_host = "127.0.0.1" if str(bound_host) in ("0.0.0.0", "::", "::1") else bound_host
    sys.stderr.write("监听 %s:%s\n" % (bound_host, bound_port))
    sys.stderr.write("在浏览器打开 http://%s:%s/\n" % (browse_host, bound_port))
    sys.stderr.write("只生成本机预览文本，不会登录设备。按 Ctrl+C 停止。\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        sys.stderr.write("\n已停止。\n")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
