#!/usr/bin/env python3
"""
Print markdown table with the test matrix
with a nice badge with openQA results.
"""

import sys
from urllib.parse import parse_qs, urlparse


def table() -> None:
    """
    Generate markdown table
    """
    arches = set()
    tests = set()
    matrix = {}

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        urlx = urlparse(line)
        qs = parse_qs(urlx.query)

        arch = qs["arch"][0]
        test = qs["test"][0]
        test = test.replace("_testsuite", "").removeprefix("container_host_")

        arches.add(arch)
        tests.add(test)
        matrix[(test, arch)] = line

    arches = sorted(arches)  # type: ignore
    tests = sorted(tests)  # type: ignore

    # Table header
    print("| Testsuite / Architecture | " + " | ".join(arches) + " |")
    print("|:---:|" + ":---:|" * len(arches))

    # Table body
    for test in tests:
        row = [test]
        for arch in arches:
            if (test, arch) in matrix:
                name = test.replace("_crun", " + crun").replace("_", " ")
                row.append(f"[![{name}_{arch}_logo]][{test}_{arch}]")
            else:
                row.append("")
        print("| " + " | ".join(row) + " |")
    print()

    # References
    for test in tests:
        for arch in arches:
            if (test, arch) not in matrix:
                continue

            url = matrix[(test, arch)]
            urlx = urlparse(url)
            badge = f"{urlx.scheme}://{urlx.netloc}{urlx.path.rstrip('/')}/badge?{urlx.query}"
            print(f"[{test}_{arch}_logo]: {badge}")
            print(f"[{test}_{arch}]: {url}")
            print()


if __name__ == "__main__":
    table()
