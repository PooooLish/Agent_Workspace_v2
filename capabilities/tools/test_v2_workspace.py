#!/usr/bin/env python3
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from workspace_paths import (
    CONFIG_PATH,
    ExternalRoot,
    load_workspace_config,
    require_writable_external_root,
    resolve_external_root,
    workspace_root,
)
from workspace import task_workspace_root
from task_lifecycle import discover_task_names, load_task
from make_task import build_task_md


ROOT = Path(__file__).resolve().parents[2]


class WorkspacePathTests(unittest.TestCase):
    def test_config_format_matches_the_json_parser(self) -> None:
        self.assertEqual(CONFIG_PATH, Path(".workspace/config.json"))
        self.assertTrue((ROOT / CONFIG_PATH).is_file())
        self.assertFalse((ROOT / ".workspace" / "config.yaml").exists())

    def test_tool_location_resolves_v2_root(self) -> None:
        self.assertEqual(workspace_root(), ROOT)

    def test_config_declares_external_tasks_read_only(self) -> None:
        config = load_workspace_config(ROOT)
        with patch.dict(os.environ, {"AGENT_TASKS_ROOT": ""}):
            tasks = resolve_external_root(ROOT, config, "tasks")

        self.assertEqual(tasks.access, "read_only")
        self.assertEqual(tasks.path, (ROOT / "../agent_workspace/tasks").resolve())
        self.assertFalse(tasks.path.is_relative_to(ROOT))

    def test_environment_can_override_external_tasks_path(self) -> None:
        config = load_workspace_config(ROOT)
        with tempfile.TemporaryDirectory(dir=ROOT / "runtime" / "tmp") as directory:
            with patch.dict(os.environ, {"AGENT_TASKS_ROOT": directory}):
                tasks = resolve_external_root(ROOT, config, "tasks")

        self.assertEqual(tasks.path, Path(directory).resolve())
        self.assertEqual(tasks.source, "AGENT_TASKS_ROOT")

    def test_read_only_external_root_rejects_write_access(self) -> None:
        external = ExternalRoot(
            path=(ROOT / "../agent_workspace/tasks").resolve(),
            access="read_only",
            source=".workspace/config.json",
        )

        with self.assertRaisesRegex(PermissionError, "read-only"):
            require_writable_external_root(external, "create task")

    def test_task_commands_resolve_the_local_projects_root(self) -> None:
        with patch.dict(os.environ, {"AGENT_TASKS_ROOT": ""}):
            self.assertEqual(
                task_workspace_root(ROOT),
                (ROOT / "projects").resolve(),
            )

    def test_lifecycle_uses_an_overridden_tasks_root_with_any_name(self) -> None:
        config = load_workspace_config(ROOT)
        with tempfile.TemporaryDirectory(dir=ROOT / "runtime" / "tmp") as directory:
            tasks_root = Path(directory)
            task_root = tasks_root / "example"
            task_root.mkdir()
            (task_root / "task.md").write_text(
                build_task_md("example", "standard"),
                encoding="utf-8",
            )
            with patch.dict(os.environ, {"AGENT_TASKS_ROOT": directory}):
                resolved = resolve_external_root(ROOT, config, "tasks")
                names = discover_task_names(resolved.path)
                task = load_task(resolved.path, "example")

        self.assertEqual(names, ["example"])
        self.assertEqual(task.root, task_root)

    def test_project_discovery_ignores_non_task_project_directories(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "runtime" / "tmp") as directory:
            projects_root = Path(directory)
            (projects_root / "plain-project").mkdir()
            task_root = projects_root / "tracked-task"
            task_root.mkdir()
            (task_root / "task.md").write_text(
                build_task_md("tracked-task", "standard"),
                encoding="utf-8",
            )

            self.assertEqual(discover_task_names(projects_root), ["tracked-task"])


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
