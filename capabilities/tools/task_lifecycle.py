#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Callable

from task_names import TASK_NAME_RE, validate_task_name

SECTION_RE = re.compile(r"^##[ \t]+(.+?)[ \t]*$", re.MULTILINE)
COMPLEXITIES = ("simple", "standard", "complex")
STATUSES = ("planning", "active", "blocked", "completed", "abandoned")
CONTRACT_STATUSES = ("pending", "in_progress", "blocked", "completed", "not-applicable")
CONTRACT_COLUMNS = (
    "ID",
    "Dependencies",
    "Owner",
    "Worktree",
    "Allowed paths",
    "Verification",
    "Status",
)
PLACEHOLDER_PREFIXES = (
    "describe ",
    "list ",
    "record ",
    "add ",
    "write ",
)


class TaskRecord:
    def __init__(self, root: Path, name: str, sections: dict[str, str]) -> None:
        self.root = root
        self.name = name
        self.sections = sections
        self.status = section_value(sections, "Status")
        self.complexity = section_value(sections, "Complexity") or "standard"
        self.phase = section_value(sections, "Phase") or infer_legacy_phase(self.status)
        self.goal = section_value(sections, "Goal")
        self.constraints = section_value(sections, "Constraints")
        self.decisions = section_value(sections, "Decisions")
        self.progress = section_value(sections, "Progress")
        self.next_action = section_value(sections, "Next action")
        self.blockers = section_value(sections, "Blockers")
        self.verification = section_value(sections, "Verification commands")
        self.verification_commands = extract_commands(self.verification)


CommandRunner = Callable[[str, Path], int]


def parse_sections(text: str) -> dict[str, str]:
    spans = section_spans(text)
    return {
        heading: text[body_start:body_end].strip()
        for heading, (_, body_start, body_end) in spans.items()
    }


def section_spans(text: str) -> dict[str, tuple[int, int, int]]:
    headings: list[tuple[str, int, int]] = []
    in_fence = False
    offset = 0
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            offset += len(line)
            continue
        if not in_fence:
            match = SECTION_RE.fullmatch(line.rstrip("\r\n"))
            if match:
                heading = match.group(1).strip()
                if any(existing == heading for existing, _, _ in headings):
                    raise ValueError(f"duplicate section heading: {heading}")
                headings.append((heading, offset, offset + len(line)))
        offset += len(line)

    spans: dict[str, tuple[int, int, int]] = {}
    for index, (heading, heading_start, body_start) in enumerate(headings):
        body_end = headings[index + 1][1] if index + 1 < len(headings) else len(text)
        spans[heading] = (heading_start, body_start, body_end)
    return spans


def infer_legacy_phase(status: str) -> str:
    if status == "planning":
        return "planning"
    if status in ("completed", "abandoned"):
        return "completed"
    return "implementation"


def section_value(sections: dict[str, str], heading: str) -> str:
    return sections.get(heading, "").strip()


def is_placeholder(value: str) -> bool:
    normalized = value.strip().lower()
    if not normalized:
        return True
    return any(normalized.startswith(prefix) for prefix in PLACEHOLDER_PREFIXES)


