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
from bats.tap import download_file, grep_notok


TAP_REGEX = r"-((?:root|user)(?:-(?:local|remote))?)\.tap$"


def process_files(job: Job, files: list[str]) -> dict[str, str]:
    """
    Process .tap files
    """
    info = {}
    skip_common = set()
    found: dict[str, set] = {}
    for file in files:
        found[file] = set(map(str, grep_notok(job, file).keys()))
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

    logs = list(filter(lambda s: s.endswith(".tap"), job.logs))

    with tempfile.TemporaryDirectory() as tmpdir, contextlib.chdir(tmpdir):
        with ThreadPoolExecutor(max_workers=min(10, len(logs))) as executor:
            downloaded_files = filter(None, executor.map(download_file, logs))

        if args.verbose:
            for file in downloaded_files:
                failed = grep_notok(job, file, alles=args.verbose > 1)
                for test in failed:
                    print(file, test.url)
                    for sub in failed[test]:
                        print(sub)
            sys.exit(0)

        # Group multiple .tap files by their prefixes:
        # (podman|buildah|etc)_integration_.*.tap
        for _, files in groupby(
            downloaded_files, key=lambda s: s.split("_integration")[0]
        ):
            info = process_files(job, list(files))
            for key, value in info.items():
                print(f"{key}='{value}'")
