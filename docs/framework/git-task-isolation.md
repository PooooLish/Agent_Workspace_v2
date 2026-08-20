# Git And Task Isolation

## Decision

V2 is an independent framework repository. Concrete projects are separate
ownership domains and never become contents of the workspace repository.

## Boundaries

- V2 Git owns `.workspace/`, reusable capabilities, adapters, framework docs,
  runtime README contracts, and durable V2 storage.
- Current concrete tasks and projects live under ignored `projects/<name>/`
  directories and are never owned by V2 Git.
- V2 checks must not stage or recursively scan concrete projects.
- Nested repositories inside concrete project directories are not V2
  submodules and remain outside V2 maintenance.
- Generated runtime data and machine-local credentials remain ignored.

## V2 Publication Gate

Before committing or pushing the V2 framework:

1. Run `python -B capabilities/tools/workspace.py check --full`.
2. Inspect staged files and outgoing commits.
3. Confirm `runtime/` and `.local/` contain no tracked local state beyond
   intended README contracts.
4. Confirm no concrete project, secret, cache, worktree, or local snapshot is in
   the candidate set.
5. Push only after the destination and scope are explicitly confirmed.

## Independent Task Publication

If a current task is deliberately published later, initialize an independent
repository inside its `projects/<name>/` directory only after approval. Review
its complete candidate list, secret scan, local ignore rules, large files, and
destination. Publishing never adds task contents to the V2 repository.
