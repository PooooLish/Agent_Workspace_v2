#!/usr/bin/env python3
from __future__ import annotations

import io
import os
import re
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import audit_git_readiness
import check_python_syntax
import check_workspace
import generate_workspace_status
import make_task
import prepare_first_commit_report
import task_lifecycle
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

    def test_verification_stops_after_the_first_failed_command(self) -> None:
        task = task_lifecycle.TaskRecord(
            ROOT,
            "example",
            {"Verification commands": "first\nsecond\nthird"},
        )
        executed: list[str] = []

        def runner(command: str, cwd: Path) -> int:
            executed.append(command)
            return 7 if command == "second" else 0

        with redirect_stdout(io.StringIO()):
            result = task_lifecycle.verify_task(
                task,
                run=True,
                command_runner=runner,
            )
        self.assertEqual(result, 7)
        self.assertEqual(executed, ["first", "second"])

    def test_command_parser_uses_only_fenced_commands_when_a_fence_exists(self) -> None:
        section = "Do not run this prose\n```powershell\npython -B test.py\n```\n"
        self.assertEqual(
            task_lifecycle.extract_commands(section),
            ("python -B test.py",),
        )

    def test_close_task_updates_only_lifecycle_fields(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
            tasks_root = Path(directory)
            task_root = tasks_root / "example"
            task_root.mkdir()
            (task_root / "task.md").write_text(
                """# Task: example

## Status

active

## Complexity

simple

## Phase

verification

## Goal

Finish the task.

## Acceptance criteria

The result is verified.

## Verification commands

python -B test.py

## Decisions

Keep the change small.

## Progress

Implementation complete.

## Next action

Close the task.

## Blockers

None
""",
                encoding="utf-8",
            )
            (task_root / "summary.md").write_text(
                """# Summary: example

## Goal

Finish the task.

## Outcome

Completed.

## Changes

Updated the implementation.

## Verification

Passed.

## Open issues

None.
""",
                encoding="utf-8",
            )
            task_lifecycle.close_task(task_lifecycle.load_task(tasks_root, "example"))
            sections = task_lifecycle.parse_sections(
                (task_root / "task.md").read_text(encoding="utf-8")
            )

        self.assertEqual(sections["Status"], "completed")
        self.assertEqual(sections["Phase"], "completed")
        self.assertEqual(sections["Next action"], "None")
        self.assertEqual(sections["Goal"], "Finish the task.")

    def test_coordination_flags_independent_overlapping_paths(self) -> None:
        text = """| ID | Dependencies | Owner | Worktree | Allowed paths | Verification | Status |
| --- | --- | --- | --- | --- | --- | --- |
| A | None | one | wt-a | src | test-a | pending |
| B | None | two | wt-b | src/module | test-b | pending |
"""
        findings = task_lifecycle.coordination_findings(text)
        self.assertTrue(any("overlapping Allowed paths" in item for item in findings))


class V2IntegrationTests(unittest.TestCase):
    def test_status_inventory_uses_configured_internal_paths(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
            base = Path(directory)
            skills = base / "skills"
            sops = base / "sops"
            prompts = base / "prompts"
            environments = base / "environments"
            (skills / "configured-skill").mkdir(parents=True)
            (skills / "configured-skill" / "SKILL.md").write_text(
                "---\nname: configured-skill\ndescription: test\n---\n",
                encoding="utf-8",
            )
            for path in (sops, prompts, environments):
                path.mkdir()
                (path / "configured-marker.md").write_text("# Marker\n", encoding="utf-8")

            config = deepcopy(load_workspace_config(ROOT))
            for name, path in (
                ("skills", skills),
                ("sops", sops),
                ("prompts", prompts),
                ("environment_docs", environments),
            ):
                config["paths"][name] = path.relative_to(ROOT).as_posix()

            with patch.object(
                generate_workspace_status,
                "load_workspace_config",
                return_value=config,
            ):
                status = generate_workspace_status.build_status(ROOT)

        self.assertIn("configured-skill", status)
        self.assertEqual(status.count("configured-marker.md"), 3)

    def test_syntax_checker_uses_configured_tools_path_by_default(self) -> None:
        config = deepcopy(load_workspace_config(ROOT))
        config["paths"]["tools"] = "runtime/tmp/configured-tools"
        self.assertEqual(
            check_python_syntax.default_targets(ROOT, config),
            [ROOT / "runtime" / "tmp" / "configured-tools"],
        )

    def test_first_commit_report_output_stays_in_configured_outputs(self) -> None:
        expected = ROOT / "runtime" / "outputs" / "report.md"
        self.assertEqual(
            prepare_first_commit_report.resolve_report_output(ROOT, "report.md"),
            expected,
        )
        for unsafe in ("../outside.md", str(ROOT.parent / "outside.md")):
            with self.subTest(unsafe=unsafe):
                with self.assertRaisesRegex(ValueError, "output path"):
                    prepare_first_commit_report.resolve_report_output(ROOT, unsafe)

    def test_git_readiness_fails_when_git_candidate_enumeration_fails(self) -> None:
        failure = SimpleNamespace(returncode=128, stderr="fatal: probe", stdout="")
        with patch.object(audit_git_readiness, "run_git", return_value=failure):
            with self.assertRaisesRegex(RuntimeError, "git ls-files failed"):
                audit_git_readiness.candidate_files(ROOT)

    def test_git_readiness_fails_when_candidate_content_cannot_be_read(self) -> None:
        candidate = ROOT / "unreadable-candidate.txt"
        with (
            patch.object(audit_git_readiness, "is_probably_text", return_value=True),
            patch.object(Path, "open", side_effect=OSError("access denied")),
        ):
            with self.assertRaisesRegex(RuntimeError, "cannot scan Git candidate"):
                audit_git_readiness.has_secret_content(candidate)

    def test_workspace_check_fails_when_tracked_files_cannot_be_enumerated(self) -> None:
        failure = SimpleNamespace(returncode=128, stderr="fatal: probe", stdout="")
        with patch.object(check_workspace.subprocess, "run", return_value=failure):
            with self.assertRaisesRegex(RuntimeError, "git ls-files failed"):
                check_workspace.git_tracked_files(ROOT)

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

    def test_workspace_check_validates_skill_metadata(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
            skills = Path(directory) / "skills"
            skill = skills / "Bad_Name"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: different-name\n---\n",
                encoding="utf-8",
            )
            config = deepcopy(load_workspace_config(ROOT))
            config["paths"]["skills"] = skills.relative_to(ROOT).as_posix()
            with (
                patch.object(check_workspace, "load_workspace_config", return_value=config),
                patch.object(check_workspace, "git_tracked_files", return_value=[]),
            ):
                issues = check_workspace.check_workspace(ROOT)

        self.assertTrue(any("kebab-case" in issue for issue in issues))
        self.assertTrue(any("name does not match" in issue for issue in issues))
        self.assertTrue(any("missing description" in issue for issue in issues))

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

    def test_every_python_tool_is_registered(self) -> None:
        tool_files = {
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "capabilities" / "tools").glob("*.py")
        }
        self.assertEqual(set(TOOL_DESCRIPTIONS), tool_files)

    def test_first_commit_report_contains_no_v1_task_root_policy(self) -> None:
        excluded_paths = {path for path, _ in prepare_first_commit_report.EXCLUDE_NOTES}
        self.assertNotIn("tasks/*", excluded_paths)

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

    def test_new_dry_run_is_allowed_for_a_read_only_external_root(self) -> None:
        tasks_root = TMP_ROOT / "dry-run-external-root"
        task_root = tasks_root / "dry-run-preview"
        self.assertFalse(task_root.exists())
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "capabilities/tools/workspace.py",
                "new",
                "dry-run-preview",
                "--dry-run",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env={**os.environ, "AGENT_TASKS_ROOT": str(tasks_root)},
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Dry run:", result.stdout)
        self.assertFalse(task_root.exists())

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
        self.assertIn("## Reserved Control Plane", first)
        self.assertIn("## Current Framework Docs", first)
        self.assertIn("docs/framework/task-lifecycle.md", first)
        self.assertNotIn("External tasks available:", first)
        self.assertNotIn("External tasks source:", first)

    def test_workspace_parser_has_explicit_status_update_command(self) -> None:
        args = workspace.build_parser().parse_args(["update-status"])
        self.assertEqual(args.command, "update-status")

    def test_codex_adapter_contains_no_legacy_workspace_paths(self) -> None:
        text = (ROOT / ".codex" / "config.toml").read_text(encoding="utf-8")
        for legacy in ("tools/", "prompts/", "sops/", "outputs/", "logs/", "tmp/", "envs/", "archives/"):
            self.assertNotIn(legacy, text)

    def test_v2_operating_docs_contain_no_root_private_area_checks(self) -> None:
        for relative in (
            "capabilities/sops/git_first_commit.md",
            "capabilities/sops/workspace_maintenance.md",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn("git ls-files tasks", text)
            self.assertNotIn("tasks archives sandboxes", text)

    def test_new_task_sop_uses_contiguous_numbering(self) -> None:
        text = (ROOT / "capabilities" / "sops" / "new_task.md").read_text(
            encoding="utf-8"
        )
        numbers = [
            int(match.group(1))
            for match in re.finditer(r"^(\d+)\. ", text, re.MULTILINE)
        ]
        self.assertEqual(numbers, list(range(1, len(numbers) + 1)))

    def test_framework_docs_match_current_check_behavior(self) -> None:
        efficiency = (
            ROOT / "docs" / "framework" / "workspace-efficiency.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn("regenerate and\nverify `WORKSPACE_STATUS.md`", efficiency)
        self.assertIn("verify `WORKSPACE_STATUS.md` without rewriting it", efficiency)

    def test_v2_docs_preserve_common_safety_and_lifecycle_contracts(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for required in (
            "global shell configuration",
            "~/.ssh",
            "whole-project refactor",
        ):
            self.assertIn(required, agents)

        lifecycle = (
            ROOT / "docs" / "framework" / "task-lifecycle.md"
        ).read_text(encoding="utf-8")
        for heading in (
            "## Complexity Levels",
            "## State Ownership",
            "## Verification Safety",
            "## Closeout Boundary",
        ):
            self.assertIn(heading, lifecycle)

        guide = (ROOT / "WORKSPACE_GUIDE.md").read_text(encoding="utf-8")
        self.assertIn("## Common Operating Principles", guide)

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
