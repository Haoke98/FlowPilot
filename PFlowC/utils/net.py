# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/4/30
@Software: PyCharm
@disc:
======================================="""
import geoip2.database

# GeoIP数据库文件路径
try:
    from importlib.resources import files
    path_to_utils = files('PFlowC.utils')
    GEOIP_DB_PATH = str(path_to_utils.joinpath('Country.mmdb'))
except ImportError:
    try:
        from importlib_resources import files
        path_to_utils = files('PFlowC.utils')
        GEOIP_DB_PATH = str(path_to_utils.joinpath('Country.mmdb'))
    except ImportError:
        import os
        import pkgutil
        data = pkgutil.get_data('PFlowC.utils', 'Country.mmdb')
        if data:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
                tmpfile.write(data)
                GEOIP_DB_PATH = tmpfile.name
        else:
            raise ImportError("无法加载资源文件 'Country.mmdb'")

if not GEOIP_DB_PATH:
    raise FileNotFoundError("未能找到或创建GeoIP数据库文件的路径")

# 初始化GeoIP数据库（供 router.py 使用）
geoip_db = geoip2.database.Reader(GEOIP_DB_PATH)
