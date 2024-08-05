"""
tap module
"""

import os
import re
import sys
from collections import defaultdict

from requests.exceptions import RequestException

from bats.session import session, TIMEOUT


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
            if "in test file" in line:
                filename = re.findall(r"/(.*?\.bats)", line)[0]
                test = os.path.basename(filename.removesuffix(".bats"))
            buffer.append(line)
    if test and buffer:
        tests[test].append("\n".join(buffer) + "\n")

    if not alles:
        for test in tests:
            tests[test] = list(filter(lambda s: not s.startswith("#"), tests[test]))

    return {test: tests[test] for test in tests if tests[test]}


def download_file(url: str) -> str | None:
    """
    Download a file from URL to current directory
    """
    filename = os.path.basename(url)
    try:
        with session.get(url, stream=True, timeout=TIMEOUT) as r:
            r.raise_for_status()
            with open(filename, "xb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    except RequestException as error:
        print(f"ERROR: {url}: {error}", file=sys.stderr)
        return None
    return filename
