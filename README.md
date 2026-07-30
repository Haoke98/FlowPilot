# FlowPilot

**智能代理路由器** — 纯 Python asyncio CONNECT 代理。支持 GeoIP 智能分流、多上游代理池、全局直连模式、Token/Basic 鉴权。

> **v4.0** 新增：全局直连模式 · 多上游代理 + 路由策略 · 鉴权 (Basic/Token) · 交互式配置向导

## 架构

```
Client (browser/curl)
    │  CONNECT → 127.0.0.1:7890
    ▼
┌──────────────────────────────────────────────────┐
│              FlowPilot Router v4.0                │
│         (async CONNECT proxy, ~400 LOC)           │
│                                                   │
│   ┌─ mode: direct ──────────────────────────────┐ │
│   │  → DIRECT to target (边缘节点模式)            │ │
│   └─────────────────────────────────────────────┘ │
│   ┌─ mode: smart ───────────────────────────────┐ │
│   │  _is_domestic(host)?                         │ │
│   │  ├── YES → DIRECT to target                  │ │
│   │  └── NO  → _pick_upstream(strategy)          │ │
│   │           → CONNECT through best upstream    │ │
│   └─────────────────────────────────────────────┘ │
│                                                   │
│   🔒 鉴权: Basic Auth / Bearer Token              │
└──────────────────────────────────────────────────┘
```

## 快速开始

```bash
# 1. 安装
pip install PFlowC -U

# 2. 交互式配置
pflow-cli setup

# 3. 启动
pflow-cli server

# 4. 使用代理
curl -x http://proxy-user:proxy-pass@127.0.0.1:7890 https://ipinfo.io
```

## 命令

```bash
pflow-cli setup        # 交互式配置向导（v4.0 新增）
pflow-cli show-config  # 查看当前配置（v4.0 新增）
pflow-cli server       # 启动代理路由服务
pflow-cli on           # 设置系统代理 (macOS)
pflow-cli off          # 清除所有代理设置
pflow-cli version      # 显示版本
```

**server 选项：**
```bash
pflow-cli server --port 7890 --mode direct
pflow-cli server --mode smart --strategy round_robin
```

## 配置

`~/.PFlowC/config.json`：

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `port` | int | 监听端口 | `7890` |
| `mode` | string | 运行模式：`smart`(GeoIP分流) / `direct`(全局直连) | `"smart"` |
| `routing_strategy` | string | 路由策略 (仅smart)：`round_robin` / `random` / `lowest_latency` / `geoip_preferred` | `"round_robin"` |
| `upstreams` | array | 上游代理列表 | 见下方 |
| `auth.enabled` | bool | 是否启用鉴权 | `true` |
| `auth.username` | string | Basic Auth 用户名 | `"proxy"` |
| `auth.password` | string | Basic Auth 密码 | `"secret"` |
| `auth.tokens` | array | Token 列表 | `["token1"]` |
| `bypass_domains` | array | 系统级代理绕过 | `["127.0.0.1"]` |

### 上游代理 (upstreams)

```json
{
  "upstreams": [
    {
      "host": "192.168.76.145",
      "port": 7890,
      "protocol": "http",
      "auth_type": "basic",
      "username": "user",
      "password": "pass",
      "token": "",
      "weight": 1,
      "tags": "us"
    }
  ]
}
```

| 字段 | 说明 |
|------|------|
| `host` / `port` | 上游代理地址 |
| `protocol` | 协议：`http` / `https` / `socks5` |
| `auth_type` | 鉴权类型：`basic` / `token` |
| `username` / `password` | Basic Auth 凭证 |
| `token` | Bearer Token 凭证 |
| `weight` | 权重（预留） |
| `tags` | 标签，如国家代码 `us`/`jp`/`hk` |

> 兼容旧格式：单个 `"upstream": {...}` 自动转为 `"upstreams": [...]`

### 鉴权示例

**Basic Auth：**
```json
{ "auth": { "enabled": true, "username": "proxy", "password": "secret" } }
```
```bash
curl -x http://proxy:secret@127.0.0.1:7890 https://ipinfo.io
```

**Token：**
```json
{ "auth": { "enabled": true, "tokens": ["my-token-xxx"] } }
```
```bash
curl -x http://my-token-xxx:@127.0.0.1:7890 https://ipinfo.io
```

## 使用场景

### 场景一：边缘节点（直连模式）

部署在各 IP 区域的节点，只需提供出口 IP，不走上游：

```bash
pflow-cli setup   # mode: direct, 启用鉴权(token)
pflow-cli server
```

### 场景二：中央节点（多上游模式）

汇聚多个边缘节点，对外提供统一的智能代理入口：

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

配合 [ProxyPool](https://github.com/Haoke98/proxy-pool) 可实现完整的 IP 代理池服务平台。

## 打包 & 安装 & 发布

```bash
# 打包
rm -rf ./build ./dist
python setup.py sdist bdist_wheel

# 本地安装验证
pip install ./dist/PFlowC-4.0.0.tar.gz

# 发布
git tag v4.0.0 && git push origin v4.0.0
# 或: twine upload ./dist/PFlowC-4.0.0.tar.gz
```

## 更新日志

### v4.0.0

- ✨ 全局直连模式 (`mode: direct`) — 所有流量直连，适合边缘节点
- ✨ 多上游代理 + 可选路由策略 (round_robin / random / lowest_latency / geoip_preferred)
- ✨ 鉴权支持: Basic Auth + Bearer Token
- ✨ 动态鉴权回调 (`AUTH_CHECKER`) — 支持外部注入验证逻辑
- ✨ 交互式配置向导 (`pflow-cli setup`)
- ✨ 自动迁移旧配置格式
- 🐛 上游 CONNECT Token 鉴权支持

### v3.0.0

- 纯 asyncio CONNECT 代理，移除 mitmproxy 依赖
- GeoIP 智能路由（国内直连 / 境外代理）
- CI/CD 自动发布 PyPI

## License

MIT · Copyright Sadam·Sadik
