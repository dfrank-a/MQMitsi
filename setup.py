#!/usr/bin/env python
from setuptools import setup

setup(
    name="mitsubishi",
    version="1.0.0",
    description="Mitsubishi heat pump controller",
    install_requires=[],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Environment :: Console'
    ],
    packages=["mitsubishi"],
    entry_points={
        'console_scripts': []
    }
)