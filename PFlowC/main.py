# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/7/30
@Software: PyCharm
@disc: FlowPilot v4.0 CLI — 多上游 + 直连模式 + 鉴权
======================================="""
import json
import logging
import os
import click

from PFlowC import get_version
from PFlowC.proxy_helper import set_all_proxy, clear_all_proxy
from PFlowC.utils import logger
from PFlowC.__version__ import __banner__

home_dir = os.path.expanduser("~/.PFlowC")
config_fp = os.path.join(home_dir, "config.json")
log_dir = os.path.join(home_dir, "logs")
logger.init("PFlowC", console_level=logging.INFO, log_dir=log_dir)


def print_banner():
    click.secho(__banner__, fg='green', bold=True)
    click.secho("Proxy Flow Controller v4.0 — 智能代理路由", fg='yellow', bold=True)
    click.secho("Version: {}   By: BlackHaoke<Haoke98@outlook.com>".format(get_version()),
                fg='red', bold=True)


print_banner()

# ═══════════════════════════════════════════════════════════
#  配置管理
# ═══════════════════════════════════════════════════════════

DEFAULT_CONFIG = {
    "port": 7890,
    "mode": "smart",
    "routing_strategy": "round_robin",
    "upstreams": [],
    "auth": {
        "enabled": False,
        "username": "",
        "password": "",
        "tokens": []
    },
    "bypass_domains": [
        "127.0.0.1",
        "192.168.0.0/16",
        "172.16.0.0/16",
        "10.0.0.0/8"
    ]
}


class Config:
    def __init__(self):
        os.makedirs(os.path.dirname(config_fp), exist_ok=True)
        if not os.path.isfile(config_fp):
            logging.warning("配置文件不存在: {}，创建默认配置".format(config_fp))
            self._write_default()
        self.load()

    def _write_default(self):
        with open(config_fp, "w", encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)

    def load(self):
        self.ctx = json.load(open(config_fp))

        # 迁移旧格式
        if "upstream" in self.ctx and "upstreams" not in self.ctx:
            u = self.ctx.pop("upstream")
            self.ctx["upstreams"] = [{
                "host": u.get("host", ""),
                "port": int(u.get("port", 0)),
                "protocol": "http",
                "username": "",
                "password": "",
                "weight": 1,
                "tags": "",
            }]
            self.save()

        # 确保必要字段存在
        for key, val in DEFAULT_CONFIG.items():
            if key not in self.ctx:
                self.ctx[key] = val
        if "auth" not in self.ctx:
            self.ctx["auth"] = DEFAULT_CONFIG["auth"]

    def save(self):
        with open(config_fp, "w", encoding='utf-8') as f:
            json.dump(self.ctx, f, ensure_ascii=False, indent=2)

    def get_port(self):
        return self.ctx.get("port", 7890)

    def get_proxy_config(self):
        port = self.get_port()
        bypass = list(set(self.ctx.get("bypass_domains", [])))
        return "127.0.0.1", port, bypass

    def get_mode(self):
        return self.ctx.get("mode", "smart")

    def get_upstreams(self):
        return self.ctx.get("upstreams", [])

    def get_strategy(self):
        return self.ctx.get("routing_strategy", "round_robin")

    def get_auth(self):
        return self.ctx.get("auth", DEFAULT_CONFIG["auth"])


config = Config()


# ═══════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════

@click.group()
def main():
    pass


@main.command(help="显示版本")
def version():
    print(get_version())


@main.command(help="配置交互式向导")
def setup():
    """交互式配置向导"""
    click.secho("═══ FlowPilot v4.0 配置向导 ═══", fg='cyan', bold=True)

    # 端口
    port = click.prompt("监听端口", default=config.get_port(), type=int)

    # 运行模式
    mode = click.prompt(
        "运行模式 (smart=GeoIP分流 / direct=全局直连)",
        default=config.get_mode(), type=click.Choice(["smart", "direct"])
    )

    config.ctx["port"] = port
    config.ctx["mode"] = mode

    if mode == "smart":
        # 上游代理
        upstreams = []
        click.secho("\n配置上游代理（留空主机名结束）:", fg='yellow')
        while True:
            host = click.prompt("  上游主机 (回车结束)", default="")
            if not host:
                break
            port_u = click.prompt("  上游端口", type=int)
            protocol = click.prompt("  协议 (http/https/socks5)", default="http")
            username = click.prompt("  认证用户名 (可选)", default="")
            password = click.prompt("  认证密码 (可选)", default="", hide_input=True) if username else ""
            tags = click.prompt("  标签 (如: us/jp/hk, 可选)", default="")
            upstreams.append({
                "host": host,
                "port": port_u,
                "protocol": protocol,
                "username": username,
                "password": password,
                "weight": 1,
                "tags": tags,
            })
            click.secho("  ✓ 已添加 {}/{}:{}".format(protocol, host, port_u), fg='green')
            if not click.confirm("  继续添加?", default=False):
                break

        config.ctx["upstreams"] = upstreams

        # 路由策略
        strategy = click.prompt(
            "\n路由策略",
            default=config.get_strategy(),
            type=click.Choice(["round_robin", "random", "lowest_latency", "geoip_preferred"])
        )
        config.ctx["routing_strategy"] = strategy

    # 鉴权
    click.secho("\n鉴权配置:", fg='yellow')
    auth_enabled = click.confirm("启用鉴权?", default=config.get_auth().get("enabled", False))
    if auth_enabled:
        auth_type = click.prompt("鉴权方式 (basic/token)", default="basic",
                                 type=click.Choice(["basic", "token"]))
        if auth_type == "basic":
            auth_user = click.prompt("用户名")
            auth_pass = click.prompt("密码", hide_input=True)
            config.ctx["auth"] = {
                "enabled": True,
                "username": auth_user,
                "password": auth_pass,
                "tokens": []
            }
        else:
            token = click.prompt("Token")
            config.ctx["auth"] = {
                "enabled": True,
                "username": "",
                "password": "",
                "tokens": [token]
            }
    else:
        config.ctx["auth"] = DEFAULT_CONFIG["auth"]

    config.save()
    click.secho("\n✓ 配置已保存到 {}".format(config_fp), fg='green', bold=True)


@main.command(help="查看当前配置")
def show_config():
    """打印当前配置"""
    click.secho("═══ 当前配置 ═══", fg='cyan', bold=True)
    click.echo("  监听端口: {}".format(config.get_port()))
    click.echo("  运行模式: {}".format(config.get_mode()))

    if config.get_mode() == "smart":
        us = config.get_upstreams()
        click.echo("  上游代理: {} 个".format(len(us)))
        click.echo("  路由策略: {}".format(config.get_strategy()))
        for i, u in enumerate(us):
            auth_str = " (需认证)" if u.get("username") else ""
            tags_str = " [{}]".format(u.get("tags")) if u.get("tags") else ""
            click.echo("    {}. {}://{}:{}{}{}".format(
                i + 1, u.get("protocol", "http"), u["host"], u["port"], tags_str, auth_str))

    auth = config.get_auth()
    click.echo("  鉴权: {}".format("✓ 已启用" if auth.get("enabled") else "✗ 未启用"))


@main.command(help="启动代理路由服务")
@click.option("--port", "-p", type=int, help="监听端口")
@click.option("--mode", "-m", type=click.Choice(["smart", "direct"]), help="运行模式")
@click.option("--strategy", "-s", type=click.Choice(["round_robin", "random", "lowest_latency", "geoip_preferred"]),
              help="路由策略（仅 smart 模式）")
def server(port, mode, strategy):
    """启动路由代理"""
    from PFlowC.router import start
    logging.info("启动 FlowPilot v4.0 ...")
    start(
        listen_port=port or config.get_port(),
        mode=mode or config.get_mode(),
        upstreams=config.get_upstreams(),
        strategy=strategy or config.get_strategy(),
        auth_config=config.get_auth(),
    )


@main.command(help="Run proxy flow controller.")
def on():
    set_all_proxy(*config.get_proxy_config())


@main.command(help="Set off and clear all proxy config.")
def off():
    clear_all_proxy()


if __name__ == '__main__':
    main()
