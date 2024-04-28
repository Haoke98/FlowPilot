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
import os


def set_cmd_proxy(host, port, bypass_domains: list[str], env_rc_files: list[str] = [".zshrc", ".bashrc"]):
    # 新的代理服务器设置
    http_proxy_url = "http://{}:{}".format(host, port)
    https_proxy_url = "http://{}:{}".format(host, port)
    no_proxy_domains = ",".join(bypass_domains)
    for env_rc_file in env_rc_files:
        # 要编辑的文件路径
        env_rc_fp = os.path.expanduser(f"~/{env_rc_file}")

        # 检查并读取文件内容
        if not os.path.isfile(env_rc_fp):
            pass
        else:
            with open(env_rc_fp, "r+") as zshrc_file:
                lines = zshrc_file.readlines()
                updated_lines = []

                # 查找并移除旧的代理设置
                for line in lines:
                    if not (
                            ("http_proxy=" in line)
                            or ("https_proxy=" in line)
                            or ("no_proxy=" in line)
                    ):
                        updated_lines.append(line)

                # 添加新的代理设置
                updated_lines.append("\n# 更新代理设置\n")
                updated_lines.append(f"export http_proxy=\"{http_proxy_url}\"\n")
                updated_lines.append(f"export https_proxy=\"{https_proxy_url}\"\n")
                updated_lines.append(f"export no_proxy=\"{no_proxy_domains}\"\n")

                # 将更新后的行重写回文件
                zshrc_file.seek(0)
                zshrc_file.truncate()
                zshrc_file.writelines(updated_lines)

            logging.info(f"代理设置已在{env_rc_file}文件中更新，请运行 'source ~/{env_rc_file}' 以应用新的环境变量设置。")


def get_network_services():
    """
    利用 networksetup的 -listallnetworkservices 参数来获取并自动遍历出 networservices.
    """

    try:
        # 调用networksetup命令并使用-listallnetworkservices选项来列出所有网络服务
        output = subprocess.check_output(["networksetup", "-listallnetworkservices"])
        # 将输出从字节串转换为字符串，并按行分割
        network_services = output.decode("utf-8").strip().split("\n")
        # 过滤掉可能的空行
        res = []
        for service in network_services:
            if service and "is disabled" not in service:
                res.append(service)
        return res
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return []


def set_web_proxy(host, port: int, bypass_domains: list[str]):
    """
    Apply the settings using 'networksetup'
    :param host:
    :param port:
    :param bypass_domains:
    :return:
    """
    # 利用 networksetup的 -listallnetworkservices 参数来获取并自动遍历出 networservices.
    network_services = get_network_services()
    logging.info(f"network services:{network_services}")
    for service in network_services:
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
