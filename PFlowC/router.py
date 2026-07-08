# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/7/8
@Software: PyCharm
@disc: 轻量 CONNECT 代理 — 国内直连，境外走 upstream
======================================="""
import asyncio
import json
import logging
import os
import socket
import sys

import geoip2.errors

from PFlowC.utils.net import geoip_db

LOCAL_REGION_CODE = 'CN'
home_dir = os.path.expanduser("~/.PFlowC")

# 缓存
_domain_cache = {}

# 运行时配置（由 start() 注入）
UPSTREAM_HOST = ""
UPSTREAM_PORT = 0
LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 7890


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
            response = geoip_db.country(ip)
            result = response.country.iso_code == LOCAL_REGION_CODE
        except (socket.gaierror, geoip2.errors.AddressNotFoundError):
            result = False
    except geoip2.errors.AddressNotFoundError:
        result = True
    except Exception:
        result = False
    _domain_cache[host] = result
    return result


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
        # 解析 CONNECT 请求行
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

        # 吞掉剩余请求头
        while True:
            l = await reader.readline()
            if l in (b'\r\n', b'\n', b''):
                break

        # 路由决策
        if _is_domestic(host):
            _type = "DIRECT"
            remote_reader, remote_writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=30)
        else:
            _type = "PROXY"
            logging.info("[PROXY] connecting to upstream {}:{}".format(UPSTREAM_HOST, UPSTREAM_PORT))
            remote_reader, remote_writer = await asyncio.wait_for(
                asyncio.open_connection(UPSTREAM_HOST, UPSTREAM_PORT), timeout=30)
            # 向上游代理发送 CONNECT
            upstream_req = "CONNECT {}:{} HTTP/1.1\r\nHost: {}:{}\r\n\r\n".format(
                host, port, host, port)
            remote_writer.write(upstream_req.encode())
            await remote_writer.drain()
            # 读取上游响应
            resp_line = await asyncio.wait_for(remote_reader.readline(), timeout=15)
            writer.write(resp_line)
            await writer.drain()
            if not resp_line or b'200' not in resp_line.split(b' ', 2)[0:2]:
                _type = "PROXY_ERR"

        # 200 Connection Established（直连模式跳过 upstream 响应已经写了）
        if _type == "DIRECT":
            writer.write(b'HTTP/1.1 200 Connection Established\r\n\r\n')
            await writer.drain()

        logging.info("[{}][{}] {}:{}".format(_type, client_addr, host, port))

        # 双向中继
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


def start(listen_port=None, upstream_host=None, upstream_port=None):
    """启动路由代理（阻塞）"""
    global LISTEN_PORT, UPSTREAM_HOST, UPSTREAM_PORT

    # 从配置文件读取
    config_fp = os.path.join(home_dir, "config.json")
    if os.path.isfile(config_fp):
        try:
            cfg = json.load(open(config_fp))
            if listen_port is None:
                LISTEN_PORT = int(cfg.get("port", 7890))
            if upstream_host is None:
                UPSTREAM_HOST = cfg.get("upstream", {}).get("host", "")
            if upstream_port is None:
                UPSTREAM_PORT = int(cfg.get("upstream", {}).get("port", 0))
        except Exception as e:
            print("读取配置失败: {}".format(e), file=sys.stderr)

    # 命令行参数覆盖
    if listen_port is not None:
        LISTEN_PORT = listen_port
    if upstream_host is not None:
        UPSTREAM_HOST = upstream_host
    if upstream_port is not None:
        UPSTREAM_PORT = upstream_port

    if not UPSTREAM_HOST or not UPSTREAM_PORT:
        print("错误: 未配置上游代理地址", file=sys.stderr)
        sys.exit(1)

    async def _serve():
        server = await asyncio.start_server(_handle, LISTEN_HOST, LISTEN_PORT)
        addr = server.sockets[0].getsockname()
        logging.info("PFlowC router listening on {}:{}".format(*addr))
        logging.info("Upstream: {}:{}".format(UPSTREAM_HOST, UPSTREAM_PORT))
        async with server:
            await server.serve_forever()

    asyncio.run(_serve())
