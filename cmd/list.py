#!/usr/bin/env python3
"""
List skipped BATS tests on all schedules
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
from itertools import chain

from bats.repos import REPOS, get_tests


def main_list(args: argparse.Namespace) -> None:
    """
    Main function
    """
    _ = args

    with ThreadPoolExecutor(max_workers=len(REPOS)) as executor:
        tests = list(chain.from_iterable(executor.map(get_tests, REPOS.values())))

    if not tests:
        return

    width = max(len(test.product) for test in tests)

    for test in tests:
        print(f"{test.product:<{width}}  {test.url}")
