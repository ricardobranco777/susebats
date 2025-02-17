"""
Services module
"""

import os
import re
import sys
from dataclasses import dataclass
from urllib.parse import urljoin

from requests.exceptions import RequestException

from bats.requests import get_json, session, TIMEOUT


BUGZILLA_TOKEN = os.getenv("BUGZILLA_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REDMINE_TOKEN = os.getenv("REDMINE_TOKEN")


@dataclass(frozen=True)
class Issue:
    """
    Issue class
    """

    url: str
    summary: str


def get_bugzilla_issue(url: str) -> Issue | None:
    """
    Get Bugzilla issue
    """
    if not BUGZILLA_TOKEN:
        return None
    if "=" in url:
        issue = url.split("=")[-1]
    else:
        issue = url.split("/")[-1]
    api_url = urljoin(url, "rest/bug")
    params = {
        "Bugzilla_api_key": BUGZILLA_TOKEN,
        "include_fields": "id,summary",
        "id": issue,
    }
    try:
        got = session.get(api_url, params=params, timeout=TIMEOUT)
        got.raise_for_status()
        data = got.json()["bugs"]
    except RequestException as exc:
        # Prevent API key leaking in the URL
        error = str(exc).split("?", maxsplit=1)[0]
        print(f"ERROR: {url}: {error}", file=sys.stderr)
        return None
    return Issue(url=url, summary=data[0]["summary"])


def get_github_issue(repo: str, issue: int) -> Issue | None:
    """
    Get Github issue
    """
    if not GITHUB_TOKEN:
        return None
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    api_url = f"https://api.github.com/repos/{repo}/issues/{issue}"
    data = get_json(api_url, headers=headers)
    if data is None:
        return None
    assert isinstance(data, dict)
    url = f"https://github.com/{repo}/issues/{issue}"
    return Issue(url=url, summary=data["title"])


def get_redmine_issue(url: str) -> Issue | None:
    """
    Get Redmine issues
    """
    if not REDMINE_TOKEN:
        return None
    api_url = f"{url}.json"
    headers = {"X-Redmine-API-Key": REDMINE_TOKEN}
    data = get_json(api_url, headers=headers, key="issue")
    if data is None:
        return None
    assert isinstance(data, dict)
    return Issue(url=url, summary=data["subject"])


def get_tagurl(tag: str) -> Issue | None:
    """
    Get URL from tag
    """
    tag_to_host = {
        "bsc": "bugzilla.suse.com",
        "boo": "bugzilla.opensuse.org",
        "gh": "github.com",
        "poo": "progress.opensuse.org",
    }

    repo = ""
    try:
        code, repo, issue = re.split(r"[#!]", tag)
    except ValueError:
        code, issue = tag.split("#", 1)
    host = tag_to_host.get(code)
    if host is None:
        return Issue(url="", summary=tag)

    url = ""
    if host.startswith("bugzilla"):
        url = f"https://{host}/show_bug.cgi?id={issue}"
        return get_bugzilla_issue(url)
    if host == "progress.opensuse.org":
        url = f"https://{host}/issues/{issue}"
        return get_redmine_issue(url)
    if host.endswith("github.com"):
        return get_github_issue(repo, int(issue))
    return Issue(url="", summary=tag)
