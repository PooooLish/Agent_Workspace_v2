#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from workspace_paths import workspace_root


DEFAULT_MAX_MB = 5
CONTENT_SCAN_CHUNK_BYTES = 256 * 1024
CONTENT_SCAN_OVERLAP_BYTES = 256

SENSITIVE_NAME_PATTERNS = [
    re.compile(r"(^|[\\/])\.env(\.|$)", re.IGNORECASE),
    re.compile(r"(^|[\\/])id_rsa($|\.)", re.IGNORECASE),
    re.compile(r"(^|[\\/])id_ed25519($|\.)", re.IGNORECASE),
    re.compile(r"\.(pem|p12|pfx|key)$", re.IGNORECASE),
]

SECRET_CONTENT_PATTERNS = [
    ("private_key_marker", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("anthropic_key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("github_token", re.compile(r"\b(?:gh[opusr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("aws_access_key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("generic_secret_assignment", re.compile(r"\b(?P<name>[A-Z0-9_]*(?:API_KEY|TOKEN|SECRET|PASSWORD)[A-Z0-9_]*)\b[ \t]*[:=][ \t]*[\"']?(?P<value>[A-Za-z0-9_./+=-]{16,})", re.IGNORECASE)),
]

PLACEHOLDER_VALUES = {
    "your_key_here",
    "placeholder",
    "changeme",
    "change_me",
    "example",
    "dummy",
    "test",
}

PLACEHOLDER_MARKERS = (
    "your",
    "placeholder",
    "example",
    "changeme",
    "change_me",
    "dummy",
)

COMMON_CODE_VALUE_PREFIXES = (
    "get",
    "tokenizer.",
    "self.",
)

TOKEN_CREDENTIAL_NAMES = {
    "access_token",
    "api_token",
    "auth_token",
    "bearer_token",
    "github_token",
    "refresh_token",
    "session_token",
}


def is_credential_name(name: str) -> bool:
    lower_name = name.lower()
    if "api_key" in lower_name or "password" in lower_name or "secret" in lower_name:
        return True
    if lower_name in TOKEN_CREDENTIAL_NAMES:
        return True
    return name.isupper() and lower_name.endswith("token")


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
        print("Error: git ls-files failed.", file=sys.stderr)
        if result.stderr:
            print(result.stderr.strip(), file=sys.stderr)
        return []

    paths: list[Path] = []
    for raw in result.stdout.split("\0"):
        if not raw:
            continue
        path = root / raw
        if path.is_file():
            paths.append(path)
    return paths


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def is_sensitive_name(relative_path: str) -> bool:
    return any(pattern.search(relative_path) for pattern in SENSITIVE_NAME_PATTERNS)


def is_probably_text(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:4096]
    except OSError:
        return False
    return b"\0" not in chunk


def has_secret_content(path: Path) -> list[str]:
    if not is_probably_text(path):
        return []

    findings: list[str] = []
    try:
        overlap = b""
        with path.open("rb") as handle:
            while chunk := handle.read(CONTENT_SCAN_CHUNK_BYTES):
                combined = overlap + chunk
                text = combined.decode("utf-8", errors="ignore")
                for name, pattern in SECRET_CONTENT_PATTERNS:
                    if name in findings:
                        continue
                    for match in pattern.finditer(text):
                        if name == "generic_secret_assignment":
                            raw_variable_name = match.group("name")
                            value = match.group("value").strip().strip("\"'")
                            lower_value = value.lower()
                            if not is_credential_name(raw_variable_name):
                                continue
                            if lower_value in PLACEHOLDER_VALUES:
                                continue
                            if any(marker in lower_value for marker in PLACEHOLDER_MARKERS):
                                continue
                            if lower_value.startswith(COMMON_CODE_VALUE_PREFIXES):
                                continue
                        findings.append(name)
                        break
                overlap = combined[-CONTENT_SCAN_OVERLAP_BYTES:]
    except OSError:
        return []
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit files that Git would track before staging or committing.")
    parser.add_argument("--max-mb", type=float, default=DEFAULT_MAX_MB, help="Warn when a Git candidate file is larger than this size.")
    args = parser.parse_args()

    root = workspace_root()
    files = candidate_files(root)
    max_bytes = int(args.max_mb * 1024 * 1024)

    large_files: list[tuple[str, float]] = []
    sensitive_names: list[str] = []
    secret_content: list[tuple[str, list[str]]] = []

    for path in files:
        relative_path = rel(path, root)
        size = path.stat().st_size
        if size > max_bytes:
            large_files.append((relative_path, size / (1024 * 1024)))
        if is_sensitive_name(relative_path):
            sensitive_names.append(relative_path)
        patterns = has_secret_content(path)
        if patterns:
            secret_content.append((relative_path, patterns))

    print(f"Git candidate files: {len(files)}")

    print("Large candidate files:")
    for path, size_mb in large_files:
        print(f"  ! {path} ({size_mb:.2f} MB)")

    print("Sensitive-looking candidate names:")
    for path in sensitive_names:
        print(f"  ! {path}")

    print("Secret-like candidate content:")
    for path, patterns in secret_content:
        joined = ", ".join(sorted(set(patterns)))
        print(f"  ! {path} ({joined})")

    if large_files or sensitive_names or secret_content:
        print(
            f"Summary: {len(large_files)} large file(s), "
            f"{len(sensitive_names)} sensitive-looking name(s), "
            f"{len(secret_content)} file(s) with secret-like content."
        )
        return 2

    print("Summary: no large or secret-like Git candidates found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
