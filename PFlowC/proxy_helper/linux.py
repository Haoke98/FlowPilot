# _*_ coding:utf8 _*_
"""Linux 系统代理配置"""

import logging
import os
import subprocess

SHELL_RC_FILES = [".zshrc", ".bashrc", ".profile"]


def _write_env_to_rc(env_vars: dict, clear: bool = False):
    """写入/清除 shell 配置文件中的环境变量"""
    for rc_file in SHELL_RC_FILES:
        fp = os.path.expanduser(f"~/{rc_file}")
        if not os.path.isfile(fp):
            continue
        with open(fp, "r+") as f:
            lines = f.readlines()
            updated = []
            for line in lines:
                if not any(f"{key}=" in line for key in ["http_proxy=", "https_proxy=", "HTTP_PROXY=", "HTTPS_PROXY=", "all_proxy=", "ALL_PROXY=", "no_proxy=", "NO_PROXY="]):
                    updated.append(line)
            if not clear and env_vars:
                for k, v in env_vars.items():
                    updated.append(f'export {k}="{v}"\n')
            f.seek(0)
            f.truncate()
            f.writelines(updated)


def set_web_proxy(host: str, port: int, bypass_domains: list):
    """设置 Linux 系统代理（环境变量 + gsettings）"""
    proxy_url = f"http://{host}:{port}"
    no_proxy = ",".join(bypass_domains)

    # 写入 shell 配置文件
    _write_env_to_rc({
        "http_proxy": proxy_url,
        "https_proxy": proxy_url,
        "HTTP_PROXY": proxy_url,
        "HTTPS_PROXY": proxy_url,
        "no_proxy": no_proxy,
        "NO_PROXY": no_proxy,
    })

    # 尝试 GNOME gsettings
    try:
        subprocess.run(["gsettings", "set", "org.gnome.system.proxy", "mode", "manual"],
                       capture_output=True, timeout=5)
        subprocess.run(["gsettings", "set", "org.gnome.system.proxy.http", "host", host],
                       capture_output=True, timeout=5)
        subprocess.run(["gsettings", "set", "org.gnome.system.proxy.http", "port", str(port)],
                       capture_output=True, timeout=5)
        subprocess.run(["gsettings", "set", "org.gnome.system.proxy.https", "host", host],
                       capture_output=True, timeout=5)
        subprocess.run(["gsettings", "set", "org.gnome.system.proxy.https", "port", str(port)],
                       capture_output=True, timeout=5)
        # Ignore hosts
        subprocess.run(["gsettings", "set", "org.gnome.system.proxy", "ignore-hosts",
                        str([d for d in bypass_domains])], capture_output=True, timeout=5)
    except Exception:
        pass  # gsettings not available

    logging.info(f"Linux 代理已设置: {proxy_url}")


def stop_web_proxy():
    """清除 Linux 系统代理"""
    _write_env_to_rc({}, clear=True)

    try:
        subprocess.run(["gsettings", "set", "org.gnome.system.proxy", "mode", "none"],
                       capture_output=True, timeout=5)
    except Exception:
        pass

    logging.info("Linux 代理已清除")


def set_cmd_proxy(host, port, bypass_domains):
    """写入环境变量到 shell 配置（同 set_web_proxy 的 shell 部分）"""
    proxy_url = f"http://{host}:{port}"
    no_proxy = ",".join(bypass_domains)
    _write_env_to_rc({
        "http_proxy": proxy_url,
        "https_proxy": proxy_url,
        "HTTP_PROXY": proxy_url,
        "HTTPS_PROXY": proxy_url,
        "no_proxy": no_proxy,
        "NO_PROXY": no_proxy,
    })


def clear_cmd_proxy():
    _write_env_to_rc({}, clear=True)
