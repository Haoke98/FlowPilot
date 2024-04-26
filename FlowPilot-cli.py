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

from utils import logger
from utils.proxy_helper import set_proxy_config

if __name__ == '__main__':
    logger.init("FlowPilot", console_level=logging.INFO)
    host = "10.2.1.0"
    port = 7890
    ignores_list = []
    ignores_fps = os.listdir('ignores')
    for fn in ignores_fps:
        fp = os.path.join('ignores', fn)
        with open(fp, 'r') as f:
            _list = json.load(f)
            print(fp, _list)
            ignores_list.extend(_list)
    bypass_domains = list(set(ignores_list))
    set_proxy_config(host, port, bypass_domains)
    print("export http_proxy={}".format(host))
    print("export https_proxy={}".format(port))
    # 控制台不支持范型和通配符, 必须是确切的域名
    print(f'export no_proxy="%s"' % (",".join(bypass_domains)))
