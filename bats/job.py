"""
Job module
"""

import os
import sys
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import parse_qs, urljoin, urlparse

from requests.exceptions import RequestException

from bats.requests import session, TIMEOUT


@dataclass(frozen=True)
class Comment:
    """
    Comment class
    """

    author: str
    bugref: str
    created: datetime
    text: str
    updated: datetime


@dataclass(frozen=True)
class Job:
    """
    Job class
    """

    comments: list[Comment]
    name: str
    logs: list[str]
    result: str
    results: list[dict]
    settings: dict[str, str]
    url: str


def get_job_id(url: str, params: dict[str, list[str]] | None = None) -> int | None:
    """
    Get job ID from URL with no job ID in URL
    """
    urlx = urlparse(url)
    if not urlx.query:
        return int(os.path.basename(urlx.path).removeprefix("t"))

    api_url = f"{urlx.scheme}://{urlx.netloc}/api/v1/jobs/overview"
    try:
        got = session.get(api_url, params=params, timeout=TIMEOUT)
        got.raise_for_status()
        data = got.json()
    except RequestException as error:
        print(f"ERROR: {url}: {error}", file=sys.stderr)
        return None
    if len(data) != 1:
        return None

    return data[0]["id"]


def get_job(url: str, full: bool = False) -> Job | None:
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
    try:
        got = session.get(api_url, timeout=TIMEOUT)
        got.raise_for_status()
        info = got.json()["job"]
    except RequestException as error:
        print(f"ERROR: {api_url}: {error}", file=sys.stderr)
        return None

    url = f"{urlx.scheme}://{urlx.netloc}/tests/{job_id}"
    logs = [
        urljoin(f"{url}/", f"file/{log}")
        for log in info.get("ulogs", [])
        if log.endswith(".tap")
    ]

    comments: list[Comment] = []
    if full and info["result"] == "failed":
        api_url = f"{urlx.scheme}://{urlx.netloc}/api/v1/jobs/{job_id}/comments"
        try:
            got = session.get(api_url, timeout=TIMEOUT)
            got.raise_for_status()
            data = got.json()
        except RequestException as error:
            print(f"ERROR: {api_url}: {error}", file=sys.stderr)
        comments = [
            Comment(
                author=item["userName"],
                bugref=item["bugrefs"][0],
                created=datetime.fromisoformat(item["created"]).astimezone(),
                text=item["text"].replace("\n", " ").strip(),
                updated=datetime.fromisoformat(item["updated"]).astimezone(),
            )
            for item in data
            if item["bugrefs"]
        ]

    return Job(
        comments=comments,
        logs=logs,
        name=info["name"],
        result=info["result"] if info["result"] != "none" else info["state"],
        results=info.get("testresults", []),
        settings=info["settings"],
        url=url,
    )
