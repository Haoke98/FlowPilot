# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/4/26
@Software: PyCharm
@disc:
======================================="""

import platform
from PFlowC.proxy_helper.git import set_git_proxy, clear_git_proxy


def set_bypass_domains(bypass_domains):
    if platform.system() == "Darwin":
        from PFlowC.proxy_helper.macosx import set_bypass_domains
        set_bypass_domains(bypass_domains)


def set_all_proxy(host, port, bypass_domains):
    if platform.system() == "Darwin":
        from PFlowC.proxy_helper.macosx import set_web_proxy, set_cmd_proxy
        set_web_proxy(host, port, bypass_domains)
        set_cmd_proxy(host, port, bypass_domains)
    # Git 代理全平台通用
    set_git_proxy(host, port)


def clear_all_proxy():
    if platform.system() == "Darwin":
        from PFlowC.proxy_helper.macosx import stop_web_proxy, clear_cmd_proxy
        stop_web_proxy()
        clear_cmd_proxy()
    # Git 代理全平台通用
    clear_git_proxy()
