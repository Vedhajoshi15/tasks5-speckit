# Spec-Kit — Development Task List

Version: 1.0
Date: 2025-11-14

This document converts the implementation plan into small, actionable development tasks. Each task lists: goal, affected files/modules, inputs/outputs, and acceptance criteria. Follow the Spec-Driven Development loop: create a micro-spec in `.specify/specs/` for each feature before implementing, and add tests for each acceptance criterion.

Format conventions
- Files given relative to repository root.
- `src/speckit/...` is the canonical implementation path.
- Mark tasks as small, testable commits.

----

1) Project scaffold and repo layout
- Goal: Create the project folder structure and basic entrypoint so the project is runnable and tests can run.
- Affects: repository root, `src/`, `tests/`, `spec/`, `.specify/` (existing files remain)
- Files to create:
  - `src/speckit/__init__.py`
  - `src/speckit/cli.py`
  - `src/speckit/__main__.py` (optional)
  - `tests/` directory placeholder
  - `pyproject.toml` or `setup.cfg` minimal (optional)
- Inputs: none (scaffold task)
- Outputs: created files and a `python -m speckit --help` (or `python -c 'import speckit; print(speckit)'`) safe to run.
- Acceptance criteria:
  - Running `python -m speckit -h` prints usage or help text and exits 0 (implement a minimal help string in `cli.py`).
  - `pytest` recognizes the tests directory (even if empty).

2) Micro-spec files for core features
- Goal: Create per-feature spec files that define inputs, outputs, and acceptance tests.
- Affects: `.specify/specs/`
- Files to create:
  - `.specify/specs/add-task.spec.md`
  - `.specify/specs/list-tasks.spec.md`
  - `.specify/specs/search-tasks.spec.md`
  - `.specify/specs/show-task.spec.md` (optional)
- Inputs: specification templates from `spec/spec.md`
- Outputs: specs that will be referenced in commit messages and developer workflow
- Acceptance criteria:
  - Each spec contains: purpose, inputs, outputs, exit codes, and 2 acceptance test examples.

3) Implement Task data model
- Goal: Implement a `Task` dataclass with (de)serialization and validation.
- Affects: `src/speckit/model/task.py`, unit tests in `tests/unit/test_task_model.py`
- Responsibilities:
  - Fields: id (string), description (string), created (ISO timestamp), completed (bool), tags (list[str])
  - Provide `Task.from_dict()` and `Task.to_dict()` methods
  - Provide `Task.create(description, tags=None, id=None, created=None)` convenience factory
- Inputs: dictionaries (from JSON) and constructor args
- Outputs: Task instances, JSON-serializable dicts
- Acceptance criteria:
  - Unit tests validate round-trip: `Task.from_dict(task.to_dict())` yields an equivalent task.
  - Timestamps are output in stable ISO-8601 UTC format.
  - Validation rejects empty descriptions (unit test).

4) Implement ID utility
- Goal: Provide IDs for tasks with deterministic, testable behavior.
- Affects: `src/speckit/util/ids.py`, used by `model/task.py` and tests
- Options: simple incrementing integer persisted by storage, or short uuid4 strings.
- Inputs: optional `id` override
- Outputs: string id
- Acceptance criteria:
  - Generated ids are unique across a session; unit test checks two generated ids are different.

5) Implement timestamp utilities
- Goal: Centralize timestamp creation/parsing to ensure consistent timezone and format.
- Affects: `src/speckit/util/time.py`, `model/task.py` tests
- Inputs: optional created timestamp string; otherwise use now()
- Outputs: ISO 8601 UTC string
- Acceptance criteria:
  - Timestamps parse back via Task.from_dict and preserve ISO format in tests.

