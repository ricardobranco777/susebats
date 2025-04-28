"""
tap module
"""

import fnmatch
import os
import re
import sys
from collections import defaultdict
from functools import cache

from bats.requests import get_json
from bats.versions import TEST_URL


@cache
def list_tests(package: str, version: str) -> list[str]:
    """
    List tests from upstream
    """

    repo_regex = r"^https://github.com/(.*)/blob/v{}/(.*)/{}\.bats$"
    repo, test_dir = re.findall(repo_regex, TEST_URL[package])[0]

    tag = version
    if tag == "":
        api_url = f"https://api.github.com/repos/{repo}/tags"
        data = get_json(api_url)
        if data is None:
            sys.exit(f"ERROR: {package} {tag}")
        tag = data[0]["name"]
    elif tag[0].isdigit() and not tag.startswith("v"):
        tag = f"v{tag}"

    api_url = f"https://api.github.com/repos/{repo}/contents/{test_dir}"
    params = {"ref": tag}
    data = get_json(api_url, params=params)
    if data is None:
        sys.exit(f"ERROR: {package} {tag}")

    items = []
    for item in data:
        if not item["name"].endswith(".bats"):
            continue
        items.append(item["name"].removesuffix(".bats"))
    return items


def grep_notok(  # pylint: disable=too-many-branches
    file: str, alles: bool = True
) -> dict[str, list[str]]:
    """
    Find the failed tests in a .tap file
    """
    with open(file, encoding="utf-8") as f:
        lines = f.read().splitlines()

    test = ""
    buffer: list[str] = []
    tests = defaultdict(list)

    # Second line may be like this: "# package version release DISTRI VERSION BUILD ARCH"
    # podman 5.4.2 1.1 opensuse Tumbleweed 20250426 x86_64
    package = version = ""
    try:
        _, package, version, *_ = lines[1].split()
    except ValueError:
        pass

    for line in lines:
        if line.startswith(("not ok", "#not ok")):
            # Sometimes, bats failures in podman don't show the "in test file" in the else below
            # so extract "130" from "not ok 295 [130] podman kill - print IDs or raw input"
            try:
                number = re.findall(r"#?not ok \d+ \[(\d+)\] .*", line)[0]
                package = package or "podman"
                test = fnmatch.filter(list_tests(package, version), f"{number}-*")[0]
            except IndexError:
                pass
            if test and buffer:
                tests[test].append("\n".join(buffer) + "\n")
            if package != "podman":
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
