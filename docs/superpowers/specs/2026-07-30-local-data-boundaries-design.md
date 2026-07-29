# Local Data Boundaries Design

## Goal

Keep the remote repository limited to the Agent Workspace V2 architecture.
Concrete projects, generated runtime state, durable artifacts, and local
archives remain local even when they are active, completed, archived, or
abandoned.

## Repository Boundary

The root repository tracks directory contracts but not directory contents:

- `projects/README.md` defines the active-project area.
- `runtime/*/README.md` defines regenerable runtime areas.
- `storage/artifacts/README.md` and `storage/archives/README.md` define durable
  local storage areas.
- Concrete content below `projects/`, `runtime/`, and `storage/` is ignored.

Workspace policy, documentation, adapters, reusable capabilities, checks, and
the contract README files remain eligible for the remote repository.

## Local Project Lifecycle

Active projects live at `projects/<project-name>/`. Archived or abandoned
projects live at `storage/archives/projects/<project-name>/`. Moving a project
between these locations changes its local lifecycle state but never makes its
contents a root-repository Git candidate.

The existing `expense-insight-cli` test project will be moved intact from
`projects/expense-insight-cli/` to
`storage/archives/projects/expense-insight-cli/`. Its source, tests,
documentation, examples, outputs, logs, and temporary review records remain
local and are not staged or pushed.

## Scaffold Safety

`workspace.py project new <name>` creates only a previously absent project
directory. If an exact-name or case-insensitive equivalent directory already
exists, the command fails without adding or changing files.

`--dry-run` performs the same validation and collision checks as the real
command. A successful dry run reports the resolved target and excluded side
effects without creating directories or files.

## Enforcement

The workspace structure check rejects tracked files in:

- `projects/`, except `projects/README.md`;
- `runtime/`, except the documented runtime contract README files;
- `storage/artifacts/`, except `storage/artifacts/README.md`;
- `storage/archives/`, except `storage/archives/README.md`.

The check also requires matching ignore rules so an accidental `git add` does
not make local content eligible for commit.

## Compatibility Verification

The root tools continue to require Python 3.10 or newer and use only the
standard library. GitHub Actions verifies the full workspace check on Python
3.10, 3.11, and 3.12 on both Ubuntu and Windows.

Regression tests cover exact-name project collisions, case-insensitive
collisions, dry-run collision handling, and rejection of tracked storage
content. Existing workspace and boundary tests remain part of the full check.

## Review Proportionality

Simple, small-scale changes use a short conversational plan, focused
verification, one self-review, and a concise completion report. They do not
require standalone specifications, implementation plans, or repeated human
approval checkpoints unless a safety rule, destructive action, or material
product decision requires explicit approval.

Formal design and review workflows remain appropriate for high-risk,
cross-module, long-running, destructive, publishing, or multi-agent work.

## Publication

Only framework changes and contract documentation are staged. Before pushing,
the complete workspace verification, Git-candidate security audit, line-ending
audit, status freshness check, and final diff review must pass. The branch is
pushed to the configured GitHub remote and opened as a draft pull request
against `main`.
