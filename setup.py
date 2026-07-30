# _*_ coding:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/7/30
@Software: PyCharm
@disc:
======================================="""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from PFlowC.__version__ import (
    __version__, __url__, __author__, __author_email__,
    __license__, __description__,
)

long_description = open('README.md', encoding='utf-8').read()

setup(
    name='PFlowC',
    version=__version__,
    url=__url__,
    author=__author__,
    author_email=__author_email__,
    license=__license__,
    description=__description__,
    packages=["PFlowC", "PFlowC.utils", "PFlowC.proxy_helper"],
    install_requires=['click', 'colorlog', 'geoip2>=4.8.0', 'dnspython>=2.6.1',
                      'python-dotenv>=1.0.0'],
    package_data={
        'PFlowC.utils': ['Country.mmdb'],
    },
    include_package_data=True,
    python_requires='>=3.8',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: Proxy Servers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="proxy flow control geoip routing",
    entry_points={
        'console_scripts': [
            'pflow-cli=PFlowC.main:main',
            'proxy-cli=PFlowC.proxy:main',
        ],
    },
)
