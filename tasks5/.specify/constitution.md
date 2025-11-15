# Spec-Kit Constitution

Version: 1.0
Date: 2025-11-14

## Purpose

This constitution defines the principles, constraints, development rules, and workflows for the Spec-Kit CLI tasks manager (CSC299 assignment). It focuses on software development practices for a small, testable, and extensible command-line application written in Python.

## Scope

This document applies to all code, tests, specifications, documentation, and commit history in this repository for the CSC299 tasks manager project. It is intended to guide day-to-day development and ensure reproducible, spec-driven progress.

## Core Principles (non-negotiable)

- The system must be a command-line (terminal) task manager implemented in Python.
- The system must support at minimum: adding tasks, listing tasks, searching tasks, and displaying task details.
- Tasks must be stored persistently using a structured, human-readable format (JSON or equivalent). The storage should be file-based (e.g., a JSON file in the project data directory) and not rely on external services.
- The project follows Spec-Driven Development: constitution → specification → plan → tasks → implementation → revision.
- AI coding assistance (GitHub Copilot, ChatGPT, Claude, etc.) may be used but every use must be documented in commit messages and summarized in repository documentation.
- All code must be committed with clear, meaningful commit messages that describe the intent and scope of the change.
- Tests, documentation, and specification artifacts must be maintained alongside implementation; they are first-class deliverables.
- Keep the system simple, readable, and easy to extend. Prioritize clarity over cleverness.
- No external web frameworks or GUIs — terminal-only user experience.
- UX must favor clarity, consistency, and robust error handling.

## Spec-Driven Development (SDD) Workflow

1. Constitution: This document captures project-level rules and constraints (this file).
2. Specification: For each feature or change, create a small machine- and human-readable specification in `.specify/specs/` (e.g., `add-task.spec.md`) that lists behavior, inputs, outputs, and acceptance criteria.
3. Plan: Convert the specification into a short plan (1–5 tasks) in `.specify/plans/` or the issue tracker. Each plan item should be small and testable.
4. Tasks: Implement each plan item with a commit and an associated test that demonstrates the required behavior.
5. Implementation: Keep implementations minimal to satisfy the spec and tests. Avoid premature optimization.
6. Revision: If tests/specs fail or requirements change, revise the spec, update tests, and iterate.

## Minimal Specification Contract (for each feature)

- Inputs: command-line arguments, environment variables, or interactive prompts.
- Outputs: CLI exit codes, printed output (stdout/stderr), and updates to the persistent JSON data file.
- Error modes: invalid input, file I/O errors, concurrency/locking issues — these must be handled gracefully with clear messages and non-zero exit codes.
- Success criteria: All acceptance tests specified in the feature spec pass.

## Development Rules

- Language: Python 3.9+ (match course requirements). Keep dependency footprint minimal; prefer the standard library where reasonable.
- CLI interface: Use a small CLI library (argparse or click). If using a third-party library, justify it in the spec.
- Storage: Use a single JSON file (or a small set of JSON files) under a data directory (e.g., `~/.speckit/tasks.json` or a project-local `data/` folder for tests). Implement safe write patterns (atomic write or temp file rename) to reduce corruption risk.
- Configuration: Keep defaults simple; allow overrides via environment variables or explicit CLI flags.
- No background services or network calls required for core functionality.

## Coding Practices

- Keep functions and modules small and focused.
- Prefer explicit, readable code over clever idioms.
- Provide docstrings for public functions/classes and a concise README for the project.
- Follow consistent formatting (black/flake8 or project default). If tools are adopted, list them in the repository documentation.

## Commit and Branching Guidelines

- Commit small, focused changes that correspond to a single spec/task.
- Commit messages must be meaningful and follow this pattern: `<area>: <short description>` followed by an optional body describing reasoning and how tests were updated.
- Document any use of AI assistance in the commit body. Example: `AI-assisted: used ChatGPT to generate initial parsing logic; reviewed and adjusted manually.`
- Keep a linear history for the assignment (simple feature branches merging into `main` or direct commits, as instructed by the course staff).

## AI Assistance Policy

- AI tools may be used to generate code, tests, or documentation drafts.
- All AI usage must be explicitly recorded in the corresponding commit message (see above) and summarized periodically in repository documentation (e.g., `AI_ASSISTANCE.md` or a `docs/` entry).
- When accepting AI-generated content, the developer is responsible for verifying correctness, security, and license compliance.
- Never paste or use code from untrusted sources without review. Adopt, adapt, and test — do not blindly accept AI output.

## Testing Guidelines

- Unit tests: Cover core business logic (parsing, task validation, storage operations). Aim for deterministic, fast tests that do not rely on external state.
- Integration tests: Validate CLI behavior using subprocess invocation or a CLI testing harness. Test common user flows: add → list → show → search.
- Edge cases: empty input, invalid JSON file, file locking or concurrent writes, very large task lists, Unicode in task fields.
- Test data: Put small fixtures under `tests/fixtures/` and ensure tests clean up temporary files.
- Continuous verification: Run the test suite locally before committing substantial changes.

## User Experience and Error Handling

- Output should be clear and consistent. Use concise, human-readable messages for normal output and helpful error messages for problems.
- Exit codes: 0 for success; non-zero for errors. Document exit codes in feature specs if non-trivial.
- For commands that modify data, show a concise confirmation, and optionally provide `--dry-run` for risky operations.

## Extensibility and Maintenance

- Keep the core data model (task fields) minimal and versionable. If the schema changes, provide migration helpers or a clear migration plan in the spec.
- Avoid premature abstraction. Refactor when multiple features justify it.
- Keep CLI commands composable and orthogonal.

## Files and Artifacts

- This constitution: `.specify/constitution.md`
- Feature specs: `.specify/specs/*.md`
- Plans: `.specify/plans/*.md`
- Tests: `tests/` (unit and integration)
- Main code: `src/` or top-level `speckit/` package as decided in the project spec
- Data: `data/` (project-local) or documented per-user location (see spec)
- AI usage log (recommended): `AI_ASSISTANCE.md` or `docs/ai-assistance.md`

## Amendment

- Small, non-breaking editorial changes to this document may be made directly and recorded with a clear commit message.
- Substantive changes to principles (e.g., changing storage model or adding network features) must be justified in a spec and recorded as a new constitution version.

---

This constitution is intentionally focused on software development practices for the CSC299 CLI task manager. Follow it to produce small, spec-driven, well-tested, and well-documented changes.
