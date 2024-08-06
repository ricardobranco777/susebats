#!/usr/bin/env python3
"""
susebats
"""

import argparse
import sys

from cmd.all import main_all
from cmd.jobs import main_jobs
from cmd.list import main_list
from cmd.notok import main_notok
from cmd.versions import main_versions


VERSION = "0.4.0"


def main() -> None:
    """
    Main function
    """

    parser = argparse.ArgumentParser(
        prog="susebats",
        add_help=False,
    )
    parser.add_argument(
        "-h", "--help", action="store_true", help="show this help message and exit"
    )
    parser.add_argument("--version", action="version", version=VERSION)
    subparsers = parser.add_subparsers(dest="command", required=False)

    parser_all = subparsers.add_parser(
        "all",
        help="dump all as json",
        epilog="set GITLAB_TOKEN environment variable for gitlab",
    )
    parser_all.set_defaults(func=main_all)

    parser_jobs = subparsers.add_parser(
        "jobs",
        help="list BATS jobs in o.s.d & o3",
        epilog="set GITLAB_TOKEN environment variable for gitlab",
    )
    parser_jobs.add_argument("-b", "--build", help="-DAYS_AGO or YYYYMMDD")
    parser_jobs.add_argument("-v", "--verbose", action="store_true")
    parser_jobs.set_defaults(func=main_jobs)

    parser_list = subparsers.add_parser(
        "list",
        help="list skipped BATS tests per product",
        epilog="set GITLAB_TOKEN environment variable for gitlab",
    )
    parser_list.set_defaults(func=main_list)

    parser_notok = subparsers.add_parser(
        "notok",
        help="Generate BATS_SKIP variables from an openQA job URL",
    )
    parser_notok.add_argument(
        "-d", "--diff", action="store_true", help="show diff of settings"
    )
    parser_notok.add_argument(
        "-v", "--verbose", action="count", help="may be specified more than once"
    )
    parser_notok.add_argument("url", help="openQA job")
    parser_notok.set_defaults(func=main_notok)

    parser_versions = subparsers.add_parser(
        "versions",
        help="print versions of BATS tested packages in openQA job",
    )
    parser_versions.add_argument("-v", "--verbose", action="store_true")
    parser_versions.add_argument("url", help="openQA job")
    parser_versions.set_defaults(func=main_versions)

    args = parser.parse_args()

    if args.command is None or args.help:
        parser.print_help()
        # Print help for all subcommands
        for cmd in subparsers.choices:
            print()
            subparsers.choices[cmd].print_help()
            print()
        sys.exit(0 if args.help else 1)

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
