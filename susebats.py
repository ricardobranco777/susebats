#!/usr/bin/env python3
"""
susebats
"""

import argparse
import contextlib
import os
import re
import sys
import tempfile
import textwrap
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from itertools import chain

from bats.build import get_builds, get_build_jobs
from bats.job import get_job, get_jobs, Job
from bats.junit import get_failures, get_skipped, get_timings
from bats.repos import REPOS, get_tests, get_urls
from bats.requests import download_file, ping

VERSION = "1.9"

EXTRA = re.compile(r"-(container_host_)?[a-z]+_(rootless_)?(e2e|testsuite).*$")


def scheme_url(url: str) -> str:
    """
    Prepend a scheme to an URL if not present
    """
    if not url.startswith(("http:", "https:")):
        url = f"https://{url}"
    return url


def main() -> None:
    """
    Main function
    """

    parser = argparse.ArgumentParser(
        prog="susebats",
        epilog="set GITLAB_TOKEN environment variable for gitlab.suse.de",
    )
    parser.add_argument(
        "-l", "--list", action="store_true", help="list openQA testsuites"
    )
    parser.add_argument(
        "-s", "--skipped", action="store_true", help="print only skipped tests"
    )
    parser.add_argument(
        "-t", "--timing", action="store_true", help="timing information"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="verbose operation"
    )
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument("url", nargs="?", help="openQA job", type=scheme_url)
    args = parser.parse_args()

    if args.list:
        list_testsuites()
    elif args.url:
        if "/group_overview/" in args.url:
            print_jobgroup(args.url, verbose=args.verbose)
        else:
            print_jobinfo(
                url=args.url,
                skipped=args.skipped,
                timing=args.timing,
                verbose=args.verbose,
            )
    else:
        list_jobs(timing=args.timing, verbose=args.verbose)


def check_repo(repo: str, url: str) -> str | None:
    """
    Check repo availability
    """
    openqa_url = "https://openqa.opensuse.org"
    if repo == "osd":
        openqa_url = "https://openqa.suse.de"
    if ping(openqa_url):
        return url
    return None


def list_jobs(timing: bool = False, verbose: bool = False) -> None:
    """
    List jobs
    """
    with ThreadPoolExecutor(max_workers=len(REPOS)) as executor:
        futures = [
            executor.submit(check_repo, repo, url) for repo, url in REPOS.items()
        ]
        repos = [future.result() for future in as_completed(futures) if future.result()]

    if len(repos) == 0:
        return

    urls = []
    with ThreadPoolExecutor(max_workers=len(repos)) as executor:
        for results in executor.map(get_urls, repos):
            urls.extend(results)
    urls.sort()

    with ThreadPoolExecutor(max_workers=len(urls)) as executor:
        for job in executor.map(
            lambda u: get_job(u, include_comments=verbose, details=verbose),
            urls,
        ):
            if job is None:
                continue
            print_job(job, timing=timing, verbose=verbose)


def print_job(job: Job, timing: bool = False, verbose: bool = False) -> None:
    """
    Print job
    """
    arch = job.settings["ARCH"]
    name = EXTRA.sub("", job.name)
    package = job.settings.get(
        "BATS_PACKAGE",
        job.settings["TEST"]
        .removeprefix("container_host_")
        .removesuffix("_crun")
        .removesuffix("_testsuite")
        .replace("_", "/"),
    )
    runtime = job.settings.get("OCI_RUNTIME", "")
    if runtime:
        package = f"{package}+{runtime}"
    status = job.result if job.result != "none" else job.state
    status = job.result.upper() if job.result == "failed" else job.result
    status = status.split("_")[-1]
    if timing:
        print(job.seconds, end="\t")
    print(f"{status:10}  {package:24}  {arch:7}  {job.url:<42}  {name}")
    if verbose:
        print_extra(job)


def print_extra(job: Job) -> None:
    """
    Print extra info
    """
    print_passed(job)
    traces = get_traces(job)
    if len(traces) > 0:
        try:
            serial0 = [log for log in job.logs if log.endswith("serial0.txt")].pop()
            print(f"\ttraces: {serial0}")
        except IndexError:
            pass
    for core in (log for log in job.logs if "core." in log):
        print(f"\tcore: {core}")
    print_results(job)
    print_comments(job)


def print_passed(job: Job) -> None:
    """
    Print skipped passed tests recorded by `record_info("PASS", $test)`
    """
    passed = {
        detail["text_data"]
        for result in job.results
        for detail in result["details"]
        if "title" in detail and detail["title"] == "PASS"
    }
    if len(passed) > 0:
        print("\tpassed:")
        for test in sorted(passed):
            print(f"\t{test}")


