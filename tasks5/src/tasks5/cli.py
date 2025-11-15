"""Command-line entrypoint and subcommand routing for tasks5.

This module provides a `main` function that can be invoked from tests or
the console. It uses argparse to register subcommands from the
`tasks5.commands` package.
"""
from __future__ import annotations

import argparse
import sys
from types import SimpleNamespace

from .storage import Storage

def build_parser():
    parser = argparse.ArgumentParser(prog="speckit", description="Speckit CLI - task manager")
    parser.add_argument("--data-file", help="Path to tasks.json file", default="tasks.json")
    parser.add_argument("--debug", action="store_true", help="Show debug output")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Import command modules and let them register their subparsers
    from .commands import add as add_cmd
    from .commands import list as list_cmd
    from .commands import search as search_cmd

    add_cmd.configure_parser(subparsers)
    list_cmd.configure_parser(subparsers)
    search_cmd.configure_parser(subparsers)

    return parser


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    # Build a simple context with storage instance
    ctx = SimpleNamespace()
    ctx.data_file = args.data_file
    ctx.debug = getattr(args, "debug", False)
    ctx.storage = Storage(args.data_file)

    try:
        if args.command == "add":
            from .commands import add as add_cmd

            return add_cmd.run(args, ctx)
        if args.command == "list":
            from .commands import list as list_cmd

            return list_cmd.run(args, ctx)
        if args.command == "search":
            from .commands import search as search_cmd

            return search_cmd.run(args, ctx)

        parser.print_help()
        return 1
    except Exception as exc:  # keep this broad in scaffold; refine later
        if ctx.debug:
            raise
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
