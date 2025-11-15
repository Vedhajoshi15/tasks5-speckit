# Spec-Kit — Implementation Plan

Version: 1.0
Date: 2025-11-14

This implementation plan follows the rules in `.specify/constitution.md` and the project specification in `spec/spec.md`. It breaks the project into phases, defines module layout, CLI structure, storage and error strategies, testing expectations, and guidance to keep development aligned to specs.

## High-level architectural plan

Phases
1. Foundation: repository layout, minimal packaging, config, and CLI entrypoint.
2. Data model & storage: implement task model, JSON storage helpers, atomic write and schema versioning.
3. Core CLI commands (add, list, show): implement command wiring, basic formatting, and tests.
4. Search and advanced filters: implement search logic and tag/field filters.
5. Optional commands: complete, delete, migrations, import/export.
6. Polish: docs, README, AI assistance log, CI/test scripts, linting/formatting.

Phase sequencing rationale
- Phase 1 establishes the project scaffolding so work is testable and runnable.
- Phase 2 isolates storage and model logic so CLI commands remain thin and testable.
- Core commands are prioritized so the system is usable early and integration tests can exercise full flows.
- Search and optional features build on the core storage and command structure.

Success criteria per phase
- Foundation: `speckit --help` runs and exits 0.
- Data: in-memory model serialization round-trips; read/write tests pass for `tasks.json`.
- Core commands: add→list→show integration test green.
- Search: text-based and tag-based queries produce expected results.

## Module organization under `src/`

Top-level package name: `speckit` (or `src/speckit` depending on chosen layout). We'll use `src/` layout recommended for packaging.

Suggested tree (under repository root):

- src/
  - speckit/
    - __init__.py
    - __main__.py        # optional: allow `python -m speckit`
    - cli.py             # CLI wiring and command registration
    - commands/
      - __init__.py
      - add.py
      - list.py
      - search.py
      - show.py
      - delete.py        # optional
      - complete.py      # optional
    - model/
      - __init__.py
      - task.py          # Task dataclass and (de)serialization
      - schema.py        # schema versioning helpers and migration stubs
    - storage/
      - __init__.py
      - storage.py       # read/write tasks.json, locking, atomic writes
    - util/
      - __init__.py
      - time.py          # timestamp helpers
      - ids.py           # id generation utilities
      - format.py        # output formatting for lists and show
    - testsupport/
      - cli_runner.py    # helpers to test CLI (invoke subprocess or call click runner)
- tests/
  - unit/
  - integration/
- spec/
- .specify/

Rationale
- Keep data model separate from storage and CLI code so unit-testing is straightforward.
- Each command in `commands/` should be small: parse args, call model/storage helpers, format output.

## How the CLI will be structured

CLI entry and library
- `cli.py` exposes a function `main(argv: Optional[List[str]] = None) -> int` which parses arguments and dispatches commands. This allows programmatic testing by calling `main()` and also shell usage via `console_scripts` entry or `__main__`.

Argument parsing
- Use `argparse` from the standard library for minimal dependencies. If `click` is chosen, justify in the spec and keep the dependency small.
- Each command should register a subparser (argparse) or a subcommand (click) defined in a command module.

Command modules
- Each command module (e.g., `commands/add.py`) defines:
  - `configure_parser(subparsers)` — to add its args and help text.
  - `run(args, ctx)` — the execution function which does minimal I/O and uses model/storage utilities.

Shared context
- `cli.py` prepares a lightweight context object (or simple dict) containing configuration like data file path, verbosity, and a `Storage` instance.

Example `main` flow (high-level)
- parse global args (`--data-file`, `--debug`)
- create `Storage` (pointing to data file)
- dispatch to selected command `run(args, ctx)`
- handle exceptions and map them to exit codes

## How commands (add, list, search) will be implemented

General rule: commands orchestrate only; business logic lives in model/storage modules.

