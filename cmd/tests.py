#!/usr/bin/env python3
"""
list BATS tests for package and tag
"""

import argparse
import re
import sys

from requests.exceptions import RequestException

from bats.requests import session, TIMEOUT
from bats.versions import TEST_URL


def main_tests(args: argparse.Namespace) -> None:
    """
    Main function
    """

    repo_regex = r"^https://github.com/(.*)/blob/v{}/(.*)/{}\.bats$"
    repo, test_dir = re.findall(repo_regex, TEST_URL[args.package])[0]

    tag = args.version
    if tag[0].isdigit() and not tag.startswith("v"):
        tag = f"v{tag}"
    elif tag == "latest":
        api_url = f"https://api.github.com/repos/{repo}/tags"
        try:
            got = session.get(api_url, timeout=TIMEOUT)
            data = got.json()
        except RequestException as err:
            sys.exit(f"ERROR: {args.package} {tag}: {err}")
        tag = data[0]["name"]

    api_url = f"https://api.github.com/repos/{repo}/contents/{test_dir}"
    params = {"ref": tag}

    try:
        got = session.get(api_url, params=params, timeout=TIMEOUT)
        data = got.json()
    except RequestException as err:
        sys.exit(f"ERROR: {args.package} {tag}: {err}")

    for item in data:
        if not item["name"].endswith(".bats"):
            continue
        if args.verbose:
            print(item["download_url"])
        else:
            print(item["name"])