def print_results(job: Job) -> None:
    """
    Print results
    """
    for result in job.results:
        # Skip non-failed modules
        if result["result"] == "failed":
            if not result["has_parser_text_result"]:
                print(f"\t{result['name']}")
                continue
            for test in result["details"]:
                # Skip non-failed sub-tests
                if test["result"] == "fail":
                    title = test["text_data"]
                    print(f"\t{result['name']:<20}  {title}")


def print_comments(job: Job) -> None:
    """
    Print comments
    """
    for comment in job.comments:
        if comment.text.startswith(
            (
                "Automatic bisect jobs",
                "Automatic investigation jobs",
                "Investigate retry job",
                "Restarting because RETRY is set",
            )
        ):
            continue
        for bugref in comment.issues:
            print(f"\t{bugref.url}\t{bugref.title}")
        if len(comment.issues) == 0:
            print(f"\t{comment.text} by {comment.author}")


def list_testsuites() -> None:
    """
    List testsuites
    """
    with ThreadPoolExecutor(max_workers=len(REPOS)) as executor:
        tests = list(chain.from_iterable(executor.map(get_tests, REPOS.values())))

    if not tests:
        return

    width = max(len(test.product) for test in tests)

    for test in tests:
        print(f"{test.product:<{width}}  {test.url}")


def print_jobinfo(
    url: str, skipped: bool = False, timing: bool = False, verbose: bool = False
) -> None:
    """
    Print job info
    """
    job = get_job(url, include_comments=True, details=True)
    if job is None:
        sys.exit(f"ERROR: {url}")

    logs = [log for log in job.logs if log.endswith(".xml")]
    if not logs:
        sys.exit(f"ERROR: {url}: No logs")

    with tempfile.TemporaryDirectory() as tmpdir, contextlib.chdir(tmpdir):
        files = []
        if len(logs) == 1:
            file = download_file(logs[0])
            if file is not None:
                files = [file]
        else:
            with ThreadPoolExecutor(max_workers=len(logs)) as executor:
                files = list(filter(None, executor.map(download_file, logs)))

        if skipped:
            print_skipped(files)
        elif timing:
            print_timings(files, verbose=verbose)
        else:
            print_failures(files, verbose=verbose)
            for trace in get_traces(job):
                print(trace)
            print_extra(job)


def print_failures(logs: list[str], verbose: bool = False) -> None:
    """
    Print job failures
    """
    for file in logs:
        failed = get_failures(file, ignored=verbose)
        for test in failed:
            print(test.tag, file, test.name, test.url)
            print(textwrap.indent(test.text.strip(), "  "))
            print()


def print_skipped(logs: list[str]) -> None:
    """
    Print skipped tests
    """
    suite_width = reason_width = -1
    for file in logs:
        skipped = get_skipped(file)
        for suite, reason, _ in skipped:
            suite_width = max(suite_width, len(suite))
            reason_width = max(reason_width, len(reason))
    fmt = f"{{:{suite_width}}}  {{:{reason_width}}}  {{}}"
    for file in logs:
        skipped = get_skipped(file)
        for suite, reason, test in skipped:
            print(fmt.format(suite, reason, test))


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
                    print(fmt.format(int(msecs), file, test))
                total += int(msecs)
            if not verbose:
                print(fmt.format(total, file))
            file_total += total
        if verbose:
            print("# total: ", file_total)


def get_traces(job: Job) -> list[str]:
    """
    Get traces recorded by `record_info("TRACE", $trace)`
    """
    traces = [
        detail["text_data"]
        for result in job.results
        for detail in result["details"]
        if "title" in detail and detail["title"] == "TRACE"
    ]
    package = job.settings.get("BATS_PACKAGE", "")
    # Ignore OOM failures in runc since these are expected
    if package == "runc":
        traces = list(filter(lambda t: "mem_cgroup_out_of_memory" not in t, traces))
    return traces


def print_jobgroup(url: str, verbose: bool = False) -> None:
    """
    Print job group
    """
    now = datetime.now()
    builds = list(filter(lambda b: now - b.date < timedelta(days=10), get_builds(url)))

    if not builds:
        return

    urls = []
    with ThreadPoolExecutor(max_workers=len(builds)) as executor:
        for results in executor.map(
            lambda b: get_build_jobs(url, b),
            builds,
        ):
            urls.extend(
                [
                    item["url"]
                    for item in results
                    if item["name"].split("@")[0].endswith("_testsuite")
                ]
            )

    jobs: list[Job] = []
    if verbose:
        with ThreadPoolExecutor(max_workers=len(urls)) as executor:
            for job in executor.map(
                lambda u: get_job(u, include_comments=verbose, details=verbose),
                urls,
            ):
                if job is not None:
                    jobs.append(job)
    else:
        jobs = get_jobs(urls[0], list(map(int, map(os.path.basename, urls))))
    jobs.sort(
        key=lambda j: (j.settings["BUILD"], j.settings["ARCH"], j.settings["TEST"])
    )

    for job in jobs:
        print_job(job, verbose=verbose)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
