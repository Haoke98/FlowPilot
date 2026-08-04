# FlowPilot

**智能代理路由器** — 纯 Python asyncio CONNECT 代理。支持 GeoIP 智能分流 · 多上游代理池 · 全局直连 · Token/Basic 鉴权 · 后台守护 · systemd 自启。

<div align="right">
  <img src="https://komarev.com/ghpvc/?username=Haoke98&repo=FlowPilot&color=07C160&label=👁️+Views&style=flat-square" alt="views"/>
</div>

## 架构

```
Client (browser/curl)
    │  CONNECT → 127.0.0.1:7890
    ▼
┌──────────────────────────────────────────────────┐
│              FlowPilot Router v4.0                │
│          (async CONNECT proxy ~500 LOC)           │
│                                                   │
│   ┌─ mode: direct ──────────────────────────────┐ │
│   │  → 所有流量直连 (边缘节点模式)                 │ │
│   └─────────────────────────────────────────────┘ │
│   ┌─ mode: smart ───────────────────────────────┐ │
│   │  GeoIP → 国内: DIRECT / 境外: 上游代理池选取   │ │
│   │  策略: round_robin | random | geoip_preferred │ │
│   └─────────────────────────────────────────────┘ │
│                                                   │
│   🔒 鉴权: Basic Auth | Bearer Token | AUTH_CHECKER│
└──────────────────────────────────────────────────┘
```

## 快速开始

```bash
pip install git+https://github.com/Haoke98/FlowPilot.git
pflow-cli setup         # 交互式配置
pflow-cli server -d     # 启动 (debug 模式)
curl -x http://user:pass@127.0.0.1:7890 https://ipinfo.io
```

## 命令

| 命令 | 说明 |
|------|------|
| `pflow-cli setup` | 交互式配置向导 (端口/模式/上游/鉴权) |
| `pflow-cli show-config` | 查看当前配置 |
| `pflow-cli server [OPTIONS]` | 启动代理路由服务 |
| `pflow-cli install-service` | 生成 systemd 服务文件 (开机自启) |
| `pflow-cli on` | 设置系统代理 (macOS) |
| `pflow-cli off` | 清除所有代理设置 |
| `pflow-cli version` | 显示版本 |

**server 选项：**

| 选项 | 说明 |
|------|------|
| `--port, -p` | 监听端口 (默认: 配置值) |
| `--mode, -m` | `smart` (GeoIP分流) / `direct` (全局直连) |
| `--strategy, -s` | 路由策略: `round_robin` / `random` / `lowest_latency` / `geoip_preferred` |
| `--debug, -d` | Debug 模式，输出鉴权参数和所有请求头 |
| `--daemon` | 后台守护进程 (double-fork, 日志 → `~/.PFlowC/logs/daemon.log`) |

## 配置

`~/.PFlowC/config.json`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `port` | int | 监听端口 |
| `mode` | string | `"smart"` (GeoIP) / `"direct"` (直连) |
| `routing_strategy` | string | 上游选取策略 (仅 smart) |
| `upstreams` | array | 上游代理列表 |
| `auth.enabled` | bool | 是否启用鉴权 |
| `auth.username` / `auth.password` | string | Basic Auth 凭证 |
| `auth.tokens` | array | Bearer Token 列表 |
| `bypass_domains` | array | 系统代理绕过 |

### 上游代理

```json
{
  "upstreams": [{
    "host": "10.0.1.1", "port": 7890,
    "protocol": "http", "auth_type": "token",
    "username": "", "password": "", "token": "my-token",
    "weight": 1, "tags": "us"
  }]
}
```

| 字段 | 说明 |
|------|------|
| `auth_type` | `"basic"` (用户名密码) / `"token"` (Bearer Token) |
| `token` | Bearer Token 值 (auth_type=token 时生效) |
| `tags` | 标签，如国家代码 `us`/`jp` |

> 兼容旧格式：单个 `"upstream": {...}` 自动转为 `"upstreams": [...]`

## 使用场景

### 边缘节点（直连模式）

```bash
pflow-cli setup   # mode: direct, 启用鉴权 → token
pflow-cli server --daemon
```

### 中央节点（多上游模式）

```json
{
  "mode": "smart",
  "upstreams": [
    { "host": "10.0.1.1", "port": 7890, "auth_type": "token", "token": "tok-us" },
    { "host": "10.0.2.1", "port": 7890, "auth_type": "token", "token": "tok-jp" }
  ],
  "routing_strategy": "round_robin"
}
```

配合 [ProxyPool](https://github.com/Haoke98/proxy-pool) 实现完整的 IP 代理池服务平台。

## 部署

### 方案一：pip 安装

```bash
pip install git+https://github.com/Haoke98/FlowPilot.git
```

### 方案二：deploy.sh 一键部署（CentOS 7 / 无 Python 环境）

自动下载便携 Python → 安装 FlowPilot → 配置 → 启动：

```bash
curl -fsSL https://raw.githubusercontent.com/Haoke98/FlowPilot/main/deploy.sh \
  | bash -s -- --token "your-token" --systemd
```

### 方案三：PyInstaller 单文件二进制

```bash
pyinstaller --clean flowpilot.spec
# 输出: dist/pflowc (~15MB 单文件)
scp dist/pflowc root@target:/usr/local/bin/
```

### systemd 开机自启

```bash
pflow-cli install-service              # 生成配置
# 复制输出到 /etc/systemd/system/pflowc.service
systemctl daemon-reload
systemctl enable --now pflowc
```

## 打包 & 发布

```bash
rm -rf ./build ./dist
python setup.py sdist bdist_wheel
pip install ./dist/PFlowC-4.0.8.tar.gz

# 发布 PyPI
git tag v4.0.8 && git push origin v4.0.8
# 或: twine upload dist/PFlowC-4.0.8.tar.gz
```

## 更新日志

### v4.0.x

- ✨ 全局直连模式 + 多上游代理 + 路由策略
- ✨ 鉴权: Basic Auth / Bearer Token + AUTH_CHECKER 动态回调
- ✨ `--debug` 模式：输出所有请求头和鉴权比对详情
- ✨ `--daemon` 后台守护 + `install-service` systemd 自启
- ✨ `deploy.sh` 一键部署脚本 (便携 Python，无需预装)
- ✨ PyInstaller spec (单文件二进制构建)
- 🐛 上游 CONNECT Token 鉴权 (Bearer header)
- 🐛 鉴权 Debug 日志 handler 级别修复

### v3.0.0

- 纯 asyncio CONNECT 代理，移除 mitmproxy 依赖
- GeoIP 智能路由（国内直连 / 境外代理）
- CI/CD 自动发布 PyPI + GitHub Release

## License

MIT · Copyright Sadam·Sadik
