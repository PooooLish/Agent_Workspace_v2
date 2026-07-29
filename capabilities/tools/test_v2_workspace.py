#!/usr/bin/env python3
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from workspace_paths import (
    ExternalRoot,
    load_workspace_config,
    require_writable_external_root,
    resolve_external_root,
    workspace_root,
)
from workspace import require_task_write, task_workspace_root


ROOT = Path(__file__).resolve().parents[2]


class WorkspacePathTests(unittest.TestCase):
    def test_tool_location_resolves_v2_root(self) -> None:
        self.assertEqual(workspace_root(), ROOT)

    def test_config_declares_external_tasks_read_only(self) -> None:
        config = load_workspace_config(ROOT)
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
            source=".workspace/config.yaml",
        )

        with self.assertRaisesRegex(PermissionError, "read-only"):
            require_writable_external_root(external, "create task")

    def test_task_commands_resolve_the_external_workspace_root(self) -> None:
        self.assertEqual(
            task_workspace_root(ROOT),
            (ROOT / "../agent_workspace").resolve(),
        )

    def test_mutating_task_commands_are_blocked(self) -> None:
        for action in ("create task", "run task verification", "close task"):
            with self.subTest(action=action):
                with self.assertRaisesRegex(PermissionError, "read-only"):
                    require_task_write(ROOT, action)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
