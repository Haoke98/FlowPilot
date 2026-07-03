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


def set_git_proxy(host, port):
    """设置 Git 全局代理（全平台通用）"""
    proxy_url = "http://{}:{}".format(host, port)
    try:
        subprocess.run(["git", "config", "--global", "http.proxy", proxy_url], check=True)
        subprocess.run(["git", "config", "--global", "https.proxy", proxy_url], check=True)
        msg = "Git 全局代理已设置为 {}".format(proxy_url)
        logging.info(msg)
        print(msg)
    except subprocess.CalledProcessError as e:
        msg = "Git 代理设置失败: {}".format(e)
        logging.error(msg)
        print(msg)


def clear_git_proxy():
    """清除 Git 全局代理（全平台通用）"""
    try:
        subprocess.run(["git", "config", "--global", "--unset", "http.proxy"], check=False)
        subprocess.run(["git", "config", "--global", "--unset", "https.proxy"], check=False)
        msg = "Git 全局代理已清除"
        logging.info(msg)
        print(msg)
    except subprocess.CalledProcessError as e:
        msg = "Git 代理清除失败: {}".format(e)
        logging.error(msg)
        print(msg)
