"""
List BATS jobs on o.s.d & o3
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

from bats.repos import REPOS, build_url, get_urls
from bats.job import get_job, Job


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
            lambda u: get_job(build_url(u, build), full=args.verbose), urls
        ):
            if job is None or build and not job.settings["BUILD"].startswith(build):
                continue
            print_job(job)


def print_job(job: Job) -> None:
    """
    Print job
    """
    status = job.result.upper() if job.result == "failed" else job.result
    print(f"{status:10}  {job.url:<42}  {job.name}")
    # Skip non-failed jobs
    if status != "FAILED":
        return
    for result in job.results:
        # Skip non-failed modules
        if result["result"] == "failed":
            if not result["has_parser_text_result"]:
                print(f"\t{result['name']}")
                continue
            for test in result["details"]:
                # Skip non-failed sub-tests
                if test["result"] == "fail":
                    print(f"\t{result['name']:<30}  {test['text_data']}")
