# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/4/22
@Software: PyCharm
@disc:
======================================="""
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
import click

from PFlowC import get_version
from PFlowC.proxy_helper import set_all_proxy, clear_all_proxy
from PFlowC.utils import logger
from PFlowC.__version__ import __banner__
home_dir = os.path.expanduser("~/.PFlowC")
config_fp = os.path.join(home_dir, "config.json")
log_dir = os.path.join(home_dir, "logs")
logger.init("PFlowC", console_level=logging.INFO, log_dir=log_dir)
# alpha (https://www.bootschool.net/ascii)


def print_banner():
    click.secho(__banner__, fg='green', bold=True)
    click.secho("Command line interface for Proxy Flow Controller with basic auto configurations.", fg='yellow',
                bold=True)
    click.secho("Version: {}".format(get_version()) + " " * 20 + "By: BlackHaoke<Haoke98@outlook.com>", fg='red',
                bold=True)


print_banner()


class Config:
    def __init__(self):
        if not os.path.isfile(config_fp):
            logging.warning("upstream config file: {} does not exist.".format(config_fp))
            self.prompt()
        self.ctx: dict = json.load(open(config_fp))
        # 进行系统自检(配置自检)
        if self.ctx.__contains__("upstream") and self.ctx.__contains__("port") and self.ctx.__contains__(
                "bypass_domains"):
            pass
        else:
            self.prompt()

    def prompt(self):
        mixed_port = click.prompt("Input the port of the proxy.", default=7890, type=int)
        upstream_proxy_host = click.prompt("Input the upstream-proxy  host")
        upstream_proxy_port = click.prompt("Input the upstream-proxy  port")
        self.ctx = {
            "port": mixed_port,
            "upstream": {
                "host": upstream_proxy_host,
                "port": upstream_proxy_port
            },
            "bypass_domains": [
                "127.0.0.1",
                "192.168.0.0/16",
                "172.16.0.0/16",
                "10.0.0.0/8"
            ]}
        os.makedirs(os.path.dirname(config_fp), exist_ok=True)
        with open(config_fp, "w", encoding='utf-8') as f:
            json.dump(self.ctx, f, ensure_ascii=False)

    def get_port(self):
        pass

    def get_proxy_config(self):
        port = self.ctx["upstream"]["port"]
        ignores_list = self.ctx["bypass_domains"]
        bypass_domains = list(set(ignores_list))
        return "127.0.0.1", port, bypass_domains

    def get_upstream_proxy_address(self):
        upstream_proxy_host = self.ctx["upstream"]["host"]
        upstream_proxy_port = self.ctx["upstream"]["port"]
        return f"http://{upstream_proxy_host}:{upstream_proxy_port}"


@click.group()
def main():
    pass


@main.command(help="Version")
def version():
    print(get_version())


@main.command(help="Run proxy flow controller.")
def on():
    config = Config()
    set_all_proxy(*config.get_proxy_config())


@main.command(help="Set off and clear all proxy config.")
def off():
    clear_all_proxy()


@main.command(help="Server as the Agent service for the local device in same LAN networks.")
def server():
    config = Config()
    proxy_config = config.get_proxy_config()
    set_all_proxy(*proxy_config)
    upstream_proxy_address = config.get_upstream_proxy_address()
    fp = os.path.join(Path(__file__).parent, "geo_proxy.py")
    cmd = [
        "mitmdump", "--listen-port", str(proxy_config[1]), "--mode", f"upstream:{upstream_proxy_address}",
        "-s", fp,
    ]
    logging.debug("CMD:%s" % cmd)
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        logging.info("Server is now on!")
        # 循环读取输出并打印，使用更健壮的解码方式
        for line in iter(p.stdout.readline, b''):
            try:
                # 首先尝试 UTF-8
                decoded_line = line.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    # 如果 UTF-8 失败，尝试系统默认编码
                    decoded_line = line.decode('cp936')
                except UnicodeDecodeError:
                    # 如果还是失败，使用 'replace' 错误处理器
                    decoded_line = line.decode('utf-8', errors='replace')
            
            sys.stdout.write(decoded_line)
            sys.stdout.flush()
    except subprocess.CalledProcessError as e:
        logging.error("CallSubprocessFailed:%s" % e.stderr)


if __name__ == '__main__':
    main()
