#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path

import check_workspace
import generate_workspace_status
import make_task
import workspace
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
            tasks_root = Path(directory) / "custom-projects"
            tasks_root.mkdir()
            created, skipped = make_task.scaffold_task(
                tasks_root,
                "example",
                complexity="simple",
            )
            self.assertFalse(skipped)
            self.assertTrue((tasks_root / "example" / "task.md").is_file())
            self.assertFalse((tasks_root / "example" / "docs" / "superpowers").exists())
            self.assertIn(str(tasks_root / "example" / "summary.md"), created)

    def test_complex_scaffold_has_explicit_coordination_files(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
            tasks_root = Path(directory) / "custom-projects"
            tasks_root.mkdir()
            make_task.scaffold_task(tasks_root, "example", complexity="complex")
            task = tasks_root / "example"
            self.assertTrue((task / "docs" / "superpowers" / "README.md").is_file())
            self.assertTrue((task / "coordination" / "contract.md").is_file())


class V2IntegrationTests(unittest.TestCase):
    def test_python_steps_disable_bytecode_writes(self) -> None:
        command = workspace.resolve_command(("{python}", "example.py"))
        self.assertEqual(command, [sys.executable, "-B", "example.py"])

        for document in ("README.md", "WORKSPACE_GUIDE.md"):
            text = (ROOT / document).read_text(encoding="utf-8")
            self.assertNotIn("python -m compileall", text)

    def test_syntax_checker_reports_invalid_python_without_bytecode(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
            target = Path(directory)
            (target / "valid.py").write_text("value = 1\n", encoding="utf-8")
            (target / "invalid.py").write_text("value =\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "capabilities/tools/check_python_syntax.py",
                    str(target),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            bytecode_created = (target / "__pycache__").exists()

        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid.py", result.stdout)
        self.assertFalse(bytecode_created)

    def test_workspace_structure_contract(self) -> None:
        self.assertEqual(check_workspace.check_workspace(ROOT), [])

    def test_ci_checks_windows_and_linux(self) -> None:
        workflow = ROOT / ".github" / "workflows" / "workspace-check.yml"
        text = workflow.read_text(encoding="utf-8")
        self.assertIn("windows-latest", text)
        self.assertIn("ubuntu-latest", text)
        self.assertIn("capabilities/tools/workspace.py check --full", text)

    def test_link_scan_excludes_private_and_runtime_roots(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
            root = Path(directory)
            managed = root / "capabilities" / "tools"
            workflow = root / ".github" / "workflows"
            private = root / ".local" / "secrets"
            runtime = root / "runtime" / "tmp"
            for path in (managed, workflow, private, runtime):
                path.mkdir(parents=True)
                (path / "marker.txt").write_text("marker", encoding="utf-8")

            scanned = {
                path.relative_to(root).as_posix()
                for path in check_workspace.iter_link_candidates(root)
            }

        self.assertIn("capabilities/tools/marker.txt", scanned)
        self.assertIn(".github/workflows/marker.txt", scanned)
        self.assertFalse(any(path.startswith(".local/") for path in scanned))
        self.assertFalse(any(path.startswith("runtime/") for path in scanned))

    def test_windows_reparse_points_are_treated_as_links(self) -> None:
        fake_stat = SimpleNamespace(st_file_attributes=0x400)
        self.assertTrue(
            check_workspace.is_link_or_junction(
                Path("junction"),
                lstat=lambda _: fake_stat,
            )
        )

    def test_manifest_uses_only_v2_tool_paths(self) -> None:
        steps = (*QUICK_CHECK_STEPS, *FULL_ONLY_STEPS)
        commands = [part for step in steps for part in step.command]
        self.assertTrue(any("capabilities/tools/" in part for part in commands))
        self.assertFalse(any(part.startswith("tools/") for part in commands))
        self.assertTrue(all(path.startswith("capabilities/tools/") for path in TOOL_DESCRIPTIONS))

    def test_full_check_verifies_status_without_regenerating_it(self) -> None:
        commands = [part for step in FULL_ONLY_STEPS for part in step.command]
        self.assertIn("capabilities/tools/verify_workspace_status.py", commands)
        self.assertNotIn("capabilities/tools/generate_workspace_status.py", commands)

    def test_task_cli_rejects_mutation_before_access(self) -> None:
        for arguments in (
            ("new", "must_not_exist"),
            ("verify", "must_not_exist", "--run"),
            ("close", "must_not_exist"),
        ):
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    [sys.executable, "-B", "capabilities/tools/workspace.py", *arguments],
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

    def test_missing_external_tasks_root_is_not_a_structure_failure(self) -> None:
        missing = ROOT.parent / "missing-external-tasks-review"
        with patch.dict("os.environ", {"AGENT_TASKS_ROOT": str(missing)}):
            issues = check_workspace.check_workspace(ROOT)
            warnings = check_workspace.workspace_warnings(ROOT)

        self.assertFalse(
            any("external tasks root is unavailable" in issue for issue in issues),
            issues,
        )
        self.assertTrue(
            any("external tasks root is unavailable" in warning for warning in warnings),
            warnings,
        )

    def test_status_generator_is_deterministic(self) -> None:
        with patch.dict("os.environ", {"AGENT_TASKS_ROOT": str(ROOT.parent / "one")}):
            first = generate_workspace_status.build_status(ROOT)
        with patch.dict("os.environ", {"AGENT_TASKS_ROOT": str(ROOT.parent / "two")}):
            second = generate_workspace_status.build_status(ROOT)
        self.assertEqual(first, second)
        self.assertIn("External tasks access: `read_only`", first)
        self.assertNotIn("External tasks available:", first)
        self.assertNotIn("External tasks source:", first)

    def test_workspace_parser_has_explicit_status_update_command(self) -> None:
        args = workspace.build_parser().parse_args(["update-status"])
        self.assertEqual(args.command, "update-status")

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
