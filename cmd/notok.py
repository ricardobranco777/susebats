#!/usr/bin/env python3
"""
Generate BATS_SKIP variables from an openQA job URL
"""

import argparse
import contextlib
import re
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from functools import reduce
from itertools import groupby

from bats.job import get_job, Job
from bats.requests import download_file
from bats.tap import grep_notok
from bats.versions import get_versions, TEST_URL


TAP_REGEX = r"-((?:root|user)(?:-(?:local|remote))?)\.tap$"


def process_files(files: list[str]) -> dict[str, str]:
    """
    Process .tap files
    """
    info = {}
    skip_common = set()
    found: dict[str, set] = {}
    for file in files:
        found[file] = set(grep_notok(file).keys())
    # Find failed subtests in all scenarios for general skip variable
    skip_common = reduce(lambda x, y: x & y, found.values())
    if len(files) > 1:
        for file in files:
            found[file] -= skip_common
    package = files[0].split("_")[0].upper() + "_BATS_SKIP"
    info[package] = " ".join(sorted(skip_common)) or "none"
    if len(files) > 1:
        for file in files:
            skip = re.findall(TAP_REGEX, file)[0].replace("-", "_").upper()
            info[f"{package}_{skip}"] = " ".join(sorted(found[file])) or "none"
    return info


def main_notok(args: argparse.Namespace) -> None:
    """
    Main function
    """
    job = get_job(args.url, full=True)
    if job is None:
        sys.exit(f"ERROR: {args.url}")

    with tempfile.TemporaryDirectory() as tmpdir, contextlib.chdir(tmpdir):
        with ThreadPoolExecutor(max_workers=min(10, len(job.logs))) as executor:
            downloaded_files = list(filter(None, executor.map(download_file, job.logs)))

        if args.verbose:
            print_failures(job, downloaded_files, alles=args.verbose > 1)
        else:
            print_settings(job, downloaded_files, diff=args.diff)


def print_failures(job: Job, tap_files: list[str], alles: bool = False) -> None:
    """
    Print job failures
    """
    versions = get_versions(job.results)
    for file in tap_files:
        package = file.split("_")[0]
        if package == "aardvark":
            package = "aardvark-dns"
        version = versions[package].git_version
        failed = grep_notok(file, alles=alles)
        for test in failed:
            test_url = TEST_URL[package].format(version, test)
            print(file, test_url)
            for sub in failed[test]:
                print(sub)


def print_settings(job: Job, tap_files: list[str], diff: bool = False) -> None:
    """
    Print job settings
    """
    # Group multiple .tap files by their prefixes:
    # (podman|buildah|etc)_integration_.*.tap
    for _, files in groupby(tap_files, key=lambda s: s.split("_integration")[0]):
        info = process_files(list(files))
        for key, value in info.items():
            if diff and job.settings.get(key) != value:
                print(f"-{key}='{job.settings[key]}'")
                print(f"+{key}='{value}'")
            else:
                print(f"{key}='{value}'")
