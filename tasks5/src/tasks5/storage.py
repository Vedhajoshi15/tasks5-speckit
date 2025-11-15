"""Simple JSON file storage for tasks.

Provides a minimal Storage class with load/save/add/get methods. Writes are
performed via an atomic replace of a temporary file.
"""
from __future__ import annotations

import json
import os
from typing import List

from .models import Task


class StorageError(Exception):
    pass


class Storage:
    def __init__(self, path: str = "tasks.json") -> None:
        self.path = path

    def _ensure_parent(self) -> None:
        parent = os.path.dirname(os.path.abspath(self.path))
        if parent and not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)

    def load(self) -> List[Task]:
        if not os.path.exists(self.path):
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            raise StorageError(f"invalid JSON in {self.path}: {exc}")
        except OSError as exc:
            raise StorageError(f"could not read {self.path}: {exc}")

        tasks_data = data.get("tasks") if isinstance(data, dict) else None
        if tasks_data is None:
            raise StorageError(f"unexpected file format in {self.path}")

        return [Task.from_dict(t) for t in tasks_data]

    def save(self, tasks: List[Task]) -> None:
        self._ensure_parent()
        data = {
            "version": "1.0",
            "updated": Task.create("_meta_", created=None).created,  # cheap timestamp
            "tasks": [t.to_dict() for t in tasks],
        }

        tmp_path = f"{self.path}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self.path)
        except OSError as exc:
            raise StorageError(f"could not write {self.path}: {exc}")

    def add_task(self, task: Task) -> None:
        tasks = self.load()
        tasks.append(task)
        self.save(tasks)

    def get_task_by_id(self, id: str) -> Task | None:
        tasks = self.load()
        for t in tasks:
            if t.id == id:
                return t
        return None
