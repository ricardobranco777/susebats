"""
RPMVersion module
"""

from functools import total_ordering

import rpm  # type: ignore


@total_ordering
class RPMVersion:
    """
    RPMVersion class to compare RPM versions
    """

    def __init__(self, version: str, release: str) -> None:
        self.version = version
        self.release = release
        self._tuple = ("1", version, release)

    def __str__(self) -> str:
        return f"{self.version}-{self.release}"

    def __lt__(self, other) -> bool:
        # pylint: disable=no-member
        return rpm.labelCompare(self._tuple, other._tuple) < 0

    def __eq__(self, other) -> bool:
        # pylint: disable=no-member
        return rpm.labelCompare(self._tuple, other._tuple) == 0
