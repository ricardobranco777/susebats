#!/usr/bin/env python3
"""
List BATS jobs on o.s.d & o3
"""

import argparse
import sys

from bats.job import get_job, Job
from bats.suse import fetch_version
from bats.versions import get_version


def main_versions(args: argparse.Namespace) -> None:
    """
    Main function
    """
    job = get_job(args.url, full=True)
    if job is None:
        sys.exit(f"ERROR: {args.url}")

    print_versions(job, verbose=args.verbose)


def print_versions(job: Job, verbose: bool = False) -> None:
    """
    Print job
    """
    package = job.settings["BATS_PACKAGE"]
    version = get_version(job.results)
    if version is None:
        sys.exit("ERROR: No version")

    fields = ["PACKAGE", "TAG", "TESTED"]
    fmt = "{:<12}  {:<12}  {:<30}"
    if verbose:
        fmt += "  {}"
        fields.append("PUBLISHED")

    published = None
    if verbose:
        product = job.name.split("-Build")[0]
        published = fetch_version(product, package)

    print(fmt.format(*fields))
    print(
        fmt.format(
            *[package, version.git_version, version.rpm_version, published][
                : len(fields)
            ]
        )
    )
