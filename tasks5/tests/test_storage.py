import json
import os
import tempfile

from types import SimpleNamespace

from tasks5.models import Task
from tasks5.storage import Storage, StorageError


def test_storage_save_and_load():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "tasks.json")
        s = Storage(path)

        t = Task.create("Test task", tags=["unit"])
        s.save([t])

        loaded = s.load()
        assert len(loaded) == 1
        assert loaded[0].description == "Test task"
        assert loaded[0].tags == ["unit"]


def test_storage_handles_invalid_json():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "tasks.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write("not a json")

        s = Storage(path)
        try:
            s.load()
            assert False, "expected StorageError"
        except StorageError:
            pass
