"""
Generate BATS_IGNORE variables from an openQA job URL
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
from bats.tap import get_timings, grep_notok, grep_skipped
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
    info["BATS_IGNORE"] = " ".join(sorted(skip_common))
    if len(files) > 1:
        for file in files:
            skip = re.findall(TAP_REGEX, file)[0].replace("-", "_").upper()
            info[f"BATS_IGNORE_{skip}"] = " ".join(sorted(found[file]))
    return info


def main_notok(args: argparse.Namespace) -> None:
    """
    Main function
    """
    job = get_job(args.url, full=True)
    if job is None:
        sys.exit(f"ERROR: {args.url}")

    logs = [log for log in job.logs if log.endswith((".tap", ".tap.txt"))]
    if not logs:
        sys.exit(f"ERROR: {args.url}: No .tap logs")

    with tempfile.TemporaryDirectory() as tmpdir, contextlib.chdir(tmpdir):
        files = []
        if len(logs) == 1:
            file = download_file(logs[0])
            if file is not None:
                files = [file]
        else:
            with ThreadPoolExecutor(max_workers=len(logs)) as executor:
                files = list(filter(None, executor.map(download_file, logs)))

        if args.skipped:
            print_skipped(files)
        elif args.timing:
            print_timings(files, verbose=args.verbose)
        elif args.verbose:
            print_failures(files, verbose=args.verbose > 1)
            print_traces(job)
        else:
            print_settings(files)


def print_failures(logs: list[str], verbose: bool = False) -> None:
    """
    Print job failures
    """
    for file in logs:
        failed = grep_notok(file, ignored=verbose)
        for test in failed:
            print(file, test.url)
            print("\n" + "\n".join(test.lines) + "\n")


def print_skipped(logs: list[str]) -> None:
    """
    Print skipped tests
    """
    for file in logs:
        print(file)
        skipped = grep_skipped(file)
        for line in skipped:
            print(f"\t{line}")


def print_timings(logs: list[str], verbose: bool = False) -> None:
    """
    Print timings
    """
    for file in logs:
        print("#", file)
        timings = get_timings(file)
        file_width = max(map(len, timings))
        fmt = f"{{}}\t{{:{file_width}}}"
        if verbose:
            fmt += "  {}"
        file_total = 0
        for file in timings:
            total = 0
            for test, msecs in timings[file]:
                if verbose:
                    # seconds = msecs // 1000 or 1
                    print(fmt.format(msecs, file, test))
                total += msecs
            if not verbose:
                print(fmt.format(total, file))
            file_total += total
        print("# total: ", file_total)


def print_traces(job: Job) -> None:
    """
    Print traces recorded by `record_info("TRACE", $trace)`
    """
    for trace in get_traces(job):
        print(trace)


def print_settings(logs: list[str]) -> None:
    """
    Print job settings
    """
    info = process_files(logs)
    for key, value in info.items():
        if value:
            print(f"    {key}:", value)
        else:
            print(f"    {key}:")
