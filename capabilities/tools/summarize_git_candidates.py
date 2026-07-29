#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from collections import Counter
from pathlib import Path
from workspace_paths import workspace_root


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
    return files


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def top_bucket(relative_path: str) -> str:
    parts = relative_path.split("/")
    if len(parts) == 1:
        return "<root>"
    if parts[0] == "tasks":
        if len(parts) == 2 and parts[1] == "README.md":
            return "tasks"
        return f"tasks/{parts[1]}"
    return parts[0]


def extension(path: Path) -> str:
    suffix = path.suffix.lower()
    return suffix or "<none>"


def print_counter(title: str, counter: Counter[str]) -> None:
    print(f"{title}:")
    for name, count in counter.most_common():
        print(f"  {name}: {count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize files Git would track before staging or committing.")
    parser.add_argument("--top", type=int, default=12, help="Number of largest files to show.")
    args = parser.parse_args()

    root = workspace_root()
    files = candidate_files(root)
    total_bytes = sum(path.stat().st_size for path in files)

    by_bucket: Counter[str] = Counter()
    by_extension: Counter[str] = Counter()
    for path in files:
        relative_path = rel(path, root)
        by_bucket[top_bucket(relative_path)] += 1
        by_extension[extension(path)] += 1

    print(f"Git candidate files: {len(files)}")
    print(f"Total candidate size: {total_bytes / (1024 * 1024):.2f} MB")
    print_counter("Candidates by area", by_bucket)
    print_counter("Candidates by extension", by_extension)

    print("Largest candidates:")
    for path in sorted(files, key=lambda item: item.stat().st_size, reverse=True)[: args.top]:
        print(f"  {rel(path, root)} ({path.stat().st_size / (1024 * 1024):.2f} MB)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
