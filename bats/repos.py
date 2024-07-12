#!/usr/bin/env python3
"""
Repos module
"""

import io
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


def find_products(file: io.TextIOWrapper) -> Iterator[Product]:
    """
    Find products in YAML schedule with settings containing "BATS_SKIP"
    """
    try:
        data = yaml.safe_load(file)
    except yaml.YAMLError:
        return

    if "scenarios" not in data:
        return

    for arch, products in data["scenarios"].items():
        for product, scenarios in products.items():
            for scenario in filter(lambda s: isinstance(s, dict), scenarios):
                for test in scenario.keys():
                    if "settings" not in scenario[test]:
                        continue
                    settings = {
                        setting: scenario[test]["settings"][setting]
                        for setting in sorted(scenario[test]["settings"])
                        if "BATS_SKIP" in setting
                    }
                    if not settings:
                        continue
                    if product.startswith("opensuse"):
                        url = "https://openqa.opensuse.org"
                    else:
                        url = "https://openqa.suse.de"
                    params = data["products"][product] | {"arch": arch, "test": test}
                    url = f"{url}/tests/latest?{urlencode(params)}"
                    yield Product(name=product, url=url, settings=settings)


def grep_tarball(
    url: str,
    file_pattern: str,
) -> Iterator[io.TextIOWrapper]:
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
