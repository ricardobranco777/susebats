#!/usr/bin/env python3
"""
List skipped BATS tests on all schedules
"""

import argparse
from concurrent.futures import ThreadPoolExecutor

from bats.repos import REPOS, get_tests


def main_list(args: argparse.Namespace) -> None:
    """
    Main function
    """
    _ = args

    with ThreadPoolExecutor(max_workers=min(10, len(REPOS))) as executor:
        for tests in executor.map(get_tests, REPOS):
            for test in tests:
                print(f"{test.product}\t{test.url}")
                for setting, values in test.settings.items():
                    print(f"\t{setting}='{' '.join(values)}'")
