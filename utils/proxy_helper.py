# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/4/26
@Software: PyCharm
@disc:
======================================="""
import logging
import subprocess


def set_proxy_config(host, port: int, bypass_domains: list[str]):
    """
    Apply the settings using 'networksetup'
    :param host:
    :param port:
    :param bypass_domains:
    :return:
    """
    # TODO: 实现 利用 networksetup的 -listallnetworkservices 参数来获取并自动遍历出 networservices.
    for service in ["Wi-Fi", "USB 10/100 LAN", "USB 10/100 LAN 2", "USB 10/100 LAN 3"]:
        for proxy_type in ["webproxy", "securewebproxy", "socksfirewallproxy"]:
            cmd = ["/usr/sbin/networksetup", "-set" + proxy_type, service, host, str(port)]
            resp = subprocess.run(cmd, check=True)
            if resp.returncode != 0:
                logging.error(f"执行{cmd}时发生异常!")
        cmd = ["/usr/sbin/networksetup", "-setproxybypassdomains", service, *bypass_domains]
        resp = subprocess.run(cmd)
        if resp.returncode != 0:
            logging.error(f"执行{cmd}时发生异常!")
        logging.info(f"网络[{service}]配置代理成功!")
