# FlowPilot

A smart proxy router that automatically routes domestic traffic directly and foreign traffic through an upstream proxy — all decided by GeoIP at the TCP CONNECT level.

**No more growing bypass_domains lists. No mitmproxy dependency. Just pure Python asyncio.**

## How It Works

```
Client (browser/curl)
    │  proxy → 127.0.0.1:7891
    ▼
┌─────────────────────────────────┐
│         FlowPilot Router        │
│   (async CONNECT proxy, ~150 LOC)│
│                                 │
│   _is_domestic(host)?           │
│   ├── YES → DIRECT to target    │
│   └── NO  → CONNECT to upstream │
│             (192.168.76.x:7890) │
└─────────────────────────────────┘
```

- **Domestic** (China): TCP connects directly to the target server, zero latency overhead.
- **Foreign**: TCP connects to the configured upstream proxy, sends `CONNECT target:443`, relays traffic.
- Routing decisions are cached in memory for instant lookups on repeated requests.

## Quick Start

```bash
# 1. Install
pip install PFlowC -U

# 2. Configure upstream proxy
mkdir -p ~/.PFlowC
cat > ~/.PFlowC/config.json << 'EOF'
{
  "port": 7891,
  "upstream": {"host": "192.168.76.145", "port": "7890"},
  "bypass_domains": ["127.0.0.1", "192.168.0.0/16", "172.16.0.0/16", "10.0.0.0/8"]
}
EOF

# 3. Start the router
pflow-cli server

# 4. Set system proxy (separate terminal, or use pflow-cli on)
pflow-cli on
```

## Commands

```
Usage: pflow-cli [OPTIONS] COMMAND [ARGS]...

  ██████╗ ███████╗██╗      ██████╗ ██╗    ██╗ ██████╗
  ██╔══██╗██╔════╝██║     ██╔═══██╗██║    ██║██╔════╝
  ██████╔╝█████╗  ██║     ██║   ██║██║ █╗ ██║██║
  ██╔═══╝ ██╔══╝  ██║     ██║   ██║██║███╗██║██║
  ██║     ██║     ███████╗╚██████╔╝╚███╔███╔╝╚██████╗
  ╚═╝     ╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝  ╚═════╝

Commands:
  server    Start the smart proxy router (GeoIP-based)
  on        Set macOS system proxy + shell env + git proxy
  off       Clear all proxy settings
  version   Show version
```

## Configuration

`~/.PFlowC/config.json`:

| Field | Description | Example |
|-------|-------------|---------|
| `port` | Local listen port | `7891` |
| `upstream.host` | Upstream proxy host | `"192.168.76.145"` |
| `upstream.port` | Upstream proxy port | `"7890"` |
| `bypass_domains` | System-level bypass (LAN/local only) | `["127.0.0.1", "192.168.0.0/16"]` |

## 打包 & 安装 & 发布

以下操作均在项目根目录进行。

**1. 打包**

先清旧再打包，避免覆盖冲突：

```bash
rm -rf ./build ./dist
python setup.py sdist bdist_wheel
```

**2. 安装（本地验证）**

```bash
pip install ./dist/PFlowC-3.0.0.tar.gz
```

**3. 发布**

推送 `v*` tag 会自动触发 GitHub Actions 发布到 PyPI 并创建 GitHub Release：

```bash
git tag v3.0.0 && git push origin v3.0.0
```

或手动发布：

```bash
twine upload ./dist/PFlowC-3.0.0.tar.gz
```

## TODO

- [ ] 完善多平台系统代理自动配置
    - [x] macOS
    - [ ] Windows
    - [ ] Linux
- [ ] 完善多平台命令行代理自动配置
    - [x] macOS (.zshrc / .bashrc)
    - [ ] 自动检测 shell 配置文件
    - [ ] Windows
    - [ ] Linux
- [x] 上游代理可配置
- [x] 发布为 Python site-packages
- [x] 使用 GeoIP 实现智能路由（国内直连 / 境外代理）
- [x] 在程序内部实现流量分流（不再依赖系统 bypass_domains）
- [x] 自动配置 Git 全局代理
- [x] CI/CD：GitHub Actions 自动发布到 PyPI + GitHub Release
- [ ] 发布各平台预编译包 (macOS / Windows / Linux)
- [ ] 利用 Curses 优化控制台流量展示
- [ ] 后台服务模式 + 状态栏组件
- [ ] GUI 桌面应用
- [ ] 利用 Trojan 实现可跨 GFW 的传统代理
    - [ ] 参考 [trojan-go](https://github.com/p4gefau1t/trojan-go)
- [ ] 与内网穿透工具集成
    - [ ] [ZeroTier](https://github.com/zerotier/ZeroTierOne)
    - [ ] [Tailscale](https://tailscale.com)
- [ ] 从数据中心按地理位置拉取忽略列表

## Contributing

欢迎参与！无论是 Bug 反馈、功能建议还是代码贡献，都欢迎提 [Issue](https://github.com/Haoke98/FlowPilot/issues) 或 PR。

如果你有这些方面的经验，特别欢迎：
- Windows / Linux 平台的系统代理配置
- Curses TUI 开发
- 跨平台 GUI (Electron / Tauri)

## License

MIT · Copyright Sadam·Sadik

## Acknowledgments

- [geoip2](https://github.com/maxmind/GeoIP2-python) for IP geolocation
- [dnspython](https://www.dnspython.org/) for DNS utilities
