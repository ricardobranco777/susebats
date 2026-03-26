"""
Job module
"""

import os
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import parse_qs, urljoin, urlparse

from bats.issues import get_issue, Issue
from bats.requests import get_json


@dataclass(frozen=True)
class Comment:
    """
    Comment class
    """

    author: str
    created: datetime
    updated: datetime
    text: str
    issues: list[Issue]


@dataclass(frozen=True)
class Job:  # pylint: disable=too-many-instance-attributes
    """
    Job class
    """

    name: str
    url: str
    cloned_as: str
    cloned_from: str
    seconds: int
    logs: list[str]
    result: str
    state: str
    results: list[dict]
    settings: dict[str, str]
    comments: list[Comment]


def get_job_id(url: str, params: dict[str, list[str]]) -> int | None:
    """
    Get job ID from URL with no job ID in URL
    """
    urlx = urlparse(url)
    if not urlx.query:
        return int(os.path.basename(urlx.path).removeprefix("t"))

    api_url = f"{urlx.scheme}://{urlx.netloc}/api/v1/jobs/"
    data = get_json(api_url, params=params, key="jobs")
    if data is None or len(data) == 0:
        return None
    for job in reversed(data):
        if job["settings"]["BUILD"].isdigit():
            return job["id"]
    return data[-1]["id"]


def get_job(
    url: str, include_comments: bool = False, details: bool = False
) -> Job | None:
    """
    Get a job
    """
    if not url.startswith(("http:", "https:")):
        url = f"https://{url}"
    urlx = urlparse(url)

    params: dict[str, list[str]] = parse_qs(urlx.query)
    job_id = get_job_id(url, params=params)
    if job_id is None:
        return None

    api_url = f"{urlx.scheme}://{urlx.netloc}/api/v1/jobs/{job_id}"
    if details:
        api_url = f"{api_url}/details"
    info = get_json(api_url, key="job")
    if info is None:
        return None
    assert isinstance(info, dict)

    url = f"{urlx.scheme}://{urlx.netloc}/tests/{job_id}"

    for key in ("clone_id", "origin_id"):
        info[key] = urljoin(url, str(info[key])) if info.get(key) else ""

    logs = []
    for key in ("logs", "ulogs"):
        logs.extend([urljoin(f"{url}/", f"file/{log}") for log in info.get(key, [])])

    seconds = -1
    if info["t_started"] and info["t_finished"]:
        seconds = int(
            (
                datetime.fromisoformat(info["t_finished"])
                - datetime.fromisoformat(info["t_started"])
            ).total_seconds()
        )

    comments: list[Comment] = []
    if include_comments:
        api_url = f"{urlx.scheme}://{urlx.netloc}/api/v1/jobs/{job_id}/comments"
        data = get_json(api_url)
        if data is None:
            return None
        comments = []
        for item in data:
            issues = []
            if item["bugrefs"]:
                issues = list(filter(None, (get_issue(b) for b in item["bugrefs"])))
            elif item["text"].startswith("https://"):
                issues = list(filter(None, [get_issue(item["text"].split()[0])]))
            comments.append(
                Comment(
                    author=item["userName"],
                    created=datetime.fromisoformat(item["created"]).astimezone(),
                    updated=datetime.fromisoformat(item["updated"]).astimezone(),
                    text=item["text"].replace("\r", "").replace("\n", " ").strip(),
                    issues=issues,
                )
            )

    return Job(
        cloned_as=info["clone_id"],
        cloned_from=info["origin_id"],
        comments=comments,
        logs=logs,
        name=info["name"],
        result=info["result"],
        results=info.get("testresults", []),
        seconds=seconds,
        settings=info["settings"],
        state=info["state"],
        url=url,
    )
