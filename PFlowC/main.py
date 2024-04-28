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

import click

from PFlowC import get_version
from PFlowC.proxy_helper.macosx import set_web_proxy, set_cmd_proxy, stop_web_proxy, clear_cmd_proxy
from PFlowC.utils import logger

home_dir = os.path.expanduser("~/.PFlowC")
config_fp = os.path.join(home_dir, "config.json")
log_dir = os.path.join(home_dir, "logs")
logger.init("PFlowC", console_level=logging.INFO, log_dir=log_dir)


@click.group(
    help="Command line interface for Proxy Flow Controller with basic auto configurations.\nVersion: {}".format(
        get_version()))
def main():
    pass


@main.command(help="Version")
def version():
    print(get_version())


@main.command(help="Run proxy flow controller.")
def on():
    if not os.path.isfile(config_fp):
        logging.warning("upstream config file: {} does not exist.".format(config_fp))
        host = click.prompt("Input the proxy upstream host")
        port = click.prompt("Input the proxy upstream port")
        config = {"host": host, "port": port, "bypass_domains": [
            "127.0.0.1",
            "192.168.0.0/16",
            "172.16.0.0/16",
            "10.0.0.0/8"
        ]}
        os.makedirs(os.path.dirname(config_fp), exist_ok=True)
        with open(config_fp, "w", encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False)
    else:
        config = json.load(open(config_fp))
    host = config["host"]
    port = config["port"]
    ignores_list = config["bypass_domains"]
    bypass_domains = list(set(ignores_list))
    set_web_proxy(host, port, bypass_domains)
    set_cmd_proxy(host, port, bypass_domains)


@main.command()
def off():
    stop_web_proxy()
    clear_cmd_proxy()


if __name__ == '__main__':
    main()
