from __future__ import annotations

import re
import subprocess
import tempfile
import unittest
import uuid
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
LAUNCHER = WORKSPACE_ROOT / "capabilities" / "tools" / "opencode-v2.ps1"
# opencode 版本主号变化时 `debug paths` 输出格式可能不兼容，届时需更新本测试。
SUPPORTED_OPENCODE_MAJOR = 1


def _opencode_version() -> tuple[int, int, int] | None:
    """读取已安装 opencode 的版本；不可用时返回 None，不阻塞测试主体。"""

    try:
        completed = subprocess.run(
            ["opencode", "--version"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+).*", completed.stdout.strip())
    if match is None:
        return None
    return tuple(int(group) for group in match.groups())


def _parse_path_report(stdout: str) -> dict[str, Path]:
    """严格解析 `opencode debug paths` 的 `key value` 行。

    值缺失或格式不符必须显式失败，避免空路径在 resolve 后落回当前目录
    造成假阳性。
    """

    reported: dict[str, Path] = {}
    for line in stdout.splitlines():
        key, separator, value = line.partition(" ")
        if not separator or not value.strip():
            raise AssertionError(f"无法解析 opencode 路径报告行：{line!r}")
        reported[key] = Path(value.strip()).resolve()
    return reported


class OpenCodeV2LauncherTests(unittest.TestCase):
    def run_launcher(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-File",
                str(LAUNCHER),
                *arguments,
            ],
            cwd=WORKSPACE_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def _require_supported_version(self) -> None:
        version = _opencode_version()
        if version is not None and version[0] != SUPPORTED_OPENCODE_MAJOR:
            self.skipTest(
                f"opencode {'.'.join(map(str, version))} 的输出格式可能不兼容，"
                "需先更新本测试再验证"
            )

    def _create_junction(self, link: Path, target: Path) -> bool:
        """尝试创建指向 target 的 junction；无权限时返回 False。"""
        completed = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    f"New-Item -ItemType Junction -Path '{link}' "
                    f"-Target '{target}' | Out-Null"
                ),
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
        )
        return completed.returncode == 0 and link.exists()

    def test_rejects_junction_escaping_workspace(self) -> None:
        """GetFullPath 不解析 junction，指向外部的链接必须被安全拒绝。"""
        if not hasattr(__import__("os"), "symlink"):
            self.skipTest("当前平台不支持创建链接")
        outside = WORKSPACE_ROOT.parent / f"opencode-outside-{uuid.uuid4().hex[:8]}"
        outside.mkdir()
        link = (
            WORKSPACE_ROOT
            / "projects"
            / f"escape-junction-{uuid.uuid4().hex[:8]}"
        )
        try:
            if not self._create_junction(link, outside):
                self.skipTest("当前环境没有创建 junction 的权限")
            result = self.run_launcher("-Project", str(link), "--version")
        finally:
            if link.exists():
                link.rmdir()
            outside.rmdir()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reparse point", result.stderr)

    def test_redirects_opencode_state_into_v2_workspace(self) -> None:
        self._require_supported_version()
        result = self.run_launcher("debug", "paths")

        self.assertEqual(result.returncode, 0, result.stderr)
        try:
            reported_paths = _parse_path_report(result.stdout)
        except AssertionError as exc:
            self.fail(f"{exc}\n原始输出：\n{result.stdout}")

        for key in ("data", "bin", "log", "repos", "cache", "config", "state", "tmp"):
            with self.subTest(key=key):
                self.assertIn(key, reported_paths, f"缺少路径字段 {key}")
                self.assertTrue(
                    reported_paths[key].is_relative_to(WORKSPACE_ROOT),
                    f"{key} escaped V2: {reported_paths[key]}",
                )

    def test_rejects_project_outside_v2_workspace(self) -> None:
        result = self.run_launcher("-Project", str(WORKSPACE_ROOT.parent), "--version")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Project must stay inside the V2 workspace", result.stderr)


if __name__ == "__main__":
    unittest.main()
