#!/usr/bin/env python3
"""
List skipped BATS tests on all schedules
"""

import argparse
from concurrent.futures import ThreadPoolExecutor

from bats.repos import REPOS, Product, find_products, grep_tarball


def get_products(repo: str) -> list[Product]:
    """
    Get products from YAML schedules in repo
    """
    return [
        product
        for file in grep_tarball(repo, "*.yaml", ignore_pattern="*_old.yaml")
        for product in find_products(file)
    ]


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
