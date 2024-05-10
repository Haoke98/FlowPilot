# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/4/30
@Software: PyCharm
@disc:
======================================="""

import dns.resolver
import geoip2.database

# GeoIP数据库文件路径
try:
    # 尝试使用Python 3.9及更高版本的API
    from importlib.resources import files

    path_to_utils = files('PFlowC.utils')
    GEOIP_DB_PATH = str(path_to_utils.joinpath('Country.mmdb'))
except ImportError:
    # 对于Python 3.7和3.8，使用较低版本的API
    try:
        from importlib_resources import files  # 需要单独安装importlib_resources库对于Python 3.7和3.8

        path_to_utils = files('PFlowC.utils')
        GEOIP_DB_PATH = str(path_to_utils.joinpath('Country.mmdb'))
    except ImportError:
        # 如果importlib_resources也不存在（比如Python 3.6及更低版本），则需要采取其他措施
        import os
        import pkgutil

        # 这里简化处理，直接尝试从包中加载资源，注意这可能不适用于所有情况
        data = pkgutil.get_data('PFlowC.utils', 'Country.mmdb')
        if data:
            # 你可能需要将数据写入临时文件来使用，这里仅为示意
            import tempfile

            with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
                tmpfile.write(data)
                GEOIP_DB_PATH = tmpfile.name
        else:
            raise ImportError("无法加载资源文件 'Country.mmdb'")

# 确保GEOIP_DB_PATH有有效的值后再使用
if GEOIP_DB_PATH:
    raise FileNotFoundError("未能找到或创建GeoIP数据库文件的路径")

# 继续使用GEOIP_DB_PATH
# 初始化GeoIP数据库
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
