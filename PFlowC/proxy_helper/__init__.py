# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/4/26
@Software: PyCharm
@disc:
======================================="""

import platform


def set_bypass_domains(bypass_domains):
    if platform.system() == "Darwin":
        from PFlowC.proxy_helper.macosx import set_bypass_domains
        set_bypass_domains(bypass_domains)


def set_all_proxy(host, port, bypass_domains):
    if platform.system() == "Darwin":
        from PFlowC.proxy_helper.macosx import set_web_proxy, set_cmd_proxy
        set_web_proxy(host, port, bypass_domains)
        set_cmd_proxy(host, port, bypass_domains)


def clear_all_proxy():
    if platform.system() == "Darwin":
        from PFlowC.proxy_helper.macosx import stop_web_proxy, clear_cmd_proxy
        stop_web_proxy()
        clear_cmd_proxy()
