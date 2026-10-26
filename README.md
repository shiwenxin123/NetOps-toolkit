# NetOps Toolkit v4.0 - 网络运维工具集

一个功能强大、现代化界面的**多品牌网络设备配置生成工具**，支持**华为/H3C/锐捷/迈普/中兴交换机**、**中兴 ROSNG**、**中兴 OLT**、**迪普 FW1000 防火墙**和**华三 SecPath 负载均衡**，内置**11+网络工具**，基于 Python + PyQt5 开发。

## v4.0 新特性

### 🎨 科技感UI设计
- **深色渐变主题** - 紫蓝渐变背景，赛博朋克风格
- **发光边框效果** - 霓虹蓝色高亮，科技感十足
- **窗口自适应** - 自动适配不同屏幕尺寸
- **现代化控件** - 渐变按钮、玻璃态卡片

### 🔄 多品牌设备支持
- **华为 (Huawei)** - 248条命令 + 8个配置案例
- **华三 (H3C)** - 239条命令 + 9个配置案例  
- **锐捷 (Ruijie)** - 284条命令 + 10个配置案例
- **迈普 (Maipu)** - 229条命令 + 8个配置案例
- **中兴 (ZTE)** - ZXR10 5200/5900/8900 经典 ZXROS 配置生成（基础、VLAN、路由、ACL、聚合）
- **中兴 ROSNG** - ZXR10 5960/9900 新一代 ROSNG 配置生成（VLAN、Access/Trunk、SSH、smartgroup、静态路由）
- **中兴 OLT** - ZXA10 C300/C320 与 C600 配置生成（主机名、管理地址、上联 VLAN、SSH、静态路由；ONU 注册只留注释）
- **迪普 FW1000 (DPtech)** - 防火墙 Conplat 配置生成（管理口、VLAN、安全域、包过滤、bond）
- **迪普 LSW (DPtech)** - LSW3600/LSW5600 交换机 Conplat 配置生成（VLAN、Access/Trunk、SSH、bond）
- **华三负载均衡 (H3C SecPath)** - 服务器负载均衡配置生成（实服务器、实服务组、虚服务器、ICMP 健康检查、静态路由）
- 一键切换设备类型。选择「中兴」后，生成结果使用经典 ZXROS。选择「中兴 ROSNG」后，生成结果使用 `switchvlan-configuration`、`system-user` 和 `gei-0/1/1/1`。选择「迪普 FW1000」后，生成结果使用 `conf-mode`、`gige0_1` 和 `security-policy`。选择「迪普 LSW」后，生成结果是交换机脚本：`switchport`、`ssh enable`、`bond`，没有安全策略。选择「中兴 OLT (C300/C600)」后，生成结果是 ZXAN 脚本：`hostname`、`interface vlan mng1` 或 `interface vlan100`、`switchport vlan ... tag`。C300 与 C600 的接口名不要混在一份脚本里。选择「华三负载均衡 (SecPath)」后，生成结果是 Comware 负载均衡脚本：`system-view`、`real-server`、`server-farm`、`virtual-server`，不是交换机的 `switchport`

### 🧰 内置网络工具箱
- **子网计算器** - IP子网计算、子网划分、IP范围转CIDR
- **Ping测试** - 单主机/批量Ping、Ping扫描
- **端口扫描** - 常用端口/全端口扫描、快速端口测试
- **路由跟踪** - Traceroute路由路径追踪
- **DNS/Whois** - DNS查询、反向DNS、Whois域名信息
- **网络信息** - 本机IP、公网IP查询
- **IP转换** - 十进制/十六进制/二进制转换
- **配置命令手册** - 华为/H3C/锐捷/迈普/中兴/中兴 ROSNG/中兴 OLT/迪普 FW1000/迪普 LSW/华三负载均衡 配置命令速查、配置案例
- **配置比较工具** - 配置差异对比、华为/H3C命令转换
- **配置导入导出** - JSON/文本格式导入导出、配置解析

## 功能特性

### 配置模板功能
- 华为/H3C预设场景模板
- 模板加载自动填充配置项
- 可根据实际需求调整模板参数

