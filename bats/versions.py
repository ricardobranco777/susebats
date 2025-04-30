"""
versions module
"""

import re


# NOTE: aardvark is repeated as aardvark-dns because we use aardvark.pm for the openQA module
TEST_URL = {
    "aardvark": "https://github.com/containers/aardvark-dns/blob/v{}/test/{}.bats",
    "aardvark-dns": "https://github.com/containers/aardvark-dns/blob/v{}/test/{}.bats",
    "buildah": "https://github.com/containers/buildah/blob/v{}/tests/{}.bats",
    "netavark": "https://github.com/containers/netavark/blob/v{}/test/{}.bats",
    "podman": "https://github.com/containers/podman/blob/v{}/test/system/{}.bats",
    "runc": "https://github.com/opencontainers/runc/blob/v{}/tests/integration/{}.bats",
    "skopeo": "https://github.com/containers/skopeo/blob/v{}/systemtest/{}.bats",
}


def get_git_version(info: str) -> str:
    """
    Get git version
    """
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
    return version


def get_version(package: str, results: list[dict]) -> str | None:
    """
    Get the git version for packages in openQA results
    """

    # This needs to be done in openQA for this function to work:
    #   record_info("podman version", script_output("podman version"));
    for result in results:
        # Skip TAP parser output
        if result["has_parser_text_result"]:
            continue
        for detail in result["details"]:
            if "title" not in detail:
                continue
            if re.match(rf"{package} version", detail["title"]):
                git_version = get_git_version(detail["text_data"])
                return git_version

    return None
