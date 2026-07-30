# Local Data Boundaries Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep concrete projects, runtime state, artifacts, and archives local while strengthening project scaffold safety and aligning Python compatibility checks.

**Architecture:** Git ignore rules establish the default local-data boundary, while `check_workspace.py` verifies both required ignore patterns and the tracked-file allowlist. Project creation uses a shared target-validation function so dry runs and real creation reject the same collisions. Documentation and CI describe and verify the same Python support matrix.

**Tech Stack:** Python 3.10+ standard library, `unittest`, Git, GitHub Actions YAML, Markdown.

## Global Constraints

- The root remote repository contains workspace architecture and contract README files only.
- Concrete content below `projects/`, `runtime/`, and `storage/` remains local.
- The external source workspace remains read-only.
- No dependency installation is required.
- Tests that create temporary files must write only below `runtime/tmp/`.
- The archived `expense-insight-cli` project must never become a Git candidate.

---

### Task 1: Enforce local storage boundaries

**Files:**
- Modify: `.gitignore`
- Modify: `capabilities/tools/check_workspace.py`
- Modify: `capabilities/tools/test_workspace_tools.py`
- Modify: `projects/README.md`
- Modify: `storage/artifacts/README.md`
- Modify: `storage/archives/README.md`

**Interfaces:**
- Consumes: `check_workspace.check_workspace(root: Path) -> list[str]`
- Produces: tracked-file allowlists for projects, runtime, artifacts, and archives.

- [ ] **Step 1: Write failing tracked-storage tests**

Add tests that patch `git_tracked_files()` with
`storage/artifacts/report.json` and
`storage/archives/projects/example/src/app.py`, then assert that both paths are
reported as local storage content that must not be tracked.

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```powershell
python -B -m unittest capabilities.tools.test_workspace_tools.ScaffoldTests.test_workspace_check_rejects_tracked_artifact_content capabilities.tools.test_workspace_tools.ScaffoldTests.test_workspace_check_rejects_tracked_archive_content -v
```

Expected: both tests fail because the structure check does not yet reject those
tracked paths.

- [ ] **Step 3: Add ignore rules and tracked-file checks**

Add these contracts to `.gitignore`, preserving the existing README files:

```gitignore
storage/artifacts/**
storage/archives/**
!storage/artifacts/README.md
!storage/archives/README.md
```

Extend `REQUIRED_IGNORE_PATTERNS` and reject tracked content below both storage
roots except their exact README allowlist entries.

- [ ] **Step 4: Clarify directory contract documentation**

State in the three contract README files that concrete content is local-only
and that the root remote tracks only the contract README.

- [ ] **Step 5: Run focused tests and verify GREEN**

Run:

```powershell
python -B -m unittest capabilities.tools.test_workspace_tools.ScaffoldTests.test_workspace_check_rejects_tracked_project_content capabilities.tools.test_workspace_tools.ScaffoldTests.test_workspace_check_rejects_tracked_artifact_content capabilities.tools.test_workspace_tools.ScaffoldTests.test_workspace_check_rejects_tracked_archive_content -v
```

Expected: all three tests pass.

### Task 2: Make project creation collision-safe

**Files:**
- Modify: `capabilities/tools/make_project.py`
- Modify: `capabilities/tools/workspace.py`
- Modify: `capabilities/tools/test_workspace_tools.py`

**Interfaces:**
- Produces: `validate_project_target(projects_root: Path, project_name: str) -> Path`
- Consumes: `scaffold_project(projects_root: Path, project_name: str) -> tuple[list[str], list[str]]`

- [ ] **Step 1: Write failing collision tests**

Add tests proving:

- an exact existing project directory raises `ValueError`;
- a case-insensitive equivalent directory raises `ValueError`;
- `run_project_new(..., dry_run=True)` rejects an existing target;
- failed collision validation creates or changes no files.

- [ ] **Step 2: Run focused collision tests and verify RED**

Run the four new test methods with `python -B -m unittest ... -v`.

Expected: exact-name and dry-run tests fail because current code silently
accepts an existing exact-name directory and dry-run checks only name syntax.

- [ ] **Step 3: Implement shared validation**

Implement `validate_project_target()` in `make_project.py` to:

1. validate portable names;
2. resolve and enforce containment below `projects_root`;
3. scan immediate child directories for case-insensitive matches;
4. reject both exact and case-only collisions;
5. return the validated absent target path.

Call it from both dry-run entry points and from `scaffold_project()` before any
directory creation. Remove duplicated validation logic from `workspace.py`.

- [ ] **Step 4: Run focused collision tests and verify GREEN**

Run the same four test methods.

Expected: all pass with no files created for rejected targets.