Add command (`commands/add.py`)
- parse description and flags (`--tags`, `--id`, `--dry-run`, `--created`)
- validate inputs (non-empty description, tag format)
- call `task = Task.create(description=..., tags=..., id=...)` (task model helper)
- if `--dry-run`: format and print the created task without persisting
- else: `storage.add_task(task)` which reads file, appends, and writes atomically
- print confirmation and exit 0

List command (`commands/list.py`)
- parse filters (`--tag`, `--completed`, `--sort`, `--limit`)
- `tasks = storage.load_tasks()` then filter/sort in-memory using utility functions
- format tasks using `util.format.list_tasks(tasks, options)` and print
- support `--json` to dump matching tasks as JSON

Search command (`commands/search.py`)
- parse search expression and flags (`--ignore-case`, `--field`)
- `tasks = storage.load_tasks()` then apply search predicate (string containment, token match)
- for matches, produce context snippets or highlighted text (optional)
- output via same formatting helpers as list

Show command (`commands/show.py`)
- parse id argument
- `task = storage.get_task_by_id(id)` — if not found, raise `TaskNotFound` handled by CLI wrapper
- print pretty-printed details or JSON when `--json` is set

Implementation details
- Use exceptions for error cases inside model/storage (e.g., `TaskNotFound`, `StorageError`) and let `cli.py` map them to exit codes and user messages.
- Keep commands small (<= ~100 lines) and move any reusable logic to `util/`.

## How JSON storage will be implemented

Storage responsibilities (`src/speckit/storage/storage.py`)
- Provide a `Storage` class with methods:
  - `load() -> List[Task]` — reads and returns tasks
  - `save(tasks: List[Task]) -> None` — writes tasks atomically
  - `add_task(task: Task) -> None` — convenience wrapper
  - `get_task(id: str) -> Task | None`
  - `delete_task(id: str) -> bool`
  - `update_task(task: Task) -> None`
- Manage path resolution for default data file (`data/tasks.json` vs `~/.speckit/tasks.json`) based on CLI args or environment.

Atomic write and locking
- Implement atomic write via:
  1. Serialize to a temporary file in the same directory (e.g., `tasks.json.tmp`).
  2. Flush and fsync where possible.
  3. Rename (`os.replace`) to destination path.
- Use a simple file lock (e.g., `portalocker` if allowed) or an advisory lock using `msvcrt` on Windows and `fcntl` on Unix. If no lock library is used, implement a best-effort lock file with retry and clear messaging.

Schema and versioning
- Top-level wrapper in JSON holds `version` and `tasks` as in spec.
- `schema.py` contains constants and migration helpers. If `version` mismatches and migrations are required, `Storage.load()` should raise `SchemaVersionError` or attempt automated migration if a migration function exists.

Error handling for I/O
- Wrap `json.load`/`json.dump` with try/except to convert `JSONDecodeError` or `OSError` into `StorageError` with informative messages.

## Error handling strategy

Error categories and handling
- CLI argument errors: detected by argparse/click; print usage/help and exit non-zero.
- User errors (e.g., task not found): raise domain exceptions (`TaskNotFound`) and in `cli.py` catch them and print a clear message and exit with a specific non-zero status (e.g., 2).
- Storage errors (I/O, permission, corrupt JSON): raise `StorageError`, print actionable message explaining the file path and options (`--recover`, `--init`), and exit with a different non-zero status (e.g., 3).
- Unexpected errors/bugs: in `--debug` mode print full traceback; otherwise print a short message and exit with a generic error code.

Exit code mapping (suggested)
- 0 — success
- 1 — general error / unhandled
- 2 — user/domain error (invalid id, validation)
- 3 — storage / I/O error
- 4 — argument parsing / usage error

Logging
- Minimal by default. Use `--verbose` to enable info logging and `--debug` to show tracebacks. Use `logging` module and configure handlers in `cli.py`.

## Testing plan for each command

Test principles
- Keep unit tests pure and fast — exercise functions/classes in isolation.
- Use temporary directories and a test-specific data file for integration tests.
- Use fixtures to avoid repetition.

