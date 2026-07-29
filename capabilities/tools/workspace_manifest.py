#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StepSpec:
    name: str
    command: tuple[str, ...]
    allow_nonzero: bool = False


QUICK_CHECK_STEPS = (
    StepSpec("Python syntax", ("{python}", "capabilities/tools/check_python_syntax.py")),
    StepSpec("tool regression tests", ("{python}", "capabilities/tools/test_workspace_tools.py")),
    StepSpec("V2 boundary tests", ("{python}", "capabilities/tools/test_v2_workspace.py")),
    StepSpec("workspace structure", ("{python}", "capabilities/tools/check_workspace.py")),
    StepSpec("git readiness", ("{python}", "capabilities/tools/audit_git_readiness.py")),
    StepSpec("line endings", ("{python}", "capabilities/tools/audit_line_endings.py", "--strict")),
)

FULL_ONLY_STEPS = (
    StepSpec("git candidate summary", ("{python}", "capabilities/tools/summarize_git_candidates.py", "--top", "8")),
    StepSpec("workspace status freshness", ("{python}", "capabilities/tools/verify_workspace_status.py")),
    StepSpec(
        "strict large-file reminder",
        ("{python}", "capabilities/tools/audit_git_readiness.py", "--max-mb", "1"),
        allow_nonzero=True,
    ),
)


CORE_MAINTENANCE_COMMANDS = [
    "python -B capabilities/tools/workspace.py check",
    "python -B capabilities/tools/workspace.py check --full",
    "python -B capabilities/tools/workspace.py update-status",
]

TASK_LIFECYCLE_COMMANDS = [
    "python -B capabilities/tools/workspace.py status",
    "python -B capabilities/tools/workspace.py resume my_task",
    "python -B capabilities/tools/workspace.py doctor my_task",
    "python -B capabilities/tools/workspace.py verify my_task",
]

TOOL_DESCRIPTIONS = {
    "capabilities/tools/audit_git_readiness.py": "checks V2 Git candidates for risky files and secret-like content.",
    "capabilities/tools/audit_line_endings.py": "reports line ending drift against `.gitattributes` policy.",
    "capabilities/tools/check_workspace.py": "checks the V2 structure, ignore policy, adapters, and external-root boundary.",
    "capabilities/tools/check_python_syntax.py": "checks maintained Python source without writing bytecode.",
    "capabilities/tools/generate_workspace_status.py": "regenerates the current-state summary.",
    "capabilities/tools/make_task.py": "contains task scaffolding helpers; its CLI honors the external-root access policy.",
    "capabilities/tools/prepare_baseline_report.py": "provides a compatibility entry for the V2 first-commit report.",
    "capabilities/tools/prepare_first_commit_report.py": "writes a bounded V2 first-commit recommendation report.",
    "capabilities/tools/run_workspace_maintenance.py": "runs the full V2 maintenance chain.",
    "capabilities/tools/summarize_git_candidates.py": "summarizes V2 Git candidates.",
    "capabilities/tools/task_lifecycle.py": "parses task state and implements read-only lifecycle views.",
    "capabilities/tools/task_names.py": "validates portable task names.",
    "capabilities/tools/test_v2_workspace.py": "tests path resolution and read-only external-root enforcement.",
    "capabilities/tools/test_workspace_tools.py": "runs focused regression tests for V2 tools.",
    "capabilities/tools/verify_baseline_report.py": "provides a compatibility entry for V2 report verification.",
    "capabilities/tools/verify_first_commit_report.py": "verifies the generated V2 first-commit report.",
    "capabilities/tools/verify_workspace_status.py": "verifies that `WORKSPACE_STATUS.md` is current.",
    "capabilities/tools/workspace_manifest.py": "centralizes V2 tool metadata and maintenance commands.",
    "capabilities/tools/workspace_paths.py": "resolves configured internal and external paths.",
    "capabilities/tools/workspace.py": "provides the unified V2 checks and read-only task views.",
}
