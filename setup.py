# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/4/28
@Software: PyCharm
@disc:
======================================="""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from PFlowC import __version__

long_description = open('README.rst', encoding='utf-8').read()

setup(
    name='PFlowC',
    version=__version__.__version__,
    url=__version__.__url__,
    author=__version__.__author__,
    author_email=__version__.__author_email__,
    license=__version__.__license__,
    description=__version__.__description__,
    packages=["PFlowC", "PFlowC.utils", "PFlowC.proxy_helper"],
    install_requires=['colorlog', 'click', 'mitmproxy>=10.3.0', 'geoip2>=4.8.0', 'dnspython>=2.6.1'],
    package_data={
        'PFlowC.utils': ['Country.mmdb'],
    },
    include_package_data=True,
    python_requires='>=3.7',
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Visualization",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords="proxy flow control",
    entry_points={
        'console_scripts': [
            'pflow-cli=PFlowC.main:main',
            'proxy-cli=PFlowC.proxy:main',
        ],
    },
)