### 配置验证功能
- IP地址格式验证
- 子网掩码有效性检查
- VLAN ID范围验证 (1-4094)
- 主机名格式验证
- 密码强度验证

### 基础配置
- 主机名配置
- 管理密码设置（明文/密文）
- 管理接口配置（IP地址、子网掩码、网关）
- SSH/Telnet服务配置
- 用户管理
- NTP时间同步
- SNMP配置
- 日志配置

### VLAN配置
- VLAN批量创建
- 接口VLAN配置（Access、Trunk、Hybrid）
- VLANIF接口配置
- STP配置

### 路由配置
- 静态路由配置
- 默认路由配置
- OSPF动态路由配置
- BGP配置

### 安全配置
- ACL配置
- 端口安全配置
- MAC地址绑定
- ARP防护配置
- 802.1X认证

### 接口配置
- 端口聚合 Eth-Trunk
- LLDP配置
- PoE配置
- 速率限制

## 安装依赖

```bash
pip install PyQt5
```

## 运行程序

**方式一：运行Python脚本**
```bash
cd netops_toolkit
python main.py
```

**方式二：双击批处理文件**
```bash
run.bat
```

**方式三：本机浏览器（第一版）**

桌面版不用改。如果只想在浏览器里生成一份可粘贴的配置，在仓库根目录执行：

```bash
python web_server.py
```

或：

```bash
python -m web
```

然后打开 http://127.0.0.1:8765/ 。默认端口是 8765，可以用 `python web_server.py --port 9000` 更换。进程默认只监听 `127.0.0.1`，不会对局域网或公网开放。

网页第一版直接调用现有生成器，目前可以生成：

- **华三交换机 (H3C)**：`modules/h3c_config.py`
- **中兴经典 ZXROS**：`modules/zte_config.py`（5200/5900/8900，不是 ROSNG，也不是 OLT）
- **迪普 FW1000**：`modules/dptech_config.py`（不是 LSW 交换机）

华为、锐捷、迈普、迪普 LSW、中兴 ROSNG、中兴 OLT、华三 SecPath 负载均衡在页面上标为「网页暂未开放」，请继续用 `python main.py`。

也可以直接调接口，示例里不要写真实口令：

```bash
curl -s http://127.0.0.1:8765/api/generate \
  -H 'Content-Type: application/json' \
  -d '{"brand":"h3c","hostname":"Access-SW-01","mgmt_ip":"192.168.1.1"}'
```

`GET /api/brands` 返回哪些品牌已开放。加上 `?format=text` 得到纯文本配置。服务器不保存配置、不记录口令，也不会登录设备。

## 打包为EXE

```bash
pip install pyinstaller
python build.py
```

## 目录结构