Unit tests
- `model/test_task.py`: Task creation, serialization, deserialization, validation of fields, timestamp format.
- `storage/test_storage.py`: atomic write behavior (use tmpdir), correct reading/writing, schema handling, and simulated file corruption handling.
- `util/test_format.py`: formatting output for tables and JSON output correctness.

Integration tests
- `integration/test_add_list_show.py`:
  1. Run `speckit add "Task A" --data-file <tmp>`
  2. Run `speckit list --data-file <tmp>` and assert output contains Task A
  3. Run `speckit show <id>` and assert details match
- `integration/test_search.py`:
  1. Seed multiple tasks
  2. Run `speckit search "keyword"` and assert returned items
- `integration/test_error_handling.py`:
  - Simulate corrupted JSON and assert the CLI reports a helpful error and does not overwrite file by default

Testing harness
- Tests invoke the CLI in one of two ways:
  - Programmatic: call `speckit.cli.main([...])` capturing stdout/stderr via capsys or similar
  - Subprocess: spawn `python -m speckit` or installed console entry using `subprocess.run` for end-to-end behavior
- For `argparse`-based designs, programmatic invocation is easy and fast; for click, use click's CliRunner.

Coverage targets
- Aim for high coverage on model and storage code (> 80%). Keep CLI thin and test behavior via integration tests.

## How data model utilities will be separated from CLI code

Separation rules
- All data structure definitions live in `model/task.py` (dataclass or pydantic-free simple class) including JSON (de)serialization and validation.
- Storage mechanics (file I/O, locking, atomic operations, migrations) live in `storage/storage.py` and call `task.to_dict()` / `Task.from_dict()`.
- Formatting and presentation live in `util/format.py` and are only used by command modules.
- CLI command modules import model/storage/util but never perform low-level JSON or filesystem operations directly.

Benefits
- Easier unit testing of model and storage without parsing CLI args.
- Cleaner responsibilities and simpler code reviews.

## How to maintain spec alignment during implementation

Practical steps
- Create a micro-spec file for each feature under `.specify/specs/`, e.g., `.specify/specs/add-task.spec.md`, with inputs, outputs, and acceptance tests (examples and exit codes). Implement exactly what the spec requires before expanding.
- For each plan item create a small plan under `.specify/plans/` linking to the spec and listing 1–4 commits/tasks.
- Include a test corresponding to each acceptance criterion in the spec. Tests must be green before the feature is considered done.
- In each commit message reference the spec and plan file, and document any AI assistance used in the commit body.
- Keep PRs or commits focused: each commit should implement one small plan item and include test(s) for it.

Review checklist before merging a feature
- Spec exists in `.specify/specs/` and contains acceptance criteria.
- Tests exercising acceptance criteria exist and pass.
- Commit message documents AI usage (if any).
- Lint/format run locally and code is readable.

Automation
- Optionally add a simple `Makefile` or script `scripts/run_tests.sh` that runs the test suite and linting.
- Optionally include a GitHub Actions workflow to run `pytest` on pushes to `main`.

## Small milestones and estimated effort (student-focused)

- Milestone 1 (2–4 hours): Project scaffold + `speckit --help` + basic `Task` dataclass + storage read/write unit tests.
- Milestone 2 (2–4 hours): Implement `add` and `list` commands + integration test add→list.
- Milestone 3 (1–2 hours): Implement `show` and basic `search` + tests.
- Milestone 4 (1–2 hours): Implement optional `complete` and `delete` + tests.
- Milestone 5 (1–2 hours): Documentation, AI log, polish, and CI (optional).

Adjust estimates based on experience; keep commits small and tests incremental.

## Deliverables from implementation

- `src/speckit/` with modules described above
- `.specify/specs/` feature specs and `.specify/plans/` tasks
- `spec/spec.md` and `spec/plan.md`
- `tests/` unit & integration
- `data/tasks.json` example (in tests/fixtures)
- `AI_ASSISTANCE.md` documenting AI usage in drafting files

---

This plan is intentionally concrete and minimal to match the constitution's emphasis on clarity, testability, and spec-driven development. Follow the micro-spec → plan → implement → test loop for each feature to keep the project aligned and reviewable.
