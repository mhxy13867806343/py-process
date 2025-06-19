#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="py-process-monitor",
    version="1.0.0",
    author="hooksvue",
    author_email="hooksvue@example.com",
    description="A Python package to monitor and manage processes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hooksvue/py-process-monitor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
    install_requires=[
        "psutil>=5.9.0",
    ],
    entry_points={
        "console_scripts": [
            "process-monitor=process_monitor.cli:main",
        ],
    },
    keywords="process monitor management system",
    project_urls={
        "Bug Reports": "https://github.com/hooksvue/py-process-monitor/issues",
        "Source": "https://github.com/hooksvue/py-process-monitor",
    },
)