# Spec-Kit — Project Specification

Version: 1.0
Date: 2025-11-14

## Project purpose and goals

Purpose
- Build a small, reliable, and well-tested command-line (terminal) task manager for the CSC299 assignment.

Goals
- Provide a minimal, easy-to-use CLI for creating and managing tasks.
- Persist tasks in a human-readable structured file (JSON) so the data survives across runs.
- Follow Spec-Driven Development (constitution → specification → plan → tasks → implementation → revision).
- Produce high-quality tests, documentation, and clear commit history.
- Maintain a simple, readable codebase in Python that is easy to extend.

Constraints (from the constitution)
- Terminal-only interface (no web frameworks or GUIs).
- Implemented in Python (3.9+ or course-required version).
- Tasks stored in a JSON file or similar structured format.
- Favor clarity, consistency, and robust error handling.

## High-level CLI description

The CLI exposes a small set of commands for core task management operations. Commands must be intuitive, have consistent flags, and print clear outputs. Commands should return appropriate exit codes (0 = success, non-zero = error).

Top-level CLI invocation (example)

speckit [command] [options]

The CLI should support short `-h`/`--help` output for global and per-command usage.

## Supported commands (required and optional)

Required commands (must implement):
- add — add a new task
- list — list tasks
- search — search tasks
- show — display details for a specific task (recommended; considered part of core display behavior)

Optional but recommended commands:
- delete — remove a task by id
- complete — mark a task as completed

Each command should have a consistent set of flags for filtering and formatting (see below).

## Data model for a task

A task is a JSON object with the following fields:

- id (string) — a stable, unique identifier. Prefer short UUID or incrementing integer stored as string; must be unique across the task file.
- description (string) — the main text of the task (short summary). Required.
- created (ISO 8601 timestamp string) — creation time in UTC, e.g., `2025-11-14T13:45:00Z`.
- completed (boolean) — whether the task is completed (default: false).
- tags (array of strings, optional) — short tags to categorize tasks, e.g., `["home","urgent"]`.

Example task JSON

{
  "id": "1",
  "description": "Write project specification",
  "created": "2025-11-14T13:45:00Z",
  "completed": false,
  "tags": ["course","spec"]
}

## Storage requirements (JSON file structure)

- Use a single file to persist task data, e.g., `data/tasks.json` (project-local) or `~/.speckit/tasks.json` (per-user) — choose a default and document it in the spec for each feature.
- File format: top-level JSON object containing metadata and an array of tasks.

Example `tasks.json` structure

{
  "version": "1.0",
  "updated": "2025-11-14T13:50:00Z",
  "tasks": [
    { /* task objects as defined above */ }
  ]
}

Storage semantics and safety
- Writes must be atomic: write to a temporary file and rename/replace the original to reduce corruption risk.
- Handle robustly the case of an invalid JSON file (report a clear error and offer recovery options such as `--init` or `--recover`).
- Keep the JSON format stable; when changing schema, include migrations in the spec and implement helper scripts.

## Command input formats and example usage

1) Add task

Description: Add a new task with a description and optional tags.

Usage examples:

- Positional description
  speckit add "Buy groceries"

- With tags
  speckit add "Finish lab report" --tags school,urgent

- With explicit id (only for advanced/restore use)
  speckit add --id 42 "Restore previous task"

Flags
- `--tags` or `-t` (comma-separated list)
- `--id` (optional, for imports or deterministic ids — otherwise auto-generate)
- `--created` (optional timestamp override; normally automated)
- `--dry-run` (show what would be created without persisting)

Exit codes
- 0 on success
- non-zero on invalid input or I/O error

2) List tasks

Description: Show a list of tasks, optionally filtered or sorted.

Usage examples:

- All tasks
  speckit list

- Only incomplete tasks
  speckit list --filter "completed=false"

- Show tasks with a tag
  speckit list --tag urgent

- Sort by date
  speckit list --sort created

Flags
- `--tag` / `-t` to filter by tag (multiple allowed)
- `--completed` / `--incomplete` to filter by completion state
- `--sort` to control ordering (created, description, id)
- `--limit` to show at most N items

3) Search tasks

Description: Perform a text search against task descriptions and tags.

Usage examples:

- Simple search
  speckit search "report"

- Case-insensitive search
  speckit search --ignore-case "Report"

- Search by field
  speckit search --field tags --value urgent

Flags
- `--ignore-case` for case-insensitive matching
- `--field` to limit search to certain fields (description, tags)

4) Show task details

