# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/4/29
@Software: PyCharm
@disc:
======================================="""
import json
import logging
import os

from mitmproxy import http
import geoip2.database
import socket

from PFlowC.proxy_helper import set_bypass_domains

# GeoIP数据库文件路径
GEOIP_DB_PATH = '/Users/shadikesadamu/数据/geoip/Country.mmdb'

# 本地区域的国家代码，例如'CN'为中国
LOCAL_REGION_CODE = 'CN'

# 初始化GeoIP数据库
geoip_db = geoip2.database.Reader(GEOIP_DB_PATH)
home_dir = os.path.expanduser("~/.PFlowC")
bypass_domains_fp = os.path.join(home_dir, "bypass_domains.json")
if not os.path.isfile(bypass_domains_fp):
    logging.warning("bypass domains cache file[{}] does not exist.".format(bypass_domains_fp))
    bypass_domains = [
        "127.0.0.1",
        "192.168.0.0/16",
        "172.16.0.0/16",
        "10.0.0.0/8"
    ]
else:
    try:
        bypass_domains = json.load(open(bypass_domains_fp))
        # TODO: 加载时对在PROXY规则里, 但是由于时间关系, 之前被加入到DIRECT里的域名都要提取出来
        # TODO: 用户个人的BypassDomains列表也要进行汇入.
    except json.decoder.JSONDecodeError as e:
        logging.warning("BypassDomains缓存列表解析异常")
        bypass_domains = [
            "127.0.0.1",
            "192.168.0.0/16",
            "172.16.0.0/16",
            "10.0.0.0/8"
        ]


def is_local_region(ip):
    try:
        response = geoip_db.country(ip)
        return response.country.iso_code == LOCAL_REGION_CODE
    except geoip2.errors.AddressNotFoundError:
        return False


def request(flow: http.HTTPFlow) -> None:
    # 获取请求的目标IP地址
    # FIXME: 这里通过域名服务获取IP地址的方法要改成从特定的DNS获取, 直接从socket获取可能会因为不同的本地环境而导致出现异常.
    ip = socket.gethostbyname(flow.request.pretty_host)

    # 判断是否属于本地区域
    if is_local_region(ip):
        # 直接访问，不走上游代理
        print(
            f"[{flow.timestamp_start}][{flow.type}][mode:{flow.mode}][DIRECT][{ip} - {flow.request.pretty_host}][{flow.modified()}]")
        # 更新一下bypass_domains列表
        # TODO: 部分特殊域名要存在于官网规则中, 对他们进行过滤单独分离出来
        if not bypass_domains.__contains__(flow.request.pretty_host):
            bypass_domains.append(flow.request.pretty_host)
            set_bypass_domains(bypass_domains)
            with open(bypass_domains_fp, "w") as bypass_domains_file:
                json.dump(bypass_domains, bypass_domains_file, indent=4, ensure_ascii=False)
        # TODO: 收集到中央服务方便以后成为按地区分布代理流量控制缓存.
    else:
        print(
            f"[{flow.timestamp_start}][{flow.type}][mode:{flow.mode}][PROXY][{ip} - {flow.request.pretty_host}][{flow.modified()}]")