```
netops_toolkit/
├── main.py                  # 桌面版主程序入口
├── web_server.py            # 本机网页入口（python web_server.py）
├── web/                     # 浏览器第一版：表单、接口、现有生成器适配
├── build.py                 # EXE打包脚本
├── run.bat                  # Windows启动脚本
├── README.md                # 说明文档
├── gui/
│   ├── main_window.py       # 主窗口
│   ├── tools_window.py      # 工具箱窗口
│   ├── styles.py            # 样式定义
│   ├── tabs/                # 配置标签页
│   └── tools/               # 网络工具界面
│       ├── subnet_tool.py   # 子网计算器
│       ├── ping_tool.py     # Ping测试
│       ├── port_tool.py     # 端口扫描
│       ├── trace_tool.py    # 路由跟踪
│       ├── dns_tool.py      # DNS/Whois工具
│       ├── manual_tool.py   # 配置命令手册
│       ├── config_compare_tool.py  # 配置比较工具
│       └── config_io_tool.py       # 配置导入导出
├── modules/
│   ├── basic_config.py      # 基础配置生成器
│   ├── vlan_config.py       # VLAN配置生成器
│   ├── routing_config.py    # 路由配置生成器
│   ├── security_config.py   # 安全配置生成器
│   ├── interface_config.py  # 接口配置生成器
│   ├── h3c_config.py        # H3C配置生成器
│   ├── ruijie_config.py     # 锐捷配置生成器
│   ├── maipu_config.py      # 迈普配置生成器
│   ├── zte_config.py        # 中兴 ZXR10 经典 ZXROS 配置生成器
│   ├── zte_rosng_config.py  # 中兴 ZXR10 ROSNG 配置生成器
│   ├── zte_olt_config.py    # 中兴 ZXA10 C300/C600 OLT 配置生成器
│   ├── dptech_config.py     # 迪普 FW1000 防火墙配置生成器
│   ├── dptech_lsw_config.py # 迪普 LSW 交换机配置生成器
│   ├── h3c_lb_config.py     # 华三 SecPath 负载均衡配置生成器
│   └── qos_config.py        # QoS配置生成器
└── utils/
    ├── templates.py         # 配置模板
    ├── validator.py         # 配置验证器
    ├── manual/              # 配置命令手册
    │   ├── huawei_manual.py # 华为命令手册 (248条)
    │   ├── h3c_manual.py    # H3C命令手册 (239条)
    │   ├── ruijie_manual.py # 锐捷命令手册 (284条)
    │   ├── maipu_manual.py  # 迈普命令手册 (229条)
    │   ├── zte_manual.py    # 中兴 ZXR10 经典 ZXROS 命令速查
    │   ├── zte_rosng_manual.py # 中兴 ZXR10 ROSNG 命令速查
    │   ├── zte_olt_manual.py # 中兴 ZXA10 C300/C600 OLT 命令速查
    │   ├── dptech_manual.py # 迪普 FW1000 命令速查
    │   ├── dptech_lsw_manual.py # 迪普 LSW 命令速查
│   └── h3c_lb_manual.py     # 华三 SecPath 负载均衡命令速查
    └── network_tools/       # 网络工具模块
        ├── subnet_calculator.py  # 子网计算器
        ├── ping_tool.py          # Ping工具
        ├── trace_route.py        # 路由跟踪
        ├── port_scanner.py       # 端口扫描
        └── dns_tool.py           # DNS/Whois工具
```

## 使用说明

### 配置生成
1. 选择设备品牌（华为/H3C/锐捷/迈普/中兴/中兴 ROSNG/中兴 OLT/迪普 FW1000/迪普 LSW/华三负载均衡）
2. 点击"配置模板"选择预设场景（可选）
3. 在各标签页填写配置参数
4. 点击"验证配置"检查参数格式
5. 点击"生成配置"生成完整脚本
6. 导出文件或复制到剪贴板

### 网络工具
- 通过菜单栏「网络工具」访问单个工具
- 或点击「打开工具箱」使用完整工具集

| 工具 | 功能 |
|------|------|
| 子网计算器 | IP子网信息、子网划分、CIDR转换 |
| Ping测试 | 单主机/批量Ping测试 |
| 端口扫描 | 端口开放检测、服务识别 |
| 路由跟踪 | 网络路径追踪 |
| DNS/Whois | 域名解析、反向查询、域名信息 |
| 网络信息 | 本机IP、公网IP |
| IP转换 | 十进制/十六进制/二进制转换 |
| 配置命令手册 | 华为/H3C/中兴/中兴 ROSNG/中兴 OLT/迪普 FW1000/迪普 LSW/华三负载均衡 命令速查、配置案例 |
| 配置比较工具 | 配置差异对比、华为/H3C命令转换 |
| 配置导入导出 | JSON/文本导入导出、配置解析 |

### 华为与H3C配置差异

| 配置项 | 华为 | H3C |
|--------|------|-----|
| 进入系统视图 | `system-view` | `system-view` |
| 设备命名 | `sysname` | `sysname` |
| VLAN接口 | `interface Vlanif10` | `interface Vlan-interface10` |
| 端口聚合 | `interface Eth-Trunk1` | `interface Bridge-Aggregation 1` |
| SSH服务 | `stelnet server enable` | `ssh server enable` |
| 用户权限 | `level 15` (0-15) | `level 3` (0-3) |

### 中兴 ZXR10

品牌选「中兴 (ZTE)」后点「生成配置」。脚本按经典 ZXROS 输出，适合 ZXR10 5200/5900/8900 这一类交换机：

