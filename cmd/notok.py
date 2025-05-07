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

from bats.job import get_job, Job
from bats.requests import download_file
from bats.tap import grep_notok
from bats.versions import get_version, TEST_URL


TAP_REGEX = r"((?:root|user)(?:-(?:local|remote))?)\.tap$"


def process_files(files: list[str]) -> dict[str, str]:
    """
    Process .tap files
    """
    info = {}
    skip_common = set()
    found: dict[str, set] = {}
    for file in files:
        found[file] = set(t.name for t in grep_notok(file))
    # Find failed subtests in all scenarios for general skip variable
    skip_common = reduce(lambda x, y: x & y, found.values())
    if len(files) > 1:
        for file in files:
            found[file] -= skip_common
    info["BATS_SKIP"] = " ".join(sorted(skip_common))
    if len(files) > 1:
        for file in files:
            skip = re.findall(TAP_REGEX, file)[0].replace("-", "_").upper()
            info[f"BATS_SKIP_{skip}"] = " ".join(sorted(found[file]))
    return info


def main_notok(args: argparse.Namespace) -> None:
    """
    Main function
    """
    job = get_job(args.url, full=True)
    if job is None:
        sys.exit(f"ERROR: {args.url}")

    tap_logs = [log for log in job.logs if log.endswith(".tap")]
    if not tap_logs:
        sys.exit(f"ERROR: {args.url}: No .tap logs")

    with tempfile.TemporaryDirectory() as tmpdir, contextlib.chdir(tmpdir):
        with ThreadPoolExecutor(max_workers=len(tap_logs)) as executor:
            downloaded_files = list(filter(None, executor.map(download_file, tap_logs)))

        if args.verbose:
            print_failures(job, downloaded_files, verbose=args.verbose > 1)
        else:
            print_settings(job, downloaded_files, diff=args.diff)


def print_failures(job: Job, tap_files: list[str], verbose: bool = False) -> None:
    """
    Print job failures
    """
    package = job.settings["BATS_PACKAGE"]
    version = get_version(package, job.results)
    if version is None:
        return
    for file in tap_files:
        failed = grep_notok(file)
        for test in failed:
            if not test.lines:
                continue
            if not verbose and test.lines[0].startswith("#"):
                continue
            test_url = TEST_URL[package].format(version, test.name)
            print(file, test_url)
            print("\n".join(test.lines) + "\n")


def print_settings(job: Job, tap_files: list[str], diff: bool = False) -> None:
    """
    Print job settings
    """
    if not diff:
        for key, value in job.settings.items():
            if key.startswith("BATS_SKIP") or not key.startswith("BATS_"):
                continue
            print(f"  {key}: '{value}'")
    info = process_files(tap_files)
    for key, value in info.items():
        if diff and job.settings.get(key) != value:
            print(f"- {key}: '{job.settings[key]}'")
            print(f"+ {key}: '{value}'")
        else:
            print(f"  {key}: '{value}'")
