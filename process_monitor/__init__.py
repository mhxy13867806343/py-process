#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
py-process-monitor: A Python package to monitor and manage processes

This package provides functionality to monitor system processes and automatically
terminate processes that have been inactive for a specified period of time,
while protecting system processes from being terminated.
"""

__version__ = "1.0.0"
__author__ = "hooksvue"
__email__ = "hooksvue@example.com"
__license__ = "MIT"

from .monitor import ProcessMonitor
from .utils import is_system_process, get_process_info

__all__ = [
    "ProcessMonitor",
    "is_system_process",
    "get_process_info",
]