6) Implement JSON storage utilities (atomic write + read)
- Goal: Implement safe read/write and a Storage API to manage tasks.
- Affects: `src/speckit/storage/storage.py`, `src/speckit/model/schema.py`, unit tests in `tests/unit/test_storage.py`
- Methods to implement:
  - `Storage.load()` returns list[Task]
  - `Storage.save(tasks)` writes atomically
  - `Storage.add_task(task)` convenience
  - `Storage.get_task_by_id(id)`
  - `Storage.delete_task(id)` (optional)
- Implementation details:
  - Use `os.replace()` to atomically rename temp file to target
  - Use a local temporary file in same directory
  - Best-effort locking: implement simple lockfile with retries. Document limitations.
- Inputs: data file path, list of Task objects
- Outputs: persisted `tasks.json` with top-level keys `version`, `updated`, `tasks`
- Acceptance criteria:
  - Unit tests confirm `load()` after `save()` returns identical tasks.
  - Write is atomic: after saving, file contains valid JSON (test simulating interruption can be limited).
  - `Storage` raises a `StorageError` on invalid JSON with informative message (unit test that writes malformed JSON to the file then calls `load()`).

7) Implement storage schema and migrations stub
- Goal: Add `schema.py` constants (version) and a placeholder for migration functions.
- Affects: `src/speckit/model/schema.py`, storage tests
- Inputs/Outputs: see storage
- Acceptance criteria:
  - `Storage` reads `version` and raises `SchemaVersionError` if unsupported (unit test)

8) Implement CLI command routing and context
- Goal: Wire `cli.py` to parse global args and register subcommands from `commands/`.
- Affects: `src/speckit/cli.py`, `src/speckit/commands/__init__.py`, and command modules placeholders
- Inputs: argv
- Outputs: calls to `commands.<cmd>.run(args, ctx)` and appropriate exit codes
- Acceptance criteria:
  - `speckit -h` shows all registered commands
  - Programmatic call `cli.main(['add', '--help'])` returns usage string and exit code 0

9) Implement `add` command
- Goal: Implement `commands/add.py` to create tasks and persist them.
- Affects: `src/speckit/commands/add.py`, tests `tests/integration/test_add_list_show.py`, unit tests for `add` behavior
- Behavior:
  - Accept description (positional) and flags `--tags/-t`, `--id`, `--dry-run`, `--created`
  - Validate description not empty
  - Create Task and call `storage.add_task()` (unless dry-run)
  - On success print succinct confirmation and exit 0
- Inputs: CLI args; storage context
- Outputs: updated `tasks.json` and stdout confirmation
- Acceptance criteria:
  - Integration test: run `add` then `list` to verify the new task exists
  - `--dry-run` does not modify `tasks.json` and prints the would-be task
  - Invalid input returns non-zero and helpful message

10) Implement `list` command
- Goal: Implement `commands/list.py` to list tasks, apply filters, and format output
- Affects: `src/speckit/commands/list.py`, `src/speckit/util/format.py`, tests under `tests/integration/test_add_list_show.py`
- Behavior:
  - Support flags: `--tag/-t`, `--completed/--incomplete`, `--sort`, `--limit`, `--json`
  - Use `storage.load()` to get current tasks and apply filters/sorting in memory
  - Format output using `util.format` routines
- Inputs: CLI flags
- Outputs: pretty table on stdout or JSON array with `--json`
- Acceptance criteria:
  - Integration test demonstrates `list` shows the tasks previously added
  - `--json` outputs valid JSON matching tasks returned
  - Filters (tag/completed) work as expected in tests

11) Implement `search` command
- Goal: Implement `commands/search.py` to search task descriptions and tags
- Affects: `src/speckit/commands/search.py`, `src/speckit/util/search.py` (or inside commands), tests in `tests/integration/test_search.py`
- Behavior:
  - Support positional search query and flags `--ignore-case`, `--field`
  - Return matching tasks via `util.format` (reuse list formatting), or `--json` for machine output
- Inputs: query string and flags
- Outputs: filtered list of matching tasks
- Acceptance criteria:
  - Integration test seeds tasks and asserts search results are correct
  - Case-insensitive flag works as expected

