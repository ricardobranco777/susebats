"""
dump all
"""

import argparse
import contextlib
import json
import tempfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from dataclasses import asdict, fields

from bats.job import get_job, Job
from bats.repos import REPOS, build_url, get_tests
from bats.requests import download_file
from bats.tap import grep_notok
from bats.versions import get_versions, TEST_URL


def main_all(args: argparse.Namespace) -> None:
    """
    Main function
    """
    _ = args

    tests = []
    with ThreadPoolExecutor(max_workers=len(REPOS)) as executor:
        for results in executor.map(get_tests, REPOS):
            tests.extend(results)

    date = datetime.now().date() - timedelta(days=1)
    build = date.strftime("%Y%m%d")

    items: list[dict[str, dict]] = []
    with ThreadPoolExecutor(max_workers=len(tests)) as executor:
        for test, job in zip(
            tests,
            executor.map(
                lambda p: get_job(build_url(p.url, build), full=True),
                tests,
            ),
        ):
            if job is None or build and build != job.settings["BUILD"] != build:
                continue
            if job.result not in {"passed", "failed"}:
                continue
            info = {
                field.name: getattr(job, field.name)
                for field in fields(job)
                if field.name not in {"results"}
            }
            info["logs"] = get_logs(job)
            items.append(
                {
                    "job": info,
                    "test": asdict(test),
                }
            )

    print(json.dumps(items))


def get_logs(job: Job) -> dict[str, dict[str, list[str]]]:
    """
    Get logs
    """
    logs: dict[str, dict[str, list[str]]] = defaultdict(dict)
    versions = get_versions(job.results)
    with tempfile.TemporaryDirectory() as tmpdir, contextlib.chdir(tmpdir):
        with ThreadPoolExecutor(max_workers=len(job.logs)) as executor:
            for file_url, file in zip(job.logs, executor.map(download_file, job.logs)):
                if file is None:
                    continue
                package = file.split("_")[0]
                if package == "aardvark":
                    package = "aardvark-dns"
                failed = grep_notok(file, alles=True)
                version = versions[package].git_version
                for test in failed:
                    test_url = TEST_URL[package].format(version, test)
                    logs[file_url][test_url] = failed[test]
    return logs
