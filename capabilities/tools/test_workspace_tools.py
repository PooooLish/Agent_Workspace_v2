#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import check_workspace
import generate_workspace_status
import make_task
from task_names import validate_task_name
from workspace_manifest import FULL_ONLY_STEPS, QUICK_CHECK_STEPS, TOOL_DESCRIPTIONS
from workspace_paths import load_workspace_config, resolve_external_root, workspace_root


ROOT = workspace_root()
TMP_ROOT = ROOT / "runtime" / "tmp"


class TaskScaffoldTests(unittest.TestCase):
    def test_portable_task_names(self) -> None:
        for name in ("task1", "task_name", "task-name_123"):
            with self.subTest(name=name):
                self.assertIsNone(validate_task_name(name))
        for name in ("", "../escape", "bad/name", "CON", "has space"):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    validate_task_name(name)

    def test_scaffold_writes_only_to_explicit_test_root(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
            root = Path(directory)
            (root / "tasks").mkdir()
            created, skipped = make_task.scaffold_task(root, "example", complexity="simple")
            self.assertFalse(skipped)
            self.assertTrue((root / "tasks" / "example" / "task.md").is_file())
            self.assertFalse((root / "tasks" / "example" / "docs" / "superpowers").exists())
            self.assertIn(str(root / "tasks" / "example" / "summary.md"), created)

    def test_complex_scaffold_has_explicit_coordination_files(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
            root = Path(directory)
            (root / "tasks").mkdir()
            make_task.scaffold_task(root, "example", complexity="complex")
            task = root / "tasks" / "example"
            self.assertTrue((task / "docs" / "superpowers" / "README.md").is_file())
            self.assertTrue((task / "coordination" / "contract.md").is_file())


class V2IntegrationTests(unittest.TestCase):
    def test_workspace_structure_contract(self) -> None:
        self.assertEqual(check_workspace.check_workspace(ROOT), [])

    def test_manifest_uses_only_v2_tool_paths(self) -> None:
        steps = (*QUICK_CHECK_STEPS, *FULL_ONLY_STEPS)
        commands = [part for step in steps for part in step.command]
        self.assertTrue(any("capabilities/tools/" in part for part in commands))
        self.assertFalse(any(part.startswith("tools/") for part in commands))
        self.assertTrue(all(path.startswith("capabilities/tools/") for path in TOOL_DESCRIPTIONS))

    def test_task_cli_rejects_mutation_before_access(self) -> None:
        for arguments in (
            ("new", "must_not_exist"),
            ("verify", "must_not_exist", "--run"),
            ("close", "must_not_exist"),
        ):
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    [sys.executable, "capabilities/tools/workspace.py", *arguments],
                    cwd=ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                self.assertEqual(result.returncode, 1)
                self.assertIn("read-only", result.stdout)

    def test_external_tasks_override_does_not_change_access(self) -> None:
        config = load_workspace_config(ROOT)
        tasks = resolve_external_root(ROOT, config, "tasks")
        self.assertEqual(tasks.access, "read_only")
        self.assertFalse(tasks.path.is_relative_to(ROOT))

    def test_status_generator_is_deterministic(self) -> None:
        first = generate_workspace_status.build_status(ROOT)
        second = generate_workspace_status.build_status(ROOT)
        self.assertEqual(first, second)
        self.assertIn("External tasks access: `read_only`", first)

    def test_codex_adapter_contains_no_legacy_workspace_paths(self) -> None:
        text = (ROOT / ".codex" / "config.toml").read_text(encoding="utf-8")
        for legacy in ("tools/", "prompts/", "sops/", "outputs/", "logs/", "tmp/", "envs/", "archives/"):
            self.assertNotIn(legacy, text)

    def test_no_forbidden_source_assets_were_copied(self) -> None:
        for relative in (
            "tasks",
            "secrets",
            ".superpowers",
            ".worktrees",
            "sandboxes",
            "outputs",
            "logs",
            "tmp",
            ".playwright-cli",
            ".ruff_cache",
        ):
            with self.subTest(relative=relative):
                self.assertFalse((ROOT / relative).exists())


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