| 配置项 | 中兴 ZXR10 |
|--------|------------|
| 进入配置 | `configure terminal` |
| 主机名 | `hostname` |
| 三层 VLAN | `interface vlan 10` |
| Access/Trunk | `switchport access vlan` / `switchport trunk vlan` |
| 聚合 | `interface smartgroup1`，成员口 `smartgroup 1 mode active` |
| SSH | `ssh server enable` |
| 生成树 | `spanning-tree enable`，模式为 `sstp` / `rstp` / `mstp` |

界面里如果管理口仍是 `Vlanif1`，生成时会改成 `vlan 1`。二层口请手写 `gei_1/1` 或 `fei_1/1`。

这套语法不覆盖 5900E/5960/9900 的 ROSNG（`system-user`、`gei-0/1/1/1`）。5960/9900 请改选「中兴 ROSNG (5960/9900)」。也不覆盖 C300/C600 OLT，请改选「中兴 OLT (C300/C600)」。端口安全、PoE、`rate-limit` 在不同子系列上命令名可能不同，脚本里用的是接入/汇聚交换机上较常见的写法。

### 中兴 ROSNG

品牌选「中兴 ROSNG (5960/9900)」后点「生成配置」。脚本按 ROSNG 输出，适合 ZXR10 5960/9900 这一类新一代交换机。命令依据是 ZXR10 5900E V3.00.11 公开配置手册里已经核对过的写法：

| 配置项 | 中兴 ROSNG |
|--------|------------|
| 进入配置 | `configure terminal`，结束用 `end` |
| 主机名 | `hostname` |
| 登录用户 | `system-user` 里的 `user-name` / `password`，并绑定本地 AAA 模板 |
| SSH | `ssh server enable`。监听端口只接受 22 或 49152-65535 |
| 三层 VLAN | `interface vlan10`，地址写成 `ip address 192.168.10.1 255.255.255.0` |
| Access/Trunk | 写在 `switchvlan-configuration` 里：`switchport access vlan` / `switchport trunk vlan` |
| 聚合 | `interface smartgroup1`，`lacp mode 802.3ad` 或 `lacp mode on`，成员口 `smartgroup 1 mode active` |
| 静态路由 | `ip route 198.51.100.0 255.255.255.0 192.0.2.1` |
| 保存 | 注释里的 `write`。脚本不会登录设备，也不会自动保存 |

二层口填 `gei-0/1/1/1`，万兆口填 `xgei-0/1/1/1`。界面里的 `Vlanif1` 会改成 `vlan1`。命令手册里选「中兴 ROSNG」可以对照同一套写法。

OSPF、BGP、RIP、生成树、ACL、LLDP、PoE 和端口安全没有写成可执行命令，脚本里用注释留下界面上的参数。VLAN 名称和接口描述同样只留注释。模板里的 `Placeholder1` 是占位口令，下发前请改掉。

### 中兴 OLT（C300/C600）

品牌选「中兴 OLT (C300/C600)」后点「生成配置」。脚本按 ZXAN 输出，适合 ZXA10 C300/C320 和 C600。经典 ZXROS 和 ROSNG 都不覆盖这两款 OLT。命令只采用公开手册里能对上的写法：

| 配置项 | 中兴 OLT |
|--------|----------|
| 进入配置 | `configure terminal`，结束用 `end` |
| 主机名 | `hostname` |
| 特权口令 | `enable secret 0 <明文>`。明文 3 到 16 位。密文不写，手册写明 `enable secret 5` 只在加载配置文件时使用 |
| SSH | `ssh server enable`、`ssh server version 2`、`ssh server authentication mode local`、`ssh server authentication type pap` |
| C300 带外管理 | `interface vlan mng1`，地址 `ip address 10.200.0.2 255.255.255.0` |
| C300 三层 VLAN | `interface vlan 10`。界面里的 `Vlanif10` 会改成这种写法 |
| C600 带外管理 | `interface mgmt_eth` |
| C600 三层 VLAN | `interface vlan100`（中间没有空格） |
| 上联 VLAN | `switchport mode trunk` 或 `hybrid`，然后 `switchport vlan 100 tag`。上联口不能配 access，界面的 Access 改写成 `switchport default vlan` |
| C300 接口名 | 上联 `gei_1/19/1`、`xgei_1/10/1`，PON `gpon-olt_1/1/1` |
| C600 接口名 | 上联 `xgei-1/1/1`，PON `gpon_olt-1/1/1`。C600 上联和 PON 口会写 `no shutdown` |
| 静态路由 | `ip route 198.51.100.0 255.255.255.0 10.1.1.254` |
| 保存 | 注释里的 `write`。脚本不会登录设备，也不会自动保存 |

