"""
List BATS jobs on o.s.d & o3
"""

import argparse
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

from bats.repos import REPOS, build_url, get_urls
from bats.requests import ping
from bats.job import get_job, Job


EXTRA = re.compile(r"-(?:container_host_)?[a-z]+_testsuite.*$")
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

    build = args.build
    if build and build.startswith("-") and len(build) < 8 and build[1:].isdigit():
        today = datetime.now().date()
        date = today - timedelta(days=int(build[1:]))
        build = date.strftime("%Y%m%d")

    with ThreadPoolExecutor(max_workers=len(urls)) as executor:
        for job in executor.map(
            lambda u: get_job(
                build_url(u, build), full=args.verbose, previous=args.previous
            ),
            urls,
        ):
            if job is None or build and not job.settings["BUILD"].startswith(build):
                continue
            print_job(job, verbose=args.verbose)


def print_job(job: Job, verbose: bool = False) -> None:
    """
    Print job
    """
    status = job.result.upper() if job.result == "failed" else job.result
    package = job.settings["BATS_PACKAGE"]
    runtime = job.settings.get("OCI_RUNTIME", "")
    if runtime:
        package = f"{package}+{runtime}"
    name = EXTRA.sub("", job.name)
    print(f"{status:10}  {package:13}  {job.url:<42}  {name}")
    if verbose:
        print_passed(job)
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
        print("\tPASSED:\t", " ".join(list(sorted(passed))))


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
            )
        ):
            continue
        for bugref in comment.issues:
            print(f"\t{bugref.url}\t{bugref.title}")
        if len(comment.issues) == 0:
            print(f"\t{comment.text} by {comment.author}")
