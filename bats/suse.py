"""
SUSE module
"""

import re
from functools import cache

from bats.requests import get_json
from bats.rpmversion import RPMVersion


@cache
def get_products() -> list[dict] | None:
    """
    Get products
    """
    url = "https://scc.suse.com/api/package_search/products"
    headers = {"Accept": "application/vnd.scc.suse.com.v4+json"}
    products = get_json(url, headers=headers, key="data")
    if products is None:
        return None
    assert isinstance(products, list)
    return products


# Cache the product list
_ = get_products()


def opensuse_package_info(info: dict) -> dict:
    """
    Get openSUSE package info
    """
    # Extract version & release from rpm filename
    version, release = info["file"].rsplit(".", 2)[0].rsplit("-", 2)[1:]
    return {
        "name": info["name"],
        "version": version,
        "release": release,
    }


def fetch_version(product: str, package: str) -> RPMVersion | None:
    """
    Fetch latest package version for the specified product
    """
    if package == "aardvark":
        package = "aardvark-dns"
    if product.startswith("opensuse"):
        url = "https://mirrorcache.opensuse.org/rest/search/package_locations"
        headers = {"Accept": "application/json"}
        params = {
            "ignore_file": "json",
            "ignore_path": "/repositories/home:",
            "os": "tumbleweed",
            "official": 1,
            "package": package,
        }
    else:
        product_id = get_product_id(product)
        if product_id is None:
            return None

        url = "https://scc.suse.com/api/package_search/packages"
        headers = {"Accept": "application/vnd.scc.suse.com.v4+json"}
        params = {
            "query": package,
            "product_id": product_id,
        }

    data = get_json(url, headers=headers, params=params, key="data")
    if data is None:
        return None
    if product.startswith("opensuse"):
        data = [opensuse_package_info(p) for p in data]

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

    return identifier


def get_product_id(product: str) -> int | None:
    """
    Get SUSE product id from openQA product triplet
    """
    identifier = get_product_identifier(product)
    if identifier is None:
        return None
    products = get_products()
    if products is None:
        return None
    for suseproduct in products:
        if suseproduct["identifier"] == identifier:
            return suseproduct["id"]
    return None
