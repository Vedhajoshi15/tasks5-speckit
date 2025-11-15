"""Add command for speckit CLI"""
from __future__ import annotations

import argparse
from typing import Optional

from ..models import Task


def configure_parser(subparsers: argparse._SubParsersAction):
    p = subparsers.add_parser("add", help="Add a new task")
    p.add_argument("description", help="Task description")
    p.add_argument("--tags", "-t", help="Comma-separated tags", default="")
    p.add_argument("--id", help="Optional id for the task", default=None)
    p.add_argument("--dry-run", action="store_true", help="Show task that would be created")
    p.set_defaults(func=run)


def run(args, ctx) -> int:
    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
    try:
        task = Task.create(description=args.description, tags=tags, id=args.id)
    except ValueError as exc:
        print(f"Invalid input: {exc}")
        return 2

    if getattr(args, "dry_run", False):
        print("Dry run — task would be:")
        print(task.to_dict())
        return 0

    try:
        ctx.storage.add_task(task)
    except Exception as exc:
        print(f"Could not save task: {exc}")
        return 3

    print(f"Added task {task.id}: {task.description}")
    return 0
