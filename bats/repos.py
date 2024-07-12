#!/usr/bin/env python3
"""
Repos module
"""

import io
import re
import os
import sys
import tarfile
from dataclasses import dataclass
from fnmatch import fnmatch
from typing import Iterator
from urllib.parse import urlencode

import requests
from requests.exceptions import RequestException
import yaml

GITLAB_TOKEN = os.environ.get("GITLAB_TOKEN")

REPOS = [
    "https://github.com/os-autoinst/opensuse-jobgroups/archive/refs/heads/master.tar.gz",
    "https://gitlab.suse.de/qac/qac-openqa-yaml/-/archive/master/qac-openqa-yaml-master.tar.gz",
]


@dataclass
class Product:
    """
    Product class
    """

    name: str
    url: str
    settings: dict[str, str]


def find_file(file: io.TextIOWrapper) -> Iterator[Product]:
    """
    Find settings in file
    """
    try:
        data = yaml.safe_load(file)
    except yaml.YAMLError:
        return

    if "scenarios" not in data:
        return

    products = data["products"]

    for arch, scenario in data["scenarios"].items():
        for product, tests in scenario.items():
            for info in filter(lambda t: isinstance(t, dict), tests):
                for test in info.keys():
                    if "settings" not in info[test]:
                        continue
                    settings = {
                        k: v
                        for k, v in info[test]["settings"].items()
                        if "BATS_SKIP" in k
                    }
                    if not settings:
                        continue
                    settings = {k: settings[k] for k in sorted(settings)}
                    if product.startswith("opensuse"):
                        url = "https://openqa.opensuse.org"
                    else:
                        url = "https://openqa.suse.de"
                    params = products[product] | {"arch": arch, "test": test}
                    url = f"{url}/tests/latest?{urlencode(params)}"
                    yield Product(name=product, url=url, settings=settings)


def grep_dir(
    directory: str,
    regex: re.Pattern,
    file_pattern: str,
    ignore_dirs: list[str] | None = None,
) -> Iterator[str]:
    """
    Recursive grep
    """
    if ignore_dirs is None:
        ignore_dirs = []
    for root, dirs, files in os.walk(directory):
        for ignore in set(ignore_dirs) & set(dirs):
            dirs.remove(ignore)
        for file in files:
            if fnmatch(file, file_pattern):
                file = os.path.join(root, file)
                with open(file, encoding="utf-8") as f:
                    if regex.search(f.read(), re.M):
                        yield file


def grep_tarball(
    url: str,
    file_pattern: str,
) -> Iterator[io.TextIOWrapper]:
    """
    Downloads a tarball and return the content of files
    """
    headers = {}
    if "gitlab" in url:
        headers["PRIVATE-TOKEN"] = GITLAB_TOKEN
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()
    except RequestException as error:
        sys.exit(f"ERROR: {url}: {error}")
    data = io.BytesIO(response.content)
    try:
        with tarfile.open(fileobj=data, mode="r:gz") as tar:
            for elem in tar.getmembers():
                if elem.isfile() and fnmatch(elem.name, file_pattern):
                    file = tar.extractfile(elem)
                    if file is not None:
                        yield io.TextIOWrapper(io.BytesIO(file.read()))
    except tarfile.ReadError as error:
        # May fail because GITLAB_TOKEN is not set
        print(f"ERROR: {url}: {error}", file=sys.stderr)
