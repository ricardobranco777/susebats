#!/usr/bin/env python3
"""
Helpers to read JUnit XML
"""

import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass

from bats.repos import get_url


@dataclass(frozen=True)
class Test:
    """
    Test class
    """

    name: str
    url: str
    tag: str
    text: str


def get_failures(  # pylint: disable=too-many-locals
    file: str, ignored: bool = False
) -> list[Test]:
    """
    Find the failed tests in a JUnit XML file.

    If `ignored` is True, also include <xfailure> entries (expected failures).
    """
    tree = ET.parse(file)
    root = tree.getroot()
    tests: list[Test] = []

    prefix = root.attrib["name"].removeprefix("bats-")

    package = root.attrib.get("package", "")
    version = root.attrib.get("version", "")
    # fallback: read <property> entries if attributes missing
    for prop in root.findall("./properties/property"):
        if not package and prop.get("name") == "package":
            package = prop.get("value", "")
        elif not version and prop.get("name") == "version":
            version = prop.get("value", "")

    for tc in root.iter("testcase"):
        failure = tc.find("failure")
        xfailure = tc.find("xfailure")

        # always include real failures/errors
        if failure is not None:
            node = failure
        # include xfailure only when requested
        elif ignored and xfailure is not None:
            node = xfailure
        else:
            continue

        is_bats = tc.attrib["classname"].endswith(".bats")
        filename = tc.attrib["classname"].removeprefix(f"{prefix}-")
        if is_bats:
            filename = filename.removesuffix(".bats")

        fail = node.tag if node.tag == "xfailure" else node.tag.upper()
        test = tc.attrib["name"]
        text = (node.text or "").strip()
        system_err = tc.find("system-err")
        if system_err is not None and system_err.text:
            text += "\n" + system_err.text.strip()

        tests.append(
            Test(
                name=test,
                url=get_url(package, version, filename) if is_bats else filename,
                tag=fail,
                text=text,
            )
        )

    return tests


def get_skipped(file: str) -> list[tuple[str, str, str]]:
    """
    Find the skipped tests in a JUnit XML file
    """
    tree = ET.parse(file)
    root = tree.getroot()
    skipped: list[tuple[str, str, str]] = []

    prefix = root.attrib["name"].removeprefix("bats-")

    for tc in root.iter("testcase"):
        skip = tc.find("skipped")
        if skip is None:
            continue
        bats_file = (
            tc.attrib["classname"].removeprefix(f"{prefix}-").removesuffix(".bats")
        )
        test = tc.attrib["name"]
        text = skip.attrib.get("message") or (skip.text or "")
        skipped.append((bats_file, text, test))
    return skipped


def get_timings(file: str) -> dict[str, list[tuple[str, float]]]:
    """
    Return timings (seconds) for each test in a JUnit XML file,
    grouped by classname
    """
    tree = ET.parse(file)
    root = tree.getroot()

    timings: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for tc in root.iter("testcase"):
        classname = tc.attrib["classname"]
        name = tc.attrib["name"]
        time = float(tc.attrib["time"]) * 1000
        timings[classname].append((name, time))
    return timings
