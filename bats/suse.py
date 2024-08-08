"""
SUSE module
"""

import re
from functools import cache

from requests.exceptions import RequestException

from bats.requests import session, TIMEOUT
from bats.rpmversion import RPMVersion


def get_data(
    url: str,
    headers: dict[str, str] | None = None,
    params: dict[str, str | int] | None = None,
) -> list[dict]:
    """
    Get data from URL
    """
    try:
        got = session.get(url, headers=headers, params=params, timeout=TIMEOUT)
        got.raise_for_status()
    except RequestException as error:
        print(f"ERROR: {url}: {error}")
        raise
    return got.json()["data"]


@cache
def get_products() -> list[dict]:
    """
    Get products
    """
    url = "https://scc.suse.com/api/package_search/products"
    headers = {"Accept": "application/vnd.scc.suse.com.v4+json"}
    return get_data(url, headers=headers)


# Cache the product list
_ = get_products()


def fetch_version(product: str, package: str) -> RPMVersion | None:
    """
    Fetch latest package version for the specified product
    """
    product_id = get_product_id(product)
    if product_id is None:
        return None

    url = "https://scc.suse.com/api/package_search/packages"
    headers = {"Accept": "application/vnd.scc.suse.com.v4+json"}
    params: dict[str, str | int] = {
        "query": package,
        "product_id": product_id,
    }
    data = get_data(url, headers=headers, params=params)

    regex = re.compile(rf"{package}$")
    latest: dict[str, RPMVersion] = {}
    for info in sorted(
        filter(lambda i: regex.match(i["name"]), data),
        key=lambda i: (i["name"], RPMVersion(i["version"], i["release"])),
    ):
        latest[info["name"]] = RPMVersion(info["version"], info["release"])

    return latest[package]


def get_product_identifier(product: str) -> str | None:
    """
    Get SUSE product name from openQA product triplet
    """
    identifier: str | None = None
    arch = product.split("-")[-1]
    if product.startswith("sle-micro-"):
        version = product.split("sle-micro-")[1].split("-")[0]
        if int(version[0]) > 5:
            identifier = f"SL-Micro/{version}/{arch}"
        elif int(version[2]) > 2:
            identifier = f"SLE-Micro/{version}/{arch}"
        else:
            identifier = f"SUSE-MicroOS/{version}/{arch}"
    elif product.startswith("sle-15-SP"):
        version = product[len("sle-15-SP")]
        identifier = f"SLES/15.{version}/{arch}"
    elif product.startswith("opensuse-"):
        return None

    assert identifier is not None
    return identifier


def get_product_id(product: str) -> int | None:
    """
    Get SUSE product id from openQA product triplet
    """
    identifier = get_product_identifier(product)
    if identifier is None:
        return None
    for suseproduct in get_products():
        if suseproduct["identifier"] == identifier:
            return suseproduct["id"]
    return None
