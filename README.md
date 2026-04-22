# NetOps Toolkit v4.0 - 网络运维工具集

一个功能强大、现代化界面的**多品牌交换机配置生成工具**，支持**华为/H3C/锐捷/迈普**四大品牌，内置**11+网络工具**，基于 Python + PyQt5 开发。

## v4.0 新特性

### 🎨 科技感UI设计
- **深色渐变主题** - 紫蓝渐变背景，赛博朋克风格
- **发光边框效果** - 霓虹蓝色高亮，科技感十足
- **窗口自适应** - 自动适配不同屏幕尺寸
- **现代化控件** - 渐变按钮、玻璃态卡片

### 🔄 四品牌设备支持
- **华为 (Huawei)** - 248条命令 + 8个配置案例
- **华三 (H3C)** - 239条命令 + 9个配置案例  
- **锐捷 (Ruijie)** - 284条命令 + 10个配置案例
- **迈普 (Maipu)** - 229条命令 + 8个配置案例
- 一键切换设备类型，自动适配命令格式

### 🧰 内置网络工具箱
- **子网计算器** - IP子网计算、子网划分、IP范围转CIDR
- **Ping测试** - 单主机/批量Ping、Ping扫描
- **端口扫描** - 常用端口/全端口扫描、快速端口测试
- **路由跟踪** - Traceroute路由路径追踪
- **DNS/Whois** - DNS查询、反向DNS、Whois域名信息
- **网络信息** - 本机IP、公网IP查询
- **IP转换** - 十进制/十六进制/二进制转换
- **配置命令手册** - 华为/H3C配置命令速查、配置案例
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

## 打包为EXE

```bash
pip install pyinstaller
python build.py
```

## 目录结构

```
netops_toolkit/
├── main.py                  # 主程序入口
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
│   └── qos_config.py        # QoS配置生成器
└── utils/
    ├── templates.py         # 配置模板
    ├── validator.py         # 配置验证器
    ├── manual/              # 配置命令手册
    │   ├── huawei_manual.py # 华为命令手册 (248条)
    │   ├── h3c_manual.py    # H3C命令手册 (239条)
    │   ├── ruijie_manual.py # 锐捷命令手册 (284条)
    │   └── maipu_manual.py  # 迈普命令手册 (229条)
    └── network_tools/       # 网络工具模块
        ├── subnet_calculator.py  # 子网计算器
        ├── ping_tool.py          # Ping工具
        ├── trace_route.py        # 路由跟踪
        ├── port_scanner.py       # 端口扫描
        └── dns_tool.py           # DNS/Whois工具
```

## 使用说明

### 配置生成
1. 选择设备品牌（华为/H3C/锐捷/迈普）
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
| 配置命令手册 | 华为/H3C命令速查、配置案例 |
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

## 系统要求

- Python 3.8+
- PyQt5
- Windows/Linux/macOS

## 更新日志

### v4.0 (当前版本)
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
