"""
Job module
"""

import os
import sys
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

import requests
from requests.exceptions import RequestException


_TIMEOUT = 30

session = requests.Session()


@dataclass
class Job:
    """
    Job class
    """

    name: str
    logs: list[str] | None
    result: str
    results: list[dict] | None
    url: str


def get_job_id(
    url_string: str, params: dict[str, list[str]] | None = None
) -> int | None:
    """
    Get job ID from URL with no job ID in URL
    """
    url = urlparse(url_string)
    if not url.query:
        return int(os.path.basename(url.path).removeprefix("t"))

    api_url = f"{url.scheme}://{url.netloc}/api/v1/jobs/overview"
    try:
        got = session.get(api_url, params=params, timeout=_TIMEOUT)
        got.raise_for_status()
        data = got.json()
    except RequestException as error:
        print(f"ERROR: {url_string}: {error}", file=sys.stderr)
        return None
    if len(data) != 1:
        return None

    return data[0]["id"]


def get_job(
    url_string: str, full: bool = False, build: str | None = None
) -> Job | None:
    """
    Get a job
    """
    if not url_string.startswith(("http:", "https:")):
        url_string = f"https://{url_string}"
    url = urlparse(url_string)

    params: dict[str, list[str]] = parse_qs(url.query)
    if build:
        params["build"] = [build]

    job_id = get_job_id(url_string, params=params)
    if job_id is None:
        return None

    api_url = f"{url.scheme}://{url.netloc}/api/v1/jobs/{job_id}"
    if full:
        api_url = f"{api_url}/details"
    try:
        got = session.get(api_url, timeout=_TIMEOUT)
        got.raise_for_status()
        info = got.json()["job"]
    except RequestException as error:
        print(f"ERROR: {api_url}: {error}", file=sys.stderr)
        return None

    if build and info["settings"]["BUILD"] != build:
        return None

    return Job(
        logs=info.get("ulogs"),
        name=info["name"],
        result=info["result"] if info["result"] != "none" else info["state"],
        results=info.get("testresults"),
        url=f"{url.scheme}://{url.netloc}/tests/{job_id}",
    )
