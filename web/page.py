#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""单页中文表单。不引用外网资源，口令框不预填。"""

from html import escape


DEFAULTS = {
    "brand": "h3c",
    "hostname": "Access-SW-01",
    "username": "",
    "privilege": "3",
    "enable_ssh": "1",
    "mgmt_interface": "Vlan-interface1",
    "mgmt_ip": "192.168.1.1",
    "mgmt_mask": "255.255.255.0",
    "gateway": "192.168.1.254",
    "vlan_id": "10",
    "vlan_name": "Office",
    "access_interface": "",
    "access_vlan": "10",
    "route_dest": "",
    "route_mask": "",
    "route_nexthop": "",
}


def render_page(brands, values=None, config_text="", error=""):
    """返回完整 HTML。values 里的口令不会写回输入框。"""
    current = dict(DEFAULTS)
    if values:
        for key in DEFAULTS:
            if key in values and values[key] is not None:
                current[key] = str(values[key])
    current["enable_password"] = ""
    current["user_password"] = ""
    checked = current.get("enable_ssh", "1").lower() in ("1", "true", "yes", "on")
    supported = [item for item in brands if item["supported"]]
    blocked = [item for item in brands if not item["supported"]]
    parts = [
        "<!DOCTYPE html>",
        "<html lang=\"zh-CN\">",
        "<head>",
        "<meta charset=\"utf-8\">",
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
        "<title>NetOps 配置生成</title>",
        "<style>",
        _CSS,
        "</style>",
        "</head>",
        "<body>",
        "<main>",
        "<header>",
        "<p class=\"eyebrow\">NetOps Toolkit · 本机网页</p>",
        "<h1>生成交换机 / 防火墙配置</h1>",
        "<p class=\"lead\">在这台电脑上填写少量字段，调用已有生成器，得到可以粘贴的配置文本。"
        "默认只监听 127.0.0.1，不登录设备，也不保存口令。</p>",
        "</header>",
        _notice(error),
        "<div class=\"layout\">",
        "<form id=\"form\" method=\"post\" action=\"/api/generate\">",
        "<input type=\"hidden\" name=\"response\" value=\"html\">",
        "<section>",
        "<h2>品牌</h2>",
        "<label for=\"brand\">选择已支持的设备</label>",
        "<select id=\"brand\" name=\"brand\">",
    ]
    for item in supported:
        selected = " selected" if item["id"] == current["brand"] else ""
        parts.append(
            "<option value=\"%s\"%s>%s</option>"
            % (escape(item["id"]), selected, escape(item["name"]))
        )
    parts.extend([
        "</select>",
        "<p id=\"brand-note\" class=\"hint\"></p>",
        "<h3>网页暂未开放</h3>",
        "<ul class=\"blocked\">",
    ])
    for item in blocked:
        parts.append(
            "<li><span>%s</span> %s</li>"
            % (escape(item["name"]), escape(item["note"]))
        )
    parts.extend([
        "</ul>",
        "</section>",
        "<section>",
        "<h2>设备与登录</h2>",
        _field("hostname", "主机名", current["hostname"], "例如 Access-SW-01"),
        _field("enable_password", "管理密码", "", "留空则不写入口令", password=True),
        _field("username", "用户名", current["username"], "例如 netops，留空则不写用户"),
        _field("user_password", "用户密码", "", "与用户名同时填写", password=True),
        _field("privilege", "权限级别", current["privilege"], "华三 0-3，中兴/迪普 0-15"),
        "<label class=\"check\"><input type=\"checkbox\" id=\"enable_ssh\" name=\"enable_ssh\" value=\"1\"%s> 开启 SSH</label>"
        % (" checked" if checked else ""),
        "</section>",
        "<section>",
        "<h2>管理地址</h2>",
        _field("mgmt_interface", "管理接口", current["mgmt_interface"], ""),
        _field("mgmt_ip", "管理 IP", current["mgmt_ip"], "192.168.1.1"),
        _field("mgmt_mask", "掩码", current["mgmt_mask"], "255.255.255.0"),
        _field("gateway", "网关", current["gateway"], "可留空"),
        "</section>",
        "<section>",
        "<h2>VLAN 与接入端口</h2>",
        _field("vlan_id", "VLAN ID", current["vlan_id"], "1-4094，可留空"),
        _field("vlan_name", "VLAN 名称", current["vlan_name"], "可留空"),
        _field("access_interface", "接入端口", current["access_interface"], "按品牌提示填写"),
        _field("access_vlan", "接入 VLAN", current["access_vlan"], "留空则使用上面的 VLAN ID"),
        "</section>",
        "<section>",
        "<h2>静态路由（可选）</h2>",
        _field("route_dest", "目的网段", current["route_dest"], "例如 10.2.0.0"),
        _field("route_mask", "掩码", current["route_mask"], "点分掩码，例如 255.255.0.0"),
        _field("route_nexthop", "下一跳", current["route_nexthop"], "例如 10.1.1.2"),
        "</section>",
        "<div class=\"actions\">",
        "<button type=\"submit\">生成配置</button>",
        "<button type=\"button\" id=\"copy\" class=\"secondary\">复制结果</button>",
        "</div>",
        "<p class=\"hint\">口令只出现在生成结果里，服务器日志不记录。示例地址是文档用的私网地址，不要填真实口令后再把页面外传。</p>",
        "</form>",
        "<section class=\"output\">",
        "<h2>配置文本</h2>",
        "<textarea id=\"output\" readonly spellcheck=\"false\">",
        escape(config_text or ""),
        "</textarea>",
        "</section>",
        "</div>",
        "<details>",
        "<summary>接口说明</summary>",
        "<p>POST /api/generate ，JSON 或表单都可以。加 <code>?format=text</code> 得到纯文本。GET /api/brands 查看哪些品牌已开放。</p>",
        "<pre>curl -s http://127.0.0.1:8765/api/generate \\\n"
        "  -H 'Content-Type: application/json' \\\n"
        "  -d '{\"brand\":\"h3c\",\"hostname\":\"Access-SW-01\",\"mgmt_ip\":\"192.168.1.1\"}'</pre>",
        "</details>",
        "</main>",
        "<script>",
        _SCRIPT,
        "</script>",
        "</body>",
        "</html>",
    ])
    return "\n".join(parts)


