"""
tap module
"""

import os
import re
from collections import defaultdict


def grep_notok(file: str, alles: bool = True) -> dict[str, list[str]]:
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
            matches = re.findall(r"in test file .*/(.*?\.bats)", line)
            if matches:
                filename = matches.pop()
                test = os.path.basename(filename.removesuffix(".bats"))
            buffer.append(line)
    if test and buffer:
        tests[test].append("\n".join(buffer) + "\n")

    if not alles:
        for test in tests:
            tests[test] = list(filter(lambda s: not s.startswith("#"), tests[test]))

    return {test: tests[test] for test in tests if tests[test]}
