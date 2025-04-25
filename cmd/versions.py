#!/usr/bin/env python3
"""
List BATS jobs on o.s.d & o3
"""

import argparse
import sys

from bats.job import get_job, Job
from bats.versions import get_versions, get_published


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
    versions = get_versions(job.results)
    published = {}

    fields = ["PACKAGE", "TAG", "TESTED"]
    fmt = "{:<12}  {:<12}  {:<30}"
    if verbose:
        fmt += "  {}"
        fields.append("PUBLISHED")

    if verbose:
        product = job.name.split("-Build")[0]
        published = get_published(product, list(versions.keys()))
    print(fmt.format(*fields))

    for package in sorted(versions):
        print(
            fmt.format(
                *[
                    package,
                    versions[package].git_version,
                    versions[package].rpm_version,
                    published.get(package, ""),
                ][: len(fields)]
            )
        )
