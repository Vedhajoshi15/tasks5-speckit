"""List command for speckit CLI"""
from __future__ import annotations

import argparse
import json
from typing import List

from ..storage import Storage


def configure_parser(subparsers: argparse._SubParsersAction):
    p = subparsers.add_parser("list", help="List tasks")
    p.add_argument("--tag", "-t", help="Filter by tag", default=None)
    p.add_argument("--completed", action="store_true", help="Show only completed tasks")
    p.add_argument("--incomplete", action="store_true", help="Show only incomplete tasks")
    p.add_argument("--json", action="store_true", help="Output JSON")
    p.set_defaults(func=run)


def _filter_tasks(tasks: List, tag: str | None, completed_only: bool | None):
    out = tasks
    if tag:
        out = [t for t in out if tag in t.tags]
    if completed_only is True:
        out = [t for t in out if t.completed]
    if completed_only is False:
        out = [t for t in out if not t.completed]
    return out


def run(args, ctx) -> int:
    try:
        tasks = ctx.storage.load()
    except Exception as exc:
        print(f"Could not load tasks: {exc}")
        return 3

    completed_only = None
    if getattr(args, "completed", False):
        completed_only = True
    if getattr(args, "incomplete", False):
        completed_only = False

    tasks = _filter_tasks(tasks, getattr(args, "tag", None), completed_only)

    if getattr(args, "json", False):
        print(json.dumps([t.to_dict() for t in tasks], ensure_ascii=False, indent=2))
        return 0

    # Simple table-like print
    print("ID  CREATED               C  DESCRIPTION")
    for t in tasks:
        created_short = t.created.split("T")[0]
        flag = "✓" if t.completed else " "
        print(f"{t.id[:8]}  {created_short}    {flag}  {t.description}")

    return 0
