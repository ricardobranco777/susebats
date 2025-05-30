"""
Services module
"""

import os
import sys
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

from requests.exceptions import RequestException

from bats.requests import get_json, session, TIMEOUT


BUGZILLA_TOKEN = os.getenv("BUGZILLA_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
REDMINE_TOKEN = os.getenv("REDMINE_TOKEN")


@dataclass(frozen=True)
class Issue:
    """
    Issue class
    """

    url: str
    title: str


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
    return Issue(url=url, title=data[0]["summary"])


def get_gitea_issue(url: str) -> Issue | None:
    """
    Get Gitea issue
    """
    urlx = urlparse(url)
    issues = "issues" if "/issues/" in url else "pulls"
    repo, issue = urlx.path[1:].split(f"/{issues}/")
    api_url = f"{urlx.scheme}://{urlx.netloc}/api/v1/repos/{repo}/{issues}/{issue}"
    data = get_json(api_url)
    if data is None:
        return None
    assert isinstance(data, dict)
    return Issue(url=url, title=data["title"])


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
    return Issue(url=url, title=data["title"])


def get_jira_issue(url: str) -> Issue | None:
    """
    Get Jira issue
    """
    if not JIRA_TOKEN:
        return None
    issue = os.path.basename(url)
    api_url = "https://jira.suse.com/rest/api/2/search"
    headers = {"Authorization": f"Bearer {JIRA_TOKEN}"}
    params = {
        "fields": "summary",
        "jql": f"key in ({issue})",
    }
    data = get_json(api_url, headers=headers, params=params, key="issues")
    if data is None:
        return None
    assert isinstance(data, list)
    return Issue(url=url, title=data[0]["fields"]["summary"])


def get_redmine_issue(url: str) -> Issue | None:
    """
    Get Redmine issue
    """
    if not REDMINE_TOKEN:
        return None
    api_url = f"{url}.json"
    headers = {"X-Redmine-API-Key": REDMINE_TOKEN}
    data = get_json(api_url, headers=headers, key="issue")
    if data is None:
        return None
    assert isinstance(data, dict)
    return Issue(url=url, title=data["subject"])


def get_issue(tag: str) -> Issue | None:  # pylint: disable=too-many-return-statements
    """
    Get issue from tag
    """
    tag_to_host = {
        "bsc": "bugzilla.suse.com",
        "boo": "bugzilla.opensuse.org",
        "gh": "github.com",
        "jsc": "jira.suse.com",
        "poo": "progress.opensuse.org",
        "ssd": "src.suse.de",
        "soo": "src.opensuse.org",
    }

    repo = ""
    if tag.startswith("https://"):
        url = tag
        host: str | None = urlparse(url).netloc
        issue = os.path.basename(tag)
    else:
        try:
            code, repo, issue = tag.split("#", 2)
        except ValueError:
            code, issue = tag.split("#", 1)
        host = tag_to_host.get(code)
    if host is None:
        return Issue(url="", title=tag)

    url = ""
    if host.startswith("bugzilla"):
        url = f"https://{host}/show_bug.cgi?id={issue}"
        return get_bugzilla_issue(url)
    if host == "progress.opensuse.org":
        url = f"https://{host}/issues/{issue}"
        return get_redmine_issue(url)
    if host.endswith("github.com"):
        return get_github_issue(repo, int(issue))
    if host.startswith("src."):
        return get_gitea_issue(tag)
    if "jira" in host:
        url = f"https://{host}/browse/{issue}"
        return get_jira_issue(url)
    return Issue(url="", title=tag)
