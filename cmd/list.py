#!/usr/bin/env python3
"""
List skipped BATS tests on all schedules
"""

import argparse
from concurrent.futures import ThreadPoolExecutor

from bats.repos import REPOS, get_products


def main_list(args: argparse.Namespace) -> None:
    """
    Main function
    """
    _ = args

    with ThreadPoolExecutor(max_workers=min(10, len(REPOS))) as executor:
        for products in executor.map(get_products, REPOS):
            for product in products:
                print(f"{product.name}\t{product.url}")
                for setting, values in product.settings.items():
                    print(f"\t{setting}='{' '.join(values)}'")
