#!/usr/bin/env python3
"""
list failures & xfailures in Junit XML files
"""

import argparse
import sys
import xml.etree.ElementTree as ET


def process(path: str, alles: bool = False) -> None:
    """
    Process Junit XML
    """
    with open(path, encoding="utf-8") as file:
        data = file.read()
    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        sys.exit(f"Malformed JUnit XML file: {path}: {e}")

    keys = ["failure"]
    if alles:
        keys.append("xfailure")

    tests = []
    for testcase in root.iter("testcase"):
        key: str | None = None
        for k in keys:
            if testcase.find(k) is not None:
                key = k
                break
        if key is None:
            continue
        name = testcase.get("name", "unknown")
        classname = testcase.get("classname", "")
        tests.append(f"{key:>8}  {classname}::{name}")
    for test in sorted(tests):
        print(path, test, sep="\t")


def xmain() -> None:
    """
    Main function
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("file", nargs="+", help="Junit XML file")
    args = parser.parse_args()
    for path in args.file:
        process(path, alles=args.verbose)


if __name__ == "__main__":
    try:
        xmain()
    except KeyboardInterrupt:
        sys.exit(1)
