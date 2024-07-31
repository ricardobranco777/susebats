"""
List BATS jobs on o.s.d & o3
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

from bats.repos import REPOS, get_products
from bats.job import get_job, Job


def get_urls(repo: str) -> list[str]:
    """
    Get URL's from YAML schedules in repo
    """
    return [product.url for product in get_products(repo)]


def get_build(url: str, build: str | None) -> str | None:
    """
    Normalize build
    """
    if not build:
        return None
    # Append "-1" to aggregate tests in o.s.d
    if "openqa.suse.de" in url and build.isdigit():
        return f"{build}-1"
    return build


def main_jobs(args: argparse.Namespace) -> None:
    """
    Main function
    """
    urls = []
    with ThreadPoolExecutor(max_workers=min(10, len(REPOS))) as executor:
        for results in executor.map(get_urls, REPOS):
            urls.extend(results)

    build = args.build
    if build and build.startswith("-") and len(build) < 8 and build[1:].isdigit():
        today = datetime.now().date()
        date = today - timedelta(days=int(build[1:]))
        build = date.strftime("%Y%m%d")

    with ThreadPoolExecutor(max_workers=min(10, len(urls))) as executor:
        for job in executor.map(
            lambda u: get_job(u, full=args.verbose, build=get_build(u, build)), urls
        ):
            if job is None:
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
