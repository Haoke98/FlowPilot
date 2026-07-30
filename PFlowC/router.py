# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/7/30
@Software: PyCharm
@disc: 智能 CONNECT 代理 v4.0
       — 全局直连模式
       — 多上游代理 + 可选路由策略
       — 鉴权 (Basic Auth / Token)
======================================="""
import asyncio
import base64
import json
import logging
import os
import random
import socket
import sys
import time

# geoip2 为可选依赖
try:
    import geoip2.errors
    _GEOIP_AVAILABLE = True
except ImportError:
    _GEOIP_AVAILABLE = False
    geoip2 = None

try:
    from PFlowC.utils.net import geoip_db
except ImportError:
    geoip_db = None
    _GEOIP_AVAILABLE = False

LOCAL_REGION_CODE = 'CN'
home_dir = os.path.expanduser("~/.PFlowC")

# ── 缓存 ──────────────────────────────────────────────────
_domain_cache = {}
_geoip_country_cache = {}

# ── 运行时配置（由 start() 注入） ─────────────────────────
LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 7890

# 运行模式: "smart" (GeoIP分流) | "direct" (全局直连)
MODE = "smart"

# 上游代理列表（多上游）
UPSTREAMS = []  # list of {host, port, protocol, username, password, weight, tags}

# 路由策略: "round_robin" | "random" | "lowest_latency" | "geoip_preferred"
ROUTING_STRATEGY = "round_robin"

# 鉴权配置
AUTH_ENABLED = False
AUTH_USERNAME = ""
AUTH_PASSWORD = ""
AUTH_TOKENS = []  # 备用: 多token支持
AUTH_CHECKER = None  # 自定义鉴权回调: callable(username, password) -> bool

# Debug 模式
DEBUG = False

# 路由计数器（轮询用）
_round_robin_counter = 0
_upstream_latency = {}  # {upstream_key: avg_latency_ms}


# ═══════════════════════════════════════════════════════════
#  GeoIP
# ═══════════════════════════════════════════════════════════

def _is_domestic(host):
    """快速 GeoIP 判断（系统DNS + 缓存）"""
    if host in _domain_cache:
        return _domain_cache[host]
    try:
        socket.inet_aton(host)
        response = geoip_db.country(host)
        result = response.country.iso_code == LOCAL_REGION_CODE
    except (socket.error, OSError):
        try:
            ip = socket.gethostbyname(host)
            if ip in _geoip_country_cache:
                result = _geoip_country_cache[ip] == LOCAL_REGION_CODE
            else:
                response = geoip_db.country(ip)
                code = response.country.iso_code
                _geoip_country_cache[ip] = code
                result = code == LOCAL_REGION_CODE
        except (socket.gaierror, geoip2.errors.AddressNotFoundError):
            result = False
    except geoip2.errors.AddressNotFoundError:
        result = True
    except Exception:
        result = False
    _domain_cache[host] = result
    return result


# ═══════════════════════════════════════════════════════════
#  鉴权
# ═══════════════════════════════════════════════════════════

def _check_auth(auth_header: str) -> bool:
    """验证 Basic Auth 或 Token"""
    if not AUTH_ENABLED:
        return True

    if not auth_header:
        if DEBUG:
            logging.debug("[AUTH] 未收到鉴权头")
        return False

    # Token 鉴权: Proxy-Authorization: Bearer <token>
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        if DEBUG:
            logging.debug("[AUTH] Bearer token (len={}, prefix={}...)".format(
                len(token), token[:8] if len(token) >= 8 else token))
            logging.debug("[AUTH] AUTH_CHECKER={}, tokens_count={}".format(
                AUTH_CHECKER is not None, len(AUTH_TOKENS)))
        if AUTH_CHECKER:
            result = AUTH_CHECKER(token, "")
            if DEBUG:
                logging.debug("[AUTH] checker result: {}".format(result))
            return result
        if AUTH_TOKENS and token in AUTH_TOKENS:
            if DEBUG:
                logging.debug("[AUTH] token matched in tokens list")
            return True
        if AUTH_PASSWORD and token == AUTH_PASSWORD:
            return True
        if DEBUG:
            logging.debug("[AUTH] token NOT matched (tokens={})".format(
                [t[:8]+"..." if len(t)>8 else t for t in AUTH_TOKENS]))
        return False

    # Basic 鉴权: Proxy-Authorization: Basic <base64>
    if auth_header.startswith("Basic "):
        try:
            decoded = base64.b64decode(auth_header[6:]).decode('utf-8')
            username, _, password = decoded.partition(':')
            if DEBUG:
                logging.debug("[AUTH] Basic: user={} pass_len={}".format(
                    username, len(password)))
            if AUTH_CHECKER:
                result = AUTH_CHECKER(username, password)
                if DEBUG:
                    logging.debug("[AUTH] checker result: {}".format(result))
                return result
            ok = username == AUTH_USERNAME and password == AUTH_PASSWORD
            if DEBUG and not ok:
                logging.debug("[AUTH] Basic mismatch: got {}/{} vs config {}/{}".format(
                    username, "*"*len(password), AUTH_USERNAME, "*"*len(AUTH_PASSWORD)))
            return ok
        except Exception as e:
            if DEBUG:
                logging.debug("[AUTH] Basic decode failed: {}".format(e))
            return False

    if DEBUG:
        logging.debug("[AUTH] unknown auth type: {}".format(auth_header[:20]))
    return False


# ═══════════════════════════════════════════════════════════
#  上游代理选取
# ═══════════════════════════════════════════════════════════

def _pick_upstream():
    """根据路由策略选取一个上游代理"""
    if not UPSTREAMS:
        return None

    active = UPSTREAMS  # TODO: 健康检查后可过滤离线节点
    if not active:
        return None

    global _round_robin_counter

    if ROUTING_STRATEGY == "random":
        return random.choice(active)

    elif ROUTING_STRATEGY == "lowest_latency":
        best = None
        best_lat = float('inf')
        for u in active:
            key = "{}:{}".format(u["host"], u["port"])
            lat = _upstream_latency.get(key, float('inf'))
            if lat < best_lat:
                best_lat = lat
                best = u
        return best if best else active[0]

    elif ROUTING_STRATEGY == "geoip_preferred":
        cn = [u for u in active if u.get("tags", "").lower() in ("cn", "china", "domestic")]
        if cn:
            return random.choice(cn)
        return random.choice(active)

    else:  # round_robin (default)
        idx = _round_robin_counter % len(active)
        _round_robin_counter += 1
        return active[idx]


# ═══════════════════════════════════════════════════════════
#  中继 & 处理
# ═══════════════════════════════════════════════════════════

async def _relay(reader, writer):
    """单向中继"""
    try:
        while True:
            data = await reader.read(32768)
            if not data:
                break
            writer.write(data)
            await writer.drain()
    except Exception:
        pass


async def _handle(reader, writer):
    """处理一个客户端连接"""
    client_addr = writer.get_extra_info('peername')
    target = ""
    host = ""
    port = 0
    _type = "?"
    remote_reader = remote_writer = None

    try:
        # ── 解析 CONNECT 请求行 ──────────────────────────
        line = await asyncio.wait_for(reader.readline(), timeout=30)
        if not line:
            writer.close()
            return
        line = line.decode('utf-8', errors='replace').strip()

        if not line.startswith('CONNECT'):
            writer.write(b'HTTP/1.1 405 Method Not Allowed\r\n\r\n')
            await writer.drain()
            writer.close()
            return

        parts = line.split()
        if len(parts) < 2:
            writer.close()
            return
        target = parts[1]
        host, _, port_str = target.partition(':')
        port = int(port_str) if port_str else 443

        # ── 吞掉请求头 + 提取鉴权 ────────────────────────
        proxy_auth = ""
        while True:
            l = await reader.readline()
            if l in (b'\r\n', b'\n', b''):
                break
            header_line = l.decode('utf-8', errors='replace').strip()
            if header_line.lower().startswith('proxy-authorization:'):
                proxy_auth = header_line.split(':', 1)[1].strip()

        # ── 鉴权检查 ─────────────────────────────────────
        if DEBUG and proxy_auth:
            logging.debug("[AUTH] 收到鉴权头: {}...".format(proxy_auth[:50]))
        if AUTH_ENABLED and not _check_auth(proxy_auth):
            writer.write(b'HTTP/1.1 407 Proxy Authentication Required\r\n'
                         b'Proxy-Authenticate: Basic realm="PFlowC"\r\n\r\n')
            await writer.drain()
            writer.close()
            logging.warning("[AUTH-FAIL][{}] {}".format(client_addr, target))
            return

        # ── 模式：全局直连 ───────────────────────────────
        if MODE == "direct":
            _type = "DIRECT"
            remote_reader, remote_writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=30)
            writer.write(b'HTTP/1.1 200 Connection Established\r\n\r\n')
            await writer.drain()

        # ── 模式：智能路由 (GeoIP 分流) ──────────────────
        else:
            if _is_domestic(host):
                _type = "DIRECT"
                remote_reader, remote_writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port), timeout=30)
                writer.write(b'HTTP/1.1 200 Connection Established\r\n\r\n')
                await writer.drain()
            else:
                upstream = _pick_upstream()
                if upstream is None:
                    _type = "FALLBACK"
                    logging.warning("[FALLBACK] 无可用上游代理，直连 {}".format(target))
                    remote_reader, remote_writer = await asyncio.wait_for(
                        asyncio.open_connection(host, port), timeout=30)
                    writer.write(b'HTTP/1.1 200 Connection Established\r\n\r\n')
                    await writer.drain()
                else:
                    _type = "PROXY"
                    u_host = upstream["host"]
                    u_port = upstream["port"]
                    u_proto = upstream.get("protocol", "http")

                    logging.info("[PROXY] 使用上游 {}://{}:{} → {}".format(
                        u_proto, u_host, u_port, target))

                    remote_reader, remote_writer = await asyncio.wait_for(
                        asyncio.open_connection(u_host, u_port), timeout=30)

                    # 构造 CONNECT 请求
                    upstream_req = "CONNECT {}:{} HTTP/1.1\r\nHost: {}:{}\r\n".format(
                        host, port, host, port)

                    # 上游鉴权
                    auth_type = upstream.get("auth_type", "basic")
                    u_user = upstream.get("username", "")
                    u_pass = upstream.get("password", "")
                    u_token = upstream.get("token", "")

                    if auth_type == "token" and u_token:
                        upstream_req += "Proxy-Authorization: Bearer {}\r\n".format(u_token)
                        if DEBUG:
                            logging.debug("[UPSTREAM-AUTH] Bearer token(len={}) → {}:{}".format(
                                len(u_token), u_host, u_port))
                    elif u_user or u_pass:
                        auth_b64 = base64.b64encode(
                            "{}:{}".format(u_user or "", u_pass or "").encode()).decode()
                        upstream_req += "Proxy-Authorization: Basic {}\r\n".format(auth_b64)
                        if DEBUG:
                            logging.debug("[UPSTREAM-AUTH] Basic auth → {}:{}".format(u_host, u_port))

                    upstream_req += "\r\n"
                    remote_writer.write(upstream_req.encode())
                    await remote_writer.drain()

                    # 读取上游响应
                    resp_line = await asyncio.wait_for(remote_reader.readline(), timeout=15)
                    writer.write(resp_line)
                    await writer.drain()

                    if not resp_line or b'200' not in resp_line.split(b' ', 2)[0:2]:
                        _type = "PROXY_ERR"
                        logging.error("[PROXY_ERR] 上游 {}:{} 拒绝 CONNECT: {}".format(
                            u_host, u_port, resp_line.decode(errors='replace').strip()))

        logging.info("[{}][{}] {}:{}".format(_type, client_addr, host, port))

        # ── 双向中继 ─────────────────────────────────────
        await asyncio.gather(
            _relay(reader, remote_writer),
            _relay(remote_reader, writer),
            return_exceptions=True,
        )

    except asyncio.TimeoutError:
        logging.error("[TIMEOUT][{}] {}:{}".format(client_addr, host, port))
    except ConnectionRefusedError:
        logging.error("[REFUSED][{}] {}:{}".format(client_addr, host, port))
    except Exception as e:
        logging.error("[ERROR][{}] {} — {}".format(client_addr, target, e))
    finally:
        for rw in (remote_reader, remote_writer, reader, writer):
            try:
                rw.close()
            except Exception:
                pass


# ═══════════════════════════════════════════════════════════
#  启动入口
# ═══════════════════════════════════════════════════════════

def start(listen_port=None, mode=None, upstreams=None,
          strategy=None, auth_config=None, debug=False):
    """启动路由代理（阻塞）

    Args:
        listen_port: 监听端口，None 从配置文件读取
        mode: "smart" | "direct"，None 从配置文件
        upstreams: 上游代理列表 [{host, port, ...}]
        strategy: 路由策略 "round_robin" | "random" | "lowest_latency" | "geoip_preferred"
        auth_config: {"enabled": bool, "username": "", "password": "", "tokens": []}
        debug: 开启 debug 模式，输出鉴权参数等调试信息
    """
    global LISTEN_PORT, MODE, UPSTREAMS, ROUTING_STRATEGY
    global AUTH_ENABLED, AUTH_USERNAME, AUTH_PASSWORD, AUTH_TOKENS
    global DEBUG

    # 从配置文件读取
    config_fp = os.path.join(home_dir, "config.json")
    if os.path.isfile(config_fp):
        try:
            cfg = json.load(open(config_fp))

            # 端口
            if listen_port is None and "port" in cfg:
                LISTEN_PORT = int(cfg["port"])

            # 模式
            if mode is None and "mode" in cfg:
                MODE = cfg["mode"]

            # ── 上游代理：兼容旧格式 + 新格式 ──────────
            if upstreams is None:
                if "upstreams" in cfg and cfg["upstreams"]:
                    UPSTREAMS = cfg["upstreams"]
                elif "upstream" in cfg and cfg["upstream"]:
                    u = cfg["upstream"]
                    UPSTREAMS = [{
                        "host": u.get("host", ""),
                        "port": int(u.get("port", 0)),
                        "protocol": u.get("protocol", "http"),
                        "username": u.get("username", ""),
                        "password": u.get("password", ""),
                        "weight": u.get("weight", 1),
                        "tags": u.get("tags", ""),
                    }]

            # 路由策略
            if strategy is None and "routing_strategy" in cfg:
                ROUTING_STRATEGY = cfg["routing_strategy"]

            # 鉴权
            if auth_config is None and "auth" in cfg:
                a = cfg["auth"]
                AUTH_ENABLED = a.get("enabled", False)
                AUTH_USERNAME = a.get("username", "")
                AUTH_PASSWORD = a.get("password", "")
                AUTH_TOKENS = a.get("tokens", [])

        except Exception as e:
            print("读取配置失败: {}".format(e), file=sys.stderr)

    # 命令行参数覆盖
    if listen_port is not None:
        LISTEN_PORT = listen_port
    if mode is not None:
        MODE = mode
    if upstreams is not None:
        UPSTREAMS = upstreams
    if strategy is not None:
        ROUTING_STRATEGY = strategy
    if auth_config is not None:
        AUTH_ENABLED = auth_config.get("enabled", AUTH_ENABLED)
        AUTH_USERNAME = auth_config.get("username", AUTH_USERNAME)
        AUTH_PASSWORD = auth_config.get("password", AUTH_PASSWORD)
        AUTH_TOKENS = auth_config.get("tokens", AUTH_TOKENS)

    # Debug 模式
    DEBUG = debug
    if DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)

    async def _serve():
        server = await asyncio.start_server(_handle, LISTEN_HOST, LISTEN_PORT)
        addr = server.sockets[0].getsockname()
        logging.info("PFlowC v4.0 router → {}:{}".format(*addr))
        logging.info("  模式: {}".format(MODE))
        logging.info("  上游代理: {} 个".format(len(UPSTREAMS)))
        if MODE == "smart" and UPSTREAMS:
            logging.info("  路由策略: {}".format(ROUTING_STRATEGY))
            for i, u in enumerate(UPSTREAMS):
                tags = u.get("tags", "")
                tag_str = " [{}]".format(tags) if tags else ""
                logging.info("    {}. {}://{}:{}{}".format(
                    i + 1, u.get("protocol", "http"), u["host"], u["port"], tag_str))
        if MODE == "direct":
            logging.info("  ⚡ 全局直连模式 — 所有流量不走上游代理")
        if AUTH_ENABLED:
            logging.info("  🔒 鉴权已启用")
        if DEBUG:
            logging.info("  🐛 Debug 模式已开启")
        async with server:
            await server.serve_forever()

    asyncio.run(_serve())
