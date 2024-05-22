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
import socket

from mitmproxy import http

from PFlowC.proxy_helper import set_bypass_domains
from PFlowC.utils.net import is_domestic2

# 本地区域的国家代码，例如'CN'为中国
LOCAL_REGION_CODE = 'CN'
DEFAULT_BYPASS_DOMAINS = [
    # LOCAL Address
    "127.0.0.1",
    "192.168.0.0/16",
    "172.16.0.0/16",
    "10.0.0.0/8",
    # DNS
    '223.5.5.5',
    '119.29.29.29',
    'doh.pub',
    'dns.alidns.com',
]
DOMAINS = {
    "CN": [
        # TODO:不要用记下IP地址, 因为GeoIP就能够分辨IP地址的区域划分.
        "218.31.113.0/24"
    ],
    "US": [
        "github.com",
        "api.github.com",
        "collector.github.com"
    ]
}

home_dir = os.path.expanduser("~/.PFlowC")
bypass_domains_fp = os.path.join(home_dir, "bypass_domains.json")
bypass_domains = set()
if not os.path.isfile(bypass_domains_fp):
    print("bypass domains cache file[{}] does not exist.".format(bypass_domains_fp))
else:
    try:
        bypass_domains = set(json.load(open(bypass_domains_fp)))
        # TODO: 加载时对在PROXY规则里, 但是由于时间关系, 之前被加入到DIRECT里的域名都要提取出来
        # TODO: 用户个人的BypassDomains列表也要进行汇入.
    except json.decoder.JSONDecodeError as e:
        print("BypassDomains缓存列表解析异常")


def save_bypass_domains():
    with open(bypass_domains_fp, "w") as bypass_domains_file:
        json.dump(list(bypass_domains), bypass_domains_file, indent=4, ensure_ascii=False)


for item in DEFAULT_BYPASS_DOMAINS:
    bypass_domains.add(item)
for domain in DOMAINS[LOCAL_REGION_CODE]:
    bypass_domains.add(domain)
set_bypass_domains(bypass_domains)


def is_exact_other_region(host):
    for country_code, domains in DOMAINS.items():
        if country_code != LOCAL_REGION_CODE:
            if host in domains:
                return True
    return False


def request(flow: http.HTTPFlow) -> None:
    # 获取请求的目标IP地址
    # 这里通过域名服务获取IP地址的方法要改成从特定的DNS获取, 直接从socket获取可能会因为不同的本地环境而导致出现异常.
    # 判断是否属于本地区域
    ip = socket.gethostbyname(flow.request.pretty_host)
    _type = "PROXY"
    if is_exact_other_region(flow.request.pretty_host):
        _type = "PROXY"
    else:
        # 直接访问，不走上游代理
        if is_domestic2(flow.request.pretty_host, LOCAL_REGION_CODE):
            _type = "PROXY ===To===> DIRECT"
            # 需要更新一下bypass_domains列表
            # TODO: 部分特殊域名要存在于官网规则中, 对他们进行过滤单独分离出来
            bypass_domains.add(flow.request.pretty_host)
            set_bypass_domains(bypass_domains)
            save_bypass_domains()
            # TODO: 收集到中央服务方便以后成为按地区分布代理流量控制缓存.
    logging.info(f"[{flow.timestamp_start}][{flow.type}][mode:{flow.mode}][{_type}][{ip} - {flow.request.pretty_host}]")
