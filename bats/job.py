"""
Job module
"""

import os
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import parse_qs, urljoin, urlparse

from bats.requests import get_json
from bats.services import get_tagurl, Issue


@dataclass(frozen=True)
class Comment:
    """
    Comment class
    """

    author: str
    bugrefs: list[Issue]
    created: datetime
    text: str
    updated: datetime


@dataclass(frozen=True)
class Job:  # pylint: disable=too-many-instance-attributes
    """
    Job class
    """

    name: str
    url: str
    logs: list[str]
    result: str
    results: list[dict]
    settings: dict[str, str]
    comments: list[Comment]
    extra: dict[str, str | int]


def get_job_id(url: str, params: dict[str, list[str]] | None = None) -> int | None:
    """
    Get job ID from URL with no job ID in URL
    """
    urlx = urlparse(url)
    if not urlx.query:
        return int(os.path.basename(urlx.path).removeprefix("t"))

    api_url = f"{urlx.scheme}://{urlx.netloc}/api/v1/jobs/overview"
    data = get_json(api_url, params=params)
    if data is None:
        return None
    if len(data) != 1:
        return None

    return data[0]["id"]


def get_job(url: str, full: bool = False, previous: bool = False) -> Job | None:
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
    if full:
        api_url = f"{api_url}/details"
    info = get_json(api_url, key="job")
    if info is None:
        return None
    assert isinstance(info, dict)

    url = f"{urlx.scheme}://{urlx.netloc}/tests/{job_id}"

    if previous and info["state"] != "done" and "origin_id" in info:
        return get_job(urljoin(url, str(info["origin_id"])), previous)

    logs = [urljoin(f"{url}/", f"file/{log}") for log in info.get("ulogs", [])]

    comments: list[Comment] = []
    if full and info["result"] == "failed":
        api_url = f"{urlx.scheme}://{urlx.netloc}/api/v1/jobs/{job_id}/comments"
        data = get_json(api_url)
        if data is not None:
            comments = [
                Comment(
                    author=item["userName"],
                    bugrefs=list(
                        filter(None, (get_tagurl(b) for b in item["bugrefs"]))
                    ),
                    created=datetime.fromisoformat(item["created"]).astimezone(),
                    text=item["text"].replace("\r", "").replace("\n", " ").strip(),
                    updated=datetime.fromisoformat(item["updated"]).astimezone(),
                )
                for item in data
            ]

    seconds = -1
    if info["t_started"] and info["t_finished"]:
        seconds = int(
            (
                datetime.fromisoformat(info["t_finished"])
                - datetime.fromisoformat(info["t_started"])
            ).total_seconds()
        )

    return Job(
        name=info["name"],
        url=url,
        logs=logs,
        result=info["result"] if info["result"] != "none" else info["state"],
        results=info.get("testresults", []),
        settings=info["settings"],
        comments=comments,
        extra={
            "origin": (
                urljoin(url, str(info["origin_id"])) if "origin_id" in info else ""
            ),
            "seconds": seconds,
        },
    )
