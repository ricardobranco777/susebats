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


def get_job_id(url: str) -> int | None:
    """
    Get job ID from URL with no job ID in URL
    """
    urlx = urlparse(url)
    if not urlx.query:
        return int(os.path.basename(urlx.path).removeprefix("t"))

    api_url = f"{urlx.scheme}://{urlx.netloc}/api/v1/jobs/"
    params: dict[str, list[str]] = parse_qs(urlx.query)
    data = get_json(api_url, key="jobs", params=params)
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
    urlx = urlparse(url)
    job_id = get_job_id(url)
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


def get_jobs(url: str, ids: list[int]) -> list[Job]:
    """
    Get (less) info on a list of jobs with a single request
    """
    urlx = urlparse(url)

    query = "ids=" + ",".join(map(str, ids))
    api_url = f"{urlx.scheme}://{urlx.netloc}/api/v1/jobs?{query}"
    data = get_json(api_url, key="jobs")
    if data is None:
        return []
    assert isinstance(data, list)

    jobs = []
    for info in data:
        job_id = info["id"]
        url = f"{urlx.scheme}://{urlx.netloc}/tests/{job_id}"

        for key in ("clone_id", "origin_id"):
            info[key] = urljoin(url, str(info[key])) if info.get(key) else ""

        seconds = -1
        if info["t_started"] and info["t_finished"]:
            seconds = int(
                (
                    datetime.fromisoformat(info["t_finished"])
                    - datetime.fromisoformat(info["t_started"])
                ).total_seconds()
            )

        jobs.append(
            Job(
                cloned_as=info["clone_id"],
                cloned_from=info["origin_id"],
                comments=[],
                logs=[],
                name=info["name"],
                result=info["result"],
                results=info.get("testresults", []),
                seconds=seconds,
                settings=info["settings"],
                state=info["state"],
                url=url,
            )
        )

    return jobs
