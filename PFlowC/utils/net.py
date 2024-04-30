# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/4/30
@Software: PyCharm
@disc:
======================================="""
import os
from pathlib import Path

import dns.resolver
import geoip2.database
import importlib.resources as pkg_resources

GEOIP_DB_PATH = str(pkg_resources.path('PFlowC.utils', 'Country.mmdb'))
geoip_db = geoip2.database.Reader(GEOIP_DB_PATH)
# 初始化DNS解析器
resolver = dns.resolver.Resolver()
resolver.nameservers = ['223.5.5.5', '119.29.29.29', 'https://doh.pub/dns-query',
                        'https://dns.alidns.com/dns-query']


def resolve(domain_name: str, max_count: int = 20):
    ips = {}
    for i in range(max_count):
        answers = resolver.resolve(domain_name, 'A')
        for rdata in answers:
            try:
                response = geoip_db.country(rdata.address)
                ips[rdata.address] = response.country.iso_code
            except geoip2.errors.AddressNotFoundError as e:
                pass
    return ips


def is_domestic(domain_name: str, max_try=10, target_country_code: str = "CN") -> bool:
    count = 0
    print(f"{domain_name} 的A记录指向IP地址:")
    result = resolve(domain_name, max_count=max_try)
    for ip in result:
        print(" " * 10, "+", "-" * 10, f"{ip}", result[ip])
        if result[ip] == target_country_code:
            count += 1
    score = count / len(result.keys())
    return score > 0.5


def is_domestic2(domain_name: str, max_try=10, target_country_code: str = "CN"):
    for i in range(max_try):
        answers = resolver.resolve(domain_name, 'A')
        for rdata in answers:
            try:
                response = geoip_db.country(rdata.address)
                if response.country.iso_code == target_country_code:
                    pass
                else:
                    return False
            except geoip2.errors.AddressNotFoundError as e:
                pass
    return True
