"""
List BATS jobs on o.s.d & o3
"""

import argparse
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from bats.job import get_job, Job
from bats.repos import REPOS, get_urls
from bats.requests import ping
from bats.utils import get_traces


EXTRA = re.compile(r"-(?:container_host_)?[a-z]+_(e2e|testsuite).*$")
TIMING = re.compile(r" in \d+ms(?: # .*)?$")


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


def main_jobs(args: argparse.Namespace) -> None:
    """
    Main function
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
            lambda u: get_job(u, full=args.verbose),
            urls,
        ):
            if job is None:
                continue
            print_job(job, verbose=args.verbose)


def print_job(job: Job, verbose: bool = False) -> None:
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
    status = job.result.upper() if job.result == "failed" else job.result
    status = status.split("_")[-1]
    if verbose:
        print(job.seconds, end="\t")
    print(f"{status:10}  {package:15}  {arch:7}  {job.url:<42}  {name}")
    if verbose:
        print_passed(job)
        print_traces(job)
        for core in (log for log in job.logs if ".core" in log):
            print(f"\tcore: {core}")
        if status != "passed":
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


def print_traces(job: Job) -> None:
    """
    Print traces recorded by `record_info("TRACE", $trace)`
    """
    traces = get_traces(job)
    if len(traces) > 0:
        serial0 = [log for log in job.logs if log.endswith("serial0.txt")].pop()
        print(f"\ttraces: {serial0}")


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
                    title = TIMING.sub("", test["text_data"])
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
