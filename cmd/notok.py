#!/usr/bin/env python3
"""
Generate BATS_SKIP variables from an openQA job URL
"""

import argparse
import contextlib
import os
import re
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from functools import reduce
from itertools import groupby

from requests.exceptions import RequestException

from bats.job import get_job, Job, session, TIMEOUT
from bats.tap import grep_notok


def download_file(url: str) -> str | None:
    """
    Download a file from URL to current directory
    """
    filename = os.path.basename(url)
    try:
        with session.get(url, stream=True, timeout=TIMEOUT) as r:
            r.raise_for_status()
            with open(filename, "xb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    except RequestException as error:
        print(f"ERROR: {url}: {error}", file=sys.stderr)
        return None
    return filename


def process_files(job: Job, files: list[str]) -> None:
    """
    Process .tap files
    """
    skip_common = set()
    found: dict[str, set] = {}
    for file in files:
        found[file] = set(map(str, grep_notok(job, file).keys()))
    # Find failed subtests in all scenarios for general skip variable
    skip_common = reduce(lambda x, y: x & y, found.values())
    if len(files) > 1:
        for file in files:
            found[file] -= skip_common

    prefix = files[0].split("_")[0].upper() + "_BATS_SKIP"
    skip = " ".join(sorted(skip_common)) or "none"
    print(f"{prefix}='{skip}'")
    if len(files) == 1:
        return
    for file in files:
        name = re.findall(r"-((?:root|user)(?:-(?:local|remote))?)\.tap$", file)[0]
        name = name.replace("-", "_").upper()
        skip = " ".join(sorted(found[file])) or "none"
        print(f"{prefix}_{name}='{skip}'")


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
            process_files(job, list(files))
