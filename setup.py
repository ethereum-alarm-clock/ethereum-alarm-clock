#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages


DIR = os.path.dirname(os.path.abspath(__file__))


version = '8.0.0b1'

setup(
    name='ethereum-alarm-clock-client',
    version=version,
    description="""Ethereum Alarm Clock""",
    long_description="Ethereum Alarm Clock service",
    author='Piper Merriam',
    author_email='pipermerriam@gmail.com',
    url='http://www.ethereum-alarm-clock.com',
    include_package_data=True,
    py_modules=['eth_alarm_client'],
    install_requires=[
        "populus>=1.2.1",
        "web3>=3.0.1",
        "pylru>=1.0.9",
        "python-dotenv>=0.6.0",
    ],
    license="MIT",
    zip_safe=False,
    keywords='ethereum',
    packages=find_packages(exclude=["tests", "tests.*"]),
    entry_points={
        'console_scripts': ["eth_alarm=alarm_client.cli:main"],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
)
