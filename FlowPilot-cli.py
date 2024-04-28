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

from utils import logger
from utils.proxy_helper.macosx import set_web_proxy, set_cmd_proxy


@click.command(help="Command line interface for FlowPilot")
def main():
    config_fp = os.path.expanduser("~/.flowPilot/config.json")
    if not os.path.isfile(config_fp):
        click.echo("upstream config file: {} does not exist.".format(config_fp))
        host = click.prompt("Input the proxy upstream host")
        port = click.prompt("Input the proxy upstream port")
        config = {"host": host, "port": port}
        os.makedirs(os.path.dirname(config_fp), exist_ok=True)
        with open(config_fp, "w", encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False)
    else:
        config = json.load(open(config_fp))
    host = config["host"]
    port = config["port"]
    ignores_list = []
    ignores_fps = os.listdir('ignores')
    for fn in ignores_fps:
        fp = os.path.join('ignores', fn)
        with open(fp, 'r') as f:
            _list = json.load(f)
            print(fp, _list)
            ignores_list.extend(_list)
    bypass_domains = list(set(ignores_list))
    set_web_proxy(host, port, bypass_domains)
    set_cmd_proxy(host, port, bypass_domains)


if __name__ == '__main__':
    logger.init("FlowPilot", console_level=logging.INFO)
    main()