def extract_commands(section: str) -> tuple[str, ...]:
    lines = section.splitlines()
    has_fence = any(line.strip().startswith("```") for line in lines)
    in_fence = False
    commands: list[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if not line or line.startswith("#"):
            continue
        if has_fence and not in_fence:
            continue
        if line.startswith(("- ", "* ")):
            line = line[2:].strip()
        if line.startswith("`") and line.endswith("`") and len(line) > 2:
            line = line[1:-1].strip()
        if line and not is_placeholder(line):
            commands.append(line)
    return tuple(commands)


def task_root_for(tasks_root: Path, name: str) -> Path:
    validate_task_name(name)
    tasks_root = tasks_root.resolve()
    task_root = (tasks_root / name).resolve()
    if tasks_root not in task_root.parents:
        raise ValueError("task path must stay inside tasks")
    return task_root


def load_task(tasks_root: Path, name: str) -> TaskRecord:
    task_root = task_root_for(tasks_root, name)
    task_path = task_root / "task.md"
    if not task_path.is_file():
        raise ValueError(f"tasks/{name}/task.md does not exist")
    return TaskRecord(task_root, name, parse_sections(task_path.read_text(encoding="utf-8")))


def discover_task_names(tasks_root: Path) -> list[str]:
    if not tasks_root.is_dir():
        return []
    return sorted(
        path.name
        for path in tasks_root.iterdir()
        if path.is_dir() and TASK_NAME_RE.fullmatch(path.name)
    )


def git_context(task_root: Path) -> tuple[str, str]:
    top_level = run_git(task_root, "rev-parse", "--show-toplevel")
    if not top_level or Path(top_level).resolve() != task_root.resolve():
        return "not initialized", "unavailable"
    branch = run_git(task_root, "branch", "--show-current")
    commit = run_git(task_root, "rev-parse", "--short", "HEAD")
    return branch or "not a Git repository", commit or "unavailable"


def run_git(task_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(task_root), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def build_resume_packet(task: TaskRecord) -> str:
    branch, commit = git_context(task.root)
    fields = (
        ("Goal", task.goal),
        ("Constraints", task.constraints),
        ("Decisions", task.decisions),
        ("Progress", task.progress),
        ("Verification commands", task.verification),
        ("Next action", task.next_action),
        ("Blockers", task.blockers),
    )
    lines = [
        f"# Resume: {task.name}",
        "",
        f"- Status: {task.status or 'unknown'}",
        f"- Complexity: {task.complexity or 'unknown'}",
        f"- Phase: {task.phase or 'unknown'}",
        f"- Git branch: {branch}",
        f"- Git commit: {commit}",
    ]
    for heading, value in fields:
        lines.extend(("", f"## {heading}", "", value or "Not recorded."))
    return "\n".join(lines)


def diagnose_task(task: TaskRecord) -> list[str]:
    findings: list[str] = []
    required = {
        "Status": task.status,
        "Complexity": task.complexity,
        "Phase": task.phase,
        "Goal": task.goal,
        "Acceptance criteria": section_value(task.sections, "Acceptance criteria"),
        "Verification commands": task.verification,
        "Next action": task.next_action,
        "Blockers": task.blockers,
    }
    for heading, value in required.items():
        if is_placeholder(value):
            findings.append(f"{heading} is missing or still contains scaffold text")
    if task.status and task.status not in STATUSES:
        findings.append(f"Status must be one of: {', '.join(STATUSES)}")
    if task.complexity and task.complexity not in COMPLEXITIES:
        findings.append(f"Complexity must be one of: {', '.join(COMPLEXITIES)}")
    if task.verification and not task.verification_commands:
        findings.append("Verification commands does not contain an executable command")
    planning_root = task.root / "docs" / "superpowers"
    contract_path = task.root / "coordination" / "contract.md"
    if task.complexity == "simple" and planning_root.is_dir():
        planning_files = [path for path in planning_root.rglob("*") if path.is_file()]
        if planning_files:
            findings.append("simple task must not contain standalone planning artifacts under docs/superpowers")
    if task.complexity == "complex":
        if not planning_root.is_dir():
            findings.append("complex task is missing docs/superpowers")
        if not contract_path.is_file():
            findings.append("complex task is missing coordination/contract.md")
        else:
            columns = coordination_columns(contract_path.read_text(encoding="utf-8"))
            missing_columns = [column for column in CONTRACT_COLUMNS if column not in columns]
            if missing_columns:
                findings.append(
                    "coordination/contract.md is missing columns: " + ", ".join(missing_columns)
                )
            else:
                findings.extend(
                    coordination_findings(contract_path.read_text(encoding="utf-8"))
                )
    if not (task.root / "summary.md").is_file():
        findings.append("summary.md is missing")
    return findings


def coordination_columns(text: str) -> tuple[str, ...]:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        cells = split_markdown_table_row(line)
        if cells and cells[0] == "ID":
            return cells
    return ()


def coordination_rows(text: str) -> list[dict[str, str]]:
    columns = coordination_columns(text)
    if not columns:
        return []
    rows: list[dict[str, str]] = []
    header_seen = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        cells = split_markdown_table_row(line)
        if cells == columns:
            header_seen = True
            continue
        if not header_seen or len(cells) != len(columns):
            continue
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(dict(zip(columns, cells)))
    return rows


def split_markdown_table_row(line: str) -> tuple[str, ...]:
    content = line.strip()
    if content.startswith("|"):
        content = content[1:]
    if content.endswith("|"):
        content = content[:-1]
    cells: list[str] = []
    current: list[str] = []
    index = 0
    while index < len(content):
        character = content[index]
        if character == "\\" and index + 1 < len(content) and content[index + 1] in ("|", "\\"):
            current.append(content[index + 1])
            index += 2
            continue
        if character == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(character)
        index += 1
    cells.append("".join(current).strip())
    return tuple(cells)


def coordination_row_findings(text: str) -> list[str]:
    columns = coordination_columns(text)
    if not columns:
        return []
    findings: list[str] = []
    header_seen = False
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        cells = split_markdown_table_row(line)
        if cells == columns:
            header_seen = True
            continue
        if not header_seen or all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        if len(cells) != len(columns):
            findings.append(
                f"coordination/contract.md has malformed row at line {line_number}; "
                "escape literal pipes as \\|"
            )
    return findings


def dependency_ids(value: str) -> tuple[str, ...]:
    if value.strip().lower() in ("", "-", "none", "n/a"):
        return ()
    return tuple(part.strip() for part in value.split(",") if part.strip())


def allowed_paths(value: str) -> tuple[str, ...]:
    return tuple(part.strip().replace("\\", "/") for part in value.split(",") if part.strip())


def unsafe_relative_path(value: str) -> bool:
    path = Path(value)
    return (
        path.is_absolute()
        or ".." in path.parts
        or value.startswith(("~", "/", "//"))
        or bool(re.match(r"^[A-Za-z]:/", value))
        or any(character in value for character in "*?[]")
    )


def paths_overlap(first: str, second: str) -> bool:
    def normalize(value: str) -> str:
        parts = [
            part
            for part in value.replace("\\", "/").split("/")
            if part not in ("", ".")
        ]
        return "/".join(parts).casefold()

    left = normalize(first)
    right = normalize(second)
    if not left or not right:
        return True
    return left == right or left.startswith(f"{right}/") or right.startswith(f"{left}/")


def dependency_closure(task_id: str, graph: dict[str, tuple[str, ...]]) -> set[str]:
    seen: set[str] = set()
    pending = list(graph.get(task_id, ()))
    while pending:
        dependency = pending.pop()
        if dependency in seen:
            continue
        seen.add(dependency)
        pending.extend(graph.get(dependency, ()))
    return seen


def coordination_findings(text: str) -> list[str]:
    findings = coordination_row_findings(text)
    rows = coordination_rows(text)
    if not rows:
        findings.append(
            "coordination/contract.md has no work rows; "
            "use an explicit N/A row for single-agent work"
        )
        return findings
    if len(rows) == 1 and rows[0].get("ID", "").upper() == "N/A":
        if rows[0].get("Status") == "not-applicable":
            return findings
        findings.append("coordination N/A row must use Status not-applicable")
        return findings

    ids = [row.get("ID", "") for row in rows]
    known_ids = {task_id for task_id in ids if task_id}
    duplicates = sorted({task_id for task_id in known_ids if ids.count(task_id) > 1})
    for task_id in duplicates:
        findings.append(f"coordination contract has duplicate ID: {task_id}")

    required_values = ("ID", "Owner", "Worktree", "Allowed paths", "Verification", "Status")
    graph: dict[str, tuple[str, ...]] = {}
    first_rows: dict[str, dict[str, str]] = {}
    for row_number, row in enumerate(rows, start=1):
        task_id = row.get("ID", "") or f"row {row_number}"
        for column in required_values:
            if not row.get(column, "").strip():
                findings.append(f"coordination {task_id} has empty {column}")
        dependencies = dependency_ids(row.get("Dependencies", ""))
        if row.get("ID") and row["ID"] not in first_rows:
            first_rows[row["ID"]] = row
            graph[row["ID"]] = dependencies
        for dependency in dependencies:
            if dependency not in known_ids:
                findings.append(f"coordination {task_id} has unknown dependency: {dependency}")
        unsafe = [path for path in allowed_paths(row.get("Allowed paths", "")) if unsafe_relative_path(path)]
        if unsafe:
            findings.append(
                f"coordination {task_id} has unsafe Allowed paths: {', '.join(unsafe)}"
            )
        status = row.get("Status", "")
        if status and status not in CONTRACT_STATUSES:
            findings.append(
                f"coordination {task_id} has invalid Status {status}; "
                f"expected one of: {', '.join(CONTRACT_STATUSES)}"
            )

    for task_id in graph:
        if task_id in dependency_closure(task_id, graph):
            findings.append(f"coordination dependency cycle includes: {task_id}")

    unique_rows = list(first_rows.items())
    for index, (left_id, left_row) in enumerate(unique_rows):
        left_dependencies = dependency_closure(left_id, graph)
        for right_id, right_row in unique_rows[index + 1:]:
            right_dependencies = dependency_closure(right_id, graph)
            if left_id in right_dependencies or right_id in left_dependencies:
                continue
            overlaps = [
                f"{left_path} <> {right_path}"
                for left_path in allowed_paths(left_row.get("Allowed paths", ""))
                for right_path in allowed_paths(right_row.get("Allowed paths", ""))
                if not unsafe_relative_path(left_path)
                and not unsafe_relative_path(right_path)
                and paths_overlap(left_path, right_path)
            ]
            if overlaps:
                findings.append(
                    f"coordination {left_id} and {right_id} have overlapping Allowed paths: "
                    + ", ".join(overlaps)
                )
    return findings


def default_command_runner(command: str, cwd: Path) -> int:
    if os.name == "nt":
        args = ["powershell.exe", "-NoProfile", "-Command", command]
    else:
        args = ["/bin/sh", "-lc", command]
    return subprocess.run(args, cwd=cwd, check=False).returncode


def verify_task(
    task: TaskRecord,
    *,
    run: bool,
    command_runner: CommandRunner = default_command_runner,
) -> int:
    if not task.verification_commands:
        raise ValueError("task has no verification commands")
    print("Verification commands:")
    for command in task.verification_commands:
        print(f"  {command}")
    if not run:
        print("Read-only preview. Add --run to execute inside the task directory.")
        return 0
    print(
        "Warning: --run executes trusted shell commands without sandboxing; "
        "the task directory is only the working directory."
    )
    for command in task.verification_commands:
        print(f"\n==> {command}", flush=True)
        code = command_runner(command, task.root)
        if code != 0:
            print(f"Verification failed with exit {code}.")
            return code
    print("Verification commands completed.")
    return 0


def complete_summary_sections(summary_path: Path) -> list[str]:
    if not summary_path.is_file():
        return []
    sections = parse_sections(summary_path.read_text(encoding="utf-8"))
    required = ("Goal", "Outcome", "Changes", "Verification", "Open issues")
    complete = [
        heading
        for heading in required
        if not is_placeholder(section_value(sections, heading))
    ]
    verification = section_value(sections, "Verification").strip().lower()
    rejected_verification = ("not run", "not verified", "pending", "unknown", "未运行", "未验证")
    if "Verification" in complete and any(
        marker in verification for marker in rejected_verification
    ):
        complete.remove("Verification")
    return complete


def replace_section(text: str, heading: str, value: str) -> str:
    spans = section_spans(text)
    if heading not in spans:
        raise ValueError(f"task.md is missing {heading}")
    _, body_start, body_end = spans[heading]
    prefix = text[:body_start]
    suffix = text[body_end:].lstrip("\r\n")
    return f"{prefix}\n{value}\n\n{suffix}".rstrip() + "\n"


def ensure_section(text: str, heading: str, value: str, *, after: str) -> str:
    spans = section_spans(text)
    if heading in spans:
        return text
    if after not in spans:
        raise ValueError(f"task.md is missing {after}")
    insert_at = spans[after][2]
    prefix = text[:insert_at].rstrip()
    suffix = text[insert_at:].lstrip("\r\n")
    return f"{prefix}\n\n## {heading}\n\n{value}\n\n{suffix}".rstrip() + "\n"


def close_task(task: TaskRecord) -> None:
    findings = diagnose_task(task)
    if findings:
        raise ValueError(f"task lifecycle has unresolved findings: {'; '.join(findings)}")
    if task.complexity == "complex":
        contract_path = task.root / "coordination" / "contract.md"
        unfinished = [
            row.get("ID", "unknown")
            for row in coordination_rows(contract_path.read_text(encoding="utf-8"))
            if row.get("Status") not in ("completed", "not-applicable")
        ]
        if unfinished:
            raise ValueError(f"unfinished coordination rows: {', '.join(unfinished)}")
    summary_path = task.root / "summary.md"
    complete = complete_summary_sections(summary_path)
    required = {"Goal", "Outcome", "Changes", "Verification", "Open issues"}
    missing = sorted(required - set(complete))
    if missing:
        raise ValueError(f"summary.md has incomplete sections: {', '.join(missing)}")
    task_path = task.root / "task.md"
    text = task_path.read_text(encoding="utf-8")
    text = ensure_section(text, "Complexity", task.complexity, after="Status")
    text = ensure_section(text, "Phase", task.phase, after="Complexity")
    text = replace_section(text, "Status", "completed")
    text = replace_section(text, "Phase", "completed")
    text = replace_section(text, "Next action", "None")
    task_path.write_text(text, encoding="utf-8", newline="\n")
