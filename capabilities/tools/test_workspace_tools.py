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
import make_project
import make_task
import prepare_first_commit_report
import task_lifecycle
import workspace
from task_names import validate_task_name
from workspace_manifest import FULL_ONLY_STEPS, QUICK_CHECK_STEPS, TOOL_DESCRIPTIONS
from workspace_paths import load_workspace_config, resolve_external_root, workspace_root


ROOT = workspace_root()
TMP_ROOT = ROOT / "runtime" / "tmp"


class ScaffoldTests(unittest.TestCase):
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

    def test_task_scaffold_uses_only_workspace_root_skills(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
            projects_root = Path(directory) / "projects"
            make_task.scaffold_task(projects_root, "example", complexity="simple")
            task = projects_root / "example"

            self.assertFalse((task / ".agents").exists())
            self.assertFalse((task / "docs" / "skills").exists())
            self.assertNotIn(
                "task-specific skills",
                (task / "AGENTS.md").read_text(encoding="utf-8"),
            )
            self.assertNotIn("docs/skills", (task / "README.md").read_text(encoding="utf-8"))

    def test_task_scaffold_rejects_existing_project_without_changes(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
            projects_root = Path(directory) / "projects"
            project = projects_root / "example"
            project.mkdir(parents=True)
            marker = project / "keep.txt"
            marker.write_text("unchanged", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "already exists"):
                make_task.scaffold_task(projects_root, "example")

            self.assertEqual(marker.read_text(encoding="utf-8"), "unchanged")

    def test_task_scaffold_rejects_a_file_name_collision(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
            projects_root = Path(directory) / "projects"
            projects_root.mkdir()
            marker = projects_root / "example"
            marker.write_text("unchanged", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "already exists"):
                make_task.scaffold_task(projects_root, "example")

            self.assertEqual(marker.read_text(encoding="utf-8"), "unchanged")

    def test_complex_scaffold_has_explicit_coordination_files(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
            tasks_root = Path(directory) / "custom-projects"
            tasks_root.mkdir()
            make_task.scaffold_task(tasks_root, "example", complexity="complex")
            task = tasks_root / "example"
            self.assertTrue((task / "docs" / "superpowers" / "README.md").is_file())
            self.assertTrue((task / "coordination" / "contract.md").is_file())


    def test_scaffold_creates_project_without_initializing_git(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
            projects_root = Path(directory) / "projects"
            created, skipped = make_project.scaffold_project(
                projects_root,
                "example-project",
            )

            project = projects_root / "example-project"
            self.assertFalse(skipped)
            self.assertTrue((project / "project.md").is_file())
            self.assertTrue((project / "AGENTS.md").is_file())
            self.assertFalse((project / ".git").exists())
            self.assertIn(str(project / "README.md"), created)

    def test_project_scaffold_includes_open_source_assessment(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
            projects_root = Path(directory) / "projects"
            make_project.scaffold_project(projects_root, "example-project")

            assessment = (
                projects_root
                / "example-project"
                / "docs"
                / "open-source-assessment.md"
            )
            text = assessment.read_text(encoding="utf-8")

        for heading in (
            "## Search Scope",
            "## Candidates",
            "## License and Obligations",
            "## Security and Maintenance",
            "## Decision",
            "## Reuse Boundary",
        ):
            with self.subTest(heading=heading):
                self.assertIn(heading, text)

    def test_generated_project_rules_require_open_source_intake(self) -> None:
        rules = make_project.build_agents("example-project")
        self.assertIn("open-source-assessment.md", rules)
        self.assertIn("before implementation", rules)

    def test_open_source_research_skill_and_sop_exist(self) -> None:
        self.assertTrue(
            (
                ROOT
                / ".agents"
                / "skills"
                / "open-source-project-research"
                / "SKILL.md"
            ).is_file()
        )
        self.assertTrue(
            (
                ROOT
                / "capabilities"
                / "sops"
                / "open_source_project_intake.md"
            ).is_file()
        )

    def test_scaffold_rejects_exact_existing_project_without_changes(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
            projects_root = Path(directory) / "projects"
            project = projects_root / "example-project"
            project.mkdir(parents=True)
            marker = project / "keep.txt"
            marker.write_text("unchanged", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "already exists"):
                make_project.scaffold_project(projects_root, "example-project")

            self.assertEqual(marker.read_text(encoding="utf-8"), "unchanged")
            self.assertEqual(
                [path.name for path in project.iterdir()],
                ["keep.txt"],
            )

    def test_scaffold_rejects_case_insensitive_project_collision(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
            projects_root = Path(directory) / "projects"
            (projects_root / "Example-Project").mkdir(parents=True)

            with self.assertRaisesRegex(ValueError, "already exists"):
                make_project.scaffold_project(projects_root, "example-project")

    def test_project_dry_run_rejects_existing_project(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
            root = Path(directory)
            projects_root = root / "projects"
            (projects_root / "example-project").mkdir(parents=True)
            config = {"paths": {"projects": "projects"}}

            with patch.object(workspace, "load_workspace_config", return_value=config):
                with self.assertRaisesRegex(ValueError, "already exists"):
                    workspace.run_project_new(
                        root,
                        "example-project",
                        dry_run=True,
                    )

    def test_project_new_reports_created_project(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
            root = Path(directory)
            config = {"paths": {"projects": "projects"}}

            with patch.object(workspace, "load_workspace_config", return_value=config):
                with redirect_stdout(io.StringIO()) as output:
                    result = workspace.run_project_new(
                        root,
                        "example-project",
                        dry_run=False,
                    )

            self.assertEqual(result, 0)
            self.assertIn(
                str(root / "projects" / "example-project"),
                output.getvalue(),
            )

    def test_make_project_main_reports_created_project(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
            root = Path(directory)
            config = {"paths": {"projects": "projects"}}

            with (
                patch.object(make_project, "workspace_root", return_value=root),
                patch.object(
                    make_project,
                    "load_workspace_config",
                    return_value=config,
                ),
                patch.object(sys, "argv", ["make_project.py", "example-project"]),
                redirect_stdout(io.StringIO()) as output,
            ):
                result = make_project.main()

            self.assertEqual(result, 0)
            self.assertIn(
                str(root / "projects" / "example-project"),
                output.getvalue(),
            )

    def test_project_path_is_configured_and_root_exists(self) -> None:
        config = load_workspace_config(ROOT)
        self.assertEqual(config["paths"]["projects"], "projects")
        self.assertTrue((ROOT / "projects" / "README.md").is_file())

    def test_workspace_parser_has_explicit_project_new_command(self) -> None:
        args = workspace.build_parser().parse_args(
            ["project", "new", "example-project"]
        )
        self.assertEqual(args.command, "project")
        self.assertEqual(args.project_command, "new")
        self.assertEqual(args.project_name, "example-project")

    def test_workspace_check_rejects_tracked_project_content(self) -> None:
        with patch.object(
            check_workspace,
            "git_tracked_files",
            return_value=["projects/README.md", "projects/example/src/app.py"],
        ):
            issues = check_workspace.check_workspace(ROOT)

        self.assertIn(
            "project content must not be tracked by the workspace repository: "
            "projects/example/src/app.py",
            issues,
        )

    def test_workspace_check_rejects_tracked_artifact_content(self) -> None:
        with patch.object(
            check_workspace,
            "git_tracked_files",
            return_value=[
                "storage/artifacts/README.md",
                "storage/artifacts/report.json",
            ],
        ):
            issues = check_workspace.check_workspace(ROOT)

        self.assertIn(
            "local storage content must not be tracked by the workspace "
            "repository: storage/artifacts/report.json",
            issues,
        )

    def test_workspace_check_rejects_tracked_archive_content(self) -> None:
        with patch.object(
            check_workspace,
            "git_tracked_files",
            return_value=[
                "storage/archives/README.md",
                "storage/archives/projects/example/src/app.py",
            ],
        ):
            issues = check_workspace.check_workspace(ROOT)

        self.assertIn(
            "local storage content must not be tracked by the workspace "
            "repository: storage/archives/projects/example/src/app.py",
            issues,
        )

    def test_runtime_gitignore_is_default_deny_with_contract_allowlist(self) -> None:
        ignored = subprocess.run(
            [
                "git",
                "check-ignore",
                "--no-index",
                "--quiet",
                "runtime/installers/future-installer.bin",
            ],
            cwd=ROOT,
            check=False,
        )
        contract = subprocess.run(
            [
                "git",
                "check-ignore",
                "--no-index",
                "--quiet",
                "runtime/tmp/README.md",
            ],
            cwd=ROOT,
            check=False,
        )

        self.assertEqual(ignored.returncode, 0)
        self.assertEqual(contract.returncode, 1)

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

    def test_ci_checks_every_supported_python_version(self) -> None:
        workflow = ROOT / ".github" / "workflows" / "workspace-check.yml"
        text = workflow.read_text(encoding="utf-8")
        for version in ('"3.10"', '"3.11"', '"3.12"'):
            with self.subTest(version=version):
                self.assertIn(version, text)
        self.assertIn("python-version: ${{ matrix.python-version }}", text)

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

    def test_task_new_uses_configured_projects_root(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
            root = Path(directory)
            config = {"paths": {"projects": "projects"}}

            with patch.object(workspace, "load_workspace_config", return_value=config):
                with redirect_stdout(io.StringIO()) as output:
                    result = workspace.run_new(
                        root,
                        "example-task",
                        dry_run=False,
                        complexity="simple",
                    )

            self.assertEqual(result, 0)
            self.assertTrue((root / "projects" / "example-task" / "task.md").is_file())
            self.assertIn(str(root / "projects" / "example-task"), output.getvalue())

    def test_task_dry_run_ignores_external_tasks_override(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
            root = Path(directory)
            config = {"paths": {"projects": "projects"}}
            external_root = root / "external-tasks"

            with (
                patch.object(workspace, "load_workspace_config", return_value=config),
                patch.dict(os.environ, {"AGENT_TASKS_ROOT": str(external_root)}),
                redirect_stdout(io.StringIO()) as output,
            ):
                result = workspace.run_new(
                    root,
                    "dry-run-preview",
                    dry_run=True,
                    complexity="simple",
                )

            self.assertEqual(result, 0)
            self.assertIn(str(root / "projects" / "dry-run-preview"), output.getvalue())
            self.assertFalse(external_root.exists())

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
            any("legacy external tasks root is unavailable" in issue for issue in issues),
            issues,
        )
        self.assertTrue(
            any("legacy external tasks root is unavailable" in warning for warning in warnings),
            warnings,
        )

    def test_status_generator_is_deterministic(self) -> None:
        with patch.dict("os.environ", {"AGENT_TASKS_ROOT": str(ROOT.parent / "one")}):
            first = generate_workspace_status.build_status(ROOT)
        with patch.dict("os.environ", {"AGENT_TASKS_ROOT": str(ROOT.parent / "two")}):
            second = generate_workspace_status.build_status(ROOT)
        self.assertEqual(first, second)
        self.assertIn("Legacy external tasks access: `read_only`", first)
        self.assertIn("## Reserved Control Plane", first)
        self.assertIn("## Current Framework Docs", first)
        self.assertIn("## Local Task And Project Policy", first)
        self.assertIn("workspace repository tracks only `projects/README.md`", first)
        self.assertIn("docs/framework/task-lifecycle.md", first)
        self.assertNotIn("Legacy external tasks available:", first)
        self.assertNotIn("Legacy external tasks source:", first)

    def test_markdown_inventory_uses_portable_casefolded_order(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
            docs = Path(directory)
            (docs / "aider.md").write_text("# Aider\n", encoding="utf-8")
            (docs / "README.md").write_text("# Readme\n", encoding="utf-8")

            items = generate_workspace_status.markdown_items(ROOT, docs)

        self.assertEqual(
            items,
            [
                f"- `{(docs / 'aider.md').relative_to(ROOT).as_posix()}`",
                f"- `{(docs / 'README.md').relative_to(ROOT).as_posix()}`",
            ],
        )

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