### Task 3: Align Python compatibility documentation and CI

**Files:**
- Modify: `.github/workflows/workspace-check.yml`
- Modify: `docs/environments/base_python.md`
- Modify: `capabilities/tools/test_workspace_tools.py`

**Interfaces:**
- Produces: GitHub Actions matrix covering Python `"3.10"`, `"3.11"`, and `"3.12"` on Ubuntu and Windows.

- [ ] **Step 1: Write a failing workflow contract test**

Add a test that reads the workflow and asserts that the Python matrix contains
the three quoted versions and that `setup-python` uses
`${{ matrix.python-version }}`.

- [ ] **Step 2: Run the focused test and verify RED**

Run the new test with `python -B -m unittest ... -v`.

Expected: failure because the workflow currently hard-codes Python 3.12.

- [ ] **Step 3: Implement the CI matrix and update documentation**

Add `python-version` to the workflow matrix and reference it from
`actions/setup-python`. Update `base_python.md` to state that 3.10, 3.11, and
3.12 are checked on Ubuntu and Windows.

- [ ] **Step 4: Run the focused test and verify GREEN**

Run the same test.

Expected: pass.

### Task 4: Archive the test project locally

**Files:**
- Move locally: `projects/expense-insight-cli/`
- To local ignored path: `storage/archives/projects/expense-insight-cli/`

**Interfaces:**
- Produces: a complete local archive with the original project absent from the active-project area.

- [ ] **Step 1: Verify exact source and destination paths**

Resolve both absolute paths, confirm the source is inside `projects/`, confirm
the destination is inside `storage/archives/projects/`, and confirm the
destination does not exist.

- [ ] **Step 2: Move the directory with native PowerShell**

Use `Move-Item -LiteralPath` after the resolved-path checks. Preserve the full
project tree, including generated local records.

- [ ] **Step 3: Verify the archive remains ignored**

Run:

```powershell
git check-ignore -v storage/archives/projects/expense-insight-cli/AGENTS.md
git status --short --ignored projects storage/archives/projects
```

Expected: the archived project is ignored and no project content appears as an
untracked Git candidate.

### Task 5: Update framework documentation and generated status

**Files:**
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `WORKSPACE_GUIDE.md`
- Modify: `WORKSPACE_STATUS.md`
- Modify: `capabilities/tools/generate_workspace_status.py`
- Modify: `capabilities/tools/workspace_manifest.py`
- Modify: `.workspace/config.json`

**Interfaces:**
- Produces: one consistent policy: remote Git tracks architecture and directory contracts, never concrete local data.

- [ ] **Step 1: Update permanent rules and user documentation**

Document active projects at `projects/<name>/`, local archives at
`storage/archives/projects/<name>/`, and the no-concrete-content remote policy
for projects, runtime, and storage. Define simple work as requiring only a short
conversational plan, focused verification, one self-review, and a concise
report, without formal planning files or repeated human approval gates unless
safety or material product decisions require them.

- [ ] **Step 2: Add the local archive path to configuration**

Add `"project_archives": "storage/archives/projects"` to the `paths` mapping so
tools and future lifecycle commands do not scatter the relative path.

- [ ] **Step 3: Regenerate workspace status**

Run:

```powershell
python -B capabilities/tools/workspace.py update-status
```

Expected: `WORKSPACE_STATUS.md` matches the generator and documents local data
boundaries.

- [ ] **Step 4: Check documentation consistency**

Search tracked documentation for statements implying concrete project,
runtime, artifact, or archive content is pushed by the root repository and
correct any contradiction.

### Task 6: Verify, review, commit, and publish

**Files:**
- Review: all intended framework changes
- Exclude: `storage/archives/projects/expense-insight-cli/**`

**Interfaces:**
- Produces: verified commits on `codex/local-data-boundaries` and a draft pull request against `main`.

- [ ] **Step 1: Run full verification**

Run:

```powershell
python -B capabilities/tools/workspace.py check --full
```

Expected: all syntax checks, 48 existing tests plus new regression tests,
structure checks, audits, line-ending checks, candidate summaries, and status
freshness checks pass.

- [ ] **Step 2: Review Git scope**

Run `git status -sb`, `git diff --check`, inspect the complete diff, and confirm
that no path below the archived project appears in Git candidates.

- [ ] **Step 3: Commit intended framework changes**

Stage explicit framework paths only and commit with:

```text
Keep workspace data local
```

- [ ] **Step 4: Push the branch**

Run:

```powershell
git push -u origin codex/local-data-boundaries
```

- [ ] **Step 5: Open a draft pull request**

Create a draft PR against `main` describing the local-data boundary, scaffold
collision fix, CI matrix, archived local test project, and verification
evidence.
