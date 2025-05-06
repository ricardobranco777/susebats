"""
List BATS jobs on o.s.d & o3
"""

import argparse
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

from bats.repos import REPOS, build_url, get_urls
from bats.job import get_job, Job


TIMING = re.compile(r" in \d+ms$")


def main_jobs(args: argparse.Namespace) -> None:
    """
    Main function
    """
    urls = []
    with ThreadPoolExecutor(max_workers=len(REPOS)) as executor:
        for results in executor.map(get_urls, REPOS):
            urls.extend(results)

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
    print(f"{status:10}  {job.url:<42}  {job.name}")
    if not verbose:
        return
    print_passed(job)
    if status == "passed":
        return
    if job.origin:
        print(f"\tCloned from: {job.origin}")
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
            ("Automatic investigation jobs", "Investigate retry job")
        ):
            continue
        time = comment.updated.isoformat(sep=" ", timespec="seconds")
        for bugref in comment.bugrefs:
            print(f"\t=> {time} {bugref.url}\t{bugref.title} by {comment.author}")
        if len(comment.bugrefs) == 0:
            print(f"\t=> {time} {comment.text} by {comment.author}")
