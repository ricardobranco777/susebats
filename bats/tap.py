#!/usr/bin/env python3
"""
tap module
"""

import os
import re
from collections import defaultdict
from dataclasses import dataclass

from bats.job import Job
from bats.versions import get_versions


_TEST_URL = {
    "aardvark-dns": "https://github.com/containers/aardvark-dns/tree/{}/test/{}.bats",
    "buildah": "https://github.com/containers/buildah/tree/{}/tests/{}.bats",
    "netavark": "https://github.com/containers/netavark/tree/{}/test/{}.bats",
    "podman": "https://github.com/containers/podman/tree/{}/test/system/{}.bats",
    "runc": "https://github.com/opencontainers/runc/tree/{}/tests/integration/{}.bats",
    "skopeo": "https://github.com/containers/skopeo/tree/{}/systemtest/{}.bats",
}


@dataclass(frozen=True)
class Test:
    """
    Test class
    """

    name: str
    url: str

    def __str__(self) -> str:
        return self.name


def grep_notok(job: Job, file: str, alles: bool = True) -> dict[Test, list[str]]:
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

    package = file.split("_")[0]
    if package == "aardvark":
        package = "aardvark-dns"
    version = get_versions(job.results)[package].git_version
    return {
        Test(name=test, url=_TEST_URL[package].format(version, test)): tests[test]
        for test in tests
        if tests[test]
    }
