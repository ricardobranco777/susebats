"""
Job module
"""

import os
from dataclasses import asdict, dataclass
from datetime import datetime
from urllib.parse import urlencode, urlparse

from bats.requests import get_json


@dataclass(frozen=True)
class Build:
    """
    Build class
    """

    build: str
    date: datetime
    distri: str
    groupid: int
    version: str


def get_builds(url: str) -> list[Build]:
    """
    Get builds
    """
    urlx = urlparse(url)
    groupid = int(os.path.basename(urlx.path))
    api_url = f"{urlx.scheme}://{urlx.netloc}/api/v1/job_groups/{groupid}/build_results"
    data = get_json(api_url, key="build_results")
    assert isinstance(data, list)
    return [
        Build(
            build=item["build"],
            date=datetime.fromisoformat(item["date"]),
            distri=list(item["distris"].keys()).pop(),
            groupid=groupid,
            version=item["version"],
        )
        for item in data
    ]


def get_jobs(url: str, build: Build, **kwargs) -> list[dict[str, str]]:
    """
    Get jobs from build
    Valid kwargs: result, state, groupid, etc
    """
    extra = asdict(build)
    extra.pop("date")
    if kwargs is not None:
        extra.update(kwargs)
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
