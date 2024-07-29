#!/usr/bin/env python3
"""
List BATS jobs on o.s.d & o3
"""

import argparse
import re
import sys
from concurrent.futures import ThreadPoolExecutor

from bats.job import get_job, Job
from bats.suse import fetch_version


VERSION = re.compile(
    "(aardvark(?:-dns)?|buildah|netavark|podman|runc|skopeo) (?:info|version)"
)


def get_version(title: str, info: str) -> tuple[str, str]:
    """
    Get version
    """
    package = title.split()[0]
    if package == "aardvark":
        package = "aardvark-dns"
    version = ""
    lines = info.splitlines()
    for line in lines:
        if line.split()[0] == "Version:":
            version = line.split()[-1]
            break
    if not version:
        if "version" in lines[0]:
            version = lines[0].split()[2]
        else:
            version = lines[0].split()[-1]
    return package, version


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
    versions = {}
    for result in job.results:
        if not result["has_parser_text_result"]:
            for detail in result["details"]:
                if "title" not in detail:
                    continue
                if VERSION.match(detail["title"]):
                    package, version = get_version(detail["title"], detail["text_data"])
                    if package not in versions:
                        versions[package] = version

    rpm_versions = {}
    if verbose:
        product = job.name.split("-Build")[0]
        with ThreadPoolExecutor(max_workers=min(10, len(versions))) as executor:
            for package, rpm_version in zip(
                versions, executor.map(lambda p: fetch_version(product, p), versions)
            ):
                if rpm_version is not None:
                    rpm_versions[package] = rpm_version

    for package in sorted(versions):
        if package in rpm_versions:
            print(f"{package:<12}  {versions[package]:<12}  {rpm_versions[package]}")
        else:
            print(f"{package:<12}  {versions[package]:<12}")
