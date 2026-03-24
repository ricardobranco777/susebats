"""
Job module
"""

import os
from dataclasses import asdict, dataclass
from datetime import datetime
from urllib.parse import urlencode, urlparse

from bats.const import JOB_STATES, JOB_RESULTS
from bats.requests import get_json


@dataclass(frozen=True)
class Build:
    """
    Build class
    """

    build: str
    date: datetime
    distri: str
    group_id: int
    version: str


def get_builds(url: str) -> list[Build]:
    """
    Get builds
    """
    urlx = urlparse(url)
    group_id = int(os.path.basename(urlx.path))
    api_url = (
        f"{urlx.scheme}://{urlx.netloc}/api/v1/job_groups/{group_id}/build_results"
    )
    data = get_json(api_url, key="build_results")
    assert isinstance(data, list)
    return [
        Build(
            build=item["build"],
            date=datetime.fromisoformat(item["date"]),
            distri=list(item["distris"].keys()).pop(),
            group_id=group_id,
            version=item["version"],
        )
        for item in data
    ]


def get_jobs(
    url: str, build: Build, result: str = "", state: str = ""
) -> list[dict[str, str]]:
    """
    Get jobs from build
    """
    extra = asdict(build)
    if result:
        if result not in set(JOB_RESULTS):
            raise ValueError(f"Invalid result: {result}")
        extra["result"] = result
    if state:
        if state not in set(JOB_STATES):
            raise ValueError(f"Invalid state: {state}")
        extra["state"] = state
    extra.pop("date")
    urlx = urlparse(url)
    api_url = f"{urlx.scheme}://{urlx.netloc}/api/v1/jobs/overview?" + urlencode(extra)
    data = get_json(api_url)
    assert isinstance(data, list)
    return [
        {
            "name": item["name"],
            "url": f"{urlx.scheme}://{urlx.netloc}/tests/{item['id']}",
        }
        for item in data
    ]
