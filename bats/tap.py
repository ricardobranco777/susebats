"""
tap module
"""

import fnmatch
import re
import os
import sys
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass

from bats.repos import get_bats_tests, get_url, list_files


# We want to extract the timing information from lines like these:
# not ok 166 bud-git-context in 118ms
# not ok 655 [520] podman checkpoint --export, with volumes in 1558ms
# not ok 7 runc exec (cgroup v2, ro cgroupfs, new cgroupns) does not chown cgroup # in 418 ms
TIMING = re.compile(
    r"^(?:#?not )?ok \d+ (?:\[\d+\] )?(.*?)\s+#?\s*in (\d+)\s*ms(?: # .*)?$"
)


@dataclass(frozen=True)
class Test:
    """
    Test class
    """

    name: str
    url: str
    lines: list[str]


def grep_notok(  # pylint: disable=too-many-branches
    file: str, ignored: bool = False
) -> list[Test]:
    """
    Find the failed tests in a TAP file
    """
    with open(file, encoding="utf-8") as f:
        lines = f.read().splitlines()

    # Second line may be like this: "# package version release DISTRI VERSION BUILD ARCH"
    # podman 5.4.2 1.1 opensuse Tumbleweed 20250426 x86_64
    package = version = ""
    try:
        _, package, version, *_ = lines[1].split()
    except ValueError:
        pass

    # Fetch the plan to check that we don't have a truncated TAP file
    found = last = 0
    for line in lines:
        if line.startswith("1.."):
            last = int(line.split("..", 1)[1])
            break
    if not last:
        sys.exit(f"Malformed TAP file: {file}")

    test = ""
    tests = []
    buffer: list[str] = []

    for line in lines:
        if line.startswith(("ok", "not ok", "#not ok")):
            found += 1
            if test and buffer:
                tests.append(
                    Test(name=test, url=get_url(package, version, test), lines=buffer)
                )
            # bats failures in podman may not show the "in test file" in the else block below
            # so extract "130" from "not ok 295 [130] podman kill - print IDs or raw input"
            try:
                number = re.findall(r"#?not ok \d+ \[(\d+)\] .*", line)[0]
                package = package or "podman"
                test = fnmatch.filter(list_files(package, version), f"{number}-*")[0]
            except IndexError:
                pass
            if line.startswith("ok"):
                test = ""
                buffer = []
            else:
                test = test if package == "podman" else ""
                buffer = [line]
        else:
            matches = re.findall(r"in test file .*/(.*?)\.bats", line)
            if matches:
                test = matches.pop()
            buffer.append(line)
    if test and buffer:
        tests.append(Test(name=test, url=get_url(package, version, test), lines=buffer))

    if found != last:
        sys.exit(f"Truncated TAP file: {file}")

    return [
        t
        for t in tests
        if t.lines[0].startswith("not ok")
        or (t.lines[0].startswith("#not ok") and ignored)
    ]


def grep_skipped(file: str) -> list[str]:
    """
    Find the skipped tests in a TAP file
    """
    with open(file, encoding="utf-8") as f:
        lines = f.read().splitlines()

    skipped = []
    for line in lines:
        if line.startswith("ok") and "# skip" in line:
            skipped.append(line)
    return skipped


def get_timings(file: str) -> dict[str, list[tuple[str, int]]]:
    """
    Return the time it takes each test
    """
    with open(file, encoding="utf-8") as f:
        lines = f.read().splitlines()

    # Second line may be like this: "# package version release DISTRI VERSION BUILD ARCH"
    # podman 5.4.2 1.1 opensuse Tumbleweed 20250426 x86_64
    package = version = ""
    try:
        _, package, version, *_ = lines[1].split()
    except ValueError:
        pass

    # Fetch the plan to check that we don't have a truncated TAP file
    found = last = 0
    for line in lines:
        if line.startswith("1.."):
            last = int(line.split("..", 1)[1])
            break
    if not last:
        sys.exit(f"Malformed TAP file: {file}")

    # We need a deepcopy because we use list.pop()
    tests = deepcopy(get_bats_tests(package, version))
    file = ""

    timings: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for line in lines:
        if not line.startswith(("ok", "not ok", "#not ok")):
            continue
        found += 1
        match = TIMING.findall(line)
        if not match:
            continue
        test, msecs = match[0]
        try:
            file = os.path.basename(tests[test].pop()).removesuffix(".bats")
        except IndexError:
            # Some test descriptions have shell $variables so use the previous filename
            if not file:
                # Assume first test file by default
                file = list(tests.keys())[0]
        timings[file].append((test, int(msecs)))

    if found != last:
        sys.exit(f"Truncated TAP file: {file}")

    return timings
