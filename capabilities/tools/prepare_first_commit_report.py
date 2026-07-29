#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from workspace_paths import configured_path, load_workspace_config, workspace_root


CONFIRMED_ASSET_PREFIXES: tuple[str, ...] = ()

REVIEW_SUFFIXES = {
    ".7z", ".avi", ".bin", ".db", ".dll", ".doc", ".docx", ".dylib", ".exe",
    ".gif", ".ico", ".jpeg", ".jpg", ".m4a", ".mov", ".mp3", ".mp4", ".pdf",
    ".png", ".ppt", ".pptx", ".pyc", ".rar", ".so", ".sqlite", ".tar", ".wasm",
    ".webm", ".webp", ".xls", ".xlsx", ".zip",
}

EXCLUDE_NOTES = [
    ("runtime/**", "Generated runtime state is ignored; only directory README files are tracked."),
    (".local/envs/**", "Machine-local environments are ignored."),
    (".local/secrets/**", "Machine-local credentials are ignored."),
    ("*.bak", "Local backup files are ignored; keep canonical docs instead."),
    ("**/node_modules/", "Dependency folders are ignored by policy."),
]

DEFAULT_OUTPUT = "first_commit_recommendation.md"


def resolve_report_output(root: Path, value: str) -> Path:
    output_root = configured_path(root, load_workspace_config(root), "outputs")
    requested = Path(value)
    if requested.is_absolute():
        raise ValueError("output path must be relative to the configured outputs directory")
    resolved = (output_root / requested).resolve()
    if not resolved.is_relative_to(output_root):
        raise ValueError("output path escapes the configured outputs directory")
    return resolved


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def candidate_files(root: Path) -> list[Path]:
    result = run_git(root, ["ls-files", "--cached", "--others", "--exclude-standard", "-z"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git ls-files failed")

    files: list[Path] = []
    for raw in result.stdout.split("\0"):
        if not raw:
            continue
        path = root / raw
        if path.is_file():
            files.append(path)
    return sorted(files)


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def area(relative_path: str) -> str:
    parts = relative_path.split("/")
    if len(parts) == 1:
        return "<root>"
    return parts[0]


def needs_review(relative_path: str) -> bool:
    suffix = Path(relative_path).suffix.lower()
    if suffix in REVIEW_SUFFIXES:
        return True
    return False


def is_confirmed_asset(relative_path: str) -> bool:
    return any(relative_path.startswith(prefix) for prefix in CONFIRMED_ASSET_PREFIXES)


def markdown_list(paths: list[str], limit: int | None = None) -> list[str]:
    selected = paths if limit is None else paths[:limit]
    lines = [f"- `{path}`" for path in selected]
    if limit is not None and len(paths) > limit:
        lines.append(f"- ... {len(paths) - limit} more")
    return lines


def build_report(root: Path, files: list[Path]) -> str:
    recommended: list[str] = []
    review: list[str] = []
    confirmed_assets: list[str] = []

    for path in files:
        relative_path = rel(path, root)
        if needs_review(relative_path):
            review.append(relative_path)
        else:
            recommended.append(relative_path)
        if is_confirmed_asset(relative_path):
            confirmed_assets.append(relative_path)

    by_area: dict[str, list[str]] = defaultdict(list)
    for path in recommended:
        by_area[area(path)].append(path)

    total_size = sum(path.stat().st_size for path in files) / (1024 * 1024)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines: list[str] = [
        "# Workspace Baseline Recommendation",
        "",
        f"Generated: {now}",
        "",
        "## Summary",
        "",
        f"- Git candidate files: {len(files)}",
        f"- Total candidate size: {total_size:.2f} MB",
        f"- Recommended baseline files: {len(recommended)}",
        f"- Needs manual confirmation: {len(review)}",
        f"- Confirmed public/site assets included: {len(confirmed_assets)}",
        "",
        "## Recommended Baseline Files",
        "",
        "These files look like source, rules, docs, prompts, SOPs, templates, or small project files.",
        "",
    ]

    for name in sorted(by_area):
        paths = sorted(by_area[name])
        lines.append(f"### {name}")
        lines.append("")
        lines.extend(markdown_list(paths, limit=80))
        lines.append("")

    lines.extend(
        [
            "## Confirmed Public/Site Assets",
            "",
            "These public assets are recommended for the baseline because current site code references or uses them.",
            "",
        ]
    )
    lines.extend(markdown_list(sorted(confirmed_assets), limit=None) or ["- None"])
    lines.append("")

    lines.extend(
        [
            "## Needs Manual Confirmation",
            "",
            "Review these before staging. They may be legitimate assets, but they are binary, backup, or public media files.",
            "",
        ]
    )
    lines.extend(markdown_list(sorted(review), limit=None) or ["- None"])
    lines.append("")

    lines.extend(
        [
            "## Intentionally Excluded Or Deferred",
            "",
            "These are governed by ignore rules or cleanup notes.",
            "",
        ]
    )
    for pattern, reason in EXCLUDE_NOTES:
        lines.append(f"- `{pattern}`: {reason}")

    lines.extend(
        [
            "",
            "## Suggested Commands",
            "",
            "```powershell",
        "python -B capabilities/tools/check_workspace.py",
        "python -B capabilities/tools/audit_git_readiness.py",
        "python -B capabilities/tools/summarize_git_candidates.py",
            "```",
            "",
            "Stage files only after reviewing this report and confirming no private task content is included.",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Markdown recommendation for the workspace baseline.")
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help="Report path relative to the configured outputs directory.",
    )
    args = parser.parse_args()

    root = workspace_root()
    files = candidate_files(root)
    report = build_report(root, files)

    output_path = resolve_report_output(root, args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8", newline="\n")
    print(f"Wrote {output_path}")
    print(f"Git candidate files: {len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
