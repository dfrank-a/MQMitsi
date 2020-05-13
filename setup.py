#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="growroom",
    version="1.0.0",
    description="Grow room controller",
    install_requires=[
        "adafruit-circuitpython-dht==3.4.1",
        "paho-mqtt==1.4.0",
        "pyserial==3.4"
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Environment :: Console'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': ["growroom=growroom:main"]
    }
)