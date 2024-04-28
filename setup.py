# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/4/28
@Software: PyCharm
@disc:
======================================="""
import pip
import logging
import pkg_resources

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def _parse_requirements(file_path):
    pip_ver = pkg_resources.get_distribution('pip').version
    pip_version = list(map(int, pip_ver.split('.')[:2]))
    if pip_version >= [6, 0]:
        raw = pip.req.parse_requirements(file_path,
                                         session=pip.download.PipSession())
    else:
        raw = pip.req.parse_requirements(file_path)
    return [str(i.req) for i in raw]


# parse_requirements() returns generator of pip.req.InstallRequirement objects
try:
    install_reqs = _parse_requirements("requirements.txt")
except Exception:
    logging.warning('Fail load requirements file, so using default ones.')
    install_reqs = []

long_description = open('README.rst').read()

setup(
    name='PFlowC',
    version='1.4.1',
    url='https://github.com/Haoke98/FlowPilot',
    author='Haoke98',
    author_email='BlackHaoke<Haoke98@outlook.com>',
    license='MIT',
    description='https://github.com/Haoke98/FlowPilot/README.md',
    packages=["PFlowC", "PFlowC.utils", "PFlowC.proxy_helper"],
    install_requires=install_reqs,
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
