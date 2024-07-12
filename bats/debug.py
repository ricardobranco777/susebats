"""
Debug utilities
"""

import sys

try:
    from requests_toolbelt.utils import dump  # type: ignore
except ImportError:
    dump = None


def debugme(got, *args, **kwargs):  # pylint: disable=unused-argument
    """
    Print requests response
    """
    got.hook_called = True
    if dump is not None:
        print(dump.dump_all(got).decode("utf-8"), file=sys.stderr)
    return got
