import os
import tempfile
from types import SimpleNamespace

from tasks5.commands import add as add_cmd
from tasks5.commands import list as list_cmd
from tasks5.models import Task
from tasks5.storage import Storage


def test_add_and_list_command_output(capsys):
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "tasks.json")
        storage = Storage(path)

        args = SimpleNamespace(description="My task", tags="home,urgent", id=None, dry_run=False)
        ctx = SimpleNamespace(storage=storage)
        rc = add_cmd.run(args, ctx)
        assert rc == 0

        # Now list
        args_list = SimpleNamespace(tag=None, completed=False, incomplete=False, json=False)
        ctx = SimpleNamespace(storage=storage)
        rc = list_cmd.run(args_list, ctx)
        captured = capsys.readouterr()
        assert "My task" in captured.out
        assert rc == 0
