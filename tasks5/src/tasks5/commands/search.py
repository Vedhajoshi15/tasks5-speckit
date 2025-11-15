"""Search command for speckit CLI"""
from __future__ import annotations

import argparse
import json
from typing import List

from ..models import Task


def configure_parser(subparsers: argparse._SubParsersAction):
    p = subparsers.add_parser("search", help="Search tasks")
    p.add_argument("query", help="Search query")
    p.add_argument("--ignore-case", action="store_true", help="Case-insensitive search")
    p.add_argument("--field", choices=["description", "tags"], default="description", help="Field to search")
    p.add_argument("--json", action="store_true", help="Output JSON")
    p.set_defaults(func=run)


def _matches(task: Task, query: str, field: str, ignore_case: bool) -> bool:
    q = query.lower() if ignore_case else query
    if field == "description":
        hay = task.description.lower() if ignore_case else task.description
        return q in hay
    if field == "tags":
        tags = [t.lower() for t in task.tags] if ignore_case else task.tags
        return q in tags
    return False


def run(args, ctx) -> int:
    try:
        tasks = ctx.storage.load()
    except Exception as exc:
        print(f"Could not load tasks: {exc}")
        return 3

    matches = [t for t in tasks if _matches(t, args.query, args.field, getattr(args, "ignore_case", False))]

    if getattr(args, "json", False):
        print(json.dumps([t.to_dict() for t in matches], ensure_ascii=False, indent=2))
        return 0

    for t in matches:
        print(f"{t.id[:8]}: {t.description}")

    return 0