一份脚本里不要混用两套接口名。只填了 `Vlanif` 或 `vlan 10`、没有上联口时，按 C300 的 `interface vlan 10` 生成，文件头会说明 C600 的差别。

ONU 注册没有写成可执行命令。界面没有 ONU 类型、SN 和 LOID。脚本在 PON 口下用注释保留手册示例：`onu <编号> type <类型> sn <SN>`（C300 命令手册 1.13；C600 另有 `loid`）。`service-port` 需要 vport 和 user-vlan，同样只留注释。

本地用户、聚合、OSPF、BGP、RIP、生成树、ACL、NTP、SNMP、LLDP 和 PoE 没有写成可执行命令。C300 和 C600 的用户、聚合命令不一样，所以不猜。模板里的 `LabOnly1` 和 `Placeholder1` 是占位符，下发前请改掉。命令手册里选「中兴 OLT」可以对照同一套写法。

### 迪普 FW1000

品牌选「迪普 FW1000 (防火墙)」后点「生成配置」。脚本按 Conplat 输出，适合 FW1000 系列防火墙。交换机请改选「迪普 LSW」：

| 配置项 | 迪普 FW1000 |
|--------|-------------|
| 进入配置 | `conf-mode` |
| 系统名 | `sysname` |
| 管理口 / 业务口 | `interface meth0_0` / `interface gige0_1` |
| 三层 VLAN | `interface vlan-if 10`，地址写成 `ip address 192.168.10.1/24` |
| Access/Trunk | `switchport access vlan` / `switchport trunk allowed vlan` |
| 安全域 | `security-zone Trust` 后把接口加进去 |
| 包过滤 | `address-object`、`service-object`、`security-policy` |
| 聚合 | `interface bond 1`，成员口 `bond group 1` |
| SSH | `ssh enable` |
| 保存 | `write file` |

界面里如果管理口仍是 `Vlanif1`，生成时会改成 `vlan-if 1`。二层口请手写 `gige0_1`。生成的接口会先放入预定义安全域 Trust，外网口需要改到 Untrust。

OSPF、BGP、RIP、生成树、LLDP、PoE、端口安全和 DHCP Snooping 没有写成可执行命令，脚本里用注释留下界面上的参数。ADX 应用交付不在这套语法里。

### 迪普 LSW

品牌选「迪普 LSW (交换机)」后点「生成配置」。脚本仍是 Conplat，但按 LSW3600/LSW5600 交换机来写，不会生成 FW1000 的 `security-policy`：

| 配置项 | 迪普 LSW |
|--------|----------|
| 进入配置 | `conf-mode`，结束用 `exit` |
| 系统名 | `sysname` |
| 管理地址 | `interface vlan-if 1`，地址写成 `ip address 192.168.1.1/24` |
| Access/Trunk | `switchport access vlan` / `switchport trunk allowed vlan` |
| 聚合 | `interface bond 1`，`bond mode dynamic` 或 `bond mode static`，成员口 `bond group 1` |
| SSH | `ssh enable`，用户是 `local-user admin password <密码> role super` |
| 生成树 | `spanning-tree enable`，模式 `stp` / `rstp` / `mst` |
| 静态 / RIP / OSPF | `ip route`、`router rip`、`router ospf`。BGP 只留注释 |

二层口填 `gige0_1`，万兆口填 `tengige0_1`。界面里的 `Vlanif1` 会改成 `vlan-if 1`。命令手册里选「迪普 LSW」可以对照同一套写法。

