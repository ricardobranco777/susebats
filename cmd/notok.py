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
from bats.tap import grep_notok, grep_skipped
from bats.utils import get_traces


TAP_REGEX = r"((?:root|user)(?:-(?:local|remote))?)\.tap(?:\.txt)?$"


def process_files(files: list[str]) -> dict[str, str]:
    """
    Process .tap files
    """
    info = {}
    skip_common = set()
    found: dict[str, set] = {}
    for file in files:
        found[file] = set(t.name for t in grep_notok(file, ignored=True))
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

    tap_logs = [log for log in job.logs if log.endswith((".tap", ".tap.txt"))]
    if not tap_logs:
        sys.exit(f"ERROR: {args.url}: No .tap logs")

    with tempfile.TemporaryDirectory() as tmpdir, contextlib.chdir(tmpdir):
        with ThreadPoolExecutor(max_workers=len(tap_logs)) as executor:
            downloaded_files = list(filter(None, executor.map(download_file, tap_logs)))

        if args.skipped:
            print_skipped(downloaded_files)
        elif args.verbose:
            print_failures(downloaded_files, verbose=args.verbose > 1)
            print_traces(job)
        else:
            print_settings(downloaded_files)


def print_failures(tap_files: list[str], verbose: bool = False) -> None:
    """
    Print job failures
    """
    for file in tap_files:
        failed = grep_notok(file, ignored=verbose)
        for test in failed:
            print(file, test.url)
            print("\n" + "\n".join(test.lines) + "\n")


def print_skipped(tap_files: list[str]) -> None:
    """
    Print skipped tests
    """
    for file in tap_files:
        print(file)
        skipped = grep_skipped(file)
        for line in skipped:
            print(f"\t{line}")


def print_traces(job: Job) -> None:
    """
    Print traces recorded by `record_info("TRACE", $trace)`
    """
    for trace in get_traces(job):
        print(trace)


def print_settings(tap_files: list[str]) -> None:
    """
    Print job settings
    """
    info = process_files(tap_files)
    for key, value in info.items():
        if value:
            print(f"    {key}:", value)
        else:
            print(f"    {key}:")
