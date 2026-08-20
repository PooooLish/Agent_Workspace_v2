#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from workspace_paths import (
    CONFIG_PATH,
    load_workspace_config,
    workspace_root,
)
from workspace import task_workspace_root
from task_lifecycle import discover_task_names
from make_task import build_task_md


ROOT = Path(__file__).resolve().parents[2]


class WorkspacePathTests(unittest.TestCase):
    def test_config_format_matches_the_json_parser(self) -> None:
        self.assertEqual(CONFIG_PATH, Path(".workspace/config.json"))
        self.assertTrue((ROOT / CONFIG_PATH).is_file())
        self.assertFalse((ROOT / ".workspace" / "config.yaml").exists())

    def test_tool_location_resolves_v2_root(self) -> None:
        self.assertEqual(workspace_root(), ROOT)

    def test_config_has_no_external_workspace_roots(self) -> None:
        config = load_workspace_config(ROOT)
        self.assertNotIn("external_roots", config)

    def test_task_commands_resolve_the_local_projects_root(self) -> None:
        self.assertEqual(
            task_workspace_root(ROOT),
            (ROOT / "projects").resolve(),
        )

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