LSW3600-24GT4GP-LI 的彩页没有三层路由；入门型号如果拒绝 `router ospf`，删掉那一段即可。LLDP、PoE、端口安全、风暴抑制和编号 ACL 没有核对到可粘贴参数，脚本里只留注释。

### 华三负载均衡（SecPath）

品牌选「华三负载均衡 (SecPath)」后点「生成配置」。脚本按 Comware 输出，适合使用 `real-server` / `server-farm` / `virtual-server` 的华三负载均衡。华三交换机请改选「华三 (H3C)」，迪普应用交付不在这套语法里。

到「路由配置」页填写实服务组、实服务器和虚服务器。管理口填 `GigabitEthernet1/0/1`。

| 配置项 | 华三负载均衡 |
|--------|----------------|
| 进入配置 | `system-view`，结束用 `quit` |
| 系统名 | `sysname` |
| 接口地址 | `interface GigabitEthernet 1/0/1`，地址 `ip address 192.168.1.1 255.255.255.0` |
| 静态路由 | `ip route-static 198.51.100.0 255.255.255.0 192.168.1.254` |
| 健康检查 | `nqa template icmp icmp1`，实服务组里 `probe icmp1` |
| 实服务器 | `real-server rs1`，`ip address`、`port`、`weight`、`server-farm` |
| 虚服务器 | `virtual-server vs-web type tcp`，`virtual ip address`、`default server-farm`、`service enable` |
| 同网段 | `arp-nd interface GigabitEthernet 1/0/1` |
| 聚合 | `interface Route-Aggregation 1`，成员口 `port link-aggregation group 1` |
| 保存 | 注释里的 `save`。脚本不会登录设备，也不会自动保存或重启 |

`service enable` 只打开虚服务器。虚服务器缺省是关闭的，这条不是重启设备。

以 `#` 开头的行是说明。Comware 命令行里输入 `#` 会退回用户视图，粘贴时请跳过这些行。

SSH、本地用户、安全域、`security-policy`、OSPF、BGP、RIP、生成树和 `switchport` 没有写成可执行命令。安全策略示例需要先指定 trust/untrust，界面没有这个字段，所以不代填。模板里的 `Admin@123` 是占位口令，下发前请改掉，脚本本身不会把口令写出来。命令手册里选「华三负载均衡」可以对照同一套写法。

## 系统要求

- Python 3.8+
- PyQt5
- Windows/Linux/macOS

## 更新日志

### v4.0 (当前版本)
- 🔥 新增华三 SecPath 服务器负载均衡配置生成（实服务器、虚服务器、ICMP 健康检查、静态路由）
- 🔥 新增中兴 ZXA10 C300/C600 OLT 配置生成（管理地址、上联 VLAN、SSH、静态路由；ONU 注册只留注释）
- 🔥 新增中兴 ZXR10 ROSNG 配置生成（5960/9900：VLAN、SSH、smartgroup、静态路由）
- 🔥 新增迪普 LSW3600/LSW5600 交换机配置生成（Conplat：VLAN、SSH、bond）
- 🔥 新增迪普 FW1000 防火墙配置生成（Conplat：安全域、包过滤、bond）
- 🎨 项目重命名为 NetOps Toolkit
- 🔄 新增锐捷(Ruijie)和迈普(Maipu)两大品牌支持
- 📚 命令手册全面扩充: 1000+条命令、35+配置案例
- ✨ 四品牌命令格式自动适配
- 🛠️ 内置11+网络运维工具
- 🐛 修复端口扫描工具无法使用问题
- 🐛 修复Ping测试工具Windows兼容性问题
- 📚 丰富配置命令手册内容

### v3.1
- ✨ 新增配置比较工具
- ✨ 新增配置导入导出工具
- 🐛 修复网络工具兼容性问题

### v3.0
- ✨ 新增H3C华三交换机配置支持
- ✨ 新增网络工具箱（9种工具）
- 🎨 设备品牌切换功能

### v2.1
- 配置模板功能
- 配置验证功能
- 界面交互优化

### v2.0
- 基础配置增强
- 全新现代化UI设计

### v1.0
- 基础功能

## 许可证

MIT License
