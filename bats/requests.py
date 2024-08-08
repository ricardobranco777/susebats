"""
session module
"""

import atexit
import os
import sys

import requests
from requests.exceptions import RequestException

try:
    from requests_toolbelt.utils import dump  # type: ignore
except ImportError:
    dump = None


session = requests.Session()

TIMEOUT = 30


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
        print(f"ERROR: {url}: {error}", file=sys.stderr)
        return None
    return filename


if os.getenv("DEBUG"):
    session.hooks["response"].append(debugme)
atexit.register(session.close)
