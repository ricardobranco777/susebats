"""
versions module
"""

import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from bats.suse import fetch_version, RPMVersion


PACKAGES = r"(aardvark-dns|buildah|netavark|podman|runc|skopeo)"
GIT_VERSION = re.compile(rf"{PACKAGES} version$")
RPM_VERSION = re.compile(rf"{PACKAGES} package version$")


@dataclass
class Version:
    """
    Version class
    """

    git_version: str
    rpm_version: str


def get_rpm_version(info: str) -> tuple[str, str]:
    """
    Get RPM version from package name
    """
    assert info.endswith((".aarch64", ".noarch", ".ppc64le", ".s390x", ".x86_64"))
    package, version, release = info.rsplit(".", 1)[0].rsplit("-", 2)
    return package, f"{version}-{release}"


def get_git_version(title: str, info: str) -> tuple[str, str]:
    """
    Get git version
    """
    package = title.split()[0]
    version = ""
    lines = info.splitlines()
    for line in lines:
        if line.split()[0] == "Version:":
            version = line.split()[-1]
            break
    if not version:
        if "version" in lines[0]:
            version = lines[0].split()[2]
        else:
            version = lines[0].split()[-1]
    return package, version


def get_versions(results: list[dict]) -> dict[str, Version]:
    """
    Get the git & RPM version for packages in openQA results
    """

    versions: dict[str, Version] = {}

    # This needs to be done in openQA for this function to work, in this order:
    #   record_info("podman version", script_output("podman version"));
    #   record_info("podman package version", script_output("rpm -q podman"));
    for result in results:
        # Skip TAP parser output
        if result["has_parser_text_result"]:
            continue
        package = git_version = rpm_version = ""
        for detail in result["details"]:
            if "title" not in detail:
                continue
            if GIT_VERSION.match(detail["title"]):
                _, git_version = get_git_version(detail["title"], detail["text_data"])
            elif RPM_VERSION.match(detail["title"]):
                package, rpm_version = get_rpm_version(detail["text_data"])
                break
        if package:
            versions[package] = Version(
                git_version=git_version, rpm_version=rpm_version
            )

    return versions


def get_published(product: str, packages: list[str]) -> dict[str, RPMVersion]:
    """
    Get published RPM versions for packages in product
    """
    published = {}
    with ThreadPoolExecutor(max_workers=min(10, len(packages))) as executor:
        for package, rpm_version in zip(
            packages, executor.map(lambda p: fetch_version(product, p), packages)
        ):
            if rpm_version is not None:
                published[package] = rpm_version
    return published
