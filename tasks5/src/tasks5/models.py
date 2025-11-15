"""Task data model for tasks5.

Contains a small dataclass-like Task with serialization helpers.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import uuid


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Task:
    id: str
    description: str
    created: str
    completed: bool = False
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "created": self.created,
            "completed": self.completed,
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        return cls(
            id=str(data.get("id", "")),
            description=str(data.get("description", "")),
            created=str(data.get("created", utc_now_iso())),
            completed=bool(data.get("completed", False)),
            tags=list(data.get("tags", [])),
        )

    @classmethod
    def create(cls, description: str, tags: Optional[List[str]] = None, id: Optional[str] = None, created: Optional[str] = None) -> "Task":
        if not description or not description.strip():
            raise ValueError("description must be non-empty")
        return cls(
            id=(id if id is not None else uuid.uuid4().hex),
            description=description.strip(),
            created=(created if created is not None else utc_now_iso()),
            completed=False,
            tags=tags or [],
        )
