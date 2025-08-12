"""
tap module
"""

import fnmatch
import re
import sys
from dataclasses import dataclass
from functools import cache

from bats.requests import get_json
from bats.issues import GITHUB_TOKEN


TEST_URL = {
    "aardvark-dns": "https://github.com/containers/aardvark-dns/blob/v{}/test/{}.bats",
    "buildah": "https://github.com/containers/buildah/blob/v{}/tests/{}.bats",
    "netavark": "https://github.com/containers/netavark/blob/v{}/test/{}.bats",
    "podman": "https://github.com/containers/podman/blob/v{}/test/system/{}.bats",
    "podman-tui": "https://github.com/containers/podman-tui/blob/v{}/test/{}.bats",
    "runc": "https://github.com/opencontainers/runc/blob/v{}/tests/integration/{}.bats",
    "skopeo": "https://github.com/containers/skopeo/blob/v{}/systemtest/{}.bats",
    "umoci": "https://github.com/opencontainers/umoci/blob/v{}/test/{}.bats",
}


@dataclass(frozen=True)
class Test:
    """
    Test class
    """

    name: str
    url: str
    lines: list[str]


def get_url(package: str, version: str, test: str) -> str:
    """
    Get URL for test
    """
    return TEST_URL[package].format(version, test)


@cache
def list_files(package: str, version: str) -> list[str]:
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
    headers = None
    if GITHUB_TOKEN:
        headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    params = {"ref": tag}
    data = get_json(api_url, headers=headers, params=params)
    if data is None:
        sys.exit(f"ERROR: {package} {tag}")

    items = []
    for item in data:
        if not item["name"].endswith(".bats"):
            continue
        items.append(item["name"].removesuffix(".bats"))
    return items


def grep_notok(file: str, ignored: bool = False) -> list[Test]:
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

    test = ""
    tests = []
    buffer: list[str] = []

    for line in lines:
        if line.startswith(("ok", "not ok", "#not ok")):
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

    return [
        t
        for t in tests
        if t.lines[0].startswith("not ok")
        or (t.lines[0].startswith("#not ok") and ignored)
    ]
