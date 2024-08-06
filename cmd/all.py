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
from bats.repos import REPOS, get_build, get_tests
from bats.tap import download_file, grep_notok
from bats.versions import get_versions, TEST_URL


def nested_defaultdict():
    """
    Helper function to create a defaultdict of defaultdicts
    """
    return defaultdict(nested_defaultdict)


def main_all(args: argparse.Namespace) -> None:
    """
    Main function
    """
    _ = args

    tests = []
    with ThreadPoolExecutor(max_workers=min(10, len(REPOS))) as executor:
        for results in executor.map(get_tests, REPOS):
            tests.extend(results)

    date = datetime.now().date() - timedelta(days=1)
    build = date.strftime("%Y%m%d")

    items: dict[str, dict] = nested_defaultdict()
    with ThreadPoolExecutor(max_workers=min(10, len(tests))) as executor:
        for test, job in zip(
            tests,
            executor.map(
                lambda p: get_job(p.url, full=True, build=get_build(p.url, build)),
                tests,
            ),
        ):
            if job is None:
                continue
            info = {
                field.name: getattr(job, field.name)
                for field in fields(job)
                if field.name not in {"results"}
            }
            info["logs"] = get_logs(job)
            items[test.distri][test.version][test.arch][test.name] = {
                "test": asdict(test),
                "job": info,
            }

    print(json.dumps(items, default=str, sort_keys=True))


def get_logs(job: Job) -> dict[str, dict[str, list[str]]]:
    """
    Get logs
    """
    logs: dict[str, dict[str, list[str]]] = defaultdict(dict)
    versions = get_versions(job.results)
    with tempfile.TemporaryDirectory() as tmpdir, contextlib.chdir(tmpdir):
        with ThreadPoolExecutor(max_workers=min(10, len(job.logs))) as executor:
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
