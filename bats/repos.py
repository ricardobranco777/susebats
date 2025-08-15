"""
Repos module
"""

import io
import os
import sys
import tarfile
from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Callable, Iterator
from urllib.parse import urlencode

import requests
from requests.exceptions import RequestException
import yaml

REPOS = {
    "o3": "https://github.com/os-autoinst/opensuse-jobgroups/archive/refs/heads/master.tar.gz",
    "osd": "https://gitlab.suse.de/qac/qac-openqa-yaml/-/archive/master/qac-openqa-yaml-master.tar.gz",  # pylint: disable=line-too-long
}


@dataclass(frozen=True, order=True)
class Test:
    """
    Test class
    """

    url: str
    product: str
    name: str
    settings: dict[str, str | list[str]] = field(compare=False)


def find_tests(
    buf: str,
    match: Callable,
) -> list[Test]:
    """
    Find tests in YAML schedule with settings containing "BATS_PACKAGE"
    """
    try:
        data = yaml.safe_load(buf)
    except yaml.YAMLError:
        return []

    if "scenarios" not in data:
        return []

    tests: list[Test] = []

    for arch, products in data["scenarios"].items():
        for product, scenarios in products.items():
            for scenario in filter(lambda s: isinstance(s, dict), scenarios):
                for test in scenario.keys():
                    if scenario[test] is None or "settings" not in scenario[test]:
                        continue
                    if not match(scenario[test]):
                        continue
                    settings = scenario[test]["settings"]
                    if product.startswith("opensuse"):
                        url = "https://openqa.opensuse.org"
                    else:
                        url = "https://openqa.suse.de"
                    params = data["products"][product] | {"arch": arch, "test": test}
                    url = f"{url}/tests/latest?{urlencode(params)}"
                    tests.append(
                        Test(name=test, product=product, url=url, settings=settings)
                    )

    return tests


def grep_tarball(
    url: str,
    file_pattern: str,
    ignore_pattern: str | None = None,
) -> Iterator[tuple[str, str]]:
    """
    Downloads a tarball and return the content of files
    """
    headers = {}
    if "gitlab" in url:
        headers["PRIVATE-TOKEN"] = os.environ.get("GITLAB_TOKEN")
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()
    except RequestException as error:
        print(f"ERROR: {url}: {error}")
        return
    data = io.BytesIO(response.content)
    try:
        with tarfile.open(fileobj=data, mode="r:gz") as tar:
            for elem in tar.getmembers():
                if not elem.isfile():
                    continue
                if ignore_pattern and fnmatch(elem.name, ignore_pattern):
                    continue
                if fnmatch(elem.name, file_pattern):
                    file = tar.extractfile(elem)
                    if file is not None:
                        yield elem.name, file.read().decode()
    except tarfile.ReadError as error:
        # May fail because GITLAB_TOKEN is not set
        print(f"ERROR: {url}: {error}", file=sys.stderr)


def bats_test(test: dict[str, str]) -> bool:
    """
    Filter to be used on find_tests()
    """
    return "BATS_PACKAGE" in test["settings"]


def get_tests(repo: str) -> list[Test]:
    """
    Get tests from YAML schedules in repo
    """
    tests = [
        test
        for file, data in grep_tarball(repo, "*.yaml")
        for test in find_tests(data, match=bats_test)
    ]
    tests.sort()
    return tests


def get_urls(repo: str) -> list[str]:
    """
    Get URL's from YAML schedules in repo
    """
    return [test.url for test in get_tests(repo)]
