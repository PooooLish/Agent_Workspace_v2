#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from workspace_paths import workspace_root


LF_SUFFIXES = {
    ".css",
    ".csv",
    ".example",
    ".html",
    ".js",
    ".json",
    ".jsonl",
    ".md",
    ".py",
    ".sh",
    ".ts",
    ".vue",
    ".yaml",
    ".yml",
}

CRLF_SUFFIXES = {
    ".bat",
    ".cmd",
    ".ps1",
}

LF_NAMES = {
    ".gitattributes",
    ".gitignore",
    "AGENTS.md",
    "README",
}


def git_candidate_paths(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git ls-files failed")
    return [path for path in result.stdout.split("\0") if path]


def expected_line_ending(relative_path: str) -> str | None:
    path = Path(relative_path)
    suffix = path.suffix.lower()
    if suffix in CRLF_SUFFIXES:
        return "crlf"
    if suffix in LF_SUFFIXES or path.name in LF_NAMES:
        return "lf"
    return None


def audit_line_endings(root: Path) -> tuple[list[str], list[str]]:
    lf_policy_with_crlf: list[str] = []
    crlf_policy_without_crlf: list[str] = []

    for relative_path in git_candidate_paths(root):
        expected = expected_line_ending(relative_path)
        if expected is None:
            continue

        path = root / relative_path
        if not path.is_file():
            continue

        data = path.read_bytes()
        has_crlf = b"\r\n" in data
        if expected == "lf" and has_crlf:
            lf_policy_with_crlf.append(relative_path)
        elif expected == "crlf" and data and not has_crlf:
            crlf_policy_without_crlf.append(relative_path)

    return lf_policy_with_crlf, crlf_policy_without_crlf


def normalize_line_endings(root: Path, lf_paths: list[str], crlf_paths: list[str]) -> int:
    changed = 0

    for relative_path in lf_paths:
        path = root / relative_path
        data = path.read_bytes()
        normalized = data.replace(b"\r\n", b"\n")
        if normalized != data:
            path.write_bytes(normalized)
            changed += 1

    for relative_path in crlf_paths:
        path = root / relative_path
        data = path.read_bytes()
        text = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        normalized = text.replace(b"\n", b"\r\n")
        if normalized != data:
            path.write_bytes(normalized)
            changed += 1

    return changed


def print_examples(title: str, paths: list[str], limit: int) -> None:
    print(f"{title}: {len(paths)}")
    for path in paths[:limit]:
        print(f"  ! {path}")
    if len(paths) > limit:
        print(f"  ... {len(paths) - limit} more")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Git candidate line endings against .gitattributes policy.")
    parser.add_argument("--strict", action="store_true", help="Return nonzero when drift is found.")
    parser.add_argument("--fix", action="store_true", help="Rewrite drifted candidate files to their expected line endings.")
    parser.add_argument("--examples", type=int, default=12, help="Maximum example paths to print per category.")
    args = parser.parse_args()

    root = workspace_root()
    lf_policy_with_crlf, crlf_policy_without_crlf = audit_line_endings(root)

    if args.fix:
        changed = normalize_line_endings(root, lf_policy_with_crlf, crlf_policy_without_crlf)
        print(f"Normalized line endings in {changed} file(s).")
        lf_policy_with_crlf, crlf_policy_without_crlf = audit_line_endings(root)

    print_examples("LF-policy candidate files containing CRLF", lf_policy_with_crlf, args.examples)
    print_examples("CRLF-policy candidate files without CRLF", crlf_policy_without_crlf, args.examples)

    drift_count = len(lf_policy_with_crlf) + len(crlf_policy_without_crlf)
    print(f"Summary: {drift_count} line ending drift reminder(s).")
    if args.strict and drift_count:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
