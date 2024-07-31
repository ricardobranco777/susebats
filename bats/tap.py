#!/usr/bin/env python3
"""
tap module
"""

import os
import re


def grep_notok(file: str) -> set[str]:
    """
    Find the failed tests in a .tap file
    """
    tests = set()
    with open(file, encoding="utf-8") as f:
        failed = [line for line in f.read().splitlines() if "in test file" in line]
    for fail in failed:
        test = re.findall(r"/(.*?\.bats)", fail)[0]
        tests.add(os.path.basename(test.removesuffix(".bats")))
    return tests