12) Implement `show` command (optional but recommended)
- Goal: Show full details for a task by id
- Affects: `src/speckit/commands/show.py`, tests `tests/integration/test_show.py`
- Behavior:
  - Accept a single `id` positional argument
  - Print pretty details or `--json`
- Acceptance criteria:
  - Integration test confirms `show <id>` prints expected fields
  - Non-existent id returns `Task not found: <id>` and non-zero exit code

13) Implement `delete` and `complete` commands (optional)
- Goal: Provide task lifecycle commands
- Affects: `src/speckit/commands/delete.py`, `src/speckit/commands/complete.py`, storage methods
- Acceptance criteria:
  - `delete` removes the task from storage; integration test confirms it's gone
  - `complete` toggles the `completed` flag and `list --completed` reflects change

14) Input validation and argument parsing tests
- Goal: Validate CLI argument edge cases and ensure helpful errors
- Affects: tests in `tests/unit/test_cli_args.py`
- Cases to test:
  - Missing description for `add`
  - Bad tag formatting
  - Unknown flag
- Acceptance criteria:
  - Each invalid input returns the appropriate non-zero code and helpful message

15) Error handling behavior and tests
- Goal: Implement and test error mappings (TaskNotFound, StorageError, SchemaVersionError)
- Affects: `src/speckit/errors.py` (create), `cli.py` exception mapping, unit and integration tests
- Acceptance criteria:
  - Simulated storage corruption produces the documented error message and exit code
  - TaskNotFound produces documented message and exit code

16) Unit tests for utilities and formatters
- Goal: Implement unit tests for `util/format.py`, `util/ids.py`, `util/time.py`.
- Affects: `tests/unit/test_format.py`, `tests/unit/test_ids.py`, `tests/unit/test_time.py`
- Acceptance criteria:
  - Formatters produce correct table output and valid JSON output
  - ID utilities are deterministic in tests where overridden
  - Timestamp utilities produce parseable ISO strings

17) Integration testing for end-to-end flows
- Goal: Provide end-to-end tests for the main flows: add → list → show → search → delete/complete
- Affects: `tests/integration/test_add_list_show.py`, `tests/integration/test_search.py`, helper `testsupport/cli_runner.py`
- Inputs: CLI invocations in temporary directories
- Outputs: assertions about stdout, exit codes, and content of `tasks.json`
- Acceptance criteria:
  - All integration tests pass on a clean run

18) Documentation updates and AI usage log
- Goal: Update README with usage examples and produce `AI_ASSISTANCE.md` noting any AI help used to draft files
- Affects: `README.md`, `AI_ASSISTANCE.md`
- Acceptance criteria:
  - README contains quickstart examples for add/list/search
  - `AI_ASSISTANCE.md` lists tools used for drafting the constitution/spec/plan and commit references

19) CI (optional)
- Goal: Add GitHub Actions workflow to run `pytest` on push
- Affects: `.github/workflows/python-tests.yml`
- Acceptance criteria:
  - Workflow runs pytest and passes on the repository once tests are green locally

20) Final polish and cleanup
- Goal: Run formatters, linters, and finalize commit history
- Affects: repo root files, codebase
- Acceptance criteria:
  - Code formatted consistently and linter warnings checked/fixed
  - Each feature commit references its spec and documents AI usage where applicable

----

How to use these tasks
- Pick the smallest task (e.g., Task data model) and implement it, creating a single commit that includes tests for its acceptance criteria.
- Before starting a task, create a short micro-plan file under `.specify/plans/` that lists the 1–3 commits you intend to make for the task.
- After finishing, mark tests green and reference the spec in commit messages. Update `.specify/specs/` if the implementation requires small, approved deviations.

Notes and assumptions
- Uses Python 3.9+ and prefers the standard library (`argparse`, `json`, `os`) to keep dependencies minimal.
- Locking is best-effort for cross-platform; document any limitations.

----

Saved: `spec/tasks.md`
