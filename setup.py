#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

DIR = os.path.dirname(os.path.abspath(__file__))

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

version = '0.1.0'

setup(
    name='ethereum-alarm-clock-client',
    version=version,
    description="""Ethereum JSON RPC Client""",
    long_description="client for the ethereum-alarm-clock-service",
    author='Piper Merriam',
    author_email='pipermerriam@gmail.com',
    url='http://www.ethereum-alarm-clock.com',
    include_package_data=True,
    py_modules=['eth_alarm_client'],
    install_requires=[
        "populus",
    ],
    license="MIT",
    zip_safe=False,
    keywords='ethereum',
    packages=find_packages(exclude=["tests", "tests.*"]),
    entry_points={
        'console_scripts': ["eth_alarm=eth_alarm_client.cli:main"],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
