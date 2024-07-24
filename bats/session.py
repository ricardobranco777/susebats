"""
session module
"""

import atexit
import os

import requests

from bats.debug import debugme


session = requests.Session()
TIMEOUT = 30


if os.getenv("DEBUG"):
    session.hooks["response"].append(debugme)
atexit.register(session.close)