def _field(name, label, value, placeholder, password=False):
    kind = "password" if password else "text"
    extra = " autocomplete=\"off\"" if password else ""
    return (
        "<label for=\"%s\">%s</label>"
        "<input id=\"%s\" name=\"%s\" type=\"%s\" value=\"%s\" placeholder=\"%s\"%s>"
        % (
            escape(name),
            escape(label),
            escape(name),
            escape(name),
            kind,
            escape(value, quote=True),
            escape(placeholder, quote=True),
            extra,
        )
    )


def _notice(error):
    if not error:
        return ""
    return "<p class=\"error\" role=\"alert\">%s</p>" % escape(error)


_CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  background: #f4f6f8;
  color: #1c2430;
}
main { max-width: 1100px; margin: 0 auto; padding: 28px 20px 48px; }
header { margin-bottom: 18px; }
.eyebrow { margin: 0 0 6px; color: #3d6b8c; font-size: 13px; letter-spacing: 0.04em; }
h1 { margin: 0 0 8px; font-size: 28px; }
h2 { margin: 0 0 12px; font-size: 16px; }
h3 { margin: 14px 0 6px; font-size: 13px; color: #66707c; }
.lead, .hint { color: #4c5866; line-height: 1.55; }
.layout { display: grid; grid-template-columns: minmax(280px, 420px) 1fr; gap: 20px; align-items: start; }
form, .output, details { background: #fff; border: 1px solid #d9e0e7; border-radius: 12px; padding: 16px 16px 18px; }
form section + section { margin-top: 18px; padding-top: 14px; border-top: 1px solid #eef1f4; }
label { display: block; margin: 10px 0 4px; font-size: 13px; }
input, select, textarea {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #c5ced6;
  border-radius: 8px;
  font: inherit;
  background: #fff;
}
textarea { min-height: 640px; font-family: "Cascadia Code", "Sarasa Mono SC", Consolas, monospace; font-size: 13px; line-height: 1.45; }
label.check { display: flex; align-items: center; gap: 8px; margin-top: 12px; }
label.check input { width: auto; }
.actions { display: flex; gap: 8px; margin-top: 16px; }
button {
  border: 0;
  border-radius: 8px;
  padding: 10px 16px;
  background: #1f6f8b;
  color: #fff;
  font: inherit;
  cursor: pointer;
}
button.secondary { background: #e8eef2; color: #1c2430; }
.blocked { margin: 0; padding-left: 18px; color: #66707c; font-size: 13px; }
.blocked span { color: #1c2430; }
.error { background: #fff4f2; border: 1px solid #f0c2ba; color: #8a2b1f; padding: 10px 12px; border-radius: 8px; }
details { margin-top: 16px; }
pre { overflow: auto; background: #f7f9fb; padding: 12px; border-radius: 8px; }
@media (max-width: 860px) {
  .layout { grid-template-columns: 1fr; }
  textarea { min-height: 320px; }
}
"""

_SCRIPT = """
var HINTS = {
  h3c: {
    mgmt: "Vlan-interface1",
    access: "GigabitEthernet1/0/1",
    privilege: "3",
    note: "华三 Comware 交换机。权限级别请填 0-3。管理口示例 Vlan-interface1，接入端口示例 GigabitEthernet1/0/1。"
  },
  zte: {
    mgmt: "Vlanif1",
    access: "gei_1/1",
    privilege: "15",
    note: "中兴经典 ZXROS（5200/5900/8900）。Vlanif1 生成时写成 vlan 1。接入端口示例 gei_1/1。不是 ROSNG，也不是 OLT。"
  },
  dptech: {
    mgmt: "Vlanif1",
    access: "gige0_1",
    privilege: "15",
    note: "迪普 FW1000。主机名最长 20 位且不要用中文。管理口 Vlanif1 会写成 vlan-if 1，接入端口示例 gige0_1。不是 LSW。"
  }
};
var DEFAULT_MGMT = ["Vlan-interface1", "Vlanif1", ""];
var DEFAULT_PRIV = ["3", "15", ""];

function applyHint(resetDefaults) {
  var brand = document.getElementById("brand").value;
  var hint = HINTS[brand];
  if (!hint) return;
  document.getElementById("brand-note").textContent = hint.note;
  var mgmt = document.getElementById("mgmt_interface");
  var privilege = document.getElementById("privilege");
  var access = document.getElementById("access_interface");
  access.placeholder = hint.access;
  if (resetDefaults && DEFAULT_MGMT.indexOf(mgmt.value) >= 0) mgmt.value = hint.mgmt;
  if (resetDefaults && DEFAULT_PRIV.indexOf(privilege.value) >= 0) privilege.value = hint.privilege;
}

document.getElementById("brand").addEventListener("change", function () {
  applyHint(true);
});
applyHint(false);

document.getElementById("copy").addEventListener("click", function () {
  var output = document.getElementById("output");
  var text = output.value;
  if (!text) return;
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).catch(function () { output.select(); });
  } else {
    output.select();
  }
});

document.getElementById("form").addEventListener("submit", function (event) {
  if (!window.fetch) return;
  event.preventDefault();
  var form = event.target;
  var data = {
    brand: form.brand.value,
    hostname: form.hostname.value,
    enable_password: form.enable_password.value,
    username: form.username.value,
    user_password: form.user_password.value,
    privilege: form.privilege.value,
    enable_ssh: form.enable_ssh.checked,
    mgmt_interface: form.mgmt_interface.value,
    mgmt_ip: form.mgmt_ip.value,
    mgmt_mask: form.mgmt_mask.value,
    gateway: form.gateway.value,
    vlan_id: form.vlan_id.value,
    vlan_name: form.vlan_name.value,
    access_interface: form.access_interface.value,
    access_vlan: form.access_vlan.value,
    route_dest: form.route_dest.value,
    route_mask: form.route_mask.value,
    route_nexthop: form.route_nexthop.value
  };
  var output = document.getElementById("output");
  output.value = "正在生成…";
  fetch("/api/generate", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data)
  }).then(function (response) {
    return response.json().then(function (body) {
      return {ok: response.ok, body: body};
    });
  }).then(function (result) {
    if (!result.ok || !result.body.ok) {
      output.value = "";
      window.alert(result.body.error || "生成失败");
      return;
    }
    output.value = result.body.config;
    form.enable_password.value = "";
    form.user_password.value = "";
  }).catch(function () {
    output.value = "";
    window.alert("无法连接本机生成服务");
  });
});
"""
