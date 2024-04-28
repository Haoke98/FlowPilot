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
# alpha (https://www.bootschool.net/ascii)
banner_txt = """
          _____                    _____                    _____           _______                   _____                    _____          
         /\    \                  /\    \                  /\    \         /::\    \                 /\    \                  /\    \         
        /::\    \                /::\    \                /::\____\       /::::\    \               /::\____\                /::\    \        
       /::::\    \              /::::\    \              /:::/    /      /::::::\    \             /:::/    /               /::::\    \       
      /::::::\    \            /::::::\    \            /:::/    /      /::::::::\    \           /:::/   _/___            /::::::\    \      
     /:::/\:::\    \          /:::/\:::\    \          /:::/    /      /:::/~~\:::\    \         /:::/   /\    \          /:::/\:::\    \     
    /:::/__\:::\    \        /:::/__\:::\    \        /:::/    /      /:::/    \:::\    \       /:::/   /::\____\        /:::/  \:::\    \    
   /::::\   \:::\    \      /::::\   \:::\    \      /:::/    /      /:::/    / \:::\    \     /:::/   /:::/    /       /:::/    \:::\    \   
  /::::::\   \:::\    \    /::::::\   \:::\    \    /:::/    /      /:::/____/   \:::\____\   /:::/   /:::/   _/___    /:::/    / \:::\    \  
 /:::/\:::\   \:::\____\  /:::/\:::\   \:::\    \  /:::/    /      |:::|    |     |:::|    | /:::/___/:::/   /\    \  /:::/    /   \:::\    \ 
/:::/  \:::\   \:::|    |/:::/  \:::\   \:::\____\/:::/____/       |:::|____|     |:::|    ||:::|   /:::/   /::\____\/:::/____/     \:::\____\
\::/    \:::\  /:::|____|\::/    \:::\   \::/    /\:::\    \        \:::\    \   /:::/    / |:::|__/:::/   /:::/    /\:::\    \      \::/    /
 \/_____/\:::\/:::/    /  \/____/ \:::\   \/____/  \:::\    \        \:::\    \ /:::/    /   \:::\/:::/   /:::/    /  \:::\    \      \/____/ 
          \::::::/    /            \:::\    \       \:::\    \        \:::\    /:::/    /     \::::::/   /:::/    /    \:::\    \             
           \::::/    /              \:::\____\       \:::\    \        \:::\__/:::/    /       \::::/___/:::/    /      \:::\    \            
            \::/____/                \::/    /        \:::\    \        \::::::::/    /         \:::\__/:::/    /        \:::\    \           
             ~~                       \/____/          \:::\    \        \::::::/    /           \::::::::/    /          \:::\    \          
                                                        \:::\    \        \::::/    /             \::::::/    /            \:::\    \         
                                                         \:::\____\        \::/____/               \::::/    /              \:::\____\        
                                                          \::/    /         ~~                      \::/____/                \::/    /        
                                                           \/____/                                   ~~                       \/____/         

"""
# ansi_shadow (https://www.bootschool.net/ascii)
banner_txt = """
██████╗ ███████╗██╗      ██████╗ ██╗    ██╗ ██████╗
██╔══██╗██╔════╝██║     ██╔═══██╗██║    ██║██╔════╝
██████╔╝█████╗  ██║     ██║   ██║██║ █╗ ██║██║     
██╔═══╝ ██╔══╝  ██║     ██║   ██║██║███╗██║██║     
██║     ██║     ███████╗╚██████╔╝╚███╔███╔╝╚██████╗
╚═╝     ╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝  ╚═════╝
"""


def print_banner():
    click.secho(banner_txt, fg='green', bold=True)
    click.secho("Command line interface for Proxy Flow Controller with basic auto configurations.", fg='yellow',bold=True)
    click.secho("Version: {}".format(get_version())+" "*20+"By: BlackHaoke<Haoke98@outlook.com>", fg='red', bold=True)


print_banner()


@click.group()
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


@main.command(help="Set off and clear all proxy config.")
def off():
    stop_web_proxy()
    clear_cmd_proxy()


if __name__ == '__main__':
    main()