Description: Display full details for a single task by id.

Usage example:

  speckit show 42

Output: full JSON or pretty-printed human readable format controlled via `--json` flag.

5) Delete task (optional)

Usage example:
  speckit delete 42

Flags: `--yes` to bypass confirmation, `--dry-run` to preview.

6) Complete task (optional)

Usage example:
  speckit complete 42

Flags: `--undo` to un-complete.

## Output formatting rules for listing and searching

- Default `list` output must be a compact, human-readable table/list with columns: id, created (short date), completed indicator, description, tags (comma-separated).
- Use aligned columns or a clear separator (pipe or two spaces) for readability.
- For `search`, highlight matching text if the terminal supports it (optional). Otherwise, include a short context snippet.
- Provide `--json` or `--raw` flags for machine-readable output (dump matching tasks as JSON array).
- For `show`, default to a pretty-printed multi-line human format; `--json` emits raw JSON.

Example list output (compact)

ID  CREATED     C  DESCRIPTION                 TAGS
1   2025-11-14  ×  Write project specification  course,spec
2   2025-11-14     Buy groceries                home

Legend: `C` column uses a check mark or `x` for completed tasks.

## Error handling rules

General principles
- Validate user input early and give clear, actionable messages.
- Return a non-zero exit code for failures.
- Differentiate user errors (invalid args) vs runtime errors (I/O, permission).

Specific rules
- Missing description for `add`: print usage and an error, exit non-zero.
- Invalid flags: show help for the command and exit non-zero.
- Corrupted `tasks.json`: print an error describing the file path, suggest recovery options (e.g., `--recover`), and do not overwrite the file without explicit user confirmation.
- Concurrent write conflicts: obtain a file lock if possible; if lock acquisition fails, retry a small number of times then report an error.
- Unrecognized task id (for `show`, `delete`, `complete`): print "Task not found: <id>" and exit with a specific error code.

Logging and debug
- Provide `--verbose` or `--debug` to show internal diagnostics and stack traces; keep default output clean.

## Testing expectations

Testing is mandatory and considered part of the deliverable. Tests should be fast, deterministic, and isolated.

Test suites
- Unit tests: cover parsing, validation, data model functions, and storage helpers (read/write/migration logic).
- Integration tests: exercise CLI end-to-end using subprocess or test harness to run the command and inspect stdout, stderr, exit code, and file changes.
- Edge-case tests: invalid JSON file, very long descriptions, non-UTF-8 content in files (where applicable), simultaneous writes, and tag parsing.

Test organization
- Place tests under `tests/` with fixtures under `tests/fixtures/`.
- Use temporary directories and files for filesystem tests (do not modify real user data).
- Aim for a small set of integration tests that cover the add→list→show→search flow.

Example tests to include
- Unit: `test_task_model.py` — validate JSON serialization/deserialization and timestamp handling.
- Unit: `test_storage_atomic_write.py` — ensure writes are atomic and produce a valid JSON file.
- Integration: `test_cli_add_list_search.py` — add a task, list to confirm presence, search to confirm match.

Test run
- Provide a short script or instructions in README to run tests, e.g., `python -m pytest`.

## Security and privacy considerations

- Do not execute arbitrary code from task descriptions.
- Store only non-sensitive information; document where the file is stored and how to back it up.
- If an optional import/export feature is added, validate input files before processing.

## Extensibility and versioning

- Keep the schema version in the `tasks.json` top-level object.
- When changing schema, add a migration script and update the spec.
- Avoid coupling the CLI output format to storage schema; provide JSON output for programmatic consumers.

## Non-functional requirements

- Performance: Handle a few thousand tasks efficiently; listing should remain responsive (<200ms for 1000 tasks) on typical student hardware.
- Portability: Support Windows, macOS, and Linux terminals.

## Files and artifacts produced by implementation

- `spec/spec.md` — this specification
- `.specify/constitution.md` — project constitution (already created)
- `.specify/specs/*.md` — per-feature specs (add, list, search, show, delete, complete)
- `src/` or `speckit/` — main Python source package
- `tests/` — unit and integration tests
- `data/tasks.json` — default data file (documented location)
- `AI_ASSISTANCE.md` — optional summary of AI usage

## Acceptance criteria

The project meets its spec when:
- The CLI implements add, list, search, and show (delete/complete optional but recommended).
- Tasks persist in a JSON file and survive restarts.
- A set of unit and integration tests pass locally (`pytest`).
- All code is committed with meaningful messages and any AI assistance documented.

---

End of specification.
