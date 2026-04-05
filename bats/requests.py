"""
session module
"""

import atexit
import logging
import os
import sys
from urllib3.util.retry import Retry

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from requests.utils import parse_header_links

try:
    from requests_toolbelt.utils import dump  # type: ignore
except ImportError:
    dump = None


session = requests.Session()
adapter = HTTPAdapter(
    max_retries=Retry(
        allowed_methods={"GET", "HEAD"},
        backoff_factor=0.1,
        status_forcelist={429, 502, 503, 504},
        total=10,
    ),
    pool_connections=200,
    pool_maxsize=200,
)
session.mount("https://", adapter)

TIMEOUT = 60


def debugme(got, *args, **kwargs):  # pylint: disable=unused-argument
    """
    Print requests response
    """
    got.hook_called = True
    if dump is not None:
        print(dump.dump_all(got).decode("utf-8"), file=sys.stderr)
    return got


def download_file(url: str) -> str | None:
    """
    Download a file from URL to current directory
    """
    filename = os.path.basename(url)
    try:
        with session.get(url, stream=True, timeout=TIMEOUT) as r:
            r.raise_for_status()
            with open(filename, "xb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    except RequestException as error:
        logging.error("%s: %s", url, error)
        return None
    return filename


def get_file(url: str) -> str | None:
    """
    Download a text file and return its contents
    """
    try:
        got = session.get(url, timeout=TIMEOUT)
        got.raise_for_status()
    except RequestException as error:
        logging.error("%s: %s", url, error)
        return None
    return got.text


def get_json(
    url: str | None, method: str = "GET", key: str | None = None, **kwargs
) -> dict | list[dict] | None:
    """
    Get JSON following pagination via Link header if present
    """
    results = []
    while url:
        try:
            got = session.request(method, url, timeout=TIMEOUT, **kwargs)
            got.raise_for_status()
            data = got.json()
        except RequestException as error:
            logging.error("%s: %s", url, error)
            return None

        page = data[key] if key is not None else data
        if method != "GET" or not isinstance(page, list):
            return page
        results.extend(page)

        if "Link" not in got.headers:
            break
        links = parse_header_links(got.headers["Link"])
        url = next((x["url"] for x in links if x.get("rel") == "next"), None)

    return results


def ping(url: str, timeout: int = 5) -> bool:
    """
    Ping URL to see if it's reachable
    """
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code < 400
    except RequestException:
        return False


if os.getenv("DEBUG"):
    session.hooks["response"].append(debugme)

atexit.register(session.close)
