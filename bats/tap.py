#!/usr/bin/env python3
"""
tap module
"""

import os
import re
from collections import defaultdict


def grep_notok(file: str) -> dict[str, list[str]]:
    """
    Find the failed tests in a .tap file
    """
    with open(file, encoding="utf-8") as f:
        lines = f.read().splitlines()

    test = ""
    buffer: list[str] = []
    tests = defaultdict(list)

    for line in lines:
        if line.startswith(("not ok", "#not ok")):
            if test and buffer:
                tests[test].append("\n".join(buffer) + "\n")
            test = ""
            buffer = [line]
        elif line.startswith("ok"):
            if test and buffer:
                tests[test].append("\n".join(buffer) + "\n")
            test = ""
            buffer = []
        else:
            if "in test file" in line:
                filename = re.findall(r"/(.*?\.bats)", line)[0]
                test = os.path.basename(filename.removesuffix(".bats"))
            buffer.append(line)
    if test and buffer:
        tests[test].append("\n".join(buffer) + "\n")

    return tests
